"""Session 105, pred/02_m31.md items P1 (ctx105 checks), P3 (vct105 video), P4 (ect105_* entries) and the screen
(reg105a vs reg105b). Reads raw logs only.

    python C:/kyty/s105/check105.py [--out <json>]
"""
import glob
import hashlib
import json
import os
import re
import statistics
import sys

sys.path.insert(0, 'C:/kyty/s105')
from run_safety99 import failure_marker  # noqa: E402

ROOT = 'C:/kyty/s105'
PRED = ROOT + '/pred/02_m31.md'
LINE = re.compile(rb'^(FrameTrace(?:-draw|-x)?): n=(\d+)')
FIELD = re.compile(rb'(\w+)=(-?\d+)')


def frames(tag):
    doc = json.load(open('%s/%s.json' % (ROOT, tag), encoding='utf-8'))
    ok = [a for a in doc.get('attempts', []) if a.get('outcome') == 'ok']
    stable = ok[-1].get('stable_frame', 0) if ok else None
    rows, lines = {}, []
    with open('%s/log_%s.txt' % (ROOT, tag), 'rb') as f:
        for line in f:
            m = LINE.match(line)
            if m:
                n = int(m.group(2))
                pre = {b'FrameTrace': '', b'FrameTrace-draw': 'd.', b'FrameTrace-x': 'x.'}[m.group(1)]
                d = rows.setdefault(n, {})
                for k, v in FIELD.findall(line[m.end():]):
                    d[pre + k.decode()] = int(v)
                continue
            if line.startswith(b'CtxCheck:') or failure_marker(line):
                lines.append(line[:200].decode('utf-8', 'replace').strip())
    return doc, stable, rows, lines


def p1():
    doc, stable, rows, lines = frames('ctx105')
    scene = [d for n, d in rows.items() if stable is not None and n >= stable and 'x.ctx_chk_n' in d]
    tot = lambda k: sum(d.get(k, 0) for d in rows.values())
    work = [d.get('draws', 0) + d.get('dispatches', 0) for d in scene]
    chk = [d.get('x.ctx_chk_n', 0) for d in scene]
    mid = [d.get('x.ctx_midsub', 0) for d in scene]
    res = dict(frames=len(scene), chk_bad=tot('x.ctx_chk_bad'), rec_block=tot('x.ctx_rec_block'),
               ctxcheck_lines=[l for l in lines if l.startswith('CtxCheck:')][:10],
               median_chk=statistics.median(chk) if chk else None,
               median_work=statistics.median(work) if work else None,
               midsub_mean=statistics.mean(mid) if mid else None)
    res['pass'] = (res['chk_bad'] == 0 and res['rec_block'] == 0 and not res['ctxcheck_lines']
                   and res['median_chk'] is not None and res['median_chk'] >= res['median_work'])
    # the ctx-mid site table from FrameTrace-submit lines
    sites = {}
    with open('%s/log_ctx105.txt' % ROOT, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace-submit'):
                for m in re.finditer(rb'ctx-mid:([\w-]+)=(\d+)', line):
                    sites[m.group(1).decode()] = sites.get(m.group(1).decode(), 0) + int(m.group(2))
    res['midsub_sites_total'] = sites
    return res


def p3():
    rp = '%s/vct105_glitch.txt' % ROOT
    text = open(rp, encoding='utf-8', errors='replace').read() if os.path.exists(rp) else ''
    mf = re.search(r'(\d+) frames', text)
    mg = re.search(r'one-frame glitches:\s*(\d+)', text)
    meta = json.load(open('%s/vct105.json' % ROOT, encoding='utf-8')) if os.path.exists('%s/vct105.json' % ROOT) else {}
    frames_n = int(mf.group(1)) if mf else None
    glitches = int(mg.group(1)) if mg else None
    gates = ' ' + (meta.get('gates') or '') + ' '
    return dict(frames=frames_n, glitches=glitches, gate_ctxtick1=' ctxtick=1 ' in gates,
                binary=meta.get('binary_sha256'),
                pass_=frames_n is not None and frames_n >= 3000 and glitches == 0 and ' ctxtick=1 ' in gates)


def p4():
    out = []
    for i in range(1, 11):
        tag = 'ect105_%02d' % i
        if not os.path.exists('%s/%s.json' % (ROOT, tag)):
            out.append(dict(tag=tag, missing=True))
            continue
        doc, stable, rows, lines = frames(tag)
        att = (doc.get('attempts') or [{}])[-1]
        hang = [l for l in lines if 'GpuHangAbort' in l or 'ErrorDeviceLost' in l.replace(' ', '')]
        bvh = all('role=4' in l for l in hang if 'GpuHangAbort' in l) and hang
        out.append(dict(tag=tag, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'),
                        chk_bad=sum(d.get('x.ctx_chk_bad', 0) for d in rows.values()),
                        chk_n=sum(d.get('x.ctx_chk_n', 0) for d in rows.values()),
                        hang_lines=hang[:3], bvh_signature=bool(bvh)))
    ok = all(not e.get('missing') and e['chk_bad'] == 0 and e['chk_n'] > 0 and
             (e['outcome'] == 'ok' and e['hold_exit'] is None or e['bvh_signature']) for e in out)
    return dict(entries=out, pass_=ok)


def screen():
    def mid(tag):
        rows = []
        for line in open('%s/log_%s.txt' % (ROOT, tag), 'rb'):
            if line.startswith(b'FrameTrace: '):
                m = re.search(rb' dt_us=(\d+).* draws=(\d+).* cpu_gpu_us=(\d+)', line)
                if m:
                    rows.append(tuple(int(x) for x in m.groups()))
        w = rows[len(rows) // 3: 2 * len(rows) // 3]
        return dict(mean_dt=statistics.mean(r[0] for r in w), cpu_per_draw=sum(r[2] for r in w) / sum(r[1] for r in w),
                    n=len(w))
    a, b = mid('reg105a'), mid('reg105b')
    rel = b['cpu_per_draw'] / a['cpu_per_draw'] - 1
    return dict(a=a, b=b, cpu_per_draw_rel=rel, dt_rel=b['mean_dt'] / a['mean_dt'] - 1, flag=rel > 0.02)


def main():
    res = dict(seal_sha256=hashlib.sha256(open(PRED, 'rb').read()).hexdigest())
    for name, fn in (('P1', p1), ('P3', p3), ('P4', p4), ('screen', screen)):
        try:
            res[name] = fn()
        except Exception as e:  # noqa: BLE001
            res[name] = dict(error=repr(e))
    print(json.dumps(res, indent=1, default=str))
    if '--out' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
