# tilepeek145.py - Session Auditor, s145 step 3 (HPP-353): frames i-1, i, i+1 of the top per-tile events of glitch145.py
# as one PNG per event (upper row: whole frames at half size; lower row: the tile at double size). Local files only.
# Usage: python tilepeek145.py <tag> <frame> <row> <col> [...repeated quadruples]
import subprocess, sys, os

OUT = 'C:/kyty/s145/step3/glx/peek'
os.makedirs(OUT, exist_ok=True)
a = sys.argv[1:]
for k in range(0, len(a), 4):
    tag, fr, r, c = a[k], int(a[k + 1]), int(a[k + 2]), int(a[k + 3])
    root = 'C:/kyty/s144' if tag.startswith('v144') else 'C:/kyty/s145'
    src = '%s/rec_%s.mp4' % (root, tag)
    out = '%s/%s_f%d_r%dc%d.png' % (OUT, tag, fr, r, c)
    sel = "select='between(n,%d,%d)',setpts=N/FRAME_RATE/TB" % (fr - 1, fr + 1)
    flt = ("[0:v]%s,split=2[a][b];[a]scale=480:270,tile=3x1[top];[b]crop=240:135:%d:%d,scale=480:270:flags=neighbor,tile=3x1[bot];"
           "[top][bot]vstack=inputs=2[o]") % (sel, c * 240, r * 135)
    p = subprocess.run(['ffmpeg', '-nostdin', '-y', '-hide_banner', '-loglevel', 'error', '-i', src, '-filter_complex', flt, '-map', '[o]',
                        '-frames:v', '1', out], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    print(tag, fr, r, c, 'rc', p.returncode, out, p.stderr.strip()[:200])
