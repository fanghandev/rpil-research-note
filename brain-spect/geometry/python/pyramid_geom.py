import numpy as np
from manifold3d import Manifold, Mesh


def create_pyramid_manifold(width, length, height, z_offset=0.0):
    """Generates a Manifold object from raw pyramid vertices and faces."""
    # Define vertices (X, Y, Z)
    vertices = np.array(
        [
            [-width / 2, -length / 2, z_offset],  # 0: Bottom-left
            [width / 2, -length / 2, z_offset],  # 1: Bottom-right
            [width / 2, length / 2, z_offset],  # 2: Top-right
            [-width / 2, length / 2, z_offset],  # 3: Top-left
            [0, 0, height + z_offset],  # 4: Apex
        ],
        dtype=np.float32,
    )

    # Define triangles (counter-clockwise winding order for outward normals)
    faces = np.array(
        [
            [0, 2, 1],
            [0, 3, 2],  # Base
            [0, 1, 4],  # Front
            [1, 2, 4],  # Right
            [2, 3, 4],  # Back
            [3, 0, 4],  # Left
        ],
        dtype=np.int32,
    )

    # Construct the native Manifold object
    mesh = Mesh(vert_properties=vertices, tri_verts=faces)
    return Manifold(mesh)


def save_as_obj(manifold_obj, filename):
    """Extracts raw geometry from a Manifold object and writes a 3D .obj file."""
    mesh = manifold_obj.to_mesh()

    # Extract X, Y, Z coordinates
    verts = mesh.vert_properties[:, :3]
    faces = mesh.tri_verts

    with open(filename, "w") as f:
        for v in verts:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            # OBJ files use 1-based indexing for vertices
            f.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")


# --- 1. Define Outer Pyramid ---
outer_w = 100.0
outer_l = 80.0
outer_h = 100.0
thickness = 2.0

# --- 2. Calculate Inner Pyramid Parameters ---
angle_w = np.arctan2(outer_h, outer_w / 2.0)
angle_l = np.arctan2(outer_h, outer_l / 2.0)

offset_w = thickness / np.sin(angle_w)
offset_l = thickness / np.sin(angle_l)

inner_w = outer_w - (2 * offset_w)
inner_l = outer_l - (2 * offset_l)

drop_h = thickness / np.cos(angle_w)
inner_h = outer_h - drop_h

# --- 3. Build the Manifold Objects ---
outer = create_pyramid_manifold(outer_w, outer_l, outer_h)
# Push the inner pyramid down by 1mm to cleanly cut the floor open
inner = create_pyramid_manifold(inner_w, inner_l, inner_h, z_offset=-1.0)

# --- 4. Execute Native Boolean Difference ---
# Manifold3D allows you to use standard Python operators
hollow_pyramid = outer - inner

import k3d
import numpy as np

# Assuming 'hollow_pyramid' is your Manifold object from the previous step

# 1. Convert the Manifold object to a raw mesh
mesh_data = hollow_pyramid.to_mesh()

# 2. Extract vertices and faces, enforcing K3D's required data types
vertices = mesh_data.vert_properties[:, :3].astype(np.float32)
indices = mesh_data.tri_verts.astype(np.uint32)

# 3. Initialize the K3D plot
plot = k3d.plot(name="Hollow Pyramid")

# 4. Create the K3D mesh object (you can customize colors and shading here)
mesh_vis = k3d.mesh(
    vertices,
    indices,
    color=0x00A0FF,  # Hex color (e.g., light blue)
    wireframe=False,  # Set to True to see the topology
    side="double",  # Renders both inside and outside faces
)

# 5. Add the mesh to the plot and display it
plot += mesh_vis
plot.display()
