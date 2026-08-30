# bloon/tests/test_manifold_diffusion.py
import numpy as np
import pytest
from topology.sphere import create_ico_sphere
from physics.manifold_diffusion import ManifoldDiffusion

@pytest.fixture
def sphere_diffusion():
    mesh = create_ico_sphere(subdivisions=3)
    return ManifoldDiffusion(mesh, alpha=0.1)

def test_mass_matrix_properties(sphere_diffusion):
    M = sphere_diffusion.mass_diag

    # 1. Positivity: M_ii > 0
    assert np.all(M > 0), "All lumped mass entries must be strictly positive"

    # 2. Geometric consistency: Total area of unit sphere is 4*pi
    total_area = np.sum(M)
    assert np.isclose(total_area, 4 * np.pi, rtol=1e-2), \
        f"Total mass (area) should approximate 4*pi (12.566). Got {total_area}"

def test_operator_properties(sphere_diffusion):
    K = sphere_diffusion.K
    K_dense = K.toarray()

    # 1. K = K^T (Symmetry)
    assert np.allclose(K_dense, K_dense.T), "Operator K must be symmetric"

    # 2. Spectral Analysis
    eigvals = np.linalg.eigvalsh(K_dense)

    # PSD test: All eigenvalues must be >= 0 (up to numerical precision)
    min_eig = eigvals.min()
    assert min_eig >= -1e-10, f"Operator K must be PSD. Lowest eigenvalue is {min_eig}"

    # Null space test: The first eigenvalue must be strictly 0 (constant null space)
    assert abs(eigvals[0]) < 1e-10, f"Expected 0-eigenvalue for null space, got {eigvals[0]}"

def test_constant_state_preservation(sphere_diffusion):
    # If u is constant, diffusion should not alter it
    C = 7.5
    u_const = np.full(sphere_diffusion.K.shape[0], C)

    u_next = sphere_diffusion.step(u_const, dt=1.0)

    assert np.allclose(u_next, C, atol=1e-12), \
        "Backward Euler step must perfectly preserve a constant state"

def test_conservation_and_decay(sphere_diffusion):
    # Initialize a localized bump
    V = sphere_diffusion.mesh.vertices
    pole = np.array([0, 0, 1])
    u = np.exp(-10.0 * np.sum((V - pole)**2, axis=1))

    dt = 0.5

    for _ in range(5):
        mass_n = sphere_diffusion.get_total_mass(u)
        energy_n = sphere_diffusion.get_dirichlet_energy(u)

        u_next = sphere_diffusion.step(u, dt)

        mass_next = sphere_diffusion.get_total_mass(u_next)
        energy_next = sphere_diffusion.get_dirichlet_energy(u_next)

        # 1. Strict mass conservation (1^T M u = constant)
        assert np.isclose(mass_n, mass_next, atol=1e-12), \
            "Total mass must be strictly conserved across time steps"

        # 2. Dirichlet energy is non-increasing
        assert energy_next <= energy_n + 1e-12, \
            "Discrete Dirichlet energy must be non-increasing under Backward Euler scheme"

        u = u_next
