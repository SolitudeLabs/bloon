# bloon/examples/visualize_manifold.py
import os
import numpy as np
import matplotlib.pyplot as plt

from topology.sphere import create_ico_sphere
from physics.manifold_diffusion import ManifoldDiffusion

def plot_sphere(ax, mesh, u, title):
    V = mesh.vertices
    F = mesh.faces

    # Average the state 'u' from the three nodes in each element.
    u_faces = np.mean(u[F], axis=1)

    # Plot a 3D surface with a transparent wireframe.
    surf = ax.plot_trisurf(
        V[:, 0], V[:, 1], V[:, 2],
        triangles=F,
        edgecolor='white',
        linewidth=0.1,
        alpha=0.9,
        shade=False
    )

    # Utilize native matplotlib collection scalar mapping
    surf.set_array(u_faces)
    surf.set_cmap('inferno')
    surf.set_clim(vmin=0.0, vmax=1.0)

    # Subtitle using stable 2D text placement
    ax.text2D(
        0.5, 0.93, title,
        transform=ax.transAxes,
        ha='center',
        va='top',
        color='white',
        fontsize=12
    )
    ax.set_axis_off()
    ax.view_init(elev=20, azim=45)

    return surf

def main():
    print("Generating geometry and discrete operators...")
    mesh = create_ico_sphere(subdivisions=3)
    diffusion = ManifoldDiffusion(mesh, alpha=0.02)

    # Initial State: High concentration/heat at one pole
    pole = np.array([0, 0, 1])
    u_init = np.exp(-3.0 * np.sum((mesh.vertices - pole)**2, axis=1))

    # Evolve Time
    dt = 0.5
    steps = 15
    u_final = u_init.copy()
    for _ in range(steps):
        u_final = diffusion.step(u_final, dt)

    # --- Rendering Setup ---
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12, 6))
    fig.canvas.manager.set_window_title('BLOON Manifold Dynamics')

    # Plot Initial State
    ax1 = fig.add_subplot(121, projection='3d')
    plot_sphere(
        ax1, mesh, u_init,
        r'Initial State | $t=0$'
    )

    # Plot Final State
    ax2 = fig.add_subplot(122, projection='3d')
    surf2 = plot_sphere(
        ax2, mesh, u_final,
        rf'Diffused State | $t={steps * dt}$'
    )

    # Main Title
    fig.suptitle(
        r'Laplace-Beltrami Diffusion on $\mathcal{M}=S^2$',
        color='white',
        fontsize=16,
        y=0.98
    )

    # Add a unified colorbar
    cbar = fig.colorbar(
        surf2,
        ax=[ax1, ax2],
        shrink=0.5,
        aspect=20,
        pad=0.05
    )

    cbar.set_label('Concentration / Temperature', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

    fig.subplots_adjust(
        left=0.02,
        right=0.90,
        bottom=0.03,
        top=0.86,
        wspace=0.02
    )

    # Save output image
    out_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'manifold_diffusion.png')
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor())
    print(f"Visualization saved to: {out_path}")

    print("Rendering... (Close window to exit)")
    plt.show()

if __name__ == "__main__":
    main()
