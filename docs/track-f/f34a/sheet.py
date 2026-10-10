"""F34a: contact sheet of a KYTY_REC video by present numbers from its .idx (frame present time).
usage: sheet.py <mp4> <out.png> <p_from> <p_to> <step> [cols]"""
import subprocess, sys
mp4, out, a, b, st = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 6
idx = [l.split() for l in open(mp4 + '.idx') if l.strip()]
p2f = {int(p): int(f) for f, p, t in idx}
pres = sorted(p2f)
fr = []
for w in range(a, b + 1, st):
    q = min(pres, key=lambda p: abs(p - w))
    fr.append((q, p2f[q]))
rows = (len(fr) + cols - 1) // cols
sel = '+'.join('eq(n' + chr(92) + ',%d)' % f for _, f in fr)
vf = "select='%s',scale=256:144,tile=%dx%d" % (sel, cols, rows)
r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vf', vf, '-vsync', '0', '-frames:v', '1', out],
                   capture_output=True, text=True)
print('rc', r.returncode, 'tiles (present, frame):', fr)
