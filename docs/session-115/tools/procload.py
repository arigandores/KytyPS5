"""Session 115, ROADMAP item 2 (audit 114 finding F1): refuse a sealed chain while any single process burns more than
MAX_RATE CPU seconds per wall second (the aggregate CPU check cannot see one busy core of 32).  Two snapshots of the
per-process CPU time, SPAN seconds apart; retries every RETRY_S seconds up to WAIT_S; exit 0 when clean, 1 otherwise.

    python C:/kyty/s115/procload.py [--wait-s 1800]
"""
import json
import subprocess
import sys
import time

MAX_RATE = 0.5
SPAN = 10.0
RETRY_S = 60
IGNORE = {'idle', 'system', 'system idle process'}


def snapshot():
    cmd = ['powershell', '-NoProfile', '-Command',
           'Get-Process | Select-Object Id,ProcessName,CPU | ConvertTo-Json -Compress']
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace').stdout
    rows = json.loads(out)
    return {(r['Id'], r['ProcessName']): float(r['CPU'] or 0.0) for r in rows}


def offenders():
    a = snapshot()
    t0 = time.monotonic()
    time.sleep(SPAN)
    b = snapshot()
    dt = time.monotonic() - t0
    bad = []
    for key, cpu in b.items():
        if key[1].lower() in IGNORE or key not in a:
            continue
        rate = (cpu - a[key]) / dt
        if rate > MAX_RATE:
            bad.append((key[1], key[0], round(rate, 3)))
    return sorted(bad, key=lambda r: -r[2])


def main():
    wait_s = float(sys.argv[sys.argv.index('--wait-s') + 1]) if '--wait-s' in sys.argv else 1800.0
    start = time.monotonic()
    while True:
        bad = offenders()
        if not bad:
            print('procload: clean (no process above %.2f CPU s/s)' % MAX_RATE)
            return 0
        print('procload: busy %s' % bad, flush=True)
        if time.monotonic() - start + RETRY_S > wait_s:
            return 1
        time.sleep(RETRY_S)


if __name__ == '__main__':
    sys.exit(main())
