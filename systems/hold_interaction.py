# Shared settings and helper functions for hidden hold interactions.
#
# This file applies to EVERY normal gameplay scene.
#
# IMPORTANT:
# The screen itself never moves.
# Only the hidden WORD being held changes appearance after 1 second.

# Rich Style lets us attach invisible metadata to individual words.
from rich.style import Style

# Rich Text lets us build styled text without making it look like a button.
from rich.text import Text


# Invisible metadata key stored inside every hidden interaction word.
INTERACTION_META_KEY = "investigation_interaction"


# Hold for 1 second before the word begins wobbling.
HOLD_WOBBLE_TIME = 1.0


# Hold for 1.5 seconds before the object activates.
HOLD_ACTIVATE_TIME = 1.5


# How quickly the held word changes wobble frames.
WORD_WOBBLE_INTERVAL = 0.07


# Alternate glyphs used to imitate the old "watch" effect.
#
# Example:
#
#     watch
#     ᴡatch
#     wɑtch
#     waᴛch
#     watᴄh
#     watcʜ
#
# Not every letter has a perfect small-cap equivalent, so this dictionary
# contains useful substitutions for common letters.
WOBBLE_GLYPHS = {
    "a": "ɑ",
    "b": "ʙ",
    "c": "ᴄ",
    "d": "ᴅ",
    "e": "ᴇ",
    "f": "ꜰ",
    "g": "ɢ",
    "h": "ʜ",
    "i": "ɪ",
    "j": "ᴊ",
    "k": "ᴋ",
    "l": "ʟ",
    "m": "ᴍ",
    "n": "ɴ",
    "o": "ᴏ",
    "p": "ᴘ",
    "r": "ʀ",
    "s": "ꜱ",
    "t": "ᴛ",
    "u": "ᴜ",
    "v": "ᴠ",
    "w": "ᴡ",
    "y": "ʏ",
}


def wobble_word(visible_text: str, frame_index: int) -> str:
    """
    Return one wobble frame for any hidden word.

    Only ONE character is distorted at a time.

    For example, "lamp" cycles approximately like:

        lamp
        ʟamp
        lɑmp
        laᴍp
        lamᴘ
        lamp

    This keeps the word in the same place in the sentence instead of
    shaking the whole interface.
    """

    if not visible_text:
        return visible_text

    # One normal frame at the start and one normal frame at the end.
    cycle_length = len(visible_text) + 2
    frame = frame_index % cycle_length

    # First and last frame are the normal word.
    if frame == 0 or frame == cycle_length - 1:
        return visible_text

    # Convert frame number into a character position.
    character_index = frame - 1

    characters = list(visible_text)
    original = characters[character_index]

    # Look up a distorted version of this character.
    replacement = WOBBLE_GLYPHS.get(original.lower())

    # If there is no special glyph for this character, use uppercase as a
    # harmless fallback visual change.
    if replacement is None:
        replacement = original.upper()

    characters[character_index] = replacement

    return "".join(characters)


def hidden_word(
    visible_text: str,
    interaction_id: str,
    display_text: str | None = None,
) -> Text:
    """
    Create a hidden interactive word.

    visible_text:
        The normal word written by the scene author.

    interaction_id:
        Internal ID used when the word activates.

    display_text:
        Optional temporary version displayed during the wobble animation.

    The interaction metadata is invisible. No underline, button, or color
    reveals that the word can be held.
    """

    # Metadata only: this adds no visible styling.
    invisible_style = Style.from_meta(
        {
            INTERACTION_META_KEY: interaction_id,
        }
    )

    # Normally display visible_text.
    # During a wobble frame the base scene passes a distorted display_text.
    text_to_show = (
        visible_text
        if display_text is None
        else display_text
    )

    return Text(
        text_to_show,
        style=invisible_style,
    )
