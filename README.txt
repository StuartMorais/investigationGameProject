

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
