"""Session 103 scorer of the BVH loop-cap entry series (sealed C:/kyty/s103/pred/01_bvh_cap_series.md).

    python C:/kyty/s103/bvh103.py [--out <json>]           score every ent103_NN present
    import bvh103; bvh103.entry(tag)                       one entry (the series driver uses it)
"""
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, 'C:/kyty/s103')
from run_safety99 import failure_marker  # noqa: E402

ROOT = 'C:/kyty/s103'
PRED = ROOT + '/pred/01_bvh_cap_series.md'
ARMED = b"BvhLoopCap: cap=65536 token=''"
HANG_TOKENS = (b'gpuhangabort', b'errordevicelost', b'gpumarkerhung', b'gpucheckpointhang',
               b'std::terminate', b'abort()', b'unhandled exception', b'fatal')
COUNTED = 67
MAX_REPLACEMENTS = 3
A4_MAX_TRIP_ENTRIES = 15
A5_MAX_DT_US = 30_000_000


def seal_sha():
    return hashlib.sha256(open(PRED, 'rb').read()).hexdigest()


def entry(tag):
    log = '%s/log_%s.txt' % (ROOT, tag)
    doc_path = '%s/%s.json' % (ROOT, tag)
    res = dict(tag=tag, armed=False, hang=False, slow=0, bl_trip=0, bl_near=0, trip_log_total=0,
               near_log_total=0, max_dt_us=0, frames=0, outcome=None, hold_exit=None,
               binary_sha256=None, markers=[])
    if os.path.exists(doc_path):
        doc = json.load(open(doc_path, encoding='utf-8'))
        res['binary_sha256'] = doc.get('binary_sha256')
        attempts = doc.get('attempts') or []
        counted = [a for a in attempts if a.get('label') != 'warmup'] or attempts
        if counted:
            res['outcome'] = counted[-1].get('outcome')
            res['hold_exit'] = counted[-1].get('hold_exit')
    logs = [log] + sorted(glob.glob('%s/log_%s_a*.txt' % (ROOT, tag)))
    for path in logs:
        if not os.path.exists(path):
            continue
        with open(path, 'rb') as f:
            for line in f:
                if line.startswith(b'FrameTrace: '):
                    m = re.search(rb' dt_us=(\d+)', line)
                    if m:
                        res['max_dt_us'] = max(res['max_dt_us'], int(m.group(1)))
                        res['frames'] += 1
                    continue
                if line.startswith(b'FrameTrace-x: '):
                    m = re.search(rb' bl_trip=(\d+)', line)
                    if m:
                        res['bl_trip'] += int(m.group(1))
                    m = re.search(rb' bl_near=(\d+)', line)
                    if m:
                        res['bl_near'] += int(m.group(1))
                    continue
                if ARMED in line:
                    res['armed'] = True
                if line.startswith(b'BvhLoopCapTrip:'):
                    m = re.search(rb'total=(\d+) near=\+\d+ near_total=(\d+)', line)
                    if m:
                        res['trip_log_total'] = max(res['trip_log_total'], int(m.group(1)))
                        res['near_log_total'] = max(res['near_log_total'], int(m.group(2)))
                if failure_marker(line):
                    low = line.lower()
                    if b'gpuwaitslow' in low:
                        res['slow'] += 1
                    if any(t in low for t in HANG_TOKENS):
                        res['hang'] = True
                        if len(res['markers']) < 4:
                            res['markers'].append(line[:200].decode('utf-8', 'replace').strip())
    res['trips'] = max(res['bl_trip'], res['trip_log_total'])
    res['near'] = max(res['bl_near'], res['near_log_total'])
    ok = res['outcome'] == 'ok' and res['hold_exit'] is None
    if res['hang']:
        res['class'] = 'hang'
    elif ok:
        res['class'] = 'ok'
    else:
        res['class'] = 'technical'
    return res


def verdict(entries):
    counted, replacements, technical = [], 0, []
    for e in entries:
        if e['class'] == 'technical':
            technical.append(e['tag'])
            continue
        counted.append(e)
    items = {}
    items['A1_armed'] = all(e['armed'] for e in counted)
    hangs = [e['tag'] for e in counted if e['class'] == 'hang']
    items['A2_no_hang'] = not hangs and len(counted) >= COUNTED and len(technical) <= MAX_REPLACEMENTS
    items['A3_margin'] = all(e['near'] == 0 for e in counted)
    trip_entries = [e['tag'] for e in counted if e['trips'] > 0]
    items['A4_not_systematic'] = len(trip_entries) <= A4_MAX_TRIP_ENTRIES
    worst = max((e['max_dt_us'] for e in counted), default=0)
    items['A5_worst_frame'] = worst < A5_MAX_DT_US
    accepted = all(items.values())
    return dict(accepted=accepted, verdict='ACCEPTED' if accepted else 'NOT ACCEPTED',
                items=items, counted=len(counted), technical=technical, hangs=hangs,
                trip_entries=trip_entries, worst_dt_us=worst,
                total_trips=sum(e['trips'] for e in counted),
                total_near=sum(e['near'] for e in counted),
                binaries=sorted({e['binary_sha256'] for e in counted if e['binary_sha256']}))


def main():
    tags = sorted({os.path.basename(p)[:-5] for p in glob.glob(ROOT + '/ent103_[0-9][0-9].json')})
    entries = [entry(t) for t in tags]
    v = verdict(entries)
    v['seal_sha256'] = seal_sha()
    for e in entries:
        print('%-10s %-9s armed=%d trips=%d near=%d slow=%d max_dt=%.2fs frames=%d %s' % (
            e['tag'], e['class'], e['armed'], e['trips'], e['near'], e['slow'], e['max_dt_us'] / 1e6,
            e['frames'], '; '.join(e['markers'])[:160]))
    print(json.dumps({k: v[k] for k in ('verdict', 'items', 'counted', 'technical', 'hangs',
                                         'trip_entries', 'worst_dt_us', 'total_trips',
                                         'total_near', 'binaries', 'seal_sha256')}, indent=1))
    if '--out' in sys.argv:
        json.dump(dict(verdict=v, entries=entries), open(sys.argv[sys.argv.index('--out') + 1], 'w'),
                  indent=1)


if __name__ == '__main__':
    main()
