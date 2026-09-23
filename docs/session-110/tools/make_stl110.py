"""Session 110: derive stl110.py (the duration guard of knob `cspfree`, ABBA of entries) from the session-109
ent109b.py (unpinned staging copy) by anchored substitutions.  Byte-reproducible."""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
SRC_SHA = '3947236bcf47a06a73ded592155523d932ecc1b697d1ff0662a2625e1911f6e4'  # ent109b.py as generated in s109
src = (STAGE / 'ent109b.py').read_bytes()
assert hashlib.sha256(src).hexdigest() == SRC_SHA, 'ent109b.py moved'
s = src.decode('utf-8')
pairs = [
    ('''"""Session 109, pred/02_ent109b.md: the powered guard of knob `cspfree` as an ABBA of ENTRIES (derived from
ent109.py by make_ent109b.py).''', '''"""Session 110, pred/01_stl110.md: the powered guard of knob `cspfree` by stall DURATION, an ABBA of ENTRIES (derived
from ent109b.py by make_stl110.py).'''),
    ('''(A = gates_free0.txt, cspfree=0; B = gates_free1.txt, cspfree=1), 150 s each, pinned.  Over ALL
FrameTrace-x rows of each entry (the load included) S = sum(cs_sync_new + cs_sync_wait).
    PASS      admitted, S_A > 0 (the positive control: the guard has exposure) and S_B <= S_A + SLACK
    FAIL      admitted, S_A > 0 and S_B > S_A + SLACK
    NO_POWER  admitted and S_A == 0 (nothing to catch: cspfree is not taken further on this run)
    NOT_ADMITTED  any admission term fails''', '''(A = gates_free0.txt, cspfree=0; B = gates_free1.txt, cspfree=1), 150 s each, pinned.  Each dispatch-time stall
(a synchronous compute compile or a wait for a pending one) logs `CsStall: kind=new|wait us=<N> ...`; per entry D = sum
of us, M = the longest; D_A, D_B sum over each arm's entries, M_A, M_B the longest over them.
    PASS      admitted, A has >= 1 CsStall line (the positive control), D_B <= 1.25 * D_A + 20 000 us and
              M_B <= M_A + 10 000 us
    FAIL      admitted, the control holds, and either bound is exceeded
    NO_POWER  admitted and A has no CsStall line
    NOT_ADMITTED  any admission term fails (the ent109b terms plus STALL_SYNC: the CsStall lines of an entry equal
              its FrameTrace-x sum(cs_sync_new + cs_sync_wait), allowing one stall in flight at exit)'''),
    ("python C:/kyty/s109/ent109b.py", "python C:/kyty/s110/stl110.py"),
    ("ROOT = 'C:/kyty/s109'", "ROOT = 'C:/kyty/s110'"),
    ("PRED = 'C:/kyty/s109/pred/02_ent109b.md'", "PRED = 'C:/kyty/s110/pred/01_stl110.md'"),
    ("BINARY_SHA = '2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77'",
     "BINARY_SHA = 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82'"),
    ("TAGS = ['ent109b_%d' % (i + 1) for i in range(len(ORDER))]", "TAGS = ['stl110_%d' % (i + 1) for i in range(len(ORDER))]"),
    ("SLACK = 2\n", "D_FACTOR = 1.25\nD_SLACK_US = 20000\nM_SLACK_US = 10000\n"),
    ("""FIELDS = ('cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspfam_clr', 'cspf_new', 'cspfree_look',
          'cspfree_hit', 'cspfree_bad')""",
     """FIELDS = ('cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspfam_clr', 'cspf_new', 'cspfree_look',
          'cspfree_hit', 'cspfree_bad', 'cs_sync_new_us', 'cs_sync_wait_us')
STALL = re.compile(rb'^CsStall: kind=(new|wait) us=(\\d+) ')"""),
    ("""    pins = markers = rows = missing = 0
    queued = None""", """    pins = markers = rows = missing = 0
    stall_n = stall_d = stall_m = 0
    queued = None"""),
    ("""            if any(k in line.lower() for k in MARKERS):
                markers += 1""", """            if any(k in line.lower() for k in MARKERS):
                markers += 1
            m = STALL.match(line)
            if m:
                us = int(m.group(2))
                stall_n += 1
                stall_d += us
                stall_m = max(stall_m, us)"""),
    ("""    if arm == 'B' and (tot['cspfree_hit'] <= 0 or tot['cspfree_bad']):
        fails.append('ARM_B_ARMED')
    res = dict(tag=tag, arm=arm, rows=rows, launched=meta.get('launched'), fails=fails,
               s=tot['cs_sync_new'] + tot['cs_sync_wait'], **tot)""",
     """    if arm == 'B' and (tot['cspfree_hit'] <= 0 or tot['cspfree_bad']):
        fails.append('ARM_B_ARMED')
    s = tot['cs_sync_new'] + tot['cs_sync_wait']
    if not 0 <= s - stall_n <= 1:
        fails.append('STALL_SYNC')
    res = dict(tag=tag, arm=arm, rows=rows, launched=meta.get('launched'), fails=fails, s=s, stall_n=stall_n,
               d=stall_d, m=stall_m, **tot)"""),
    ("""    out = dict(scorer_sha256=sha_file(__file__), pred=PRED, pred_sha256=PRED_SHA, order=ORDER, slack=SLACK)""",
     """    out = dict(scorer_sha256=sha_file(__file__), pred=PRED, pred_sha256=PRED_SHA, order=ORDER, d_factor=D_FACTOR,
               d_slack_us=D_SLACK_US, m_slack_us=M_SLACK_US)"""),
    ("""    sa = sum(e.get('s', 0) for e in entries if e['arm'] == 'A')
    sb = sum(e.get('s', 0) for e in entries if e['arm'] == 'B')
    out['S_A'], out['S_B'] = sa, sb
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif sa == 0:
        out['verdict'] = 'NO_POWER'
    elif sb <= sa + SLACK:
        out['verdict'] = 'PASS'
    else:
        out['verdict'] = 'FAIL'
    return out""", """    sa = sum(e.get('s', 0) for e in entries if e['arm'] == 'A')
    sb = sum(e.get('s', 0) for e in entries if e['arm'] == 'B')
    na = sum(e.get('stall_n', 0) for e in entries if e['arm'] == 'A')
    da = sum(e.get('d', 0) for e in entries if e['arm'] == 'A')
    db = sum(e.get('d', 0) for e in entries if e['arm'] == 'B')
    ma = max([e.get('m', 0) for e in entries if e['arm'] == 'A'] or [0])
    mb = max([e.get('m', 0) for e in entries if e['arm'] == 'B'] or [0])
    out.update(S_A=sa, S_B=sb, N_A=na, D_A=da, D_B=db, M_A=ma, M_B=mb, D_BOUND=D_FACTOR * da + D_SLACK_US,
               M_BOUND=ma + M_SLACK_US)
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif na == 0:
        out['verdict'] = 'NO_POWER'
    elif db <= D_FACTOR * da + D_SLACK_US and mb <= ma + M_SLACK_US:
        out['verdict'] = 'PASS'
    else:
        out['verdict'] = 'FAIL'
    return out"""),
    ("""        print('  %-11s %s rows %6s  sync_new %4s  sync_wait %4s  S %4s  cspf_new %4s  free_look %8s  hit %8s  %s'
              % (e['tag'], e['arm'], e.get('rows'), e.get('cs_sync_new'), e.get('cs_sync_wait'), e.get('s'),
                 e.get('cspf_new'), e.get('cspfree_look'), e.get('cspfree_hit'), ','.join(e['fails']) or 'ok'))
    print('  S_A %d  S_B %d  slack %d  errors %s' % (res['S_A'], res['S_B'], SLACK, res['errors'] or 'none'))""",
     """        print('  %-10s %s rows %6s  new %3s wait %3s  lines %3s  D_us %8s  M_us %7s  cspf_new %4s  hit %8s  %s'
              % (e['tag'], e['arm'], e.get('rows'), e.get('cs_sync_new'), e.get('cs_sync_wait'), e.get('stall_n'),
                 e.get('d'), e.get('m'), e.get('cspf_new'), e.get('cspfree_hit'), ','.join(e['fails']) or 'ok'))
    print('  S_A %d S_B %d  N_A %d  D_A %d D_B %d (bound %.0f)  M_A %d M_B %d (bound %d)  errors %s'
          % (res['S_A'], res['S_B'], res['N_A'], res['D_A'], res['D_B'], res['D_BOUND'], res['M_A'], res['M_B'],
             res['M_BOUND'], res['errors'] or 'none'))"""),
    # session-109 audit survivors (AUDIT109 MINOR-5): every GpuClockPin line counts, and markers are read from the
    # entry's stdout file too (VEH prints there)
    ("""    pins = markers = rows = missing = 0
    stall_n""", """    pins = pin1 = markers = rows = missing = 0
    stall_n"""),
    ("""            if line.startswith(b'GpuClockPin: mode 1'):
                pins += 1""", """            if line.startswith(b'GpuClockPin:'):
                pins += 1
                pin1 += int(line.startswith(b'GpuClockPin: mode 1'))"""),
    ("""    if pins != 1:
        fails.append('PIN_ONCE')""", """    stdout_p = Path(root) / ('stdout_%s.txt' % tag)
    if stdout_p.is_file():
        with open(stdout_p, 'rb') as f:
            markers += sum(1 for line in f if any(k in line.lower() for k in MARKERS))
    if pins != 1 or pin1 != 1:
        fails.append('PIN_ONCE')"""),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
(STAGE / 'stl110.py').write_bytes(s.encode('utf-8'))
print('stl110.py', hashlib.sha256(s.encode('utf-8')).hexdigest())
