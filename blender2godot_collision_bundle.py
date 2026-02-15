import bpy
import os

# === CONFIG ===
output_dir = "C:/Exports/GLB"  # Change to your desired folder

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_collision(obj):
    coll = obj.copy()
    coll.data = obj.data.copy()
    bpy.context.collection.objects.link(coll)
    coll.name = f"{obj.name}_Collision"
    coll.display_type = 'WIRE'
    coll.hide_render = True   # invisible in render
    coll.hide_viewport = False  # still visible in viewport so it exports
    # Parent collision to the original mesh
    coll.parent = obj
    # Add convex hull modifier for collision shape
    mod = coll.modifiers.new(name="CollisionHull", type='REMESH')
    mod.mode = 'BLOCKS'
    return coll

for obj in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Apply transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Create collision mesh as child
    coll = create_collision(obj)

    # Select parent + child
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    coll.select_set(True)

    # Export as GLB
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
