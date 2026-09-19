"""Both-instrument mode2 diagnostic; never closes G/R1 or licenses development."""
import argparse
import math
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bf99


def branch(a, c):
    if a is None or c is None or any(not math.isfinite(x) or x <= 0 for x in (a, c)):
        return 'NO VERDICT'
    if min(a, c) >= 15.5:
        return 'HIGH DIAGNOSTIC'
    if max(a, c) <= 11:
        return 'LOW DIAGNOSTIC'
    return 'DIAGNOSTIC GAP'


def score(tag, instrument, root, mechanics):
    cmd = [sys.executable, str(Path(__file__).with_name('bf99.py')), tag,
           '--instrument', instrument, '--root', str(root)]
    if mechanics:
        cmd.append('--mechanics-only')
    process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    output = process.stdout + process.stderr
    for line in output.splitlines():
        print(tag + '| ' + line)
    number = re.findall(r"^B_st'' = ([0-9.]+) ms$", output, re.M)
    admitted = re.findall(r'^ADMISSION: (.*)$', output, re.M)
    actual = re.findall(r'^INSTRUMENT99 = (.*)$', output, re.M)
    hashes = re.findall(r'^BINARY99 = (.*)$', output, re.M)
    if mechanics or process.returncode or admitted != ['ADMITTED'] or len(number) != 1 \
            or actual != [instrument] or hashes != [bf99.BINARY_SHA]:
        return None
    return float(number[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True)
    ap.add_argument('--c', required=True, help='mandatory; no walk-subtraction fallback')
    ap.add_argument('--root', type=Path, default=Path('C:/kyty/s99'))
    ap.add_argument('--mechanics-only', action='store_true')
    args = ap.parse_args()
    print('GLOBAL M3: existing GAP unchanged; historical constant 2.2535 stands.')
    print('MODE2: no addends. Unknown pessimism P: no architecture closure or licence.')
    if args.a == args.c:
        print('DIAGNOSTIC99: NO VERDICT (need two distinct instruments)'); return 1
    a = score(args.a, 'a', args.root, args.mechanics_only)
    c = score(args.c, 'c', args.root, args.mechanics_only)
    result = branch(a, c)
    if result != 'NO VERDICT':
        print('B_a=%.9f B_c=%.9f ms; min=%.9f max=%.9f' % (a, c, min(a, c), max(a, c)))
        print('DESCRIPTIVE CROSS-BINARY NET CONTRAST: B_a-F_a=%+.9f, B_c-F_c=%+.9f ms; '
              'F_a=14.274, F_c=12.825 on s98 binary/clear1; not a materialization timer.' %
              (a - 14.274, c - 12.825))
    print('DIAGNOSTIC99: ' + result)
    print('G/R1 alive and unlicensed; M3 remains GAP; M4/M5 not advanced.')
    return 1 if result == 'NO VERDICT' else 0


if __name__ == '__main__':
    sys.exit(main())
