# Base class used by EVERY normal gameplay scene.
#
# The Main Menu does NOT inherit from this class.
# Menu buttons therefore continue using normal single-click behavior.

from textual import events

# Timer objects are returned by Textual's set_timer() and set_interval().
from textual.timer import Timer

# Every playable room ultimately comes from Textual's Screen.
from textual.screen import Screen

# Static is the widget containing the room prose.
from textual.widgets import Static

# Shared hold timings and word-wobble helpers.
from systems.hold_interaction import (
    HOLD_ACTIVATE_TIME,
    HOLD_WOBBLE_TIME,
    INTERACTION_META_KEY,
    WORD_WOBBLE_INTERVAL,
    hidden_word,
    wobble_word,
)


class InvestigationScene(Screen):
    """
    Base class for every PLAYABLE investigation scene.

    Universal hidden-word behavior:

        mouse down on hidden word
                ↓
        hold for 1.0 second
                ↓
        ONLY THAT WORD begins wobbling
                ↓
        keep holding until 1.5 seconds
                ↓
        interaction activates

    Release before 1.5 seconds:
        cancel everything

    The screen, story box, and notebook NEVER move.
    """

    def __init__(self, *args, **kwargs) -> None:
        # Let Textual initialize the Screen first.
        super().__init__(*args, **kwargs)

        # Common class available to every gameplay scene in styles.tcss.
        self.add_class("gameplay-scene")

        # Interaction ID currently being held.
        #
        # Example:
        # "windows"
        # "lamp"
        #
        # None means no hidden word is being held.
        self._held_interaction: str | None = None

        # Timer that waits until the 1-second wobble point.
        self._wobble_start_timer: Timer | None = None

        # Timer that waits until the 1.5-second activation point.
        self._activate_timer: Timer | None = None

        # Repeating timer used only while the held WORD is wobbling.
        self._word_wobble_timer: Timer | None = None

        # Current word-wobble animation frame.
        self._word_wobble_frame = 0

        # True only after the player has held for at least 1 second.
        self._word_wobble_active = False

        # Mouse capture lets us still detect release if the cursor moves
        # slightly while the player is holding.
        self._mouse_is_captured = False

    def hidden(self, visible_text: str, interaction_id: str):
        """
        Create a hidden hold-interaction word.

        Scene-writing example:

            self.hidden("windows", "windows")

        The first value is what the player sees.
        The second value is the internal interaction ID.

        This method also decides whether THIS particular word should currently
        display a wobble frame.
        """

        display_text = visible_text

        # Only distort the exact word currently being held.
        if (
            self._word_wobble_active
            and interaction_id == self._held_interaction
        ):
            display_text = wobble_word(
                visible_text,
                self._word_wobble_frame,
            )

        return hidden_word(
            visible_text=visible_text,
            interaction_id=interaction_id,
            display_text=display_text,
        )

    def refresh_scene_text(self) -> None:
        """
        Rebuild only the prose widget.

        Every gameplay scene using this base class should provide:

            build_scene()

        and should display that scene inside:

            id="scene-text"

        This is used by the word-wobble animation.
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
            # Defensive cleanup for moments when a screen is mounting or
            # unmounting and the widget may temporarily not exist.
            pass

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """
        Called when the left mouse button is PRESSED.

        We inspect the invisible Rich metadata under the cursor.
        """

        # Ignore buttons other than normal left-click.
        if event.button != 1:
            return

        # Hidden words created with self.hidden() contain our metadata ID.
        interaction_id = event.style.meta.get(
            INTERACTION_META_KEY
        )

        # Ordinary text has no hidden interaction metadata.
        if not interaction_id:
            return

        # Cancel any previous unfinished hold.
        self.cancel_hold_interaction()

        # Remember which exact object the player is holding.
        self._held_interaction = str(
            interaction_id
        )

        # Capture mouse release even if the cursor shifts slightly.
        self.capture_mouse()
        self._mouse_is_captured = True

        # At 1.0 second, begin wobbling only the held word.
        self._wobble_start_timer = self.set_timer(
            HOLD_WOBBLE_TIME,
            self.begin_word_wobble,
        )

        # At 1.5 seconds, activate the interaction.
        self._activate_timer = self.set_timer(
            HOLD_ACTIVATE_TIME,
            self.finish_hold_interaction,
        )

        # Do not let other handlers process this mouse-down.
        event.stop()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """
        Called when the left mouse button is RELEASED.

        If activation has not happened yet, releasing cancels the hold.
        """

        if event.button != 1:
            return

        if self._held_interaction is None:
            return

        self.cancel_hold_interaction()
        event.stop()

    def begin_word_wobble(self) -> None:
        """
        Called when the player reaches 1.0 second of holding.

        Only the held word begins changing glyphs.
        """

        # The player may have released before the timer fired.
        if self._held_interaction is None:
            return

        self._word_wobble_active = True
        self._word_wobble_frame = 0

        # Redraw immediately so the player sees feedback right away.
        self.refresh_scene_text()

        # Continue changing the held word until activation/release.
        self._word_wobble_timer = self.set_interval(
            WORD_WOBBLE_INTERVAL,
            self.advance_word_wobble,
        )

    def advance_word_wobble(self) -> None:
        """
        Move to the next visual frame of the currently held word.
        """

        if self._held_interaction is None:
            self.stop_word_wobble()
            return

        self._word_wobble_frame += 1

        # Rebuild the prose.
        #
        # self.hidden() changes ONLY the currently held word.
        self.refresh_scene_text()

    def stop_word_wobble(self) -> None:
        """
        Stop the word animation and restore the ordinary spelling.
        """

        if self._word_wobble_timer is not None:
            self._word_wobble_timer.stop()
            self._word_wobble_timer = None

        self._word_wobble_active = False
        self._word_wobble_frame = 0

        # Rebuild the prose one last time so the held word returns to normal.
        self.refresh_scene_text()

    def finish_hold_interaction(self) -> None:
        """
        Called after the hidden word has been held for 1.5 seconds.

        This is when the object actually activates.
        """

        # The player may have released early.
        if self._held_interaction is None:
            return

        # Save the ID before cleanup clears it.
        interaction_id = self._held_interaction

        # Stop wobble/timers and return the word to normal first.
        self.cancel_hold_interaction()

        # Let the specific room decide what this ID does.
        self.activate_interaction(
            interaction_id
        )

    def cancel_hold_interaction(self) -> None:
        """
        Cancel the current hold interaction.

        Used when:
        - the mouse is released early
        - activation finishes
        - another hold begins
        - the player leaves the scene
        """

        # Cancel the pending 1-second timer.
        if self._wobble_start_timer is not None:
            self._wobble_start_timer.stop()
            self._wobble_start_timer = None

        # Cancel the pending 1.5-second timer.
        if self._activate_timer is not None:
            self._activate_timer.stop()
            self._activate_timer = None

        # Stop and reset only the held WORD animation.
        if self._word_wobble_active or self._word_wobble_timer is not None:
            self.stop_word_wobble()

        # Forget the current interaction.
        self._held_interaction = None

        # Return mouse routing to normal.
        if self._mouse_is_captured:
            self.release_mouse()
            self._mouse_is_captured = False

        # Make certain the normal word is displayed after _held_interaction
        # has been cleared.
        self.refresh_scene_text()

    def activate_interaction(self, interaction_id: str) -> None:
        """
        Default behavior for hidden objects.

        Most hidden interactions are clues, so by default we call:

            self.inspect(interaction_id)

        A particular scene can override this for switches, lamps, doors,
        drawers, etc.
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
        Stop any active hold timers when the player leaves the scene.
        """
        self.cancel_hold_interaction()
