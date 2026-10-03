"""F13a (HPP-479): the sheet of the frames around each press of f13_k for the lead and F13b - one row per press, columns at the video
frame of the press + OFFSETS (frames of the 60 Hz recording: -1 s, +0.5 s, +2 s, +5 s, +9 s), each 240 px wide.
usage: python press_sheet.py <read.json> <rec.mp4> <out.png>      prints 'press_sheet: <png> rows <n> frames <list>' (ASCII); rc 1 on
no press / ffmpeg failure."""
import json, subprocess, sys

OFFSETS = (-60, 30, 120, 300, 540)


def main(argv):
    res = json.load(open(argv[1]))
    frames = []
    for p in res.get('presses', []):
        if p.get('video_frame') is None:
            continue
        frames += [max(0, p['video_frame'] + o) for o in OFFSETS]
    if not frames:
        print('press_sheet: no press with a video frame')
        return 1
    sel = '+'.join('eq(n\\,%d)' % f for f in frames)
    rows = len(frames) // len(OFFSETS)
    vf = "select='%s',scale=240:-1,tile=%dx%d" % (sel, len(OFFSETS), rows)
    done = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', argv[2], '-vf', vf, '-frames:v', '1',
                           '-fps_mode', 'vfr', argv[3]], capture_output=True, text=True)
    if done.returncode != 0:
        print('press_sheet: ffmpeg rc %d %s' % (done.returncode, done.stderr.strip()[:200].encode('ascii', 'replace').decode()))
        return 1
    print('press_sheet: %s rows %d frames %s' % (argv[3], rows, ','.join(str(f) for f in frames)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
