import numpy as np
from core.state import State


class StructuralDynamicsPhysics:
    """
    N-DOF Structural Oscillator: M u'' + C u' + K u = f(t)
    Recast into 1st-order state-space: U = [u, v]^T
    State rate:
    d/dt [u] = [          v          ]
    d/dt [v]   [ M^{-1}(f - C v - K u) ]
    """
    def __init__(self, M: np.ndarray, C: np.ndarray, K: np.ndarray):
        self.M = np.atleast_2d(M)
        self.C = np.atleast_2d(C)
        self.K = np.atleast_2d(K)
        self.dof = self.M.shape[0]
        self.M_inv = np.linalg.inv(self.M)

    def compute_residual(self, state: State) -> np.ndarray:
        u = state.values[:self.dof]
        v = state.values[self.dof:]
        
        f_ext = np.zeros(self.dof)  # Unforced free response
        a = self.M_inv @ (f_ext - self.C @ v - self.K @ u)
        
        return np.concatenate([v, a])

    def get_matrix(self, state: State) -> np.ndarray:
        return np.eye(2 * self.dof)

    def apply_storage(self, state: State, rate: np.ndarray) -> np.ndarray:
        return rate

    def compute_jacobian(self, state: State) -> np.ndarray:
        Zero = np.zeros((self.dof, self.dof))
        Eye = np.eye(self.dof)
        
        J_top = np.hstack([Zero, Eye])
        J_bot = np.hstack([-self.M_inv @ self.K, -self.M_inv @ self.C])
        
        return np.vstack([J_top, J_bot])