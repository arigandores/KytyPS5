"""Audit 108: parallel mutant runner - each worker uses its own copy of test_fam108.py with BASE in the audit dir."""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, 'C:/kyty/s108/audit108')
AUD = Path('C:/kyty/s108/audit108')
SRC = Path('C:/kyty/s108/fam108.py').read_text(encoding='utf-8')
TEST = Path('C:/kyty/s108/test_fam108.py').read_text(encoding='utf-8')
OLD_BASE = "BASE = Path('C:/kyty/s106_stage/fx_fam108')"
assert TEST.count(OLD_BASE) == 1
import mutants_def  # noqa: E402

done = set(sys.argv[1:])
names = [n for n in mutants_def.MUTANTS if n not in done]
OUT = AUD / 'mutants'
OUT.mkdir(exist_ok=True)


def run(i_name):
    i, name = i_name
    old, new = mutants_def.MUTANTS[name]
    if SRC.count(old) != 1:
        return name, 'ANCHOR x%d' % SRC.count(old)
    p = OUT / ('fam108_%s.py' % name)
    p.write_text(SRC.replace(old, new), encoding='utf-8')
    t = OUT / ('test_fam108_w%d.py' % i)
    t.write_text(TEST.replace(OLD_BASE, "BASE = Path('C:/kyty/s108/audit108/fx_w%d')" % i), encoding='utf-8')
    r = subprocess.run([sys.executable, str(t), str(p)], capture_output=True, text=True, encoding='utf-8',
                       errors='replace')
    txt = r.stdout + r.stderr
    (OUT / ('%s.out' % name)).write_text(txt, encoding='utf-8')
    bad = [ln.split()[0] for ln in txt.splitlines() if ln.strip() and not ln.rstrip().endswith(('rc=0', 'rc=1',
                                                                                                'rc=2'))
           and ' OK ' not in ln and 'cases' not in ln and 'ALL OK' not in ln and 'S2 case' not in ln]
    fails = [ln.split()[0] for ln in txt.splitlines() if ' BAD ' in ln or ' FAIL ' in ln or 'MISMATCH' in ln]
    return name, ('SURVIVED' if 'ALL OK' in txt else 'KILLED by %s' % (fails[:5] or bad[:3] or txt.splitlines()[-1:]))


with ThreadPoolExecutor(max_workers=6) as ex:
    for name, verdict in ex.map(run, list(enumerate(names))):
        print('%-24s %s' % (name, verdict), flush=True)
