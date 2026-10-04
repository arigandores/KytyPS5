"""Track S, link S12c (HPP-496): writes the seal C:/kyty/s288/pred/08_s.md from s12/seal08_body.md, the DRY=2 plans of go_s12.sh, the
seal lines (sha256 of every sealed file) and the evidence (the LAST output of each suite and tool: path, sha256, count, first line).
Run only without the lock (general rule 27); ASCII only.  usage: python mkseal_s08.py"""
import datetime
import hashlib
import os
import re
import subprocess
import sys

ROOT = 'C:/kyty/s288'
S12 = ROOT + '/s12'
OUT = ROOT + '/pred/08_s.md'
BASH = 'C:/Program Files/Git/bin/bash.exe'
BIN = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
BINP = 'C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe'
TAGS = ('s12_w', 's12_v', 's12_gw', 's12_gr', 's12_v0')
SEAL_FILES = ('s12/go_s12.sh', 's12/sc_s12.py', 's12/test_sc_s12.py', 's12/mut_sc_s12.py', 's12/test_go_s12.py', 's12/regress_s12.py',
              's12/mkseal_s08.py', 's12/seal08_body.md', 's9/enter_scene_s9.py', 'sc_s.py', 'cachex_s.py', 'procload.py', 'idle142.py',
              'fgcpu143.py', 'sheet142.py', 'gates_default.txt', 'run_safety99.py', 'launch_run.py', 'C:/kyty/s142/sc142.py',
              'C:/kyty/scripts/s51_vidglitch.py')
EVIDENCE = (('fixtures sc_s12', 's12/test_sc_s12.out.txt', r'^cases: (\d+)$'),
            ('fixtures go_s12', 's12/test_go_s12.out.txt', r'^checks: (\d+)$'),
            ('regression on real logs (FS5c fs5_w / fs5_v, S10 pi_w1 / pi_r1 / t2_1)', 's12/regress_s12.out.txt', None),
            ('mutants --only (every mutant of mut_sc_s12.py; the whole scorer is new)', 's12/mut_sc_s12.txt', r'^(ALL KILLED.*|SURVIVORS.*)$'))


def sha(p):
    p = p if ':' in p else os.path.join(ROOT, p)
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def first_last(p, rx):
    p = os.path.join(ROOT, p)
    lines = open(p, 'rb').read().decode('ascii', 'replace').splitlines()
    m = None
    if rx:
        for x in lines:
            mm = re.match(rx, x)
            if mm:
                m = mm.group(1)
    return lines[0] if lines else '', lines[-1] if lines else '', m


def main():
    if os.path.exists('C:/kyty/SEALED_RUN.lock'):
        print('lock held - no seal written')
        return 5
    if sha(BINP) != BIN:
        print('the S12 copy differs')
        return 1
    plans = []
    env = dict(os.environ)
    env['DRY'] = '2'
    env['PATH'] = '/usr/bin:/mingw64/bin:' + env.get('PATH', '')
    for t in TAGS:
        p = subprocess.run([BASH, S12 + '/go_s12.sh', t], capture_output=True, text=True, env=env, timeout=120)
        o = (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!\n', '').strip()
        if p.returncode != 0 or not o.startswith('PLAN %s:' % t):
            print('DRY=2 of %s failed: rc %d %s' % (t, p.returncode, o))
            return 1
        plans.append(o)
    body = open(os.path.join(S12, 'seal08_body.md'), 'rb').read().decode('ascii')
    body, tail = body.split('\n## 6. ', 1)
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    out = [body.replace('@WRITTEN@', 'Written by C:/kyty/s288/s12/mkseal_s08.py (sha256 %s) at %s.' % (sha('s12/mkseal_s08.py'), now)).rstrip('\n'),
           '', '## 2. The binary and the call lines (one per tag; PLWAIT=540, item 105 (v); go_s12.sh unsets every KYTY_* and VK_LAYER_* itself)', '',
           's12 binary: %s %s' % (BIN, BINP), '']
    out += ['go_s12 call: PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh %s' % t for t in TAGS]
    out += ['', 'Order (sc_s12.py --allowed): %s; one tag per lock; the lock queue P > F > S (item 322 (g)); the series stops at the first '
            'death marker and at an arm with the word INTERFERENCE; s12_gr only after s12_gw PASS or FAIL with its post copies.' % ' '.join(TAGS),
            '', '## 3. The plan of every arm (go_s12.sh DRY=2, verbatim)', '', '```']
    out += plans
    out += ['```', '', '## 4. Seal lines (sc_s12.py --check-seal checks each before every lock)', '']
    out += ['seal: %s %s' % (sha(f), f) for f in SEAL_FILES]
    out += ['', '## 5. Evidence (the last output of each suite and tool)', '']
    for name, path, rx in EVIDENCE:
        f, l, m = first_last(path, rx)
        out.append('- %s: C:/kyty/s288/%s sha256 %s; %s%s; first line: %s' % (name, path, sha(path), ('count %s / ' % m) if m and rx
                                                                                    and 'KILLED' not in m and 'SURV' not in m else '',
                                                                                    m if m and ('KILLED' in m or 'SURV' in m) else l, f))
    out += ['', '## 6. ' + tail.rstrip('\n')]
    text = '\n'.join(out) + '\n'
    text.encode('ascii')
    with open(OUT, 'wb') as fo:
        fo.write(text.encode('ascii'))
    print('seal %s sha256 %s' % (OUT, hashlib.sha256(text.encode('ascii')).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
