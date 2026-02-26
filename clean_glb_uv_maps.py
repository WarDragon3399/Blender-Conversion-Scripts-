import bpy
import os

# --- SET YOUR FOLDER PATH HERE ---
folder_path = r'C:\Path\To\Your\GLB\Files' #use your own path of folder

def clean_glb_uv_maps(directory):
    if not os.path.exists(directory):
        print("Folder path does not exist.")
        return

    # Filter for GLB files
    files = [f for f in os.listdir(directory) if f.lower().endswith(".glb")]
    print(f"Found {len(files)} files. Starting batch process...")

    for filename in files:
        file_path = os.path.join(directory, filename)
        
        # 1. CLEAN SCENE (Manual deletion so the script keeps running)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Clear orphaned data (meshes, materials, etc.) to keep memory low
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
        for img in bpy.data.images:
            bpy.data.images.remove(img)
        for mat in bpy.data.materials:
            bpy.data.materials.remove(mat)

        # 2. IMPORT
        try:
            bpy.ops.import_scene.gltf(filepath=file_path)
        except Exception as e:
            print(f"Failed to import {filename}: {e}")
            continue

        modified = False
        
        # 3. PROCESS UVs
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                uv_layers = obj.data.uv_layers
                # Check if multiple UVs exist
                if len(uv_layers) > 1:
                    target_uv = uv_layers.get("UVMap")
                    if target_uv:
                        uv_layers.remove(target_uv)
                        modified = True
                        print(f"-> Removed 'UVMap' from {obj.name} in {filename}")

        # 4. EXPORT AND OVERWRITE
        if modified:
            try:
                # Ensure something is active for the exporter
                if bpy.context.scene.objects:
                    bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]
                
                bpy.ops.export_scene.gltf(
                    filepath=file_path,
                    export_format='GLB',
                    use_selection=False
                )
                print(f"DONE: {filename} updated.")
            except Exception as e:
                print(f"ERROR: Could not export {filename}: {e}")
        else:
            print(f"SKIP: {filename} had no extra UVs.")

    print("--- Batch Process Complete ---")

# Run the script
clean_glb_uv_maps(folder_path)
