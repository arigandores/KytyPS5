"""Session 114, ROADMAP §0.1 "СЕССИЯ 114" items 9-11: the video pass vid114 and the boot run boot114 of the build
8d7ba8f4 (knob `titleasync`, default 1; KYTY_PREPARE_HOLD_MS; the PresentOverlap detector) with today's defaults
(`daslot=1 daguard=1 cspfree=1 bdanarrow=0 titleasync=1`).  Derived from check113.py by make_check114.py; fixtures
in test_check114.py, mutants in mut_check114.py; committed and hashed in SEALS114 before its runs.

PASS needs every check below (video TAG, then boot BOOT_TAG):
  binary / installed_now   TAG.json binary and the installed exe are BUILD_SHA
  pinned                   env KYTY_GPU_CLOCK_PIN=1 and exactly one `GpuClockPin:` line, and it is mode 1
  recorded                 env KYTY_REC set
  no_schedule              no KYTY_GATE_SCHEDULE in env
  no_checkpoints           no KYTY_GPU_CHECKPOINTS in env
  one_ok_attempt           one attempt, outcome ok, no hold_exit
  default_runs             none of ` daslot=`, ` daguard=`, ` cspfree=`, ` bdanarrow=` in the gate text (defaults)
  no_shift                 no KYTY_BUFFER_GC_TRIGGER_SHIFT_MB in env (the buffer-GC trigger as shipped)
  frames                   >= 3 000 video frames;  no_glitch: 0 one-frame glitches
  rows                     >= 1 000 FrameTrace-x rows from the stable frame on, every one carrying the 8 fields
  slot_default_armed       sum da_q_free > 0 (daslot != 0) and sum da_q_noguard == 0 (daguard=1 or daslot != 0)
  slot_no_bad              sum da_slot_bad == 0 (daslot=1 never verifies: non-zero means a wrong knob or build)
  free_default_armed       sum cspfree_hit > 0 and sum cspfree_bad == 0
  guard                    sum cs_sync_new == 0 over the scene rows
  no_marker                no failure marker in the log or stdout
  narrow_default_dark      sum bda_nskip == 0 and sum bda_nwould == 0 (bdanarrow=0: no skip, no check)
  gc_default               exactly one `BufferGc:` line, ending in shift_mb=0
  no_title_knob            no ` titleasync=` in the gate text (the default 1 runs)
  no_hold                  no KYTY_PREPARE_HOLD_MS in env
  title_default_on         sum pres_title_n > 0 and sum pres_title_ns <= TITLE_WALL_MAX_NS * sum pres_title_n over
                           the scene rows (UpdateTitle posts without waiting for the main thread)
  no_overlap               sum present_overlap == 0 over the scene rows and no `PresentOverlap:` line in the log
  boot_binary / boot_pinned / boot_no_schedule / boot_no_checkpoints / boot_no_shift / boot_one_ok_attempt /
  boot_no_marker           as the video checks, on BOOT_TAG (its env, attempts, log, stdout)
  boot_hold_env            env KYTY_PREPARE_HOLD_MS == HOLD_MS
  boot_default_runs        none of ` daslot=`, ` daguard=`, ` cspfree=`, ` bdanarrow=`, ` titleasync=` in its gates
  boot_hold_logged         exactly one line `PrepareHold: ms=HOLD_MS`
  boot_wait                exactly one `ShaderPreparation: startup wait finished in N ms` line, N >= HOLD_MS
  boot_rows                >= MIN_ROWS FrameTrace-x rows (all of them), every one carrying present_overlap
  boot_no_overlap          no `PresentOverlap:` line and sum present_overlap == 0 over all its rows
Admission (ROADMAP item 12; a failed adm_* check makes the verdict NOT_ADMITTED, not FAIL):
  adm_idle_vid / adm_idle_boot   pre_run.gpu_util_median <= IDLE_GPU_MAX in TAG.json / BOOT_TAG.json
  adm_boot_parked          the first `MainTaskLate: us=X` after the wait line has X >= HOLD_MS * 1000 (the present
                           thread's title task parked through the hold) and >= PROG_MIN_LINES `ShaderPreparation:
                           progress` lines reach elapsed_ms >= PROG_MIN_MS (the main thread presented throughout)
Limit (audit M1): present_overlap is counted only from the guest's first flip on, so the `PresentOverlap:` line is
the only detector of the boot window.
Reported, not checked: cs_sync_wait, da_guard_yield, prio_stall, prio_unsub; the boot rows before the wait line;
the row median of the UpdateTitle wall per call.

    python C:/kyty/s114/check114.py [--root C:/kyty/s114] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s114'
TAG = 'vid114'
BOOT_TAG = 'boot114'
BUILD_SHA = '8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
MIN_FRAMES = 3000
MIN_ROWS = 1000
TITLE_WALL_MAX_NS = 60000
HOLD_MS = 10000
BOOT_DEFAULTS = ('daslot', 'daguard', 'cspfree', 'bdanarrow', 'titleasync')
IDLE_GPU_MAX = 10
PROG_MIN_LINES = 9
PROG_MIN_MS = 9000
FIELDS = ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait', 'da_q_free', 'da_q_noguard', 'da_slot_bad',
          'da_guard_yield', 'bda_nskip', 'bda_nwould', 'prio_stall', 'prio_unsub', 'pres_title_ns', 'pres_title_n',
          'present_overlap')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
LINE = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
WAIT = re.compile(rb'^ShaderPreparation: startup wait finished in (\d+) ms')
PROG = re.compile(rb'^ShaderPreparation: progress \d+/\d+ skipped=\d+ elapsed_ms=(\d+)')
LATE = re.compile(rb'^MainTaskLate: us=(\d+)')


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def idle_ok(meta):
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX


def evaluate(root=ROOT, installed_sha=None):
    res = dict(check_sha256=sha_file(__file__), build_sha256=BUILD_SHA)
    meta = json.loads((Path(root) / (TAG + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    atts = meta.get('attempts') or []
    ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    stable = ok_att[-1].get('stable_frame', 0) if ok_att else None
    gates = ' ' + ' '.join((meta.get('gates') or '').split()) + ' '
    text = (Path(root) / (TAG + '_glitch.txt')).read_text(encoding='utf-8', errors='replace')
    mf = re.search(r'(\d+) frames', text)
    mg = re.search(r'one-frame glitches:\s*(\d+)', text)
    tot = {k: 0 for k in FIELDS}
    rows = missing = pins = pin1 = 0
    gc_lines = []
    overlap_lines = 0
    title_per_call = []
    markers = []
    with open(Path(root) / ('log_%s.txt' % TAG), 'rb') as f:
        for line in f:
            if line.find(b'PresentOverlap:') >= 0:
                overlap_lines += 1
            if line.startswith(b'BufferGc: '):
                gc_lines.append(line[:200].decode('utf-8', 'replace').strip())
            if line.startswith(b'GpuClockPin:'):
                pins += 1
                pin1 += int(line.startswith(b'GpuClockPin: mode 1'))
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            m = LINE.match(line)
            if m and stable is not None and int(m.group(1)) >= stable:
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                rows += 1
                missing += int(any(k not in d for k in FIELDS))
                for k in FIELDS:
                    tot[k] += d.get(k, 0)
                if d.get('pres_title_n', 0) > 0:
                    title_per_call.append(d['pres_title_ns'] / d['pres_title_n'])
    so = Path(root) / ('stdout_%s.txt' % TAG)
    if so.is_file():
        for line in open(so, 'rb'):
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    checks = dict(binary=meta.get('binary_sha256') == BUILD_SHA,
                  installed_now=installed_sha == BUILD_SHA,
                  pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and pins == 1 and pin1 == 1,
                  recorded=bool(env.get('KYTY_REC')),
                  no_schedule='KYTY_GATE_SCHEDULE' not in env,
                  no_checkpoints='KYTY_GPU_CHECKPOINTS' not in env,
                  one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,
                  default_runs=(' daslot=' not in gates and ' daguard=' not in gates and ' cspfree=' not in gates
                                and ' bdanarrow=' not in gates),
                  no_shift='KYTY_BUFFER_GC_TRIGGER_SHIFT_MB' not in env,
                  frames=bool(mf) and int(mf.group(1)) >= MIN_FRAMES,
                  no_glitch=bool(mg) and int(mg.group(1)) == 0,
                  rows=rows >= MIN_ROWS and missing == 0,
                  slot_default_armed=tot['da_q_free'] > 0 and tot['da_q_noguard'] == 0,
                  slot_no_bad=tot['da_slot_bad'] == 0,
                  free_default_armed=tot['cspfree_hit'] > 0 and tot['cspfree_bad'] == 0,
                  guard=tot['cs_sync_new'] == 0,
                  no_marker=not markers,
                  narrow_default_dark=tot['bda_nskip'] == 0 and tot['bda_nwould'] == 0,
                  gc_default=len(gc_lines) == 1 and gc_lines[0].endswith(' shift_mb=0'),
                  no_title_knob=' titleasync=' not in gates,
                  no_hold='KYTY_PREPARE_HOLD_MS' not in env,
                  title_default_on=(tot['pres_title_n'] > 0
                                    and tot['pres_title_ns'] <= TITLE_WALL_MAX_NS * tot['pres_title_n']),
                  no_overlap=tot['present_overlap'] == 0 and overlap_lines == 0,
                  adm_idle_vid=idle_ok(meta))
    res.update(checks=checks, frames=int(mf.group(1)) if mf else None, glitches=int(mg.group(1)) if mg else None,
               scene_rows=rows, totals=tot, per_row={k: tot[k] / rows for k in FIELDS} if rows else None,
               markers=markers[:10], stable_frame=stable, gc_lines=gc_lines, overlap_lines=overlap_lines,
               title_median_ns=sorted(title_per_call)[len(title_per_call) // 2] if title_per_call else None)
    res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    return res


def evaluate_boot(root=ROOT):
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
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate_all(root)
    print(json.dumps(res, indent=1))
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
