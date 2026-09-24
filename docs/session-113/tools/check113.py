"""Session 113, ROADMAP §0.1 "СЕССИЯ 113" item 21: the video pass of the build 1678d3f4 (knob `bdanarrow`, default 0;
the env KYTY_BUFFER_GC_TRIGGER_SHIFT_MB, default 0; the exact knob-2 check; the priority-stall instrument) with
today's defaults (`daslot=1 daguard=1 cspfree=1 bdanarrow=0`).  Derived from check112.py by make_check113.py.
Written fresh (session 111's check111.py had a stale docstring and no fixtures - audit MINOR-3); fixtures in
test_check112.py; committed and hashed in SEALS112 before its run.

PASS needs every check below:
  binary / installed_now   vid112.json binary and the installed exe are BUILD_SHA
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
Reported, not checked: cs_sync_wait, da_guard_yield, prio_stall, prio_unsub.

    python C:/kyty/s113/check113.py [--root C:/kyty/s113] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s113'
TAG = 'vid113'
BUILD_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
MIN_FRAMES = 3000
MIN_ROWS = 1000
FIELDS = ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait', 'da_q_free', 'da_q_noguard', 'da_slot_bad',
          'da_guard_yield', 'bda_nskip', 'bda_nwould', 'prio_stall', 'prio_unsub')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
LINE = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


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
    markers = []
    with open(Path(root) / ('log_%s.txt' % TAG), 'rb') as f:
        for line in f:
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
                  gc_default=len(gc_lines) == 1 and gc_lines[0].endswith(' shift_mb=0'))
    res.update(checks=checks, frames=int(mf.group(1)) if mf else None, glitches=int(mg.group(1)) if mg else None,
               scene_rows=rows, totals=tot, per_row={k: tot[k] / rows for k in FIELDS} if rows else None,
               markers=markers[:10], stable_frame=stable, gc_lines=gc_lines)
    res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    return res


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate(root)
    print(json.dumps(res, indent=1))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
