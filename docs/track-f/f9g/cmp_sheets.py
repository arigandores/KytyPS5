"""F9g (HPP-424, ROADMAP s122 item 349 (g)(3)): sheets of pairs - the same video frame v of the =0 tag (left) and the =1 tag
(right) - for every 15th frame of [from, to) (the rotation phase, form of sheets_f9d.py).  One streaming decode per video.
usage: python cmp_sheets.py <rec_left.mp4> <rec_right.mp4> <out_dir> <prefix> <from> <to>
Pairs of 320x180 tiles side by side, 3 pairs per row, 6 rows per sheet; every tile carries its v and L/R.  ASCII output only."""
import os, subprocess, sys
from PIL import Image, ImageDraw

W, H = 960, 540


def grab(path, lo, hi):
    out = {}
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        if lo <= n < hi and (n - lo) % 15 == 0:
            out[n] = Image.frombuffer('RGB', (W, H), buf, 'raw', 'RGB', 0, 1).resize((320, 180), Image.BILINEAR)
        n += 1
    p.wait()
    return out, n


def main():
    left, right, out, prefix, lo, hi = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
    os.makedirs(out, exist_ok=True)
    a, na = grab(left, lo, hi)
    b, nb = grab(right, lo, hi)
    keys = sorted(set(a) & set(b))
    print('frames left %d right %d pairs %d' % (na, nb, len(keys)))
    per = 18
    for s in range(0, len(keys), per):
        chunk = keys[s:s + per]
        rows = (len(chunk) + 2) // 3
        sheet = Image.new('RGB', (3 * 650, rows * 180), (40, 40, 40))
        for i, v in enumerate(chunk):
            x, y = (i % 3) * 650, (i // 3) * 180
            for j, img in enumerate((a[v], b[v])):
                t = img.copy()
                d = ImageDraw.Draw(t)
                label = '%s f%d' % ('L=0' if j == 0 else 'R=1', v)
                d.rectangle([0, 0, 7 * len(label) + 4, 12], fill=(0, 0, 0))
                d.text((2, 0), label, fill=(255, 255, 0))
                sheet.paste(t, (x + j * 325, y))
        name = os.path.join(out, '%s_%02d.png' % (prefix, s // per + 1))
        sheet.save(name)
        print('%s pairs %d' % (name, len(chunk)))


if __name__ == '__main__':
    main()
