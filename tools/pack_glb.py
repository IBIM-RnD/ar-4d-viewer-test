# Blender에서 실행: 작업별 FBX(T001.fbx ...)를 작업 단위로 합치고 면 수를 줄여 model.glb 하나로 묶는다.
#   blender -b --python pack_glb.py -- <FBX 폴더> <면 수 비율 0~1>
# 객체 이름 = 작업 ID. 묶은 뒤 tasks.csv 와 맞는지 검사하고, 도면 배치용 drawings.csv 를 쓴다.
import bpy, sys, glob, os, time, csv, io, json, math
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; S = a[0]; RATIO = float(a[1]) if len(a) > 1 else 1.0
t0 = time.time(); bpy.ops.wm.read_factory_settings(use_empty=True)
f0 = f1 = 0; made = []
for f in sorted(glob.glob(S + '/T*.fbx')):
    tid = os.path.splitext(os.path.basename(f))[0]
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f)
    newnames = [o.name for o in bpy.data.objects if o.name not in before]
    meshes = [bpy.data.objects[n] for n in newnames if bpy.data.objects[n].type == 'MESH' and len(bpy.data.objects[n].data.polygons)]
    if not meshes:
        for n in newnames: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
        continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    if len(meshes) > 1: bpy.ops.object.join()          # 같은 작업의 부재끼리만 합침
    j = bpy.context.view_layer.objects.active; jn = j.name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    f0 += len(j.data.polygons)
    if RATIO < 1.0 and len(j.data.polygons) > 50:
        m = j.modifiers.new('dec', 'DECIMATE'); m.ratio = RATIO; bpy.ops.object.modifier_apply(modifier=m.name)
    f1 += len(j.data.polygons)
    for n in newnames:
        if n != jn and n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
    for k in list(j.keys()): del j[k]
    j.name = tid; j.data.name = tid; made.append(tid)
# 원점을 모델 바닥 중심으로 옮김 (큰 좌표로 인한 떨림 방지)
lo = Vector((1e18,) * 3); hi = Vector((-1e18,) * 3)
for tid in made:
    for c in bpy.data.objects[tid].bound_box:
        for i in range(3): lo[i] = min(lo[i], c[i]); hi[i] = max(hi[i], c[i])
off = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
for tid in made:
    o = bpy.data.objects[tid]; o.data.transform(__import__('mathutils').Matrix.Translation(-off))
tris = 0
for tid in made:
    me = bpy.data.objects[tid].data; me.calc_loop_triangles(); tris += len(me.loop_triangles)
bpy.ops.export_scene.gltf(filepath=S + '/model.glb', export_format='GLB', export_materials='NONE')
# 연결 검사
ids = [r['task_id'] for r in csv.DictReader(io.open(S + '/tasks.csv', encoding='utf-8-sig'))]
missing = sorted(set(ids) - set(made)); extra = sorted(set(made) - set(ids))
sx, sy = hi.x - lo.x, hi.y - lo.y
scale = int(math.ceil(max(sx / 0.240, sy / 0.110) / 50.0) * 50)      # A4 가로 도면의 240×110mm 칸에 들어가는 축척
with io.open(S + '/drawings.csv', 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh); w.writerow(['drawing_id', 'title', 'marker_id', 'scale', 'marker_size_mm', 'origin_dx_mm', 'origin_dy_mm', 'rotation_deg', 'model'])
    w.writerow(['DWG-001', 'Navisworks 샘플 (작업 %d개)' % len(made), 7, scale, 50, 103, -80, 0, 'model.glb'])
json.dump({'tasks': len(made), 'faces_before': f0, 'faces_after': f1, 'triangles': tris, 'size_m': [round(sx, 1), round(sy, 1), round(hi.z - lo.z, 1)], 'origin_shift': [round(v, 3) for v in off], 'scale': scale,
           'missing_in_model': missing, 'extra_in_model': extra, 'seconds': round(time.time() - t0, 1), 'glb_mb': round(os.path.getsize(S + '/model.glb') / 1e6, 2)},
          io.open(S + '/info.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('RESULT', open(S + '/info.json', encoding='utf-8').read().replace('\n', ' '))
