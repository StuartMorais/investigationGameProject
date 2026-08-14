# Office scene BEHAVIOR.
#
# Investigation writing lives next door in clue_data.py.

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Static

from screens.base_scene import InvestigationScene
from screens.TrainScene.train_scene import TrainSceneScreen

from .clue_data import (
    CLUES,
    DEDUCTIONS,
    RELEVANT_PREVIOUS_CLUES,
    SCENE_ID,
)


class OfficeSceneScreen(InvestigationScene):
    """Office room."""

    # Connect this scene to its own clue_data.py.
    scene_id = SCENE_ID
    clue_data = CLUES
    deduction_data = DEDUCTIONS
    relevant_previous_clues = RELEVANT_PREVIOUS_CLUES

    def __init__(self) -> None:
        super().__init__()

        # Room state stays in the room file.
        self.lamp_on = False

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="scene-scroll"):
            with Horizontal(id="scene-body"):
                with Vertical(id="story-column"):
                    yield Static("OFFICE — 8:47 PM", id="scene-title")
                    yield Static(self.build_scene(), id="scene-text")
                    yield Static(
                        "John stands quietly in the office.",
                        id="detail",
                        markup=True,
                    )
                    yield Button(
                        "RETURN TO MENU",
                        id="return-menu",
                        classes="scene-navigation",
                    )

                # Permanent UI, but scene-controlled information.
                yield self.build_sidebar()

    def build_scene(self):
        if self.lamp_on:
            office_light = "The office is dimly lit."
        else:
            office_light = "The office is almost completely dark."

        return self.scene(
            f"{office_light}\n\n"
            "Rain presses against the [[windows]].\n\n"
            "A wooden desk sits beneath the [[lamp]]. "
            "A folded [[ticket stub|ticket]] rests beside the blotter."
        )

    def activate_interaction(self, interaction_id: str) -> None:
        # Lamp is room state, not evidence.
        if interaction_id == "lamp":
            self.toggle_lamp()
            return

        # Normal clues are handled by InvestigationScene.inspect().
        super().activate_interaction(interaction_id)

    def toggle_lamp(self) -> None:
        self.lamp_on = not self.lamp_on
        self.query_one("#scene-text", Static).update(self.build_scene())

        detail = self.query_one("#detail", Static)
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

    def can_follow_deduction(self, lead_id: str) -> bool:
        return lead_id == "train"

    def follow_deduction(self, lead_id: str) -> None:
        if lead_id == "train":
            self.app.push_screen(TrainSceneScreen())

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
        if event.button.id == "return-menu":
            self.app.pop_screen()
