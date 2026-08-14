# events gives us the Resize event when the terminal window changes size.
from textual import events

# Rich Text lets us assemble normal prose and invisible interactive spans.
from rich.text import Text

# ComposeResult is the return type used by Textual's compose() method.
from textual.app import ComposeResult

# Horizontal places widgets side-by-side.
# Vertical stacks widgets from top to bottom.
# VerticalScroll keeps everything reachable when the terminal is short.
from textual.containers import Horizontal, Vertical, VerticalScroll

# Button creates normal buttons.
# Static displays text that can be updated later.
from textual.widgets import Button, Static

# EVERY normal gameplay room inherits from InvestigationScene instead of
# inheriting directly from Textual's Screen.
#
# This automatically gives the room:
# - hidden hold interactions
# - 1.0 second held-word wobble
# - 1.5 second activation
# - early-release cancellation
from screens.base_scene import InvestigationScene

# Import this room's clue text from the file beside office_scene.py.
from .clue_data import CLUE_DESCRIPTIONS, CLUE_NAMES


# This class represents the Office scene.
class OfficeSceneScreen(InvestigationScene):
    """Office Room."""

    def __init__(self) -> None:
        # InvestigationScene.__init__() sets up the universal hold system.
        super().__init__()

        # Store actual clues discovered in this room.
        self.found: set[str] = set()

        # Room STATE:
        #
        # False = lamp is off.
        # True  = lamp is on.
        #
        # The lamp is an interactive object, but it is not automatically
        # notebook evidence.
        self.lamp_on = False

    def compose(self) -> ComposeResult:
        # Keep the whole gameplay scene reachable on short terminals.
        with VerticalScroll(id="scene-scroll"):

            # Standard gameplay body.
            #
            # The hold system does NOT move this container anymore.
            # Only the exact hidden word being held changes glyphs.
            with Horizontal(id="scene-body"):

                # ------------------------------------------------------
                # LEFT SIDE: story / room
                # ------------------------------------------------------
                with Vertical(id="story-column"):
                    yield Static(
                        "OFFICE — 8:47 PM",
                        id="scene-title",
                    )

                    # build_scene() now returns a Rich Text object.
                    #
                    # Rich Text lets invisible metadata exist on individual
                    # words without visually changing them.
                    yield Static(
                        self.build_scene(),
                        id="scene-text",
                    )

                    # Examination and interaction results appear here.
                    yield Static(
                        "John stands quietly in the office.",
                        id="detail",
                        markup=True,
                    )

                    yield Button(
                        "LEAVE OFFICE",
                        id="leave-office",
                    )

                # ------------------------------------------------------
                # RIGHT SIDE: notebook
                # ------------------------------------------------------
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

    def build_scene(self) -> Text:
        """
        Build the current office prose.

        Hidden interaction syntax is now:

            self.hidden("VISIBLE WORD", "INTERACTION_ID")

        There is NO @click anymore.
        """

        # Change room prose based on lamp state.
        if self.lamp_on:
            office_light = "The office is dimly lit."
        else:
            office_light = "The office is almost completely dark."

        # Start an empty Rich Text document.
        scene = Text()

        # Normal prose.
        scene.append(
            f"{office_light}\n\n"
        )

        scene.append(
            "Rain presses against the "
        )

        # Hidden interaction example #1:
        #
        # The player sees "windows".
        # Holding it for 1.5 seconds activates interaction ID "windows".
        scene.append(
            self.hidden(
                "windows",
                "windows",
            )
        )

        scene.append(
            ".\n\n"
        )

        scene.append(
            "A wooden desk sits beneath the "
        )

        # Hidden interaction example #2:
        #
        # This does NOT become a clue.
        # The same global hold system activates interaction ID "lamp".
        scene.append(
            self.hidden(
                "lamp",
                "lamp",
            )
        )

        scene.append(".")

        return scene

    def activate_interaction(self, interaction_id: str) -> None:
        """
        Decide what an activated hidden object does in THIS room.

        Most IDs are clues and use the shared default inspect behavior.

        Special room-state objects can be intercepted here.
        """

        # The lamp changes the room instead of becoming notebook evidence.
        if interaction_id == "lamp":
            self.toggle_lamp()
            return

        # Everything else uses InvestigationScene's default behavior:
        #
        # self.inspect(interaction_id)
        super().activate_interaction(
            interaction_id
        )

    def toggle_lamp(self) -> None:
        """
        Turn the lamp on/off and rebuild the room prose.
        """

        # False -> True
        # True  -> False
        self.lamp_on = not self.lamp_on

        # Rebuild the main scene so office_light changes.
        self.query_one(
            "#scene-text",
            Static,
        ).update(
            self.build_scene()
        )

        # Show immediate feedback in the detail box.
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

        # Unknown IDs should not crash the scene.
        if clue_id not in CLUE_DESCRIPTIONS:
            return

        detail = self.query_one(
            "#detail",
            Static,
        )

        # Display the full clue description.
        detail.update(
            CLUE_DESCRIPTIONS[clue_id]
        )

        # Only discover each clue once.
        if clue_id not in self.found:
            self.found.add(
                clue_id
            )

            self.refresh_notebook()

        detail.scroll_visible()

    def refresh_notebook(self) -> None:
        """
        Rebuild the right-side notebook after discovering evidence.
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
        """
        Choose the correct story/sidebar layout when the room opens.
        """
        self.apply_responsive_layout()

    def on_resize(self, event: events.Resize) -> None:
        """
        Re-check layout when the terminal window changes size.
        """
        self.apply_responsive_layout()

    def apply_responsive_layout(self) -> None:
        """
        Wide:
            STORY | NOTEBOOK

        Narrow:
            STORY
            NOTEBOOK
        """

        if self.size.width < 90:
            self.add_class(
                "compact-scene"
            )
        else:
            self.remove_class(
                "compact-scene"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Normal visible buttons still use normal single-click behavior.
        """

        if event.button.id == "leave-office":
            self.app.pop_screen()
