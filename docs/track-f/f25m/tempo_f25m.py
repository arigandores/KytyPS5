"""F25m (HPP-680; ROADMAP s122 item 620 (g)(2), seal 2): the admission member 'scene tempo' of a made tag - frames of the scene per
second >= 10 (mean dt < 100 ms) from the line 'GuestOut: Level has started' to the end of the hold.  The reader f25m_read.py is not
changed; this is a separate admission tool called by post_f25m.sh after the reader.
Source by the form of the tag (named in seal 2):
  harness form (any 'FrameTrace: n=' line after the level line; tags b36_f*, b36_k*, b36_v, b36_w): mean dt_us of the FrameTrace frames
    whose line lies after the level line (sum dt_us / count); a row: flip records after the level line.
  user form (no FrameTrace after the level line; tags b36_s*): the flip records of the guest - lines starting with
    '\\t display_buffer_index' (the argument print of the flip call) after the level line - divided by the hold of enter_scene
    ('holding the run for <H> s' of run.txt; in the user form the hold starts at the level line); a row: LongFrame n / t_ms span
    after the level line (>= 2 lines).
Verdict: TEMPO PASS (mean dt < 100 000 us), TEMPO FAIL (mean dt > 100 000 us), TEMPO EDGE (mean dt == 100 000 us exactly: 'dt < 100 ms'
  says FAIL, '>= 10 fps' says PASS - both printed, stop and a question to the lead), TEMPO UNDETERMINED (no level line, 0 frames,
  no hold line in the user form).
EXIT: 0 PASS, 1 FAIL, 2 UNDETERMINED, 3 EDGE, 9 usage.  ASCII only.
usage: python tempo_f25m.py <log> <run.txt>"""
import os
import re
import sys

LIMIT_US = 100000
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_LF = re.compile(rb'^LongFrame: n=(\d+) dt_us=(\d+) log_async=(\d+) t_ms=(\d+)')
RX_HOLD = re.compile(r'holding the run for (\d+(?:\.\d+)?) s')
LEVEL = b'GuestOut: Level has started'
FLIP = b'\t display_buffer_index'


def scan(log_path):
    import lzma
    fh = lzma.open(log_path, 'rb') if log_path.endswith('.xz') else open(log_path, 'rb')
    r = dict(level=False, ft=[], flips=0, lf=[])
    with fh:
        for line in fh:
            if not r['level']:
                if line.startswith(LEVEL):
                    r['level'] = True
                continue
            if line.startswith(b'FrameTrace: n='):
                m = RX_FT.match(line)
                if m:
                    r['ft'].append(int(m.group(2)))
                continue
            if line.startswith(FLIP):
                r['flips'] += 1
                continue
            if line.startswith(b'LongFrame:'):
                m = RX_LF.match(line)
                if m:
                    r['lf'].append((int(m.group(1)), int(m.group(4))))
    return r


def hold_s(run_path):
    if not run_path or not os.path.isfile(run_path):
        return None
    h = None
    with open(run_path, 'r', encoding='ascii', errors='replace') as f:
        for line in f:
            m = RX_HOLD.search(line)
            if m:
                h = float(m.group(1))
    return h


def verdict(mean_us):
    if mean_us is None:
        return 'UNDETERMINED', 2
    if mean_us < LIMIT_US:
        return 'PASS', 0
    if mean_us > LIMIT_US:
        return 'FAIL', 1
    return 'EDGE', 3


def tempo(log_path, run_path):
    r = scan(log_path)
    if not r['level']:
        return dict(status='UNDETERMINED', rc=2, why='no level line', form=None, frames=0, mean_us=None, fps=None, rows=[])
    rows = []
    if r['ft']:
        form = 'harness'
        n = len(r['ft'])
        mean_us = sum(r['ft']) / n
        span_s = sum(r['ft']) / 1e6
        rows.append('flip records after the level line %d' % r['flips'])
        why = 'FrameTrace frames after the level line %d, span %.1f s' % (n, span_s)
    else:
        form = 'user'
        n = r['flips']
        h = hold_s(run_path)
        if h is None or h <= 0:
            return dict(status='UNDETERMINED', rc=2, why='user form without the hold line of run.txt', form=form, frames=n,
                        mean_us=None, fps=None, rows=rows)
        if n == 0:
            return dict(status='UNDETERMINED', rc=2, why='user form: 0 flip records after the level line', form=form, frames=0,
                        mean_us=None, fps=None, rows=rows)
        mean_us = h * 1e6 / n
        why = 'flip records after the level line %d over the hold %.1f s' % (n, h)
        if len(r['lf']) >= 2:
            (n0, t0), (n1, t1) = r['lf'][0], r['lf'][-1]
            if t1 > t0 and n1 > n0:
                rows.append('LongFrame span n %d..%d over %.1f s: %.2f fps (row)' % (n0, n1, (t1 - t0) / 1e3, (n1 - n0) * 1e3 / (t1 - t0)))
            else:
                rows.append('LongFrame span: no time span (row)')
        else:
            rows.append('LongFrame lines after the level line %d (< 2, no span row)' % len(r['lf']))
    st, rc = verdict(mean_us)
    return dict(status=st, rc=rc, why=why, form=form, frames=n, mean_us=mean_us, fps=1e6 / mean_us if mean_us else None, rows=rows)


def main(argv):
    if len(argv) not in (1, 2):
        print(__doc__.splitlines()[-1])
        return 9
    t = tempo(argv[0], argv[1] if len(argv) == 2 else None)
    if t['mean_us'] is None:
        print('TEMPO %s form %s frames %d (%s)' % (t['status'], t['form'], t['frames'], t['why']))
    else:
        extra = ''
        if t['status'] == 'EDGE':
            extra = '; edge: dt < 100 ms -> FAIL, >= 10 fps -> PASS (stop, question to the lead)'
        print('TEMPO %s form %s mean_dt_ms %.2f fps %.2f frames %d (%s)%s' % (
            t['status'], t['form'], t['mean_us'] / 1e3, t['fps'], t['frames'], t['why'], extra))
    for row in t['rows']:
        print('  row: %s' % row)
    return t['rc']


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
