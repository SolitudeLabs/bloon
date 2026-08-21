import pytest
import numpy as np
from core import State, Topology1D, DiscreteDomain, PositivityConstraint, AdmissibilityLayer, ObservableManager, run_simulation
from physics.heat import HeatPhysics
from physics.reaction_diffusion import ReactionDiffusionPhysics
from physics.structural import StructuralDynamicsPhysics
from evolution.backward_euler import BackwardEulerIntegrator


def test_bloon_architectural_agnosticism():
    """
    CORE ARCHITECTURE TEST:
    Executes THREE mathematically distinct physical models through the EXACT same 
    run_simulation pipeline using Backward Euler integration.
    Proves that the computational infrastructure is domain-agnostic.
    """
    integrator = BackwardEulerIntegrator()

    # 1. Heat Setup
    topo_h = Topology1D(num_nodes=11)
    phys_h = HeatPhysics(topo_h)
    state_h = State(values=np.ones(11), time=0.0)

    # 2. Reaction Setup
    topo_r = Topology1D(num_nodes=11)
    phys_r = ReactionDiffusionPhysics(topo_r)
    state_r = State(values=np.ones(11)*0.5, time=0.0)

    # 3. Structural Setup
    topo_s = DiscreteDomain(num_nodes=1, dim=1)
    phys_s = StructuralDynamicsPhysics(M=np.eye(1), C=np.eye(1), K=np.eye(1))
    state_s = State(values=np.array([1.0, 0.0]), time=0.0)

    models = [
        (state_h, topo_h, phys_h),
        (state_r, topo_r, phys_r),
        (state_s, topo_s, phys_s)
    ]

    for state, topo, phys in models:
        res = run_simulation(
            initial_state=state,
            topology=topo,
            residual_op=phys,
            storage_op=phys,
            jacobian_op=phys,
            integrator=integrator,
            admissibility=AdmissibilityLayer([PositivityConstraint()]),
            observables=ObservableManager({}),
            dt=0.01,
            num_steps=2
        )
        assert len(res.state_history) == 3
        assert res.state_history[-1].time == pytest.approx(0.02)