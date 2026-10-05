"""Track F link F16q (HPP-597; ROADMAP s122 item 504 (zh), (z)): the present number of the first scene frame of one video arm - a REPORT row
for the lead (item 504 (z): an entry screen frame - mean brightness <= 5 of 255 - in one arm against a scene frame in the other is a
different moment of the entry, the lead compares the present of the first scene frame of both arms).  No verdict.
usage: python f16q_luma.py <rec.mp4> <rec.mp4.idx>
Definition (the seal docs/track-f/f16q.md section 5): the mean of R, G, B over the frame scaled to 32x18 (ffmpeg rgb24, full range), per
video frame in video order; the present of a video frame - the second column of its .idx record.  Printed:
  SCENE first > 5        the first video frame with mean > 5, its present;
  SCENE first > 5 held   the first video frame with mean > 5 whose next 59 video frames also have mean > 5 (one second at 60), its present.
ASCII output only."""
import subprocess, sys

W, H = 32, 18
THR = 5.0
HELD = 60


def means(rec):
    pr = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', rec, '-vf', 'scale=%d:%d' % (W, H), '-pix_fmt', 'rgb24',
                         '-f', 'rawvideo', '-'], capture_output=True)
    b = pr.stdout
    n = W * H * 3
    return [sum(b[i:i + n]) / float(n) for i in range(0, len(b) - n + 1, n)]


def idx_presents(path):
    out = []
    with open(path, 'rb') as f:
        for raw in f:
            parts = raw.split()
            if len(parts) >= 2:
                out.append(int(parts[1]))
    return out


def first_scene(m, held):
    for i in range(len(m)):
        if all(x > THR for x in m[i:i + held]) and len(m[i:i + held]) == held:
            return i
    return None


def main(argv):
    m = means(argv[0])
    pres = idx_presents(argv[1])
    print('LUMA %s: video frames %d, idx records %d' % (argv[0], len(m), len(pres)))
    for name, held in (('first > 5', 1), ('first > 5 held %d frames' % HELD, HELD)):
        i = first_scene(m, held)
        if i is None:
            print('SCENE %s: none' % name)
        else:
            print('SCENE %s: video %d present %s mean %.1f' % (name, i, pres[i] if i < len(pres) else 'NOT_IN_IDX', m[i]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
