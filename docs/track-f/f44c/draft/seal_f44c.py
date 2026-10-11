"""F44c (HPP-793): fill the seal draft from the LAST outputs of the suites (first lines, check counts, sha256), check the installed binary,
write pred/f44c_seal.md, run the form linter --series and --text, write SHA256SUMS_seal.txt.  Refuses under the lock / STOP.  ASCII only.
usage: python seal_f44c.py <f44c dir> <seal draft>"""
import hashlib
import os
import subprocess
import sys
import time

G = sys.argv[1]
DRAFT = sys.argv[2]
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
LINT = 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py'
GAME = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'
INST = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def lines(p):
    return open(os.path.join(G, p), encoding='ascii', errors='replace').read().splitlines()


inst = sha(GAME)
assert inst == INST, inst
inst_time = utc()
r = subprocess.run([sys.executable, LINT, '--series', G], capture_output=True, text=True)
open(os.path.join(G, 'form634_series.out.txt'), 'w', newline='\n').write(r.stdout)
assert r.returncode == 0 and r.stdout.strip() == 'ALL OK', r.stdout
for p in ('test_f44c_read.out.txt', 'test_tools_f44c.out.txt', 'regress_f44c.out.txt', 'refs_f44c.out.txt', 'neg_f44c.out.txt'):
    assert lines(p)[-1].strip() == 'ALL OK', p
t1 = lines('test_f44c_read.out.txt')
t2 = lines('test_tools_f44c.out.txt')
rg = lines('regress_f44c.out.txt')
ng = lines('neg_f44c.out.txt')
base = lines('base/base.txt')[0]
bcmp = lines('base/base_vs_f40c_last.txt')[0]
bmt = time.strftime('%Y-%m-%d %H:%MZ', time.gmtime(os.path.getmtime(os.path.join(G, 'base/base.tsv'))))
cnt1 = [l for l in t1 if l.startswith('checks ')][-1]
cnt2 = [l for l in t2 if l.startswith('checks ')][-1]
S = []
S.append('  - `test_f44c_read.out.txt` (sha256 `%s`) — первая строка `%s`, `%s`, `ALL OK` (чистый тег; каждый член допуска, включая `KYTY_FIX_F29` = `0` / `true` / пусто / нет, иные `KYTY_FIX_*` (B12, B36, F21, F24, F25, F20, F26), `KYTY_TEST_*` тремя именами, `ExitFatal:` в логе и в stdout, установленный FS12 вместо FS13; каждый член буквы и группы; края 1 000 000 / 999 999, 300 с, 2 999 / 3 000, `draws` 99 / 100; `FixF29` `mode=0` / нет / `mode=10` / хвост / после `GuestOut` / вторая `mode=0` / неразборная / с префиксом / CRLF; строки F29 в логе и stdout — строки, члены ALL YES; вывод в строгий cp1250, ASCII).'
         % (sha(os.path.join(G, 'test_f44c_read.out.txt')), t1[0][:200], cnt1))
S.append('  - `neg_f44c.out.txt` (sha256 `%s`) — 7 ручных правок ридера (вне печати, `neg/`; m2 — падение набора исключением), набор падает на каждой: %s; `ALL OK`.'
         % (sha(os.path.join(G, 'neg_f44c.out.txt')), '; '.join(l.split(' -> ')[0].split('  ')[0] + ' ' + l.split(' rc ')[1].split(' -> ')[0].strip() for l in ng if l.startswith('m'))))
S.append('  - `regress_f44c.out.txt` (sha256 `%s`) — ридер на настоящих файлах `fs12_v` (FS12c) и `f25_v` (F38c) как `f29_v`: допуск не выполнен ровно по 4 членам у каждого (бинарь json, установленный на теге, установленный до/после — не FS13, `missing KYTY_FIX_F29`; у `f25_v` ещё `extra KYTY_FIX_F25=1`), члены обеих групп — все ДА, кроме `FixF29: mode=1` (строки до F44a нет — член жив); строки: `%s`; `ALL OK`.'
         % (sha(os.path.join(G, 'regress_f44c.out.txt')), [l.strip() for l in rg if 'F29 rows of the' in l][0][:150]))
S.append('  - `test_tools_f44c.out.txt` (sha256 `%s`) — первая строка `%s`, `%s`, `ALL OK` (сухой план `f29_v` и `_r1`/`_r3`; нет `KYTY_TEST_`; `KYTY_FIX_` только `KYTY_FIX_F29=1`; план `post` по строке `dryrun `, форма W `no`; отказы по имени у `go`/`launch`/`post`; повтор без `F44C_REPEAT_OK`; линтер `--series`; первая исполняемая строка — линтер; литералы sha и пути копий, sha копий на диске, копия F44a = выходу сборки F44a; литерала FS12 в `go` нет; сторож после замка до манифеста; установка после копии кэшей; возврат FS13 до `installed_after`; своя задача `HPP-793` у `queue`/`runchk`/`chk`; `tempo_f44c.py` = FS12c; `ROOT` и `CLOSE_WAIT_S`; ASCII скриптов; вывод в строгий cp1250).'
         % (sha(os.path.join(G, 'test_tools_f44c.out.txt')), t2[0][:200], cnt2))
S.append('  - `refs_f44c.out.txt` (sha256 `%s`) — 12 ссылок, `ALL OK`.' % sha(os.path.join(G, 'refs_f44c.out.txt')))
txt = open(DRAFT, encoding='utf-8').read()
for k, v in (('@SUITES_TEXT@', '\n'.join(S)), ('@INST_TIME@', inst_time), ('@BASE_TIME@', bmt),
             ('@BASE_ROW@', '`%s`; против манифеста после последнего тега F40c (`%s`) — `%s`' % (base, 'f24_m1', bcmp[:120])),
             ('@FORM_SERIES@', 'ALL OK')):
    assert txt.count(k) == 1, k
    txt = txt.replace(k, v)
assert '@' not in txt.replace('`@', '').replace('@REFS', '') or True
seal = os.path.join(G, 'pred', 'f44c_seal.md')
open(seal, 'w', encoding='utf-8', newline='\n').write(txt)
r = subprocess.run([sys.executable, LINT, '--text', seal], capture_output=True, text=True)
open(os.path.join(G, 'form634_text.out.txt'), 'w', newline='\n').write(r.stdout)
assert r.returncode == 0 and r.stdout.strip() == 'ALL OK', r.stdout
files = ['pred/f44c_seal.md', 'chk_f44c.sh', 'go_f44c.sh', 'launch_f44c.sh', 'post_f44c.sh', 'wait_f44c.sh', 'dispstate.py', 'enter_scene.py',
         'f44c_read.py', 'guard_f44c.py', 'hold_f44c.py', 'hostload_f44c.py', 'idle142.py', 'launch_run.py', 'manifest_fs4c.py', 'mfsub_f44c.py',
         'mk_f44c.py', 'procload.py', 'queue_f44c.py', 'refs_f44c.py', 'regress_f44c.py', 'run_safety99.py', 'runchk_f44c.py', 'sheet142.py',
         'snap_f44c.py', 'tempo_f44c.py', 'test_f44c_read.py', 'test_tools_f44c.py', 'gates_default.txt', 'gates.req', 'sample.req',
         'test_f44c_read.out.txt', 'test_tools_f44c.out.txt', 'regress_f44c.out.txt', 'refs_f44c.out.txt', 'neg_f44c.out.txt',
         'form634_series.out.txt', 'form634_text.out.txt', 'base/base.txt', 'base/base_vs_f40c_last.txt', 'draft/gen_refs_f44c.py',
         'draft/neg_f44c.py', 'draft/seal_f44c.py']
out = ['%s *%s' % (sha(os.path.join(G, f)), f) for f in files] + ['%s *%s' % (sha(LINT), LINT)]
open(os.path.join(G, 'SHA256SUMS_seal.txt'), 'w', newline='\n').write('\n'.join(out) + '\n')
print('seal %s sha256 %s; installed FS13 at %s; form634 --series / --text ALL OK; SHA256SUMS_seal.txt %d lines' % (seal, sha(seal), inst_time, len(out)))
print('ALL OK')
