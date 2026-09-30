"""Session 142 step 0: fill pred/01_sc142.md from step0/pred_template.md (calls, evidence, seal lines with sha256).  Writes
LF, UTF-8; prints ASCII.  Refuses to overwrite an existing seal."""
import datetime
import hashlib
import importlib.util
import os
import sys

ROOT = 'C:/kyty/s142'
OUT = ROOT + '/pred/01_sc142.md'
spec = importlib.util.spec_from_file_location('sc', ROOT + '/sc142.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def tail(p, n=1):
    return open(p, encoding='utf-8', errors='replace').read().rstrip('\n').split('\n')[-n:]


if os.path.exists(OUT):
    print('seal exists: %s - refused' % OUT)
    sys.exit(1)
t = open(ROOT + '/step0/pred_template.md', encoding='utf-8').read()
when = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
calls = '\n'.join('    go142a call: PLWAIT=540 bash C:/kyty/s142/go142a.sh %s' % x for x in S.SEQ)
calls = '```\n' + '\n'.join(l[4:] for l in calls.split('\n')) + '\n```'
ev = []


def e(label, path, extra=''):
    ev.append('- %s: `%s` sha256 `%s`%s' % (label, path, sha(path), extra))


e('калибровка без игры (п. 221(г)(4)) — `CALIB 5 of 5`', ROOT + '/step0/calib142.out.txt',
  ' — eatl122 K2 n 191 (окно); edes122 K2 n 4945 (удержание); atl122 ни K2, ни K3; ednn122 окно без K3, K3 удержания n 1826; '
  'eght122 K3 окна n 389 (и n 816) «тёплой базы нет»; первые кадры сцены 189 / 232 / 149 / 219 / 253 = `p221chk.out.txt` лида')
e('фикстуры скорера — %s, `%s`' % (tail(ROOT + '/step0/test_sc142.out.txt', 2)[0], tail(ROOT + '/step0/test_sc142.out.txt')[0]),
  ROOT + '/step0/test_sc142.out.txt', ' (первая строка — `suite test_sc142.py sha256 … target sc142.py sha256 …`)')
e('фикстуры цепочки — %s, `%s`' % (tail(ROOT + '/step0/test_go142a.out.txt', 2)[0], tail(ROOT + '/step0/test_go142a.out.txt')[0]),
  ROOT + '/step0/test_go142a.out.txt')
e('мутанты — зачётный полный `mutlib` 4.1 (`--control --no-memo --workers 8 --work-dir C:/kyty/s142/mutwork --cache-dir '
  'C:/kyty/s142/mutcache`, без `--changed-from`), 159 мутантов: 156 убиты, 3 выжили (`sealed_vid`, `sk_w_ok`, `su_b5a`), '
  'контроли 3/3, `fast on`, стена 117,5 с; отчёт', ROOT + '/mut_sc142.txt')
e('лог полного прогона', ROOT + '/mut_run.log')
e('набор полного прогона (копия)', ROOT + '/step0/v1/test_sc142.py')
e('доказательство «только добавление» набора (x1–x3 в конце) — `ADDONLY: PASS`', ROOT + '/step0/addonly142.out.txt')
e('добор `--only sealed_vid,sk_w_ok,su_b5a` на наборе с x1–x3: 3 из 3 убиты, контроли 3/3, стена 25,3 с; отчёт',
  ROOT + '/mut_sc142.add.txt')
e('лог добора', ROOT + '/mut_run.add.log')
e('`mutlib` v4.1', 'C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py')
e('закреплённая сборка', 'C:/kyty/s128/kyty_emulator_9235a7ac.exe')
seals = []
for name in S.SEALED_NAMES:
    p = name if name.startswith('C:/') else ROOT + '/' + name
    seals.append('seal: %s %s' % (sha(p), name))
seals = '```\n' + '\n'.join(seals) + '\n```'
t = t.replace('{WHEN}', when).replace('{CALLS}', calls).replace('{EVIDENCE}', '\n'.join(ev)).replace('{SEALS}', seals)
assert '{' + 'WHEN}' not in t and '{' + 'SEALS}' not in t
os.makedirs(ROOT + '/pred', exist_ok=True)
open(OUT, 'wb').write(t.encode('utf-8'))
print('seal written %s sha256 %s bytes %d at %s UTC' % (OUT, sha(OUT), os.path.getsize(OUT), when))
