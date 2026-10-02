"""tilereg146.py - session 146 step 0 (HPP-386): the regression of tiles146.py on the videos of s145 against the auditor's
counts (C:/kyty/KytyPS5/docs/session-145/audit/glitch145.out.txt: "frames with a tile event T 4: K, T 12: K12" and the first
"top tile events" entry) and the frame count of the same line.  ASCII.  usage: python tilereg146.py <part 1|2|all> [--workers N]"""
import os
import re
import subprocess
import sys
from multiprocessing import Pool

AUD = 'C:/kyty/KytyPS5/docs/session-145/audit/glitch145.out.txt'
VIDS = ['C:/kyty/s145/rec_v145_%02d.mp4' % i for i in range(2, 18)] + ['C:/kyty/s144/rec_v144_09.mp4']
OUT = 'C:/kyty/s146/step0/tilereg'
RX = re.compile(r'^GLITCH (\S+) sha (\w+): frames (\d+) .*frames with a tile event T 4: (\d+), T 12: (\d+); top tile events '
                r'\(frame, row, col, d1, d2, back, tiles\) (.*)$')


def run(v):
    os.makedirs(OUT, exist_ok=True)
    o = os.path.join(OUT, os.path.basename(v) + '.tiles.txt')
    subprocess.run([sys.executable, 'C:/kyty/s146/tiles146.py', v, o], capture_output=True)
    return v, open(o, encoding='ascii').readline().strip() if os.path.isfile(o) else 'missing'


def main():
    part = sys.argv[1]
    w = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 4
    vids = VIDS[:9] if part == '1' else (VIDS[9:] if part == '2' else VIDS)
    aud = {}
    for line in open(AUD, encoding='ascii', errors='replace'):
        m = RX.match(line.strip())
        if m:
            aud[m.group(1)] = (int(m.group(3)), int(m.group(4)), int(m.group(5)), m.group(6))
    with Pool(w) as p:
        res = p.map(run, vids, chunksize=1)
    ok = True
    for v, line in res:
        m = re.match(r'^TILES (\S+) sha256 \w+: frames (\d+); tile events T4 (\d+), T12 (\d+); events (.*)$', line)
        a = aud.get(os.path.basename(v))
        good = m is not None and a is not None and (int(m.group(2)), int(m.group(3)), int(m.group(4))) == a[:3]
        ok &= good
        print('TILEREG %s mine %s auditor %s -> %s' % (os.path.basename(v), (m.group(2), m.group(3), m.group(4)) if m else line[:80],
                                                      a[:3] if a else None, 'equal' if good else 'DIFFERENT'))
    print('TILEREG part %s: %s' % (part, 'ALL EQUAL' if ok else 'SOME DIFFERENT'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
