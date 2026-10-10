"""F34a: two-row sheet, same offsets from level start in two KYTY_REC videos.
usage: pair.py <out.png> <mp4_a> <present_of_level_start_a> <mp4_b> <present_of_level_start_b> <rel>[,<rel>...]"""
import subprocess, sys
out, A, pa, B, pb, rels = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), [int(x) for x in sys.argv[6].split(',')]
def frames(mp4, p0):
    idx = [l.split() for l in open(mp4 + '.idx') if l.strip()]
    p2f = {int(p): int(f) for f, p, t in idx}
    pres = sorted(p2f)
    return [p2f[min(pres, key=lambda p: abs(p - (p0 + r)))] for r in rels]
rows = []
for k, (mp4, p0) in enumerate(((A, pa), (B, pb))):
    fr = frames(mp4, p0)
    sel = '+'.join('eq(n' + chr(92) + ',%d)' % f for f in fr)
    o = out + '.row%d.png' % k
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vf', "select='%s',scale=384:216,tile=%dx1" % (sel, len(fr)),
                        '-vsync', '0', '-frames:v', '1', o], capture_output=True, text=True)
    print(mp4, 'frames', fr, 'rc', r.returncode, r.stderr[-200:])
    rows.append(o)
r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', rows[0], '-i', rows[1], '-filter_complex', 'vstack', out], capture_output=True, text=True)
print('vstack rc', r.returncode)
