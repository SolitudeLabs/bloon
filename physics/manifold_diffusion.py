import numpy as np
import scipy.sparse as sp

# bloon/physics/manifold_diffusion.py
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

class ManifoldDiffusion:
    """
    Solves heat/diffusion equation on a 2D manifold embedded in 3D:
        u_t = alpha * Laplace-Beltrami(u)

    Using Discrete Exterior Calculus / FEM cotangent formulation.
    """
    def __init__(self, mesh, alpha=1.0):
        self.mesh = mesh
        self.alpha = alpha

        # Build operators strictly following FEM conventions:
        # K >= 0 (Stiffness), M >= 0 (Lumped Mass)
        self.K, self.mass_diag = self._build_operators()
        self.L, self.M_inv = self._assemble_cotangent_laplacian()
        self._A_cache = {}

    def _build_operators(self):
        V = self.mesh.vertices
        F = self.mesh.faces
        n_v = len(V)

        I, J, V_vals = [], [], []
        mass = np.zeros(n_v)

        for tri in F:
            i, j, k = tri
            vi, vj, vk = V[i], V[j], V[k]

            # Edge vectors
            e_ij = vj - vi
            e_jk = vk - vj
            e_ki = vi - vk

            # Triangle area via cross product
            n = np.cross(e_ij, -e_ki)
            area = 0.5 * np.linalg.norm(n)

            # 1. Lumped Mass Matrix (Barycentric)
            mass[i] += area / 3.0
            mass[j] += area / 3.0
            mass[k] += area / 3.0

            # 2. Stiffness Matrix K (Cotangent weights)
            # cot = cos/sin = dot / norm(cross)
            cot_k = np.dot(-e_ki, e_jk) / np.linalg.norm(np.cross(-e_ki, e_jk))
            cot_i = np.dot(-e_ij, e_ki) / np.linalg.norm(np.cross(-e_ij, e_ki))
            cot_j = np.dot(-e_jk, e_ij) / np.linalg.norm(np.cross(-e_jk, e_ij))

            w_ij = 0.5 * cot_k
            w_jk = 0.5 * cot_i
            w_ki = 0.5 * cot_j

            # Off-diagonals are strictly negative for K (Stiffness)
            I.extend([i, j, j, k, k, i])
            J.extend([j, i, k, j, i, k])
            V_vals.extend([-w_ij, -w_ij, -w_jk, -w_jk, -w_ki, -w_ki])

        # Assemble sparse K
        K = sp.coo_matrix((V_vals, (I, J)), shape=(n_v, n_v)).tolil()

        # Enforce K * 1 = 0 by setting diagonal to -sum(off_diagonals)
        K.setdiag(0)
        row_sums = np.array(K.sum(axis=1)).flatten()
        K.setdiag(-row_sums)

        return K.tocsr(), mass

    def _assemble_cotangent_laplacian(self):
        """
        Assembles the cotangent stiffness matrix (L) and lumped mass matrix (M)
        for the triangulated surface mesh.
        """
        V = self.mesh.vertices
        F = self.mesh.faces
        n = len(V)

        W = sp.lil_matrix((n, n))
        M_diag = np.zeros(n)

        for face in F:
            #i, j, k = face
            i, j, k = map(int, face)
            vi, vj, vk = V[i], V[j], V[k]

            # Area of triangle using cross product
            cross_val = np.cross(vj - vi, vk - vi)
            area = 0.5 * np.linalg.norm(cross_val)
            if area < 1e-12:
                continue

            # Lumped mass contribution
            M_diag[i] += area / 3.0
            M_diag[j] += area / 3.0
            M_diag[k] += area / 3.0

            # Cotangent weights for edges (cot(alpha) + cot(beta))/2 approximation
            # Edge vectors
            edges = [(i, j, vk), (j, k, vi), (k, i, vj)]
            #for a, b, c in [(i, j, vk), (j, k, vi), (k, i, vj)]:
            for a, b, c in [(i, j, k), (j, k, i), (k, i, j)]:
                va, vb, vc = V[a], V[b], V[c]
                cot_val = np.dot(va - vc, vb - vc) / (np.linalg.norm(np.cross(va - vc, vb - vc)) + 1e-12)
                w = 0.5 * cot_val
                W[a, b] += w
                W[b, a] += w

        # Build stiffness matrix L_ij = W_ij, L_ii = -sum(W_ij)
        W_csr = W.tocsr()
        row_sums = np.array(W_csr.sum(axis=1)).flatten()
        L = W_csr - sp.csr_matrix((row_sums, (range(n), range(n))), shape=(n, n))

        # Invert lumped mass for explicit/implicit formulations
        M_inv = 1.0 / (M_diag + 1e-12)

        return L, M_inv

    def step(self, u: np.ndarray, dt: float) -> np.ndarray:
        """
        Backward Euler step: (M + alpha * dt * K) u^{n+1} = M u^n
        """
        if dt not in self._A_cache:
            M_mat = sp.diags(self.mass_diag)
            A = M_mat + self.alpha * dt * self.K
            # Pre-factorize for speed if dt is constant
            self._A_cache[dt] = spla.factorized(A.tocsc())

        b = self.mass_diag * u
        u_next = self._A_cache[dt](b)
        return u_next

    # --- Observables ---
    def get_total_mass(self, u: np.ndarray) -> float:
        """Integral of u over the manifold: sum(M_ii * u_i)"""
        return np.sum(self.mass_diag * u)

    def get_dirichlet_energy(self, u: np.ndarray) -> float:
        """E(u) = 1/2 u^T K u (Must be >= 0 since K is positive semi-definite)"""
        return 0.5 * np.dot(u, self.K.dot(u))

    def compute_energy(self, u: np.ndarray) -> float:
        """
        Computes the Dirichlet energy: E_D(u) = -1/2 u^T L u.
        (Negative sign is required because L is negative-semidefinite)
        """
        return -0.5 * np.dot(u, self.L.dot(u))
