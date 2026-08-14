# Investigation DATA belonging to the Train scene.
#
# The Train does NOT inherit the entire Office notebook.
#
# It deliberately chooses which old information remains relevant.

from screens.OfficeScene.clue_data import CLUES as OFFICE_CLUES


SCENE_ID = "train"


# Empty until the Train story is written.
CLUES = {}


# Empty until the Train story is written.
DEDUCTIONS = {}


# =====================================================================
# RELEVANT PREVIOUS CLUES
# =====================================================================
#
# This example deliberately brings TWO Office clues forward.
#
# That demonstrates how a later scene can pull only the exact information
# it needs.
#
RELEVANT_PREVIOUS_CLUES = [
    {
        "source_scene": "office",
        "source_clue": "windows",
        "label": "From the Office",
        "notebook": OFFICE_CLUES["windows"]["notebook"],
    },

    {
        "source_scene": "office",
        "source_clue": "ticket",
        "label": "From the Office",
        "notebook": OFFICE_CLUES["ticket"]["notebook"],
    },
]
