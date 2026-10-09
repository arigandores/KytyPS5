"""FS11c (HPP-716): the F25m tempo tool copied unchanged (names only); F25m (HPP-716; ROADMAP s122 item 620 (g)(2), seal 2; item 621, seal 2a): the admission member 'scene tempo' of a made tag - mean dt
of the scene frames from the line 'GuestOut: Level has started' to the end of the hold below the limit of the form.  The reader
f25m_read.py is not changed; this is a separate admission tool called by post_fs11c.sh after the reader.
Limit by the form of the launch (item 621):
  W form (the seal plan launches the tag with '--vulkan-validation true'; post_fs11c.sh gives --plan-w yes from the dry run of go_fs11c.sh,
    not from the tag name): mean dt < 200 000 us (>= 5 fps).  The launch arguments of the run json (the last '--vulkan-validation' of
    'cmdline') must agree with the plan, else TEMPO UNDETERMINED.
  any other form (--plan-w no): mean dt < 100 000 us (>= 10 fps), item 620 (g)(2).
Source by the form of the tag (named in seal 2; the W form uses the harness source):
  harness form (any 'FrameTrace: n=' line after the level line; tags b36_f*, b36_k*, b36_v, b36_w): mean dt_us of the FrameTrace frames
    whose line lies after the level line (sum dt_us / count); a row: flip records after the level line.
  user form (no FrameTrace after the level line; tags b36_s*): the flip records of the guest - lines starting with
    '\\t display_buffer_index' (the argument print of the flip call) after the level line - divided by the hold of enter_scene
    ('holding the run for <H> s' of run.txt; in the user form the hold starts at the level line); a row: LongFrame n / t_ms span
    after the level line (>= 2 lines).
Verdict: TEMPO PASS (mean dt < limit), TEMPO FAIL (mean dt > limit), TEMPO EDGE (mean dt == limit exactly: 'dt < limit' says FAIL,
  '>= fps' says PASS - both printed, stop and a question to the lead), TEMPO UNDETERMINED (no level line, 0 frames, no hold line in the
  user form, the plan and the launch arguments disagree, no or bad run json with --plan-w yes).
EXIT: 0 PASS, 1 FAIL, 2 UNDETERMINED, 3 EDGE, 9 usage.  ASCII only.
usage: python tempo_f25m.py <log> <run.txt> [--plan-w yes|no] [--json <run json>]"""
import json
import os
import re
import sys

LIMIT_US = 100000
LIMIT_W_US = 200000
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


def last_flag(cmd, flag):
    v = None
    for i, x in enumerate(cmd or []):
        if x == flag and i + 1 < len(cmd):
            v = cmd[i + 1]
    return v


def json_vv(json_path):
    """The last '--vulkan-validation' value of the run json cmdline; ('error', why) when it cannot be read."""
    if not json_path or not os.path.isfile(json_path):
        return 'error', 'no run json %s' % json_path
    try:
        cmd = json.load(open(json_path, encoding='utf-8')).get('cmdline')
    except Exception as e:  # noqa: BLE001
        return 'error', 'run json not read (%s)' % type(e).__name__
    if not isinstance(cmd, list) or not cmd:
        return 'error', 'run json without cmdline'
    return 'ok', last_flag(cmd, '--vulkan-validation')


def verdict(mean_us, limit_us=LIMIT_US):
    if mean_us is None:
        return 'UNDETERMINED', 2
    if mean_us < limit_us:
        return 'PASS', 0
    if mean_us > limit_us:
        return 'FAIL', 1
    return 'EDGE', 3


def undet(why, form, frames, wform, limit_us, rows=None):
    return dict(status='UNDETERMINED', rc=2, why=why, form=form, frames=frames, mean_us=None, fps=None, rows=rows or [], wform=wform,
                limit_us=limit_us)


def tempo(log_path, run_path, plan_w=False, json_path=None):
    """plan_w: the seal plan launches the tag with --vulkan-validation true (item 621).  json_path: the run json; with plan_w it is
    required and its last --vulkan-validation must be 'true'; without plan_w, when given, it must not be 'true'."""
    limit_us = LIMIT_W_US if plan_w else LIMIT_US
    if plan_w or json_path:
        st, vv = json_vv(json_path)
        if st == 'error':
            if plan_w:
                return undet('W form: %s' % vv, None, 0, plan_w, limit_us)
        elif (vv == 'true') != bool(plan_w):
            return undet('the plan (W %s) and the launch arguments (--vulkan-validation %s) disagree' % ('yes' if plan_w else 'no', vv),
                         None, 0, plan_w, limit_us)
    r = scan(log_path)
    if not r['level']:
        return undet('no level line', None, 0, plan_w, limit_us)
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
            return undet('user form without the hold line of run.txt', form, n, plan_w, limit_us, rows)
        if n == 0:
            return undet('user form: 0 flip records after the level line', form, 0, plan_w, limit_us, rows)
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
    st, rc = verdict(mean_us, limit_us)
    return dict(status=st, rc=rc, why=why, form=form, frames=n, mean_us=mean_us, fps=1e6 / mean_us if mean_us else None, rows=rows,
                wform=plan_w, limit_us=limit_us)


def parse(argv):
    pos, plan_w, jp = [], False, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--plan-w':
            if i + 1 >= len(argv) or argv[i + 1] not in ('yes', 'no'):
                return None
            plan_w = argv[i + 1] == 'yes'
            i += 2
        elif a == '--json':
            if i + 1 >= len(argv):
                return None
            jp = argv[i + 1]
            i += 2
        elif a.startswith('--'):
            return None
        else:
            pos.append(a)
            i += 1
    if len(pos) not in (1, 2):
        return None
    return pos[0], (pos[1] if len(pos) == 2 else None), plan_w, jp


def main(argv):
    a = parse(argv)
    if a is None:
        print(__doc__.splitlines()[-1])
        return 9
    t = tempo(a[0], a[1], plan_w=a[2], json_path=a[3])
    lim = 'limit_ms %d (%s)' % (t['limit_us'] // 1000, 'W form, item 621' if t['wform'] else 'item 620 (g)(2)')
    if t['mean_us'] is None:
        print('TEMPO %s form %s frames %d %s (%s)' % (t['status'], t['form'], t['frames'], lim, t['why']))
    else:
        extra = ''
        if t['status'] == 'EDGE':
            extra = '; edge: dt < %d ms -> FAIL, >= %d fps -> PASS (stop, question to the lead)' % (
                t['limit_us'] // 1000, 1000000 // t['limit_us'])
        print('TEMPO %s form %s mean_dt_ms %.2f fps %.2f frames %d %s (%s)%s' % (
            t['status'], t['form'], t['mean_us'] / 1e3, t['fps'], t['frames'], lim, t['why'], extra))
    for row in t['rows']:
        print('  row: %s' % row)
    return t['rc']


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
