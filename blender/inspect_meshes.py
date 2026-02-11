import bpy
import json

# Print all mesh objects with their bounding box info
for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if obj.type != 'MESH':
        continue
    verts = obj.data.vertices
    if len(verts) == 0:
        continue

    # Get world-space vertex positions
    xs = [v.co.x for v in verts]
    ys = [v.co.y for v in verts]
    zs = [v.co.z for v in verts]

    print(f"\n=== {obj.name} === ({len(verts)} verts)")
    print(f"  X: {min(xs):.3f} ~ {max(xs):.3f}  (width: {max(xs)-min(xs):.3f})")
    print(f"  Y: {min(ys):.3f} ~ {max(ys):.3f}  (depth: {max(ys)-min(ys):.3f})")
    print(f"  Z: {min(zs):.3f} ~ {max(zs):.3f}  (height: {max(zs)-min(zs):.3f})")
    print(f"  Center: ({(min(xs)+max(xs))/2:.3f}, {(min(ys)+max(ys))/2:.3f}, {(min(zs)+max(zs))/2:.3f})")

    # Check if mesh is symmetric (can be split L/R)
    left_count = sum(1 for v in verts if v.co.x < -0.05)
    right_count = sum(1 for v in verts if v.co.x > 0.05)
    center_count = len(verts) - left_count - right_count
    print(f"  L/C/R verts: {left_count}/{center_count}/{right_count}")
