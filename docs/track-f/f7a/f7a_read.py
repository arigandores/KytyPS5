"""f7a_read.py - F7a (HPP-397; ROADMAP p.327(e)): the reader of one RenderDoc capture run of enemy_final (and of the reference log
for the frame choice).  Reads the log in binary mode, line by line; prints ASCII only (p.175(v)).
  python f7a_read.py <log> [--level enemy_final]
Lines printed (the last line starts with 'F7A READ'):
  entry          - 'Level has started: <level>' lines; FrameTrace n of the last row before the first such line (n_entry)
  first scene    - the first FrameTrace row after the entry line with draws >= 100 (the rule of sc145/sc146, item 218 (g)): n_fs
  renderdoc      - 'RenderDoc: API 1.6.0 bound', 'level started at frame X, capture at frame Y', 'auto capture at frame Z (level+N)',
                   'capture started', 'captured guest flip k/m', 'capture finished' / 'capture failed' / 'unavailable';
                   for each: the FrameTrace n of the last row before the line (the presented-frame counter of the log);
  capture place  - FrameTrace n before 'capture started' minus n_fs (frames after the first scene frame) and the sum of dt_us
                   from the first scene frame to that row (seconds of scene before the capture);
  deaths / window - 'Unhandled exception:', '--- Fatal Error ---', 'GpuHangAbort:', 'ErrorDeviceLost', 'DEVICE_LOST',
                   'Window <id> minimized', 'Recovering Vulkan swapchain' line counts;
  defaults       - 'DualSrcBlend: supported=1 enabled=1' and 'FixB9a: on' line counts (information: the defaults of dac02fb9).
exit 0 always when the log is readable (the verdict is in the text), 2 on a missing log.
"""
import re
import sys

RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) .*? draws=(\d+) ')
RX_LS = re.compile(rb'RenderDoc: level started at frame (\d+), capture at frame (\d+)')
RX_AC = re.compile(rb'RenderDoc: auto capture at frame (\d+) \((?:level\+(\d+)|KYTY_RD_FRAME=(-?\d+))\)')
RX_FLIP = re.compile(rb'RenderDoc: captured guest flip (\d+)/(\d+)')
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'GpuHangAbort:', b'ErrorDeviceLost', b'DEVICE_LOST')
RX_WIN = re.compile(rb'Window \d+ minimized|Recovering Vulkan swapchain')


def read(lines, level='enemy_final'):
    """lines: iterable of bytes lines -> dict of the reading."""
    entry_key = b'Level has started: ' + level.encode('ascii')
    r = dict(entries=0, n_entry=None, n_fs=None, fs_dt=None, bound=0, level_started=None, auto=None, started=[], flips=[],
             finished=[], failed=0, unavailable=0, deaths=0, window=0, dualsrc=0, fixb9a=0, rows=0, cum_to=None)
    last_n = None
    cum = 0
    after_fs = False
    cap_row = None
    for l in lines:
        if l.startswith(b'FrameTrace: n='):
            m = RX_FT.match(l)
            if not m:
                continue
            n, dt, dr = int(m.group(1)), int(m.group(2)), int(m.group(3))
            r['rows'] += 1
            last_n = n
            if r['entries'] and r['n_fs'] is None and dr >= 100:
                r['n_fs'] = n
                r['fs_dt'] = dt
                after_fs = True
                cum = 0
            if after_fs and (not r['started'] or cap_row is None):
                cum += dt
            continue
        if entry_key in l:
            r['entries'] += 1
            if r['entries'] == 1:
                r['n_entry'] = last_n
            continue
        if b'RenderDoc:' in l:
            if b'API 1.6.0 bound' in l:
                r['bound'] += 1
            m = RX_LS.search(l)
            if m:
                r['level_started'] = (int(m.group(1)), int(m.group(2)), last_n)
            m = RX_AC.search(l)
            if m:
                rel = m.group(2) if m.group(2) is not None else m.group(3)
                r['auto'] = (int(m.group(1)), rel.decode('ascii'), last_n)
            if b'capture started' in l:
                r['started'].append(last_n)
                if cap_row is None and after_fs:
                    cap_row = last_n
                    r['cum_to'] = cum
            m = RX_FLIP.search(l)
            if m:
                r['flips'].append((int(m.group(1)), int(m.group(2)), last_n))
            if b'capture finished' in l:
                r['finished'].append(last_n)
            if b'capture failed' in l:
                r['failed'] += 1
            if b'unavailable' in l:
                r['unavailable'] += 1
            continue
        if any(d in l for d in DEATH):
            r['deaths'] += 1
        if RX_WIN.search(l):
            r['window'] += 1
        if b'DualSrcBlend: supported=1 enabled=1' in l:
            r['dualsrc'] += 1
        if b'FixB9a: on' in l:
            r['fixb9a'] += 1
    r['cap_row'] = cap_row
    return r


def verdict(r):
    """-> (word, text)."""
    entered = r['entries'] > 0 and r['n_fs'] is not None
    done = bool(r['started']) and bool(r['finished']) and r['failed'] == 0
    if not entered:
        word = 'NOT_ENTERED'
    elif r['deaths'] or r['window']:
        word = 'DEATH_OR_WINDOW'
    elif done:
        word = 'CAPTURED'
    else:
        word = 'NO_CAPTURE'
    place = 'n/a'
    if r['cap_row'] is not None and r['n_fs'] is not None:
        place = '%d presented frames after the first scene frame (%.2f s of dt_us from it)' % (
            r['cap_row'] - r['n_fs'], (r['cum_to'] or 0) / 1e6)
    text = ('entered %s (entry lines %d, FrameTrace n before the entry %s, first scene frame n=%s); rd bound %d; '
            'level started %s; auto capture %s; capture started at FrameTrace n %s; flips %s; finished at %s; failed %d; '
            'unavailable %d; capture place: %s; deaths %d; window %d; DualSrcBlend on %d; FixB9a on %d; FrameTrace rows %d' % (
                'yes' if entered else 'no', r['entries'], r['n_entry'], r['n_fs'], r['bound'],
                ('gpu frame %d, target %d (FrameTrace n %s)' % r['level_started']) if r['level_started'] else 'none',
                ('gpu frame %d (level+%s) (FrameTrace n %s)' % r['auto']) if r['auto'] else 'none',
                r['started'] or 'none', ['%d/%d@%s' % f for f in r['flips']] or 'none', r['finished'] or 'none',
                r['failed'], r['unavailable'], place, r['deaths'], r['window'], r['dualsrc'], r['fixb9a'], r['rows']))
    return word, text


def main(argv):
    if not argv:
        print('usage: f7a_read.py <log> [--level enemy_final]')
        return 2
    level = 'enemy_final'
    if '--level' in argv:
        level = argv[argv.index('--level') + 1]
    try:
        with open(argv[0], 'rb') as f:
            r = read(f, level)
    except OSError as e:
        print('F7A READ %s: NO_LOG (%s)' % (argv[0], type(e).__name__))
        return 2
    word, text = verdict(r)
    print('F7A READ %s: %s; %s' % (argv[0], word, text))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
