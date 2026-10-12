"""Track M, M2b (HPP-839, ROADMAP s122 item 756(v)(2)(i)): driver and reader of m_wave1_hle_stand.

Usage: run_stand_m2b.py <stand exe> <out dir> [--only t265|t272|t231] [--knob 0|1]
Runs every arm at KYTY_M_<theme>=0 and =1 (one process each; the other two knobs unset), writes <out>/<arm>_k<k>.out.txt
and checks the members fixed before the code (item 756(v)(2)(i)):
  t265 =0 reproduced: every /app0/ pair resolves, both paths get the same ID and the file ID API answers A's ID with B's
       size (keep_a=0) - 5 of 5; =1: expect_upstream=1 (distinct valid IDs, A's size and stat by A's ID, the ID kept on
       re-resolution) - 5 of 5. The app0/ pairs (no leading slash) are reference only.
  t272 =0 reproduced: after the effects are set and the triggers pass their start positions the answer is 0,0 (step
       "triggers did not activate at the documented start positions"); =1: every upstream check matches (45 of 45).
  t231 =0 reproduced: every glyph of the game's font at 310 px comes out at most 128 x 128 while the reference is
       larger (clamp128=1, 10 of 10); =1: image size, ink box, pixel sum and metric height equal the reference, 10 of 10.
Last line ALL OK, or FAIL with every failed member. Lock and STOP checked before every process.
"""
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
GAME = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app'
FONT = GAME + '/data/common/font/LevelNameFont.otf'
HERE = 'C:/kyty/m657/m2b'
ARMS = {
    't265': (['t265', GAME, HERE + '/pairs_t265.tsv'], 'KYTY_M_T265'),
    't272': (['t272'], 'KYTY_M_T272'),
    't231': (['t231', FONT, '310', 'SkyGardenW'], 'KYTY_M_T231'),
}


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def run(exe, arm, knob, out_dir):
    guard()
    args, name = ARMS[arm]
    env = dict(os.environ)
    for _, (_, n) in ARMS.items():
        env.pop(n, None)
    env[name] = str(knob)
    p = subprocess.run([exe] + args, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    text = p.stdout.decode('utf-8', 'replace')
    path = '%s/%s_k%d.out.txt' % (out_dir, arm, knob)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return p.returncode, text


def kv(line):
    return dict(re.findall(r'(\w+)=("[^"]*"|\S+)', line))


def check(arm, knob, rc, text):
    fails = []
    lines = [l for l in text.splitlines() if l.startswith('MStand: ' + arm + ' ')]
    end = [l for l in lines if l.endswith(' END')]
    if rc != 0 or len(end) != 1:
        return ['%s k%d: rc=%d END lines=%d' % (arm, knob, rc, len(end))]
    e = kv(end[0])
    if int(e['knob']) != knob:
        fails.append('%s k%d: knob read %s' % (arm, knob, e['knob']))
    body = [kv(l) for l in lines if ' END' not in l]
    if arm == 't265':
        pairs = [b for b in body if b.get('prefix') == '/app0/']
        if len(pairs) != 5:
            fails.append('t265 k%d: /app0/ pairs %d != 5' % (knob, len(pairs)))
        if knob == 0:
            rep = [b for b in pairs if b['rc_a'] == '0' and b['rc_b'] == '0' and b['same_id'] == '1' and
                   b['keep_a'] == '0' and b['expect_upstream'] == '0']
            if len(rep) != 5:
                fails.append('t265 k0: reproduced %d of 5' % len(rep))
        else:
            ok = [b for b in pairs if b['expect_upstream'] == '1']
            if len(ok) != 5:
                fails.append('t265 k1: upstream answer %d of 5' % len(ok))
    elif arm == 't272':
        if len(body) != 45:
            fails.append('t272 k%d: checks %d != 45' % (knob, len(body)))
        if knob == 0:
            key = [b for b in body if b.get('name') == '"triggers did not activate at the documented start positions"']
            if len(key) != 1 or key[0]['got'] != '0,0' or key[0]['want'] != '2,4':
                fails.append('t272 k0: answer after the set effect is not 0,0')
        else:
            bad = [b['step'] for b in body if b['match'] != '1']
            if bad:
                fails.append('t272 k1: mismatched steps %s' % ','.join(bad))
    elif arm == 't231':
        if len(body) != 10:
            fails.append('t231 k%d: glyphs %d != 10' % (knob, len(body)))
        if knob == 0:
            rep = [b for b in body if b['clamp128'] == '1' and b['match'] == '0']
            if len(rep) != 10:
                fails.append('t231 k0: clamp128 %d of 10' % len(rep))
        else:
            ok = [b for b in body if b['match'] == '1']
            if len(ok) != 10:
                fails.append('t231 k1: match %d of 10' % len(ok))
    return fails


def main():
    exe, out_dir = sys.argv[1], sys.argv[2]
    only = None
    knobs = [0, 1]
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]
    if '--knob' in sys.argv:
        knobs = [int(sys.argv[sys.argv.index('--knob') + 1])]
    os.makedirs(out_dir, exist_ok=True)
    fails = []
    for arm in ARMS:
        if only and arm != only:
            continue
        for k in knobs:
            rc, text = run(exe, arm, k, out_dir)
            f = check(arm, k, rc, text)
            print('%s k%d: %s' % (arm, k, 'OK' if not f else 'FAIL ' + '; '.join(f)))
            fails += f
    print('ALL OK' if not fails else 'FAIL ' + ' | '.join(fails))
    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    main()
