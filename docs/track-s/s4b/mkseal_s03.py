#!/usr/bin/env python3
"""mkseal_s03.py (S4b, HPP-349) - writes the seal C:/kyty/s288/pred/03_s.md of track S (ROADMAP "SESSION 122" item 265).
Port of s3b/mkseal_s.py: the constants (section 1 of seal 02) are copied verbatim from pred/02_s.md (item 265 changes no
constant); the plan of every arm is the output of DRY=2 bash go_s.sh <tag> verbatim; every sha line is computed here; the
census of the 13 RX_* is copied from s4b/census_s03.out.txt.  Seal 02 is not changed.  ASCII only.
Refuses when the seal exists (a seal is never rewritten)."""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/s288')
import sc_s as S  # noqa: E402

ROOT = 'C:/kyty/s288'
OUT = 'C:/kyty/s288/pred/03_s.md'
P02 = 'C:/kyty/s288/pred/02_s.md'
if os.path.exists(OUT):
    print('seal exists, refuse')
    sys.exit(3)
assert S.PRED_PATH == OUT and S.PRED_02 == P02 and S.PRED_S6 == 'C:/kyty/s288/pred/04_s.md', S.PRED_PATH
BASH = 'C:/Program Files/Git/bin/bash.exe'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(P02) == S.SHA_02
assert sha(ROOT + '/s4/log_c1_0.txt') == '49d0a5222ef568553808c8c34989b1a743e860a2bc39fd2c33ee7a8b9032d902'


def path(n):
    return n if n.startswith('C:/') else '%s/%s' % (ROOT, n)


def plan(tag):
    env = dict(os.environ, DRY='2', PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    p = subprocess.run([BASH, ROOT + '/go_s.sh', tag], capture_output=True, text=True, env=env, timeout=120)
    lines = [x for x in (p.stdout + p.stderr).splitlines() if x.startswith('PLAN ')]
    assert p.returncode == 0 and len(lines) == 1, (tag, p.returncode, p.stdout, p.stderr)
    return lines[0]


t02 = open(P02, 'rb').read().decode('ascii').splitlines()
i1 = t02.index('## 1. Constants (item 241 numbered by its sub-items; changes of item 250 marked)')
i2 = [i for i, x in enumerate(t02) if x.startswith('## 2. ')][0]
CONST = t02[i1 + 1:i2]
s4 = [a['tag'] for a in S.ARMS if a['link'] == 's4']
done = list(S.SEAL02_TAGS)
assert s4[:len(done)] == done, s4[:6]
after = s4[len(done):]
s6 = [a['tag'] for a in S.ARMS if a['link'] == 's6']
census = [x for x in open(ROOT + '/s4b/census_s03.out.txt', 'rb').read().decode('ascii').splitlines()]
L = []
w = L.append
w('# Seal 03_s - track S link S4b (HPP-349): RX_SHADER reads a label with a space; the S4 arms after c1_0 and the recount of'
  ' c1_0 (ROADMAP "SESSION 122" item 265, on items 241, 245, 247, 250, 260)')
w('')
w('Written by C:/kyty/s288/s4b/mkseal_s03.py after S4 stopped at c1_0 (S4 times.txt 06:23:29Z) and before any S4 arm after')
w('c1_0.  It replaces seal 02 (pred/02_s.md, sha256 %s, not changed) for the S4 arms after c1_0 (item 265,' % S.SHA_02)
w('(b): the prohibition of item 260 (g) is fulfilled in the form of a new seal).  The arms made under seal 02 (%s) are' % ' '.join(done))
w('not repeated; the scorer of this seal admits them against seal 02 (its sha256 is pinned in sc_s.py SHA_02) and recounts')
w('c1_0 from the same log (item 265 (g)).  The S6 arms are NOT callable with this seal: their seal is pred/04_s.md (item 265')
w('(e)) with the line "pcw binary: <sha256> <path>"; the debts of item 260 (g) (pcw_val admission rows), item 263 (g) (a restore')
w('fixture on every real source of an arm) and the RX_PCWOV fixture from a real line of the S-pcw binary go to seal 04.  After')
w('this seal the scorer, the fixtures, the mutants, the harness and the cache tool do not change (a change = a new seal).')
w('ASCII only.')
w('')
w('## 0. What item 265 changed (and nothing else)')
w('')
for line in (
        '- (v)(1) RX_SHADER: the label group (\\S+) -> (.+?) (sc_s.py, the RX_SHADER line); the emulator writes "AvTrace: shader %s'
        ' hash=0x%016..." with label "ShaderRecompiler VS" (4fc501f4:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:3916);'
        ' s4/log_c1_0.txt (sha256 49d0a522...2d902): 17 lines of the form, seal 02 matched 0, seal 03 matches 17.',
        '- (v)(2) fixtures (test_sc_s.py section 12): S4b-1 the real line 232419 of log_c1_0.txt byte for byte; S4b-2 a one-word'
        ' label; S4b-3 the order of the branches on the real shader-emit (232401) / shader-cache save (232417) / shader-spec'
        ' (232418) lines - none enters s[sh]; S4b-4 a T arm with the real lines (T-3 1 / 1, gate "cold").',
        '- (v)(3) the census of the 13 RX_* on log_c1_0.txt and the four sw_* logs (s4b/census_s03.out.txt, below); no other'
        ' expression of the class diverges; RX_PCWOV: the form on a real log is not checked (0 lines: the S-pcw binary is not'
        ' installed) - a debt of seal 04.',
        '- (v)(6) seal names: S4 PRED_PATH pred/03_s.md, S6 PRED_S6 pred/04_s.md (item 265 (e)); go_s.sh: only the seal paths'
        ' (s4 -> pred/03_s.md, s6 -> pred/04_s.md and two comment lines); test_go_s.py: the same two names.',
        '- executor variant V13: the arms of SEAL02_TAGS are admitted against seal 02 (PRED_02, SHA_02 pinned; a file with another'
        ' sha256 admits none) by the row "prereg = the seal of its run 02_s.md (item 265 (g))"; every other S4 arm by the row'
        ' "prereg = the seal now" against this seal.  Without it the recount of c1_0 and every later reading of C1 under this seal'
        ' would fail the prereg admission row of seal 02.  Fixtures S4b-5, -5b, -5c, -7.',
        '- executor variant V14: --tag <tag> --json-out <path> writes the score json to <path> (default runs_s/<tag>.score.json'
        ' as before) - the files of seal 02 are not rewritten (item 265 (v)(7)).  Fixture S4b-6.'):
    w(line)
w('')
w('Census of the 13 RX_* (s4b/census_rx.py on the scorer of this seal; form = the line prefix the scorer dispatches on):')
w('')
w('```')
for x in census:
    w(x)
w('```')
w('')
w('## 1. Constants - section 1 of seal 02 verbatim (item 265 changes no constant, threshold, window or rule)')
for x in CONST:
    w(x)
w('## 2. Call lines of S4 after c1_0 (one per tag; PLWAIT=540, item 105 (v)) and the plan of every arm (DRY=2, verbatim)')
w('')
w('The arms %s were made under seal 02 and have no call line here (go_s.sh refuses them: no call line, and the attempt' % ' '.join(done))
w('marker / json exists).  The order of item 260 (d) holds: the next tag is the one sc_s.py --allowed admits.')
w('')
for t in after:
    w('go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s' % t)
w('')
w('```')
for t in after:
    w(plan(t))
w('```')
w('')
w('## 3. The plan of every S6 arm (DRY=2, verbatim) - NOT callable with this seal (seal 04, item 265 (e))')
w('')
w('```')
for t in s6:
    w(plan(t))
w('```')
w('')
w('## 4. The recount of c1_0 (item 265 (v)(7), (g)) - the same log, not a repeat')
w('')
w('- the log s4/log_c1_0.txt sha256 49d0a5222ef568553808c8c34989b1a743e860a2bc39fd2c33ee7a8b9032d902 is checked before the read;')
w('- recount call: python C:/kyty/s288/sc_s.py --tag c1_0 --json-out C:/kyty/s288/s4/c1_0.s03.json > C:/kyty/s288/s4/score_c1_0.s03.txt')
w('- the files of seal 02 for c1_0 (s4/score_c1_0.txt, s4/runs_s/c1_0.score.json) are not deleted and not rewritten.')
w('')
w('## 5. Seal lines (sc_s.py --check-seal checks each before every lock)')
w('')
for n in S.SEALED_NAMES:
    w('seal: %s %s' % (sha(path(n)), n))
w('')
w('## 6. Binary and the evidence of the link')
w('')
w('- S4 arm binary: C:/kyty/s128/kyty_emulator_9235a7ac.exe sha256 %s; the build installed before each arm is copied and'
  ' returned after it (item 250 (b)) - whatever it is.' % sha('C:/kyty/s128/kyty_emulator_9235a7ac.exe'))
w('- seal 02 (the arms %s): pred/02_s.md sha256 %s (= SHA_02 of sc_s.py).' % (' '.join(done), sha(P02)))
for name, p in (('fixtures sc_s', 's4b/test_sc_s.out.txt'), ('fixtures cachex', 's4b/test_cachex_s.out.txt'),
                ('fixtures harness', 's4b/test_go_s.out.txt'),
                ('inherited fixtures sc142 (217)', 's4b/test_sc142_inherited.out.txt'),
                ('regression 12 sc142 logs (byte-equal to s3b/regress_s.out.txt of seal 02)', 's4b/regress_s.out.txt'),
                ('sw_* regression (four logs, byte-equal to score_sw_*.txt of seal 02 except line 13, the prereg row name)',
                 's4b/reg_sw.out.txt'),
                ('census of the 13 RX_*', 's4b/census_s03.out.txt'),
                ('mutants (counted full run)', 's4b/mut_sc_s.txt'), ('snap0 index', 's3/snap0_index.json')):
    full = path(p)
    lines = open(full, 'rb').read().decode('ascii', 'replace').splitlines()
    tail = [x for x in lines if x.startswith(('checks:', 'ALL OK', 'REGRESSION:', 'ALL KILLED', 'SW REGRESSION:', 'CENSUS:'))]
    w('- %s: %s sha256 %s; %s' % (name, p, sha(full), ' / '.join(tail) or '-'))
w('')
w('## 7. Executor variants (questions to the lead in the link report)')
w('')
i7 = t02.index('## 6. Executor variants (questions to the lead in the link report)')
i8 = [i for i, x in enumerate(t02) if x.startswith('## 7. ')][0]
for x in t02[i7 + 1:i8]:
    if x.startswith('- V8 (S3b)'):
        x = x + '  Item 265 (e): the S6 seal is pred/04_s.md.'
    if x:
        w(x)
w('- V13 (S4b) the seal 02 arms admitted against seal 02 - section 0.')
w('- V14 (S4b) --json-out - section 0.')
w('- V15 (S4b) RX_SHADER (.+?) - the choice of item 265 (v)(1); a mutant (\\S+ \\S+) is killed by the one-word label fixture.')
w('')
w('## 8. Not claimed (item 265 (i))')
w('')
w('- that c1_0 is cold or warm before the recount by this seal; that sc_s.py has no other reading defect (the census reads one'
  ' T log and four M/T warm logs); that the harness runs the rest of the S4 path without an error; that the entry freezes'
  ' are caused by the shaders; no number is a gain; 60 FPS is not promised; goal (B) does not change.')
w('')
text = '\n'.join(L) + '\n'
with open(OUT, 'wb') as f:
    f.write(text.encode('ascii'))
print('seal %s sha256 %s lines %d call lines %d seal lines %d' % (OUT, sha(OUT), len(L), len(after), len(S.SEALED_NAMES)))
