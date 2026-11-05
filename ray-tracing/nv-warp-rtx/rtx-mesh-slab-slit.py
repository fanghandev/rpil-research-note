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
# 2. Warp Kernel for Volumetric Attenuation
# ==========================================
@wp.func
def compute_inside_length(
    mesh_id: wp.uint64, ro: wp.vec3, rd: wp.vec3, max_dist: float, max_bounces: int
) -> float:
    """
    Traces a ray through an arbitrarily complex, watertight mesh
    and returns the total accumulated distance traveled strictly INSIDE the volume.
    """
    total_l = float(0.0)
    current_ro = ro
    eps = 0.001

    for i in range(max_bounces):
        t, u, v, sign = float(0.0), float(0.0), float(0.0), float(0.0)
        n = wp.vec3()
        f = int(0)

        # Query the next intersection
        hit = wp.mesh_query_ray(mesh_id, current_ro, rd, max_dist, t, u, v, sign, n, f)  # type: ignore

        if not hit:
            break

        if sign < 0.0:
            # We hit a BACK-FACE (Ray is EXITING the solid volume)
            if i == 0:
                # The ray natively originated inside the volume
                total_l += t
            else:
                # We artificially stepped inside by 'eps' previously.
                # Add it back to get the true thickness of this segment.
                total_l += t + eps

            # Step slightly OUTSIDE the back face to look for the next wall
            current_ro += rd * (t + eps)
        else:
            # We hit a FRONT-FACE (Ray is ENTERING the solid volume)
            # Step slightly INSIDE the front face. Do not accumulate length yet.
            current_ro += rd * (t + eps)

    return total_l


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

    # Get the raw geometric traveling distance
    L = compute_inside_length(mesh_id, origins[tid], dirs[tid], max_dist, max_bounces)  # type: ignore

    # Apply attenuation formula: I = I_0 * e^(-mu * L)
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

    # Get the raw geometric traveling distance
    L = compute_inside_length(mesh_id, origins[tid], dirs[tid], max_dist, max_bounces)  # type: ignore

    # Apply absorption probability formula: 1 - e^(-mu * L)
    out_absorbed[tid] = 1.0 - wp.exp(-mu_abs * L)  # type: ignore


# ==========================================
# 1. Exact Solid Angle (Oosterom-Strackee)
# ==========================================
@wp.func
def exact_triangle_solid_angle(
    ro: wp.vec3, v1: wp.vec3, v2: wp.vec3, v3: wp.vec3
) -> float:
    """
    Computes the exact solid angle of a 3D triangle using the Oosterom and Strackee formula.
    """
    r1 = v1 - ro
    r2 = v2 - ro
    r3 = v3 - ro

    l1 = wp.length(r1)
    l2 = wp.length(r2)
    l3 = wp.length(r3)

    # Numerator: Scalar triple product |r1 . (r2 x r3)|
    num = wp.abs(wp.dot(r1, wp.cross(r2, r3)))

    # Denominator: l1*l2*l3 + (r1.r2)*l3 + (r2.r3)*l1 + (r3.r1)*l2
    den = l1 * l2 * l3 + wp.dot(r1, r2) * l3 + wp.dot(r2, r3) * l1 + wp.dot(r3, r1) * l2

    return 2.0 * wp.atan2(num, den)  # type: ignore


@wp.func
def exact_rect_solid_angle(
    ro: wp.vec3, v1: wp.vec3, v2: wp.vec3, v3: wp.vec3, v4: wp.vec3
) -> float:
    """
    Splits a generalized 3D rectangle into two triangles and sums their exact solid angles.
    To get the solid angle of a full 3D box, you would loop this over its 6 faces.
    """
    # Split rect into Triangle 1 (v1, v2, v3) and Triangle 2 (v1, v3, v4)
    omega1 = exact_triangle_solid_angle(ro, v1, v2, v3)
    omega2 = exact_triangle_solid_angle(ro, v1, v3, v4)
    return omega1 + omega2


# ==========================================
# 2. Fast Approximation
# ==========================================
@wp.func
def approx_rect_solid_angle(
    ro: wp.vec3, center: wp.vec3, normal: wp.vec3, area: float
) -> float:
    """
    Approximates the solid angle using Area * cos(theta) / r^2.
    """
    r_vec = center - ro
    r_len = wp.length(r_vec)

    if r_len == 0.0:
        return 0.0

    r_dir = r_vec / r_len

    # Dot product of the face normal and the reversed ray direction
    cos_theta = wp.dot(normal, -r_dir)  # type: ignore

    # If the face is pointing away from the ray origin, it contributes 0 to the solid angle
    if cos_theta <= 0.0:
        return 0.0

    return (area * cos_theta) / (r_len * r_len)


# ==========================================
# 3. Evaluation Kernel
# ==========================================
@wp.kernel
def compare_solid_angles_kernel(
    origins: wp.array[wp.vec3],
    centers: wp.array[wp.vec3],
    normals: wp.array[wp.vec3],
    v1s: wp.array[wp.vec3],
    v2s: wp.array[wp.vec3],
    v3s: wp.array[wp.vec3],
    v4s: wp.array[wp.vec3],
    areas: wp.array[float],
    out_exact: wp.array[float],
    out_approx: wp.array[float],
):
    tid = wp.tid()

    # Calculate Exact
    out_exact[tid] = exact_rect_solid_angle(  # type: ignore
        origins[tid],  # type: ignore
        v1s[tid],  # type: ignore
        v2s[tid],  # type: ignore
        v3s[tid],  # type: ignore
        v4s[tid],  # type: ignore
    )

    # Calculate Approximation
    out_approx[tid] = approx_rect_solid_angle(  # type: ignore
        origins[tid],  # type: ignore
        centers[tid],  # type: ignore
        normals[tid],  # type: ignore
        areas[tid],  # type: ignore
    )


def plot_simulation_overlay(
    ax: Axes,
    mesh_points: np.ndarray,
    mesh_indices: np.ndarray,
    attenuation_map: np.ndarray,
    extent_source: list,
    targets_x: np.ndarray,
    target_y: float,
    sources_raw: np.ndarray = None,  # type: ignore
    targets_raw: np.ndarray = None,  # type: ignore
):
    """
    Plots the 2D attenuation heatmap and overlays the geometric X-Y projection
    of the 3D mesh, the projection detector line, and sample rays on a single plot.

    Parameters:
    -----------
    mesh_points : np.ndarray
        Nx3 array of vertex coordinates (X, Y, Z) from the mesh.
    mesh_indices : np.ndarray
        Mx3 array of triangle indices mapping vertices to faces.
    attenuation_map : np.ndarray
        2D numpy array containing the computed transmittance values.
    extent_source : list
        The spatial boundaries [xmin, xmax, ymin, ymax] of the source grid plane.
    targets_x : np.ndarray
        1D array containing the X-coordinates of the projection line detectors.
    target_y : float
        The Y position of the target projection detector line.
    sources_raw : np.ndarray, optional
        Full list of source coordinates (Nx3) to draw sample rays.
    targets_raw : np.ndarray, optional
        Full list of target coordinates (Mx3) to draw sample rays.
    """

    from matplotlib.collections import PolyCollection

    ax.set_title("Unified Simulation Overlay (Geometry + Attenuation Map)")

    # 1. Plot the Attenuation Heatmap as the base background layer
    # This automatically registers pixels to world coordinates using extent_source
    im = ax.imshow(
        attenuation_map,
        origin="lower",
        extent=extent_source,  # type: ignore
        cmap="inferno",  # type: ignore
    )

    # 2. Project 3D mesh vertices to 2D (drop Z) and create a wireframe overlay
    vertices_2d = mesh_points[:, :2]
    triangles_2d = vertices_2d[mesh_indices.reshape(-1, 3)]

    # We use facecolors='none' so the mesh doesn't block the underlying heatmap data
    mesh_collection = PolyCollection(
        triangles_2d,  # type: ignore
        facecolors="cyan",
        edgecolors="none",
        linewidths=1.0,
        alpha=1.0,
        label="Projected Mesh Slabs",
    )
    ax.add_collection(mesh_collection)

    # 3. Plot the Target Detector Projection Line (at Y=150)
    ax.plot(
        targets_x,
        np.full_like(targets_x, target_y),
        color="red",
        linewidth=3,
        marker="o",
        markersize=4,
        label="Projection Line (Y=150)",
    )

    # 5. Visual formatting and bounds adjustments
    x_min, x_max, y_min, y_max = extent_source

    # Expand limits to encompass the projection line up at Y=150
    ax.set_xlim(x_min - 20, x_max + 20)
    ax.set_ylim(y_min - 20, target_y + 20)

    ax.set_xlabel("X Position (mm)")
    ax.set_ylabel("Y Position (mm)")
    ax.set_aspect("equal")  # Maintain 1:1 pixel aspect ratio distortion-free

    # Add Colorbar for the transmittance map
    fig.colorbar(im, ax=ax, shrink=0.75, label=r"Transmittance ($e^{-\mu l_i}$)")
    # Clean up legend handles
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper left")

    plt.tight_layout()
    plt.show()


# ==========================================
# 3. Main Execution
# ==========================================
if __name__ == "__main__":
    # --- A. Build the Geometry (Coordinates in mm) ---
    slab_thickness = 2.0
    slab_width = 100.0
    slab_height = 100.0
    slit_width = 2.0
    slab_y = 100.0

    # Box 1 (+X side): center is slit half-width + slab half-width
    c1_x = (slit_width / 2.0) + (slab_width / 2.0)  # 1.0 + 50.0 = 51.0
    v1, i1 = create_box_mesh(
        center=[c1_x, slab_y, 0.0], size=[slab_width, slab_thickness, slab_height]
    )

    # Box 2 (-X side): mirrored center
    c2_x = -c1_x  # -51.0
    v2, i2 = create_box_mesh(
        center=[c2_x, slab_y, 0.0], size=[slab_width, slab_thickness, slab_height]
    )

    # Combine into a single scene mesh
    verts = np.vstack([v1, v2])
    indices = np.hstack([i1, i2 + len(v1)])

    mesh = wp.Mesh(
        points=wp.array(verts, dtype=wp.vec3, device="cuda:0"),
        indices=wp.array(indices, dtype=int, device="cuda:0"),
    )

    # --- B. Generate Ray Data ---
    # 1. Source grid: 100x100 points in Z=0 plane (-100mm to 100mm)
    fov_nx = 500
    fov_ny = 500
    fov_dim_x_mm = 200.0
    fov_dim_y_mm = 200.0
    fov_x_min_mm = -fov_dim_x_mm / 2.0
    fov_x_max_mm = fov_dim_x_mm / 2.0
    fov_y_min_mm = -fov_dim_y_mm / 2.0
    fov_y_max_mm = fov_dim_y_mm / 2.0
    proj_nx = 20
    proj_center_y = 150.0  # 50mm behind the slabs

    sx = np.linspace(fov_x_min_mm, fov_x_max_mm, fov_nx)
    sy = np.linspace(fov_y_min_mm, fov_y_max_mm, fov_ny)
    SX, SY = np.meshgrid(sx, sy)
    sources = np.column_stack(
        [SX.ravel(), SY.ravel(), np.zeros_like(SX.ravel())]
    )  # (10000, 3)

    # 2. Target projection line: 20 points, Y=150 (50mm behind slabs), Z=0, X from -1 to 1 mm

    tx = np.linspace(-1, 1, proj_nx)
    targets = np.column_stack(
        [tx, np.full_like(tx, 150.0), np.zeros_like(tx)]
    )  # (20, 3)

    # 3. Permutations: 10,000 sources * 20 targets = 200,000 rays total
    origins_np = np.repeat(sources, len(targets), axis=0).astype(np.float32)
    targets_np = np.tile(targets, (len(sources), 1)).astype(np.float32)

    dirs_np = targets_np - origins_np
    dirs_np /= np.linalg.norm(dirs_np, axis=1, keepdims=True)

    # --- C. Execute Attenuation Simulation ---
    num_rays = len(origins_np)
    origins_gpu = wp.array(origins_np, dtype=wp.vec3, device="cuda:0")
    dirs_gpu = wp.array(dirs_np, dtype=wp.vec3, device="cuda:0")
    att_gpu = wp.empty(num_rays, dtype=float, device="cuda:0")

    print(f"Tracing {num_rays:,} rays...")
    max_bounces = 10
    lengths_gpu = wp.empty(num_rays, dtype=float, device="cuda:0")

    wp.launch(
        kernel=compute_attenuation_kernel,
        dim=num_rays,
        inputs=[mesh.id, origins_gpu, dirs_gpu, 2.31, 1000, max_bounces, att_gpu],
        device="cuda:0",
    )
    wp.synchronize()
    # --- D. Reshape Data ---
    att_raw = att_gpu.numpy().reshape(fov_nx, fov_ny, proj_nx)
    att_map = att_raw.mean(axis=2)

    print(verts.shape, indices.shape, att_map.shape)
    fig, ax = plt.subplots(figsize=(10, 9))
    plot_simulation_overlay(
        ax=ax,
        mesh_points=verts,
        mesh_indices=indices,
        attenuation_map=att_map,
        extent_source=[fov_x_min_mm, fov_x_max_mm, fov_y_min_mm, fov_y_max_mm],
        targets_x=tx,
        target_y=proj_center_y,
        sources_raw=sources,
        targets_raw=targets,
    )
