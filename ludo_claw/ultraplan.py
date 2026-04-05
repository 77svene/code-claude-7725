from enum import Enum
from typing import Dict, Any

class ExecutionPhase(Enum):
    PLAN = "plan"
    PROPOSE = "propose"
    EXECUTE = "execute"
    DONE = "done"

class UltraPlanEngine:
    """
    State machine for the ULTRAPLAN stage: Plan -> Propose -> Execute loop.
    Enforces the current phase so the model never manages its own state.
    """
    def __init__(self):
        self.current_phase = ExecutionPhase.PLAN
        self.plan_details = None
        self.proposal_details = None
        self.execution_results = []
        self.is_high_complexity = False

    def advance_phase(self) -> ExecutionPhase:
        """Transitions to the next logical phase."""
        if self.current_phase == ExecutionPhase.PLAN:
            self.current_phase = ExecutionPhase.PROPOSE
        elif self.current_phase == ExecutionPhase.PROPOSE:
            self.current_phase = ExecutionPhase.EXECUTE
        elif self.current_phase == ExecutionPhase.EXECUTE:
            self.current_phase = ExecutionPhase.DONE
        return self.current_phase

    def set_plan(self, plan: Dict[str, Any], complexity_marker: bool = False):
        if self.current_phase != ExecutionPhase.PLAN:
            raise ValueError(f"Cannot set plan in phase {self.current_phase}")
        self.plan_details = plan
        self.is_high_complexity = complexity_marker
        self.advance_phase()

    def set_proposal(self, proposal: Dict[str, Any]):
        if self.current_phase != ExecutionPhase.PROPOSE:
            raise ValueError(f"Cannot set proposal in phase {self.current_phase}")
        self.proposal_details = proposal
        self.advance_phase()

    def add_execution_result(self, result: Any):
        if self.current_phase != ExecutionPhase.EXECUTE:
            raise ValueError(f"Cannot execute in phase {self.current_phase}")
        self.execution_results.append(result)

    def mark_done(self):
        if self.current_phase != ExecutionPhase.EXECUTE:
            raise ValueError(f"Must complete execution before marking done.")
        self.advance_phase()

    def get_state(self) -> Dict[str, Any]:
        return {
            "phase": self.current_phase.value,
            "has_plan": self.plan_details is not None,
            "has_proposal": self.proposal_details is not None,
            "execution_count": len(self.execution_results),
            "is_high_complexity": self.is_high_complexity
        }
