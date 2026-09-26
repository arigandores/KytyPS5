#!/usr/bin/env python3
"""hostdev122 - witness of HOST device events inside a run window.

Session 122, HPP-10. The 23.8 s stall of `edes122` (frame 4945, dt_us=23 796 476)
was attributed by the user to a Bluetooth gamepad that was switched off during the
run. Three independent witnesses agree, so the attribution is not a guess:

  1. `_kyty.txt`  - exactly one wall-clock gap in the whole log: 23.809 s
                    (t=90.075 -> t=113.884), plus `MainTaskLate: us=23812688`
                    (the main thread did not service its queue for that long).
  2. gpuclk csv   - GPU utilisation 50..97 % until 21:30:24.733, then 6..9 %
                    until 21:30:48.568 -> the GPU was IDLE: a host stall, not a
                    GPU hang and not a TDR.
  3. Windows      - System log, provider `HidBth`, id 2, Warning, 21:30:24:
     System log     "Bluetooth HID device either went out of range or became
                    unresponsive." - the same second the GPU went idle.

This module is the reusable part: any run (sealed above all) can be asked
whether a host device event fell inside its window, so a stalled frame can never
be silently absorbed into a measured population.

Pure functions (`classify`, `idle_windows`, `dt_outliers`, `correlate`,
`verdict`) take data, never the machine, and are covered by
`test_hostdev122.py` offline.

Usage:
  python hostdev122.py <tag> [--dir C:/kyty/s122] [--pad 10]
  python hostdev122.py <tag> --events-json <file>   # offline / replay
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys

# Providers whose event inside a run window invalidates the run: the host input
# or GPU stack changed state under the measurement.
FATAL_PROVIDERS = {
    'hidbth',       # Bluetooth HID out of range / unresponsive (this session)
    'hidbthle',
    'bthusb',       # Bluetooth radio / transport
    'bthport',
    'bthleenum',
    'btha2dp',
    'bthhfenum',
    'nvlddmkm',     # display driver: 153 = GPU hang / reset
    'amdkmdag',
    'display',
}

# Providers worth reporting but not fatal by themselves.
WARN_PROVIDERS = {
    'microsoft-windows-kernel-pnp',
    'microsoft-windows-kernel-power',
    'usb',
    'usbhub3',
    'ucx01000',
    'disk',
    'volmgr',
}

SEV_FATAL = 'FATAL'
SEV_WARN = 'WARN'
SEV_INFO = 'INFO'


# ---------------------------------------------------------------- run window


def parse_ts(text):
    """Accept the two stamp shapes the harness writes, return naive datetime."""
    if text is None:
        return None
    text = str(text).strip()
    if not text:
        return None
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S.%f', '%Y/%m/%d %H:%M:%S'):
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def run_window(run_json, pad_s=10.0):
    """(start, end) of the run, padded. `launched` is the true start; `started`
    is written at the END by launch_run.py and must NOT be trusted as a start."""
    start = parse_ts(run_json.get('launched'))
    end = parse_ts(run_json.get('finished')) or parse_ts(run_json.get('started'))
    if start is None or end is None:
        return None
    if end < start:
        start, end = end, start
    pad = dt.timedelta(seconds=pad_s)
    return (start - pad, end + pad)


# ---------------------------------------------------------------- events


def classify(events):
    """Tag every event with a severity. `events` is a list of dicts with
    `provider`, `id`, `time` (datetime or str), `message`."""
    out = []
    for e in events:
        prov = str(e.get('provider', '')).strip().lower()
        sev = SEV_INFO
        if prov in FATAL_PROVIDERS:
            sev = SEV_FATAL
        elif prov in WARN_PROVIDERS:
            sev = SEV_WARN
        rec = dict(e)
        rec['provider'] = prov
        rec['severity'] = sev
        if not isinstance(rec.get('time'), dt.datetime):
            rec['time'] = parse_ts(rec.get('time'))
        out.append(rec)
    return out


def build_ps_query(start, end):
    """The PowerShell one-liner that reads the System log for [start, end].

    Built by concatenation on purpose: `str.format` on a script full of `@{...}`
    hashtables is a brace-escaping trap (it raised ValueError the first time this
    ran live, while the offline fixtures were green)."""
    fmt = '%Y-%m-%d %H:%M:%S'
    sel = ("Select-Object "
           "@{n='time';e={$_.TimeCreated.ToString('yyyy-MM-ddTHH:mm:ss')}},"
           "@{n='provider';e={$_.ProviderName}},"
           "@{n='id';e={$_.Id}},"
           "@{n='level';e={$_.LevelDisplayName}},"
           "@{n='message';e={($_.Message -replace \"`r`n\",' ')}}")
    return ("$a=Get-Date '" + start.strftime(fmt) + "'; "
            "$b=Get-Date '" + end.strftime(fmt) + "'; "
            "$e=Get-WinEvent -FilterHashtable "
            "@{LogName='System';StartTime=$a;EndTime=$b} -ErrorAction SilentlyContinue; "
            "if ($null -eq $e) { '[]' } else { $e | Sort-Object TimeCreated | "
            + sel + " | ConvertTo-Json -Compress -Depth 3 }")


def query_events(start, end):
    """Live query of the Windows System log. Returns None when the query itself
    failed (NOT EVALUABLE), an empty list when the window is genuinely quiet."""
    ps = build_ps_query(start, end)
    try:
        res = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps],
                             capture_output=True, text=True, timeout=180)
    except Exception:
        return None
    if res.returncode != 0:
        return None
    text = (res.stdout or '').strip()
    if not text:
        return None
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if isinstance(data, dict):
        data = [data]
    return data if isinstance(data, list) else None


# ---------------------------------------------------------------- stalls


def dt_outliers(log_path, min_us=100000, min_frame=0):
    """Frames whose `dt_us` on the main FrameTrace line is at least min_us.

    `min_frame` drops the entry hitches: frames before the scene became stable
    are not part of any measured population (the smoke report trims them too)."""
    pat = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
    out = []
    with open(log_path, 'rb') as f:
        for line in f:
            m = pat.match(line)
            if not m:
                continue
            n, us = int(m.group(1)), int(m.group(2))
            if us >= min_us and n >= min_frame:
                out.append((n, us))
    return out


def stable_frame(run_json):
    """Frame at which the scene was declared stable, 0 when unknown."""
    best = 0
    for a in run_json.get('attempts') or []:
        if a.get('outcome') == 'ok' and a.get('stable_frame'):
            best = max(best, int(a['stable_frame']))
    return best


def trim_to_busy(samples, util_max=15):
    """Drop the leading and trailing idle tails of a run: process start-up and
    shut-down are idle by construction and are not stalls."""
    first = last = None
    for i, (_, u) in enumerate(samples):
        if u > util_max:
            if first is None:
                first = i
            last = i
    if first is None:
        return []
    return samples[first:last + 1]


def read_gpu_csv(path):
    """[(datetime, util_percent)] from the nvidia-smi csv of the run."""
    out = []
    with open(path, newline='') as f:
        for row in csv.reader(f):
            if len(row) < 4:
                continue
            t = parse_ts(row[0].strip())
            if t is None:
                continue
            m = re.search(r'(\d+)', row[3])
            if not m:
                continue
            out.append((t, int(m.group(1))))
    return out


def idle_windows(samples, util_max=15, min_s=3.0):
    """Runs of consecutive samples at or below util_max lasting >= min_s.
    An idle window that starts at the first sample is still reported: a run that
    never woke is also evidence."""
    out = []
    run = []
    for t, u in samples:
        if u <= util_max:
            run.append((t, u))
            continue
        if run:
            dur = (run[-1][0] - run[0][0]).total_seconds()
            if dur >= min_s:
                out.append((run[0][0], run[-1][0], dur))
            run = []
    if run:
        dur = (run[-1][0] - run[0][0]).total_seconds()
        if dur >= min_s:
            out.append((run[0][0], run[-1][0], dur))
    return out


def correlate(events, windows, tol_s=5.0):
    """Pair fatal/warn events with the idle window they sit in (or touch)."""
    pairs = []
    tol = dt.timedelta(seconds=tol_s)
    for e in events:
        if e.get('severity') == SEV_INFO:
            continue
        t = e.get('time')
        if t is None:
            continue
        for (a, b, dur) in windows:
            if (a - tol) <= t <= (b + tol):
                pairs.append((e, (a, b, dur)))
                break
    return pairs


# ---------------------------------------------------------------- verdict


def verdict(events, windows, outliers):
    """RUN_INVALID | STALL_UNATTRIBUTED | RUN_CLEAN | NOT EVALUABLE."""
    if events is None:
        return ('NOT EVALUABLE', 'the Windows System log could not be read for this window')
    fatal = [e for e in events if e.get('severity') == SEV_FATAL]
    if fatal:
        names = sorted({'%s/%s' % (e['provider'], e.get('id')) for e in fatal})
        return ('RUN_INVALID', 'host device events inside the window: ' + ', '.join(names))
    if windows or outliers:
        return ('STALL_UNATTRIBUTED',
                'stall present (%d dt outliers, %d gpu-idle windows) with no host device event'
                % (len(outliers), len(windows)))
    return ('RUN_CLEAN', 'no host device event, no stall')


# ---------------------------------------------------------------- report


def format_report(tag, window, events, windows, outliers, pairs, verd):
    lines = []
    lines.append('hostdev122 %s' % tag)
    if window:
        lines.append('window %s .. %s (padded)' % (window[0].isoformat(), window[1].isoformat()))
    else:
        lines.append('window UNKNOWN (run json has no launched/finished)')
    if events is None:
        lines.append('events NOT EVALUABLE')
    else:
        lines.append('events %d (fatal %d, warn %d)' % (
            len(events),
            sum(1 for e in events if e['severity'] == SEV_FATAL),
            sum(1 for e in events if e['severity'] == SEV_WARN)))
        for e in events:
            if e['severity'] == SEV_INFO:
                continue
            t = e['time'].isoformat() if isinstance(e.get('time'), dt.datetime) else '?'
            msg = (e.get('message') or '').strip()
            lines.append('  %-5s %s %s/%s %s' % (e['severity'], t, e['provider'],
                                                 e.get('id'), msg[:110]))
    for (n, us) in outliers:
        lines.append('  STALL frame n=%d dt_us=%d (%.3f s)' % (n, us, us / 1e6))
    for (a, b, dur) in windows:
        lines.append('  GPU IDLE %s .. %s (%.1f s)' % (a.isoformat(), b.isoformat(), dur))
    for (e, (a, b, dur)) in pairs:
        t = e['time'].isoformat() if isinstance(e.get('time'), dt.datetime) else '?'
        lines.append('  CORRELATED %s/%s at %s with gpu-idle %.1f s from %s'
                     % (e['provider'], e.get('id'), t, dur, a.isoformat()))
    lines.append('VERDICT: %s - %s' % verd)
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('tag')
    ap.add_argument('--dir', default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument('--pad', type=float, default=10.0)
    ap.add_argument('--min-us', type=int, default=100000)
    ap.add_argument('--min-frame', type=int, default=None,
                    help='ignore frames below this number (default: the stable frame)')
    ap.add_argument('--events-json', default=None,
                    help='replay file instead of the live Windows log')
    ap.add_argument('--log', default=None)
    ap.add_argument('--csv', default=None)
    args = ap.parse_args(argv)

    root = args.dir
    run_json_path = os.path.join(root, '%s.json' % args.tag)
    run_json = {}
    if os.path.exists(run_json_path):
        with open(run_json_path) as f:
            run_json = json.load(f)
    window = run_window(run_json, args.pad)

    if args.events_json:
        with open(args.events_json) as f:
            raw = json.load(f)
    elif window:
        raw = query_events(window[0], window[1])
    else:
        raw = None
    events = None if raw is None else classify(raw)

    log_path = args.log or os.path.join(root, 'log_%s.txt' % args.tag)
    min_frame = args.min_frame if args.min_frame is not None else stable_frame(run_json)
    outliers = (dt_outliers(log_path, args.min_us, min_frame)
                if os.path.exists(log_path) else [])

    csv_path = args.csv or run_json.get('gpuclk') or os.path.join(root, 'gpuclk_%s.csv' % args.tag)
    wins = []
    if csv_path and os.path.exists(csv_path):
        # Only the busy span of a run can hold a meaningful idle window.
        wins = idle_windows(trim_to_busy(read_gpu_csv(csv_path)))
    pairs = correlate(events or [], wins)
    verd = verdict(events, wins, outliers)
    print(format_report(args.tag, window, events, wins, outliers, pairs, verd))
    return 0 if verd[0] == 'RUN_CLEAN' else 1


if __name__ == '__main__':
    sys.exit(main())
