# F26a (HPP-688, item 629(v)(3)): inventory of the intro_next entries (sweep_f26a.jsonl + meta_f26a.jsonl) and the
# historical count of sessions 42-127 (F0 aggregate C:/kyty/f287/f0/agg_f0.json, swept 2026-10-01 before the xz of p.328).
# Course line binaries (installed since 9235a7ac, CLAUDE.md state line): sha8 set COURSE below.
# Integrity of a log: counts of b'--- Error ---' and b'Unhandled host exception' (0 and 0 = intact), 'Event: quit' line or not.
import json, lzma, mmap, os, re, collections, sys
COURSE = {'9235a7ac': 's128 (4fc501f4)', 'dac02fb9': 'FSd', 'bbad499c': 'FS2', '4aa62e95': 'P23', '540c035a': 'FS3',
          '31cbfee8': 'FS4', '631ff987': 'FS5', 'adb0c82f': 'S12', '9325446c': 'FS6', '8df61c00': 'FS7',
          '2c9b69b9': 'FS8', 'b3cee576': 'S18', '3861eeea': 'FS9', 'abfded5e': 'FS10'}
R = [json.loads(l) for l in open('sweep_f26a.jsonl', encoding='utf-8')]
M = {json.loads(l)['path']: json.loads(l) for l in open('meta_f26a.jsonl', encoding='utf-8')}


def count(p, s):
    if p.endswith('.xz'):
        n = 0; keep = b''
        with lzma.open(p, 'rb') as f:
            while True:
                ch = f.read(1 << 24)
                if not ch: break
                b = keep + ch; i = b.find(s)
                while i >= 0:
                    if i + len(s) > len(keep): n += 1
                    i = b.find(s, i + len(s))
                keep = b[-64:]
        return n
    with open(p, 'rb') as f:
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        n = 0; i = m.find(s)
        while i >= 0:
            n += 1; i = m.find(s, i + len(s))
        m.close(); return n


print('== (3a) sweep of %d logs (list_f26a.tsv, roots s128+ / f287 / p283 / s288 / play); read errors %d' %
      (len(R), sum(1 for r in R if 'error' in r)))
print('logs with S1/S2/S3 (B25 signature): %d' % sum(1 for r in R if r.get('S1') or r.get('S2') or r.get('S3')))
rows = []
for r in R:
    if not r.get('E'):
        continue
    w = r['walk']; m = M.get(r['path'], {})
    sha = (m.get('binary_sha256') or '-')[:8]
    lv = w['levels']
    err = count(r['path'], b'--- Error ---'); uhe = count(r['path'], b'Unhandled host exception')
    for i, x in enumerate(lv):
        if x['name'] != 'intro_next':
            continue
        nt = lv[i + 1]['t'] if i + 1 < len(lv) else w['last_t']
        hold = (nt or 0) - (x['t'] or 0)
        env = m.get('env') or {}
        knobs = sorted(k for k in env if k.startswith('KYTY_') and k not in (
            'KYTY_FRAME_TRACE', 'KYTY_GATE_FILE', 'KYTY_GPU_CLOCK_PIN', 'KYTY_GPU_HANG_ABORT_S', 'KYTY_GPU_MARKERS',
            'KYTY_GUEST_ARGS', 'KYTY_QUEUE_TRACE', 'KYTY_SAMPLE_GATE', 'KYTY_REC', 'KYTY_AV_TRACE'))
        rows.append((r['path'], sha, COURSE.get(sha, '-'), x['t'], hold, x['frames'], x['sum_us'] / 1e6, r['S1'],
                     err, uhe, w['quit_line'] is not None, m.get('validation'), knobs))
rows.sort(key=lambda x: x[0])
print('== (3b) intro_next entries: %d in %d logs' % (len(rows), len({x[0] for x in rows})))
print('path | sha8 | course | t_entry s | hold s (wall) | frames | sum dt s | assert | --- Error --- | Unhandled | quit | vk-val | knobs')
for x in rows:
    print('%s | %s | %s | %.1f | %.1f | %d | %.1f | %d | %d | %d | %s | %s | %s' % (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7],
          x[8], x[9], 'yes' if x[10] else 'no', x[11], ','.join(x[12]) or '-'))
c90 = [x for x in rows if x[4] >= 90]
cc = [x for x in c90 if x[2] != '-']
print('entries with hold >= 90 s: %d; on course line binaries: %d (intact: %d); assert: %d' %
      (len(c90), len(cc), sum(1 for x in cc if x[8] == 0 and x[9] == 0), sum(x[7] for x in c90)))
print('course entries by binary:', dict(collections.Counter(x[2] for x in cc)))
# historical
A = json.load(open('C:/kyty/f287/f0/agg_f0.json', encoding='utf-8'))
def sess(r):
    s = r.get('session')
    try: return int(s)
    except Exception: return None
H = [r for r in A if r['dup_of'] is None and 'intro_next' in (r.get('levels') or [])]
print('== (3c) historical (F0 aggregate, %d logs, %d non-duplicate with intro_next)' % (len(A), len(H)))
SIG = {'C:/kyty/log_s14_s42_merged_cold.txt', 'C:/kyty/s59/log_sig1.txt'}
def bucket(r):
    s = sess(r)
    p = r['path']
    m = re.search(r'_s(\d+)_', p.rsplit('/', 1)[1])
    if s is None and m: s = int(m.group(1))
    return s
by = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in H:
    s = bucket(r)
    k = 'none' if s is None else ('<42' if s < 42 else ('42-127' if s <= 127 else '128+'))
    sc = [x for x in r.get('scenes') or [] if x['level'] == 'intro_next']
    su = max([x.get('sum_us', 0) for x in sc] or [0])
    by[k][0] += 1
    by[k][1] += su >= 90e6
    by[k][2] += su == 0
    by[k][3] += r['path'] in SIG
for k in sorted(by):
    v = by[k]
    print('sessions %-7s logs with intro_next %4d | intro FrameTrace sum >= 90 s %4d | no FrameTrace in intro %4d | B25 assert %d' %
          (k, v[0], v[1], v[2], v[3]))
for r in H:
    if r['path'] in SIG:
        print('  assert log %s session %s bucket %s' % (r['path'], r.get('session'), bucket(r)))
