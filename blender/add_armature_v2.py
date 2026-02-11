"""
Enhanced 10-bone armature for KETI Smart Seat
==============================================
Hierarchy:
  Root (01 Base, 02 Base rim, 03 Base controls)
  └── Slide (fore/aft)
      └── Cushion (04 Bottom seat — height + tilt)
          ├── BolsterL  (05 Bottom sides left half — squeeze)
          ├── BolsterR  (05 Bottom sides right half — squeeze)
          └── Backrest  (06 Back seat upper + 08 Upper neck — recline)
              ├── Lumbar       (06 Back seat lower — weight-painted push)
              ├── BackBolsterL (07 Seat back sides left — squeeze)
              ├── BackBolsterR (07 Seat back sides right — squeeze)
              └── Headrest     (09 Header — height + tilt)

New vs v1: +BolsterL, +BolsterR, +Lumbar, +BackBolsterL, +BackBolsterR
"""

import bpy
from mathutils import Vector

# ─── Clean up ───
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        bpy.data.objects.remove(obj, do_unlink=True)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)

# ─── Create Armature ───
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm_obj = bpy.context.active_object
arm_obj.name = 'SeatArmature'
arm_obj.data.name = 'SeatRig'
arm = arm_obj.data

for b in arm.edit_bones:
    arm.edit_bones.remove(b)

# ─── 10 Bones ───
root = arm.edit_bones.new('Root')
root.head = Vector((0, 0, 0))
root.tail = Vector((0, 0, 0.3))

slide = arm.edit_bones.new('Slide')
slide.head = Vector((0, 0, 0.1))
slide.tail = Vector((0, 0, 0.4))
slide.parent = root

cushion = arm.edit_bones.new('Cushion')
cushion.head = Vector((0, 0, 0.35))
cushion.tail = Vector((0, 0, 0.65))
cushion.parent = slide

# Bottom bolsters (children of Cushion)
# 05 Bottom sides center: X ±0.886, Y=-0.073, Z=0.188
bolL = arm.edit_bones.new('BolsterL')
bolL.head = Vector((-0.75, -0.07, 0.10))
bolL.tail = Vector((-0.75, -0.07, 0.45))
bolL.parent = cushion

bolR = arm.edit_bones.new('BolsterR')
bolR.head = Vector((0.75, -0.07, 0.10))
bolR.tail = Vector((0.75, -0.07, 0.45))
bolR.parent = cushion

backrest = arm.edit_bones.new('Backrest')
backrest.head = Vector((0, -0.9, 0.4))
backrest.tail = Vector((0, -1.8, 2.0))
backrest.parent = cushion

# Lumbar (child of Backrest, lower back area)
# 06 Back seat: Z 0.058~2.132, lumbar zone Z < 0.8
lumbar = arm.edit_bones.new('Lumbar')
lumbar.head = Vector((0, -1.1, 0.3))
lumbar.tail = Vector((0, -1.3, 0.9))
lumbar.parent = backrest

# Back bolsters (children of Backrest)
# 07 Seat back sides center: X ±1.097, Y=-1.560, Z=0.892
bbL = arm.edit_bones.new('BackBolsterL')
bbL.head = Vector((-0.90, -1.56, 0.20))
bbL.tail = Vector((-0.90, -1.56, 1.50))
bbL.parent = backrest

bbR = arm.edit_bones.new('BackBolsterR')
bbR.head = Vector((0.90, -1.56, 0.20))
bbR.tail = Vector((0.90, -1.56, 1.50))
bbR.parent = backrest

headrest = arm.edit_bones.new('Headrest')
headrest.head = Vector((0, -2.0, 2.4))
headrest.tail = Vector((0, -2.1, 3.2))
headrest.parent = backrest

bpy.ops.object.mode_set(mode='OBJECT')

print(f'\nCreated {len(arm.bones)} bones')

# ─── Helper: setup mesh for armature ───
def setup_mesh(name):
    obj = bpy.data.objects.get(name)
    if not obj:
        print(f'  WARNING: "{name}" not found')
        return None
    obj.vertex_groups.clear()
    obj.parent = arm_obj
    obj.parent_type = 'ARMATURE'
    has_mod = any(m.type == 'ARMATURE' for m in obj.modifiers)
    if not has_mod:
        mod = obj.modifiers.new(name='Armature', type='ARMATURE')
        mod.object = arm_obj
    else:
        for m in obj.modifiers:
            if m.type == 'ARMATURE':
                m.object = arm_obj
    return obj

# ─── Rigid assignments (1 bone per entire mesh) ───
rigid = {
    '01 Base': 'Root',
    '02 Base rim': 'Root',
    '03 Base controls': 'Root',
    '04 Bottom seat': 'Cushion',
    '08 Upper neck': 'Backrest',
    '09 Header': 'Headrest',
}

for mesh_name, bone_name in rigid.items():
    obj = setup_mesh(mesh_name)
    if not obj:
        continue
    vg = obj.vertex_groups.new(name=bone_name)
    vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    print(f'  Rigid: "{mesh_name}" → {bone_name} ({len(obj.data.vertices)} verts)')

# ─── 05 Bottom sides → BolsterL / BolsterR (split by X) ───
obj = setup_mesh('05 Bottom sides')
if obj:
    vgL = obj.vertex_groups.new(name='BolsterL')
    vgR = obj.vertex_groups.new(name='BolsterR')
    vgC = obj.vertex_groups.new(name='Cushion')
    nL = nR = nC = 0
    for v in obj.data.vertices:
        idx = [v.index]
        if v.co.x < -0.05:
            vgL.add(idx, 1.0, 'REPLACE')
            nL += 1
        elif v.co.x > 0.05:
            vgR.add(idx, 1.0, 'REPLACE')
            nR += 1
        else:
            vgL.add(idx, 0.35, 'REPLACE')
            vgR.add(idx, 0.35, 'REPLACE')
            vgC.add(idx, 0.30, 'REPLACE')
            nC += 1
    print(f'  Split: "05 Bottom sides" → BolsterL({nL}) / BolsterR({nR}) / center({nC})')

# ─── 06 Back seat → Backrest / Lumbar (split by Z, weight-painted) ───
obj = setup_mesh('06 Back seat')
if obj:
    vgB = obj.vertex_groups.new(name='Backrest')
    vgLu = obj.vertex_groups.new(name='Lumbar')
    for v in obj.data.vertices:
        idx = [v.index]
        z = v.co.z
        if z < 0.5:
            vgLu.add(idx, 1.0, 'REPLACE')
        elif z < 1.0:
            t = (z - 0.5) / 0.5  # 0→1 gradient
            vgLu.add(idx, 1.0 - t, 'REPLACE')
            vgB.add(idx, t, 'REPLACE')
        else:
            vgB.add(idx, 1.0, 'REPLACE')
    print(f'  WeightPaint: "06 Back seat" → Backrest/Lumbar ({len(obj.data.vertices)} verts)')

# ─── 07 Seat back sides → BackBolsterL / BackBolsterR (split by X) ───
obj = setup_mesh('07 Seat back sides')
if obj:
    vgL = obj.vertex_groups.new(name='BackBolsterL')
    vgR = obj.vertex_groups.new(name='BackBolsterR')
    vgB = obj.vertex_groups.new(name='Backrest')
    nL = nR = nC = 0
    for v in obj.data.vertices:
        idx = [v.index]
        if v.co.x < -0.05:
            vgL.add(idx, 1.0, 'REPLACE')
            nL += 1
        elif v.co.x > 0.05:
            vgR.add(idx, 1.0, 'REPLACE')
            nR += 1
        else:
            vgL.add(idx, 0.35, 'REPLACE')
            vgR.add(idx, 0.35, 'REPLACE')
            vgB.add(idx, 0.30, 'REPLACE')
            nC += 1
    print(f'  Split: "07 Seat back sides" → BackBolsterL({nL}) / BackBolsterR({nR}) / center({nC})')

# ─── Animations ───
arm_obj.rotation_mode = 'XYZ'
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

for pb in arm_obj.pose.bones:
    pb.rotation_mode = 'XYZ'

arm_obj.animation_data_create()

# Recline
act = bpy.data.actions.new('Recline')
arm_obj.animation_data.action = act
b = arm_obj.pose.bones['Backrest']
b.rotation_euler = (0, 0, 0); b.keyframe_insert(data_path='rotation_euler', frame=0)
b.rotation_euler = (0.52, 0, 0); b.keyframe_insert(data_path='rotation_euler', frame=30)
b.rotation_euler = (0, 0, 0); b.keyframe_insert(data_path='rotation_euler', frame=60)

# Headrest
act = bpy.data.actions.new('HeadrestAdjust')
arm_obj.animation_data.action = act
b = arm_obj.pose.bones['Headrest']
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=0)
b.location = (0, 0, 0.4); b.keyframe_insert(data_path='location', frame=30)
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=60)

# Slide
act = bpy.data.actions.new('SlideForAft')
arm_obj.animation_data.action = act
b = arm_obj.pose.bones['Slide']
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=0)
b.location = (0, 0.5, 0); b.keyframe_insert(data_path='location', frame=30)
b.location = (0, -0.5, 0); b.keyframe_insert(data_path='location', frame=60)
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=90)

# Height
act = bpy.data.actions.new('HeightAdjust')
arm_obj.animation_data.action = act
b = arm_obj.pose.bones['Cushion']
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=0)
b.location = (0, 0, 0.2); b.keyframe_insert(data_path='location', frame=30)
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=60)

# Bolster Squeeze (bottom)
act = bpy.data.actions.new('BolsterSqueeze')
arm_obj.animation_data.action = act
bL = arm_obj.pose.bones['BolsterL']
bR = arm_obj.pose.bones['BolsterR']
bL.location = (0, 0, 0); bR.location = (0, 0, 0)
bL.keyframe_insert(data_path='location', frame=0); bR.keyframe_insert(data_path='location', frame=0)
bL.location = (0.15, 0, 0); bR.location = (-0.15, 0, 0)  # squeeze inward
bL.keyframe_insert(data_path='location', frame=30); bR.keyframe_insert(data_path='location', frame=30)
bL.location = (0, 0, 0); bR.location = (0, 0, 0)
bL.keyframe_insert(data_path='location', frame=60); bR.keyframe_insert(data_path='location', frame=60)

# Lumbar push
act = bpy.data.actions.new('LumbarPush')
arm_obj.animation_data.action = act
b = arm_obj.pose.bones['Lumbar']
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=0)
b.location = (0, 0.3, 0); b.keyframe_insert(data_path='location', frame=30)  # push toward occupant
b.location = (0, 0, 0); b.keyframe_insert(data_path='location', frame=60)

# Back Bolster Squeeze
act = bpy.data.actions.new('BackBolsterSqueeze')
arm_obj.animation_data.action = act
bL = arm_obj.pose.bones['BackBolsterL']
bR = arm_obj.pose.bones['BackBolsterR']
bL.location = (0, 0, 0); bR.location = (0, 0, 0)
bL.keyframe_insert(data_path='location', frame=0); bR.keyframe_insert(data_path='location', frame=0)
bL.location = (0.12, 0, 0); bR.location = (-0.12, 0, 0)
bL.keyframe_insert(data_path='location', frame=30); bR.keyframe_insert(data_path='location', frame=30)
bL.location = (0, 0, 0); bR.location = (0, 0, 0)
bL.keyframe_insert(data_path='location', frame=60); bR.keyframe_insert(data_path='location', frame=60)

arm_obj.animation_data.action = bpy.data.actions['Recline']
bpy.ops.object.mode_set(mode='OBJECT')

# ─── Export GLB ───
bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True)
all_meshes = [
    '01 Base', '02 Base rim', '03 Base controls',
    '04 Bottom seat', '05 Bottom sides',
    '06 Back seat', '07 Seat back sides',
    '08 Upper neck', '09 Header',
]
for name in all_meshes:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.select_set(True)

bpy.context.view_layer.objects.active = arm_obj

bpy.ops.export_scene.gltf(
    filepath='/home/kim/Downloads/car_seat/car_seat_rigged_v2.glb',
    export_format='GLB',
    export_animations=True,
    export_skins=True,
    use_selection=True,
    export_apply=False,
)

print('\n' + '='*50)
print('EXPORT COMPLETE: car_seat_rigged_v2.glb')
print(f'Bones: {len(arm.bones)}')
print(f'Actions: {len(bpy.data.actions)}')
for a in bpy.data.actions:
    print(f'  {a.name} (frames {a.frame_range[0]:.0f}-{a.frame_range[1]:.0f})')
print('='*50)
