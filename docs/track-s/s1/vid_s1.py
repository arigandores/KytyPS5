#!/usr/bin/env python3
# S1 (Red Team): video frame count of sc142 recordings vs shown FrameTrace rows (identity proposal T-7).
import json, os
R = {r['tag']: r for r in json.load(open('C:/kyty/s288/s1/rt_s1.json', encoding='utf-8'))}
def walk(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, p + '.' + k)
    else:
        yield p, o
for tag in sorted(R):
    path = 'C:/kyty/s142/runs142/%s.score.json' % tag
    if not os.path.exists(path):
        print(tag, 'no json'); continue
    d = json.load(open(path, encoding='utf-8'))
    vid = {k: v for k, v in walk(d) if 'video' in k.lower() or 'vid' in k.lower()}
    print(tag, 'rows', R[tag]['rows'], 'held_total', R[tag]['T2'][0], 'shown_rows', R[tag]['rows'] - R[tag]['T2'][0], vid)
