# events gives us the Resize event when the terminal window changes size.
from textual import events

# ComposeResult is the return type used by Textual's compose() method.
from textual.app import ComposeResult

# Horizontal places widgets side-by-side.
# Vertical stacks widgets from top to bottom.
# VerticalScroll makes the whole scene scrollable when the terminal is short.
from textual.containers import Horizontal, Vertical, VerticalScroll

# Screen lets this room exist as its own separate game screen.
from textual.screen import Screen

# Button creates normal buttons.
# Static displays text that can be updated later.
from textual.widgets import Button, Static

# Import this room's clue text from the file beside office_scene.py.
from .clue_data import CLUE_DESCRIPTIONS, CLUE_NAMES


# This class represents the Office scene.
class OfficeSceneScreen(Screen):
    """Office Room."""

    # __init__() runs when a new OfficeSceneScreen object is created.
    def __init__(self) -> None:
        # Always let Textual initialize Screen first.
        super().__init__()

        # Store the IDs of clues the player has discovered in this scene.
        #
        # A set is useful because the same clue ID cannot be stored twice.
        #
        # Example later:
        # self.found == {"desk", "letter"}
        self.found: set[str] = set()

    # compose() builds everything the player can see on this screen.
    def compose(self) -> ComposeResult:
        # This scroll container keeps the entire scene reachable if the
        # terminal window is short.
        with VerticalScroll(id="scene-scroll"):

            # #scene-body holds the two main gameplay columns.
            #
            # On a large terminal:
            #
            #     STORY / ROOM       |       NOTEBOOK
            #
            # On a small terminal, styles.tcss changes this to:
            #
            #     STORY / ROOM
            #     NOTEBOOK
            #
            with Horizontal(id="scene-body"):

                # ------------------------------------------------------
                # LEFT SIDE: the actual room / story
                # ------------------------------------------------------
                with Vertical(id="story-column"):

                    # Scene/location title.
                    yield Static(
                        "OFFICE — 8:47 PM",
                        id="scene-title",
                    )

                    # Main prose for the room.
                    #
                    # markup=True is important because later we can place
                    # clickable Textual markup inside build_scene().
                    yield Static(
                        self.build_scene(),
                        id="scene-text",
                        markup=True,
                    )

                    # This box shows the result when the player examines
                    # something in the prose.
                    yield Static(
                        "John stands quietly in the office.",
                        id="detail",
                        markup=True,
                    )

                    # Return to the screen underneath this one.
                    # Right now that screen is the main menu.
                    yield Button(
                        "LEAVE OFFICE",
                        id="leave-office",
                    )

                # ------------------------------------------------------
                # RIGHT SIDE: permanent gameplay sidebar
                # ------------------------------------------------------
                #
                # The idea is that EVERY normal gameplay scene can use
                # this same right-side layout.
                #
                # The MAIN MENU does not use it.
                with Vertical(id="side-column"):

                    # Sidebar title.
                    yield Static(
                        "JOHN'S NOTEBOOK",
                        classes="section-title",
                    )

                    # Shows how many clues have been discovered in this scene.
                    yield Static(
                        "Clues: 0",
                        id="clue-count",
                    )

                    # This widget will contain the short notebook versions
                    # of clues after the player discovers them.
                    yield Static(
                        "No evidence recorded yet.",
                        id="notebook",
                        markup=True,
                    )

    # build_scene() returns the prose displayed in #scene-text.
    def build_scene(self) -> str:
        # For now this is plain text.
        #
        # Later you can turn individual words into hidden clickable objects.
        return (
            "The office is almost completely dark.\n\n"

            # Only the word "windows" is clickable.
            #
            # screen.inspect('windows') tells Textual to call
            # action_inspect("windows") on THIS screen.
            #
            # styles.tcss makes the link look exactly like normal prose,
            # so the player has to notice the word themselves.
            "Rain presses against the "
            "[@click=screen.inspect('windows')]windows[/].\n\n"

            "A wooden desk sits beneath the lamp."
        )

    # Textual actions must begin with action_.
    #
    # Clicking this markup:
    #
    #     [@click=screen.inspect('windows')]windows[/]
    #
    # makes Textual call:
    #
    #     action_inspect("windows")
    #
    # We then pass the clue ID to our normal inspect() function below.
    def action_inspect(self, clue_id: str) -> None:
        self.inspect(clue_id)

    # inspect() is the function we will use for hidden clickable objects.
    def inspect(self, clue_id: str) -> None:
        # If the clue ID does not exist in clue_data.py, stop here instead
        # of crashing the game.
        if clue_id not in CLUE_DESCRIPTIONS:
            return

        # Find the examination/result box by its CSS ID.
        detail = self.query_one("#detail", Static)

        # Show the full clue description from clue_data.py.
        detail.update(CLUE_DESCRIPTIONS[clue_id])

        # Only add the clue if it has not already been discovered.
        if clue_id not in self.found:
            # Remember that this clue was found.
            self.found.add(clue_id)

            # Update the permanent sidebar.
            self.refresh_notebook()

        # If the result box is outside the visible part of a small terminal,
        # scroll it into view.
        detail.scroll_visible()

    # refresh_notebook() rebuilds the sidebar after discovering a clue.
    def refresh_notebook(self) -> None:
        # Find the clue counter.
        clue_count = self.query_one("#clue-count", Static)

        # Find the notebook text area.
        notebook = self.query_one("#notebook", Static)

        # Update the number shown in the sidebar.
        clue_count.update(f"Clues: {len(self.found)}")

        # Build one notebook line for every clue we have discovered.
        #
        # CLUE_NAMES contains the short version of a clue.
        notebook_lines = [
            f"• {CLUE_NAMES[clue_id]}"
            for clue_id in self.found
            if clue_id in CLUE_NAMES
        ]

        # If we have notebook text, show it.
        if notebook_lines:
            notebook.update("\n\n".join(notebook_lines))

        # If a clue has no CLUE_NAMES entry yet, keep a useful fallback.
        elif self.found:
            notebook.update(
                "Evidence discovered.\n\n"
                "Add short notebook text for it in clue_data.py."
            )

        # If nothing was found, show the original empty message.
        else:
            notebook.update("No evidence recorded yet.")

    # on_mount() runs once when this scene appears.
    def on_mount(self) -> None:
        # Choose the correct layout for the current terminal size.
        self.apply_responsive_layout()

    # on_resize() runs every time the player changes the terminal size.
    def on_resize(self, event: events.Resize) -> None:
        # Re-check whether the sidebar should be beside or underneath
        # the story.
        self.apply_responsive_layout()

    # apply_responsive_layout() changes CSS classes based on terminal width.
    def apply_responsive_layout(self) -> None:
        # Textual measures terminal width in character cells.
        if self.size.width < 90:
            # styles.tcss contains rules for .compact-scene.
            self.add_class("compact-scene")
        else:
            # Wide terminal: return to the normal side-by-side layout.
            self.remove_class("compact-scene")

    # Handle normal visible buttons on this scene.
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Check whether the player clicked LEAVE OFFICE.
        if event.button.id == "leave-office":
            # Remove OfficeSceneScreen.
            #
            # The MainMenuScreen underneath becomes visible again.
            self.app.pop_screen()