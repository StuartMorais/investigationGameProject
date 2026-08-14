# Base class used by EVERY normal gameplay scene.
#
# The Main Menu does NOT inherit from this class.
# Menu buttons therefore continue using normal single-click behavior.

# re is Python's regular-expression module.
# We use it to find [[interactive tags]] inside normal prose.
import re

from textual import events
from textual.timer import Timer
from textual.screen import Screen
from textual.widgets import Static

# Rich Text lets scene() combine ordinary prose and hidden interactions
# into one display object.
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


# Matches text such as:
#
#     [[windows]]
#     [[floorboard|hidden_key]]
#
# It deliberately does not support nested [[tags]].
SCENE_TAG_PATTERN = re.compile(r"\[\[([^\[\]]+?)\]\]")


class InvestigationScene(Screen):
    """
    Base class for every PLAYABLE investigation scene.

    Scene-writing syntax
    --------------------

    Normal text:

        "Rain hits the windows."

    Hidden interaction:

        "Rain hits the [[windows]]."

    Different visible text and internal ID:

        "Something sits beneath the [[floorboard|hidden_key]]."

    Universal behavior
    ------------------

        mouse down
             ↓
        hold 1.0 sec
             ↓
        only that word wobbles
             ↓
        hold 1.5 sec
             ↓
        interaction activates

    Release early:
        cancel
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_class("gameplay-scene")

        # Internal ID of the object currently being held.
        self._held_interaction: str | None = None

        # Unique occurrence token for the exact word currently being held.
        #
        # This prevents two copies of the same interaction ID from wobbling
        # at the same time.
        self._held_token: str | None = None

        self._wobble_start_timer: Timer | None = None
        self._activate_timer: Timer | None = None
        self._word_wobble_timer: Timer | None = None

        self._word_wobble_frame = 0
        self._word_wobble_active = False
        self._mouse_is_captured = False

    def scene(self, prose: str) -> Text:
        """
        Convert normal scene writing into Rich Text with hidden interactions.

        This is the method you should normally use inside build_scene().

        Example:

            def build_scene(self):
                return self.scene(
                    "The office is dark.\\n\\n"
                    "Rain presses against the [[windows]].\\n\\n"
                    "A desk sits beneath the [[lamp]]."
                )

        Tag formats
        -----------

        [[windows]]

            Visible text: windows
            Interaction ID: windows

        [[hand nail|nail]]

            Visible text: hand nail
            Interaction ID: nail

        Everything outside [[...]] stays completely ordinary static text.
        """

        result = Text()
        previous_end = 0

        # Enumerate gives every tag occurrence a stable number.
        #
        # If "windows" appears twice, tokens might become:
        #
        #     windows:0
        #     windows:1
        #
        # so only the exact held occurrence wobbles.
        for occurrence, match in enumerate(SCENE_TAG_PATTERN.finditer(prose)):
            # Add untouched normal prose before this tag.
            result.append(
                prose[previous_end:match.start()]
            )

            tag_contents = match.group(1)

            # [[visible|id]] uses the part after "|" as the internal ID.
            if "|" in tag_contents:
                visible_text, interaction_id = tag_contents.split("|", 1)
            else:
                # [[windows]] means visible text and ID are the same.
                visible_text = tag_contents
                interaction_id = tag_contents

            # Remove accidental spaces around the two pieces.
            visible_text = visible_text.strip()
            interaction_id = interaction_id.strip()

            # If someone writes a malformed empty tag, leave it visible
            # instead of crashing the scene.
            if not visible_text or not interaction_id:
                result.append(match.group(0))
                previous_end = match.end()
                continue

            # Stable unique token for this exact occurrence.
            interaction_token = f"{interaction_id}:{occurrence}"

            # Normally the displayed word is unchanged.
            display_text = visible_text

            # During the 1-second feedback stage, ONLY the exact word/span
            # the player is holding gets the wobble effect.
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

        # Add the normal prose after the final [[tag]].
        result.append(
            prose[previous_end:]
        )

        return result

    def hidden(self, visible_text: str, interaction_id: str):
        """
        Lower-level helper.

        You normally do NOT need this anymore.

        Prefer:

            self.scene("Look at the [[window]].")

        This method remains available for unusual scene-building situations.
        """

        # A manually-created hidden word has a deterministic token.
        interaction_token = f"manual:{interaction_id}:{visible_text}"

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

    def refresh_scene_text(self) -> None:
        """
        Ask the current scene to rebuild only its prose widget.

        The word-wobble animation uses this repeatedly.
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
            # Defensive cleanup while screens mount/unmount.
            pass

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """
        Start a hold only when the mouse is pressed over hidden metadata.
        """

        if event.button != 1:
            return

        interaction_id = event.style.meta.get(
            INTERACTION_META_KEY
        )

        interaction_token = event.style.meta.get(
            INTERACTION_TOKEN_KEY
        )

        # Ordinary text has neither value.
        if not interaction_id or not interaction_token:
            return

        self.cancel_hold_interaction()

        self._held_interaction = str(
            interaction_id
        )

        self._held_token = str(
            interaction_token
        )

        # Keep receiving mouse-up even if the cursor moves slightly.
        self.capture_mouse()
        self._mouse_is_captured = True

        # 1.0 seconds -> wobble only the held word.
        self._wobble_start_timer = self.set_timer(
            HOLD_WOBBLE_TIME,
            self.begin_word_wobble,
        )

        # 1.5 seconds -> activate.
        self._activate_timer = self.set_timer(
            HOLD_ACTIVATE_TIME,
            self.finish_hold_interaction,
        )

        event.stop()

    def on_mouse_up(self, event: events.MouseUp) -> None:
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
        Advance the held word to its next distortion frame.
        """

        if self._held_interaction is None:
            self.stop_word_wobble()
            return

        self._word_wobble_frame += 1
        self.refresh_scene_text()

    def stop_word_wobble(self) -> None:
        """
        Stop the animation and restore normal spelling.
        """

        if self._word_wobble_timer is not None:
            self._word_wobble_timer.stop()
            self._word_wobble_timer = None

        self._word_wobble_active = False
        self._word_wobble_frame = 0

        self.refresh_scene_text()

    def finish_hold_interaction(self) -> None:
        """
        Called at 1.5 seconds.
        """

        if self._held_interaction is None:
            return

        interaction_id = self._held_interaction

        # Restore normal text before performing the interaction.
        self.cancel_hold_interaction()

        self.activate_interaction(
            interaction_id
        )

    def cancel_hold_interaction(self) -> None:
        """
        Stop timers, wobble, and mouse capture.
        """

        if self._wobble_start_timer is not None:
            self._wobble_start_timer.stop()
            self._wobble_start_timer = None

        if self._activate_timer is not None:
            self._activate_timer.stop()
            self._activate_timer = None

        if self._word_wobble_active or self._word_wobble_timer is not None:
            self.stop_word_wobble()

        self._held_interaction = None
        self._held_token = None

        if self._mouse_is_captured:
            self.release_mouse()
            self._mouse_is_captured = False

        # Final redraw after clearing the held token.
        self.refresh_scene_text()

    def activate_interaction(self, interaction_id: str) -> None:
        """
        Default hidden-object behavior.

        Most hidden interactions are clues, so by default:

            self.inspect(interaction_id)

        A room can override this method for lamps, doors, drawers, etc.
        """

        inspect_method = getattr(
            self,
            "inspect",
            None,
        )

        if callable(inspect_method):
            inspect_method(
                interaction_id
            )

    def on_unmount(self) -> None:
        """
        Clean up if the player leaves during a hold.
        """
        self.cancel_hold_interaction()
