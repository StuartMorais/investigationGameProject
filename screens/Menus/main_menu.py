# events gives us resize events when the terminal window changes size.
from textual import events

# ComposeResult is the return type used by Textual's compose() method.
from textual.app import ComposeResult

# Vertical stacks widgets from top to bottom.
from textual.containers import Vertical

# Screen is used to create a separate game/menu screen.
from textual.screen import Screen

# Button creates clickable buttons and Static displays text.
from textual.widgets import Button, Static

# Import the first playable scene.
from screens.OfficeScene.office_scene import OfficeSceneScreen


# This class represents the game's main menu.
class MainMenuScreen(Screen):
    # compose() tells Textual which widgets belong on this screen.
    def compose(self) -> ComposeResult:
        # Vertical places everything inside it one underneath another.
        with Vertical(id="menu-shell"):
            # Main title.
            yield Static(
                "THE INVESTIGATION GAME",
                id="menu-title",
            )

            # Smaller subtitle underneath the title.
            yield Static(
                "A terminal investigation",
                id="menu-subtitle",
            )

            # Short introduction / atmosphere text.
            yield Static(
                "THE PLACE WHERE EVERYTHING HAPPENS\n"
                "AND\n"
                "NOTHING IS SEEN.",
                id="menu-intro",
            )

            # Starts the first scene.
            yield Button(
                "START INVESTIGATION",
                id="start-game",
                variant="primary",
            )

            # Shows/hides the instructions below.
            yield Button(
                "HOW TO PLAY",
                id="how-to-play",
            )

            # Closes the game.
            yield Button(
                "QUIT",
                id="quit-game",
            )

            # This text starts hidden because styles.tcss gives #menu-help
            # the rule: display: none;
            yield Static(
                "HOW TO PLAY\n\n"
                "Read the prose carefully.\n"
                "Some ordinary words can be interacted with, but they "
                "look exactly like the surrounding text.\n\n"
                "Press and HOLD the left mouse button on something that "
                "catches your attention.\n"
                "After 1 second the word itself begins to wobble.\n"
                "Keep holding until 1.5 seconds to activate it.\n\n"
                "Releasing early cancels the interaction.\n"
                "There are no glowing clue markers.",
                id="menu-help",
            )

    # on_mount() runs when this screen first appears.
    def on_mount(self) -> None:
        # Check whether we should use the compact menu layout.
        self.apply_responsive_layout()

    # on_resize() runs whenever the terminal changes size.
    def on_resize(self, event: events.Resize) -> None:
        # Re-check the layout after resizing.
        self.apply_responsive_layout()

    # This method adds/removes a CSS class based on terminal width.
    def apply_responsive_layout(self) -> None:
        # self.size.width is the terminal width measured in character cells.
        if self.size.width < 55:
            # styles.tcss has special rules for .compact-menu.
            self.add_class("compact-menu")
        else:
            # Remove compact mode when there is enough room again.
            self.remove_class("compact-menu")

    # Textual sends Button.Pressed whenever one of this screen's buttons is used.
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # event.button.id tells us exactly which button was pressed.
        button_id = event.button.id

        if button_id == "start-game":
            # Put OfficeSceneScreen on top of the main menu.
            self.app.push_screen(OfficeSceneScreen())
            return

        if button_id == "how-to-play":
            # Find the help widget by its CSS id.
            help_panel = self.query_one("#menu-help")

            # Toggle between visible and hidden.
            help_panel.display = not help_panel.display
            return

        if button_id == "quit-game":
            # Shut down the Textual application.
            self.app.exit()
