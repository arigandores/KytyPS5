# F32d (HPP-742): merged input for the unchanged F32a report scripts (rep_f32a.py, extra_f32a.py) - the F32a delta records
# plus the 36 out-of-mask records of the F32d sweep.  A record of the 36 whose sha256 equals an F32a record gets dup_of = that
# F32a path (the canonical copy is the F32a one); records inside the 36 keep the sweep's own dup_of / in_f0.  Segment and
# witness files are copied (file names are md5(path), so the two sets do not collide; a collision is a FAILED).
# Usage: python merge_f32d.py <f32a_out> <f32d_sweep_out> <merged_out>
import os, sys, json, shutil
NL = chr(10)
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
if os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(4)
A, D, M = sys.argv[1:4]
a = json.load(open(A + '/agg_f32a.json', encoding='utf-8'))
d = json.load(open(D + '/agg_f32a.json', encoding='utf-8'))
sha_a = {}
for r in a:
    if not r['dup_of'] and not r['in_f0']:
        sha_a.setdefault(r['sha256'], r['path'])
paths_a = set(r['path'] for r in a)
ok = True
eq = 0
for r in d:
    if r['path'] in paths_a:
        print('FAILED path in both', r['path'])
        ok = False
    if not r['dup_of'] and not r['in_f0'] and r['sha256'] in sha_a:
        r['dup_of'] = sha_a[r['sha256']]
        eq += 1
for sub in ('seg', 'wit'):
    os.makedirs(M + '/' + sub, exist_ok=True)
    for src in (A, D):
        for f in os.listdir(src + '/' + sub):
            dst = M + '/' + sub + '/' + f
            if os.path.exists(dst) and src == D:
                print('FAILED file collision', sub, f)
                ok = False
                continue
            shutil.copyfile(src + '/' + sub + '/' + f, dst)
with open(M + '/agg_f32a.json', 'w', encoding='utf-8', newline=NL) as o:
    json.dump(a + d, o, ensure_ascii=False, indent=0)
u = [r for r in a + d if not r['dup_of'] and not r['in_f0']]
print('records', len(a) + len(d), 'F32a', len(a), 'F32d', len(d), 'F32d equal to an F32a log', eq, 'unique merged', len(u),
      'unique new of F32d', sum(1 for r in d if not r['dup_of'] and not r['in_f0']))
print('ALL OK' if ok else 'FAILED')
