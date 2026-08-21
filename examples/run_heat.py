import numpy as np
from core import State, Topology1D, PositivityConstraint, AdmissibilityLayer, ObservableManager, run_simulation
from physics.heat import HeatPhysics
from evolution.backward_euler import BackwardEulerIntegrator


class MaxTempObservable:
    def evaluate(self, state: State) -> float:
        return float(np.max(state.values))


def main():
    print("=== Executable Demo: 1D Heat Transport ===")
    topo = Topology1D(num_nodes=51, x_min=0.0, x_max=1.0)
    physics = HeatPhysics(topology=topo, alpha=1.0)
    
    # Exact initial fundamental mode: T(x,0) = sin(pi * x)
    u0 = np.sin(np.pi * topo.nodes)
    u0[0] = u0[-1] = 0.0
    init_state = State(values=u0, time=0.0)

    integrator = BackwardEulerIntegrator()
    admissibility = AdmissibilityLayer([PositivityConstraint()])
    observables = ObservableManager({"max_temp": MaxTempObservable()})

    res = run_simulation(
        initial_state=init_state,
        topology=topo,
        residual_op=physics,
        storage_op=physics,
        jacobian_op=physics,
        integrator=integrator,
        admissibility=admissibility,
        observables=observables,
        dt=0.01,
        num_steps=10
    )

    print(f"Initial Max Temp: {res.observable_history[0]['max_temp']:.6f}")
    print(f"Final Max Temp  : {res.observable_history[-1]['max_temp']:.6f}")
    print(f"Admissibility   : {'PASS' if res.admissibility_reports[-1].passed else 'FAIL'}")


if __name__ == "__main__":
    main()