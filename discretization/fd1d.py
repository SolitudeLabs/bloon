import numpy as np
from core.topology import Topology1D


def laplacian_1d_matrix(topology: Topology1D) -> np.ndarray:
    """Standard 2nd-order central finite difference 1D Laplacian operator."""
    N = topology.num_nodes
    dx = topology.dx
    diag = -2.0 * np.ones(N)
    off_diag = 1.0 * np.ones(N - 1)
    L = (np.diag(diag) + np.diag(off_diag, k=1) + np.diag(off_diag, k=-1)) / (dx**2)
    return L