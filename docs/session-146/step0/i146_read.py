"""i146_read.py - session 146 step 0 (HPP-386): the reading of the warm-up tag i146_v (ROADMAP s122 item 300 (b)(3), item 309 (l)(1)):
V Sky Garden (-lvl underwater_aerial_garden) on the INSTALLED track F shipment binary dac02fb9 at its shipped defaults, in the form of
item 221 (g)(3): video KYTY_REC, sum dt_us of the shown frames after the first scene frame >= 300 s, >= 3000 shown frames after the
first scene frame, s51_vidglitch.py 4 6 - 0 glitches, 0 death markers, 0 frames dt >= 1 s after the first scene frame; the sheet for the
lead against fs_b (sheetpair_f3d.py: rec_fs_b.mp4 of FSc on top, i146_v below, the same frame positions) - the sheet is viewed by the
lead (acceptance row), so the reader prints only that the sheet exists.

The FSc reader is NOT copied and NOT changed: C:/kyty/f287/fsc/fs_read.py is imported after its sha256 is checked (FS_READ_SHA;
another sha -> rc 2), which itself imports C:/kyty/s142/sc142.py after its sha256 check.  Only the tag table, the root and the letter
members are replaced here (module attributes of the imported reader); the admission (binary sha = dac02fb9, no KYTY_FIX_*, no
KYTY_PIPELINE_PRECACHE, KYTY_GPU_CLOCK_PIN=1, video, --vulkan-validation false, no filter), the knob control (translation cache line
ends with variant_fixb26_fixb1b), the window event and the verdict order are those of fs_read.py.
Members of the executor [I] (printed, not the verdict): 0 BvhLoopCapTrip lines; video frames >= FrameTrace rows after the first scene
frame - 100 (coverage line of sc145); no scene change; game alive at the end of the hold.
Warm-up verdict: PASS -> the install stays; anything else -> WARMUP FAIL: the harness rolls back to the pinned 9235a7ac (sha checked)
and the question goes to the lead (item 300 (b), item 309 (l)(1)).

  python i146_read.py --tag i146_v [--root <dir>] [--json <out.json>]
  python i146_read.py --check-seal <pred.md>
ASCII only.  rc 0 - read; rc 1 - no log / no json; rc 2 - usage or a sha mismatch.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

ROOT = 'C:/kyty/s146'
FS_READ = 'C:/kyty/f287/fsc/fs_read.py'
REF = 'C:/kyty/f287/fsc/rec_fs_b.mp4'
TAG = 'i146_v'
SKY = 'underwater_aerial_garden'
ROWS_V = 3000
COVER_SLACK = 100


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


FS_READ_WANT = '2d5d41150d5bac29cfd2cdf6829bb9abc206d8d53cb65677bfab2a7b024639d8'


def load_fs(want=None):
    want = want or FS_READ_WANT
    got = sha_file(FS_READ)
    if got != want:
        raise SystemExit('sha mismatch %s: %s != %s' % (FS_READ, got, want))
    spec = importlib.util.spec_from_file_location('fs_read', FS_READ)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = ROOT
    mod.TAGS = {TAG: dict(level=SKY, letter='i', arm='V', knob=None, video=True, hold_sum=300, hold_wall=None, patched=False,
                          ref=REF)}
    mod.SEQ = (TAG,)
    mod.GATED = (TAG,)
    mod.letter_members = letter_members
    mod.exec_members = exec_members
    return mod


def letter_members(r):
    """Item 221 (g)(3), the V half - every member must hold."""
    g = r['glitch']
    return [
        ('sum dt after the first scene frame >= 300 s', r['hold_sum_s'] >= 300),
        ('>= %d shown frames after the first scene frame' % ROWS_V, r['frames_after_first'] >= ROWS_V),
        ('s51_vidglitch.py 4 6: 0 glitches', g is not None and g['glitches'] == 0),
        ('0 death markers', r['deaths'] == 0),
        ('0 frames dt >= 1 s after the first scene frame', r['k2'] == 0),
        ('sheet for the lead against fs_b %s exists' % r['sheet_name'], r['sheet']),
    ]


def exec_members(r):
    g = r['glitch']
    vf = g['video_frames'] if g else None
    return [
        ('0 BvhLoopCapTrip lines', r['trips'] == 0),
        ('video frames %s >= rows after the first scene frame %d - %d' % (vf, r['frames_after_first'], COVER_SLACK),
         vf is not None and vf >= r['frames_after_first'] - COVER_SLACK),
        ('no scene change', not r['scene_change']),
        ('game alive at the end of the hold (hold_exit None)', r['hold_exit'] is None),
    ]


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if '--check-seal' in a and a.index('--check-seal') + 1 < len(a):
        pred = a[a.index('--check-seal') + 1]
        rx = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
        ok, n = True, 0
        with open(pred, encoding='utf-8') as f:
            for line in f:
                m = rx.match(line.rstrip('\r\n'))
                if not m:
                    continue
                n += 1
                p = m.group(2) if m.group(2).startswith('C:/') else os.path.join(ROOT, m.group(2))
                now = sha_file(p) if os.path.isfile(p) else None
                good = now == m.group(1)
                ok &= good
                print('seal %s %s %s' % ('ok' if good else 'MISMATCH', m.group(2), (now or 'missing')[:16]))
        ok &= n >= 1
        print('check-seal %s (%d lines)' % ('OK' if ok else 'FAILED', n))
        return 0 if ok else 1
    if '--tag' not in a or a.index('--tag') + 1 >= len(a) or a[a.index('--tag') + 1] != TAG:
        print('usage: i146_read.py --tag i146_v [--json <out>] | --check-seal <pred>')
        return 2
    root = a[a.index('--root') + 1] if '--root' in a and a.index('--root') + 1 < len(a) else ROOT
    try:
        fs = load_fs()
        r = fs.read_tag(TAG, root)
    except SystemExit as e:
        print('refused: %s' % e)
        return 2
    if r is None:
        print('no log_%s.txt or %s.json in %s' % (TAG, TAG, root))
        return 1
    txt = fs.text(r).replace('letter p.282(g)(3)(i)', 'letter p.221(g)(3) V').replace('FS VERDICT', 'WARMUP VERDICT')
    txt = txt.replace('FS EXECUTOR MEMBERS', 'WARMUP EXECUTOR MEMBERS')
    print(txt)
    if '--json' in a:
        with open(a[a.index('--json') + 1], 'w', encoding='ascii') as f:
            json.dump(r, f, indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main())
