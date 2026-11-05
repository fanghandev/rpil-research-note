import time

import numpy as np
import warp as wp


# ==========================================
# The Warp Kernel
# ==========================================
@wp.kernel
def raycast_batch_kernel(
    mesh_id: wp.uint64,
    origins: wp.array[wp.vec3],
    dirs: wp.array[wp.vec3],
    max_dist: float,
    out_t: wp.array[float],
    out_face: wp.array[int],
):
    # wp.tid() gives us the unique thread ID, which maps 1:1 to the ray index
    tid = wp.tid()

    ro = origins[tid]
    rd = dirs[tid]

    # Initialize pass-by-reference variables
    t = float(0.0)
    u = float(0.0)
    v = float(0.0)
    sign = float(0.0)
    n = wp.vec3()
    f = int(0)

    # Perform intersection
    hit = wp.mesh_query_ray(mesh_id, ro, rd, max_dist, t, u, v, sign, n, f)  # type: ignore

    if hit:
        out_t[tid] = t  # type: ignore
        out_face[tid] = f  # type: ignore
    else:
        out_t[tid] = -1.0  # type: ignore
        out_face[tid] = -1  # type: ignore


# ==========================================
# The Worker Class
# ==========================================
class WarpGPUWorker:
    def __init__(self, device_id: str, max_batch_size: int):
        """
        Initializes the GPU environment and pre-allocates VRAM buffers.
        :param device_id: The target GPU (e.g., 'cuda:0' or 'cuda:1')
        :param max_batch_size: The maximum number of rays per chunk to safely lock in VRAM.
        """
        wp.init()
        self.device = wp.get_device(device_id)
        self.max_batch_size = max_batch_size
        self.mesh = None
        self.max_dist = 1000.0

        # Pre-allocate VRAM exclusively on the targeted device
        with wp.ScopedDevice(self.device):
            self.ro_gpu = wp.empty(shape=max_batch_size, dtype=wp.vec3)
            self.rd_gpu = wp.empty(shape=max_batch_size, dtype=wp.vec3)
            self.hits_t_gpu = wp.empty(shape=max_batch_size, dtype=float)
            self.hits_face_gpu = wp.empty(shape=max_batch_size, dtype=int)

    def load_mesh(self, vertices: np.ndarray, indices: np.ndarray):
        """
        Loads the geometry into the GPU and builds the BVH.
        """
        with wp.ScopedDevice(self.device):
            v_arr = wp.array(vertices, dtype=wp.vec3)
            i_arr = wp.array(indices, dtype=int)
            self.mesh = wp.Mesh(points=v_arr, indices=i_arr)
            print(f"[{self.device}] Mesh loaded and BVH built successfully.")

    def process_chunk(self, origins_np: np.ndarray, dirs_np: np.ndarray):
        """
        Takes CPU numpy arrays, moves them to the GPU, computes intersections,
        and returns the results to CPU RAM. The output arrays map 1:1 to the inputs.
        """
        if self.mesh is None:
            raise RuntimeError("Mesh not loaded. Call load_mesh() before processing.")

        num_rays = origins_np.shape[0]
        if num_rays > self.max_batch_size:
            raise ValueError(
                f"Chunk size ({num_rays}) exceeds max_batch_size ({self.max_batch_size})"
            )

        with wp.ScopedDevice(self.device):
            # 1. Wrap the CPU numpy arrays as zero-copy Warp arrays on the CPU
            ro_cpu = wp.array(origins_np, dtype=wp.vec3, device="cpu")
            rd_cpu = wp.array(dirs_np, dtype=wp.vec3, device="cpu")

            # 2. Copy data from the CPU Warp array to our pre-allocated GPU VRAM
            wp.copy(self.ro_gpu, ro_cpu, dest_offset=0, src_offset=0, count=num_rays)
            wp.copy(self.rd_gpu, rd_cpu, dest_offset=0, src_offset=0, count=num_rays)

            # 3. Launch the kernel
            wp.launch(
                kernel=raycast_batch_kernel,
                dim=num_rays,
                inputs=[
                    self.mesh.id,
                    self.ro_gpu,
                    self.rd_gpu,
                    self.max_dist,
                    self.hits_t_gpu,
                    self.hits_face_gpu,
                ],
            )

            # 4. Synchronize to ensure computation is finished before copying back
            wp.synchronize()

            # 5. Pull the results back to the CPU as standard NumPy arrays
            hits_t_np = self.hits_t_gpu.numpy()[:num_rays].copy()
            hits_face_np = self.hits_face_gpu.numpy()[:num_rays].copy()

        return hits_t_np, hits_face_np


# ==========================================
# Independent Execution Test
# ==========================================
if __name__ == "__main__":
    print("Initializing test run...")

    # 1. Create a simple plane mesh (2 triangles) for testing
    verts = np.array(
        [
            [-10.0, -10.0, 0.0],
            [10.0, -10.0, 0.0],
            [10.0, 10.0, 0.0],
            [-10.0, 10.0, 0.0],
        ],
        dtype=np.float32,
    )
    idxs = np.array([0, 1, 2, 0, 2, 3], dtype=np.int32)

    # 2. Generate 5 million test rays pointing straight down (-Z)
    TEST_RAYS = 5_000_000
    origins = np.zeros((TEST_RAYS, 3), dtype=np.float32)
    origins[:, 0] = np.random.uniform(-5.0, 5.0, TEST_RAYS)  # X positions
    origins[:, 1] = np.random.uniform(-5.0, 5.0, TEST_RAYS)  # Y positions
    origins[:, 2] = 10.0  # Z positions (above the mesh)

    dirs = np.zeros((TEST_RAYS, 3), dtype=np.float32)
    dirs[:, 2] = -1.0  # Pointing straight down

    # 3. Initialize the worker on CUDA 0
    worker = WarpGPUWorker(device_id="cuda:0", max_batch_size=10_000_000)
    worker.load_mesh(verts, idxs)

    # 4. Execute the chunk
    print(f"Processing {TEST_RAYS:,} rays...")
    start_time = time.time()

    t_results, face_results = worker.process_chunk(origins, dirs)

    end_time = time.time()

    # 5. Verify results
    hits = np.sum(face_results != -1)
    print(f"Compute finished in {end_time - start_time:.4f} seconds.")
    print(f"Total Hits: {hits:,}")
    print(f"First 5 ray distances (t): {t_results[:5]}")
    print(f"First 5 hit face IDs: {face_results[:5]}")
