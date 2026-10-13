"""Track M link M3a (HPP-842): the pairs of the seal section 6 over the ADMITTED tags (added after the seal: post_m3a.sh pairs the base
names m3_<L>_v / m3_<L>_f only; a repeat <tag>_r<k> of item 764 replaces its base - this file picks, per name, the last admitted of
<name>, <name>_r1, <name>_r2 by runs/<tag>/read.json).  Presentation only: it reads no member and decides nothing.
  pairs/pair_<L>.png       sheet of the admitted MS1 V (left) beside the sheet of the admitted FS15 V (right)
  pairs/banner_t231.png    frames 19.5 .. 21.5 s every 0.25 s: the admitted m3_sg_v (top, T231=1) and m3_sg_t2310 (bottom, T231=0)
Prints one line per pair with the tags and the sha256 of the image.  Refuses under the lock (exit 3).  ASCII only."""
import hashlib
import json
import os
import subprocess
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - exit 3')
    sys.exit(3)
G = 'C:/kyty/m657/m3a'
P = G + '/pairs'


def admitted(name):
    pick = None
    for t in (name, name + '_r1', name + '_r2'):
        js = os.path.join(G, 'runs', t, 'read.json')
        if os.path.exists(js) and json.load(open(js, encoding='utf-8')).get('admitted'):
            pick = t
    return pick


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def ff(args):
    return subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + args, capture_output=True).returncode


def main():
    os.makedirs(P, exist_ok=True)
    for L in ('sg', 'hb', 'mg', 'ac', 'f1', 'f2'):
        a, f = admitted('m3_%s_v' % L), admitted('m3_%s_f' % L)
        if not a or not f:
            print('pair %s: not both admitted (MS1 %s, FS15 %s)' % (L, a, f))
            continue
        sa = os.path.join(G, 'runs', a, 'sheet_%s.png' % a)
        sf = os.path.join(G, 'runs', f, 'sheet_%s.png' % f)
        out = os.path.join(P, 'pair_%s.png' % L)
        rc = ff(['-i', sa, '-i', sf, '-filter_complex', '[0][1]scale2ref=iw:ih[a][b];[a][b]hstack', out])
        print('pair %s: left %s (MS1), right %s (FS15) -> pairs/pair_%s.png rc %d sha256 %s' % (L, a, f, L, rc, sha(out) if rc == 0 else '-'))
    a, b = admitted('m3_sg_v'), admitted('m3_sg_t2310')
    if a and b:
        for k, t in (('top', a), ('bottom', b)):
            ff(['-ss', '19.5', '-t', '2.1', '-i', os.path.join(G, 'rec_%s.mp4' % t), '-vf', 'fps=4,scale=320:-1,tile=9x1', '-frames:v', '1',
                os.path.join(P, 'banner_%s.png' % k)])
        out = os.path.join(P, 'banner_t231.png')
        rc = ff(['-i', os.path.join(P, 'banner_top.png'), '-i', os.path.join(P, 'banner_bottom.png'), '-filter_complex', 'vstack', out])
        print('banner T231: top %s (T231=1), bottom %s (T231=0), 19.5-21.5 s every 0.25 s -> pairs/banner_t231.png rc %d sha256 %s' % (
            a, b, rc, sha(out) if rc == 0 else '-'))
    else:
        print('banner T231: not both admitted (%s, %s)' % (a, b))
    return 0


if __name__ == '__main__':
    sys.exit(main())
