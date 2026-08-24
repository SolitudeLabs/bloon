# bloon/tests/test_topology.py
import pytest
from topology.sphere import create_ico_sphere

@pytest.mark.parametrize("subdivisions", [0, 1, 2, 3])
def test_sphere_topology(subdivisions):
    mesh = create_ico_sphere(subdivisions)
    V = len(mesh.vertices)
    F = len(mesh.faces)
    
    # Ekstraksi unik edges untuk verifikasi Euler characteristic
    edges = set()
    for face in mesh.faces:
        edges.add(tuple(sorted((face[0], face[1]))))
        edges.add(tuple(sorted((face[1], face[2]))))
        edges.add(tuple(sorted((face[2], face[0]))))
    E = len(edges)
    
    # Theoretical limits for subdivision of icosahedron
    expected_V = 10 * (4**subdivisions) + 2
    expected_F = 20 * (4**subdivisions)
    
    assert V == expected_V, f"Expected {expected_V} vertices, got {V}"
    assert F == expected_F, f"Expected {expected_F} faces, got {F}"
    assert (V - E + F) == 2, f"Euler characteristic (V - E + F) must strictly be 2, got {V - E + F}"