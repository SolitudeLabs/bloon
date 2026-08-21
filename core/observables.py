from typing import Dict
from core.state import State
from core.operators import ObservableOperator


class ObservableManager:
    """Decoupled observer collecting system statistics without altering solver loops."""
    def __init__(self, observables: Dict[str, ObservableOperator]):
        self.observables = observables

    def evaluate_all(self, state: State) -> Dict[str, float]:
        return {name: obs.evaluate(state) for name, obs in self.observables.items()}