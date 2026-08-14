# Base class used by EVERY normal gameplay scene.
#
# The Main Menu does NOT inherit from this class.

import re

from textual import events, on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Button, Static
from rich.markup import escape
from rich.text import Text

from systems.hold_interaction import (
    HOLD_ACTIVATE_TIME,
    HOLD_WOBBLE_TIME,
    INTERACTION_META_KEY,
    INTERACTION_TOKEN_KEY,
    WORD_WOBBLE_INTERVAL,
    hidden_word,
    wobble_word,
)


SCENE_TAG_PATTERN = re.compile(r"\[\[([^\[\]]+?)\]\]")


class InvestigationSidebar(Vertical):
    """
    Permanent notebook + deduction panel for gameplay scenes.

    This class lives here in base_scene.py because it only belongs to
    InvestigationScene and does not need its own widgets/ package.
    """

    def compose(self) -> ComposeResult:
        # -------------------------------------------------------------
        # NOTEBOOK
        # -------------------------------------------------------------
        yield Static(
            "JOHN'S NOTEBOOK",
            classes="section-title",
        )

        yield Static(
            "Scene clues: 0",
            id="clue-count",
        )

        yield Static(
            "No relevant evidence recorded yet.",
            id="notebook",
            markup=True,
        )

        # -------------------------------------------------------------
        # DEDUCTIONS
        # -------------------------------------------------------------
        yield Static(
            "DEDUCTIONS",
            classes="section-title deduction-section-title",
        )

        yield Static(
            "No deduction recorded yet.",
            id="deduction-list",
            markup=True,
        )

        yield Button(
            "NO NEXT LEAD",
            id="follow-deduction",
            disabled=True,
        )


class InvestigationScene(Screen):
    """
    Base class for every playable investigation scene.

    DATA ORGANIZATION:

        Global InvestigationState
            remembers only IDs / progress

        Scene clue_data.py
            stores clue text, notebook text, deductions, requirements,
            and selected previous information

    Each scene connects its own data with class attributes such as:

        scene_id = SCENE_ID
        clue_data = CLUES
        deduction_data = DEDUCTIONS
        relevant_previous_clues = RELEVANT_PREVIOUS_CLUES
    """

    # Empty defaults for a new scene.
    scene_id = "unnamed"
    clue_data: dict = {}
    deduction_data: dict = {}
    relevant_previous_clues: list = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_class("gameplay-scene")

        # Hidden hold-interaction state.
        self._held_interaction: str | None = None
        self._held_token: str | None = None
        self._wobble_start_timer: Timer | None = None
        self._activate_timer: Timer | None = None
        self._word_wobble_timer: Timer | None = None
        self._word_wobble_frame = 0
        self._word_wobble_active = False
        self._mouse_is_captured = False

    # =================================================================
    # PERMANENT SIDEBAR
    # =================================================================

    def build_sidebar(self) -> InvestigationSidebar:
        """Create the notebook + deduction sidebar for a gameplay scene."""
        return InvestigationSidebar(id="side-column")

    def refresh_sidebar(self) -> None:
        """
        Show only information relevant to THIS scene.

        The sidebar contains:
            - selected previous clues this scene explicitly asks for
            - discovered clues from the current scene
            - resolved deductions from the current scene

        It does NOT display the entire investigation history.
        """
        try:
            state = self.app.investigation_state
            notebook_lines: list[str] = []

            # A) Previous clues deliberately selected by this scene.
            for previous in self.relevant_previous_clues:
                source_scene = previous.get("source_scene")
                source_clue = previous.get("source_clue")

                if not state.has_clue(source_scene, source_clue):
                    continue

                notebook_text = previous.get("notebook", source_clue)
                label = previous.get("label")

                if label:
                    notebook_lines.append(f"• {label}: {notebook_text}")
                else:
                    notebook_lines.append(f"• {notebook_text}")

            # B) Clues discovered in the current scene.
            current_scene_clue_count = 0

            for clue_id, data in self.clue_data.items():
                if not state.has_clue(self.scene_id, clue_id):
                    continue

                current_scene_clue_count += 1
                notebook_text = data.get("notebook", clue_id)
                notebook_lines.append(f"• {notebook_text}")

            self.query_one("#clue-count", Static).update(
                f"Scene clues: {current_scene_clue_count}"
            )

            notebook = self.query_one("#notebook", Static)
            if notebook_lines:
                notebook.update("\n\n".join(notebook_lines))
            else:
                notebook.update("No relevant evidence recorded yet.")

            # C) DEDUCTIONS / CONCLUSION CHOICES
            #
            # If a correct conclusion has already been resolved, show the
            # recorded deduction.
            #
            # Otherwise, show every AVAILABLE conclusion as a clickable
            # choice. A conclusion is available only when all clue IDs in
            # its "requires" list have been discovered.
            resolved_lines: list[str] = []
            available_choices: list[str] = []

            for deduction_id, data in self.deduction_data.items():
                if state.has_deduction(self.scene_id, deduction_id):
                    resolved_lines.append(
                        f"• {escape(str(data.get('text', deduction_id)))}"
                    )
                    continue

                if not self.deduction_is_available(deduction_id):
                    continue

                option_text = escape(
                    str(
                        data.get(
                            "option",
                            data.get("text", deduction_id),
                        )
                    )
                )

                # This is a NORMAL visible menu action.
                #
                # It is intentionally different from the hidden [[word]]
                # interaction system used inside story prose.
                available_choices.append(
                    f"[@click=screen.choose_deduction({deduction_id!r})]"
                    f"CONCLUDE[/]: {option_text}"
                )

            deduction_list = self.query_one(
                "#deduction-list",
                Static,
            )

            if resolved_lines:
                deduction_list.update(
                    "\n\n".join(resolved_lines)
                )

            elif available_choices:
                deduction_list.update(
                    "\n\n".join(available_choices)
                )

            else:
                deduction_list.update(
                    "Gather more evidence before drawing a conclusion."
                )

            # D) Enable FOLLOW only if THIS scene can follow the current lead.
            follow_button = self.query_one("#follow-deduction", Button)
            lead_id = state.current_lead

            if lead_id is not None and self.can_follow_deduction(lead_id):
                follow_button.label = f"FOLLOW: {lead_id.upper()}"
                follow_button.disabled = False
            else:
                follow_button.label = "NO NEXT LEAD"
                follow_button.disabled = True

        except Exception:
            # The widgets can briefly be unavailable during mount/unmount.
            pass

    # =================================================================
    # CLUES / DEDUCTIONS
    # =================================================================

    def inspect(self, clue_id: str) -> None:
        """
        Default examination behavior for normal clues.

        Discovering clues does NOT automatically pick a conclusion.
        It only makes deduction choices available when their requirements
        have been satisfied.
        """
        if clue_id not in self.clue_data:
            return

        clue = self.clue_data[clue_id]

        detail = self.query_one(
            "#detail",
            Static,
        )

        detail.update(
            clue.get(
                "description",
                clue_id,
            )
        )

        # Only the ID is stored globally.
        self.app.investigation_state.discover_clue(
            self.scene_id,
            clue_id,
        )

        # The deduction menu may have changed because another requirement
        # has now been satisfied.
        self.refresh_sidebar()

        detail.scroll_visible()

    def deduction_is_available(
        self,
        deduction_id: str,
    ) -> bool:
        """
        Return True when ALL clues required by a conclusion were found.

        Example in clue_data.py:

            "requires": [
                "windows",
                "ticket",
            ]

        BOTH clues must be discovered.
        """
        if deduction_id not in self.deduction_data:
            return False

        state = self.app.investigation_state
        data = self.deduction_data[deduction_id]

        required_clues = data.get(
            "requires",
            [],
        )

        return all(
            state.has_clue(
                self.scene_id,
                clue_id,
            )
            for clue_id in required_clues
        )

    def action_choose_deduction(
        self,
        deduction_id: str,
    ) -> None:
        """
        Called when the player clicks one of the visible CONCLUDE options
        in the permanent deduction menu.

        Correct conclusion:
            - records the deduction ID
            - shows feedback
            - optionally unlocks next_lead

        Wrong conclusion:
            - shows why it does not fit
            - records nothing
            - leaves the choices available so the player can try again
        """

        if deduction_id not in self.deduction_data:
            return

        # Do not allow conclusions before their evidence requirements
        # have actually been satisfied.
        if not self.deduction_is_available(
            deduction_id
        ):
            return

        data = self.deduction_data[
            deduction_id
        ]

        detail = self.query_one(
            "#detail",
            Static,
        )

        feedback = data.get(
            "feedback",
            data.get(
                "text",
                deduction_id,
            ),
        )

        # ---------------------------------------------------------
        # WRONG CONCLUSION
        # ---------------------------------------------------------
        if not data.get(
            "correct",
            True,
        ):
            detail.update(
                feedback
            )

            # IMPORTANT:
            # We deliberately do NOT call resolve_deduction().
            #
            # The player can reconsider and choose another conclusion.
            self.refresh_sidebar()
            detail.scroll_visible()
            return

        # ---------------------------------------------------------
        # CORRECT CONCLUSION
        # ---------------------------------------------------------
        state = self.app.investigation_state

        state.resolve_deduction(
            self.scene_id,
            deduction_id,
            next_lead=data.get(
                "next_lead"
            ),
        )

        detail.update(
            feedback
        )

        self.refresh_sidebar()
        detail.scroll_visible()

    def evaluate_deductions(self) -> None:
        """
        Compatibility helper.

        Older versions automatically RESOLVED deductions here.

        The new model does not choose for the player. This method now only
        refreshes the deduction menu so available conclusions can appear.
        """
        self.refresh_sidebar()

    def can_follow_deduction(self, lead_id: str) -> bool:
        """Override in a scene that knows how to follow a lead."""
        return False

    def follow_deduction(self, lead_id: str) -> None:
        """Override in a scene that owns the navigation for a lead."""
        return

    @on(Button.Pressed, "#follow-deduction")
    def handle_follow_deduction(self, event: Button.Pressed) -> None:
        """Shared event handler for the permanent deduction button."""
        state = self.app.investigation_state
        lead_id = state.current_lead

        if lead_id is None or not self.can_follow_deduction(lead_id):
            return

        # The lead was followed; keep the resolved deduction ID but clear the
        # temporary navigation destination.
        state.current_lead = None
        self.follow_deduction(lead_id)
        event.stop()

    # =================================================================
    # SIMPLE [[TAG]] SCENE WRITING
    # =================================================================

    def scene(self, prose: str) -> Text:
        """
        Convert ordinary prose into Rich Text containing hidden interactions.

        Example:

            return self.scene(
                "Rain presses against the [[windows]]."
            )

        Tag formats:

            [[windows]]

                visible: windows
                ID:      windows

            [[hand nail|nail]]

                visible: hand nail
                ID:      nail
        """

        result = Text()
        previous_end = 0

        for occurrence, match in enumerate(
            SCENE_TAG_PATTERN.finditer(prose)
        ):
            # Add normal prose before this [[tag]].
            result.append(
                prose[previous_end:match.start()]
            )

            tag_contents = match.group(1)

            if "|" in tag_contents:
                visible_text, interaction_id = tag_contents.split(
                    "|",
                    1,
                )
            else:
                visible_text = tag_contents
                interaction_id = tag_contents

            visible_text = visible_text.strip()
            interaction_id = interaction_id.strip()

            # Malformed tag: leave it visible rather than crashing.
            if not visible_text or not interaction_id:
                result.append(
                    match.group(0)
                )
                previous_end = match.end()
                continue

            # Stable unique token for THIS occurrence.
            interaction_token = (
                f"{interaction_id}:{occurrence}"
            )

            display_text = visible_text

            # Only the exact held word/span wobbles.
            if (
                self._word_wobble_active
                and interaction_token == self._held_token
            ):
                display_text = wobble_word(
                    visible_text,
                    self._word_wobble_frame,
                )

            result.append(
                hidden_word(
                    visible_text=visible_text,
                    interaction_id=interaction_id,
                    interaction_token=interaction_token,
                    display_text=display_text,
                )
            )

            previous_end = match.end()

        # Add normal prose after the final tag.
        result.append(
            prose[previous_end:]
        )

        return result

    def hidden(
        self,
        visible_text: str,
        interaction_id: str,
    ):
        """
        Lower-level hidden-word helper.

        You normally DO NOT need this anymore.

        Prefer:

            self.scene(
                "Look at the [[window]]."
            )
        """

        interaction_token = (
            f"manual:{interaction_id}:{visible_text}"
        )

        display_text = visible_text

        if (
            self._word_wobble_active
            and interaction_token == self._held_token
        ):
            display_text = wobble_word(
                visible_text,
                self._word_wobble_frame,
            )

        return hidden_word(
            visible_text=visible_text,
            interaction_id=interaction_id,
            interaction_token=interaction_token,
            display_text=display_text,
        )

    # =================================================================
    # HOLD / WOBBLE SYSTEM
    # =================================================================

    def refresh_scene_text(self) -> None:
        """
        Rebuild only #scene-text.

        The wobble animation calls this repeatedly.
        """

        try:
            scene_text = self.query_one(
                "#scene-text",
                Static,
            )

            build_scene = getattr(
                self,
                "build_scene",
                None,
            )

            if callable(build_scene):
                scene_text.update(
                    build_scene()
                )

        except Exception:
            pass

    def on_mouse_down(
        self,
        event: events.MouseDown,
    ) -> None:
        """
        Start a hold when the mouse is pressed over a [[tagged]] word.
        """

        if event.button != 1:
            return

        interaction_id = event.style.meta.get(
            INTERACTION_META_KEY
        )

        interaction_token = event.style.meta.get(
            INTERACTION_TOKEN_KEY
        )

        # Ordinary text has no interaction metadata.
        if not interaction_id or not interaction_token:
            return

        self.cancel_hold_interaction()

        self._held_interaction = str(
            interaction_id
        )

        self._held_token = str(
            interaction_token
        )

        self.capture_mouse()
        self._mouse_is_captured = True

        # At 1 second:
        # wobble only the held word.
        self._wobble_start_timer = self.set_timer(
            HOLD_WOBBLE_TIME,
            self.begin_word_wobble,
        )

        # At 1.5 seconds:
        # activate the interaction.
        self._activate_timer = self.set_timer(
            HOLD_ACTIVATE_TIME,
            self.finish_hold_interaction,
        )

        event.stop()

    def on_mouse_up(
        self,
        event: events.MouseUp,
    ) -> None:
        """
        Releasing before activation cancels the hold.
        """

        if event.button != 1:
            return

        if self._held_interaction is None:
            return

        self.cancel_hold_interaction()
        event.stop()

    def begin_word_wobble(self) -> None:
        """
        Called after 1.0 second.
        """

        if self._held_interaction is None:
            return

        self._word_wobble_active = True
        self._word_wobble_frame = 0

        self.refresh_scene_text()

        self._word_wobble_timer = self.set_interval(
            WORD_WOBBLE_INTERVAL,
            self.advance_word_wobble,
        )

    def advance_word_wobble(self) -> None:
        """
        Move the exact held word to its next wobble frame.
        """

        if self._held_interaction is None:
            self.stop_word_wobble()
            return

        self._word_wobble_frame += 1
        self.refresh_scene_text()

    def stop_word_wobble(self) -> None:
        """
        Stop wobbling and restore the normal spelling.
        """

        if self._word_wobble_timer is not None:
            self._word_wobble_timer.stop()
            self._word_wobble_timer = None

        self._word_wobble_active = False
        self._word_wobble_frame = 0

        self.refresh_scene_text()

    def finish_hold_interaction(self) -> None:
        """
        Called after 1.5 seconds.
        """

        if self._held_interaction is None:
            return

        interaction_id = self._held_interaction

        # Restore normal text before the interaction result appears.
        self.cancel_hold_interaction()

        self.activate_interaction(
            interaction_id
        )

    def cancel_hold_interaction(self) -> None:
        """
        Cancel timers, wobble, metadata state, and mouse capture.
        """

        if self._wobble_start_timer is not None:
            self._wobble_start_timer.stop()
            self._wobble_start_timer = None

        if self._activate_timer is not None:
            self._activate_timer.stop()
            self._activate_timer = None

        if (
            self._word_wobble_active
            or self._word_wobble_timer is not None
        ):
            self.stop_word_wobble()

        self._held_interaction = None
        self._held_token = None

        if self._mouse_is_captured:
            self.release_mouse()
            self._mouse_is_captured = False

        self.refresh_scene_text()

    def activate_interaction(
        self,
        interaction_id: str,
    ) -> None:
        """
        Default hidden-object behavior.

        Most hidden interactions are clues, so the base class calls
        inspect(interaction_id) if the scene has an inspect() method.

        Special objects such as lamps/doors can be intercepted by the room.
        """

        self.inspect(
            interaction_id
        )

    # =================================================================
    # MOUNT / CLEANUP
    # =================================================================

    def on_mount(self) -> None:
        """
        Shared gameplay setup.

        Scene subclasses that define on_mount() should call:

            super().on_mount()
        """

        self.evaluate_deductions()
        self.refresh_sidebar()

    def on_unmount(self) -> None:
        """
        Stop active hold timers if the player leaves the scene.
        """

        self.cancel_hold_interaction()
