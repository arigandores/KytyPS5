"""Session 115, ROADMAP 0.1 "СЕССИЯ 115" item 2: check115.py / test_check115.py / mut_check115.py from session 114's
SEALED check114 files (sha pinned) by whole-line anchored replacements and whole-line delimited block replacements
(asserted).  Outputs to C:/kyty/s115.  New: the video vid115 (the build of the ring fix with titleasync default 1; the
BDA regime reported as the scene median of bda_scan) and three boot runs - boot115a (the fix, defaults), boot115b (the
positive control, KYTY_PREPARE_MAIN_PRESENT=1: the ring owner check must still fire) and boot115c (the fix with
KYTY_TITLE_ASYNC=1).  Byte-reproducible.

    python C:/kyty/s106_stage/make_check115.py <build sha256>
"""
import hashlib
import sys
from pathlib import Path

SRC_DIR = Path('C:/kyty/s114')
OUT = Path('C:/kyty/s115')
PINS = {'check114.py': '4c3d1875', 'test_check114.py': 'f45103d9', 'mut_check114.py': '3ec96c3a'}
OLD_SHA = '8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec'
NEW_SHA = sys.argv[1]
assert len(NEW_SHA) == 64 and all(c in '0123456789abcdef' for c in NEW_SHA), NEW_SHA


def load(name):
    s = (SRC_DIR / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def whole_line_index(s, line):
    assert line.endswith('\n'), line[:60]
    assert s.count(line) == 1, (line[:80], s.count(line))
    i = s.index(line)
    assert i == 0 or s[i - 1] == '\n', ('not at a line start', line[:80])
    return i


def derive(src, dst, pairs, blocks=()):
    s = load(src)
    for first, last, new in blocks:
        i = whole_line_index(s, first)
        j = whole_line_index(s, last)
        assert i <= j, (first[:60], last[:60])
        assert new.endswith('\n')
        s = s[:i] + new + s[j + len(last):]
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        whole_line_index(s, a)
        s = s.replace(a, b)
    (OUT / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


# ---------------------------------------------------------------- check115.py
DOC_HEAD = '''"""Session 115, ROADMAP §0.1 "СЕССИЯ 115" items 1-2 (seal pred/01_chk115.md): the video pass vid115 and three boot
runs of the build of the presentation-ring fix (no main-thread present during WindowPrepareShaders) with titleasync
default 1.  Derived from the sealed check114.py by make_check115.py; fixtures in test_check115.py, mutants in
mut_check115.py; committed and hashed in SEALS115 before its runs.
'''
DOC_BOOT = '''  Boot runs BOOT_TAGS, checks prefixed by the tag's last letter x (a, b, c), all with KYTY_PREPARE_HOLD_MS=HOLD_MS:
  x_binary / x_pinned / x_no_schedule / x_no_checkpoints / x_no_shift   as the video checks, on the boot run
  x_hold_env / x_hold_logged   env KYTY_PREPARE_HOLD_MS == HOLD_MS; exactly one line `PrepareHold: ms=HOLD_MS`
  x_default_runs           none of ` daslot=`, ` daguard=`, ` cspfree=`, ` bdanarrow=`, ` titleasync=` in its gates
  x_knob                   BOOT_SHIP: env KYTY_TITLE_ASYNC == '1'; the others: no KYTY_TITLE_ASYNC in env
  x_main_env               BOOT_CONTROL: env KYTY_PREPARE_MAIN_PRESENT == '1'; the others: none in env
  For BOOT_CONTROL every check above is admission (prefix adm_b_) and its pin is checked by env only (it dies before
  the guest reads the GPU clock, so the lazy `GpuClockPin:` line never prints - ROADMAP 115 item 5).
  The fix runs (all but BOOT_CONTROL):
  x_one_ok_attempt         one attempt, outcome ok, no hold_exit (the scene is reached after the hold)
  x_wait                   exactly one `ShaderPreparation: startup wait finished in N ms ...` line, N >= HOLD_MS
  x_presents_main          on that line presents_main=0 (the main thread never presented)
  x_presents_other         on that line presents_other >= PRESENTS_MIN (the present thread showed the overlay)
  x_no_main_line / x_no_fatal / x_no_overlap / x_no_marker   no `PrepareMainPresent:` line, no FATAL_SITE, no
                           `PresentOverlap:` anywhere in a line, no failure marker in the log or stdout
Admission (a failed adm_* check makes the verdict NOT_ADMITTED, not FAIL):
  adm_idle_vid / adm_idle_x   pre_run.gpu_util_median <= IDLE_GPU_MAX
  adm_b_main_logged / adm_b_fatal / adm_b_no_wait   the positive control BOOT_CONTROL: exactly one
                           `PrepareMainPresent: mode 1`, a line with FATAL_SITE after the hold line, no wait line
Reported, not checked: cs_sync_wait, da_guard_yield, prio_stall, prio_unsub; the row median of the UpdateTitle wall
per call; the scene median of bda_scan (the BDA regime: ~50 NEW, ~1 000+ OLD).

    python C:/kyty/s115/check115.py [--root C:/kyty/s115] [--out <json>]
'''
BOOT115 = '''def evaluate_boot(root, tag):
    """ROADMAP 115 item 2: BOOT_CONTROL is the positive control (KYTY_PREPARE_MAIN_PRESENT=1 - the old main-thread
    present must still trip the ring owner check); the other tags run the fix (BOOT_SHIP with KYTY_TITLE_ASYNC=1) and
    must finish the hold with the overlay presented by another thread only.  Checks: <last letter>_*, adm_*."""
    x = tag[-1]
    control = tag == BOOT_CONTROL
    p = 'adm_' + x if control else x
    bmeta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    benv = bmeta.get('env') or {}
    batts = bmeta.get('attempts') or []
    bok = [a for a in batts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    bgates = ' ' + ' '.join((bmeta.get('gates') or '').split()) + ' '
    bpin = []
    bholds = []
    bmains = []
    bwaits = []
    bmarkers = []
    bfatal_any = False
    bfatal_after_hold = False
    bov_lines = 0
    with open(Path(root) / ('log_%s.txt' % tag), 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin:'):
                bpin.append(line.startswith(b'GpuClockPin: mode 1'))
            if line.startswith(b'PrepareHold: '):
                bholds.append(line.decode('utf-8', 'replace').strip())
            if line.startswith(b'PrepareMainPresent: '):
                bmains.append(line.decode('utf-8', 'replace').strip())
            mw = WAIT.match(line)
            if mw:
                bwaits.append(tuple(None if g is None else int(g) for g in mw.groups()))
            if FATAL_SITE in line:
                bfatal_any = True
                bfatal_after_hold |= bool(bholds)
            if b'PresentOverlap:' in line:
                bov_lines += 1
            if is_marker(line):
                bmarkers.append(line[:200].decode('utf-8', 'replace').strip())
    bso = Path(root) / ('stdout_%s.txt' % tag)
    if bso.is_file():
        for line in open(bso, 'rb'):
            if is_marker(line):
                bmarkers.append(line[:200].decode('utf-8', 'replace').strip())
    knob = benv.get('KYTY_TITLE_ASYNC') == '1' if tag == BOOT_SHIP else 'KYTY_TITLE_ASYNC' not in benv
    main_env = benv.get('KYTY_PREPARE_MAIN_PRESENT') == '1' if control else 'KYTY_PREPARE_MAIN_PRESENT' not in benv
    checks = {p + '_binary': bmeta.get('binary_sha256') == BUILD_SHA,
              p + '_pinned': (bpin in ([], [True]) if control else bpin == [True])
                             and benv.get('KYTY_GPU_CLOCK_PIN') == '1',
              p + '_hold_env': benv.get('KYTY_PREPARE_HOLD_MS') == str(HOLD_MS),
              p + '_no_schedule': 'KYTY_GATE_SCHEDULE' not in benv,
              p + '_no_checkpoints': 'KYTY_GPU_CHECKPOINTS' not in benv,
              p + '_no_shift': 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB' not in benv,
              p + '_default_runs': all(' %s=' % k not in bgates for k in BOOT_DEFAULTS),
              p + '_hold_logged': bholds == ['PrepareHold: ms=%d' % HOLD_MS],
              p + '_knob': knob,
              p + '_main_env': main_env,
              'adm_idle_' + x: idle_ok(bmeta)}
    if control:
        checks.update({'adm_' + x + '_main_logged': bmains == ['PrepareMainPresent: mode 1'],
                       'adm_' + x + '_fatal': bfatal_after_hold,
                       'adm_' + x + '_no_wait': not bwaits})
    else:
        one = len(bwaits) == 1
        checks.update({x + '_one_ok_attempt': len(batts) == 1 and len(bok) == 1,
                       x + '_wait': one and bwaits[0][0] >= HOLD_MS,
                       x + '_presents_main': one and bwaits[0][2] == 0,
                       x + '_presents_other': one and bwaits[0][1] is not None and bwaits[0][1] >= PRESENTS_MIN,
                       x + '_no_main_line': not bmains,
                       x + '_no_fatal': not bfatal_any,
                       x + '_no_overlap': bov_lines == 0,
                       x + '_no_marker': not bmarkers})
    return dict(checks=checks, waits=bwaits, holds=bholds, mains=bmains, fatal_any=bfatal_any,
                fatal_after_hold=bfatal_after_hold, overlap_lines=bov_lines, markers=bmarkers[:10])


def evaluate_all(root=ROOT, installed_sha=None):
    """NOT_ADMITTED if any adm_* check fails; otherwise PASS iff every video check (TAG) and every boot check
    (BOOT_TAGS) holds, else FAIL (ROADMAP 115 item 2; the consequences are in pred/01_chk115.md)."""
    res = evaluate(root, installed_sha)
    res['boots'] = {}
    for tag in BOOT_TAGS:
        boot = evaluate_boot(root, tag)
        res['checks'].update(boot['checks'])
        res['boots'][tag] = boot
    res['admitted'] = all(v for k, v in res['checks'].items() if k.startswith('adm_'))
    if not res['admitted']:
        res['verdict'] = 'NOT_ADMITTED'
    else:
        res['verdict'] = 'PASS' if all(res['checks'].values()) else 'FAIL'
    return res
'''

derive('check114.py', 'check115.py', [
    ("  no_overlap               sum present_overlap == 0 over the scene rows and no `PresentOverlap:` line in the log\n",
     "  no_overlap               sum present_overlap == 0 over the scene rows and no `PresentOverlap:` line in the log\n"
     "  adm_idle_vid             pre_run.gpu_util_median <= IDLE_GPU_MAX (admission)\n"),
    ("ROOT = 'C:/kyty/s114'\n", "ROOT = 'C:/kyty/s115'\n"),
    ("TAG = 'vid114'\n", "TAG = 'vid115'\n"),
    ("BOOT_TAG = 'boot114'\n",
     "BOOT_TAGS = ('boot115a', 'boot115b', 'boot115c')\nBOOT_CONTROL = 'boot115b'\nBOOT_SHIP = 'boot115c'\n"),
    ("BUILD_SHA = '%s'\n" % OLD_SHA, "BUILD_SHA = '%s'\n" % NEW_SHA),
    ("PROG_MIN_LINES = 9\n", "PRESENTS_MIN = 300\n"),
    ("PROG_MIN_MS = 9000\n", "FATAL_SITE = b'commandRecorder.cpp:326'\n"),
    ("WAIT = re.compile(rb'^ShaderPreparation: startup wait finished in (\\d+) ms')\n",
     "WAIT = re.compile(rb'^ShaderPreparation: startup wait finished in (\\d+) ms(?: presents_other=(\\d+) presents_main=(\\d+))?')\n"),
    ("PROG = re.compile(rb'^ShaderPreparation: progress \\d+/\\d+ skipped=\\d+ elapsed_ms=(\\d+)')\n",
     "DRAW = re.compile(rb'^FrameTrace-draw: n=(\\d+)')\n"),
    ("LATE = re.compile(rb'^MainTaskLate: us=(\\d+)')\n", "BDA_SCAN = re.compile(rb' bda_scan=(\\d+)')\n"),
    ("    title_per_call = []\n", "    title_per_call = []\n    bda_scans = []\n"),
    ("            m = LINE.match(line)\n            if m and stable is not None and int(m.group(1)) >= stable:\n",
     "            md = DRAW.match(line)\n"
     "            if md and stable is not None and int(md.group(1)) >= stable:\n"
     "                mb = BDA_SCAN.search(line)\n"
     "                if mb:\n"
     "                    bda_scans.append(int(mb.group(1)))\n"
     "            m = LINE.match(line)\n            if m and stable is not None and int(m.group(1)) >= stable:\n"),
    ("               title_median_ns=sorted(title_per_call)[len(title_per_call) // 2] if title_per_call else None)\n",
     "               title_median_ns=sorted(title_per_call)[len(title_per_call) // 2] if title_per_call else None,\n"
     "               bda_scan_median=sorted(bda_scans)[len(bda_scans) // 2] if bda_scans else None)\n"),
], blocks=[
    ('"""Session 114, ROADMAP §0.1 "СЕССИЯ 114" items 9-11: the video pass vid114 and the boot run boot114 of the build\n',
     'in test_check114.py, mutants in mut_check114.py; committed and hashed in SEALS114 before its runs.\n', DOC_HEAD),
    ("  boot_binary / boot_pinned / boot_no_schedule / boot_no_checkpoints / boot_no_shift / boot_one_ok_attempt /\n",
     "    python C:/kyty/s114/check114.py [--root C:/kyty/s114] [--out <json>]\n", DOC_BOOT),
    ("def evaluate_boot(root=ROOT):\n", "        res['verdict'] = 'PASS' if all(res['checks'].values()) else 'FAIL'\n",
     BOOT115[:-len("    return res\n")]),
    ("PASS needs every check below (video TAG, then boot BOOT_TAG):\n",
     "PASS needs every check below (video TAG, then boot BOOT_TAG):\n",
     "PASS needs every check below (video TAG, then boot BOOT_TAGS):\n"),
])
assert BOOT115.endswith("    return res\n")

# ---------------------------------------------------------------- test_check115.py
BOOT_WRITER = '''def write_boot(d, tag, env=None, env_drop=(), atts=None, binary=None, pins=None,
               holds=('PrepareHold: ms=10000',), waits=None, mains=None, lines=None, stdout=None, gates=GATES,
               gpu_util=0.0):
    control = tag == mod.BOOT_CONTROL
    if pins is None:
        pins = () if control else ('GpuClockPin: mode 1',)
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_PREPARE_HOLD_MS': '10000'}
    if control:
        e['KYTY_PREPARE_MAIN_PRESENT'] = '1'
    if tag == mod.BOOT_SHIP:
        e['KYTY_TITLE_ASYNC'] = '1'
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    if atts is None:
        atts = [{'outcome': 'fail' if control else 'ok', 'hold_exit': None, 'stable_frame': 900}]
    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates, 'pre_run': {'gpu_util_median': gpu_util},
            'attempts': atts}
    (d / (tag + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    if waits is None:
        waits = () if control else ('ShaderPreparation: startup wait finished in 10016 ms presents_other=601 '
                                    'presents_main=0',)
    if mains is None:
        mains = ('PrepareMainPresent: mode 1',) if control else ()
    if lines is None:
        lines = ('--- Fatal Error ---', FATAL) if control else ('FrameTrace-x: n=1 present_overlap=0',)
    out = list(pins) + list(holds) + list(mains) + list(waits) + list(lines)
    (d / ('log_%s.txt' % tag)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % tag)).write_bytes((stdout + NL).encode('utf-8'))


def make(name, rows=3700, stable=280, frames=4000, glitches=0, gates=GATES, env=None, env_drop=(), atts=None,
'''

W = "ShaderPreparation: startup wait finished in %d ms presents_other=%d presents_main=%d"
BOOT_CASES = []
for x in ('a', 'c'):
    t = 'boot115' + x
    BOOT_CASES += [
        "('%s_binary', dict(boots={'%s': dict(binary='1' * 64)}), ['%s_binary'])," % (x, t, x),
        "('%s_pin_env', dict(boots={'%s': dict(env_drop=['KYTY_GPU_CLOCK_PIN'])}), ['%s_pinned'])," % (x, t, x),
        "('%s_pin_none', dict(boots={'%s': dict(pins=())}), ['%s_pinned'])," % (x, t, x),
        "('%s_pin_two', dict(boots={'%s': dict(pins=('GpuClockPin: mode 1',) * 2)}), ['%s_pinned'])," % (x, t, x),
        "('%s_pin_mode2', dict(boots={'%s': dict(pins=('GpuClockPin: mode 2',))}), ['%s_pinned'])," % (x, t, x),
        "('%s_hold_env_none', dict(boots={'%s': dict(env_drop=['KYTY_PREPARE_HOLD_MS'])}), ['%s_hold_env'])," % (x, t, x),
        "('%s_hold_env_5000', dict(boots={'%s': dict(env={'KYTY_PREPARE_HOLD_MS': '5000'})}), ['%s_hold_env'])," % (x, t, x),
        "('%s_schedule', dict(boots={'%s': dict(env={'KYTY_GATE_SCHEDULE': 'x'})}), ['%s_no_schedule'])," % (x, t, x),
        "('%s_checkpoints', dict(boots={'%s': dict(env={'KYTY_GPU_CHECKPOINTS': '0'})}), ['%s_no_checkpoints'])," % (x, t, x),
        "('%s_shift', dict(boots={'%s': dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'})}), ['%s_no_shift'])," % (x, t, x),
        "('%s_main_env', dict(boots={'%s': dict(env={'KYTY_PREPARE_MAIN_PRESENT': '1'})}), ['%s_main_env'])," % (x, t, x),
        "('%s_att_two', dict(boots={'%s': dict(atts=[{'outcome': 'ok', 'hold_exit': None}] * 2)}), ['%s_one_ok_attempt'])," % (x, t, x),
        "('%s_att_outcome', dict(boots={'%s': dict(atts=[{'outcome': 'hang', 'hold_exit': None}])}), ['%s_one_ok_attempt'])," % (x, t, x),
        "('%s_att_exit', dict(boots={'%s': dict(atts=[{'outcome': 'ok', 'hold_exit': 3}])}), ['%s_one_ok_attempt'])," % (x, t, x),
        "('%s_att_none', dict(boots={'%s': dict(atts=[])}), ['%s_one_ok_attempt'])," % (x, t, x),
        "('%s_att_extra', dict(boots={'%s': dict(atts=[{'outcome': 'hang', 'hold_exit': None}, {'outcome': 'ok', 'hold_exit': None}])}), ['%s_one_ok_attempt'])," % (x, t, x),
        "('%s_hold_none', dict(boots={'%s': dict(holds=())}), ['%s_hold_logged'])," % (x, t, x),
        "('%s_hold_two', dict(boots={'%s': dict(holds=('PrepareHold: ms=10000',) * 2)}), ['%s_hold_logged'])," % (x, t, x),
        "('%s_hold_5000', dict(boots={'%s': dict(holds=('PrepareHold: ms=5000',))}), ['%s_hold_logged'])," % (x, t, x),
        "('%s_wait_edge_fail', dict(boots={'%s': dict(waits=(W %% (9999, 601, 0),))}), ['%s_wait'])," % (x, t, x),
        "('%s_wait_edge_ok', dict(boots={'%s': dict(waits=(W %% (10000, 601, 0),))}), [])," % (x, t),
        "('%s_wait_none', dict(boots={'%s': dict(waits=())}), ['%s_presents_main', '%s_presents_other', '%s_wait'])," % (x, t, x, x, x),
        "('%s_wait_two', dict(boots={'%s': dict(waits=(W %% (10016, 601, 0),) * 2)}), ['%s_presents_main', '%s_presents_other', '%s_wait'])," % (x, t, x, x, x),
        "('%s_wait_old_format', dict(boots={'%s': dict(waits=('ShaderPreparation: startup wait finished in 10016 ms',))}), ['%s_presents_main', '%s_presents_other'])," % (x, t, x, x),
        "('%s_pmain_1', dict(boots={'%s': dict(waits=(W %% (10016, 601, 1),))}), ['%s_presents_main'])," % (x, t, x),
        "('%s_pother_edge_fail', dict(boots={'%s': dict(waits=(W %% (10016, 299, 0),))}), ['%s_presents_other'])," % (x, t, x),
        "('%s_pother_edge_ok', dict(boots={'%s': dict(waits=(W %% (10016, 300, 0),))}), [])," % (x, t),
        "('%s_main_line', dict(boots={'%s': dict(mains=('PrepareMainPresent: mode 1',))}), ['%s_no_main_line'])," % (x, t, x),
        "('%s_fatal', dict(boots={'%s': dict(lines=(FATAL,))}), ['%s_no_fatal'])," % (x, t, x),
        "('%s_overlap', dict(boots={'%s': dict(lines=('PresentOverlap: thread=1',))}), ['%s_no_overlap'])," % (x, t, x),
        "('%s_overlap_midline', dict(boots={'%s': dict(lines=('[7] x PresentOverlap: thread=1',))}), ['%s_no_overlap'])," % (x, t, x),
        "('%s_marker_log', dict(boots={'%s': dict(lines=('GpuHangAbort: role=4',))}), ['%s_no_marker'])," % (x, t, x),
        "('%s_marker_stdout', dict(boots={'%s': dict(stdout='Unhandled exception: 0xC0000005')}), ['%s_no_marker'])," % (x, t, x),
        "('%s_stdout_clean', dict(boots={'%s': dict(stdout='0xe06d7363 C++ exception (not a marker)')}), [])," % (x, t),
        "('%s_idle', dict(boots={'%s': dict(gpu_util=10.5)}), ['adm_idle_%s'])," % (x, t, x),
        "('%s_idle_edge', dict(boots={'%s': dict(gpu_util=10)}), [])," % (x, t),
    ]
    for k in ('daslot', 'daguard', 'cspfree', 'bdanarrow', 'titleasync'):
        BOOT_CASES.append("('%s_gate_%s', dict(boots={'%s': dict(gates=GATES + ' %s=1')}), ['%s_default_runs'])," % (x, k, t, k, x))
BOOT_CASES += [
    "('a_knob_env', dict(boots={'boot115a': dict(env={'KYTY_TITLE_ASYNC': '1'})}), ['a_knob']),",
    "('c_knob_missing', dict(boots={'boot115c': dict(env_drop=['KYTY_TITLE_ASYNC'])}), ['c_knob']),",
    "('c_knob_0', dict(boots={'boot115c': dict(env={'KYTY_TITLE_ASYNC': '0'})}), ['c_knob']),",
    "('b_binary', dict(boots={'boot115b': dict(binary='1' * 64)}), ['adm_b_binary']),",
    "('b_pin_none', dict(boots={'boot115b': dict(pins=())}), []),",
    "('b_pin_line', dict(boots={'boot115b': dict(pins=('GpuClockPin: mode 1',))}), []),",
    "('b_pin_mode2', dict(boots={'boot115b': dict(pins=('GpuClockPin: mode 2',))}), ['adm_b_pinned']),",
    "('b_pin_two', dict(boots={'boot115b': dict(pins=('GpuClockPin: mode 1',) * 2)}), ['adm_b_pinned']),",
    "('b_hold_5000', dict(boots={'boot115b': dict(holds=('PrepareHold: ms=5000',))}), ['adm_b_hold_logged']),",
    "('b_real_shape', dict(boots={'boot115b': dict(pins=(), lines=('--- Build ---', 'Fork build x', '--- Fatal Error ---', FATAL))}), []),",
    "('b_pin_env', dict(boots={'boot115b': dict(env_drop=['KYTY_GPU_CLOCK_PIN'])}), ['adm_b_pinned']),",
    "('b_hold_env', dict(boots={'boot115b': dict(env_drop=['KYTY_PREPARE_HOLD_MS'])}), ['adm_b_hold_env']),",
    "('b_schedule', dict(boots={'boot115b': dict(env={'KYTY_GATE_SCHEDULE': 'x'})}), ['adm_b_no_schedule']),",
    "('b_checkpoints', dict(boots={'boot115b': dict(env={'KYTY_GPU_CHECKPOINTS': '0'})}), ['adm_b_no_checkpoints']),",
    "('b_shift', dict(boots={'boot115b': dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'})}), ['adm_b_no_shift']),",
    "('b_gate', dict(boots={'boot115b': dict(gates=GATES + ' titleasync=1')}), ['adm_b_default_runs']),",
    "('b_hold_none', dict(boots={'boot115b': dict(holds=())}), ['adm_b_fatal', 'adm_b_hold_logged']),",
    "('b_knob_env', dict(boots={'boot115b': dict(env={'KYTY_TITLE_ASYNC': '1'})}), ['adm_b_knob']),",
    "('b_main_env_missing', dict(boots={'boot115b': dict(env_drop=['KYTY_PREPARE_MAIN_PRESENT'])}), ['adm_b_main_env']),",
    "('b_main_env_2', dict(boots={'boot115b': dict(env={'KYTY_PREPARE_MAIN_PRESENT': '2'})}), ['adm_b_main_env']),",
    "('b_main_missing', dict(boots={'boot115b': dict(mains=())}), ['adm_b_main_logged']),",
    "('b_main_two', dict(boots={'boot115b': dict(mains=('PrepareMainPresent: mode 1',) * 2)}), ['adm_b_main_logged']),",
    "('b_no_fatal', dict(boots={'boot115b': dict(lines=('--- Fatal Error ---', 'Error: other.cpp:1'))}), ['adm_b_fatal']),",
    "('b_fatal_midline', dict(boots={'boot115b': dict(lines=('[3] x ' + FATAL,))}), []),",
    "('b_waited', dict(boots={'boot115b': dict(waits=(W % (10016, 601, 3),))}), ['adm_b_no_wait']),",
    "('b_idle', dict(boots={'boot115b': dict(gpu_util=11)}), ['adm_idle_b']),",
    "('b_markers_allowed', dict(boots={'boot115b': dict(stdout='--- Fatal Error ---')}), []),",
    "('b_att_ignored', dict(boots={'boot115b': dict(atts=[])}), []),",
    "('a_and_vid_fail', dict(glitches=1, boots={'boot115a': dict(waits=(W % (70, 5, 0),))}), ['a_presents_other', 'a_wait', 'no_glitch']),",
    "('adm_and_fail', dict(glitches=1, boots={'boot115b': dict(mains=())}), ['adm_b_main_logged', 'no_glitch']),",
]
# the fatal-before-hold case: the control's fatal must follow the hold line
BOOT_CASES.append("('b_fatal_before_hold', dict(boots={'boot115b': dict(holds=(), lines=(FATAL, 'PrepareHold: ms=10000'))}), ['adm_b_fatal'])," )
CASES_BLOCK = ''.join('    %s\n' % c for c in BOOT_CASES)
VID_KEEP = '''    ('marker_waitslow', dict(lines=['GpuWaitSlow: tick=5 us=900000']), ['no_marker']),
    ('marker_devlost', dict(lines=['vkQueueSubmit: ErrorDeviceLost']), ['no_marker']),
    ('marker_terminate', dict(lines=['--- std::terminate ---']), ['no_marker']),
    ('marker_abort', dict(lines=['--- abort() ---']), ['no_marker']),
    ('marker_error', dict(lines=['--- Error ---']), ['no_marker']),
    ('marker_hung', dict(lines=['GpuMarkerHung: cs=1']), ['no_marker']),
    ('marker_ckpt', dict(lines=['GpuCheckpointHang: op=1']), ['no_marker']),
    ('overlap_midline', dict(lines=['[7][00:00:01.000] x PresentOverlap: thread=1']), ['no_overlap']),
    ('adm_idle_vid', dict(vid_gpu=10.5), ['adm_idle_vid']),
    ('adm_idle_vid_edge', dict(vid_gpu=10), []),
    ('adm_idle_vid_none', dict(vid_gpu=None), ['adm_idle_vid']),
'''

derive('test_check114.py', 'test_check115.py', [
    ('"""Session 114: fixtures for check114.py (from test_check113.py by make_check114.py) - PASS, every check failing\n',
     '"""Session 115: fixtures for check115.py (from the sealed test_check114.py by make_check115.py) - PASS, every check\n'),
    ("alone (video and boot), and both sides of every threshold.\n",
     "failing alone (video, the fix boots a/c, the control b), and both sides of every threshold.\n"),
    ("    python test_check114.py <check114.py>\n", "    python test_check115.py <check115.py>\n"),
    ("BASE = Path('C:/kyty/s106_stage/fx_check114')\n", "BASE = Path('C:/kyty/s106_stage/fx_check115')\n"),
    ("spec = importlib.util.spec_from_file_location('check114', SRC)\n",
     "spec = importlib.util.spec_from_file_location('check115', SRC)\n"),
    ("GC_OK = 'BufferGc: budget=14901313536 trigger=9747352781 critical=13183326618 shift_mb=0'\n",
     "GC_OK = 'BufferGc: budget=14901313536 trigger=9747352781 critical=13183326618 shift_mb=0'\n"
     "FATAL = 'Error: condition (m_producer != self || m_open_slot != nullptr) is true in C:\\\\kyty\\\\x\\\\commandRecorder.cpp:326'\n"
     "W = '%s'\n" % W),
    ("         gc=(GC_OK,), title_ns=22000, title_n=1, overlap=0, drop_title=False, boot=None, vid_gpu=0.0):\n",
     "         gc=(GC_OK,), title_ns=22000, title_n=1, overlap=0, drop_title=False, boots=None, vid_gpu=0.0):\n"),
    ("    write_boot(d, **(boot or {}))\n",
     "    for tag in mod.BOOT_TAGS:\n        write_boot(d, tag, **((boots or {}).get(tag) or {}))\n"),
    ("CONSTANTS = dict(TAG='vid114', BOOT_TAG='boot114', MIN_FRAMES=3000, MIN_ROWS=1000, TITLE_WALL_MAX_NS=60000,\n",
     "CONSTANTS = dict(TAG='vid115', BOOT_TAGS=('boot115a', 'boot115b', 'boot115c'), BOOT_CONTROL='boot115b',\n"
     "                 BOOT_SHIP='boot115c', MIN_FRAMES=3000, MIN_ROWS=1000, TITLE_WALL_MAX_NS=60000,\n"),
    ("                 IDLE_GPU_MAX=10, PROG_MIN_LINES=9, PROG_MIN_MS=9000,\n",
     "                 IDLE_GPU_MAX=10, PRESENTS_MIN=300, FATAL_SITE=b'commandRecorder.cpp:326',\n"),
    ("                 BUILD_SHA='%s')\n" % OLD_SHA, "                 BUILD_SHA='%s')\n" % NEW_SHA),
    ("    print('%-20s want %-40s got %-40s %s' % (name, want, got, 'OK' if passed else 'FAIL'))\n",
     "    print('%-24s want %-40s got %-40s %s' % (name, want, got, 'OK' if passed else 'FAIL'))\n"),
], blocks=[
    ("def write_boot(d, rows=3000, env=None, env_drop=(), atts=None, binary=None, pins=('GpuClockPin: mode 1',),\n",
     "def make(name, rows=3700, stable=280, frames=4000, glitches=0, gates=GATES, env=None, env_drop=(), atts=None,\n",
     BOOT_WRITER),
    ("    ('boot_binary', dict(boot=dict(binary='1' * 64)), ['boot_binary']),\n",
     "    ('adm_and_fail', dict(glitches=1, boot=dict(park=())), ['adm_boot_parked', 'no_glitch']),\n",
     VID_KEEP + CASES_BLOCK),
])

# ---------------------------------------------------------------- mut_check115.py
Q = '"'
MUTS = [
    ('all_merge', "res['checks'].update(boot['checks'])", 'pass'),
    ('all_verdict', "res['verdict'] = 'PASS' if all(res['checks'].values()) else 'FAIL'", "res['verdict'] = res['verdict']"),
    ('vid_binary', "binary=meta.get('binary_sha256') == BUILD_SHA,", 'binary=True,'),
    ('vid_ok_exit', "ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]",
     "ok_att = [a for a in atts if a.get('outcome') == 'ok']"),
    ('ov_mid', "if line.find(b'PresentOverlap:') >= 0:", "if line.startswith(b'PresentOverlap:'):"),
    ('adm_idle_vid', 'adm_idle_vid=idle_ok(meta))', 'adm_idle_vid=True)'),
    ('idle_max', 'IDLE_GPU_MAX = 10', 'IDLE_GPU_MAX = 11'),
    ('idle_le', 'v <= IDLE_GPU_MAX', 'v < IDLE_GPU_MAX'),
    ('idle_type', 'isinstance(v, (int, float)) and ', ''),
    ('hold_ms', 'HOLD_MS = 10000', 'HOLD_MS = 9999'),
    ('adm_verdict', "    if not res['admitted']:", '    if False:'),
    ('adm_filter', "k.startswith('adm_')", "k.startswith('adm_x')"),
    ('bt_tags', "BOOT_TAGS = ('boot115a', 'boot115b', 'boot115c')", "BOOT_TAGS = ('boot115a', 'boot115b')"),
    ('bt_control_tag', "BOOT_CONTROL = 'boot115b'", "BOOT_CONTROL = 'boot115a'"),
    ('bt_ship_tag', "BOOT_SHIP = 'boot115c'", "BOOT_SHIP = 'boot115a'"),
    ('bt_control', 'control = tag == BOOT_CONTROL', 'control = tag == BOOT_SHIP'),
    ('bt_binary', "p + '_binary': bmeta.get('binary_sha256') == BUILD_SHA,", "p + '_binary': True,"),
    ('bt_pin_list', 'else bpin == [True]', 'else True in bpin'),
    ('bt_ctl_pin', 'bpin in ([], [True])', 'bpin == [True]'),
    ('bt_ctl_pin_any', 'bpin in ([], [True])', 'True'),
    ('bt_ctl_prefix', "p = 'adm_' + x if control else x", 'p = x'),
    ('bt_pin_mode', "bpin.append(line.startswith(b'GpuClockPin: mode 1'))", 'bpin.append(True)'),
    ('bt_pin_env', " and benv.get('KYTY_GPU_CLOCK_PIN') == '1',", ','),
    ('bt_hold_env', "p + '_hold_env': benv.get('KYTY_PREPARE_HOLD_MS') == str(HOLD_MS),", "p + '_hold_env': True,"),
    ('bt_sched', "p + '_no_schedule': 'KYTY_GATE_SCHEDULE' not in benv,", "p + '_no_schedule': True,"),
    ('bt_ckpt', "p + '_no_checkpoints': 'KYTY_GPU_CHECKPOINTS' not in benv,", "p + '_no_checkpoints': True,"),
    ('bt_shift', "p + '_no_shift': 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB' not in benv,", "p + '_no_shift': True,"),
    ('bt_defaults', "p + '_default_runs': all(' %s=' % k not in bgates for k in BOOT_DEFAULTS),", "p + '_default_runs': True,"),
    ('bt_def_daslot', "('daslot', 'daguard',", "('daguard',"),
    ('bt_def_daguard', "'daslot', 'daguard', 'cspfree'", "'daslot', 'cspfree'"),
    ('bt_def_cspfree', "'daguard', 'cspfree', 'bdanarrow'", "'daguard', 'bdanarrow'"),
    ('bt_def_bdanarrow', "'cspfree', 'bdanarrow', 'titleasync'", "'cspfree', 'titleasync'"),
    ('bt_def_titleasync', "'bdanarrow', 'titleasync')", "'bdanarrow')"),
    ('bt_hold_line', "bholds == ['PrepareHold: ms=%d' % HOLD_MS]", 'len(bholds) == 1'),
    ('bt_hold_collect', "bholds.append(line.decode('utf-8', 'replace').strip())", 'pass'),
    ('bt_knob_ship', "benv.get('KYTY_TITLE_ASYNC') == '1' if tag == BOOT_SHIP", 'True if tag == BOOT_SHIP'),
    ('bt_knob_other', "else 'KYTY_TITLE_ASYNC' not in benv", 'else True'),
    ('bt_main_ctl', "benv.get('KYTY_PREPARE_MAIN_PRESENT') == '1' if control", 'True if control'),
    ('bt_main_fix', "else 'KYTY_PREPARE_MAIN_PRESENT' not in benv", 'else True'),
    ('bt_idle', "'adm_idle_' + x: idle_ok(bmeta)}", "'adm_idle_' + x: True}"),
    ('bt_ctl_main', "bmains == ['PrepareMainPresent: mode 1']", 'True'),
    ('bt_ctl_main_collect', "bmains.append(line.decode('utf-8', 'replace').strip())", 'pass'),
    ('bt_ctl_fatal', "'adm_' + x + '_fatal': bfatal_after_hold,", "'adm_' + x + '_fatal': True,"),
    ('bt_ctl_nowait', "'adm_' + x + '_no_wait': not bwaits}", "'adm_' + x + '_no_wait': True}"),
    ('bt_fatal_after', 'bfatal_after_hold |= bool(bholds)', 'bfatal_after_hold |= True'),
    ('bt_fatal_mid', 'if FATAL_SITE in line:', 'if line.startswith(FATAL_SITE):'),
    ('bt_fatal_site', "FATAL_SITE = b'commandRecorder.cpp:326'", "FATAL_SITE = b'commandRecorder.cpp:999'"),
    ('bt_att_len', 'len(batts) == 1 and ', ''),
    ('bt_att_ok', ' and len(bok) == 1,', ','),
    ('bt_att_exit', "bok = [a for a in batts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]",
     "bok = [a for a in batts if a.get('outcome') == 'ok']"),
    ('bt_one', 'one = len(bwaits) == 1', 'one = len(bwaits) >= 1'),
    ('bt_wait_gt', 'bwaits[0][0] >= HOLD_MS', 'bwaits[0][0] > HOLD_MS'),
    ('bt_wait_any', 'bwaits[0][0] >= HOLD_MS', 'bwaits[0][0] >= 0'),
    ('bt_pmain', 'bwaits[0][2] == 0', 'bwaits[0][2] is not None'),
    ('bt_pmain_le', 'bwaits[0][2] == 0', 'bwaits[0][2] <= 1'),
    ('bt_pother_gt', 'bwaits[0][1] >= PRESENTS_MIN', 'bwaits[0][1] > PRESENTS_MIN'),
    ('bt_pother_c', 'PRESENTS_MIN = 300', 'PRESENTS_MIN = 299'),
    ('bt_pother_none', 'bwaits[0][1] is not None and ', ''),
    ('bt_no_main_line', "x + '_no_main_line': not bmains,", "x + '_no_main_line': True,"),
    ('bt_no_fatal', "x + '_no_fatal': not bfatal_any,", "x + '_no_fatal': True,"),
    ('bt_no_overlap', "x + '_no_overlap': bov_lines == 0,", "x + '_no_overlap': True,"),
    ('bt_ov_mid', "if b'PresentOverlap:' in line:", "if line.startswith(b'PresentOverlap:'):"),
    ('bt_no_marker', "x + '_no_marker': not bmarkers}", "x + '_no_marker': True}"),
    ('bt_stdout', '    if bso.is_file():', '    if False:'),
]


def mline(m):
    name, old, new = m
    return '    (%r, %r, %r),\n' % (name, old, new)


MUT_BLOCK = ''.join(mline(m) for m in MUTS)
derive('mut_check114.py', 'mut_check115.py', [
    ('"""Session 114: mutants of check114.py (from mut_check113.py by make_check114.py) - each must be killed by\n',
     '"""Session 115: mutants of check115.py (from the sealed mut_check114.py by make_check115.py) - each must be killed by\n'),
    ('test_check114.py; run through mutlib v2 (frozen copy) --control --no-memo on the sealed copy."""\n',
     'test_check115.py; run through mutlib v2 (frozen copy) --control --no-memo on the sealed copy."""\n'),
    ("SRC = Path('C:/kyty/s114/check114.py').read_text(encoding='utf-8')\n",
     "SRC = Path('C:/kyty/s115/check115.py').read_text(encoding='utf-8')\n"),
    ("    path = STAGE / ('mut_check114_%s.py' % name)\n", "    path = STAGE / ('mut_check115_%s.py' % name)\n"),
    ("    r = subprocess.run([sys.executable, 'C:/kyty/s114/test_check114.py', str(path)], capture_output=True, text=True)\n",
     "    r = subprocess.run([sys.executable, 'C:/kyty/s115/test_check115.py', str(path)], capture_output=True, text=True)\n"),
], blocks=[
    ("    ('b_binary', \"boot_binary=bmeta.get('binary_sha256') == BUILD_SHA,\", 'boot_binary=True,'),\n",
     "    ('adm_filter', \"k.startswith('adm_')\", \"k.startswith('adm_x')\"),\n", MUT_BLOCK),
])
