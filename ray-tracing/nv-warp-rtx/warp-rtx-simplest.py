import numpy as np
import warp as wp

# Initialize Warp
wp.init()

# ==========================================
# Step 1: Prepare data and create wp.Mesh
# ==========================================
vertices = np.array(
    [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32
)
indices = np.array([0, 1, 2], dtype=np.int32)

v_arr = wp.array(vertices, dtype=wp.vec3)
i_arr = wp.array(indices, dtype=int)

mesh = wp.Mesh(points=v_arr, indices=i_arr)

hits_t = wp.zeros(1, dtype=float)
hits_face = wp.zeros(1, dtype=int)


# ==========================================
# Step 2: Write the intersection Kernel
# ==========================================
@wp.kernel
def raycast_kernel(
    mesh_id: wp.uint64,
    ray_origin: wp.vec3,
    ray_dir: wp.vec3,
    max_dist: float,
    out_t: wp.array[float],
    out_face: wp.array[int],
):

    # In Warp, outputs are handled by passing local variables by reference.
    # We must explicitly initialize them before calling the query.
    t = float(0.0)
    u = float(0.0)
    v = float(0.0)
    sign = float(0.0)
    n = wp.vec3()
    f = int(0)

    # Perform ray intersection. Modifies t, u, v, sign, n, and f in place.
    hit = wp.mesh_query_ray(mesh_id, ray_origin, ray_dir, max_dist, t, u, v, sign, n, f)

    if hit:
        out_t[0] = t
        out_face[0] = f
    else:
        out_t[0] = -1.0
        out_face[0] = -1


# ==========================================
# Step 3: Set ray parameters and launch the Kernel
# ==========================================
ro = wp.vec3(0.25, 0.25, 1.0)
rd = wp.vec3(0.0, 0.0, -1.0)
max_dist = 100.0

wp.launch(
    kernel=raycast_kernel, dim=1, inputs=[mesh.id, ro, rd, max_dist, hits_t, hits_face]
)

wp.synchronize()
print(f"Ray hit distance (t): {hits_t.numpy()[0]}")
print(f"Hit face index (Face ID): {hits_face.numpy()[0]}")
