# Red Team s142 step 1: an independent reading of the five calibration logs (item 221 (g)(4)) and of the s137
# validation log s6s137 - own line parser (not sc142.scan): first scene frame, K2, K3 window / hold, torn FrameTrace
# lines, n gaps and repeats after the entry, validation-layer evidence lines.  Binary, streaming, line by line.
import re, hashlib, sys
LOGS = (('eatl122', 'C:/kyty/s122/log_eatl122.txt', 'penguin_atlantis'),
        ('edes122', 'C:/kyty/s122/log_edes122.txt', 'intro_next'),
        ('atl122', 'C:/kyty/s122/log_atl122.txt', 'penguin_atlantis'),
        ('ednn122', 'C:/kyty/s122/log_ednn122.txt', 'rotating_level_day_and_night'),
        ('eght122', 'C:/kyty/s122/log_eght122.txt', 'time_stopper_ghost_world'),
        ('s6s137', 'C:/kyty/s137/log_s6s137.txt', 'underwater_aerial_garden'))
RX = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) .*? draws=(\d+) ')
EV = (b'no validation layer:', b'VK_LAYER_KHRONOS_validation available extension:', b'[Vulkan][W]', b'[Vulkan][E]',
      b'[Vulkan][I]', b'Vulkan available layer: VK_LAYER_KHRONOS_validation', b'Event: quit')
for tag, path, level in LOGS:
    h = hashlib.sha256()
    start = ('GuestOut: Level has started: ' + level).encode()
    entered = False
    rows = []
    ftany = torn = 0
    ev = dict((k, 0) for k in EV)
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            if b'FrameTrace: n=' in line:
                ftany += 1
                m = RX.match(line)
                if not m:
                    torn += 1
                elif entered:
                    rows.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
            elif not entered and line.rstrip(b'\r\n').endswith(start) and b'GuestOut: Level has started: ' in line:
                entered = True
            for k in EV:
                if k in line:
                    ev[k] += 1
    fi = next((i for i, r in enumerate(rows) if r[2] >= 100), None)
    post = rows[fi + 1:] if fi is not None else []
    win, hold = post[:599], post[599:]
    k2 = [(r[0], r[1], 'entry' if j < 599 else 'hold') for j, r in enumerate(post) if r[1] >= 1000000]
    k3w = [r[0] for r in win if 100000 <= r[1] < 1000000]
    k3h = [r[0] for r in hold if 100000 <= r[1] < 1000000]
    gaps = sum(1 for a, b in zip(post, post[1:]) if b[0] != a[0] + 1)
    print('%s sha %s entered %s first %s rows_after_first %d sum_dt_after_first %.1f s K2 %s K3w %s K3h %s'
          % (tag, h.hexdigest()[:16], entered, rows[fi] if fi is not None else None, len(post),
             sum(r[1] for r in post) / 1e6, k2 or 'none', k3w or 'none', k3h or 'none'))
    print('   FrameTrace lines %d torn (no ^FrameTrace: n= dt_us= draws= parse) %d; n gaps after first %d; last row %s'
          % (ftany, torn, gaps, post[-1] if post else None))
    print('   ' + '; '.join('%s %d' % (k.decode(), v) for k, v in ev.items()))
    sys.stdout.flush()
