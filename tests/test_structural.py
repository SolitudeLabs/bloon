import pytest
import numpy as np
from core import State, DiscreteDomain, AdmissibilityLayer, ObservableManager, run_simulation
from physics.structural import StructuralDynamicsPhysics
from evolution.backward_euler import BackwardEulerIntegrator
from diagnostics.error import compute_field_error


def test_structural_oscillator_exact_comparison():
    """
    Verifies 1-DOF undamped free vibration against exact solution:
    u(t) = cos(omega * t), v(t) = -omega * sin(omega * t)
    """
    omega = 10.0
    M = np.array([[1.0]])
    C = np.array([[0.0]])
    K = np.array([[omega**2]])
    
    physics = StructuralDynamicsPhysics(M=M, C=C, K=K)
    topo = DiscreteDomain(num_nodes=1, dim=1)
    
    u0 = np.array([1.0, 0.0])
    init_state = State(values=u0, time=0.0)
    
    dt = 0.001
    t_final = 0.05
    num_steps = int(t_final / dt)

    res = run_simulation(
        initial_state=init_state,
        topology=topo,
        residual_op=physics,
        storage_op=physics,
        jacobian_op=physics,
        integrator=BackwardEulerIntegrator(),
        admissibility=AdmissibilityLayer([]),
        observables=ObservableManager({}),
        dt=dt,
        num_steps=num_steps
    )

    final_state = res.state_history[-1].values
    exact_u = np.cos(omega * t_final)
    exact_v = -omega * np.sin(omega * t_final)
    exact = np.array([exact_u, exact_v])

    err = compute_field_error(final_state, exact)
    assert err.max_error < 0.05