from dataclasses import dataclass, field
from typing import Dict, Any
import numpy as np


@dataclass
class State:
    """
    Generic computational state vector U(x, t) at time t.
    Abstracts physical field DOFs without hardcoding specific physics.
    """
    values: np.ndarray
    time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "State":
        return State(
            values=self.values.copy(),
            time=self.time,
            metadata=dict(self.metadata)
        )

    def __len__(self) -> int:
        return len(self.values)