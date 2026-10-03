"""F9d (HPP-421, ROADMAP s122 item 349 (v')(1)): contact sheets of one recording in a single streaming decode.
usage: python sheets_f9d.py <rec.mp4> <out_dir> <prefix> <rot_from> <rot_to> <static_from>
Video frame v (0-based) = present v+1 (.idx). Sheets: 1 frame/s of the whole video (every 60th frame, 8x6 tiles 240x135),
4 frames/s (every 15th frame, 6x6 tiles 320x180) on [rot_from, rot_to) - "in water with rotation" - and on
[static_from, end) - "static side camera". Every tile carries the video frame number and the time at 60 frames/s.
Output PNG; ASCII output only."""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

path, out, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
rot_from, rot_to, static_from = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
os.makedirs(out, exist_ok=True)
W, H = 960, 540
groups = {'1fps': ([], 60, (240, 135), 8, 6), 'rot4': ([], 15, (320, 180), 6, 6), 'static4': ([], 15, (320, 180), 6, 6)}
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
n = 0
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    want = []
    if n % 60 == 0:
        want.append('1fps')
    if rot_from <= n < rot_to and (n - rot_from) % 15 == 0:
        want.append('rot4')
    if n >= static_from and (n - static_from) % 15 == 0:
        want.append('static4')
    if want:
        img = Image.frombuffer('RGB', (W, H), buf, 'raw', 'RGB', 0, 1)
        for g in want:
            tiles, _, size, _, _ = groups[g]
            t = img.resize(size, Image.BILINEAR)
            d = ImageDraw.Draw(t)
            label = 'f%d %d:%05.2f' % (n, n // 3600, (n % 3600) / 60.0)
            d.rectangle([0, 0, 7 * len(label) + 4, 12], fill=(0, 0, 0))
            d.text((2, 0), label, fill=(255, 255, 0))
            tiles.append(t)
    n += 1
p.wait()
print('frames decoded %d' % n)
for g, (tiles, _, size, cols, rows) in groups.items():
    per = cols * rows
    for s in range(0, len(tiles), per):
        chunk = tiles[s:s + per]
        r = (len(chunk) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * size[0], r * size[1]))
        for i, t in enumerate(chunk):
            sheet.paste(t, ((i % cols) * size[0], (i // cols) * size[1]))
        name = os.path.join(out, '%s_%s_%02d.png' % (prefix, g, s // per + 1))
        sheet.save(name)
        print('%s tiles %d' % (name, len(chunk)))
