"""Session 114, ROADMAP §0.1 "СЕССИЯ 114" item 13 (seal pred/03b_bootctl114.md): the two control boots of the fatal
`commandRecorder.cpp:326` seen in boot114.  boot114b = boot114 again (default titleasync=1); boot114c = the same with
KYTY_TITLE_ASYNC=0 in env and ` titleasync=0` in the gate text.  Both on the build BUILD_SHA with
KYTY_PREPARE_HOLD_MS=10000, GPU clock pin, no schedule, no checkpoints.

Per tag, setup (all must hold, else the tag is NOT_EVALUABLE):
  binary, hold_env (KYTY_PREPARE_HOLD_MS == '10000'), pinned (env KYTY_GPU_CLOCK_PIN == '1'), no_schedule,
  no_checkpoints, knob (b: no KYTY_TITLE_ASYNC in env and no ` titleasync=` in the gates;
                        c: env KYTY_TITLE_ASYNC == '0' and ` titleasync=0 ` in the gates)
Per tag, outcome SAME_FATAL iff: exactly one `PrepareHold: ms=10000` line, a line containing FATAL_SITE after it, and no
`ShaderPreparation: startup wait finished` line; otherwise OTHER.
Verdict: NOT_EVALUABLE if any tag's setup fails; KEEP_1 if both tags read SAME_FATAL; DEFAULT_0 otherwise.

    python C:/kyty/s114/bootctl114.py [--root C:/kyty/s114] [--out <json>]
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = 'C:/kyty/s114'
TAGS = ('boot114b', 'boot114c')
BUILD_SHA = '8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec'
HOLD_LINE = b'PrepareHold: ms=10000'
FATAL_SITE = b'commandRecorder.cpp:326'
WAIT_LINE = b'ShaderPreparation: startup wait finished'


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evaluate_tag(root, tag):
    meta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    gates = ' ' + ' '.join((meta.get('gates') or '').split()) + ' '
    if tag.endswith('c'):
        knob = env.get('KYTY_TITLE_ASYNC') == '0' and ' titleasync=0 ' in gates
    else:
        knob = 'KYTY_TITLE_ASYNC' not in env and ' titleasync=' not in gates
    setup = dict(binary=meta.get('binary_sha256') == BUILD_SHA,
                 hold_env=env.get('KYTY_PREPARE_HOLD_MS') == '10000',
                 pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1',
                 no_schedule='KYTY_GATE_SCHEDULE' not in env,
                 no_checkpoints='KYTY_GPU_CHECKPOINTS' not in env,
                 knob=knob)
    holds = []
    fatal_after_hold = False
    waits = 0
    fatal_lines = []
    with open(Path(root) / ('log_%s.txt' % tag), 'rb') as f:
        for i, line in enumerate(f):
            if line.startswith(HOLD_LINE):
                holds.append(i)
            if FATAL_SITE in line:
                fatal_lines.append(line[:200].decode('utf-8', 'replace').strip())
                if holds:
                    fatal_after_hold = True
            if line.startswith(WAIT_LINE):
                waits += 1
    same = len(holds) == 1 and fatal_after_hold and waits == 0
    return dict(setup=setup, setup_ok=all(setup.values()), holds=len(holds), fatal_after_hold=fatal_after_hold,
                waits=waits, fatal_lines=fatal_lines[:4], outcome='SAME_FATAL' if same else 'OTHER')


def evaluate(root=ROOT):
    res = dict(check_sha256=sha_file(__file__), build_sha256=BUILD_SHA,
               tags={tag: evaluate_tag(root, tag) for tag in TAGS})
    if not all(t['setup_ok'] for t in res['tags'].values()):
        res['verdict'] = 'NOT_EVALUABLE'
    elif all(t['outcome'] == 'SAME_FATAL' for t in res['tags'].values()):
        res['verdict'] = 'KEEP_1'
    else:
        res['verdict'] = 'DEFAULT_0'
    return res


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate(root)
    print(json.dumps(res, indent=1))
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
