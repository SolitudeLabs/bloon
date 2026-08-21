from dataclasses import dataclass
from typing import List, Protocol
import numpy as np
from core.state import State


@dataclass
class AdmissibilityReport:
    passed: bool
    violations: List[str]


class Constraint(Protocol):
    def check(self, state: State) -> bool: ...
    def name(self) -> str: ...


class PositivityConstraint:
    """Enforces non-negative values (e.g. concentration, absolute temperature)."""
    def __init__(self, tol: float = -1e-12):
        self.tol = tol

    def check(self, state: State) -> bool:
        return bool(np.all(state.values >= self.tol))

    def name(self) -> str:
        return "PositivityConstraint (U >= 0)"


class AdmissibilityLayer:
    """Verifies that the state respects thermodynamic and physical bounds."""
    def __init__(self, constraints: List[Constraint]):
        self.constraints = constraints

    def verify(self, state: State) -> AdmissibilityReport:
        violations = []
        for c in self.constraints:
            if not c.check(state):
                violations.append(f"Violation of {c.name()} at t={state.time:.4f}")
        return AdmissibilityReport(passed=len(violations) == 0, violations=violations)