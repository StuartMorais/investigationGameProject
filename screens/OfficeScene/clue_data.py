# This file stores clue DATA for the Office scene.
#
# office_scene.py controls HOW the room works.
# clue_data.py stores WHAT actual evidence says.


# Full examination text for REAL clues.
CLUE_DESCRIPTIONS = {
    # "windows" matches the interaction ID used in:
    #
    # self.hidden("windows", "windows")
    "windows": (
        "John moves closer to the windows.\n\n"
        "Rainwater crawls down the glass. "
        "One of the windows has been left slightly open."
    ),
}


# Short notebook text for discovered clues.
CLUE_NAMES = {
    "windows": (
        "One of the office windows was left slightly open."
    ),
}


# The lamp is intentionally NOT listed here.
#
# The lamp changes room state:
#
#     self.lamp_on = False / True
#
# rather than automatically becoming evidence.
