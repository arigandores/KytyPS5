"""Session 115, ROADMAP §0.1 "СЕССИЯ 115" items 1-2 (seal pred/01_chk115.md): the video pass vid115 and three boot
runs of the build of the presentation-ring fix (no main-thread present during WindowPrepareShaders) with titleasync
default 1.  Derived from the sealed check114.py by make_check115.py; fixtures in test_check115.py, mutants in
mut_check115.py; committed and hashed in SEALS115 before its runs.

PASS needs every check below (video TAG, then boot BOOT_TAGS):
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
  adm_idle_vid             pre_run.gpu_util_median <= IDLE_GPU_MAX (admission)
  Boot runs BOOT_TAGS, checks prefixed by the tag's last letter x (a, b, c), all with KYTY_PREPARE_HOLD_MS=HOLD_MS:
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
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s115'
TAG = 'vid115'
BOOT_TAGS = ('boot115a', 'boot115b', 'boot115c')
BOOT_CONTROL = 'boot115b'
BOOT_SHIP = 'boot115c'
BUILD_SHA = 'd3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
MIN_FRAMES = 3000
MIN_ROWS = 1000
TITLE_WALL_MAX_NS = 60000
HOLD_MS = 10000
BOOT_DEFAULTS = ('daslot', 'daguard', 'cspfree', 'bdanarrow', 'titleasync')
IDLE_GPU_MAX = 10
PRESENTS_MIN = 300
FATAL_SITE = b'commandRecorder.cpp:326'
FIELDS = ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait', 'da_q_free', 'da_q_noguard', 'da_slot_bad',
          'da_guard_yield', 'bda_nskip', 'bda_nwould', 'prio_stall', 'prio_unsub', 'pres_title_ns', 'pres_title_n',
          'present_overlap')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
LINE = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
WAIT = re.compile(rb'^ShaderPreparation: startup wait finished in (\d+) ms(?: presents_other=(\d+) presents_main=(\d+))?')
DRAW = re.compile(rb'^FrameTrace-draw: n=(\d+)')
BDA_SCAN = re.compile(rb' bda_scan=(\d+)')


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
    bda_scans = []
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
            md = DRAW.match(line)
            if md and stable is not None and int(md.group(1)) >= stable:
                mb = BDA_SCAN.search(line)
                if mb:
                    bda_scans.append(int(mb.group(1)))
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
               title_median_ns=sorted(title_per_call)[len(title_per_call) // 2] if title_per_call else None,
               bda_scan_median=sorted(bda_scans)[len(bda_scans) // 2] if bda_scans else None)
    res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    return res


def evaluate_boot(root, tag):
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
