from dataclasses import dataclass
import numpy as np


@dataclass
class DiscreteDomain:
    """
    Abstract spatial representation defining nodes and metric spaces.
    """
    num_nodes: int
    dim: int

    @property
    def total_dofs(self) -> int:
        return self.num_nodes


@dataclass
class Topology1D(DiscreteDomain):
    """
    1D Uniform Grid Topology.
    """
    x_min: float
    x_max: float

    def __init__(self, num_nodes: int, x_min: float = 0.0, x_max: float = 1.0):
        super().__init__(num_nodes=num_nodes, dim=1)
        self.x_min = x_min
        self.x_max = x_max

    @property
    def dx(self) -> float:
        return (self.x_max - self.x_min) / (self.num_nodes - 1)

    @property
    def nodes(self) -> np.ndarray:
        return np.linspace(self.x_min, self.x_max, self.num_nodes)