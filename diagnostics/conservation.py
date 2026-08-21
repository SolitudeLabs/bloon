import numpy as np
from core.state import State
from core.topology import Topology1D


def compute_integrated_mass_1d(state: State, topology: Topology1D) -> float:
    """Integrates scalar density/concentration over 1D spatial domain via Trapezoidal rule."""
    return float(np.trapezoid(state.values, x=topology.nodes))


def compute_oscillator_energy(state: State, M: np.ndarray, K: np.ndarray) -> float:
    """Computes total mechanical energy E = 1/2 v^T M v + 1/2 u^T K u."""
    dof = M.shape[0]
    u = state.values[:dof]
    v = state.values[dof:]
    
    kinetic = 0.5 * float(v.T @ M @ v)
    potential = 0.5 * float(u.T @ K @ u)
    return kinetic + potential