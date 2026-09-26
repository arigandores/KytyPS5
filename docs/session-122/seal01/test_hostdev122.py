#!/usr/bin/env python3
"""Offline fixtures for hostdev122.py - one per member of the verdict and one
per edge. No machine state, no Windows log, no game: safe to run while the
machine is busy. Ends with `ALL OK`."""

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import hostdev122 as H  # noqa: E402

FAILS = []
CHECKS = [0]


def check(name, got, want):
    CHECKS[0] += 1
    if got != want:
        FAILS.append('%s: got %r want %r' % (name, got, want))


def T(s):
    return dt.datetime(2026, 9, 26, 21, 30, 0) + dt.timedelta(seconds=s)


def ev(provider, eid=2, at=24, msg='m'):
    return {'provider': provider, 'id': eid, 'time': T(at).isoformat(), 'message': msg}


# ---------------------------------------------------------------- parse_ts
check('ts iso', H.parse_ts('2026-09-26T21:28:54'), dt.datetime(2026, 9, 26, 21, 28, 54))
check('ts space', H.parse_ts('2026-09-26 21:28:54'), dt.datetime(2026, 9, 26, 21, 28, 54))
check('ts nvidia', H.parse_ts('2026/09/26 21:28:54.196'),
      dt.datetime(2026, 9, 26, 21, 28, 54, 196000))
check('ts nvidia no frac', H.parse_ts('2026/09/26 21:28:54'),
      dt.datetime(2026, 9, 26, 21, 28, 54))
check('ts none', H.parse_ts(None), None)
check('ts empty', H.parse_ts('   '), None)
check('ts junk', H.parse_ts('yesterday'), None)

# ---------------------------------------------------------------- run_window
w = H.run_window({'launched': '2026-09-26T21:28:54', 'finished': '2026-09-26T21:31:32'}, pad_s=10)
check('window start', w[0], dt.datetime(2026, 9, 26, 21, 28, 44))
check('window end', w[1], dt.datetime(2026, 9, 26, 21, 31, 42))
check('window no pad', H.run_window({'launched': '2026-09-26T21:28:54',
                                     'finished': '2026-09-26T21:31:32'}, pad_s=0)[0],
      dt.datetime(2026, 9, 26, 21, 28, 54))
# `started` is written at the END of the run - it must not be taken as a start.
w2 = H.run_window({'started': '2026-09-26T21:31:32', 'launched': '2026-09-26T21:28:54',
                   'finished': '2026-09-26T21:31:32'}, pad_s=0)
check('window prefers launched', w2[0], dt.datetime(2026, 9, 26, 21, 28, 54))
# finished missing -> fall back to started, and swap if reversed.
w3 = H.run_window({'launched': '2026-09-26T21:31:32', 'started': '2026-09-26T21:28:54'}, pad_s=0)
check('window swapped', (w3[0].second, w3[1].second), (54, 32))
check('window missing', H.run_window({}, pad_s=0), None)
check('window only start', H.run_window({'launched': '2026-09-26T21:28:54'}, pad_s=0), None)

# ---------------------------------------------------------------- classify
c = H.classify([ev('HidBth'), ev('Microsoft-Windows-Kernel-PnP', 411),
                ev('Service Control Manager', 7040), ev('nvlddmkm', 153),
                ev('BTHUSB', 17), ev('BthLEEnum', 12), ev('BTHPORT', 8)])
check('classify hidbth', c[0]['severity'], H.SEV_FATAL)
check('classify pnp', c[1]['severity'], H.SEV_WARN)
check('classify other', c[2]['severity'], H.SEV_INFO)
check('classify nvlddmkm', c[3]['severity'], H.SEV_FATAL)
check('classify bthusb', c[4]['severity'], H.SEV_FATAL)
check('classify bthleenum', c[5]['severity'], H.SEV_FATAL)
check('classify bthport', c[6]['severity'], H.SEV_FATAL)
check('classify lowers provider', c[0]['provider'], 'hidbth')
check('classify parses time', c[0]['time'], T(24))
check('classify keeps datetime', H.classify([{'provider': 'HidBth', 'id': 2,
                                              'time': T(24), 'message': ''}])[0]['time'], T(24))
check('classify bad time', H.classify([ev('HidBth', 2, msg='')] and
                                      [{'provider': 'HidBth', 'id': 2, 'time': 'x'}])[0]['time'],
      None)
check('classify empty', H.classify([]), [])

# ---------------------------------------------------------------- build_ps_query
# The brace trap: this string is full of PowerShell hashtables, so it must never
# go through str.format. Assert it is emitted verbatim.
q = H.build_ps_query(dt.datetime(2026, 9, 26, 21, 28, 44), dt.datetime(2026, 9, 26, 21, 31, 42))
check('ps start', "Get-Date '2026-09-26 21:28:44'" in q, True)
check('ps end', "Get-Date '2026-09-26 21:31:42'" in q, True)
check('ps hashtable intact', "@{LogName='System';StartTime=$a;EndTime=$b}" in q, True)
check('ps braces balanced', q.count('{'), q.count('}'))
check('ps no stray format field', '{a}' in q or '{b}' in q, False)
check('ps json', 'ConvertTo-Json -Compress' in q, True)

# ---------------------------------------------------------------- idle_windows
busy = [(T(i), 60) for i in range(0, 25)]
idle = [(T(i), 6) for i in range(25, 49)]
tail = [(T(i), 80) for i in range(49, 60)]
wins = H.idle_windows(busy + idle + tail)
check('one idle window', len(wins), 1)
check('idle start', wins[0][0], T(25))
check('idle end', wins[0][1], T(48))
check('idle dur', round(wins[0][2], 1), 23.0)
check('short idle ignored', H.idle_windows(busy + [(T(25), 6), (T(26), 6)] + tail), [])
check('boundary util_max inclusive', len(H.idle_windows([(T(i), 15) for i in range(0, 10)],
                                                        util_max=15, min_s=3.0)), 1)
check('boundary util_max exclusive above', H.idle_windows([(T(i), 16) for i in range(0, 10)],
                                                          util_max=15, min_s=3.0), [])
check('trailing idle window kept', len(H.idle_windows(busy + idle)), 1)
check('all idle reported', len(H.idle_windows(idle)), 1)
check('no samples', H.idle_windows([]), [])
check('min_s boundary', len(H.idle_windows([(T(0), 5), (T(3), 5)], min_s=3.0)), 1)
check('min_s below', H.idle_windows([(T(0), 5), (T(2), 5)], min_s=3.0), [])

# ---------------------------------------------------------------- correlate
events = H.classify([ev('HidBth', 2, 24), ev('Service Control Manager', 7040, 24)])
pairs = H.correlate(events, wins, tol_s=5.0)
check('correlated one', len(pairs), 1)
check('correlated is fatal', pairs[0][0]['provider'], 'hidbth')
check('correlate tolerance edge', len(H.correlate(H.classify([ev('HidBth', 2, 20)]),
                                                 wins, tol_s=5.0)), 1)
check('correlate one second before edge', H.correlate(H.classify([ev('HidBth', 2, 19)]),
                                                      wins, tol_s=5.0), [])
check('correlate outside tolerance', H.correlate(H.classify([ev('HidBth', 2, 10)]),
                                                wins, tol_s=5.0), [])
check('correlate no windows', H.correlate(events, [], tol_s=5.0), [])
check('correlate skips info', H.correlate(H.classify([ev('Service Control Manager', 7040, 30)]),
                                          wins), [])
check('correlate null time', H.correlate(H.classify([{'provider': 'HidBth', 'id': 2,
                                                      'time': 'x'}]), wins), [])

# ---------------------------------------------------------------- verdict
check('verdict invalid', H.verdict(events, wins, [(4945, 23796476)])[0], 'RUN_INVALID')
check('verdict unattributed', H.verdict(H.classify([]), wins, [])[0], 'STALL_UNATTRIBUTED')
check('verdict unattributed by dt', H.verdict(H.classify([]), [], [(4945, 23796476)])[0],
      'STALL_UNATTRIBUTED')
check('verdict clean', H.verdict(H.classify([]), [], [])[0], 'RUN_CLEAN')
check('verdict clean with info event',
      H.verdict(H.classify([ev('Service Control Manager', 7040)]), [], [])[0], 'RUN_CLEAN')
check('verdict warn only is not invalid',
      H.verdict(H.classify([ev('Microsoft-Windows-Kernel-PnP', 411)]), [], [])[0], 'RUN_CLEAN')
check('verdict not evaluable', H.verdict(None, [], [])[0], 'NOT EVALUABLE')
check('verdict not evaluable wins over stall', H.verdict(None, wins, [(1, 2)])[0],
      'NOT EVALUABLE')

# ---------------------------------------------------------------- dt_outliers + csv + cli
tmp = tempfile.mkdtemp(prefix='hostdev122_')
log = os.path.join(tmp, 'log_t.txt')
with open(log, 'wb') as f:
    f.write(b'FrameTrace: n=1 dt_us=16700 draws=5\n')
    f.write(b'FrameTrace-x: n=1 dt_us=99999999 junk=1\n')  # must not match: wrong stream
    f.write(b'FrameTrace: n=2 dt_us=100000 draws=5\n')      # boundary: >= min_us
    f.write(b'FrameTrace: n=3 dt_us=23796476 draws=0\n')
    f.write(b'  FrameTrace: n=4 dt_us=50000000 draws=0\n')  # indented: not a report line
out = H.dt_outliers(log, 100000)
check('dt outliers', out, [(2, 100000), (3, 23796476)])
check('dt outliers high threshold', H.dt_outliers(log, 30000000), [])

check('dt outliers min_frame', H.dt_outliers(log, 100000, 3), [(3, 23796476)])
check('dt outliers min_frame above all', H.dt_outliers(log, 100000, 99), [])
check('dt outliers min_frame boundary', H.dt_outliers(log, 100000, 2), [(2, 100000),
                                                                       (3, 23796476)])

check('stable_frame', H.stable_frame({'attempts': [{'outcome': 'ok', 'stable_frame': 1507}]}), 1507)
check('stable_frame skips failed', H.stable_frame(
    {'attempts': [{'outcome': 'hold_exit', 'stable_frame': 900},
                  {'outcome': 'ok', 'stable_frame': 1507}]}), 1507)
check('stable_frame none', H.stable_frame({}), 0)
check('stable_frame null attempts', H.stable_frame({'attempts': None}), 0)
check('stable_frame missing field', H.stable_frame({'attempts': [{'outcome': 'ok'}]}), 0)

# trim_to_busy: the idle tails of start-up and shut-down are not stalls.
lead = [(T(-10 + i), 5) for i in range(0, 8)]
trail = [(T(60 + i), 5) for i in range(0, 8)]
check('trim keeps middle idle', len(H.idle_windows(H.trim_to_busy(lead + busy + idle + tail + trail))), 1)
check('trim drops tails', len(H.idle_windows(H.trim_to_busy(lead + busy + tail + trail))), 0)
check('trim all idle', H.trim_to_busy(lead), [])
check('trim empty', H.trim_to_busy([]), [])
check('trim single busy', H.trim_to_busy([(T(0), 5), (T(1), 90), (T(2), 5)]), [(T(1), 90)])

csvp = os.path.join(tmp, 'gpuclk_t.csv')
with open(csvp, 'w', newline='') as f:
    f.write('timestamp, clocks.current.sm [MHz], clocks.current.memory [MHz], utilization.gpu [%]\n')
    for i in range(0, 25):
        f.write('2026/09/26 21:30:%02d.000, 2500 MHz, 14001 MHz, 60 %%\n' % i)
    for i in range(25, 49):
        f.write('2026/09/26 21:30:%02d.000, 1900 MHz, 14001 MHz, 6 %%\n' % i)
    f.write('2026/09/26 21:30:49.000, 2600 MHz, 14001 MHz, 98 %\n')
sam = H.read_gpu_csv(csvp)
check('csv rows', len(sam), 50)
check('csv header skipped', sam[0][0], dt.datetime(2026, 9, 26, 21, 30, 0))
check('csv util', sam[30][1], 6)
check('csv idle window', round(H.idle_windows(sam)[0][2], 1), 23.0)
check('csv short row ignored', H.read_gpu_csv(log), [])

evp = os.path.join(tmp, 'events.json')
with open(evp, 'w') as f:
    json.dump([ev('HidBth', 2, 24, 'Bluetooth HID device went out of range')], f)
runp = os.path.join(tmp, 't.json')
with open(runp, 'w') as f:
    json.dump({'tag': 't', 'launched': '2026-09-26T21:28:54',
               'finished': '2026-09-26T21:31:32'}, f)
res = subprocess.run([sys.executable, os.path.join(HERE, 'hostdev122.py'), 't',
                      '--dir', tmp, '--events-json', evp],
                     capture_output=True, text=True)
check('cli rc', res.returncode, 1)
check('cli verdict', 'VERDICT: RUN_INVALID' in res.stdout, True)
check('cli correlated', 'CORRELATED hidbth/2' in res.stdout, True)
check('cli stall frame', 'STALL frame n=3 dt_us=23796476' in res.stdout, True)

with open(evp, 'w') as f:
    json.dump([], f)
os.remove(log)
os.remove(csvp)
res = subprocess.run([sys.executable, os.path.join(HERE, 'hostdev122.py'), 't',
                      '--dir', tmp, '--events-json', evp],
                     capture_output=True, text=True)
check('cli clean rc', res.returncode, 0)
check('cli clean verdict', 'VERDICT: RUN_CLEAN' in res.stdout, True)

res = subprocess.run([sys.executable, os.path.join(HERE, 'hostdev122.py'), 'missing',
                      '--dir', tmp, '--events-json', evp],
                     capture_output=True, text=True)
check('cli no run json', 'window UNKNOWN' in res.stdout, True)

print('checks: %d' % CHECKS[0])
if FAILS:
    for f in FAILS:
        print('FAIL ' + f)
    sys.exit(1)
print('ALL OK')
