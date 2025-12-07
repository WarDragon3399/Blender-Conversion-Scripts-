#Export all mesh of blend file as GLB in diffrent files location of export same as blend file   
import bpy
import os

# Ensure we are in Object Mode
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Get the folder where the blend file is saved
# If the file hasn't been saved yet, save it first!
basedir = bpy.path.abspath("//")

if not basedir:
    print("ERROR: Please save your .blend file before running this script so we know where to export.")
else:
    # Get all currently selected objects
    selection = bpy.context.selected_objects
    
    # Deselect everything initially so we can process one by one
    bpy.ops.object.select_all(action='DESELECT')

    for obj in selection:
        # Select the current object and make it active
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # 1. Set the Pivot (Origin) to the center of the mesh (Geometry)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        
        # 2. Store the original location
        original_location = obj.location.copy()
        
        # 3. Move object to world origin (0,0,0)
        # This ensures the pivot is actually at (0,0,0) inside the GLB file
        obj.location = (0, 0, 0)
        
        # 4. Construct the filename based on object name
        # "Clean_name" removes characters that might be illegal in filenames
        name = bpy.path.clean_name(obj.name)
        filepath = os.path.join(basedir, name + ".glb")
        
        # 5. Export as GLB
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            use_selection=True, 
            # These settings ensure transforms are applied correctly
            export_apply=True
        )
        
        # 6. Restore the object to its original location
        obj.location = original_location
        
        # Deselect this object to prepare for the next one
        obj.select_set(False)

    # Re-select original selection when finished
    for obj in selection:
        obj.select_set(True)


    print(f"Exported {len(selection)} objects to {basedir}")
