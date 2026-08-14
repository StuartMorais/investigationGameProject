# Shared investigation progress.
#
# IMPORTANT DESIGN RULE:
# Global state remembers only IDs / progress.
# Actual clue and deduction writing stays in each scene's clue_data.py.

from dataclasses import dataclass, field


@dataclass
class InvestigationState:
    """Small pieces of progress that must survive scene changes."""

    # Namespaced IDs such as "office:windows".
    discovered_clues: set[str] = field(default_factory=set)

    # Namespaced IDs such as "office:office_to_train".
    resolved_deductions: set[str] = field(default_factory=set)

    # Temporary destination unlocked by a deduction.
    current_lead: str | None = None

    @staticmethod
    def clue_key(scene_id: str, clue_id: str) -> str:
        """Create a globally unique clue ID."""
        return f"{scene_id}:{clue_id}"

    @staticmethod
    def deduction_key(scene_id: str, deduction_id: str) -> str:
        """Create a globally unique deduction ID."""
        return f"{scene_id}:{deduction_id}"

    def discover_clue(self, scene_id: str, clue_id: str) -> bool:
        """Remember a clue ID. Return True only on first discovery."""
        key = self.clue_key(scene_id, clue_id)
        if key in self.discovered_clues:
            return False
        self.discovered_clues.add(key)
        return True

    def has_clue(self, scene_id: str, clue_id: str) -> bool:
        """Check whether a clue from a particular scene was found."""
        return self.clue_key(scene_id, clue_id) in self.discovered_clues

    def resolve_deduction(
        self,
        scene_id: str,
        deduction_id: str,
        next_lead: str | None = None,
    ) -> bool:
        """Remember a deduction ID, not its text."""
        key = self.deduction_key(scene_id, deduction_id)
        is_new = key not in self.resolved_deductions
        self.resolved_deductions.add(key)
        if next_lead is not None:
            self.current_lead = next_lead
        return is_new

    def has_deduction(self, scene_id: str, deduction_id: str) -> bool:
        """Check whether a deduction from a scene was resolved."""
        return self.deduction_key(scene_id, deduction_id) in self.resolved_deductions
