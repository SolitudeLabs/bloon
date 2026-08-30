# bloon/topology/mesh2d.py
import numpy as np

class Mesh2D:
    """
    Minimal 2D discrete topology and geometry representation.
    Explicitly separates Geometry (node coordinates) from Topology (connectivity).
    """
    def __init__(self, vertices: np.ndarray, faces: np.ndarray):
        self.vertices = np.asarray(vertices, dtype=float)  # Geometry: (V, 2)
        self.faces = np.asarray(faces, dtype=int)          # Topology: (F, 3)
        self.edges = self._extract_edges()                 # Topology: (E, 2)
        self.num_nodes = self.num_vertices

    def _extract_edges(self) -> np.ndarray:
        edge_set = set()
        for face in self.faces:
            n = len(face)
            for i in range(n):
                p1, p2 = face[i], face[(i + 1) % n]
                edge = tuple(sorted((p1, p2)))
                edge_set.add(edge)
        return np.array(list(edge_set), dtype=int)

    @property
    def num_vertices(self) -> int:
        return len(self.vertices)

    @property
    def num_edges(self) -> int:
        return len(self.edges)

    @property
    def num_faces(self) -> int:
        return len(self.faces)

    def euler_characteristic(self) -> int:
        """Calculates Euler characteristic: chi = V - E + F"""
        return self.num_vertices - self.num_edges + self.num_faces

    def get_adjacency_list(self) -> dict:
        """Computes vertex adjacency from edge connectivity."""
        adj = {i: set() for i in range(self.num_vertices)}
        for e in self.edges:
            adj[e[0]].add(e[1])
            adj[e[1]].add(e[0])
        return {k: list(v) for k, v in adj.items()}
