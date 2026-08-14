

GLOBAL HOLD INTERACTION SYSTEM
------------------------------
All normal gameplay rooms should inherit from:

    InvestigationScene

instead of directly from Textual's Screen.

Example:

    class OfficeSceneScreen(InvestigationScene):

Hidden interactive words are created with:

    self.hidden("windows", "windows")

There is no @click in hidden investigation prose anymore.

Universal behavior:
- Mouse down on a hidden word starts the hold.
- Release before 1.0 seconds: nothing happens.
- At 1.0 seconds: only the hidden word being held begins wobbling.
- At 1.5 seconds: the interaction activates.
- Release before 1.5 seconds: the interaction is cancelled.

The universal timing lives in:

    systems/hold_interaction.py

so changing the timing there changes every gameplay scene.

The Main Menu still inherits directly from Screen and therefore does not
use the hold system.


SCENE WRITING FORMAT
--------------------
Normal gameplay scenes should inherit from:

    InvestigationScene

Write the prose with:

    return self.scene(
        "The office is dark.\n\n"
        "Rain presses against the [[windows]].\n\n"
        "A desk sits beneath the [[lamp]]."
    )

The [[...]] syntax automatically creates a hidden hold interaction.

Same visible word and interaction ID:

    [[windows]]

Different visible text and internal ID:

    [[hand nail|nail]]

    Player sees:
        hand nail

    Scene receives:
        nail

Every tagged word automatically gets the global behavior:

    hold 1.0 sec -> only that word wobbles
    hold 1.5 sec -> interaction activates
    release early -> cancel

Everything outside [[...]] stays ordinary static prose.

You should normally NOT need to use Rich Text or self.hidden() manually.
