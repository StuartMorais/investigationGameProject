# App is the main Textual application class.
from textual.app import App

# Import the first screen the player should see.
from screens.Menus.main_menu import MainMenuScreen

# InvestigationState stores clues/deductions that survive scene changes.
from systems.investigation_state import InvestigationState


class InvestigationGame(App):
    """
    Main application for the entire game.
    """

    # The actual story/game title is intentionally NOT decided yet.
    TITLE = "UNTITLED INVESTIGATION"
    SUB_TITLE = "A Terminal Investigation"

    # Tell Textual to load the styles from styles.tcss.
    CSS_PATH = "styles.tcss"

    # We are not showing global keyboard shortcuts yet.
    BINDINGS = []

    def __init__(self, *args, **kwargs) -> None:
        # Let Textual initialize the application first.
        super().__init__(*args, **kwargs)

        # One shared state object belongs to the current investigation.
        self.investigation_state = InvestigationState()

    def reset_investigation(self) -> None:
        """
        Start a completely fresh investigation.

        MainMenuScreen calls this before opening the Office.
        """
        self.investigation_state = InvestigationState()

    def on_mount(self) -> None:
        # Open the Main Menu.
        self.push_screen(
            MainMenuScreen()
        )
