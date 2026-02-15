import bpy
import os

# === CONFIG ===
output_dir = "C:/Exports/GLB"  # Change to your desired folder
lod_levels = 3  # Number of LOD levels to generate

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_lods(obj, levels=3):
    lods = []
    for i in range(1, levels+1):
        lod = obj.copy()
        lod.data = obj.data.copy()
        bpy.context.collection.objects.link(lod)
        decimate = lod.modifiers.new(name=f"Decimate_{i}", type='DECIMATE')
        decimate.ratio = 1.0 - (i * 0.25)
        lod.name = f"{obj.name}_LOD{i}"
        lods.append(lod)
    return lods

def create_collision(obj):
    coll = obj.copy()
    coll.data = obj.data.copy()
    bpy.context.collection.objects.link(coll)
    coll.name = f"{obj.name}_Collision"
    coll.display_type = 'WIRE'
    coll.hide_render = True
    coll.hide_viewport = True
    mod = coll.modifiers.new(name="CollisionHull", type='REMESH')
    mod.mode = 'BLOCKS'
    return coll

for obj in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    lods = create_lods(obj, lod_levels)
    coll = create_collision(obj)

    # Select everything in the bundle
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    for lod in lods:
        lod.select_set(True)
    coll.select_set(True)

    # Export as one GLB file containing all
    export_path = os.path.join(output_dir, f"{obj.name}.glb")
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        use_selection=True,
        export_format='GLB',
        export_apply=True
    )

    # Cleanup temporary LODs and collision
    bpy.data.objects.remove(coll, do_unlink=True)
    for lod in lods:
        bpy.data.objects.remove(lod, do_unlink=True)

print("Export complete!")
