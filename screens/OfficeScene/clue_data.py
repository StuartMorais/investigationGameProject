# This file stores clue DATA for the Office scene.
#
# office_scene.py controls HOW the room works.
# clue_data.py stores WHAT the clues say.


# Full examination text.
#
# OfficeSceneScreen.inspect() displays this when the player clicks
# a hidden interactive word in the prose.
CLUE_DESCRIPTIONS = {
    # The key "windows" must match:
    #
    #     screen.inspect('windows')
    #
    # inside office_scene.py.
    "windows": (
        "John moves closer to the windows.\n\n"
        "Rainwater crawls down the glass. "
        "One of the windows has been left slightly open."
    ),
}


# Short text that appears in JOHN'S NOTEBOOK after discovering the clue.
CLUE_NAMES = {
    # Use the same clue ID as CLUE_DESCRIPTIONS.
    "windows": (
        "One of the office windows was left slightly open."
    ),
}