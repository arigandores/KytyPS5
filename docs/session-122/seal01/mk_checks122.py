"""Session 122: writes checks/map122_checks.json - the evidence chk_map122.py reads before a sealed run (never by hand).

It (1) runs the fixture suite on the scorer NOW and requires `N fixtures, 0 failed` and a final `ALL OK`; (2) reads the
report of a FULL mutlib v4.1 run (--out file) and requires that its header names THIS harness sha, THIS scorer, THIS
suite and THIS mutant list by sha256, that its count line reads `<n> mutants: <k> killed ..., 0 survived, 0 unresolved`,
that every control survived, and that its last line is `ALL KILLED (...)`.  Any mismatch refuses (exit 1, no file).
    python C:/kyty/s122/mk_checks122.py --report C:/kyty/s122/mut_map122.<tag>.txt
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path('C:/kyty/s122')
MUTLIB = Path('C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py')
MUTLIB_SHA = 'db82ef4bcf05ddea365f50c403029bfc5d2a7a4400a12d254a6b0cc6ab3e6dde'
SCORER, SUITE, MUTANTS = ROOT / 'map122.py', ROOT / 'test_map122.py', ROOT / 'mut_map122.py'
OUT = ROOT / 'checks' / 'map122_checks.json'
PRED_SHA_LINE = re.compile(r"^PRED_SHA = '([0-9a-f]{64})'", re.M)
COUNT_LINE = re.compile(r'^(\d+) mutants: (\d+) killed .*?, (\d+) survived, (\d+) unresolved', re.M)
CONTROLS_LINE = re.compile(r'^controls: (\d+) of (\d+) survived', re.M)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def refuse(why):
    sys.stderr.write('mk_checks122: REFUSED - %s%s' % (why, chr(10)))
    return 1


def main():
    if '--report' not in sys.argv:
        return refuse('no --report <mutlib --out file>')
    report = Path(sys.argv[sys.argv.index('--report') + 1])
    if sha(MUTLIB) != MUTLIB_SHA:
        return refuse('mutlib.py is not v4.1 (%s)' % sha(MUTLIB)[:16])
    fx = subprocess.run([sys.executable, str(SUITE), str(SCORER)], capture_output=True, text=True, encoding='utf-8',
                        errors='replace')
    lines = fx.stdout.strip().splitlines()
    m = re.match(r'^(\d+) fixtures, (\d+) failed$', lines[-2]) if len(lines) >= 2 else None
    if fx.returncode != 0 or not lines or lines[-1] != 'ALL OK' or m is None or m.group(2) != '0':
        return refuse('the fixture suite is not ALL OK: %r' % lines[-3:])
    if not report.is_file():
        return refuse('no report %s' % report)
    text = report.read_text(encoding='utf-8', errors='replace')
    for label, path in (('harness', MUTLIB), ('scorer', SCORER), ('test', SUITE), ('mutants', MUTANTS)):
        head = r'^mutlib 4\.1\s+harness' if label == 'harness' else r'^' + label
        if not re.search(r'%s\s+.* sha256 %s$' % (head, sha(path)), text, re.M):
            return refuse('the report does not name the current %s (sha256 %s)' % (path.name, sha(path)[:16]))
    c = COUNT_LINE.search(text)
    k = CONTROLS_LINE.search(text)
    last = text.strip().splitlines()[-1]
    if c is None or k is None:
        return refuse('the report has no count / controls line')
    total, killed, survived, unresolved = (int(x) for x in c.groups())
    certified = (last.startswith('ALL KILLED (') and survived == 0 and unresolved == 0 and killed == total
                 and k.group(1) == k.group(2) and '--changed-from' not in text)
    if not certified:
        return refuse('the mutant run is not a certified 0-survivor full run: %r / %s' % (c.groups(), last[:80]))
    ps = PRED_SHA_LINE.search(SCORER.read_text(encoding='utf-8'))
    ev = dict(scorer_sha256=sha(SCORER), test_sha256=sha(SUITE), mutants_sha256=sha(MUTANTS),
              pred_sha256=ps.group(1) if ps else None, mutlib_sha256=MUTLIB_SHA,
              fixtures=dict(total=int(m.group(1)), failed=0, all_ok=True),
              mutants=dict(certified=True, total=total, killed=killed, survived=0, unresolved=0,
                           controls='%s of %s survived' % k.groups(), report=str(report).replace('\\', '/'),
                           report_sha256=sha(report)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes((json.dumps(ev, indent=1) + chr(10)).encode('utf-8'))
    print('mk_checks122: wrote %s (fixtures %d ALL OK, mutants %d of %d killed, pred %s)'
          % (OUT, ev['fixtures']['total'], killed, total, (ev['pred_sha256'] or 'None')[:16]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
