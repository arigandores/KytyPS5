"""sheet142.py <rec.mp4> <sheet.png> [cols=8] [rows=6] - one contact sheet of a whole video for the lead (session 142,
HPP-277; item 221 (g)(2)-(3): "the sheet is viewed by the lead").  cols*rows frames at even steps of the video's
frame count (ffprobe -count_frames), each scaled to 240 px wide, tiled into one PNG by ffmpeg.  Prints ASCII only:
"sheet: <png> frames <total> step <k> tiles <cols>x<rows>"; rc 1 when the video has no frames or ffmpeg fails.
"""
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


def main(argv):
    if len(argv) < 3:
        print('usage: sheet142.py <rec.mp4> <sheet.png> [cols] [rows]')
        return 2
    src, dst = argv[1], argv[2]
    cols = int(argv[3]) if len(argv) > 3 else 8
    rows = int(argv[4]) if len(argv) > 4 else 6
    total = frame_count(src)
    if total <= 0:
        print('sheet: %s has no frames' % src)
        return 1
    step = max(1, total // (cols * rows))
    vf = "select='not(mod(n\\,%d))',scale=240:-1,tile=%dx%d" % (step, cols, rows)
    done = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-vf', vf,
                           '-frames:v', '1', '-fps_mode', 'vfr', dst], capture_output=True, text=True)
    if done.returncode != 0:
        print('sheet: ffmpeg rc %d %s' % (done.returncode, done.stderr.strip()[:200].encode('ascii', 'replace').decode()))
        return 1
    print('sheet: %s frames %d step %d tiles %dx%d' % (dst, total, step, cols, rows))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
