from dataclasses import dataclass
import numpy as np


@dataclass
class ErrorMetrics:
    l2_error: float
    max_error: float


def compute_field_error(numerical: np.ndarray, analytical: np.ndarray) -> ErrorMetrics:
    diff = numerical - analytical
    l2_err = float(np.sqrt(np.mean(diff**2)))
    max_err = float(np.max(np.abs(diff)))
    return ErrorMetrics(l2_error=l2_err, max_error=max_err)