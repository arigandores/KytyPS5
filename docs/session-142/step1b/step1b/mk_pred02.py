"""Link 1b (HPP-282): fill pred/02_sc142.md from step1b/pred02_template.md (evidence and seal lines with sha256).  Writes LF,
UTF-8; prints ASCII.  Refuses to overwrite an existing seal."""
import datetime
import hashlib
import importlib.util
import os
import sys

ROOT = 'C:/kyty/s142'
OUT = ROOT + '/pred/02_sc142.md'
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
cache = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564'
cache_n = len(os.listdir(cache))
t = open(ROOT + '/step1b/pred02_template.md', encoding='utf-8').read()
when = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
ev = []


def e(label, path, extra=''):
    ev.append('- %s: `%s` sha256 `%s`%s' % (label, path, sha(path), extra))


B = ROOT + '/step1b/'
e('калибровка без игры заново (п. 221(г)(4), п. 224(б)(2)) — `%s`' % tail(B + 'calib142_1b.out.txt')[0], B + 'calib142_1b.out.txt',
  ' — байт в байт как вывод шага 0 `step0/calib142.out.txt`: eatl122 K2 n 191 (окно); edes122 K2 n 4945 (удержание); atl122 ни K2, '
  'ни K3; ednn122 K3 удержания n 1826; eght122 K3 окна n 389 (и 816); первые кадры 189 / 232 / 149 / 219 / 253')
e('строки проверки п. 224(б)(2) (`sc142.py --check1b`) — `%s`' % tail(B + 'check1b.out.txt')[0], B + 'check1b.out.txt',
  ' — `s1s128` K2 (первый маркер `ErrorDeviceLost` лог@67220450 раньше `--- Fatal Error ---` @67220621), `s2s128` K2 '
  '(`ErrorDeviceLost` @21410236 раньше @21410352), `s6s137` validation active (0 / 1 / 440 084)')
e('фикстуры скорера — %s, `%s`' % (tail(B + 'test_sc142.out.txt', 2)[0], tail(B + 'test_sc142.out.txt')[0]),
  B + 'test_sc142.out.txt', ' (первая строка — `suite test_sc142.py sha256 … target sc142.py sha256 …`)')
e('фикстуры цепочки — %s, `%s`' % (tail(B + 'test_go142a.out.txt', 2)[0], tail(B + 'test_go142a.out.txt')[0]),
  B + 'test_go142a.out.txt')
e('мутанты — ОДИН зачётный полный `mutlib` 4.1 звена 1б (`--control --no-memo --workers 8 --work-dir C:/kyty/s142/mutwork1b '
  '--cache-dir C:/kyty/s142/mutcache1b`, без `--changed-from`), 245 мутантов (157 шага 0 с перенесёнными якорями, 88 новых): 242 '
  'убиты, 3 выжили (`half`, `sk_v_att_ok`, `ma_nojs`), контроли 3/3, `fast on`, стена 410,2 с (прогноз 548 с); отчёт',
  ROOT + '/mut_sc142_1b.txt')
e('лог полного прогона', ROOT + '/mut_run1b.log')
e('набор полного прогона (копия)', B + 'v1/test_sc142.py')
e('доказательство «только добавление» набора (y1–y3 в конце) — `ADDONLY: PASS`', B + 'addonly142_1b.out.txt')
e('добор `--only half,sk_v_att_ok,ma_nojs` на наборе с y1–y3: 3 из 3 убиты, контроли 3/3, стена 56,6 с; отчёт',
  ROOT + '/mut_sc142_1b.add.txt')
e('лог добора', ROOT + '/mut_run1b.add.log')
ev.append('- стена всех прогонов мутантов с. 142: шаг 0 117,5 + 25,3 = 142,8 с; звено 1б 410,2 + 56,6 = 466,8 с; всего 609,6 с '
          '(≈ 10,2 мин из бюджета 30 мин, п. 84–85)')
e('печать шага 0 до пометки «заменена» (копия)', B + 'v0/01_sc142.md')
e('скорер шага 0 (копия, для разности аудита шага 3)', B + 'v0/sc142.py')
e('`mutlib` v4.1', 'C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py')
e('закреплённая сборка', 'C:/kyty/s128/kyty_emulator_9235a7ac.exe')
seals = []
for name in S.SEALED_NAMES:
    p = name if name.startswith('C:/') else ROOT + '/' + name
    seals.append('seal: %s %s' % (sha(p), name))
t = (t.replace('{WRITTEN}', when).replace('{CACHE_N}', str(cache_n)).replace('{EVIDENCE}', '\n'.join(ev))
     .replace('{SEALS}', '\n'.join(seals)))
assert '{' + 'WRITTEN}' not in t and '{' + 'SEALS}' not in t and '{' + 'EVIDENCE}' not in t and '{' + 'CACHE_N}' not in t
open(OUT, 'wb').write(t.encode('utf-8'))
print('seal written %s sha256 %s bytes %d at %s UTC; cache files %d' % (OUT, sha(OUT), os.path.getsize(OUT), when, cache_n))
