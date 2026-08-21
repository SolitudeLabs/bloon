import pytest
import numpy as np
from core import State, Topology1D, AdmissibilityLayer, ObservableManager, run_simulation
from physics.heat import HeatPhysics
from evolution.backward_euler import BackwardEulerIntegrator
from diagnostics.error import compute_field_error


def test_heat_manufactured_solution_convergence():
    """
    Verifies manufactured solution for 1D heat equation:
    Exact: T(x,t) = e^(-pi^2 * t) * sin(pi * x)
    Tests error reduction under spatial mesh refinement.
    """
    alpha = 1.0
    t_final = 0.05
    dt = 0.001
    
    errors = []
    node_counts = [21, 41]

    for N in node_counts:
        topo = Topology1D(num_nodes=N, x_min=0.0, x_max=1.0)
        physics = HeatPhysics(topology=topo, alpha=alpha)
        
        u0 = np.sin(np.pi * topo.nodes)
        init_state = State(values=u0, time=0.0)
        
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
        exact = np.exp(-(np.pi**2) * t_final) * np.sin(np.pi * topo.nodes)
        err = compute_field_error(final_state, exact)
        errors.append(err.l2_error)

    # Verify L2 error decreases with spatial refinement
    assert errors[1] < errors[0]