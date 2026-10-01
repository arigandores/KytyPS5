"""Session 145 step 0 (HPP-350): fill the seal C:/kyty/s145/pred/01_sc145.md from step0/seal_template.md - the 34-tag table,
the 34 call lines, the sha256 of every SEALED_NAMES file and of the evidence outputs.  usage: mkseal145.py <UTC written>"""
import hashlib
import importlib.util
import re
import sys

R = 'C:/kyty/s145/'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def last_checks(p, rx=r'^checks: (\d+)'):
    t = open(p, encoding='ascii').read()
    m = re.findall(rx, t, re.M)
    assert t.rstrip().endswith('ALL OK'), p
    return int(m[-1])


def tline(p, prefix):
    for line in open(R + 'step0/times.txt', encoding='ascii', errors='replace'):
        if prefix in line:
            got = line
    return got


spec = importlib.util.spec_from_file_location('sc145_seal', R + 'sc145.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
rows = []
for t in S.SEQ:
    lv = S.level_of(t)
    if t in S.W_TAGS:
        if t == S.CONTROL[0]:
            what = 'контрольный W (остановка — стоп серии, §4; 0 строк лимита слоя обязателен)'
        elif t == S.PAIRS[0][1]:
            what = 'W форма п. 254(е) + фильтр п. 273(к)(2), без видео; повтор W, пара — V `v144_09` с. 144 («Процесс» 1: не попытка уровня)'
        else:
            what = 'W форма п. 254(е) + фильтр п. 273(к)(2), без видео; W `SCENE_OK`'
        rows.append('| `%s` | `%s` | %s | 310 с | 300 / 600 |' % (t, lv, what))
    else:
        rows.append('| `%s` | `%s` | V: видео `KYTY_REC`, без валидации, холодный первый вход; строка карты и V `SCENE_OK` | 330 с | '
                    '300 / 480 |' % (t, lv))
calls = ['go145a call: PLWAIT=540 bash C:/kyty/s145/go145a.sh %s' % t for t in S.SEQ]
seals = []
for name in S.SEALED_NAMES:
    p = name if name.startswith('C:/') else R + name
    seals.append('seal: %s %s' % (sha(p), name))
mut = open(R + 'mut_sc145.txt', encoding='ascii').read().split('\n')
mline = [x for x in mut if x.startswith('631 mutants:')][0] + '; ' + [x for x in mut if x.startswith('controls:')][0] + '; ' + \
    [x for x in mut if x.startswith('wall ')][0] + '; ' + [x for x in mut if x.startswith('ALL KILLED')][0]
mwall = float(re.search(r'^wall ([\d.]+) s', [x for x in mut if x.startswith('wall ')][0]).group(1))
T = open(R + 'step0/seal_template.md', 'rb').read().decode('utf-8').replace('\r\n', '\n')
n_sc = last_checks(R + 'step0/test_sc145.out.txt')
lc = tline(R, 'live caches vs C:/kyty/s144/runs144/cache_w144_20.after.json')
val = dict(T_WRITTEN=sys.argv[1], PRED144=sha('C:/kyty/s144/pred/01_sc144.md'), TABLE='\n'.join(rows), CALLS='\n'.join(calls),
           SEALS='\n'.join(seals), F6SCAN=sha(R + 'step0/f6scan145.out.txt'), VUID=sha(R + 'step0/vuid145.out.txt'),
           LIVECACHE=sha(R + 'step0/livecache145.out.txt'), T_LIVE=lc[:20],
           REG144=sha(R + 'step0/regress144.out.txt'), REG143=sha(R + 'step0/regress143.out.txt'),
           REG142=sha(R + 'step0/regress142.out.txt'), CALIB=sha(R + 'step0/calib145.out.txt'),
           CHECK1B=sha(R + 'step0/check1b145.out.txt'), N_SC=str(n_sc), N_E=str(n_sc - 401),
           T_SC=sha(R + 'step0/test_sc145.out.txt'), N_GO=str(last_checks(R + 'step0/test_go145a.out.txt')),
           T_GO=sha(R + 'step0/test_go145a.out.txt'),
           N_GT=str(last_checks(R + 'step0/test_gate145.out.txt', r'^checks: (\d+) / ALL OK')),
           T_GT=sha(R + 'step0/test_gate145.out.txt'), N_FG=str(last_checks(R + 'step0/test_fgcpu145.out.txt')),
           T_FG=sha(R + 'step0/test_fgcpu145.out.txt'), N_TL=str(last_checks(R + 'step0/test_tools145.out.txt')),
           T_TL=sha(R + 'step0/test_tools145.out.txt'), MUT=mline, MUTSHA=sha(R + 'mut_sc145.txt'), MUTLOG=sha(R + 'mut_run.log'),
           MUTWALL='%.1f' % mwall, MUTSUM='%.0f' % (266.4 + 84.5 + 600 + mwall))
for k, v in val.items():
    assert T.count('{%s}' % k) == 1, k
    T = T.replace('{%s}' % k, v)
left = re.findall(r'\{[A-Z_0-9]+\}', T)
assert not left, left
assert len(rows) == 34 and len(calls) == 34 and len(seals) == 27
open(R + 'pred/01_sc145.md', 'wb').write(T.encode('utf-8'))
print('seal written: %d tags, %d call lines, %d seal lines; sha256 %s' % (len(rows), len(calls), len(seals),
                                                                       sha(R + 'pred/01_sc145.md')))
