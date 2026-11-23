# 시험용 가상 교량(4경간 120m)과 일정표를 만든다. 실제 과업 자료가 아님.
import trimesh, numpy as np, csv, json, datetime, sys, io
out = sys.argv[1]
sc = trimesh.Scene(); tasks = []
def box(cx, cy, cz, sx, sy, sz):
    m = trimesh.creation.box(extents=(sx, sy, sz)); m.apply_translation((cx, cy, cz)); return m
def add(tid, name, typ, start, days, meshes):
    m = trimesh.util.concatenate(meshes)
    sc.add_geometry(m, node_name=tid, geom_name=tid)
    s = datetime.date.fromisoformat(start); e = s + datetime.timedelta(days=days)
    tasks.append([tid, name, s.isoformat(), e.isoformat(), typ])
n = 0
def tid():
    global n; n += 1; return 'T%03d' % n
sup = [('A1', 0), ('P1', 30), ('P2', 60), ('P3', 90), ('A2', 120)]
H = 14.0; W = 18.0
d0 = datetime.date(2027, 1, 4)
def day(k): return (d0 + datetime.timedelta(days=k)).isoformat()
k = 0
for nm, x in sup:                       # 기초 → 기둥 → 코핑
    ab = nm.startswith('A')
    add(tid(), nm + ' 기초', '시공', day(k), 40, [box(x, -1.0, 0, 9 if not ab else 7, 2.0, 14 if not ab else W + 2)])
    if ab: add(tid(), nm + ' 벽체', '시공', day(k + 45), 50, [box(x, H / 2, 0, 2.5, H, W)])
    else:  add(tid(), nm + ' 기둥', '시공', day(k + 45), 50, [box(x, (H - 2) / 2, -4.5, 2.4, H - 2, 2.4), box(x, (H - 2) / 2, 4.5, 2.4, H - 2, 2.4)])
    if not ab: add(tid(), nm + ' 코핑', '시공', day(k + 100), 30, [box(x, H - 1, 0, 3.0, 2.0, W - 2)])
    k += 60
k = 330
for i in range(4):                      # 가설 벤트(가설) → 거더 → 바닥판 → 벤트 해체
    x0, x1 = sup[i][1], sup[i + 1][1]; xm = (x0 + x1) / 2
    bent = tid(); add(bent, 'S%d 가설 벤트' % (i + 1), '가설', day(k), 75, [box(xm, H / 2 - 0.2, zz, 1.2, H - 0.4, 1.2) for zz in (-6, 0, 6)])
    add(tid(), 'S%d 거더 가설' % (i + 1), '시공', day(k + 15), 25, [box(xm, H + 1.0, zz, x1 - x0 - 0.6, 2.0, 1.0) for zz in (-6.75, -2.25, 2.25, 6.75)])
    add(tid(), 'S%d 바닥판' % (i + 1), '시공', day(k + 45), 30, [box(xm, H + 2.15, 0, x1 - x0, 0.3, W)])
    k += 70
add(tid(), '방호벽', '시공', day(k + 20), 45, [box(60, H + 2.8, zz, 120, 1.0, 0.4) for zz in (-W / 2 + 0.2, W / 2 - 0.2)])
add(tid(), '포장', '시공', day(k + 70), 30, [box(60, H + 2.34, 0, 120, 0.08, W - 0.8)])
sc.export(out + '/model.glb')
with io.open(out + '/tasks.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['task_id', 'name', 'start', 'end', 'type']); w.writerows(tasks)
with io.open(out + '/drawings.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['drawing_id', 'title', 'marker_id', 'scale', 'marker_size_mm', 'origin_dx_mm', 'origin_dy_mm', 'rotation_deg', 'model'])
    w.writerow(['DWG-001', '시험용 교량 평면도', 7, 500, 50, -17, -80, 0, 'model.glb'])
json.dump({'source': '시험용 가상 모델 (tools/make_sample.py)', 'exported': datetime.date.today().isoformat(), 'tasks': len(tasks), 'unattached_tasks': []}, io.open(out + '/info.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('tasks', len(tasks), tasks[0], tasks[-1])
