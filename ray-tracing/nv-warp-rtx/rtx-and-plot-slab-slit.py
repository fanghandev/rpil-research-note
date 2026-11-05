from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import warp as wp
from matplotlib.axes import Axes

wp.init()


# ==========================================
# 1. Geometry Helper
# ==========================================
def create_box_mesh(center: list, size: list):
    """Generates vertices and indices for a 3D box."""
    c = np.array(center)
    s = np.array(size) / 2.0

    verts = np.array(
        [
            c + [-s[0], -s[1], -s[2]],
            c + [s[0], -s[1], -s[2]],
            c + [s[0], s[1], -s[2]],
            c + [-s[0], s[1], -s[2]],
            c + [-s[0], -s[1], s[2]],
            c + [s[0], -s[1], s[2]],
            c + [s[0], s[1], s[2]],
            c + [-s[0], s[1], s[2]],
        ],
        dtype=np.float32,
    )

    indices = np.array(
        [
            0,
            2,
            1,
            0,
            3,
            2,  # Bottom
            4,
            5,
            6,
            4,
            6,
            7,  # Top
            0,
            1,
            5,
            0,
            5,
            4,  # Front
            1,
            2,
            6,
            1,
            6,
            5,  # Right
            2,
            3,
            7,
            2,
            7,
            6,  # Back
            3,
            0,
            4,
            3,
            4,
            7,  # Left
        ],
        dtype=np.int32,
    )

    return verts, indices


# ==========================================
# 2. Warp Kernels for Physics Maps
# ==========================================
@wp.func
def compute_inside_length(
    mesh_id: wp.uint64, ro: wp.vec3, rd: wp.vec3, max_dist: float, max_bounces: int
) -> float:
    total_l = float(0.0)
    current_ro = ro
    eps = 0.001

    for i in range(max_bounces):
        t, u, v, sign = float(0.0), float(0.0), float(0.0), float(0.0)
        n = wp.vec3()
        f = int(0)

        hit = wp.mesh_query_ray(mesh_id, current_ro, rd, max_dist, t, u, v, sign, n, f)  # type: ignore

        if not hit:
            break

        if sign < 0.0:
            if i == 0:
                total_l += t
            else:
                total_l += t + eps
            current_ro += rd * (t + eps)
        else:
            current_ro += rd * (t + eps)

    return total_l


@wp.func
def approx_rect_solid_angle(
    ro: wp.vec3, center: wp.vec3, normal: wp.vec3, area: float
) -> float:
    r_vec = center - ro
    r_len = wp.length(r_vec)
    if r_len == 0.0:
        return 0.0
    r_dir = r_vec / r_len
    cos_theta = wp.dot(normal, -r_dir)  # type: ignore
    if cos_theta <= 0.0:
        return 0.0
    return (area * cos_theta) / (r_len * r_len)


@wp.kernel
def compute_attenuation_kernel(
    mesh_id: wp.uint64,
    origins: wp.array[wp.vec3],
    dirs: wp.array[wp.vec3],
    mu: float,
    max_dist: float,
    max_bounces: int,
    out_att: wp.array[float],
):
    tid = wp.tid()
    L = compute_inside_length(mesh_id, origins[tid], dirs[tid], max_dist, max_bounces)  # type: ignore
    out_att[tid] = wp.exp(-mu * L)  # type: ignore


@wp.kernel
def compute_absorption_kernel(
    mesh_id: wp.uint64,
    origins: wp.array[wp.vec3],
    dirs: wp.array[wp.vec3],
    mu_abs: float,
    max_dist: float,
    max_bounces: int,
    out_absorbed: wp.array[float],
):
    tid = wp.tid()
    L = compute_inside_length(mesh_id, origins[tid], dirs[tid], max_dist, max_bounces)  # type: ignore
    out_absorbed[tid] = 1.0 - wp.exp(-mu_abs * L)  # type: ignore


@wp.kernel
def compute_solid_angle_kernel(
    origins: wp.array[wp.vec3],
    target_center: wp.vec3,
    target_normal: wp.vec3,
    target_area: float,
    out_sa: wp.array[float],
):
    tid = wp.tid()
    out_sa[tid] = approx_rect_solid_angle(  # type: ignore
        origins[tid],  # type: ignore
        target_center,
        target_normal,
        target_area,
    )


# ==========================================
# 3. Plotting Function
# ==========================================
def plot_simulation_overlay(
    fig,
    ax: Axes,
    title: str,
    mesh_points: np.ndarray,
    mesh_indices: np.ndarray,
    data_map: np.ndarray,
    extent_source: list,
    all_crystal_rects: list,
    active_crystal_idx: int,
    cbar_label: str,
):
    from matplotlib.collections import PolyCollection

    ax.set_title(title)

    im = ax.imshow(
        data_map,
        origin="lower",
        extent=extent_source,  # type: ignore
        cmap="inferno",
    )

    # Collimator Mesh Overlay
    vertices_2d = mesh_points[:, :2]
    triangles_2d = vertices_2d[mesh_indices.reshape(-1, 3)]

    mesh_collection = PolyCollection(
        triangles_2d,  # type: ignore
        facecolors="cyan",
        edgecolors="none",
        linewidths=1.0,
        alpha=0.5,
        label="Collimator Slabs",
    )
    ax.add_collection(mesh_collection)

    # Draw all crystals in the array
    for idx, rect_params in enumerate(all_crystal_rects):
        cx, cy, cw, cd = rect_params

        # Style conditionally based on whether it is the active simulation target
        if idx == active_crystal_idx:
            fc = "red"
            alpha = 1.0
            label = "Target Crystal (Active)"
        else:
            fc = "grey"
            alpha = 0.4
            label = "Other Crystals"

        rect = patches.Rectangle(
            (cx - cw / 2, cy - cd / 2),
            cw,
            cd,
            linewidth=0.5,
            edgecolor="black",
            facecolor=fc,
            alpha=alpha,
            label=label,
        )
        ax.add_patch(rect)

        # # Plot Target Face Center ONLY for the active crystal
        # if idx == active_crystal_idx:
        #     ax.plot(
        #         cx,
        #         cy - cd / 2,
        #         marker="*",
        #         color="white",
        #         markersize=8,
        #         label="Face Center",
        #     )

    # Visual bounds formatting
    x_min, x_max, y_min, y_max = extent_source
    ax.set_xlim(x_min - 20, x_max + 20)

    # Dynamically adjust Y limit to fit the top of the crystal array
    top_y = max([r[1] + r[3] / 2 for r in all_crystal_rects])
    ax.set_ylim(y_min - 20, top_y + 10)

    ax.set_xlabel("X Position (mm)")
    ax.set_ylabel("Y Position (mm)")
    ax.set_aspect("equal")

    fig.colorbar(im, ax=ax, shrink=0.75, label=cbar_label)

    # Matplotlib will automatically deduplicate duplicate labels using this dictionary zip trick
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper left", fontsize="small")


# ==========================================
# 4. Main Execution
# ==========================================
if __name__ == "__main__":
    # --- A. Constants & Materials ---
    mu_collimator = 2.31
    mu_crystal = 0.5
    max_bounces = 10
    max_ray_dist = 500.0

    # --- B. Build Collimator Geometry ---
    slab_thickness = 2.0
    slab_width = 100.0
    slab_height = 100.0
    slit_width = 2.0
    slab_y = 100.0

    c1_x = (slit_width / 2.0) + (slab_width / 2.0)
    v1, i1 = create_box_mesh(
        center=[c1_x, slab_y, 0.0], size=[slab_width, slab_thickness, slab_height]
    )

    c2_x = -c1_x
    v2, i2 = create_box_mesh(
        center=[c2_x, slab_y, 0.0], size=[slab_width, slab_thickness, slab_height]
    )

    verts = np.vstack([v1, v2])
    indices = np.hstack([i1, i2 + len(v1)])

    collimator_mesh = wp.Mesh(
        points=wp.array(verts, dtype=wp.vec3, device="cuda:0"),
        indices=wp.array(indices, dtype=int, device="cuda:0"),
    )

    # --- C. Setup Source FOV (500x500) ---
    fov_nx, fov_ny = 500, 500
    fov_dim_x_mm, fov_dim_y_mm = 200.0, 200.0
    fov_x_min_mm, fov_x_max_mm = -fov_dim_x_mm / 2.0, fov_dim_x_mm / 2.0
    fov_y_min_mm, fov_y_max_mm = -fov_dim_y_mm / 2.0, fov_dim_y_mm / 2.0

    sx = np.linspace(fov_x_min_mm, fov_x_max_mm, fov_nx)
    sy = np.linspace(fov_y_min_mm, fov_y_max_mm, fov_ny)
    SX, SY = np.meshgrid(sx, sy)
    sources = np.column_stack(
        [SX.ravel(), SY.ravel(), np.zeros_like(SX.ravel())]
    ).astype(np.float32)
    num_sources = len(sources)
    origins_gpu = wp.array(sources, dtype=wp.vec3, device="cuda:0")

    extent_bounds = [fov_x_min_mm, fov_x_max_mm, fov_y_min_mm, fov_y_max_mm]

    num_crystals = 10
    cry_w, cry_h, cry_d = 2.0, 2.0, 10.0  # Width(X), Height(Z), Depth(Y)
    cry_area = cry_w * cry_h
    cry_normal = wp.vec3(0.0, -1.0, 0.0)  # Face looks down towards FOV

    # Output arrays
    att_gpu = wp.empty(num_sources, dtype=float, device="cuda:0")
    sa_gpu = wp.empty(num_sources, dtype=float, device="cuda:0")
    abs_gpu = wp.empty(num_sources, dtype=float, device="cuda:0")

    # Pre-compute all crystal bounding boxes for the plotting context array
    all_crystal_rects = []
    for i in range(num_crystals):
        cx = -9.0 + i * 2.0
        cy = 150.0 + (cry_d / 2.0)
        all_crystal_rects.append([cx, cy, cry_w, cry_d])

    print(
        f"Starting simulation for {num_crystals} crystals at {fov_nx}x{fov_ny} resolution..."
    )

    # --- E. Iterate over Crystals ---
    for i in range(num_crystals):
        print(f"\nProcessing Crystal {i + 1}/{num_crystals}...")

        # 1. Grab specific crystal geometry from the pre-computed array
        cx, cy, cw, cd = all_crystal_rects[i]
        cz = 0.0

        face_center_np = np.array([cx, 150.0, cz], dtype=np.float32)

        # 2. Compute Ray Directions
        dirs_np = face_center_np - sources
        dirs_np /= np.linalg.norm(dirs_np, axis=1, keepdims=True)
        dirs_gpu = wp.array(dirs_np, dtype=wp.vec3, device="cuda:0")

        # 3. Create a Warp Mesh just for this Crystal
        cv, ci = create_box_mesh(center=[cx, cy, cz], size=[cry_w, cry_d, cry_h])
        crystal_mesh = wp.Mesh(
            points=wp.array(cv, dtype=wp.vec3, device="cuda:0"),
            indices=wp.array(ci, dtype=int, device="cuda:0"),
        )

        # 4. Launch Physics Kernels
        wp.launch(
            compute_attenuation_kernel,
            dim=num_sources,
            inputs=[
                collimator_mesh.id,
                origins_gpu,
                dirs_gpu,
                mu_collimator,
                max_ray_dist,
                max_bounces,
                att_gpu,
            ],
            device="cuda:0",
        )
        wp.launch(
            compute_solid_angle_kernel,
            dim=num_sources,
            inputs=[
                origins_gpu,
                wp.vec3(*face_center_np),
                cry_normal,
                cry_area,
                sa_gpu,
            ],
            device="cuda:0",
        )
        wp.launch(
            compute_absorption_kernel,
            dim=num_sources,
            inputs=[
                crystal_mesh.id,
                origins_gpu,
                dirs_gpu,
                mu_crystal,
                max_ray_dist,
                max_bounces,
                abs_gpu,
            ],
            device="cuda:0",
        )
        wp.synchronize()

        # 5. Retrieve & Reshape Data
        map_att = att_gpu.numpy().reshape(fov_ny, fov_nx)
        map_sa = sa_gpu.numpy().reshape(fov_ny, fov_nx)
        map_abs = abs_gpu.numpy().reshape(fov_ny, fov_nx)
        map_prod = map_att * map_sa * map_abs

        # 6. Plotting the 4 maps
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        fig.suptitle(
            f"Crystal {i + 1} Simulation Maps (Position: X={cx:.1f}mm)",
            fontsize=16,
            y=0.95,
        )

        # Pass the full array and the active index to the plotter
        plot_simulation_overlay(
            fig,
            axes[0, 0],
            "1. Collimator Transmittance",
            verts,
            indices,
            map_att,
            extent_bounds,
            all_crystal_rects,
            i,
            r"Attn ($e^{-\mu l}$)",
        )
        plot_simulation_overlay(
            fig,
            axes[0, 1],
            "2. Solid Angle Multiplier",
            verts,
            indices,
            map_sa,
            extent_bounds,
            all_crystal_rects,
            i,
            r"$\Omega$ (sr)",
        )
        plot_simulation_overlay(
            fig,
            axes[1, 0],
            "3. Crystal Absorption Prob.",
            verts,
            indices,
            map_abs,
            extent_bounds,
            all_crystal_rects,
            i,
            r"Abs. ($1 - e^{-\mu_{abs} l}$)",
        )
        plot_simulation_overlay(
            fig,
            axes[1, 1],
            "4. Total Signal Product",
            verts,
            indices,
            map_prod,
            extent_bounds,
            all_crystal_rects,
            i,
            r"Signal ($A \cdot \Omega \cdot C$)",
        )

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # type: ignore

        output_filename = f"crystal_{i + 1}_simulation_maps.png"
        output_dir = "rtx_simulation_outputs"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        plt.savefig(Path(output_dir) / output_filename, dpi=300)
        # Note: plt.show() halts execution until the figure is closed.
        # Close the window to process and view the next crystal.
