import bpy
import os

# ====================================================================
# --- 1. CONFIGURATION ---
# ====================================================================

# SET THIS: The path to the folder containing ALL your Mixamo FBX files.
# Use double backslashes (\\) on Windows, or forward slashes (/) on Mac/Linux.
FBX_DIRECTORY = "C:\\Users\\DELL\\Downloads\\New folder\\New folder (2)" 

# ====================================================================
# --- 2. MAIN EXECUTION ---
# ====================================================================

print("--- STARTING BATCH MIXAMO CONVERSION (ALL WITH SKIN) ---")

# --- Helper function to find the latest imported Armature ---
def get_imported_armature(imported_objects):
    for obj in imported_objects:
        if obj.type == 'ARMATURE':
            return obj
    return None

# Sort files to ensure the intended 'main' character (e.g., Idle) is processed first
fbx_files = sorted([f for f in os.listdir(FBX_DIRECTORY) if f.endswith(".fbx")])

main_armature = None
armature_objects_to_delete = []

# --- Step A: Import all FBX files ---
for i, file_name in enumerate(fbx_files):
    file_path = os.path.join(FBX_DIRECTORY, file_name)
    animation_name = os.path.splitext(file_name)[0]

    print(f"\nImporting file {i+1}/{len(fbx_files)}: {file_name}")

    # Capture objects before import
    objects_before_import = set(bpy.context.scene.objects)
    
    # FBX Import Operator
    bpy.ops.import_scene.fbx(
        filepath=file_path,
        ignore_leaf_bones=True,
        force_connect_children=True,
        automatic_bone_orientation=True
    )
    
    # Capture objects after import
    imported_objects = set(bpy.context.scene.objects) - objects_before_import
    current_armature = get_imported_armature(imported_objects)
    
    if current_armature is None:
        print(f"WARNING: No armature found in {file_name}. Skipping.")
        continue

    # --- Step B: Designate Main Armature and Transfer Actions ---
    if main_armature is None:
        # First one imported becomes the main character/rig
        main_armature = current_armature
        print(f"MAIN ARMATURE ESTABLISHED: {main_armature.name}")
        
        # Ensure the first imported action is saved
        if main_armature.animation_data and main_armature.animation_data.action:
            main_armature.animation_data.action.name = animation_name
            print(f"Set initial action: {animation_name}")
            
    else:
        # Subsequent files are duplicates of the rig. We extract the animation and queue the rest for deletion.
        
        if current_armature.animation_data and current_armature.animation_data.action:
            action_data = current_armature.animation_data.action
            action_data.name = animation_name
            
            # Link the action to the main armature's data. This ensures it's saved.
            # We don't need to assign it to the action slot, just make sure it's in bpy.data.actions
            print(f"Action '{animation_name}' extracted.")
            
            # Queue the duplicate armature and all its children (mesh) for deletion
            armature_objects_to_delete.extend(list(current_armature.children) + [current_armature])

# --- Step C: Cleanup Duplicates ---
print("\nCleaning up duplicate armatures and meshes...")
for obj in armature_objects_to_delete:
    # Check if the object still exists before trying to delete
    if obj.name in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
        
print("Cleanup complete.")

# --- Step D: Export the final merged character as GLB ---
if not main_armature:
    print("FATAL ERROR: Main armature not found. Cannot export.")
    exit()

bpy.ops.object.select_all(action='DESELECT')
main_armature.select_set(True)
# Select the mesh object(s) parented to the main armature
for obj in main_armature.children:
    if obj.type == 'MESH':
        obj.select_set(True)

output_glb_path = os.path.join(FBX_DIRECTORY, "Final_Mixamo_Character_Merged.glb")
print(f"\nExporting final GLB to: {output_glb_path}")

bpy.ops.export_scene.gltf(
    filepath=output_glb_path,
    export_format='GLB',
    use_selection=True,
    export_animations=True,
    export_yup=True
)

print("\n--- BATCH CONVERSION COMPLETE! ---")