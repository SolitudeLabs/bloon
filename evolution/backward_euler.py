import numpy as np
from core.state import State
from core.operators import ResidualOperator, StorageOperator, JacobianOperator


class BackwardEulerIntegrator:
    """
    Implicit Backward Euler Integrator using Newton-Raphson iteration:
    G(U_{n+1}) = M * (U_{n+1} - U_n) - dt * R(U_{n+1}, t_{n+1}) = 0
    Jacobian J_G = M - dt * dR/dU
    """
    def __init__(self, max_iter: int = 20, tol: float = 1e-9):
        self.max_iter = max_iter
        self.tol = tol

    def step(
        self,
        state: State,
        residual_op: ResidualOperator,
        storage_op: StorageOperator,
        jacobian_op: JacobianOperator,
        dt: float
    ) -> State:
        u_n = state.values
        t_next = state.time + dt
        u_next = u_n.copy()
        
        for iteration in range(self.max_iter):
            temp_state = State(values=u_next, time=t_next, metadata=state.metadata)
            R = residual_op.compute_residual(temp_state)
            M = storage_op.get_matrix(temp_state)
            
            # Residual equation G(u_next) = M*(u_next - u_n) - dt * R
            G = M @ (u_next - u_n) - dt * R
            
            if np.linalg.norm(G) < self.tol:
                break
                
            dRdU = jacobian_op.compute_jacobian(temp_state)
            J_G = M - dt * dRdU
            
            delta_u = np.linalg.solve(J_G, -G)
            u_next += delta_u
        else:
            raise RuntimeError(f"Backward Euler Newton-Raphson failed to converge at t={t_next}")

        return State(values=u_next, time=t_next, metadata=state.metadata.copy())