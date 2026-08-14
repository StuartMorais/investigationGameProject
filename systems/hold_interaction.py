# Shared settings and helper functions for hidden hold interactions.
#
# This file applies to EVERY normal gameplay scene.
#
# Scene authors do NOT need to use Rich/Textual markup directly.
# They can write:
#
#     [[windows]]
#
# or:
#
#     [[floorboard|hidden_key]]
#
# screens/base_scene.py converts those tags into hidden interactive words.

# Rich Style lets us attach invisible metadata to individual words.
from rich.style import Style

# Rich Text lets us build styled text without making it look like a button.
from rich.text import Text


# Invisible metadata keys stored inside every hidden interaction word.
INTERACTION_META_KEY = "investigation_interaction"
INTERACTION_TOKEN_KEY = "investigation_interaction_token"


# Hold for 1 second before the word begins wobbling.
HOLD_WOBBLE_TIME = 1.0


# Hold for 1.5 seconds before the object activates.
HOLD_ACTIVATE_TIME = 1.5


# How quickly the held word changes wobble frames.
WORD_WOBBLE_INTERVAL = 0.07


# Alternate glyphs used to imitate the old "watch" effect.
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
    Return one wobble frame for a hidden word.

    Only one character changes at a time.

    Example:

        lamp
        ʟamp
        lɑmp
        laᴍp
        lamᴘ
        lamp
    """

    if not visible_text:
        return visible_text

    cycle_length = len(visible_text) + 2
    frame = frame_index % cycle_length

    # First and last frames show the normal word.
    if frame == 0 or frame == cycle_length - 1:
        return visible_text

    character_index = frame - 1
    characters = list(visible_text)
    original = characters[character_index]

    # Use a small-cap / alternate glyph when one exists.
    replacement = WOBBLE_GLYPHS.get(original.lower())

    # Fallback for letters/symbols without an alternate glyph.
    if replacement is None:
        replacement = original.upper()

    characters[character_index] = replacement
    return "".join(characters)


def hidden_word(
    visible_text: str,
    interaction_id: str,
    interaction_token: str,
    display_text: str | None = None,
) -> Text:
    """
    Create one hidden interactive text span.

    visible_text:
        What the player sees.

    interaction_id:
        What the scene receives when the interaction activates.

    interaction_token:
        Unique ID for THIS occurrence in the prose.

        This matters if the same interaction ID appears more than once.
        Only the exact word being held should wobble.

    display_text:
        Temporary visual version used during the wobble animation.
    """

    # Metadata does not add color, underline, or any visible clue marker.
    invisible_style = Style.from_meta(
        {
            INTERACTION_META_KEY: interaction_id,
            INTERACTION_TOKEN_KEY: interaction_token,
        }
    )

    text_to_show = visible_text if display_text is None else display_text

    return Text(
        text_to_show,
        style=invisible_style,
    )
