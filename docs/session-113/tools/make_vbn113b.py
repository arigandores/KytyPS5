"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 5 (b): vbn113b.py from vbn113.py (the draft, sha pinned) by anchored
replacements - the pre-run audit's corrections: the new build (race-separating check, counter bda_nrace), INVESTIGATE
for a BAD made only of bda_nxthr, B3-B5 as medians over the scene rows, new admission terms STREAMS and PRE_RUN, a B6
prediction on races.  Byte-reproducible.

    python C:/kyty/s106_stage/make_vbn113b.py
"""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
SRC_SHA = 'fa35ad73'   # prefix of the draft vbn113.py (the sealed copy differs only in PRED_SHA / PRED_BYTES)

src = (STAGE / 'vbn113.py').read_bytes().decode('utf-8').replace('\r\n', '\n')
assert hashlib.sha256(src.encode('utf-8')).hexdigest().startswith(SRC_SHA), hashlib.sha256(src.encode('utf-8')).hexdigest()
NL = chr(10)
PAIRS = [
    ('"""Session 113, pred/01_vbn113.md: the verify run of knob `bdanarrow` in mode 2',
     '"""Session 113, pred/01b_vbn113b.md (from vbn113.py by make_vbn113b.py - seal 01 superseded before any run by the\n'
     'pre-run audit, ROADMAP item 5): the verify run of knob `bdanarrow` in mode 2'),
    ("""whose dirty ranges overlap a registered buffer: bda_nmiss), Sky Garden 300 s, pinned, compute precache ON.  Written
fresh for session 113 (the admission terms follow vds111b.py / vdg112.py).""",
     """whose dirty ranges overlap a registered buffer and whose write stamp did not move while they were collected:
bda_nmiss; the moved ones are races, bda_nrace), Sky Garden 300 s, pinned, compute precache ON."""),
    ("""    NO_GO          admitted, BAD > 0 (mode 1 is closed as built)""",
     """    NO_GO          admitted, sum(bda_nmiss) > 0 (mode 1 is closed as built)
    INVESTIGATE    admitted, sum(bda_nmiss) == 0 and sum(bda_nxthr) > 0 (an unknown off-thread registrar: neither
                   GO nor a closing verdict)"""),
    ("    python C:/kyty/s113/vbn113.py [--tag vbn113|vbn113b] [--root C:/kyty/s113] [--out <json>]",
     "    python C:/kyty/s113/vbn113b.py [--tag vbn113|vbn113b] [--root C:/kyty/s113] [--out <json>]"),
    ("PRED = 'C:/kyty/s113/pred/01_vbn113.md'", "PRED = 'C:/kyty/s113/pred/01b_vbn113b.md'"),
    ("PRED_SHA = None     # pred/01_vbn113.md sealed", "PRED_SHA = None     # pred/01b_vbn113b.md sealed"),
    ("PRED_BYTES = None   # pred/01_vbn113.md sealed", "PRED_BYTES = None   # pred/01b_vbn113b.md sealed"),
    ("BINARY_SHA = '94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92'",
     "BINARY_SHA = '7d9fa0288099204f16974292a0d474afee80e58df43770612e11b8d5db5d6e5f'"),
    ("MIN_WOULD = 1000           # sum bda_nwould: the check must have looked at something",
     "MIN_WOULD = 1000           # sum bda_nwould: the check must have looked at something\n"
     "MAX_GPU_UTIL = 10.0        # pre_run gpu_util_median of the launcher: nothing else on the GPU before the run"),
    ("            'bgc_evict', 'da_q_free', 'cspfree_hit', 'cspfree_bad')",
     "            'bgc_evict', 'bda_nrace', 'da_q_free', 'cspfree_hit', 'cspfree_bad')"),
    ("X_ROW = re.compile(rb'^FrameTrace-x: n=(\\d+)')",
     "X_ROW = re.compile(rb'^FrameTrace-x: n=(\\d+)')\nMAIN_ROW = re.compile(rb'^FrameTrace: n=(\\d+)')"),
    ("""    ('B3', 'bda_ginv_reg level in [0.5, 3] a frame (global invalidations by registrations)',
     lambda r: r['per_row']['bda_ginv_reg'], 0.5, 3.0),
    ('B4', 'bda_nwould level in [800, 1400] a frame (what mode 1 would skip)',
     lambda r: r['per_row']['bda_nwould'], 800, 1400),
    ('B5', 'bgc_evict in [0.5, 3] a frame (the buffer GC runs)', lambda r: r['per_row']['bgc_evict'], 0.5, 3.0),
)""",
     """    ('B3', 'bda_ginv_reg median over the scene rows in [0.5, 3] a frame (global invalidations by registrations)',
     lambda r: r['level']['bda_ginv_reg'], 0.5, 3.0),
    ('B4', 'bda_nwould median over the scene rows in [800, 1400] a frame (what mode 1 would skip)',
     lambda r: r['level']['bda_nwould'], 800, 1400),
    ('B5', 'bgc_evict median over the scene rows in [0.5, 3] a frame (the buffer GC runs)',
     lambda r: r['level']['bgc_evict'], 0.5, 3.0),
    ('B6', 'sum bda_nrace <= 40 (races the check separated; the audit estimated 0.4-40 in 300 s)',
     lambda r: r['total']['bda_nrace'], None, 40),
)"""),
    ("""    pins = pin1 = markers = rows = missing = 0
    tot = {k: 0 for k in FIELDS_X}
    scans = []""",
     """    pr = meta.get('pre_run') or {}
    if not isinstance(pr.get('gpu_util_median'), (int, float)) or pr['gpu_util_median'] > MAX_GPU_UTIL:
        errors.append('PRE_RUN')
    pins = pin1 = markers = rows = missing = main_rows = 0
    tot = {k: 0 for k in FIELDS_X}
    scans = []
    scene = {k: [] for k in ('bda_ginv_reg', 'bda_nwould', 'bgc_evict')}
    xns = []"""),
    ("""            m = X_ROW.match(line)
            if m:
                rows += 1
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS_X))
                for k in FIELDS_X:
                    tot[k] += d.get(k, 0)
                continue""",
     """            if MAIN_ROW.match(line):
                main_rows += 1
                continue
            m = X_ROW.match(line)
            if m:
                rows += 1
                xns.append(int(m.group(1)))
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS_X))
                for k in FIELDS_X:
                    tot[k] += d.get(k, 0)
                if int(m.group(1)) >= stable:
                    for k in scene:
                        scene[k].append(d.get(k, 0))
                continue"""),
    ("""    if rows < MIN_ROWS or missing:
        errors.append('ROWS')""",
     """    if rows < MIN_ROWS or missing:
        errors.append('ROWS')
    # every flip reported once, in order, and every main row has its x row (a glued or lost row would hide counts)
    if (not xns or any(b - a != 1 for a, b in zip(xns, xns[1:])) or abs(rows - main_rows) > 1):
        errors.append('STREAMS')"""),
    ("""    per_row = {k: tot[k] / rows if rows else 0.0 for k in FIELDS_X}
    out.update(errors=errors, rows=rows, total=tot, per_row=per_row, bad=bad, regime_old=regime_old,
               level={'bda_scan': scan_level}, scan_rows=len(scans))""",
     """    per_row = {k: tot[k] / rows if rows else 0.0 for k in FIELDS_X}
    level = {'bda_scan': scan_level}
    level.update({k: (statistics.median(v) if v else 0) for k, v in scene.items()})
    out.update(errors=errors, rows=rows, main_rows=main_rows, total=tot, per_row=per_row, bad=bad,
               regime_old=regime_old, level=level, scan_rows=len(scans), pre_run_gpu_util=pr.get('gpu_util_median'))"""),
    ("""    elif bad == 0:
        out['verdict'] = 'GO'
    else:
        out['verdict'] = 'NO_GO'""",
     """    elif bad == 0:
        out['verdict'] = 'GO'
    elif tot['bda_nmiss'] == 0:
        out['verdict'] = 'INVESTIGATE'
    else:
        out['verdict'] = 'NO_GO'"""),
    ("""    if 'level' in res:
        print('  bda_scan level %s  regime %s' % (res['level']['bda_scan'], 'OLD' if res['regime_old'] else 'NEW'))""",
     """    if 'level' in res:
        print('  levels (medians over the scene rows) %s  regime %s' % (res['level'],
                                                                      'OLD' if res['regime_old'] else 'NEW'))
        print('  main rows %s  pre_run gpu util %s' % (res.get('main_rows'), res.get('pre_run_gpu_util')))"""),
    ("    return 0 if res['verdict'] in ('GO', 'NO_GO', 'NOT_EVALUABLE') else 1",
     "    return 0 if res['verdict'] in ('GO', 'NO_GO', 'NOT_EVALUABLE', 'INVESTIGATE') else 1"),
]
for a, b in PAIRS:
    assert src.count(a) == 1, (a[:80], src.count(a))
    src = src.replace(a, b)
(STAGE / 'vbn113b.py').write_bytes(src.encode('utf-8'))
print('vbn113b.py', hashlib.sha256(src.encode('utf-8')).hexdigest())
