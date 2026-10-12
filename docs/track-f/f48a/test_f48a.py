# F48a (HPP-830): fixtures of census_f48a.py, triage_f48a.py, sweep_f48a.py, reopen_f48a.py.  Prints one line per member and
# 'ALL OK' when every member passes.  Usage: python test_f48a.py [<register.md>]   (no game, no lock taken; temp files only)
import os, sys, time, json, tempfile, subprocess, calendar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), 'register.md')
NL = chr(10)
res = []


def member(name, cond):
    res.append((name, bool(cond)))
    print('%-58s %s' % (name, 'ok' if cond else 'FAIL'))


import census_f48a as CE  # noqa: E402
import triage_f48a as TR  # noqa: E402
import reopen_f48a as RO  # noqa: E402

# ---------------------------------------------------------------- census
text = open(REG, encoding='utf-8').read().replace(chr(13), '')
rows, msgs = CE.census(text)
member('c1 real register: 0 messages', not msgs)
member('c1 real register: 77 ids', len(rows) == 77)
member('c1 real register: OPEN 0', sum(1 for r in rows if r['code'] == 'OPEN') == 0)
member('c1 real register: 7 remainders', sum(1 for r in rows if r['code'].endswith('+REM')) == 7)
member('c1 real register: F28 last row is s106:1521 (not the reference row)',
       [r for r in rows if r['id'] == 'Ф28'][0]['last_line'] == 1521)

SYN = NL.join([
    '## 4. Таблица', '', '| № | класс | статус на сегодня |', '|---|---|---|',
    '| Б99 | K4 | открыт |', '| Б98 | K4 | открыт |', '| Б8 | K4 | открыт |', '| Б8-H | K4 | открыт |', '',
    '## 50. Исходы', '', '| № | класс | статус на сегодня |', '|---|---|---|',
    '| Б99 (поправка) | K4 | **`FIXED`** (итерация 1) |', '| Б98 | K4 | **`ТУПИК`** по п. 1 |',
    '| Б8 | K4 | **`НЕ ДЕФЕКТ`** |', '| Б8-H | K4 | **`НЕ ДЕФЕКТ`** на месте |',
    '| форма харнесса (наблюдение, справка Б99) | K5 | паркуется |', '',
    '## 103. Сводка', '', '| № | класс | статус на сегодня |', '|---|---|---|', '| Б97 | K4 | в работе |', ''])
import re  # noqa: E402
A = {'Б99': ('FIXED', re.compile('FIXED')), 'Б98': ('TUPIK', re.compile('ТУПИК')), 'Б8': ('NE_DEFEKT', re.compile('НЕ ДЕФЕКТ')),
     'Б8-H': ('NE_DEFEKT', re.compile('НЕ ДЕФЕКТ')), 'Б97': ('OPEN', re.compile('x'))}
r2, m2 = CE.census(SYN, adj={k: v for k, v in A.items() if k != 'Б97'}, lead={}, rem={})
member('c2 synthetic: B97 only in s103 -> NOT ADJUDICATED', any(m.startswith('NOT ADJUDICATED Б97') for m in m2))
r2, m2 = CE.census(SYN, adj=A, lead={}, rem={})
member('c3 synthetic: B97 only in s103 -> ONLY IN SUMMARY', any(m.startswith('ONLY IN SUMMARY Б97') for m in m2))
SYN2 = SYN.replace('| Б97 | K4 | в работе |', '')
A2 = {k: v for k, v in A.items() if k != 'Б97'}
r2, m2 = CE.census(SYN2, adj=A2, lead={}, rem={})
member('c4 synthetic clean: 0 messages', not m2)
member('c4 B8-H is its own id, last row s50', {r['id']: r['last_sec'] for r in r2}.get('Б8-H') == '50')
member('c5 reference row (справка Б99) is not a row of B99', {r['id']: r['last_line'] for r in r2}['Б99'] == SYN2.split(NL).index('| Б99 (поправка) | K4 | **`FIXED`** (итерация 1) |') + 1)
A3 = dict(A2)
A3['Б98'] = ('FIXED', re.compile('ТУПИК'))
r2, m2 = CE.census(SYN2, adj=A3, lead={}, rem={})
member('c6 census code against the last-row bold word -> CONTRADICTS', any(m.startswith('LAST ROW CONTRADICTS Б98') for m in m2))
r2, m2 = CE.census(SYN2, adj=A2, lead={'Б98': 'FIXED', 'Б77': 'TUPIK'}, rem={})
member('c7 lead count differs / missing -> messages', any('LEAD DIFFERS Б98' in m for m in m2) and any('LEAD ID MISSING Б77' in m for m in m2))
A4 = dict(A2)
A4['Б98'] = ('TUPIK', re.compile('НЕТ ТАКОГО СЛОВА'))
r2, m2 = CE.census(SYN2, adj=A4, lead={}, rem={})
member('c8 outcome word absent from every line -> NO LINE WITH', any(m.startswith('NO LINE WITH Б98') for m in m2))
A5 = dict(A2)
A5['Б99'] = ('FIXED+REM', re.compile('FIXED'))
r2, m2 = CE.census(SYN2, adj=A5, lead={}, rem={})
member('c9 remainder code without a condition line -> message', any(m.startswith('REM CODE WITHOUT CONDITION Б99') for m in m2))

# ---------------------------------------------------------------- triage
EX = {'TestHidLoss: fX mode=upd fix=X': 'INSTR', 'ExitFatal: config arm=PX seed=X pos=X': 'INSTR',
      'Error: condition (g_inject.load()) is true in C:\\kyty\\fX\\fXa\\wt\\src\\emulator.cpp:X': 'INSTR',
      'Error: condition (g_arm == Arm::CN) is true in C:\\kyty\\fX\\fXd\\wt\\src\\emulator.cpp:X': 'INSTR',
      'OK   tX shader_cfg_tests failed multiset equal: fsX True fsX True': 'INSTR',
      'OK   kernel_file_system_tests full KYTY_FIX_FX=X rc X': 'INSTR', '[X] lines overflow = min(X, X), fields PASS': 'INSTR',
      'StreamRead: #X tid=X dst=X size=X C:/kyty/x_crash.szd': 'INSTR',
      'FixFX: open failed index=X error="Couldn\'t find mapping for device (X)"': 'INSTR',
      '<X>WSL (X - Relay) ERROR: CreateProcessCommon:X: execvpe(/bin/bash) failed': 'TOOL',
      'CsPretranslate: skipped hash=X reason=C:\\kyty\\fX\\fXg\\wt\\src\\graphics/shader/recompiler/TranslationBudget.h:X speculative translation budget exceeded': 'ROW'}
member('t1 every F48a rule example gets its class', all((TR.classify(s, 'C:/kyty/f287/x/log_a.txt') or ('-',))[0] == c for s, c in EX.items()))
member('t2 unknown signature -> unclassified', TR.classify('--- Fatal Error --- something new', 'C:/kyty/f287/x/log_a.txt') is None)
member('t3 fixture signature outside a fixture path -> BAD', TR.classify('ErrorDeviceLost', 'C:/kyty/f287/x/log_a.txt')[0] == 'BAD')
member('t3 fixture signature inside a fixture path -> FIXTURE', TR.classify('ErrorDeviceLost', 'C:/kyty/f287/x/fxread/log_a.txt')[0] == 'FIXTURE')

# ---------------------------------------------------------------- sweep wrapper
tmp = tempfile.mkdtemp(prefix='f48a_fx_')
env = dict(os.environ)
env.update({'F32A_OUT': tmp + '/out', 'F32A_ROOT': tmp + '/root', 'PYTHONIOENCODING': 'utf-8'})
os.makedirs(tmp + '/root/a', exist_ok=True)
T0 = calendar.timegm((2026, 10, 10, 0, 0, 0))
for name, mt in (('log_old.txt', T0 - 1), ('log_new.txt', T0 + 1), ('_kyty_new.txt', T0 + 5), ('other.txt', T0 + 5)):
    p = tmp + '/root/a/' + name
    open(p, 'wb').write(b'FrameTrace: n=1 dt_us=16667' + bytes([10]))
    os.utime(p, (mt, mt))
wr = os.path.join(HERE, 'sweep_f48a.py')
r = subprocess.run([sys.executable, wr, 'list'], env=env, capture_output=True, text=True)
lst = open(tmp + '/out/loglist_f32a.tsv', encoding='utf-8').read() if os.path.exists(tmp + '/out/loglist_f32a.tsv') else ''
member('s1 list: mtime > 2026-10-10Z taken (log_new, _kyty_new)', r.returncode == 0 and 'log_new.txt' in lst and '_kyty_new.txt' in lst)
member('s1 list: mtime <= T0 not taken, name outside mask not taken', 'log_old.txt' not in lst and 'other.txt' not in lst)
lock = tmp + '/LOCK'
open(lock, 'w').close()
e2 = dict(env)
e2['F32A_LOCK'] = lock
r = subprocess.run([sys.executable, wr, 'list'], env=e2, capture_output=True, text=True)
member('s2 lock present -> exit 3', r.returncode == 3)
e3 = dict(env)
e3['F32A_STOP'] = lock
r = subprocess.run([sys.executable, wr, 'list'], env=e3, capture_output=True, text=True)
member('s2 STOP present -> exit 4', r.returncode == 4)

# ---------------------------------------------------------------- reopen pass
L = [b'x', b'--- Fatal Error ---', b'FixF24: mode=1 b24=1', b'FixF24: init_owner hid=1', b'FlipHold flip=3 poll_us=499999',
     b'FlipHold flip=4 poll_us=500000', b'FixF20Stat: when=exit unmatched=0', b'FixF20Stat: when=exit unmatched=3',
     b'Pause: true', b'LogAsync: stall us=5', b'--- Fatal Error ---']
blob = b'\r\n'.join(L)  # CRLF, last line without a newline
cuts = [blob[:17], blob[17:90], blob[90:]]  # boundaries inside lines
RO.LOCK = tmp + '/no_lock'
RO.STOP = tmp + '/no_stop'
w, envl, form, b, ln = RO.scan_bytes(cuts)
member('r1 lines counted across chunk cuts, CRLF, last line without NL', ln == len(L))
member('r1 two fatal lines (one is the last line), first at line 2', w['f21_second'][0] == 2 and w['f21_second'][1].startswith('2:'))
member('r2 FlipHold poll_us 499999 no, 500000 yes', w['fliphold'][0] == 1 and w['fliphold'][1].startswith('6:'))
member('r2 FixF20Stat unmatched=0 no, =3 yes', w['f20_unm'][0] == 1 and w['f20_unm'][1].startswith('8:'))
member('r2 FixF24 mode=1 and init counted', w['f24_mode1'][0] == 1 and w['f24_init'][0] == 1)
member('r2 Pause / LogAsync stall counted', w['pause_on'][0] == 1 and w['logstall'][0] == 1)
e4 = dict(env)
e4['F48A_LOCK'] = lock
r = subprocess.run([sys.executable, os.path.join(HERE, 'reopen_f48a.py'), tmp, tmp, tmp + '/o.json'], env=e4, capture_output=True, text=True)
member('r3 lock present -> exit 3', r.returncode == 3)

ok = all(x[1] for x in res)
print('members', len(res), 'passed', sum(1 for x in res if x[1]))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
