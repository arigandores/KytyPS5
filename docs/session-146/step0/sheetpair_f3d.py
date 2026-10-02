"""sheetpair_f3d.py <ref.mp4> <new.mp4> <out.png> [n=24] - the pair sheet "v142 / F3d" of ROADMAP p.259(d) V4 and p.259(e)(5)(b)
(F3d, HPP-342): n frames of each video at THE SAME frame positions k * step, step = min(frame count of the two) // n
(k = 0 .. n-1; variant of the executor [I] for "the same positions": the same frame index n of both videos), each scaled to
240 px wide and tiled 6 x (n / 6); the sheet of the reference is on top, the sheet of the new video below.  The positions are
printed.  ASCII only: "sheetpair: <png> ref <frames> new <frames> step <k> positions <list>"; rc 1 when a video has no frames
or ffmpeg fails; rc 2 usage.
"""
import os
import subprocess
import sys


def frame_count(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                          '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout.strip()
    try:
        return int(out.split(',')[0])
    except ValueError:
        return 0


def positions(total_ref, total_new, n):
    m = min(total_ref, total_new)
    if m <= 0 or n <= 0:
        return 0, []
    step = max(1, m // n)
    return step, [k * step for k in range(n) if k * step < m]


def main(argv):
    if len(argv) < 4:
        print('usage: sheetpair_f3d.py <ref.mp4> <new.mp4> <out.png> [n]')
        return 2
    ref, new, dst = argv[1], argv[2], argv[3]
    n = int(argv[4]) if len(argv) > 4 else 24
    tr, tn = frame_count(ref), frame_count(new)
    step, pos = positions(tr, tn, n)
    if not pos:
        print('sheetpair: no frames (ref %d new %d)' % (tr, tn))
        return 1
    cols = 6
    rows = (len(pos) + cols - 1) // cols
    sel = '+'.join('eq(n\\,%d)' % p for p in pos)
    one = "select='%s',scale=240:-1,tile=%dx%d" % (sel, cols, rows)
    fc = '[0:v]%s[a];[1:v]%s[b];[a][b]vstack=inputs=2[o]' % (one, one)
    done = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', ref, '-i', new, '-filter_complex', fc,
                           '-map', '[o]', '-frames:v', '1', '-fps_mode', 'vfr', dst], capture_output=True, text=True)
    if done.returncode != 0 or not os.path.isfile(dst):
        print('sheetpair: ffmpeg rc %d %s' % (done.returncode, done.stderr.strip()[:200].encode('ascii', 'replace').decode()))
        return 1
    print('sheetpair: %s ref %d new %d step %d positions %s' % (dst, tr, tn, step, ','.join(str(p) for p in pos)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
