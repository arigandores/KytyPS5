"""Session 110, ROADMAP §0.1 "СЕССИЯ 110" item 6: the video pass of the build with cspfree=1 as the DEFAULT.
Derived from check108r.py (session 108) with the default-armed check on cspfree and markers read from stdout too.
Pinned to that build's sha256.  PASS needs: the installed binary recorded in vid108.json = BUILD_SHA, pinned
(KYTY_GPU_CLOCK_PIN=1), recorded, no schedule, one ok attempt, `cspfam` absent from the gate text (the default is
what runs), >= 3 000 frames and 0 one-frame glitches, and in the log: cspfam_skip > 0 over the scene (the default
armed) and cs_sync_new == 0 over the scene (the guard), no failure marker.

    python C:/kyty/s108/check108.py [--out <json>]
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, 'C:/kyty/s110')
from run_safety99 import failure_marker  # noqa: E402

ROOT = 'C:/kyty/s110'
TAG = 'vid110'
BUILD_SHA = '072861c89193c3726232e44e78be4f36172254af826394b56c8bf671ef609c21'
LINE = re.compile(rb'^(FrameTrace(?:-draw|-x)?): n=(\d+)')
FIELD = re.compile(rb'(\w+)=(-?\d+)')


def main():
    res = dict(check_sha256=hashlib.sha256(open(__file__, 'rb').read()).hexdigest(), build_sha256=BUILD_SHA)
    meta = json.load(open('%s/%s.json' % (ROOT, TAG), encoding='utf-8'))
    env = meta.get('env') or {}
    att = [a for a in meta.get('attempts', []) if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    stable = att[-1].get('stable_frame', 0) if att else None
    gates = ' ' + (meta.get('gates') or '') + ' '
    text = open('%s/%s_glitch.txt' % (ROOT, TAG), encoding='utf-8', errors='replace').read()
    mf = re.search(r'(\d+) frames', text)
    mg = re.search(r'one-frame glitches:\s*(\d+)', text)
    hit = bad = sync_new = sync_wait = rows = missing = 0
    markers, pins = [], 0
    with open('%s/log_%s.txt' % (ROOT, TAG), 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin: mode 1'):
                pins += 1
            if failure_marker(line) or line.startswith(b'--- Error ---') or b'AsyncPipelines: skipped draw' in line:
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            m = LINE.match(line)
            if m and m.group(1) == b'FrameTrace-x' and stable is not None and int(m.group(2)) >= stable:
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                rows += 1
                missing += int(any(k not in d for k in ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait')))
                hit += d.get('cspfree_hit', 0)
                bad += d.get('cspfree_bad', 0)
                sync_new += d.get('cs_sync_new', 0)
                sync_wait += d.get('cs_sync_wait', 0)
    checks = dict(binary=meta.get('binary_sha256') == BUILD_SHA,
                  installed_now=hashlib.sha256(open('C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe',
                                                    'rb').read()).hexdigest() == BUILD_SHA,
                  pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and pins >= 1,
                  recorded=bool(env.get('KYTY_REC')),
                  no_schedule='KYTY_GATE_SCHEDULE' not in env,
                  one_ok_attempt=len(meta.get('attempts', [])) == 1 and len(att) == 1,
                  default_runs=' cspfree=' not in gates,
                  frames=bool(mf) and int(mf.group(1)) >= 3000,
                  no_glitch=bool(mg) and int(mg.group(1)) == 0,
                  default_armed=hit > 0 and rows > 0,
                  no_bad=bad == 0,
                  fields_present=missing == 0,
                  no_checkpoints='KYTY_GPU_CHECKPOINTS' not in env,
                  guard=sync_new == 0,
                  no_marker=not markers)
    so = '%s/stdout_%s.txt' % (ROOT, TAG)
    if os.path.exists(so):
        for line in open(so, 'rb'):
            if failure_marker(line) or line.startswith(b'--- Error ---') or b'AsyncPipelines: skipped draw' in line:
                markers.append(line[:200].decode('utf-8', 'replace').strip())
        checks['no_marker'] = not markers
    res.update(checks=checks, frames=int(mf.group(1)) if mf else None, glitches=int(mg.group(1)) if mg else None,
               scene_rows=rows, cspfree_hit_per_row=hit / rows if rows else None, cs_sync_new=sync_new,
               cs_sync_wait=sync_wait, markers=markers[:10], stable_frame=stable)
    res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    print(json.dumps(res, indent=1))
    if '--out' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
