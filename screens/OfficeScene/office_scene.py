# events gives us the Resize event when the terminal window changes size.
from textual import events

# ComposeResult is the return type used by Textual's compose() method.
from textual.app import ComposeResult

# Horizontal places widgets side-by-side.
# Vertical stacks widgets from top to bottom.
# VerticalScroll keeps everything reachable when the terminal is short.
from textual.containers import Horizontal, Vertical, VerticalScroll

# Button creates normal buttons.
# Static displays text that can be updated later.
from textual.widgets import Button, Static

# Every normal gameplay room inherits from InvestigationScene.
#
# This automatically provides:
# - [[hidden interaction]] parsing
# - 1.0 second held-word wobble
# - 1.5 second activation
# - early-release cancellation
from screens.base_scene import InvestigationScene

# Import this room's clue text.
from .clue_data import CLUE_DESCRIPTIONS, CLUE_NAMES


class OfficeSceneScreen(InvestigationScene):
    """Office Room."""

    def __init__(self) -> None:
        # Sets up Textual + the shared hold-interaction system.
        super().__init__()

        # Actual clues discovered in this room.
        self.found: set[str] = set()

        # Room state:
        # False = lamp off
        # True  = lamp on
        self.lamp_on = False

    def compose(self) -> ComposeResult:
        # Keeps everything reachable in a short terminal.
        with VerticalScroll(id="scene-scroll"):

            # Standard gameplay layout:
            #
            # Wide:
            # STORY | NOTEBOOK
            #
            # Narrow:
            # STORY
            # NOTEBOOK
            with Horizontal(id="scene-body"):

                # LEFT SIDE: room / story.
                with Vertical(id="story-column"):
                    yield Static(
                        "OFFICE — 8:47 PM",
                        id="scene-title",
                    )

                    # build_scene() returns the final display text.
                    yield Static(
                        self.build_scene(),
                        id="scene-text",
                    )

                    # Examination / interaction results.
                    yield Static(
                        "John stands quietly in the office.",
                        id="detail",
                        markup=True,
                    )

                    yield Button(
                        "LEAVE OFFICE",
                        id="leave-office",
                    )

                # RIGHT SIDE: notebook.
                with Vertical(id="side-column"):
                    yield Static(
                        "JOHN'S NOTEBOOK",
                        classes="section-title",
                    )

                    yield Static(
                        "Clues: 0",
                        id="clue-count",
                    )

                    yield Static(
                        "No evidence recorded yet.",
                        id="notebook",
                        markup=True,
                    )

    def build_scene(self):
        """
        Write the room almost like ordinary prose.

        [[windows]]
            Player sees "windows".
            Interaction ID is "windows".

        [[visible text|internal_id]]
            Lets visible text and the internal ID be different.

        Everything outside [[...]] is completely normal static text.
        """

        # Scene state can still change normal prose.
        if self.lamp_on:
            office_light = "The office is dimly lit."
        else:
            office_light = "The office is almost completely dark."

        # self.scene(...) parses every [[tag]] automatically.
        return self.scene(
            f"{office_light}\n\n"
            "Rain presses against the [[windows]].\n\n"
            "A wooden desk sits beneath the [[lamp]]."
        )

    def activate_interaction(self, interaction_id: str) -> None:
        """
        Decide what an activated hidden interaction does.

        Most IDs are clues.
        Special room-state objects can be handled here.
        """

        # Lamp changes room state rather than becoming notebook evidence.
        if interaction_id == "lamp":
            self.toggle_lamp()
            return

        # Everything else uses the shared default:
        # self.inspect(interaction_id)
        super().activate_interaction(
            interaction_id
        )

    def toggle_lamp(self) -> None:
        """
        Turn the lamp on/off and rebuild the room prose.
        """

        self.lamp_on = not self.lamp_on

        # Rebuild scene so the first sentence changes.
        self.query_one(
            "#scene-text",
            Static,
        ).update(
            self.build_scene()
        )

        detail = self.query_one(
            "#detail",
            Static,
        )

        if self.lamp_on:
            detail.update(
                "John switches on the lamp. "
                "A weak yellow light spreads through the office."
            )
        else:
            detail.update(
                "John switches off the lamp. "
                "The office falls back into darkness."
            )

    def inspect(self, clue_id: str) -> None:
        """
        Examine a real clue.
        """

        # Unknown IDs should not crash the room.
        if clue_id not in CLUE_DESCRIPTIONS:
            return

        detail = self.query_one(
            "#detail",
            Static,
        )

        detail.update(
            CLUE_DESCRIPTIONS[clue_id]
        )

        # Only discover a clue once.
        if clue_id not in self.found:
            self.found.add(
                clue_id
            )

            self.refresh_notebook()

        detail.scroll_visible()

    def refresh_notebook(self) -> None:
        """
        Rebuild the notebook after discovering evidence.
        """

        clue_count = self.query_one(
            "#clue-count",
            Static,
        )

        notebook = self.query_one(
            "#notebook",
            Static,
        )

        clue_count.update(
            f"Clues: {len(self.found)}"
        )

        notebook_lines = [
            f"• {CLUE_NAMES[clue_id]}"
            for clue_id in self.found
            if clue_id in CLUE_NAMES
        ]

        if notebook_lines:
            notebook.update(
                "\n\n".join(notebook_lines)
            )
        elif self.found:
            notebook.update(
                "Evidence discovered.\n\n"
                "Add short notebook text for it in clue_data.py."
            )
        else:
            notebook.update(
                "No evidence recorded yet."
            )

    def on_mount(self) -> None:
        # Pick the correct story/sidebar layout when room opens.
        self.apply_responsive_layout()

    def on_resize(self, event: events.Resize) -> None:
        # Re-check layout whenever terminal width changes.
        self.apply_responsive_layout()

    def apply_responsive_layout(self) -> None:
        # Narrow terminal = notebook moves below story.
        if self.size.width < 90:
            self.add_class(
                "compact-scene"
            )
        else:
            self.remove_class(
                "compact-scene"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Visible menu/navigation buttons remain normal single-click buttons.
        if event.button.id == "leave-office":
            self.app.pop_screen()
