"""Session 108, ROADMAP §0.1 "СЕССИЯ 108" item 5: the video pass of the new build with cspfam=4 as the DEFAULT.
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

sys.path.insert(0, 'C:/kyty/s108')
from run_safety99 import failure_marker  # noqa: E402

ROOT = 'C:/kyty/s108'
TAG = 'vid108'
BUILD_SHA = 'fc78c56417815a0ebdea1c5a5aa94306720c3307d07a6feadf3c8e37f43aae43'
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
    skip = sync_new = sync_wait = rows = 0
    markers, pins = [], 0
    with open('%s/log_%s.txt' % (ROOT, TAG), 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin: mode 1'):
                pins += 1
            if failure_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            m = LINE.match(line)
            if m and m.group(1) == b'FrameTrace-x' and stable is not None and int(m.group(2)) >= stable:
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                rows += 1
                skip += d.get('cspfam_skip', 0)
                sync_new += d.get('cs_sync_new', 0)
                sync_wait += d.get('cs_sync_wait', 0)
    checks = dict(binary=meta.get('binary_sha256') == BUILD_SHA,
                  installed_now=hashlib.sha256(open('C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe',
                                                    'rb').read()).hexdigest() == BUILD_SHA,
                  pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and pins >= 1,
                  recorded=bool(env.get('KYTY_REC')),
                  no_schedule='KYTY_GATE_SCHEDULE' not in env,
                  one_ok_attempt=len(meta.get('attempts', [])) == 1 and len(att) == 1,
                  default_runs=' cspfam=' not in gates,
                  frames=bool(mf) and int(mf.group(1)) >= 3000,
                  no_glitch=bool(mg) and int(mg.group(1)) == 0,
                  default_armed=skip > 0,
                  guard=sync_new == 0,
                  no_marker=not markers)
    res.update(checks=checks, frames=int(mf.group(1)) if mf else None, glitches=int(mg.group(1)) if mg else None,
               scene_rows=rows, cspfam_skip_per_row=skip / rows if rows else None, cs_sync_new=sync_new,
               cs_sync_wait=sync_wait, markers=markers[:10], stable_frame=stable)
    res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    print(json.dumps(res, indent=1))
    if '--out' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
