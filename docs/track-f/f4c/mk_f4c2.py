"""mk_f4c2.py - F4c (HPP-337) continuation draft (question V5 to the lead, comment 30e2d337, 2026-10-01 13:03Z): builds
go_f4c2.sh, win_f4c2.py, test_go_f4c2.py, next_f4c2.sh, wait_f4c2.sh from the sealed go_f4c.sh / win_f4c.py /
test_go_f4c.py / next_f4c.sh / wait_f4c.sh by exact replacements (every replacement must hit its count, else rc 1).
The sealed files are not touched.  ASCII, LF.  usage: python mk_f4c2.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)


def rd(n):
    return open(os.path.join(HERE, n), 'rb').read().decode('ascii')


def wr(n, s):
    assert '\r' not in s and all(ord(c) < 128 for c in s), n
    open(os.path.join(HERE, n), 'wb').write(s.encode('ascii'))


def rep(s, a, b, count=1, name=''):
    got = s.count(a)
    if got != count:
        print('REPLACE FAILED %s: %r found %d want %d' % (name, a[:80], got, count))
        sys.exit(1)
    return s.replace(a, b)


# ---------------------------------------------------------------- go_f4c2.sh
g = rd('go_f4c.sh')
HEAD = (
    '#!/bin/bash' + NL +
    '# F4c CONTINUATION (go_f4c2.sh; question V5 to the lead in HPP-337, comment 30e2d337): the series call 2 of go_f4c.sh' + NL +
    '# (lock 13:01:06Z-13:02:02Z) ran f4c_b (letter STOP SAME TEXT) and stopped at f4c_a: enter_scene.py --require-idle refused' + NL +
    '# BUSY before the emulator start (idle142 gpu_util_median 11.0 > 10, desktop GPU load), no log, not an attempt.' + NL +
    '# This script = go_f4c.sh with: (1) SEQ (a) (v) (g), stand A only; the refused f4c_a marker set (attempt_f4c_a.txt +' + NL +
    '#   f4c_a.refused.json, no log, no json) does not block - it is moved to *.busy1.* inside the lock with a times line;' + NL +
    '# (2) before every enter_scene an idle142 wait up to IDLEMAX s (step IDLESTEP s); not idle -> series stop BUSY, the tag' + NL +
    '#   is not an attempt; (3) enter_scene rc 3 with <tag>.refused.json and no log -> not an attempt: files moved to' + NL +
    '#   *.busyr1.*, one more wait and one more call; a second refusal -> series stop BUSY.  Reading (f4c_read.py), letter,' + NL +
    '#   controls, binary, stand, caches, holds - unchanged.  Seal pred/f4c2.md, call line "go_f4c2 call: ...".' + NL +
    '# ---- the header of go_f4c.sh follows unchanged ----' + NL)
g = rep(g, '#!/bin/bash' + NL, HEAD, name='head')
g = rep(g, '  A) SEQ="f4c_b f4c_a f4c_v f4c_g";;', '  A) SEQ="f4c_a f4c_v f4c_g";;', name='seqA')
g = rep(g, '  Bp) SEQ="f4c_g f4c_b f4c_a f4c_v";;', '  Bp) SEQ="";;', name='seqBp')
g = rep(g, 'PRED="pred/f4c.md"', 'PRED="pred/f4c2.md"', name='pred')
g = rep(g, '"go_f4c call: PLWAIT="*" bash C:/kyty/f287/f4c/go_f4c.sh series")',
        '"go_f4c2 call: PLWAIT="*" bash C:/kyty/f287/f4c/go_f4c2.sh series")', name='callpat')
g = rep(g, 'V=${PLINE#go_f4c call: PLWAIT=}', 'V=${PLINE#go_f4c2 call: PLWAIT=}', name='callstrip')
g = rep(g, 'L=$ROOT/go_f4c.log', 'L=$ROOT/go_f4c2.log', name='log')
g = rep(g, 'F4c go_f4c $*', 'F4c go_f4c2 $*', name='tl')
g = rep(g, 'F4c go_f4c BUSY $1', 'F4c go_f4c2 BUSY $1', name='busyname')
n = g.count('go_f4c.sh ')
g = g.replace('log "go_f4c.sh ', 'log "go_f4c2.sh ').replace('echo "go_f4c.sh ', 'echo "go_f4c2.sh ')
g = rep(g, 'WIN=$(python $ROOT/win_f4c.py 2>&1', 'WIN=$(python $ROOT/win_f4c2.py 2>&1', name='win')
g = rep(g, 'window HPP-333/HPP-347 done, HPP-328 not waiting (win_f4c)',
        'window HPP-333/HPP-347 done, HPP-328 and HPP-352 not waiting (win_f4c2); idle142 wait before every tag up to $IDLEMAX s, one retry of a BUSY refusal',
        name='dry')
# (1) the refused f4c_a marker set does not block
OLD_ATT = ('for C in $SEQ; do' + NL +
           '  if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then' + NL)
NEW_ATT = ('busy1() {' + NL +
           '  [ "$1" = "f4c_a" ] && [ -e attempt_f4c_a.txt ] && [ -e f4c_a.refused.json ] && [ ! -e f4c_a.json ] \\' + NL +
           '    && [ ! -e log_f4c_a.txt ] && [ ! -e attempt_f4c_a.busy1.txt ]' + NL +
           '}' + NL +
           'for C in $SEQ; do' + NL +
           '  busy1 $C && continue' + NL +
           '  if [ -e "attempt_$C.txt" ] || [ -e "$C.json" ]; then' + NL)
g = rep(g, OLD_ATT, NEW_ATT, name='attempt')
OLD_LT = 'tl "lock taken (winpid $WINPID)"' + NL
NEW_LT = (OLD_LT +
          'if busy1 f4c_a; then' + NL +
          '  for F in attempt_f4c_a.txt f4c_a.refused.json f4c_a.stdout.txt score_f4c_a.txt runs/f4c_a.read.json; do' + NL +
          '    [ -e "$F" ] && mv "$F" "${F/f4c_a/f4c_a.busy1}"' + NL +
          '  done' + NL +
          '  tl "f4c_a refused marker set of the first series (call 2) moved to *f4c_a.busy1* (BUSY before the emulator start, not an attempt)"' + NL +
          'fi' + NL)
g = rep(g, OLD_LT, NEW_LT, name='locktaken')
# (2) + (3) idle wait and one retry
IDLE_FN = ('IDLEMAX=300' + NL + 'IDLESTEP=15' + NL +
           'idlewait() {' + NL +
           '  WS=0' + NL +
           '  while :; do' + NL +
           '    if [ -e $STOPF ]; then tl "$1 stop file during the idle wait: $(head -1 $STOPF)"; return 1; fi' + NL +
           '    if python $ROOT/idle142.py >> $L 2>&1; then tl "$1 idle142 IDLE after $WS s of wait"; return 0; fi' + NL +
           '    WS=$((WS+IDLESTEP))' + NL +
           '    if [ $WS -gt $IDLEMAX ]; then tl "$1 idle142 still BUSY after $IDLEMAX s of wait"; return 1; fi' + NL +
           '    sleep $IDLESTEP' + NL +
           '  done' + NL +
           '}' + NL +
           'runtag() {' + NL +
           '  echo "go_f4c2.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) fix binary $BIN_EXPECT" > attempt_$C.txt' + NL +
           '  tl "$C enter_scene start$1 (level $LV, hold $HOLD, extra \'$EXTRA\', emu \'$EMUX\')"' + NL +
           '  python $ROOT/enter_scene.py $C --level $LV --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \\' + NL +
           '    --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $C.stdout.txt 2>&1' + NL +
           '}' + NL +
           'refused() { [ "$1" = "3" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }' + NL +
           'SERIES_RC=0' + NL)
g = rep(g, 'SERIES_RC=0' + NL, IDLE_FN, name='fns')
OLD_RUN = ('  echo "go_f4c2.sh $C pid $$ attempt started $(date +%Y-%m-%dT%H:%M:%S) fix binary $BIN_EXPECT" > attempt_$C.txt' + NL +
           '  tl "$C enter_scene start (level $LV, hold $HOLD, extra \'$EXTRA\', emu \'$EMUX\')"' + NL +
           '  python $ROOT/enter_scene.py $C --level $LV --attempts 1 $SD --no-install --require-idle --gates-file $ROOT/gates_default.txt \\' + NL +
           '    --pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $C.stdout.txt 2>&1' + NL +
           '  RC=$?' + NL)
NEW_RUN = ('  if ! idlewait $C; then tl "$C series stop BUSY before the tag (not an attempt) - question to the lead"; SERIES_RC=1; break; fi' + NL +
           '  runtag ""' + NL +
           '  RC=$?' + NL +
           '  if refused $RC; then' + NL +
           '    for F in attempt_$C.txt $C.refused.json $C.stdout.txt; do mv "$F" "${F/$C/$C.busyr1}"; done' + NL +
           '    tl "$C enter_scene refused BUSY before the emulator start (not an attempt): $(grep -o \'REFUSED.*\' $C.busyr1.stdout.txt | head -1 | cut -c1-160)"' + NL +
           '    if ! idlewait $C; then tl "$C series stop BUSY before the retry (not an attempt) - question to the lead"; SERIES_RC=1; break; fi' + NL +
           '    runtag " (retry after a BUSY refusal)"' + NL +
           '    RC=$?' + NL +
           '    if refused $RC; then tl "$C second BUSY refusal before the emulator start (not an attempt) - series stop, question to the lead"; SERIES_RC=1; break; fi' + NL +
           '  fi' + NL)
g = rep(g, OLD_RUN, NEW_RUN, name='run')
g = rep(g, 'echo "usage: go_f4c.sh series  (see the header)"', 'echo "usage: go_f4c2.sh series  (see the header)"', name='usage')
g = rep(g, 'win_f4c.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go_f4c.sh sheet142.py',
        'win_f4c2.py $PRED gates_default.txt enter_scene.py idle142.py procload.py go_f4c2.sh sheet142.py', name='files')
LEFT = [x for x in g.split(NL) if not x.startswith('#') and 'go_f4c.sh' in x]
assert not LEFT, LEFT
wr('go_f4c2.sh', g)

# ---------------------------------------------------------------- win_f4c2.py
w = rd('win_f4c.py')
w = rep(w, '"""win_f4c.py - F4c (HPP-337)', '"""win_f4c2.py - F4c continuation (HPP-337, V5; win_f4c.py + HPP-352: the run step of session 145 is\nbefore track F in the lock queue, p.228(v)).  Original text:\nwin_f4c.py - F4c (HPP-337)', name='wdoc')
w = rep(w, "YIELD_TO = ('HPP-328',)", "YIELD_TO = ('HPP-328', 'HPP-352')", name='yield')
w = rep(w, "print('win_f4c %s", "print('win_f4c2 %s", name='wprint')
wr('win_f4c2.py', w)

# ---------------------------------------------------------------- test_go_f4c2.py
t = rd('test_go_f4c.py')
t = rep(t, '"""test_go_f4c.py - fixtures', '"""test_go_f4c2.py - fixtures of go_f4c2.sh (continuation, V5); port of test_go_f4c.py:\nfixtures', name='tdoc')
t = t.replace("'go_f4c.sh'", "'go_f4c2.sh'").replace("'/go_f4c.sh'", "'/go_f4c2.sh'")
t = rep(t, "print('suite test_go_f4c.py sha256 %s target go_f4c.sh sha256 %s'", "print('suite test_go_f4c2.py sha256 %s target go_f4c2.sh sha256 %s'", name='tsuite')
t = rep(t, "'  A) SEQ=\"f4c_b f4c_a f4c_v f4c_g\";;' in src and '  Bp) SEQ=\"f4c_g f4c_b f4c_a f4c_v\";;' in src)",
        "'  A) SEQ=\"f4c_a f4c_v f4c_g\";;' in src and '  Bp) SEQ=\"\";;' in src)", name='tseq')
t = rep(t, "src.index('win_f4c.py 2>&1')", "src.index('win_f4c2.py 2>&1')", count=2, name='twin')
t = rep(t, 'import win_f4c as W', 'import win_f4c2 as W', name='timport')
t = rep(t, "src.index('--pre-check $C') < src.index('python $ROOT/enter_scene.py')",
        "src.index('--pre-check $C') < src.index('  runtag \"\"')", name='tprecheck')
t = rep(t, "OPEN = {'HPP-333': ('done', None), 'HPP-347': ('done', None), 'HPP-328': ('blocked', None)}",
        "OPEN = {'HPP-333': ('done', None), 'HPP-347': ('done', None), 'HPP-328': ('blocked', None), 'HPP-352': ('blocked', None)}", name='topen')
t = rep(t, "os.path.join(HERE, 'win_f4c.py')", "os.path.join(HERE, 'win_f4c2.py')", name='twinpath')
t = rep(t, "startswith('win_f4c HPP-333 None')", "startswith('win_f4c2 HPP-333 None')", name='twinout')
t = rep(t, "open(os.path.join(FX, 'pred', 'f4c.md'), 'wb')", "open(os.path.join(FX, 'pred', 'f4c2.md'), 'wb')", name='tpred')
t = rep(t, "CALL = 'go_f4c call: PLWAIT=540 bash C:/kyty/f287/f4c/go_f4c.sh series\\n'",
        "CALL = 'go_f4c2 call: PLWAIT=540 bash C:/kyty/f287/f4c/go_f4c2.sh series\\n'", name='tcall')
t = rep(t, "'stand A tags f4c_b f4c_a f4c_v f4c_g' in out", "'stand A tags f4c_a f4c_v f4c_g' in out", name='tdryA')
OLD_BP = ("make('x.exe', 'ab', '0', pred='# seal\\n' + CALL, stand='Bp')\n"
          "rc, out = run('series', env_add=dict(DRY='1'))\n"
          "check('DRY stand Bp order (g) (b) (a) (v)', rc == 0 and 'stand Bp tags f4c_g f4c_b f4c_a f4c_v' in out, (rc, out))\n")
NEW_BP = ("make('x.exe', 'ab', '0', pred='# seal\\n' + CALL, stand='Bp')\n"
          "rc, out = run('series', env_add=dict(DRY='1'))\n"
          "check('continuation: stand Bp -> not configured rc 2', rc == 2 and 'not configured' in out, (rc, out))\n")
t = rep(t, OLD_BP, NEW_BP, name='tbp')
t = rep(t, "('strings: patched only, stand Bp -> passes the strings', b'x' + PAT, 'Bp', 'gate file bad')):",
        "('strings: patched only, stand Bp -> not configured', b'x' + PAT, 'Bp', 'not configured')):", name='tbpstr')
t = rep(t, "    check(nm, rc == 1 and want in out", "    check(nm, rc == (2 if want == 'not configured' else 1) and want in out", name='tbprc')
EXTRA = (
    "check('V5 (1) refused f4c_a marker set does not block, moved inside the lock', 'busy1 $C && continue' in src\n"
    "      and src.index('if busy1 f4c_a; then') > src.index('tl \"lock taken (winpid $WINPID)\"')\n"
    "      and '[ ! -e attempt_f4c_a.busy1.txt ]' in src and '[ ! -e log_f4c_a.txt ]' in src)\n"
    "check('V5 (2) idle wait before every tag, before the attempt marker', src.index('if ! idlewait $C; then') < src.index('  runtag \"\"')\n"
    "      and 'IDLEMAX=300\\nIDLESTEP=15\\n' in src and src.index('runtag() {') < src.index('for C in $SEQ; do\\n  if [ -e $STOPF ]'))\n"
    "check('V5 (3) one retry of a BUSY refusal, second refusal stops', src.count('runtag \"') == 2 and src.count('if refused $RC; then') == 2\n"
    "      and 'second BUSY refusal' in src and 'refused() { [ \"$1\" = \"3\" ] && [ -e $C.refused.json ] && [ ! -e log_$C.txt ] && [ ! -e $C.json ]; }' in src)\n"
    "check('V5 enter_scene call line unchanged in runtag', src.count('python $ROOT/enter_scene.py $C --level $LV --attempts 1 $SD --no-install --require-idle') == 1)\n"
    "check('V5 window yields to the session-145 run step', W.decide(dict(OPEN, **{'HPP-352': ('todo', None)})) == (5, 'closed')\n"
    "      and W.decide(dict(OPEN, **{'HPP-352': ('in_progress', 'r')})) == (5, 'closed') and W.decide(dict(OPEN, **{'HPP-352': ('done', None)})) == (0, 'open'))\n"
    "make('x.exe', 'ab', '0', pred='# seal\\n' + CALL)\n"
    "for fn in ('attempt_f4c_a.txt', 'f4c_a.refused.json'):\n"
    "    open(os.path.join(FX, fn), 'w').write('x')\n"
    "rc, out = run('series', env_add=dict(DRY='1'))\n"
    "check('V5 refused f4c_a marker set -> DRY passes', rc == 0 and out.startswith('DRY series'), (rc, out))\n"
    "open(os.path.join(FX, 'log_f4c_a.txt'), 'w').write('x')\n"
    "rc, out = run('series', env_add=dict(DRY='1'))\n"
    "check('V5 f4c_a with a log -> rc 1 (an attempt)', rc == 1 and 'attempt' in out, (rc, out))\n"
    "make('x.exe', 'ab', '0', pred='# seal\\n' + CALL)\n"
    "for fn in ('attempt_f4c_a.txt', 'f4c_a.refused.json', 'attempt_f4c_a.busy1.txt'):\n"
    "    open(os.path.join(FX, fn), 'w').write('x')\n"
    "rc, out = run('series', env_add=dict(DRY='1'))\n"
    "check('V5 second continuation (busy1 exists) -> rc 1', rc == 1 and 'attempt' in out, (rc, out))\n"
    "make('x.exe', 'ab', '0', pred='# seal\\n' + CALL)\n"
    "open(os.path.join(FX, 'attempt_f4c_a.txt'), 'w').write('x')\n"
    "rc, out = run('series', env_add=dict(DRY='1'))\n"
    "check('V5 f4c_a attempt without a refused json -> rc 1', rc == 1 and 'attempt' in out, (rc, out))\n"
    "make('x.exe', 'ab', '0', pred='# seal\\n' + CALL.replace('go_f4c2', 'go_f4c'))\n"
    "rc, out = run('series', env_add=dict(DRY='1'))\n"
    "check('V5 the old seal call line is not the continuation call -> rc 1', rc == 1, (rc, out))\n"
    "shutil.rmtree(FX, ignore_errors=True)\n"
    "print('checks %d failed %d' % (N[0], len(FAIL)))\n")
t = rep(t, "shutil.rmtree(FX, ignore_errors=True)\nprint('checks %d failed %d' % (N[0], len(FAIL)))\n", EXTRA, name='textra')
wr('test_go_f4c2.py', t)

# ---------------------------------------------------------------- wrappers
for a, b in (('next_f4c.sh', 'next_f4c2.sh'), ('wait_f4c.sh', 'wait_f4c2.sh')):
    s = rd(a)
    s = s.replace('go_f4c.sh', 'go_f4c2.sh').replace('go_series.out.txt', 'go_series2.out.txt')
    s = s.replace('wait_f4c.sh', 'wait_f4c2.sh').replace('next_f4c.sh', 'next_f4c2.sh')
    s = s.replace('F4c next_f4c ', 'F4c next_f4c2 ').replace("' F4c go_f4c '", "' F4c go_f4c2 '")
    s = s.replace('F4c go_f4c series call', 'F4c go_f4c2 series call').replace('(pred/f4c.md)', '(pred/f4c2.md)')
    s = s.replace('# F4c (HPP-337) ', '# F4c continuation (HPP-337, V5) ')
    wr(b, s)
print('mk_f4c2 OK (log replacements %d)' % n)
