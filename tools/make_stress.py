# 무게 시험용 가상 교량. 같은 도면(DWG-001) 위에 작업 수와 삼각형 수만 늘린다. 실제 과업 자료가 아님.
# 사용: python make_stress.py <출력폴더> <분할수> <세분횟수>
import trimesh, numpy as np, csv, json, datetime, sys, io, os
out, SEG, SUB = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
os.makedirs(out, exist_ok=True)
sc = trimesh.Scene(); tasks = []; tri = 0
def box(cx, cy, cz, sx, sy, sz):
    m = trimesh.creation.box(extents=(sx, sy, sz))
    for _ in range(SUB): m = m.subdivide()
    m.apply_translation((cx, cy, cz)); return m
def cyl(cx, cy, cz, r, h):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=8 * 2 ** min(SUB, 4))
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0))); m.apply_translation((cx, cy, cz)); return m
n = 0; k = 0
def add(name, typ, days, meshes, gap=None):
    global n, k, tri
    n += 1; tid = 'T%03d' % n
    m = trimesh.util.concatenate(meshes); tri += len(m.faces)
    sc.add_geometry(m, node_name=tid, geom_name=tid)
    s = datetime.date(2027, 1, 4) + datetime.timedelta(days=int(k)); e = s + datetime.timedelta(days=days)
    tasks.append([tid, name, s.isoformat(), e.isoformat(), typ]); k += days * 0.45 if gap is None else gap
H = 14.0; W = 18.0
sup = [('A1', 0), ('P1', 30), ('P2', 60), ('P3', 90), ('A2', 120)]
for nm, x in sup:
    ab = nm.startswith('A')
    for i, (px, pz) in enumerate([(dx, dz) for dx in (-2.5, 2.5) for dz in (-5, 0, 5)]):
        add('%s 말뚝 %d' % (nm, i + 1), '시공', 6, [cyl(x + px, -7, pz, 0.6, 10)])
    add(nm + ' 기초', '시공', 25, [box(x, -1.0, 0, 8, 2.0, 14 if not ab else W + 2)])
    L = 4; lh = (H if ab else H - 2) / L
    for i in range(L):
        y = lh * (i + 0.5)
        if ab: add('%s 벽체 %d단' % (nm, i + 1), '시공', 12, [box(x, y, 0, 2.5, lh, W)])
        else:
            for j, z in enumerate((-4.5, 4.5)): add('%s 기둥%d %d단' % (nm, j + 1, i + 1), '시공', 8, [box(x, y, z, 2.4, lh, 2.4)])
    if not ab: add(nm + ' 코핑', '시공', 20, [box(x, H - 1, 0, 3.0, 2.0, W - 2)])
for i in range(4):
    x0, x1 = sup[i][1], sup[i + 1][1]; xm = (x0 + x1) / 2; sl = (x1 - x0) / SEG
    for j, zz in enumerate((-6, 0, 6)): add('S%d 가설 벤트 %d' % (i + 1, j + 1), '가설', 60, [box(xm, H / 2 - 0.2, zz, 1.2, H - 0.4, 1.2)], gap=2)
    for j, zz in enumerate((-6.75, -2.25, 2.25, 6.75)): add('S%d 거더 G%d' % (i + 1, j + 1), '시공', 5, [box(xm, H + 1.0, zz, x1 - x0 - 0.6, 2.0, 1.0)])
    for j in range(SEG): add('S%d 바닥판 %d' % (i + 1, j + 1), '시공', 8, [box(x0 + sl * (j + .5), H + 2.15, 0, sl, 0.3, W)])
    for j in range(SEG):
        for q, zz in enumerate((-W / 2 + 0.2, W / 2 - 0.2)): add('S%d 방호벽 %s%d' % (i + 1, 'LR'[q], j + 1), '시공', 4, [box(x0 + sl * (j + .5), H + 2.8, zz, sl, 1.0, 0.4)])
    for j in range(SEG): add('S%d 포장 %d' % (i + 1, j + 1), '시공', 3, [box(x0 + sl * (j + .5), H + 2.34, 0, sl, 0.08, W - 0.8)])
sc.export(out + '/model.glb')
with io.open(out + '/tasks.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['task_id', 'name', 'start', 'end', 'type']); w.writerows(tasks)
with io.open(out + '/drawings.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['drawing_id', 'title', 'marker_id', 'scale', 'marker_size_mm', 'origin_dx_mm', 'origin_dy_mm', 'rotation_deg', 'model'])
    w.writerow(['DWG-001', '무게 시험 (작업 %d개, 삼각형 %s)' % (len(tasks), format(tri, ',')), 7, 500, 50, -17, -80, 0, 'model.glb'])
json.dump({'source': '무게 시험용 가상 모델 (tools/make_stress.py)', 'exported': datetime.date.today().isoformat(), 'tasks': len(tasks), 'triangles': tri}, io.open(out + '/info.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out, 'tasks', len(tasks), 'triangles', tri, 'last', tasks[-1][3], 'MB', round(os.path.getsize(out + '/model.glb') / 1e6, 1))
