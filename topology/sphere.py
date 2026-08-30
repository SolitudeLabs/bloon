# bloon/topology/sphere.py
import numpy as np
from topology.mesh2d import Mesh2D

def create_ico_sphere(subdivisions: int = 2) -> Mesh2D:
    t = (1.0 + np.sqrt(5.0)) / 2.0
    verts = [[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
             [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
             [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]]
    verts = np.array(verts, dtype=float)
    verts /= np.linalg.norm(verts, axis=1, keepdims=True)

    faces = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
             [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
             [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
             [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]

    # Subdivision logic untuk visualisasi yang smooth
    for _ in range(subdivisions):
        new_faces = []
        cache = {}

        def get_midpoint(p1, p2):
            key = tuple(sorted((p1, p2)))
            if key in cache: return cache[key]
            mid = (verts[p1] + verts[p2]) / 2.0
            mid /= np.linalg.norm(mid)
            cache[key] = len(verts)
            verts.append(mid)
            return cache[key]

        verts = list(verts)
        for tri in faces:
            a, b, c = tri
            ab = get_midpoint(a, b)
            bc = get_midpoint(b, c)
            ca = get_midpoint(c, a)
            new_faces.extend([[a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]])
        faces = new_faces
        verts = np.array(verts)

    return Mesh2D(verts, faces)
