"""Session 114, ROADMAP 0.1 "СЕССИЯ 114" items 9-11: check114.py / test_check114.py / mut_check114.py from session
113's check113 files (sha pinned) by WHOLE-LINE anchored replacements (asserted).  Outputs to C:/kyty/s114.  New: the
build 8d7ba8f4 (titleasync default 1, KYTY_PREPARE_HOLD_MS, the PresentOverlap detector); the video vid114 also needs
`titleasync` absent from the gate text, no KYTY_PREPARE_HOLD_MS in env, the UpdateTitle wall per call over the scene
<= 60 us (the default is armed) and no present overlap; the boot run boot114 (KYTY_PREPARE_HOLD_MS=10000) needs one
admitted attempt, one `PrepareHold: ms=10000` line, one `startup wait finished in N ms` line with N >= 10 000 and no
present overlap.  PASS needs both.  Byte-reproducible.

    python C:/kyty/s106_stage/make_check114.py
"""
import hashlib
from pathlib import Path

SRC_DIR = Path('C:/kyty/s113')
OUT = Path('C:/kyty/s114')
PINS = {'check113.py': '2120ed5a', 'test_check113.py': 'f8415d98', 'mut_check113.py': '7cccc6fb'}
OLD_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'
NEW_SHA = '8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec'


def load(name):
    s = (SRC_DIR / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def derive(src, dst, pairs):
    s = load(src)
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        assert s.startswith(a) or ('\n' + a) in s, (src, 'anchor not at a line start', a[:80])
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    (OUT / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


BOOT_FN = '''def evaluate_boot(root=ROOT):
    """The boot run BOOT_TAG (ROADMAP items 10, 11): the preparation screen held >= HOLD_MS by the main thread while
    the VideoOut present thread is alive (the guest starts only after it), default titleasync=1.  Checks: boot_*."""
    bmeta = json.loads((Path(root) / (BOOT_TAG + '.json')).read_text(encoding='utf-8'))
    benv = bmeta.get('env') or {}
    batts = bmeta.get('attempts') or []
    bok = [a for a in batts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    bgates = ' ' + ' '.join((bmeta.get('gates') or '').split()) + ' '
    bpin = []
    bholds = []
    bwaits = []
    bprog = []
    bpark = None
    bmarkers = []
    brows = bmissing = bov_lines = bov_sum = rows_before_wait = 0
    with open(Path(root) / ('log_%s.txt' % BOOT_TAG), 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin:'):
                bpin.append(line.startswith(b'GpuClockPin: mode 1'))
            if line.startswith(b'PrepareHold: '):
                bholds.append(line.decode('utf-8', 'replace').strip())
            mw = WAIT.match(line)
            if mw:
                bwaits.append(int(mw.group(1)))
            mp = PROG.match(line)
            if mp:
                bprog.append(int(mp.group(1)))
            ml = LATE.match(line)
            if ml and bwaits and bpark is None:
                bpark = int(ml.group(1))
            if b'PresentOverlap:' in line:
                bov_lines += 1
            if is_marker(line):
                bmarkers.append(line[:200].decode('utf-8', 'replace').strip())
            m = LINE.match(line)
            if m:
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                brows += 1
                rows_before_wait += int(not bwaits)
                bmissing += int('present_overlap' not in d)
                bov_sum += d.get('present_overlap', 0)
    bso = Path(root) / ('stdout_%s.txt' % BOOT_TAG)
    if bso.is_file():
        for line in open(bso, 'rb'):
            if is_marker(line):
                bmarkers.append(line[:200].decode('utf-8', 'replace').strip())
    checks = dict(boot_binary=bmeta.get('binary_sha256') == BUILD_SHA,
                  boot_pinned=bpin == [True] and benv.get('KYTY_GPU_CLOCK_PIN') == '1',
                  boot_hold_env=benv.get('KYTY_PREPARE_HOLD_MS') == str(HOLD_MS),
                  boot_no_schedule='KYTY_GATE_SCHEDULE' not in benv,
                  boot_no_checkpoints='KYTY_GPU_CHECKPOINTS' not in benv,
                  boot_no_shift='KYTY_BUFFER_GC_TRIGGER_SHIFT_MB' not in benv,
                  boot_one_ok_attempt=len(batts) == 1 and len(bok) == 1,
                  boot_default_runs=all(' %s=' % k not in bgates for k in BOOT_DEFAULTS),
                  boot_hold_logged=bholds == ['PrepareHold: ms=%d' % HOLD_MS],
                  boot_wait=len(bwaits) == 1 and bwaits[0] >= HOLD_MS,
                  boot_rows=brows >= MIN_ROWS and bmissing == 0,
                  boot_no_overlap=bov_lines == 0 and bov_sum == 0,
                  boot_no_marker=not bmarkers,
                  adm_idle_boot=idle_ok(bmeta),
                  adm_boot_parked=(bpark is not None and bpark >= HOLD_MS * 1000
                                   and len(bprog) >= PROG_MIN_LINES and max(bprog) >= PROG_MIN_MS))
    res = dict(checks=checks, waits_ms=bwaits, holds=bholds, rows=brows, rows_before_wait=rows_before_wait,
               overlap_lines=bov_lines, overlap_sum=bov_sum, markers=bmarkers[:10], park_us=bpark,
               progress_ms=bprog)
    res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    return res


def evaluate_all(root=ROOT, installed_sha=None):
    """NOT_ADMITTED if any adm_* check fails (ROADMAP item 12); otherwise PASS iff every video check (TAG) and every
    boot check (BOOT_TAG) holds, else FAIL."""
    res = evaluate(root, installed_sha)
    boot = evaluate_boot(root)
    res['checks'].update(boot['checks'])
    res['boot'] = boot
    res['admitted'] = all(v for k, v in res['checks'].items() if k.startswith('adm_'))
    if not res['admitted']:
        res['verdict'] = 'NOT_ADMITTED'
    else:
        res['verdict'] = 'PASS' if all(res['checks'].values()) else 'FAIL'
    return res


def main():
'''

derive('check113.py', 'check114.py', [
    ('"""Session 113, ROADMAP §0.1 "СЕССИЯ 113" item 21: the video pass of the build 1678d3f4 (knob `bdanarrow`, default 0;\n'
     'the env KYTY_BUFFER_GC_TRIGGER_SHIFT_MB, default 0; the exact knob-2 check; the priority-stall instrument) with\n'
     "today's defaults (`daslot=1 daguard=1 cspfree=1 bdanarrow=0`).  Derived from check112.py by make_check113.py.\n"
     "Written fresh (session 111's check111.py had a stale docstring and no fixtures - audit MINOR-3); fixtures in\n"
     'test_check112.py; committed and hashed in SEALS112 before its run.\n',
     '"""Session 114, ROADMAP §0.1 "СЕССИЯ 114" items 9-11: the video pass vid114 and the boot run boot114 of the build\n'
     '8d7ba8f4 (knob `titleasync`, default 1; KYTY_PREPARE_HOLD_MS; the PresentOverlap detector) with today\'s defaults\n'
     '(`daslot=1 daguard=1 cspfree=1 bdanarrow=0 titleasync=1`).  Derived from check113.py by make_check114.py; fixtures\n'
     'in test_check114.py, mutants in mut_check114.py; committed and hashed in SEALS114 before its runs.\n'),
    ("PASS needs every check below:\n",
     "PASS needs every check below (video TAG, then boot BOOT_TAG):\n"),
    ("  binary / installed_now   vid112.json binary and the installed exe are BUILD_SHA\n",
     "  binary / installed_now   TAG.json binary and the installed exe are BUILD_SHA\n"),
    ("  gc_default               exactly one `BufferGc:` line, ending in shift_mb=0\n",
     "  gc_default               exactly one `BufferGc:` line, ending in shift_mb=0\n"
     "  no_title_knob            no ` titleasync=` in the gate text (the default 1 runs)\n"
     "  no_hold                  no KYTY_PREPARE_HOLD_MS in env\n"
     "  title_default_on         sum pres_title_n > 0 and sum pres_title_ns <= TITLE_WALL_MAX_NS * sum pres_title_n over\n"
     "                           the scene rows (UpdateTitle posts without waiting for the main thread)\n"
     "  no_overlap               sum present_overlap == 0 over the scene rows and no `PresentOverlap:` line in the log\n"
     "  boot_binary / boot_pinned / boot_no_schedule / boot_no_checkpoints / boot_no_shift / boot_one_ok_attempt /\n"
     "  boot_no_marker           as the video checks, on BOOT_TAG (its env, attempts, log, stdout)\n"
     "  boot_hold_env            env KYTY_PREPARE_HOLD_MS == HOLD_MS\n"
     "  boot_default_runs        none of ` daslot=`, ` daguard=`, ` cspfree=`, ` bdanarrow=`, ` titleasync=` in its gates\n"
     "  boot_hold_logged         exactly one line `PrepareHold: ms=HOLD_MS`\n"
     "  boot_wait                exactly one `ShaderPreparation: startup wait finished in N ms` line, N >= HOLD_MS\n"
     "  boot_rows                >= MIN_ROWS FrameTrace-x rows (all of them), every one carrying present_overlap\n"
     "  boot_no_overlap          no `PresentOverlap:` line and sum present_overlap == 0 over all its rows\n"
     "Admission (ROADMAP item 12; a failed adm_* check makes the verdict NOT_ADMITTED, not FAIL):\n"
     "  adm_idle_vid / adm_idle_boot   pre_run.gpu_util_median <= IDLE_GPU_MAX in TAG.json / BOOT_TAG.json\n"
     "  adm_boot_parked          the first `MainTaskLate: us=X` after the wait line has X >= HOLD_MS * 1000 (the present\n"
     "                           thread's title task parked through the hold) and >= PROG_MIN_LINES `ShaderPreparation:\n"
     "                           progress` lines reach elapsed_ms >= PROG_MIN_MS (the main thread presented throughout)\n"
     "Limit (audit M1): present_overlap is counted only from the guest's first flip on, so the `PresentOverlap:` line is\n"
     "the only detector of the boot window.\n"),
    ("Reported, not checked: cs_sync_wait, da_guard_yield, prio_stall, prio_unsub.\n",
     "Reported, not checked: cs_sync_wait, da_guard_yield, prio_stall, prio_unsub; the boot rows before the wait line;\n"
     "the row median of the UpdateTitle wall per call.\n"),
    ("    python C:/kyty/s113/check113.py [--root C:/kyty/s113] [--out <json>]\n",
     "    python C:/kyty/s114/check114.py [--root C:/kyty/s114] [--out <json>]\n"),
    ("ROOT = 'C:/kyty/s113'\n", "ROOT = 'C:/kyty/s114'\n"),
    ("TAG = 'vid113'\n", "TAG = 'vid114'\nBOOT_TAG = 'boot114'\n"),
    ("BUILD_SHA = '%s'\n" % OLD_SHA, "BUILD_SHA = '%s'\n" % NEW_SHA),
    ("MIN_ROWS = 1000\n",
     "MIN_ROWS = 1000\nTITLE_WALL_MAX_NS = 60000\nHOLD_MS = 10000\n"
     "BOOT_DEFAULTS = ('daslot', 'daguard', 'cspfree', 'bdanarrow', 'titleasync')\n"
     "IDLE_GPU_MAX = 10\nPROG_MIN_LINES = 9\nPROG_MIN_MS = 9000\n"),
    ("          'da_guard_yield', 'bda_nskip', 'bda_nwould', 'prio_stall', 'prio_unsub')\n",
     "          'da_guard_yield', 'bda_nskip', 'bda_nwould', 'prio_stall', 'prio_unsub', 'pres_title_ns', 'pres_title_n',\n"
     "          'present_overlap')\n"),
    ("FIELD = re.compile(rb' (\\w+)=(-?\\d+)')\n",
     "FIELD = re.compile(rb' (\\w+)=(-?\\d+)')\n"
     "WAIT = re.compile(rb'^ShaderPreparation: startup wait finished in (\\d+) ms')\n"
     "PROG = re.compile(rb'^ShaderPreparation: progress \\d+/\\d+ skipped=\\d+ elapsed_ms=(\\d+)')\n"
     "LATE = re.compile(rb'^MainTaskLate: us=(\\d+)')\n"),
    ("    gc_lines = []\n", "    gc_lines = []\n    overlap_lines = 0\n    title_per_call = []\n"),
    ("            if line.startswith(b'BufferGc: '):\n",
     "            if line.find(b'PresentOverlap:') >= 0:\n"
     "                overlap_lines += 1\n"
     "            if line.startswith(b'BufferGc: '):\n"),
    ("                    tot[k] += d.get(k, 0)\n",
     "                    tot[k] += d.get(k, 0)\n"
     "                if d.get('pres_title_n', 0) > 0:\n"
     "                    title_per_call.append(d['pres_title_ns'] / d['pres_title_n'])\n"),
    ("                  gc_default=len(gc_lines) == 1 and gc_lines[0].endswith(' shift_mb=0'))\n",
     "                  gc_default=len(gc_lines) == 1 and gc_lines[0].endswith(' shift_mb=0'),\n"
     "                  no_title_knob=' titleasync=' not in gates,\n"
     "                  no_hold='KYTY_PREPARE_HOLD_MS' not in env,\n"
     "                  title_default_on=(tot['pres_title_n'] > 0\n"
     "                                    and tot['pres_title_ns'] <= TITLE_WALL_MAX_NS * tot['pres_title_n']),\n"
     "                  no_overlap=tot['present_overlap'] == 0 and overlap_lines == 0,\n"
     "                  adm_idle_vid=idle_ok(meta))\n"),
    ("               markers=markers[:10], stable_frame=stable, gc_lines=gc_lines)\n",
     "               markers=markers[:10], stable_frame=stable, gc_lines=gc_lines, overlap_lines=overlap_lines,\n"
     "               title_median_ns=sorted(title_per_call)[len(title_per_call) // 2] if title_per_call else None)\n"),
    ("    return any(k in low for k in MARKERS)\n",
     "    return any(k in low for k in MARKERS)\n\n\ndef idle_ok(meta):\n"
     "    v = (meta.get('pre_run') or {}).get('gpu_util_median')\n"
     "    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX\n"),
    ("def main():\n", BOOT_FN),
    ("    res = evaluate(root)\n", "    res = evaluate_all(root)\n"),
    ("    print(json.dumps(res, indent=1))\n", "    print(json.dumps(res, indent=1))\n    print('VERDICT: %s' % res['verdict'])\n"),
])

BOOT_WRITER = '''def write_boot(d, rows=3000, env=None, env_drop=(), atts=None, binary=None, pins=('GpuClockPin: mode 1',),
               holds=('PrepareHold: ms=10000',), waits=(10240,), lines=(), stdout=None, gates=GATES, overlap=0,
               drop_field=False, gpu_util=0.0, progress=tuple(range(0, 10001, 1000)), park=(10200000,),
               park_before=False):
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_PREPARE_HOLD_MS': '10000'}
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates, 'pre_run': {'gpu_util_median': gpu_util},
            'attempts': atts if atts is not None else [{'outcome': 'ok', 'hold_exit': None, 'stable_frame': 900}]}
    (d / (mod.BOOT_TAG + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    late = ['MainTaskLate: us=%d' % x for x in park]
    out = list(pins) + list(holds) + (late if park_before else [])
    out += ['ShaderPreparation: progress 682/682 skipped=41 elapsed_ms=%d' % ms for ms in progress]
    out += ['ShaderPreparation: startup wait finished in %d ms' % w for w in waits]
    out += ([] if park_before else late) + list(lines)
    for n in range(1, rows + 1):
        f = 'pres_title_n=1 present_overlap=%d' % (overlap if n == 40 else 0)
        if drop_field and n == 50:
            f = f.replace('present_overlap=', 'present_overlaX=')
        out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, f))
    (d / ('log_%s.txt' % mod.BOOT_TAG)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % mod.BOOT_TAG)).write_bytes((stdout + NL).encode('utf-8'))


def make(name, rows=3700, stable=280, frames=4000, glitches=0, gates=GATES, env=None, env_drop=(), atts=None,
'''

derive('test_check113.py', 'test_check114.py', [
    ('"""Session 113: fixtures for check113.py (from test_check112.py by make_check113.py) - PASS, every check failing\n'
     'alone, and both sides of every threshold.\n'
     '    python test_check113.py <check113.py>\n',
     '"""Session 114: fixtures for check114.py (from test_check113.py by make_check114.py) - PASS, every check failing\n'
     'alone (video and boot), and both sides of every threshold.\n'
     '    python test_check114.py <check114.py>\n'),
    ("BASE = Path('C:/kyty/s106_stage/fx_check113')\n", "BASE = Path('C:/kyty/s106_stage/fx_check114')\n"),
    ("spec = importlib.util.spec_from_file_location('check113', SRC)\n",
     "spec = importlib.util.spec_from_file_location('check114', SRC)\n"),
    ("    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates,\n",
     "    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates, 'pre_run': {'gpu_util_median': vid_gpu},\n"),
    ("def make(name, rows=3700, stable=280, frames=4000, glitches=0, gates=GATES, env=None, env_drop=(), atts=None,\n",
     BOOT_WRITER),
    ("         gc=(GC_OK,)):\n",
     "         gc=(GC_OK,), title_ns=22000, title_n=1, overlap=0, drop_title=False, boot=None, vid_gpu=0.0):\n"),
    ("    passed = got == sorted(want) and res['verdict'] == ('PASS' if not want else 'FAIL')\n",
     "    expect = 'PASS' if not want else ('NOT_ADMITTED' if any(w.startswith('adm_') for w in want) else 'FAIL')\n"
     "    passed = got == sorted(want) and res['verdict'] == expect\n"),
    ("                                                                       would if n == stable + 15 else 0)\n",
     "                                                                       would if n == stable + 15 else 0)\n"
     "        f += ' pres_title_ns=%d pres_title_n=%d present_overlap=%d' % (title_ns, title_n,\n"
     "                                                                       overlap if n == stable + 17 else 0)\n"),
    ("            f = f.replace('da_q_noguard=', 'da_q_noguarX=')\n",
     "            f = f.replace('da_q_noguard=', 'da_q_noguarX=')\n"
     "        if drop_title and n == stable + 21:\n"
     "            f = f.replace('pres_title_n=', 'pres_title_X=')\n"),
    ("    return mod.evaluate(str(d), installed_sha=installed or mod.BUILD_SHA)\n",
     "    write_boot(d, **(boot or {}))\n"
     "    return mod.evaluate_all(str(d), installed_sha=installed or mod.BUILD_SHA)\n"),
    ("     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed']),   # no scene rows at all\n",
     "     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed', 'title_default_on']),   # no scene rows\n"),
    ("     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed']),\n",
     "     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed', 'title_default_on']),\n"),
    ("    ('marker_stdout', dict(stdout='Unhandled exception: 0xC0000005'), ['no_marker']),\n",
     "    ('marker_stdout', dict(stdout='Unhandled exception: 0xC0000005'), ['no_marker']),\n"
     "    ('gate_titleasync', dict(gates=GATES + ' titleasync=1'), ['no_title_knob']),\n"
     "    ('gate_titleasync0', dict(gates=GATES + ' titleasync=0'), ['no_title_knob']),\n"
     "    ('hold_env', dict(env={'KYTY_PREPARE_HOLD_MS': '10000'}), ['no_hold']),\n"
     "    ('title_zero', dict(title_n=0, title_ns=0), ['title_default_on']),\n"
     "    ('title_edge_ok', dict(title_ns=60000), []),\n"
     "    ('title_edge_fail', dict(title_ns=60001), ['title_default_on']),\n"
     "    ('title_wait', dict(title_ns=168468), ['title_default_on']),\n"
     "    ('title_field', dict(drop_title=True), ['rows']),\n"
     "    ('overlap_row', dict(overlap=1), ['no_overlap']),\n"
     "    ('overlap_line', dict(lines=['PresentOverlap: thread=12345']), ['no_overlap']),\n"
     "    ('boot_binary', dict(boot=dict(binary='1' * 64)), ['boot_binary']),\n"
     "    ('boot_pin_env', dict(boot=dict(env_drop=['KYTY_GPU_CLOCK_PIN'])), ['boot_pinned']),\n"
     "    ('boot_pin_none', dict(boot=dict(pins=())), ['boot_pinned']),\n"
     "    ('boot_pin_two', dict(boot=dict(pins=('GpuClockPin: mode 1', 'GpuClockPin: mode 1'))), ['boot_pinned']),\n"
     "    ('boot_pin_mode2', dict(boot=dict(pins=('GpuClockPin: mode 2',))), ['boot_pinned']),\n"
     "    ('boot_hold_env_none', dict(boot=dict(env_drop=['KYTY_PREPARE_HOLD_MS'])), ['boot_hold_env']),\n"
     "    ('boot_hold_env_5000', dict(boot=dict(env={'KYTY_PREPARE_HOLD_MS': '5000'})), ['boot_hold_env']),\n"
     "    ('boot_schedule', dict(boot=dict(env={'KYTY_GATE_SCHEDULE': 'x'})), ['boot_no_schedule']),\n"
     "    ('boot_checkpoints', dict(boot=dict(env={'KYTY_GPU_CHECKPOINTS': '0'})), ['boot_no_checkpoints']),\n"
     "    ('boot_shift', dict(boot=dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'})), ['boot_no_shift']),\n"
     "    ('boot_att_two', dict(boot=dict(atts=[{'outcome': 'ok', 'hold_exit': None}] * 2)), ['boot_one_ok_attempt']),\n"
     "    ('boot_att_outcome', dict(boot=dict(atts=[{'outcome': 'hang', 'hold_exit': None}])), ['boot_one_ok_attempt']),\n"
     "    ('boot_att_exit', dict(boot=dict(atts=[{'outcome': 'ok', 'hold_exit': 3}])), ['boot_one_ok_attempt']),\n"
     "    ('boot_att_none', dict(boot=dict(atts=[])), ['boot_one_ok_attempt']),\n"
     "    ('boot_att_extra_failed', dict(boot=dict(atts=[{'outcome': 'hang', 'hold_exit': None},"
     "                                                  {'outcome': 'ok', 'hold_exit': None}])), ['boot_one_ok_attempt']),\n"
     "    ('boot_gate_daslot', dict(boot=dict(gates=GATES + ' daslot=1')), ['boot_default_runs']),\n"
     "    ('boot_gate_daguard', dict(boot=dict(gates=GATES + ' daguard=1')), ['boot_default_runs']),\n"
     "    ('boot_gate_cspfree', dict(boot=dict(gates=GATES + ' cspfree=1')), ['boot_default_runs']),\n"
     "    ('boot_gate_bdanarrow', dict(boot=dict(gates=GATES + ' bdanarrow=0')), ['boot_default_runs']),\n"
     "    ('boot_gate_titleasync', dict(boot=dict(gates=GATES + ' titleasync=1')), ['boot_default_runs']),\n"
     "    ('boot_hold_none', dict(boot=dict(holds=())), ['boot_hold_logged']),\n"
     "    ('boot_hold_two', dict(boot=dict(holds=('PrepareHold: ms=10000',) * 2)), ['boot_hold_logged']),\n"
     "    ('boot_hold_5000', dict(boot=dict(holds=('PrepareHold: ms=5000',))), ['boot_hold_logged']),\n"
     "    ('boot_wait_edge_fail', dict(boot=dict(waits=(9999,))), ['boot_wait']),\n"
     "    ('boot_wait_edge_ok', dict(boot=dict(waits=(10000,))), []),\n"
     "    ('boot_wait_warm', dict(boot=dict(waits=(70,))), ['boot_wait']),\n"
     "    ('boot_wait_none', dict(boot=dict(waits=())), ['adm_boot_parked', 'boot_wait']),\n"
     "    ('boot_wait_two', dict(boot=dict(waits=(10240, 10240))), ['boot_wait']),\n"
     "    ('boot_rows_edge_fail', dict(boot=dict(rows=999)), ['boot_rows']),\n"
     "    ('boot_rows_edge_ok', dict(boot=dict(rows=1000)), []),\n"
     "    ('boot_rows_field', dict(boot=dict(drop_field=True)), ['boot_rows']),\n"
     "    ('boot_overlap_line', dict(boot=dict(lines=['PresentOverlap: thread=12345'])), ['boot_no_overlap']),\n"
     "    ('boot_overlap_sum', dict(boot=dict(overlap=1)), ['boot_no_overlap']),\n"
     "    ('boot_marker_log', dict(boot=dict(lines=['GpuHangAbort: role=4'])), ['boot_no_marker']),\n"
     "    ('boot_marker_stdout', dict(boot=dict(stdout='Unhandled exception: 0xC0000005')), ['boot_no_marker']),\n"
     "    ('boot_stdout_clean', dict(boot=dict(stdout='0xe06d7363 C++ exception (not a marker)')), []),\n"
     "    ('both_fail', dict(glitches=1, boot=dict(waits=(70,))), ['boot_wait', 'no_glitch']),\n"
     "    ('marker_waitslow', dict(lines=['GpuWaitSlow: tick=5 us=900000']), ['no_marker']),\n"
     "    ('marker_devlost', dict(lines=['vkQueueSubmit: ErrorDeviceLost']), ['no_marker']),\n"
     "    ('marker_terminate', dict(lines=['--- std::terminate ---']), ['no_marker']),\n"
     "    ('marker_abort', dict(lines=['--- abort() ---']), ['no_marker']),\n"
     "    ('marker_error', dict(lines=['--- Error ---']), ['no_marker']),\n"
     "    ('marker_hung', dict(lines=['GpuMarkerHung: cs=1']), ['no_marker']),\n"
     "    ('marker_ckpt', dict(lines=['GpuCheckpointHang: op=1']), ['no_marker']),\n"
     "    ('overlap_midline', dict(lines=['[7][00:00:01.000] x PresentOverlap: thread=1']), ['no_overlap']),\n"
     "    ('boot_overlap_midline', dict(boot=dict(lines=['[7] x PresentOverlap: thread=1'])), ['boot_no_overlap']),\n"
     "    ('boot_marker_terminate', dict(boot=dict(lines=['--- std::terminate ---'])), ['boot_no_marker']),\n"
     "    ('adm_idle_vid', dict(vid_gpu=10.5), ['adm_idle_vid']),\n"
     "    ('adm_idle_vid_edge', dict(vid_gpu=10), []),\n"
     "    ('adm_idle_vid_none', dict(vid_gpu=None), ['adm_idle_vid']),\n"
     "    ('adm_idle_boot', dict(boot=dict(gpu_util=11)), ['adm_idle_boot']),\n"
     "    ('adm_idle_boot_edge', dict(boot=dict(gpu_util=10.0)), []),\n"
     "    ('adm_park_short', dict(boot=dict(park=(9999999,))), ['adm_boot_parked']),\n"
     "    ('adm_park_edge', dict(boot=dict(park=(10000000,))), []),\n"
     "    ('adm_park_none', dict(boot=dict(park=())), ['adm_boot_parked']),\n"
     "    ('adm_park_before_wait', dict(boot=dict(park_before=True)), ['adm_boot_parked']),\n"
     "    ('adm_park_first_only', dict(boot=dict(park=(300000, 10200000))), ['adm_boot_parked']),\n"
     "    ('adm_park_later_long', dict(boot=dict(park=(10200000, 300000))), []),\n"
     "    ('adm_prog_count', dict(boot=dict(progress=(0, 9000))), ['adm_boot_parked']),\n"
     "    ('adm_prog_count_edge', dict(boot=dict(progress=tuple(range(1000, 9001, 1000)))), []),\n"
     "    ('adm_prog_ms', dict(boot=dict(progress=tuple(range(0, 8001, 800)))), ['adm_boot_parked']),\n"
     "    ('adm_prog_ms_edge', dict(boot=dict(progress=tuple(range(0, 9001, 900)))), []),\n"
     "    ('adm_and_fail', dict(glitches=1, boot=dict(park=())), ['adm_boot_parked', 'no_glitch']),\n"),
    ("CONSTANTS = dict(TAG='vid113', MIN_FRAMES=3000, MIN_ROWS=1000,\n",
     "CONSTANTS = dict(TAG='vid114', BOOT_TAG='boot114', MIN_FRAMES=3000, MIN_ROWS=1000, TITLE_WALL_MAX_NS=60000,\n"
     "                 HOLD_MS=10000, BOOT_DEFAULTS=('daslot', 'daguard', 'cspfree', 'bdanarrow', 'titleasync'),\n"
     "                 IDLE_GPU_MAX=10, PROG_MIN_LINES=9, PROG_MIN_MS=9000,\n"),
    ("                 BUILD_SHA='%s')\n" % OLD_SHA, "                 BUILD_SHA='%s')\n" % NEW_SHA),
])

derive('mut_check113.py', 'mut_check114.py', [
    ('"""Session 113: mutants of check113.py (from mut_check112.py by make_check113.py) - each must be killed by\n'
     'test_check113.py; run through mutlib v2 --control --no-memo on the sealed copy."""\n',
     '"""Session 114: mutants of check114.py (from mut_check113.py by make_check114.py) - each must be killed by\n'
     'test_check114.py; run through mutlib v2 (frozen copy) --control --no-memo on the sealed copy."""\n'),
    ("SRC = Path('C:/kyty/s113/check113.py').read_text(encoding='utf-8')\n",
     "SRC = Path('C:/kyty/s114/check114.py').read_text(encoding='utf-8')\n"),
    ("    ('gc_collect', \"gc_lines.append(line[:200].decode('utf-8', 'replace').strip())\", 'pass'),\n",
     "    ('gc_collect', \"gc_lines.append(line[:200].decode('utf-8', 'replace').strip())\", 'pass'),\n"
     "    ('title_knob', \"no_title_knob=' titleasync=' not in gates,\", 'no_title_knob=True,'),\n"
     "    ('no_hold', \"no_hold='KYTY_PREPARE_HOLD_MS' not in env,\", 'no_hold=True,'),\n"
     "    ('title_n', \"(tot['pres_title_n'] > 0\", '(True'),\n"
     "    ('title_cap', 'TITLE_WALL_MAX_NS = 60000', 'TITLE_WALL_MAX_NS = 60001'),\n"
     "    ('title_cap_lt', \"<= TITLE_WALL_MAX_NS * tot['pres_title_n']\", \"< TITLE_WALL_MAX_NS * tot['pres_title_n']\"),\n"
     "    ('title_wall', \"and tot['pres_title_ns'] <= TITLE_WALL_MAX_NS * tot['pres_title_n']),\", 'and True),'),\n"
     "    ('ov_sum', \"tot['present_overlap'] == 0 and \", ''),\n"
     "    ('ov_lines', \" and overlap_lines == 0,\", ','),\n"
     "    ('ov_collect', '                overlap_lines += 1', '                overlap_lines += 0'),\n"
     "    ('b_binary', \"boot_binary=bmeta.get('binary_sha256') == BUILD_SHA,\", 'boot_binary=True,'),\n"
     "    ('b_pin_list', 'bpin == [True]', 'True in bpin'),\n"
     "    ('b_pin_mode', \"bpin.append(line.startswith(b'GpuClockPin: mode 1'))\", 'bpin.append(True)'),\n"
     "    ('b_pin_env', \" and benv.get('KYTY_GPU_CLOCK_PIN') == '1',\", ','),\n"
     "    ('b_hold_env', \"boot_hold_env=benv.get('KYTY_PREPARE_HOLD_MS') == str(HOLD_MS),\", 'boot_hold_env=True,'),\n"
     "    ('b_sched', \"boot_no_schedule='KYTY_GATE_SCHEDULE' not in benv,\", 'boot_no_schedule=True,'),\n"
     "    ('b_ckpt', \"boot_no_checkpoints='KYTY_GPU_CHECKPOINTS' not in benv,\", 'boot_no_checkpoints=True,'),\n"
     "    ('b_shift', \"boot_no_shift='KYTY_BUFFER_GC_TRIGGER_SHIFT_MB' not in benv,\", 'boot_no_shift=True,'),\n"
     "    ('b_att_len', 'len(batts) == 1 and ', ''),\n"
     "    ('b_att_ok', ' and len(bok) == 1,', ','),\n"
     "    ('b_att_exit', \"bok = [a for a in batts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]\",\n"
     "     \"bok = [a for a in batts if a.get('outcome') == 'ok']\"),\n"
     "    ('b_def_daslot', \"('daslot', 'daguard',\", \"('daguard',\"),\n"
     "    ('b_def_daguard', \"'daslot', 'daguard', 'cspfree'\", \"'daslot', 'cspfree'\"),\n"
     "    ('b_def_cspfree', \"'daguard', 'cspfree', 'bdanarrow'\", \"'daguard', 'bdanarrow'\"),\n"
     "    ('b_def_bdanarrow', \"'cspfree', 'bdanarrow', 'titleasync'\", \"'cspfree', 'titleasync'\"),\n"
     "    ('b_def_titleasync', \"'bdanarrow', 'titleasync')\", \"'bdanarrow')\"),\n"
     "    ('b_def_all', \"boot_default_runs=all(' %s=' % k not in bgates for k in BOOT_DEFAULTS),\",\n"
     "     'boot_default_runs=True,'),\n"
     "    ('b_hold_line', \"bholds == ['PrepareHold: ms=%d' % HOLD_MS]\", 'len(bholds) == 1'),\n"
     "    ('b_hold_collect', \"bholds.append(line.decode('utf-8', 'replace').strip())\", 'pass'),\n"
     "    ('hold_ms', 'HOLD_MS = 10000', 'HOLD_MS = 9999'),\n"
     "    ('b_wait_count', 'len(bwaits) == 1 and ', ''),\n"
     "    ('b_wait_gt', 'bwaits[0] >= HOLD_MS', 'bwaits[0] > HOLD_MS'),\n"
     "    ('b_wait_any', 'bwaits[0] >= HOLD_MS', 'bwaits[0] >= 0'),\n"
     "    ('b_rows', 'brows >= MIN_ROWS and ', ''),\n"
     "    ('b_rows_missing', ' and bmissing == 0,', ','),\n"
     "    ('b_ov_lines', 'bov_lines == 0 and ', ''),\n"
     "    ('b_ov_sum', ' and bov_sum == 0,', ','),\n"
     "    ('b_ov_collect', '                bov_lines += 1', '                bov_lines += 0'),\n"
     "    ('b_marker', 'boot_no_marker=not bmarkers,', 'boot_no_marker=True,'),\n"
     "    ('b_stdout', '    if bso.is_file():', '    if False:'),\n"
     "    ('all_merge', \"res['checks'].update(boot['checks'])\", 'pass'),\n"
     "    ('all_verdict', \"res['verdict'] = 'PASS' if all(res['checks'].values()) else 'FAIL'\",\n"
     "     \"res['verdict'] = res['verdict']\"),\n"
     "    ('vid_binary', \"binary=meta.get('binary_sha256') == BUILD_SHA,\", 'binary=True,'),\n"
     "    ('vid_ok_exit', \"ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]\",\n"
     "     \"ok_att = [a for a in atts if a.get('outcome') == 'ok']\"),\n"
     "    ('ov_mid', \"if line.find(b'PresentOverlap:') >= 0:\", \"if line.startswith(b'PresentOverlap:'):\"),\n"
     "    ('b_ov_mid', \"if b'PresentOverlap:' in line:\", \"if line.startswith(b'PresentOverlap:'):\"),\n"
     "    ('adm_idle_vid', 'adm_idle_vid=idle_ok(meta))', 'adm_idle_vid=True)'),\n"
     "    ('adm_idle_boot', 'adm_idle_boot=idle_ok(bmeta),', 'adm_idle_boot=True,'),\n"
     "    ('idle_max', 'IDLE_GPU_MAX = 10', 'IDLE_GPU_MAX = 11'),\n"
     "    ('idle_le', 'v <= IDLE_GPU_MAX', 'v < IDLE_GPU_MAX'),\n"
     "    ('idle_type', 'isinstance(v, (int, float)) and ', ''),\n"
     "    ('park_min', 'bpark >= HOLD_MS * 1000', 'bpark >= HOLD_MS * 999'),\n"
     "    ('park_gt', 'bpark >= HOLD_MS * 1000', 'bpark > HOLD_MS * 1000'),\n"
     "    ('park_none', 'bpark is not None and ', ''),\n"
     "    ('park_after_wait', 'if ml and bwaits and bpark is None:', 'if ml and bpark is None:'),\n"
     "    ('park_first', 'if ml and bwaits and bpark is None:', 'if ml and bwaits:'),\n"
     "    ('prog_lines', 'len(bprog) >= PROG_MIN_LINES', 'len(bprog) >= 1'),\n"
     "    ('prog_lines_c', 'PROG_MIN_LINES = 9', 'PROG_MIN_LINES = 10'),\n"
     "    ('prog_ms', 'max(bprog) >= PROG_MIN_MS', 'max(bprog) >= 0'),\n"
     "    ('prog_ms_c', 'PROG_MIN_MS = 9000', 'PROG_MIN_MS = 9001'),\n"
     "    ('prog_collect', 'bprog.append(int(mp.group(1)))', 'bprog.append(99999)'),\n"
     "    ('adm_verdict', \"    if not res['admitted']:\", '    if False:'),\n"
     "    ('adm_filter', \"k.startswith('adm_')\", \"k.startswith('adm_x')\"),\n"),
    ("    ('gc_shift', \" and gc_lines[0].endswith(' shift_mb=0'))\", ')'),\n",
     "    ('gc_shift', \" and gc_lines[0].endswith(' shift_mb=0'),\", ','),\n"),
    ("    path = STAGE / ('mut_check113_%s.py' % name)\n", "    path = STAGE / ('mut_check114_%s.py' % name)\n"),
    ("    r = subprocess.run([sys.executable, 'C:/kyty/s113/test_check113.py', str(path)], capture_output=True, text=True)\n",
     "    r = subprocess.run([sys.executable, 'C:/kyty/s114/test_check114.py', str(path)], capture_output=True, text=True)\n"),
])
