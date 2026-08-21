import numpy as np
from core import State, DiscreteDomain, AdmissibilityLayer, ObservableManager, run_simulation
from physics.structural import StructuralDynamicsPhysics
from evolution.backward_euler import BackwardEulerIntegrator
from diagnostics.conservation import compute_oscillator_energy


class EnergyObservable:
    def __init__(self, M: np.ndarray, K: np.ndarray):
        self.M = M
        self.K = K

    def evaluate(self, state: State) -> float:
        return compute_oscillator_energy(state, self.M, self.K)


def main():
    print("=== BLOON Executable Demo: Structural Dynamics (1-DOF) ===")
    M = np.array([[1.0]])
    C = np.array([[0.0]])  # Undamped
    K = np.array([[100.0]]) # omega = 10 rad/s
    
    physics = StructuralDynamicsPhysics(M=M, C=C, K=K)
    topo = DiscreteDomain(num_nodes=1, dim=1)
    
    init_state = State(values=np.array([1.0, 0.0]), time=0.0) # u=1.0, v=0.0
    integrator = BackwardEulerIntegrator()
    admissibility = AdmissibilityLayer([])
    observables = ObservableManager({"total_energy": EnergyObservable(M, K)})

    res = run_simulation(
        initial_state=init_state,
        topology=topo,
        residual_op=physics,
        storage_op=physics,
        jacobian_op=physics,
        integrator=integrator,
        admissibility=admissibility,
        observables=observables,
        dt=0.005,
        num_steps=20
    )

    print(f"Initial Energy: {res.observable_history[0]['total_energy']:.6f}")
    print(f"Final Energy  : {res.observable_history[-1]['total_energy']:.6f}")


if __name__ == "__main__":
    main()