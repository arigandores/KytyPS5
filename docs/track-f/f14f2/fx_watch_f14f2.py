# F14f2: fixture of the gate sign of watch_f14f2.py on fake processes (no real gate is started - a fake procload.py
# process would make other links' watchdogs kill their steps).
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('w', 'C:/kyty/f287/f14f2/watch_f14f2.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class P:
    def __init__(self, pid, argv):
        self.info = {'pid': pid, 'create_time': 1.0}
        self._argv = argv

    def cmdline(self):
        return self._argv


cases = [
    (1, ['python', 'C:/kyty/f287/f18e/procload.py', '--wait-s', '120'], True),
    (2, ['python', 'C:' + chr(92) + 'kyty' + chr(92) + 's288' + chr(92) + 'procload.py'], True),
    (3, ['python', 'procload.py'], True),
    (4, ['bash', '-c', 'source x; echo procload.py; grep procload.py times.txt'], False),
    (5, ['bash', '-c', 'python C:/kyty/f287/f14g/procload.py --wait-s 120'], False),
    (6, ['python', 'C:/kyty/f287/f14e2/procload.py.bak'], False),
    (7, ['python', 'C:/kyty/x/notprocload.py'], False),
]
w.psutil.process_iter = lambda attrs=None: [P(pid, argv) for pid, argv, _ in cases]
hits = w.Scanner(own=-1).find()
ok = True
for pid, argv, exp in cases:
    got = pid in hits
    print(pid, 'gate' if got else 'not', 'expect', 'gate' if exp else 'not', 'OK' if got == exp else 'BAD')
    ok &= got == exp
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
