import numpy as np
from core import State, Topology1D, PositivityConstraint, AdmissibilityLayer, ObservableManager, run_simulation
from physics.reaction_diffusion import ReactionDiffusionPhysics
from evolution.backward_euler import BackwardEulerIntegrator
from diagnostics.conservation import compute_integrated_mass_1d


class TotalMassObservable:
    def __init__(self, topo: Topology1D):
        self.topo = topo
        
    def evaluate(self, state: State) -> float:
        return compute_integrated_mass_1d(state, self.topo)


def main():
    print("=== BLOON Executable Demo: 1D Reaction-Diffusion ===")
    topo = Topology1D(num_nodes=51, x_min=0.0, x_max=1.0)
    physics = ReactionDiffusionPhysics(topology=topo, D=0.01, k=1.0)
    
    # Localized Gaussian pulse initial condition
    c0 = 0.5 * np.exp(-100.0 * (topo.nodes - 0.5)**2)
    init_state = State(values=c0, time=0.0)

    integrator = BackwardEulerIntegrator()
    admissibility = AdmissibilityLayer([PositivityConstraint()])
    observables = ObservableManager({"total_mass": TotalMassObservable(topo)})

    res = run_simulation(
        initial_state=init_state,
        topology=topo,
        residual_op=physics,
        storage_op=physics,
        jacobian_op=physics,
        integrator=integrator,
        admissibility=admissibility,
        observables=observables,
        dt=0.02,
        num_steps=10
    )

    print(f"Initial Total Mass: {res.observable_history[0]['total_mass']:.6f}")
    print(f"Final Total Mass  : {res.observable_history[-1]['total_mass']:.6f}")
    print(f"Positivity Check  : {'PASS' if res.admissibility_reports[-1].passed else 'FAIL'}")


if __name__ == "__main__":
    main()