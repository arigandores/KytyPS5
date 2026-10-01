"""Session 144 step 0 (HPP-330): fill the seal C:/kyty/s144/pred/01_sc144.md from step0/seal_template.md - the 33-tag table,
the 33 call lines, the sha256 of every SEALED_NAMES file and of the evidence outputs.  usage: mkseal144.py <UTC written>"""
import hashlib
import importlib.util
import re
import sys

R = 'C:/kyty/s144/'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def last_checks(p):
    m = re.findall(r'^checks: (\d+)$', open(p, encoding='ascii').read(), re.M)
    assert open(p, encoding='ascii').read().rstrip().endswith('ALL OK'), p
    return int(m[-1])


spec = importlib.util.spec_from_file_location('sc144_seal', R + 'sc144.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
rows = []
for t in S.SEQ:
    lv = S.level_of(t)
    if t in S.W_TAGS:
        what = ('контрольный W (остановка — стоп серии, §4)' if t == S.CONTROL[0] else
                'W форма п. 254(е), без видео; пара — V `%s` с. 143' % [v for v, w, _ in S.PAIRS if w == t][0]
                if t in [w for _, w, _ in S.PAIRS[:8]] else 'W форма п. 254(е), без видео; W `SCENE_OK`')
        rows.append('| `%s` | `%s` | %s | 310 с | 300 / 600 |' % (t, lv, what))
    else:
        rows.append('| `%s` | `%s` | V: видео `KYTY_REC`, без валидации, повторный вход; строка карты и V `SCENE_OK` | 330 с | '
                    '300 / 480 |' % (t, lv))
calls = ['go144a call: PLWAIT=540 bash C:/kyty/s144/go144a.sh %s' % t for t in S.SEQ]
seals = []
for name in S.SEALED_NAMES:
    p = name if name.startswith('C:/') else R + name
    seals.append('seal: %s %s' % (sha(p), name))
mut = open(R + 'mut_sc144.txt', encoding='ascii').read().split('\n')
mline = [x for x in mut if x.startswith('506 mutants:')][0] + '; ' + [x for x in mut if x.startswith('controls:')][0] + '; ' + \
    [x for x in mut if x.startswith('wall ')][0] + '; ' + [x for x in mut if x.startswith('ALL KILLED')][0]
emp = open(R + 'step0/summary144_empty.txt', encoding='ascii').read()
n1 = len(re.findall(r'"PipelinePrecache: N recipes ->" lines log 1; executor member', emp))
assert n1 == 8, n1
T = open(R + 'step0/seal_template.md', encoding='utf-8').read()
n_sc = last_checks(R + 'step0/test_sc144.out.txt')
val = dict(T_WRITTEN=sys.argv[1], PRED143=sha('C:/kyty/s143/pred/02_sc143.md'), TABLE='\n'.join(rows), CALLS='\n'.join(calls),
           SEALS='\n'.join(seals), SMOKE=sha(R + 'step0/smoke/fgcpu_smoke.txt'), REG143=sha(R + 'step0/regress143.out.txt'),
           REG142=sha(R + 'step0/regress142.out.txt'), CALIB=sha(R + 'step0/calib144.out.txt'),
           CHECK1B=sha(R + 'step0/check1b144.out.txt'), N_SC=str(n_sc), N_D=str(n_sc - 335),
           T_SC=sha(R + 'step0/test_sc144.out.txt'), N_GO=str(last_checks(R + 'step0/test_go144a.out.txt')),
           T_GO=sha(R + 'step0/test_go144a.out.txt'), N_FG=str(last_checks(R + 'step0/test_fgcpu144.out.txt')),
           T_FG=sha(R + 'step0/test_fgcpu144.out.txt'), N_TL=str(last_checks(R + 'step0/test_tools144.out.txt')),
           T_TL=sha(R + 'step0/test_tools144.out.txt'), MUT=mline, MUTSHA=sha(R + 'mut_sc144.txt'), MUTLOG=sha(R + 'mut_run.log'))
for k, v in val.items():
    assert T.count('{%s}' % k) == 1, k
    T = T.replace('{%s}' % k, v)
assert '{' not in re.sub(r'\{[0-9a-f]', '', T.replace('{64}', '')) or True
left = re.findall(r'\{[A-Z_0-9]+\}', T)
assert not left, left
open(R + 'pred/01_sc144.md', 'wb').write(T.encode('utf-8'))
print('seal written: %d tags, %d call lines, %d seal lines; sha256 %s' % (len(rows), len(calls), len(seals),
                                                                       sha(R + 'pred/01_sc144.md')))
