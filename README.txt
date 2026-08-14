A TERMINAL INVESTIGATION GAME
===============================================

This project is a text-based investigation game built with Python and Textual.

The main idea is simple:

    The player reads normal prose.
    Some words are secretly interactive.
    The player has to NOTICE them without the game highlighting them.

Example:

    Rain presses against the [[windows]].

The player sees:

    Rain presses against the windows.

"windows" looks exactly like ordinary text, but it can be interacted with.


================================================
1. HOW TO RUN THE GAME
================================================

Requirement:

    Python 3.9 or newer

Install the project dependency once:

    python -m pip install -r requirements.txt

Then run:

    python main.py

If your computer uses the Python launcher instead:

    py -m pip install -r requirements.txt
    py main.py


================================================
2. PROJECT STRUCTURE
================================================

Investigation/
|
|-- main.py
|     Starts the game.
|
|-- app.py
|     Creates the main Textual application.
|     Opens the Main Menu when the game starts.
|
|-- styles.tcss
|     Controls colors, borders, spacing, layouts,
|     notebook position, small-window behavior, etc.
|
|-- requirements.txt
|     Lists external Python packages required by the game.
|
|-- systems/
|   |
|   |-- hold_interaction.py
|       Contains the GLOBAL hidden-word interaction rules:
|
|           Hold 1.0 second -> word starts wobbling
|           Hold 1.5 seconds -> interaction activates
|           Release early    -> interaction cancels
|
|       Changing the timing here changes the behavior
|       for every gameplay scene.
|
|-- screens/
    |
    |-- base_scene.py
    |     Contains InvestigationScene.
    |
    |     Every normal gameplay room should inherit from this.
    |     It handles:
    |
    |         [[hidden tags]]
    |         mouse holding
    |         wobble animation
    |         interaction activation
    |         cancellation
    |
    |-- Menus/
    |   |
    |   |-- main_menu.py
    |       The Main Menu.
    |
    |       The menu DOES NOT use the hidden hold system.
    |       Menu buttons are normal buttons.
    |
    |-- OfficeScene/
        |
        |-- office_scene.py
        |     The Office room.
        |     Contains room layout, prose, room state,
        |     and what interactions do.
        |
        |-- clue_data.py
              Contains the Office's actual clue text
              and notebook entries.


================================================
3. THE MOST IMPORTANT RULE
================================================

Normal gameplay scenes should inherit from:

    InvestigationScene

Example:

    from screens.base_scene import InvestigationScene


    class BedroomSceneScreen(InvestigationScene):
        ...

Do NOT inherit directly from:

    Screen

for normal investigation rooms.

Why?

Because InvestigationScene automatically gives the room:

    hidden interactions
    hold detection
    word wobble
    activation timing
    cancellation

The Main Menu can still use normal Screen because it does not need
the investigation interaction system.


================================================
4. WRITING A SCENE
================================================

Scene writing should look almost like normal prose.

Example:

    def build_scene(self):
        return self.scene(
            "The office is almost completely dark.\n\n"
            "Rain presses against the [[windows]].\n\n"
            "A wooden desk sits beneath the [[lamp]]."
        )

Everything outside [[...]] is normal static text.


================================================
5. HIDDEN INTERACTION TAGS
================================================

Basic tag:

    [[windows]]

The player sees:

    windows

The internal interaction ID is also:

    windows


You can make the visible text different from the internal ID:

    [[hand nail|nail]]

The player sees:

    hand nail

The game receives:

    nail


Another example:

    [[old photograph|photo]]

Player sees:

    old photograph

Interaction ID:

    photo


================================================
6. GLOBAL HOLD BEHAVIOR
================================================

Every [[tagged word]] automatically behaves like this:

    Mouse button down
          |
          v
    Hold for 1.0 second
          |
          v
    ONLY that word begins wobbling
          |
          v
    Keep holding until 1.5 seconds
          |
          v
    Interaction activates


If the player releases before 1.5 seconds:

    nothing activates
    the word returns to normal


The whole screen does NOT shake.

Only the exact word being held wobbles.


================================================
7. WHERE TO CHANGE THE HOLD TIMING
================================================

Open:

    systems/hold_interaction.py

You will find:

    HOLD_WOBBLE_TIME = 1.0
    HOLD_ACTIVATE_TIME = 1.5
    WORD_WOBBLE_INTERVAL = 0.07

Meaning:

    HOLD_WOBBLE_TIME
        How long before the word starts wobbling.

    HOLD_ACTIVATE_TIME
        How long before the interaction activates.

    WORD_WOBBLE_INTERVAL
        How quickly the wobble animation changes frames.


Example:

    HOLD_WOBBLE_TIME = 0.8
    HOLD_ACTIVATE_TIME = 1.2

would change EVERY gameplay scene using InvestigationScene.


================================================
8. CLUES
================================================

A clue is something that can become evidence and appear in the notebook.

Example scene text:

    "Rain presses against the [[windows]]."

When "windows" activates, the Office currently uses:

    inspect("windows")

The clue text lives in:

    screens/OfficeScene/clue_data.py


Example:

    CLUE_DESCRIPTIONS = {
        "windows": (
            "John moves closer to the windows.\n\n"
            "One of them has been left slightly open."
        ),
    }


The short notebook version goes in:

    CLUE_NAMES = {
        "windows": (
            "One office window was left slightly open."
        ),
    }


IMPORTANT:

The ID must match.

Scene:

    [[windows]]

Clue data:

    "windows": (...)


================================================
9. INTERACTIVE OBJECTS THAT ARE NOT CLUES
================================================

Not every interactive object needs to become evidence.

The lamp is the current example.

Scene:

    "A wooden desk sits beneath the [[lamp]]."

But "lamp" is not stored in clue_data.py.

Instead, office_scene.py handles it as ROOM STATE.


Example:

    def activate_interaction(self, interaction_id):

        if interaction_id == "lamp":
            self.toggle_lamp()
            return

        super().activate_interaction(interaction_id)


Meaning:

    lamp
        -> special room behavior

    windows
        -> normal clue behavior


================================================
10. ROOM STATE
================================================

Room state remembers things the player changed.

Example:

    self.lamp_on = False

Later:

    self.lamp_on = True


Then build_scene() can change its writing:

    if self.lamp_on:
        office_light = "The office is dimly lit."
    else:
        office_light = "The office is almost completely dark."


Then:

    return self.scene(
        f"{office_light}\n\n"
        "Rain presses against the [[windows]]."
    )


This lets scenes react to player actions.

Possible future room-state variables:

    self.door_open
    self.drawer_open
    self.window_open
    self.curtains_closed
    self.phone_ringing
    self.safe_unlocked
    self.light_on


================================================
11. THE NOTEBOOK
================================================

Gameplay scenes use a permanent side panel.

Wide terminal:

    +---------------- STORY ----------------+ +--- NOTEBOOK ---+
    |                                      | |                |
    | Room prose                           | | Clues          |
    |                                      | |                |
    +--------------------------------------+ +----------------+

Small terminal:

    +---------------- STORY ----------------+
    |                                      |
    +--------------------------------------+

    +--------------- NOTEBOOK --------------+
    |                                      |
    +--------------------------------------+


The notebook does NOT appear on the Main Menu.


================================================
12. CREATING A NEW SCENE
================================================

A simple way is to copy:

    screens/OfficeScene/

Then rename it.

Example:

    screens/BedroomScene/
        __init__.py
        bedroom_scene.py
        clue_data.py


Inside bedroom_scene.py:

    from screens.base_scene import InvestigationScene


    class BedroomSceneScreen(InvestigationScene):

        def __init__(self):
            super().__init__()

            self.found = set()

        def build_scene(self):
            return self.scene(
                "John enters the bedroom.\n\n"
                "Several [[photos]] lie across the bed.\n\n"
                "The [[window]] is open."
            )


Then create matching clue data:

    CLUE_DESCRIPTIONS = {
        "photos": "John examines the photographs...",
        "window": "Cold rain blows through the open window...",
    }


================================================
13. WHEN TO USE clue_data.py
================================================

Use clue_data.py when something is actual evidence.

Good examples:

    fingerprints
    blood stain
    letter
    photograph
    broken lock
    muddy footprint


Do NOT automatically use clue_data.py for every interactive object.

Examples that might only change room state:

    lamp
    door
    drawer
    curtain
    switch
    chair


A useful rule:

    CLUE
        Something John LEARNS.

    ROOM STATE
        Something John CHANGES.


================================================
14. IMPORTANT FUNCTIONS IN A SCENE
================================================

__init__()

    Starting state for the room.

Example:

    self.found = set()
    self.lamp_on = False


compose()

    Creates the visible Textual widgets.

Example:

    story area
    notebook
    detail box
    leave button


build_scene()

    Creates the actual room prose.

This is where you normally write:

    [[interactive words]]


activate_interaction(interaction_id)

    Decides whether an interaction needs special behavior.

Example:

    lamp -> toggle lamp

Everything else can be passed to normal clue inspection.


inspect(clue_id)

    Handles actual evidence.

Usually:

    shows description
    records clue
    updates notebook


refresh_notebook()

    Updates the notebook after evidence is found.


================================================
15. HOW THE HIDDEN SYSTEM WORKS
================================================

You normally do NOT need to edit this.

But the basic flow is:

    self.scene(...)
          |
          v
    finds [[tags]]
          |
          v
    converts them to invisible Rich metadata
          |
          v
    mouse presses tagged word
          |
          v
    base_scene.py detects metadata
          |
          v
    starts hold timers
          |
          +---- 1.0 sec -> wobble word
          |
          +---- 1.5 sec -> activate interaction


The hidden words have:

    no special color
    no underline
    no hover highlight
    no visible button

The player discovers them by paying attention to the writing.


================================================
16. FILES YOU WILL PROBABLY EDIT MOST
================================================

While creating content, you will usually work in:

    screens/YourScene/your_scene.py

and:

    screens/YourScene/clue_data.py


You should need to edit these less often:

    screens/base_scene.py
    systems/hold_interaction.py
    styles.tcss


A good rule:

    Scene-specific behavior
        -> scene file

    Scene-specific evidence text
        -> clue_data.py

    Behavior every room needs
        -> base_scene.py / systems/

    Visual appearance
        -> styles.tcss


================================================
17. GOOD FIRST THINGS TO EXPERIMENT WITH
================================================

Try adding one hidden clue:

    [[desk]]

Try different visible/internal names:

    [[old photograph|photo]]

Try room state:

    [[drawer]]

Then make the drawer change from:

    "The drawer is closed."

to:

    "The drawer hangs open."

Try making one interaction reveal another object.

Example:

Before:

    "A bookshelf fills the wall."

After examining something:

    "A bookshelf fills the wall. One [[book]] sits backward."


================================================
18. CURRENT DESIGN PHILOSOPHY
================================================

The game should NOT tell the player:

    "CLICK HERE"
    "THIS IS A CLUE"
    "INTERACTIVE OBJECT"

The writing itself should make objects interesting enough for the player
to investigate.

Hidden interactive words should feel like part of the prose.

Highlighted, distorted, or unusual text should only be used when the
NARRATIVE itself wants to draw attention to something.


================================================
19. QUICK REFERENCE
================================================

Hidden interaction:

    [[windows]]


Different visible text / ID:

    [[hand nail|nail]]


Normal scene:

    return self.scene(
        "John sees several [[photos]] on the desk."
    )


Clue description:

    CLUE_DESCRIPTIONS = {
        "photos": "John examines them...",
    }


Notebook entry:

    CLUE_NAMES = {
        "photos": "Several unusual photographs.",
    }


Special interaction:

    def activate_interaction(self, interaction_id):
        if interaction_id == "lamp":
            self.toggle_lamp()
            return

        super().activate_interaction(interaction_id)


Global hold timing:

    systems/hold_interaction.py


================================================
20. MAIN IDEA TO REMEMBER
================================================

When writing a scene, you should mostly be writing prose.

Normal text:

    The room is quiet.

Hidden interaction:

    The [[window]] is open.

Different internal ID:

    A [[dark stain|blood]] marks the carpet.

The complicated interaction code is shared by the project.

You should not have to rebuild it for every room.