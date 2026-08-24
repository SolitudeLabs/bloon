# bloon/examples/run_manifold_diffusion.py
import numpy as np
from topology.sphere import create_ico_sphere
from physics.manifold_diffusion import ManifoldDiffusion

def main():
    print("=== BLOON Demo 2: Manifold Diffusion on S^2 ===")
    
    # 1. State / Topology Lifecycle
    mesh = create_ico_sphere(subdivisions=0)
    print(f"Manifold Domain initialized. Vertices: {mesh.num_vertices}, Faces: {mesh.num_faces}")
    
    # 2. Operator Setup (Laplace-Beltrami)
    diffusion = ManifoldDiffusion(mesh, alpha=0.05)
    
    # 3. Initial State (e.g., concentrated heat spot on one side of the sphere)
    u = np.exp(-5.0 * np.sum((mesh.vertices - np.array([0, 0, 1]))**2, axis=1))
    initial_energy = diffusion.compute_energy(u)
    print(f"Initial Dirichlet Energy E(u): {initial_energy:.6f}")
    
    # 4. Temporal Evolution
    dt = 0.1
    steps = 5
    print(f"Evolving system over {steps} time steps (dt={dt})...")
    
    energies = [initial_energy]
    for step_idx in range(1, steps + 1):
        u = diffusion.step(u, dt)
        energy = diffusion.compute_energy(u)
        energies.append(energy)
        print(f"Step {step_idx} | Energy E(u): {energy:.6f}")
        
    # 5. Observable & Verification Check
    energy_decreasing = all(energies[i] >= energies[i+1] for i in range(len(energies)-1))
    print(f"Verification Check - Energy monotonically decreases under diffusion: {energy_decreasing}")
    print("=== Demo 2 Completed Successfully ===")

if __name__ == "__main__":
    main()