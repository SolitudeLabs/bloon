import numpy as np
from core.state import State
from core.topology import Topology1D
from discretization.fd1d import laplacian_1d_matrix


class HeatPhysics:
    """
    1D Heat Equation: dT/dt = alpha * d2T/dx2 with homogeneous Dirichlet BCs.
    """
    def __init__(self, topology: Topology1D, alpha: float = 1.0):
        self.topology = topology
        self.alpha = alpha
        self.L_mat = laplacian_1d_matrix(topology)
        
        # Apply Dirichlet boundary conditions (zero out boundary rows for residual)
        self.L_mat[0, :] = 0.0
        self.L_mat[-1, :] = 0.0

    def compute_residual(self, state: State) -> np.ndarray:
        return self.alpha * (self.L_mat @ state.values)

    def get_matrix(self, state: State) -> np.ndarray:
        return np.eye(len(state.values))

    def apply_storage(self, state: State, rate: np.ndarray) -> np.ndarray:
        return rate

    def compute_jacobian(self, state: State) -> np.ndarray:
        return self.alpha * self.L_mat