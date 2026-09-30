"""Step 2 (HPP-268): pre-screen of chosen mutants of pm4c140.py (own runner, NOT mutlib, not counted)."""
import subprocess, sys, os, concurrent.futures, pathlib, time
names = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else None
src = open('C:/kyty/s140/pm4c140.py', encoding='utf-8').read()
ns = {}
exec(open('C:/kyty/s140/mut_pm4c140.py', encoding='utf-8').read(), ns)
d = pathlib.Path(os.environ['PAPERCLIP_RUN_SCRATCH_DIR']) / 'pre2'
d.mkdir(exist_ok=True)
t0 = time.time()


def job(m):
    n, a, b = m
    wd = d / n
    wd.mkdir(exist_ok=True)
    mp = wd / 'pm4c140.py'
    mp.write_text(src.replace(a, b), encoding='utf-8')
    ts = open('C:/kyty/s140/test_pm4c140.py', encoding='utf-8').read().replace(
        "Path('C:/kyty/s140/fx_pm4c140')", "Path(r'%s')" % (wd / 'fx'))
    tp = wd / 't.py'
    tp.write_text(ts, encoding='utf-8')
    r = subprocess.run([sys.executable, str(tp), str(mp)], capture_output=True, text=True, cwd='C:/kyty/s140')
    return n, r.returncode


todo = [m for m in ns['MUTANTS'] if names is None or m[0] in names]
with concurrent.futures.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(job, todo))
print('jobs', len(todo), 'survivors', [n for n, rc in res if rc == 0], 'wall', round(time.time() - t0))
