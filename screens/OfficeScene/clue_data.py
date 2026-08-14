# Investigation DATA belonging to the Office scene.
#
# office_scene.py handles HOW the room behaves.
# clue_data.py stores WHAT John can learn and deduce here.
#
# This Office is deliberately a SMALL MODEL SCENE.
# It demonstrates:
#
#     2 clues
#        ↓
#     deduction choices unlock
#        ↓
#     wrong conclusion OR correct conclusion
#        ↓
#     correct conclusion unlocks the Train


SCENE_ID = "office"


# =====================================================================
# CLUES
# =====================================================================
#
# Each clue has:
#
#     description
#         Full examination text shown in the main scene.
#
#     notebook
#         Short version shown in JOHN'S NOTEBOOK.
#
CLUES = {
    # -------------------------------------------------------------
    # CLUE 1
    # -------------------------------------------------------------
    "windows": {
        "description": (
            "John moves closer to the windows.\n\n"
            "Rainwater crawls down the glass. "
            "One of the windows has been left slightly open."
        ),

        "notebook": (
            "One of the office windows was left slightly open."
        ),
    },

    # -------------------------------------------------------------
    # CLUE 2
    # -------------------------------------------------------------
    "ticket": {
        "description": (
            "John picks up the folded ticket stub.\n\n"
            "It is a train ticket. "
            "The printed details are still readable."
        ),

        "notebook": (
            "A train ticket stub was left on the office desk."
        ),
    },
}


# =====================================================================
# DEDUCTION CHOICES
# =====================================================================
#
# The deduction menu does NOT automatically choose the answer.
#
# When all clue IDs inside "requires" have been discovered,
# this conclusion becomes clickable in the DEDUCTIONS panel.
#
#
# FIELDS
# ------
#
# option
#     Text shown as a clickable conclusion.
#
# text
#     Final deduction text stored/displayed after the CORRECT choice.
#
# requires
#     ALL of these clues must be found before this choice appears.
#
# correct
#     True  = this is a valid conclusion.
#     False = this is a wrong conclusion.
#
# feedback
#     Text shown in the main detail box after choosing the conclusion.
#
# next_lead
#     Optional destination unlocked by a correct conclusion.
#
#
# IMPORTANT:
#
# Both conclusions below require BOTH clues:
#
#     "windows"
#     "ticket"
#
# This is the same pattern you can use later with:
#
#     "requires": ["clue_1", "clue_2", "clue_3"]
#
DEDUCTIONS = {
    # -------------------------------------------------------------
    # CORRECT CONCLUSION
    # -------------------------------------------------------------
    "office_to_train": {
        "option": (
            "The ticket is the stronger lead. Follow the train."
        ),

        "text": (
            "The train ticket gives John a concrete next lead."
        ),

        "requires": [
            "windows",
            "ticket",
        ],

        "correct": True,

        "feedback": (
            "The open window raises questions, but the ticket gives John "
            "something concrete to follow. The next lead is the train."
        ),

        "next_lead": "train",
    },

    # -------------------------------------------------------------
    # WRONG CONCLUSION
    # -------------------------------------------------------------
    "office_break_in": {
        "option": (
            "Someone entered the office through the open window."
        ),

        # A wrong conclusion is never saved as the resolved deduction,
        # but keeping a text field here makes the data structure consistent.
        "text": (
            "Someone entered through the office window."
        ),

        # The option does not appear until the SAME evidence is available.
        "requires": [
            "windows",
            "ticket",
        ],

        "correct": False,

        "feedback": (
            "The open window makes that possible, but the conclusion ignores "
            "the train ticket on the desk. John needs an explanation that "
            "accounts for both clues."
        ),

        # Wrong conclusions do not unlock a destination.
        "next_lead": None,
    },
}


# =====================================================================
# PREVIOUS INFORMATION
# =====================================================================
#
# Office is currently the first gameplay scene.
RELEVANT_PREVIOUS_CLUES = []
