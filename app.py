# App is the main Textual application class.
from textual.app import App

# Import the first screen the player should see.
from screens.Menus.main_menu import MainMenuScreen


# InvestigationGame is the main application for the entire game.
class InvestigationGame(App):
    # Text shown by Textual as the application's title/subtitle.
    TITLE = "THE INVESTIGATION GAME"
    SUB_TITLE = "A Terminal Investigation"

    # Tell Textual to load the styles from styles.tcss.
    CSS_PATH = "styles.tcss"

    # We are not showing global keyboard shortcuts yet.
    BINDINGS = []

    # on_mount() runs once after the application has started.
    def on_mount(self) -> None:
        # Open the main menu screen.
        self.push_screen(MainMenuScreen())
