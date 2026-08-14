UNTITLED INVESTIGATION GAME
PROJECT DEVELOPMENT GUIDE
================================================

The story title is intentionally NOT decided yet.


================================================
1. THE IMPORTANT DATA RULE
================================================

Store PROGRESS globally.
Store WRITING inside each scene.

Global InvestigationState remembers only things like:

    office:windows was discovered
    office:office_to_train was resolved
    current lead = train

It does NOT store clue paragraphs or notebook text.

Those stay in each scene's clue_data.py.


================================================
2. WHY THIS PREVENTS SIDEBAR OVERLOAD
================================================

The notebook/deduction sidebar is permanent UI, but its CONTENT is scene-controlled.

Office can show Office evidence.
Train can show Train evidence.

If Train still needs one clue from Office, TrainScene/clue_data.py explicitly
pulls only that clue.

The game does not dump the complete investigation history into every scene.


================================================
3. SCENE FOLDER ORGANIZATION
================================================

screens/OfficeScene/
    office_scene.py
        Room behavior and room state.

    clue_data.py
        Office clue descriptions.
        Office notebook text.
        Office deductions.
        Deduction requirements.


screens/TrainScene/
    train_scene.py
        Train behavior.

    clue_data.py
        Train information.
        Also chooses which older clues are still relevant here.


================================================
4. A NORMAL clue_data.py
================================================

    SCENE_ID = "office"

    CLUES = {
        "windows": {
            "description": (
                "John examines the window..."
            ),

            "notebook": (
                "One window was left slightly open."
            ),
        },
    }

    DEDUCTIONS = {
        "office_to_train": {
            "text": "Next lead: THE TRAIN.",
            "requires": ["windows"],
            "next_lead": "train",
        },
    }

    RELEVANT_PREVIOUS_CLUES = []


================================================
5. CONNECT A SCENE TO ITS DATA
================================================

Inside the scene file:

    from .clue_data import (
        CLUES,
        DEDUCTIONS,
        RELEVANT_PREVIOUS_CLUES,
        SCENE_ID,
    )

Then inside the class:

    scene_id = SCENE_ID
    clue_data = CLUES
    deduction_data = DEDUCTIONS
    relevant_previous_clues = RELEVANT_PREVIOUS_CLUES


================================================
6. PULL ONLY THE OLD INFORMATION YOU NEED
================================================

TrainScene/clue_data.py can do this:

    from screens.OfficeScene.clue_data import CLUES as OFFICE_CLUES

    RELEVANT_PREVIOUS_CLUES = [
        {
            "source_scene": "office",
            "source_clue": "windows",
            "label": "From the Office",
            "notebook": OFFICE_CLUES["windows"]["notebook"],
        },
    ]

That clue appears on the Train only if the player actually found it.

If Train needs no old information:

    RELEVANT_PREVIOUS_CLUES = []


================================================
7. WHY IMPORT THE TEXT INSTEAD OF COPYING IT
================================================

Use:

    OFFICE_CLUES["windows"]["notebook"]

instead of rewriting the same sentence in the Train file.

The Office remains the single source of truth for that clue's wording.


================================================
8. DEDUCTIONS LIVE WITH THE SCENE TOO
================================================

Simple deductions can be data-driven:

    "requires": ["windows"]

InvestigationScene checks whether those local clue IDs were discovered.
If yes, it records only the deduction ID globally and displays the deduction
text from the current scene's clue_data.py.


================================================
9. CLUE VS ROOM STATE
================================================

CLUE:
    Something John learns.
    Put its writing in clue_data.py.

ROOM STATE:
    Something John changes.
    Keep it in scene.py.

Example room state:

    self.lamp_on = False


================================================
10. HIDDEN INTERACTION TAGS
================================================

Normal text:

    The room is quiet.

Interactive word:

    The [[window]] is open.

Different visible text / internal ID:

    A [[dark stain|blood]] marks the carpet.

Global behavior:

    hold 1.0 sec -> only that word wobbles
    hold 1.5 sec -> activates
    release early -> cancels


================================================
11. PERMANENT SIDEBAR
================================================

Every gameplay scene still uses:

    yield self.build_sidebar()

The UI stays permanent.
The information inside it changes according to the current scene.

Wide:

    STORY | NOTEBOOK + DEDUCTIONS

Narrow:

    STORY
    NOTEBOOK + DEDUCTIONS


================================================
12. CURRENT OFFICE -> TRAIN TEST
================================================

For development only:

    discover [[windows]]
        -> Office clue ID is remembered
        -> Office deduction resolves
        -> FOLLOW: TRAIN
        -> Train opens

On the Train, only the previous information selected by
TrainScene/clue_data.py is displayed.

The Train story itself is still a placeholder.


================================================
13. MAIN RULE TO REMEMBER
================================================

Global:
    WHAT happened?

clue_data.py:
    WHAT does it say?

scene.py:
    HOW does the room behave?

That keeps the project organized as the investigation grows.


================================================
14. MODEL: TWO CLUES + RIGHT / WRONG CONCLUSION
================================================

The Office now demonstrates a full small deduction puzzle.

Scene prose contains two clues:

    [[windows]]

and:

    [[ticket stub|ticket]]


OfficeScene/clue_data.py defines both:

    CLUES = {
        "windows": {
            ...
        },

        "ticket": {
            ...
        },
    }


The deduction choices both require BOTH clues:

    "requires": [
        "windows",
        "ticket",
    ]


That means:

    windows found     + ticket missing
        -> no conclusion choices yet

    windows missing   + ticket found
        -> no conclusion choices yet

    windows found     + ticket found
        -> conclusion choices appear


================================================
15. CORRECT CONCLUSION
================================================

Example:

    "office_to_train": {
        "option": (
            "The ticket is the stronger lead. Follow the train."
        ),

        "requires": [
            "windows",
            "ticket",
        ],

        "correct": True,

        "feedback": (
            "..."
        ),

        "next_lead": "train",
    }


When the player chooses a correct conclusion:

    deduction ID is recorded
    feedback appears
    next_lead is unlocked
    FOLLOW: TRAIN becomes available


================================================
16. WRONG CONCLUSION
================================================

Example:

    "office_break_in": {
        "option": (
            "Someone entered through the open window."
        ),

        "requires": [
            "windows",
            "ticket",
        ],

        "correct": False,

        "feedback": (
            "The conclusion ignores part of the evidence..."
        ),

        "next_lead": None,
    }


When the player chooses a wrong conclusion:

    feedback appears
    deduction is NOT recorded
    no next lead is unlocked
    the player can choose again


This makes the deduction menu a reasoning step instead of automatically
solving the puzzle for the player.


================================================
17. REQUIRING MORE THAN TWO CLUES
================================================

Use as many clue IDs as needed:

    "requires": [
        "windows",
        "ticket",
        "letter",
        "footprint",
    ]


The conclusion becomes available only when ALL listed clues were discovered.


================================================
18. IMPORTANT RULE FOR IDs
================================================

The IDs inside "requires" must match keys in that scene's CLUES dictionary.

Example:

    CLUES = {
        "windows": {...},
        "ticket": {...},
    }


Then:

    "requires": [
        "windows",
        "ticket",
    ]


Use simple lowercase IDs such as:

    ticket
    window
    letter
    footprint
    broken_lock

rather than display names such as:

    "Clue 2"


The ID is for the code.
The notebook / description text is for the player.


SIDEBAR LOCATION
----------------
The permanent notebook + deduction sidebar is defined directly in:

    screens/base_scene.py

There is no separate widgets/ folder.
