import bpy
import os

# --- SETUP ---
# Note: I used the "r" trick we discussed so the path works
source_folder = r"C:\Users\DELL\Pictures\Modular Temple"
# -------------

def reset_scene():
    # Delete everything in the scene so we don't mix models
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Get all .obj files
files = [f for f in os.listdir(source_folder) if f.endswith('.obj')]

if not files:
    print("No .obj files found in that folder!")

for f in files:
    reset_scene()
    
    fullpath = os.path.join(source_folder, f)
    print(f"Converting: {f}")
    
    # --- NEW COMMAND FOR BLENDER 4.0+ ---
    bpy.ops.wm.obj_import(filepath=fullpath)
    
    # Construct output name
    out_name = os.path.splitext(f)[0] + ".glb"
    out_path = os.path.join(source_folder, out_name)
    
    # Export GLB
    # We use 'export_keep_originals' to ensure we export everything visible
    bpy.ops.export_scene.gltf(filepath=out_path)

print("--- Conversion Complete! ---")