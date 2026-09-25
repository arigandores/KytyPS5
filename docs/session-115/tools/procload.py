"""Session 115, ROADMAP item 2 (audit 114 finding F1): refuse a sealed chain while any single process burns more than
MAX_RATE CPU seconds per wall second (the aggregate CPU check cannot see one busy core of 32), or all non-system
processes together more than MAX_TOTAL (item 7: functional seals use --max-rate 1.5 --max-total 4; timing seals keep
the default 0.5 and no total cap).  Two snapshots of the per-process CPU time, SPAN seconds apart; retries every
RETRY_S seconds up to WAIT_S; exit 0 when clean, 1 otherwise.

    python C:/kyty/s115/procload.py [--wait-s 1800] [--max-rate 0.5] [--max-total N]
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


def offenders(max_rate, max_total):
    a = snapshot()
    t0 = time.monotonic()
    time.sleep(SPAN)
    b = snapshot()
    dt = time.monotonic() - t0
    bad = []
    total = 0.0
    for key, cpu in b.items():
        if key[1].lower() in IGNORE or key not in a:
            continue
        rate = (cpu - a[key]) / dt
        total += max(rate, 0.0)
        if rate > max_rate:
            bad.append((key[1], key[0], round(rate, 3)))
    bad.sort(key=lambda r: -r[2])
    if max_total is not None and total > max_total:
        bad.append(('TOTAL', 0, round(total, 3)))
    return bad


def main():
    wait_s = float(sys.argv[sys.argv.index('--wait-s') + 1]) if '--wait-s' in sys.argv else 1800.0
    max_rate = float(sys.argv[sys.argv.index('--max-rate') + 1]) if '--max-rate' in sys.argv else MAX_RATE
    max_total = float(sys.argv[sys.argv.index('--max-total') + 1]) if '--max-total' in sys.argv else None
    start = time.monotonic()
    while True:
        bad = offenders(max_rate, max_total)
        if not bad:
            print('procload: clean (no process above %.2f CPU s/s, total cap %s)' % (max_rate, max_total))
            return 0
        print('procload: busy %s' % bad, flush=True)
        if time.monotonic() - start + RETRY_S > wait_s:
            return 1
        time.sleep(RETRY_S)


if __name__ == '__main__':
    sys.exit(main())
