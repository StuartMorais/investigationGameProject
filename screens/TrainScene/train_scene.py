# Temporary Train scene BEHAVIOR.
#
# Its clue/deduction information and selected previous clues live in
# TrainScene/clue_data.py.

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Static

from screens.base_scene import InvestigationScene
from .clue_data import (
    CLUES,
    DEDUCTIONS,
    RELEVANT_PREVIOUS_CLUES,
    SCENE_ID,
)


class TrainSceneScreen(InvestigationScene):
    """Temporary Train placeholder while the story is being written."""

    scene_id = SCENE_ID
    clue_data = CLUES
    deduction_data = DEDUCTIONS
    relevant_previous_clues = RELEVANT_PREVIOUS_CLUES

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="scene-scroll"):
            with Horizontal(id="scene-body"):
                with Vertical(id="story-column"):
                    yield Static("TRAIN — NEXT SCENE", id="scene-title")
                    yield Static(self.build_scene(), id="scene-text")
                    yield Static(
                        "The Train scene is ready for the story to be written.",
                        id="detail",
                        markup=True,
                    )
                    yield Button(
                        "BACK TO OFFICE",
                        id="back-office",
                        classes="scene-navigation",
                    )

                # This sidebar shows only what TrainScene/clue_data.py requests.
                yield self.build_sidebar()

    def build_scene(self):
        return self.scene(
            "John reaches the train.\n\n"
            "The next part of the investigation will begin here."
        )

    def on_mount(self) -> None:
        super().on_mount()
        self.apply_responsive_layout()

    def on_resize(self, event: events.Resize) -> None:
        self.apply_responsive_layout()

    def apply_responsive_layout(self) -> None:
        if self.size.width < 90:
            self.add_class("compact-scene")
        else:
            self.remove_class("compact-scene")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-office":
            self.app.pop_screen()
