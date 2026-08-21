import numpy as np
from core.state import State
from core.topology import Topology1D
from discretization.fd1d import laplacian_1d_matrix


class ReactionDiffusionPhysics:
    """
    1D Non-Linear Reaction-Diffusion: dc/dt = D * d2c/dx2 + k * c * (1 - c)
    homogeneous Neumann BCs (zero flux).
    """
    def __init__(self, topology: Topology1D, D: float = 0.01, k: float = 1.0):
        self.topology = topology
        self.D = D
        self.k = k
        self.L_mat = laplacian_1d_matrix(topology)
        
        # Zero flux Neumann BCs on laplacian endpoints
        dx = topology.dx
        self.L_mat[0, 0] = -2.0 / (dx**2)
        self.L_mat[0, 1] = 2.0 / (dx**2)
        self.L_mat[-1, -1] = -2.0 / (dx**2)
        self.L_mat[-1, -2] = 2.0 / (dx**2)

    def compute_residual(self, state: State) -> np.ndarray:
        c = state.values
        diffusion = self.D * (self.L_mat @ c)
        reaction = self.k * c * (1.0 - c)
        return diffusion + reaction

    def get_matrix(self, state: State) -> np.ndarray:
        return np.eye(len(state.values))

    def apply_storage(self, state: State, rate: np.ndarray) -> np.ndarray:
        return rate

    def compute_jacobian(self, state: State) -> np.ndarray:
        c = state.values
        diag_react = self.k * (1.0 - 2.0 * c)
        return self.D * self.L_mat + np.diag(diag_react)