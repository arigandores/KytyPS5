"""Session 122: the pre-seal gate of the chain (the idiom of chk_vfy121.py, s121): go122a.sh refuses to start a
SEALED run of this session unless the scorer that will score it is the one the fixtures and the mutants were run
against, its pre-registration is sealed, the tag's arm is sealed, and the scorer still runs on a real log.

A PASS means ALL of:
  1. map122.py, test_map122.py and mut_map122.py exist;
  2. map122.py carries `PRED_SHA = '<64 hex>'` and `PRED_BYTES = <n>` and they are the sha256 and the size of
     PRED_PATH (pred/01_map122.md) NOW - an unsealed scorer (PRED_SHA = None) refuses;
  3. the tag's PLAN entry exists and its arm value is filled with a code map122 knows (an unrecorded arm refuses -
     ROADMAP s122: an unrecorded decision is void; skym122 has no entry - it left the map by item 13 (b));
  4. the evidence file checks/map122_checks.json names THIS scorer, THIS suite and THIS mutant list by sha256, its
     fixture run ended in ALL OK with 0 failures, and its mutant run was certified with 0 survivors (and 0 unresolved
     anchors).  The file is written by mk_checks122.py right after those runs, never by hand, and any edit of the
     scorer, the suite or the mutant list invalidates it by sha256;
  5. the scorer scores a REAL log of this session now (log_bsky122.txt, the unsealed six-arm burn smoke) without
     raising, and lands on NOT_ADMITTED with a non-empty list of failed checks - a scorer that admits the smoke as if
     it were the sealed ABBA is broken.
Prints PASS on stdout (exit 0) or the reason on stderr (exit 1).

    python C:/kyty/s122/chk_map122.py --tag <sealed tag> [--root C:/kyty/s122]
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s122'
EVIDENCE = 'checks/map122_checks.json'
DRY_TAG = 'bsky122'
PRED_SHA_LINE = re.compile(r"^PRED_SHA = '([0-9a-f]{64})'", re.M)
PRED_BYTES_LINE = re.compile(r'^PRED_BYTES = (\d+)', re.M)


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(path):
    spec = importlib.util.spec_from_file_location('map122_gate', str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(root=ROOT, tag=None):
    """(True, 'PASS') or (False, reason)."""
    root = Path(root)
    scorer, suite, mutants = root / 'map122.py', root / 'test_map122.py', root / 'mut_map122.py'
    for p in (scorer, suite, mutants):
        if not p.is_file():
            return False, 'missing %s' % p.name
    text = scorer.read_text(encoding='utf-8')
    m, mb = PRED_SHA_LINE.search(text), PRED_BYTES_LINE.search(text)
    if m is None or mb is None:
        return False, 'PRED_SHA / PRED_BYTES not filled in map122.py (the seal is not written)'
    mod = load_module(scorer)
    pred = Path(mod.PRED_PATH)
    if not pred.is_file():
        return False, 'the pre-registration %s does not exist' % mod.PRED_PATH
    if sha_file(pred) != m.group(1) or len(pred.read_bytes()) != int(mb.group(1)):
        return False, 'PRED_SHA / PRED_BYTES do not match %s now' % pred.name
    if tag is None:
        return False, 'no --tag given'
    if mod.plan_of(tag) is None:
        return False, 'no PLAN entry for tag %s' % tag
    value = mod.arm_value(tag)
    if value is None or mod.code_dose(value)[0] not in mod.CODE_GROUP:
        return False, ('the arm of tag %s is not sealed (PLAN burn=%r); the lead records that constant before the run'
                       % (tag, value))
    ev_path = root / EVIDENCE
    if not ev_path.is_file():
        return False, 'missing %s (run the fixtures and the mutants first)' % EVIDENCE
    try:
        ev = json.loads(ev_path.read_text(encoding='utf-8'))
    except (ValueError, OSError, UnicodeDecodeError):
        return False, 'unreadable %s' % EVIDENCE
    if not isinstance(ev, dict):
        return False, 'unreadable %s' % EVIDENCE
    for key, path in (('scorer_sha256', scorer), ('test_sha256', suite), ('mutants_sha256', mutants)):
        if ev.get(key) != sha_file(path):
            return False, '%s names another %s (%s)' % (EVIDENCE, path.name, str(ev.get(key))[:16])
    if ev.get('pred_sha256') != m.group(1):
        return False, '%s was written against another pre-registration' % EVIDENCE
    fx = ev.get('fixtures') or {}
    if fx.get('all_ok') is not True or fx.get('failed') != 0 or not fx.get('total'):
        return False, 'the recorded fixture run is not ALL OK (%r)' % fx
    mu = ev.get('mutants') or {}
    if mu.get('certified') is not True or mu.get('survived') != 0 or mu.get('unresolved') != 0 or not mu.get('total'):
        return False, 'the recorded mutant run is not a certified 0-survivor full run (%r)' % mu
    log = root / ('log_%s.txt' % DRY_TAG)
    if not log.is_file():
        return False, 'missing the dry-run log %s' % log.name
    try:
        res = mod.evaluate(str(root), DRY_TAG, draft=True, installed_sha='ff' * 32)
        mod.format_report(res)
    except Exception as exc:                        # noqa: BLE001 - the gate exists to catch exactly this
        return False, 'the scorer raised on %s: %r' % (log.name, exc)
    failed = [k for k, v in (res.get('checks') or {}).items() if not v]
    if res.get('verdict') != 'NOT_ADMITTED' or not failed:
        return False, 'the dry run of %s gave %r (failed %r), expected NOT_ADMITTED with reasons' % (
            DRY_TAG, res.get('verdict'), failed)
    return True, ('PASS (tag %s arm burn=%d, pred %s, fixtures %d, mutants %d killed of %d, dry %s NOT_ADMITTED '
                  'failed=%d)' % (tag, value, m.group(1)[:16], fx.get('total'), mu.get('killed'), mu.get('total'),
                                  DRY_TAG, len(failed)))


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else None
    ok, why = check(root, tag)
    if not ok:
        sys.stderr.write('chk_map122: REFUSED - %s' % why + chr(10))
        return 1
    sys.stdout.write('chk_map122: ' + why + chr(10))
    return 0


if __name__ == '__main__':
    sys.exit(main())
