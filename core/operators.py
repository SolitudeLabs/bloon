from typing import Protocol, runtime_checkable
import numpy as np
from core.state import State


@runtime_checkable
class ResidualOperator(Protocol):
    """Computes spatial operator R(U, t)."""
    def compute_residual(self, state: State) -> np.ndarray: ...


@runtime_checkable
class StorageOperator(Protocol):
    """Computes generalized capacity/storage matrix M(U)."""
    def apply_storage(self, state: State, rate: np.ndarray) -> np.ndarray: ...
    def get_matrix(self, state: State) -> np.ndarray: ...


@runtime_checkable
class JacobianOperator(Protocol):
    """Computes local or global Jacobian dR/dU."""
    def compute_jacobian(self, state: State) -> np.ndarray: ...


@runtime_checkable
class ConstraintOperator(Protocol):
    """Evaluates admissibility constraints g(U) >= 0 or h(U) = 0."""
    def evaluate_constraint(self, state: State) -> np.ndarray: ...


@runtime_checkable
class ObservableOperator(Protocol):
    """Maps State U -> Reduced Observables Y."""
    def evaluate(self, state: State) -> float: ...