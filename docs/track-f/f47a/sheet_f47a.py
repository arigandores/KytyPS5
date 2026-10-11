# F47a (HPP-802): sheet of video frames (0-based video frame numbers = the first column of <mp4>.idx), tiled W wide,
# each frame scaled to PX wide, with the frame number drawn in the corner (drawtext of ffmpeg's frame counter is not the
# selected frame number, so the numbers are printed in the sheet's .txt next to it, row by row).
# Usage: python sheet_f47a.py <mp4> <out.png> <a> <b> [step] [--w 6] [--px 320]
import hashlib, os, subprocess, sys

mp4, outp, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
step = int(sys.argv[5]) if len(sys.argv) > 5 and not sys.argv[5].startswith('--') else 1
W = int(sys.argv[sys.argv.index('--w') + 1]) if '--w' in sys.argv else 6
PX = int(sys.argv[sys.argv.index('--px') + 1]) if '--px' in sys.argv else 320
frames = list(range(a, b + 1, step))
sel = '+'.join('eq(n%s%d)' % (chr(92) + ',', i) for i in frames)
rows = (len(frames) + W - 1) // W
vf = "select='%s',scale=%d:-1,tile=%dx%d" % (sel, PX, W, rows)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp4, '-vf', vf, '-frames:v', '1', '-vsync', '0', outp], check=True)
with open(os.path.splitext(outp)[0] + '.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write('video %s\nframes (row-major, %d wide):\n' % (mp4, W))
    for r in range(rows):
        f.write(' '.join(str(x) for x in frames[r * W:(r + 1) * W]) + '\n')
    f.write('png sha256 %s\n' % hashlib.sha256(open(outp, 'rb').read()).hexdigest())
print(outp, len(frames), 'frames')
