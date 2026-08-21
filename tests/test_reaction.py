import pytest
import numpy as np
from core import State, Topology1D, PositivityConstraint, AdmissibilityLayer, ObservableManager, run_simulation
from physics.reaction_diffusion import ReactionDiffusionPhysics
from evolution.backward_euler import BackwardEulerIntegrator


def test_reaction_diffusion_positivity_admissibility():
    """Verifies that positive initial states respect the PositivityConstraint."""
    topo = Topology1D(num_nodes=31, x_min=0.0, x_max=1.0)
    physics = ReactionDiffusionPhysics(topology=topo, D=0.01, k=1.0)
    
    c0 = np.abs(np.sin(np.pi * topo.nodes))
    init_state = State(values=c0, time=0.0)

    res = run_simulation(
        initial_state=init_state,
        topology=topo,
        residual_op=physics,
        storage_op=physics,
        jacobian_op=physics,
        integrator=BackwardEulerIntegrator(),
        admissibility=AdmissibilityLayer([PositivityConstraint()]),
        observables=ObservableManager({}),
        dt=0.01,
        num_steps=5
    )

    for report in res.admissibility_reports:
        assert report.passed is True