import bpy
import mathutils
from mathutils import Vector

# ─── Clean up existing armatures ───
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        bpy.data.objects.remove(obj, do_unlink=True)

# ─── Create Armature ───
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
armature_obj = bpy.context.active_object
armature_obj.name = 'SeatArmature'
armature = armature_obj.data
armature.name = 'SeatRig'

# Remove default bone
for b in armature.edit_bones:
    armature.edit_bones.remove(b)

# ─── Define Bones ───
# Bone hierarchy:
#   Root (base frame, fixed reference)
#   └── Slide (fore/aft movement along Y)
#       └── Cushion (height adjustment along Z)
#           └── Backrest (recline rotation around X at hinge point)
#               └── Headrest (up/down along bone local Z)

# Root bone - at base center
root = armature.edit_bones.new('Root')
root.head = Vector((0, 0, 0))
root.tail = Vector((0, 0, 0.3))

# Slide bone - fore/aft (Y axis movement)
slide = armature.edit_bones.new('Slide')
slide.head = Vector((0, 0, 0.1))
slide.tail = Vector((0, 0, 0.4))
slide.parent = root

# Cushion bone - at seat cushion center, for height
cushion = armature.edit_bones.new('Cushion')
cushion.head = Vector((0, 0, 0.35))
cushion.tail = Vector((0, 0, 0.65))
cushion.parent = slide

# Backrest bone - hinge point at bottom of backrest
# Back seat bbox: Y=-2.15 to -0.92, Z=0.01 to 2.12
# Hinge is approximately at the junction of cushion and backrest
backrest = armature.edit_bones.new('Backrest')
backrest.head = Vector((0, -0.9, 0.4))
backrest.tail = Vector((0, -1.8, 2.0))
backrest.parent = cushion

# Headrest bone - at top of backrest going up
headrest = armature.edit_bones.new('Headrest')
headrest.head = Vector((0, -2.0, 2.4))
headrest.tail = Vector((0, -2.1, 3.2))
headrest.parent = backrest

# Exit edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# ─── Mesh to Bone Assignment ───
# Map each mesh to its controlling bone
bone_assignments = {
    '01 Base': 'Root',
    '02 Base rim': 'Root',
    '03 Base controls': 'Root',
    '04 Bottom seat': 'Cushion',
    '05 Bottom sides': 'Cushion',
    '06 Back seat': 'Backrest',
    '07 Seat back sides': 'Backrest',
    '08 Upper neck': 'Backrest',
    '09 Header': 'Headrest',
}

for mesh_name, bone_name in bone_assignments.items():
    mesh_obj = bpy.data.objects.get(mesh_name)
    if not mesh_obj:
        print(f'WARNING: mesh "{mesh_name}" not found')
        continue

    # Clear existing vertex groups
    mesh_obj.vertex_groups.clear()

    # Clear existing parent
    mesh_obj.parent = armature_obj
    mesh_obj.parent_type = 'ARMATURE'

    # Add vertex group for the bone
    vg = mesh_obj.vertex_groups.new(name=bone_name)
    # Assign ALL vertices to this bone with weight 1.0
    vg.add(list(range(len(mesh_obj.data.vertices))), 1.0, 'REPLACE')

    # Add Armature modifier if not exists
    has_armature_mod = False
    for mod in mesh_obj.modifiers:
        if mod.type == 'ARMATURE':
            mod.object = armature_obj
            has_armature_mod = True
            break
    if not has_armature_mod:
        mod = mesh_obj.modifiers.new(name='Armature', type='ARMATURE')
        mod.object = armature_obj

    print(f'Assigned "{mesh_name}" -> bone "{bone_name}" ({len(mesh_obj.data.vertices)} verts)')

# ─── Create Actions (Animations) ───
# We'll create named actions that can be triggered from Three.js

armature_obj.rotation_mode = 'XYZ'

# Pose mode to set up bone constraints/limits
bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='POSE')

# Set rotation mode for bones
for pbone in armature_obj.pose.bones:
    pbone.rotation_mode = 'XYZ'

# ─── Action 1: Recline (Backrest rotation) ───
action_recline = bpy.data.actions.new('Recline')
armature_obj.animation_data_create()
armature_obj.animation_data.action = action_recline

backrest_bone = armature_obj.pose.bones['Backrest']
# Frame 0: upright (0 degrees extra recline)
backrest_bone.rotation_euler = (0, 0, 0)
backrest_bone.keyframe_insert(data_path='rotation_euler', frame=0)
# Frame 30: reclined (~30 degrees back, rotation around X in local space)
# In this model, recline = rotating the backrest further back
backrest_bone.rotation_euler = (0.52, 0, 0)  # ~30 degrees
backrest_bone.keyframe_insert(data_path='rotation_euler', frame=30)
# Frame 60: back to upright
backrest_bone.rotation_euler = (0, 0, 0)
backrest_bone.keyframe_insert(data_path='rotation_euler', frame=60)

# ─── Action 2: Headrest up/down ───
action_headrest = bpy.data.actions.new('HeadrestAdjust')
armature_obj.animation_data.action = action_headrest

headrest_bone = armature_obj.pose.bones['Headrest']
headrest_bone.location = (0, 0, 0)
headrest_bone.keyframe_insert(data_path='location', frame=0)
headrest_bone.location = (0, 0, 0.4)  # move up along bone's local axis
headrest_bone.keyframe_insert(data_path='location', frame=30)
headrest_bone.location = (0, 0, 0)
headrest_bone.keyframe_insert(data_path='location', frame=60)

# ─── Action 3: Slide fore/aft ───
action_slide = bpy.data.actions.new('SlideForAft')
armature_obj.animation_data.action = action_slide

slide_bone = armature_obj.pose.bones['Slide']
slide_bone.location = (0, 0, 0)
slide_bone.keyframe_insert(data_path='location', frame=0)
slide_bone.location = (0, 0.5, 0)  # forward
slide_bone.keyframe_insert(data_path='location', frame=30)
slide_bone.location = (0, -0.5, 0)  # backward
slide_bone.keyframe_insert(data_path='location', frame=60)
slide_bone.location = (0, 0, 0)  # center
slide_bone.keyframe_insert(data_path='location', frame=90)

# ─── Action 4: Height adjustment ───
action_height = bpy.data.actions.new('HeightAdjust')
armature_obj.animation_data.action = action_height

cushion_bone = armature_obj.pose.bones['Cushion']
cushion_bone.location = (0, 0, 0)
cushion_bone.keyframe_insert(data_path='location', frame=0)
cushion_bone.location = (0, 0, 0.2)  # up
cushion_bone.keyframe_insert(data_path='location', frame=30)
cushion_bone.location = (0, 0, 0)
cushion_bone.keyframe_insert(data_path='location', frame=60)

# Reset to default action
armature_obj.animation_data.action = action_recline

bpy.ops.object.mode_set(mode='OBJECT')

# ─── Export as GLB ───
# Select all relevant objects
bpy.ops.object.select_all(action='DESELECT')
armature_obj.select_set(True)
for mesh_name in bone_assignments:
    obj = bpy.data.objects.get(mesh_name)
    if obj:
        obj.select_set(True)

bpy.context.view_layer.objects.active = armature_obj

bpy.ops.export_scene.gltf(
    filepath='/home/kim/Downloads/car_seat/car_seat_rigged.glb',
    export_format='GLB',
    export_animations=True,
    export_skins=True,
    use_selection=True,
    export_apply=False,
)

print('\n=== EXPORT COMPLETE ===')
print(f'Bones: {len(armature.bones)}')
print(f'Actions: {len(bpy.data.actions)}')
for a in bpy.data.actions:
    print(f'  Action: {a.name} ({a.frame_range[0]:.0f}-{a.frame_range[1]:.0f})')
