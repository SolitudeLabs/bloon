# bloon/examples/run_topology.py
import numpy as np
from topology.mesh2d import Mesh2D

def main():
    print("=== BLOON Demo 1: Discrete Topology ===")

    # Define a simple flat grid / triangulated square (2 triangles, 4 vertices)
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0]
    ])
    faces = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ])

    mesh = Mesh2D(vertices, faces)

    print(f"Geometry -> Number of Vertices (V): {mesh.num_vertices}")
    print(f"Topology -> Number of Edges (E):    {mesh.num_edges}")
    print(f"Topology -> Number of Faces (F):    {mesh.num_faces}")

    chi = mesh.euler_characteristic()
    print(f"Euler Characteristic (chi = V - E + F): {chi}")
    print("Explanation: For a disk-like flat triangulated surface with boundary, chi = 1 (or 2 for closed spheres).")

    adj = mesh.get_adjacency_list()
    print(f"Vertex 0 Adjacency: {adj[0]}")
    print("=== Demo 1 Completed Successfully ===")

if __name__ == "__main__":
    main()
