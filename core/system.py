from dataclasses import dataclass, field
from typing import List, Dict, Any, Protocol
from core.state import State
from core.topology import DiscreteDomain
from core.operators import ResidualOperator, StorageOperator, JacobianOperator
from core.constraints import AdmissibilityLayer, AdmissibilityReport
from core.observables import ObservableManager


class TimeIntegrator(Protocol):
    def step(
        self,
        state: State,
        residual_op: ResidualOperator,
        storage_op: StorageOperator,
        jacobian_op: JacobianOperator,
        dt: float
    ) -> State: ...


@dataclass
class SimulationResult:
    time_history: List[float]
    state_history: List[State]
    observable_history: List[Dict[str, float]]
    admissibility_reports: List[AdmissibilityReport]


def run_simulation(
    initial_state: State,
    topology: DiscreteDomain,
    residual_op: ResidualOperator,
    storage_op: StorageOperator,
    jacobian_op: JacobianOperator,
    integrator: TimeIntegrator,
    admissibility: AdmissibilityLayer,
    observables: ObservableManager,
    dt: float,
    num_steps: int
) -> SimulationResult:
    """
    Canonical BLOON System Execution Pipeline.
    Executes ANY physical model complying with the BLOON contract interface.
    """
    current_state = initial_state.copy()
    
    time_hist = [current_state.time]
    state_hist = [current_state.copy()]
    obs_hist = [observables.evaluate_all(current_state)]
    adm_hist = [admissibility.verify(current_state)]

    for _ in range(num_steps):
        current_state = integrator.step(
            state=current_state,
            residual_op=residual_op,
            storage_op=storage_op,
            jacobian_op=jacobian_op,
            dt=dt
        )
        
        adm_report = admissibility.verify(current_state)
        obs_data = observables.evaluate_all(current_state)

        time_hist.append(current_state.time)
        state_hist.append(current_state.copy())
        obs_hist.append(obs_data)
        adm_hist.append(adm_report)

    return SimulationResult(
        time_history=time_hist,
        state_history=state_hist,
        observable_history=obs_hist,
        admissibility_reports=adm_hist
    )