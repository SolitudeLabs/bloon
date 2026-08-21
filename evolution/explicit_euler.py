import numpy as np
from core.state import State
from core.operators import ResidualOperator, StorageOperator, JacobianOperator


class ExplicitEulerIntegrator:
    """
    Explicit Euler Integrator:
    M * (U_{n+1} - U_n) / dt = R(U_n, t_n) => U_{n+1} = U_n + dt * M^{-1} * R(U_n, t_n)
    """
    def step(
        self,
        state: State,
        residual_op: ResidualOperator,
        storage_op: StorageOperator,
        jacobian_op: JacobianOperator,
        dt: float
    ) -> State:
        R = residual_op.compute_residual(state)
        M = storage_op.get_matrix(state)
        
        # Solve M * dU = R * dt
        delta_u = np.linalg.solve(M, R * dt)
        
        next_values = state.values + delta_u
        return State(values=next_values, time=state.time + dt, metadata=state.metadata.copy())