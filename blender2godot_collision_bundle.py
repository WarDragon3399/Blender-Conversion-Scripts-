import bpy
import os
import mathutils

# === CONFIG ===
output_dir = "C:/Exports/GLB"  # Change to your desired folder

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def move_mesh_to_origin(obj):
    # Calculate bounding box center in local space
    local_coords = [mathutils.Vector(corner) for corner in obj.bound_box]
    center = sum(local_coords, mathutils.Vector()) / 8.0

    # Shift mesh data so its center is at origin
    for v in obj.data.vertices:
        v.co -= center

    # Reset object location to world origin
    obj.location = (0.0, 0.0, 0.0)

def create_collision(obj):
    coll = obj.copy()
    coll.data = obj.data.copy()
    bpy.context.collection.objects.link(coll)
    coll.name = f"{obj.name}_Collision"
    coll.display_type = 'WIRE'
    coll.hide_render = True
    coll.hide_viewport = True
    # Add convex hull modifier
    mod = coll.modifiers.new(name="CollisionHull", type='REMESH')
    mod.mode = 'BLOCKS'
    return coll

for obj in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Apply transforms first
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Move mesh geometry to origin
    move_mesh_to_origin(obj)

    # Create collision mesh
    coll = create_collision(obj)
    move_mesh_to_origin(coll)

    # Select both original + collision
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    coll.select_set(True)

    # Export as one GLB file containing both
    export_path = os.path.join(output_dir, f"{obj.name}.glb")
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        use_selection=True,
        export_format='GLB',
        export_apply=True
    )

    # Cleanup collision mesh after export
    bpy.data.objects.remove(coll, do_unlink=True)

print("Export complete!")
