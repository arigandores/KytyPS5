"""Session 121, ROADMAP s121 item 4: "shp121 ... запускается только после ПРОХОДА печати 01".  The chain gate of
go121a.sh shp121|shp121r (pre-seal check of shp121.py, blocking finding 2): the chain refuses to start the sealed ABBA
unless the sealed verify result is a PASS, so that no procedural gap in the verify evidence can turn an admitted run
into a sealed NO_SHIP.

A PASS here means ALL of:
  - shp121.py carries `VFY_SCORER_SHA = '<64 hex>'` (filled at seal 02) and it equals sha256(vfy121.py) now;
  - runs121/vfy121.score.json exists, is a JSON object with draft False, tag 'vfy121', build_sha256 BUILD,
    scorer_sha256 VFY_SCORER_SHA, and verdict PASS -> the passing tag is vfy121;
    or its verdict is NOT_ADMITTED (the only verdict that allows the repeat) and runs121/vfy121r.score.json passes the
    same checks with tag 'vfy121r' -> the passing tag is vfy121r;
  - anything else (a missing / unreadable / draft file, another scorer or build, FAIL, a vfy121r after a FAIL or a PASS)
    refuses.
The score files are written by the sealed scorer, never by hand:
    python C:/kyty/s121/vfy121.py --tag <vfy tag> --out C:/kyty/s121/runs121/<vfy tag>.score.json   (no --draft)
Prints the passing tag on stdout (exit 0) or the reason on stderr (exit 1).

    python C:/kyty/s121/chk_vfy121.py [--root C:/kyty/s121]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s121'
BUILD = '0bd21ec24e546fbbb9b923c148fb76b57f45389ac166a71bad7410a3add738c7'
VSHA_LINE = re.compile(r"^VFY_SCORER_SHA = '([0-9a-f]{64})'", re.M)


def load(path):
    """(dict or None, reason)."""
    p = Path(path)
    if not p.is_file():
        return None, 'missing %s' % p.name
    try:
        v = json.loads(p.read_text(encoding='utf-8'))
    except (ValueError, OSError, UnicodeDecodeError):
        return None, 'unreadable %s' % p.name
    if not isinstance(v, dict):
        return None, 'unreadable %s' % p.name
    return v, ''


def sealed(v, tag, vsha, build):
    """'' when the result is a sealed result of that tag, scorer and build; else the reason."""
    if v.get('draft') is not False:
        return '%s is a draft (or has no draft field)' % tag
    if v.get('tag') != tag:
        return '%s carries tag %r' % (tag, v.get('tag'))
    if v.get('build_sha256') != build:
        return '%s scored another build' % tag
    if v.get('scorer_sha256') != vsha:
        return '%s scored by another vfy121.py (%s)' % (tag, str(v.get('scorer_sha256'))[:16])
    return ''


def check(root=ROOT, build=BUILD):
    """(passing tag or None, reason)."""
    root = Path(root)
    shp = root / 'shp121.py'
    vfy = root / 'vfy121.py'
    if not shp.is_file() or not vfy.is_file():
        return None, 'shp121.py or vfy121.py missing'
    m = VSHA_LINE.search(shp.read_text(encoding='utf-8'))
    if m is None:
        return None, 'VFY_SCORER_SHA not filled in shp121.py'
    vsha = m.group(1)
    if hashlib.sha256(vfy.read_bytes()).hexdigest() != vsha:
        return None, 'VFY_SCORER_SHA != sha256(vfy121.py)'
    first, why = load(root / 'runs121' / 'vfy121.score.json')
    if first is None:
        return None, why
    why = sealed(first, 'vfy121', vsha, build)
    if why:
        return None, why
    repeat_path = root / 'runs121' / 'vfy121r.score.json'
    if first.get('verdict') == 'PASS':
        if repeat_path.exists():
            return None, 'vfy121 PASS but a vfy121r result exists (the repeat runs only on NOT_ADMITTED)'
        return 'vfy121', 'PASS'
    if first.get('verdict') != 'NOT_ADMITTED':
        return None, 'vfy121 verdict %r (not PASS; the repeat runs only on NOT_ADMITTED)' % first.get('verdict')
    second, why = load(repeat_path)
    if second is None:
        return None, 'vfy121 NOT_ADMITTED and ' + why
    why = sealed(second, 'vfy121r', vsha, build)
    if why:
        return None, why
    if second.get('verdict') != 'PASS':
        return None, 'vfy121r verdict %r' % second.get('verdict')
    return 'vfy121r', 'PASS'


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag, why = check(root)
    if tag is None:
        sys.stderr.write('chk_vfy121: REFUSED - %s' % why + chr(10))
        return 1
    sys.stdout.write(tag + chr(10))
    return 0


if __name__ == '__main__':
    sys.exit(main())
