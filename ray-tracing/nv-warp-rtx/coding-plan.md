# Project Plan: Warp RayTracer

## Phase 1: Environment and Architecture Setup

**Objective:** Establish the project skeleton and data formats before writing the heavy logic.

* **Action for You:** Create the following directory structure for the project:
```text
warp_raycaster/
│
├── main.py              # The Orchestrator
├── module_1_source.py   # Data Generator / Reader
├── module_2_worker.py   # NVIDIA Warp GPU Process
├── module_3_writer.py   # Disk I/O (HDF5)
├── requirements.txt
└── mesh_data/           # Folder for your 10k triangle mesh (.obj or .ply)

```

* **Action for AI Agent:** Instruct the agent to generate the `requirements.txt`.
* *Agent Prompt:* "Generate a `requirements.txt` for a Python project using NVIDIA Warp, NumPy, and `h5py` (or `zarr`) for high-speed massive array I/O."

## Phase 2: Module Implementation

Hand these discrete tasks to your AI agent one by one. Do not ask it to write the whole system at once.

### Task 1: The Data Sourcing Module (`module_1_source.py`)

* **Goal:** Create a generator that yields chunks of ray origins and directions without exceeding system RAM.
* **Agent Instructions:** "Write a Python class `RaySource` that acts as an iterator. It must yield a tuple of two NumPy float32 arrays `(origins, directions)`. Ensure the batch size is configurable (default 20,000,000) and that it gracefully handles the final partial batch. Leave a placeholder function for the actual data loading/generation logic."

### Task 2: The GPU Worker Module (`module_2_worker.py`)

* **Goal:** The isolated Warp environment that runs on a specific GPU.
* **Agent Instructions:** "Write a Python function `run_warp_worker(gpu_id: int, input_queue, output_queue, mesh_path: str)`. This function must initialize Warp targeting the specific `gpu_id` (e.g., `cuda:0` or `cuda:1`). It needs to load a 3D mesh into `wp.Mesh`, pre-allocate `wp.array` buffers for 20 million rays, and continuously pull data from `input_queue`. Use the `@wp.kernel` raycast logic to compute intersections, and push the resulting `hits_t` and `hits_face` NumPy arrays to the `output_queue`."

### Task 3: The Disk I/O Module (`module_3_writer.py`)

* **Goal:** Write results to disk fast enough to prevent a GPU bottleneck.
* **Agent Instructions:** "Write a Python class `ResultWriter` that listens to a `multiprocessing.Queue`. It should take NumPy arrays of hit distances and face IDs and append them to an HDF5 (or Zarr) dataset on disk. Ensure it uses chunked storage and compression optimized for sequential appending. It must cleanly close the file when it receives a 'STOP' signal."

### Task 4: The Orchestrator (`main.py`)

* **Goal:** Tie it all together using Python's `multiprocessing`.
* **Agent Instructions:** "Write the main execution script using `multiprocessing`. It must set up two worker processes (one for `cuda:0`, one for `cuda:1`), one writer process, and the necessary data queues. Use the `RaySource` generator to feed chunks into the input queue in a round-robin fashion between the two GPU workers. Include a progress bar using `tqdm` tracking total rays processed."

## Phase 3: The Sandbox Test

Before unleashing 50 trillion rays, we must prove the pipeline holds together without memory leaks.

* **Test Parameter:** 100 million rays.
* **Batch Size:** 20 million.
* **Success Criteria:** Both GPUs hit 100% utilization in bursts, system RAM stays flat (no creeping memory leaks), and the final HDF5 file exactly matches 100 million records.
* **Action:** You and the agent will debug the queues and inter-process communication (IPC) here. IPC serialization can sometimes slow down passing large NumPy arrays between processes, which might require tweaking to use shared memory (`multiprocessing.shared_memory`) if the queues become a bottleneck.

## Phase 4: Production Run

Once Phase 3 passes, you scale up the total ray count in `main.py` and let it run.

---

To complete the exact specifications for **Task 1** so you can hand it to the agent, I need to clarify the missing piece: Are the 50 trillion rays going to be procedurally generated on the fly via mathematical rules, or do you have a massive pre-existing dataset of rays sitting on a hard drive that this module needs to read?