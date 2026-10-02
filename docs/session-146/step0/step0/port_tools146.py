"""port_tools146.py - session 146 step 0 (HPP-386): builds the chain, gate, wrappers and tools of s146 from the s145 files by
anchored replacements (each anchor exactly the named number of times).  Writes LF bytes, ASCII only; prints source and target
sha256 of every file.  No logic of a scorer here (sc146.py: port_sc146.py)."""
import hashlib
import os
import sys

S5 = 'C:/kyty/s145'
S6 = 'C:/kyty/s146'
NEW146 = ('robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit',
          'collectible_viewer', 'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo',
          'fragile_battle_1', 'voxel_challenge_1', 'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2',
          'fragile_battle_3')
RECHECK = (('r146_01', 'hoover_beach'), ('r146_02', 'sponge_dirty_bath'), ('r146_03', 'timestop_casino'),
           ('r146_04', 'bonus_path_maker_mix'))
SEQ = ['w146_00'] + [r for r, _ in RECHECK] + [x for i in range(5, 20) for x in ('v146_%02d' % i, 'w146_%02d' % i)]
OK = [True]


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Doc:
    def __init__(self, src):
        self.src = src
        self.b = open(src, 'rb').read()
        assert b'\r' not in self.b, src
        self.t = self.b.decode('ascii')

    def rep(self, old, new, count=1):
        n = self.t.count(old)
        if n != count:
            print('ANCHOR %s %d != %d: %r' % (self.src, n, count, old[:100]))
            OK[0] = False
            return self
        self.t = self.t.replace(old, new)
        return self

    def write(self, dst):
        bad = [i for i, c in enumerate(self.t) if ord(c) > 127]
        if bad:
            print('NON-ASCII %s at %s' % (dst, bad[:3]))
            OK[0] = False
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'wb').write(self.t.encode('ascii'))
        print('port %s %s -> %s %s' % (self.src, sha(self.b)[:16], dst, sha(self.t.encode('ascii'))[:16]))


# ---------------- go146a.sh
d = Doc(S5 + '/go145a.sh')
d.rep('''#!/bin/bash
# Session 145 step 0 (HPP-350;''', '''#!/bin/bash
# Session 146 step 0 (HPP-386; ROADMAP s.0.1 "SESSION 122" item 309 (k), (l)(1)-(7), item 300 (b)(4), item 281 (g); brief
# docs/next-session-146.md): the game chain of the SCENE_OK series sc146 on the INSTALLED track F shipment binary dac02fb9 with
# its shipped defaults (an EMPTY gate file), installed by step 0 (go146i.sh, pred/00_i146.md).  Port of C:/kyty/s145/go145a.sh
# (pred/03_sc145.md): the same lock, guards, one attempt, order, seal call line, stop file, cache count and manifests, foreign-
# CPU row, winpid lock line - with the 35 tags of item 309 (l)(2), the W form of item 300 (b)(4) (precache by default: NO
# KYTY_PIPELINE_PRECACHE; the duplicate limit 100000000 and NO message filter of item 295), the skip of a W whose V is
# NOT_ENTERED (item 309 (k)(1)), the tile events of every V video (tiles146.py, D-4) and the BUSY row with <app> ("Process" 5).
#   TAGS AND ORDER (item 309 (l)(2); one call each, exactly this order):
#     w146_00            the control W on Sky Garden (underwater_aerial_garden)
#     r146_01..r146_03   V of the re-check of hoover_beach, sponge_dirty_bath, timestop_casino (item 300 (g))
#     r146_04            the second hold V of bonus_path_maker_mix (p of B40)
#     v146_NN, w146_NN   NN = 05..19, V then W per level of the list of step 0 (step0/lvl146.py, accepted by the lead)
#   V: -lvl entry, shipped defaults, video KYTY_REC, hold VHOLD=330 s, --stable-draws 300 --timeout 480, --attempts 1.
#   W: --vulkan-validation true with VK_LAYER_PATH and VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP (100000000), precache by
#     default, NO VK_LAYER_MESSAGE_ID_FILTER; no video, hold WHOLD=310 s, --stable-draws 300 --timeout 600, --attempts 1.
#   SKIP (item 309 (k)(1)): a W of a pair whose V is NOT_ENTERED (sc146.py --skip-w, from the V's score.json, else its log) is
#     not called: skipped_<tag>.txt + a times row "SKIPPED_V_NOT_ENTERED", rc 0, no lock, not an attempt.
#   STOP RULES (item 273 (k)(4), 309 (l)(5)): every call refuses rc 5 when sc146.py --stop-check finds the control W stopped
#     (incl. its layer limit lines and the DualSrcBlend line of item 300 (b)(4)), two W in a row stopped before the first
#     GuestOut line with one key, three V in a row not entered with one marker, or a window event on the made tag right before.
# Session 145 header (carried):
# Session 145 step 0 (HPP-350;''')
d.rep('''ROOT=C:/kyty/s145
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s145/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"
BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"''', '''ROOT=C:/kyty/s146
LOCK=/c/kyty/SEALED_RUN.lock
STOPF=/c/kyty/s146/STOP
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
BUILD_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"
BUILD_PINNED="/c/kyty/s146/kyty_emulator_dac02fb9.exe"''')
d.rep('PRED="pred/03_sc145.md"', 'PRED="pred/01_sc146.md"')
d.rep('SC="sc145.py"', 'SC="sc146.py"')
d.rep('''SEQ="w145_00 w145_01 v145_02 w145_02 v145_03 w145_03 v145_04 w145_04 v145_05 w145_05 v145_06 w145_06 v145_07 w145_07 v145_08 w145_08 v145_09 w145_09 v145_10 w145_10 v145_11 w145_11 v145_12 w145_12 v145_13 w145_13 v145_14 w145_14 v145_15 w145_15 v145_16 w145_16 v145_17 w145_17"''',
      'SEQ="%s"' % ' '.join(SEQ))
cases = ['  w146_00) LEVEL=underwater_aerial_garden;;'] + ['  %s) LEVEL=%s;;' % (r, lv) for r, lv in RECHECK] + [
    '  v146_%02d|w146_%02d) LEVEL=%s;;' % (i + 5, i + 5, lv) for i, lv in enumerate(NEW146)]
old_cases = d.t[d.t.index('  w145_00) LEVEL=underwater_aerial_garden;;'):d.t.index('  *) echo "usage: go145a.sh')]
d.rep(old_cases, '\n'.join(cases) + '\n')
d.rep('''  *) echo "usage: go145a.sh w145_00 | w145_01 | v145_02|w145_02 .. v145_17|w145_17  (see the header)"; exit 2;;''',
      '''  *) echo "usage: go146a.sh w146_00 | r146_01..r146_04 | v146_05|w146_05 .. v146_19|w146_19  (see the header)"; exit 2;;''')
d.rep('L=$ROOT/go145a.log', 'L=$ROOT/go146a.log')
d.rep('OUT=$ROOT/runs145', 'OUT=$ROOT/runs146')
d.rep('''busy() { log "go145a.sh $T refused BUSY''', '''busy() { log "go146a.sh $T refused BUSY''')
d.rep('''      "go145a call: PLWAIT="*" bash C:/kyty/s145/go145a.sh $T")
        V=${PLINE#go145a call: PLWAIT=}''', '''      "go146a call: PLWAIT="*" bash C:/kyty/s146/go146a.sh $T")
        V=${PLINE#go146a call: PLWAIT=}''')
d.t = d.t.replace('go145a.sh $T', 'go146a.sh $T').replace('"go145a.sh ', '"go146a.sh ')
d.rep('''if [ -e "$MARK" ] || [ -e "$T.json" ]; then
  log "go146a.sh $T refused: $MARK or $T.json exists - the one attempt of $T was made (item 273 (k)(2): --attempts 1, no repeat)"''',
      '''if [ -e "$MARK" ] || [ -e "$T.json" ] || [ -e "skipped_$T.txt" ]; then
  log "go146a.sh $T refused: $MARK, $T.json or skipped_$T.txt exists - the one call of $T was made (item 309 (l)(3): --attempts 1, no repeat)"''')
d.rep('''if [ -n "$PREV" ] && [ ! -e "attempt_$PREV.txt" ] && [ ! -e "$PREV.json" ]; then
  log "go146a.sh $T refused: the call $PREV before it was not made (item 273 (k)(1): the sealed order)"''',
      '''if [ -n "$PREV" ] && [ ! -e "attempt_$PREV.txt" ] && [ ! -e "$PREV.json" ] && [ ! -e "skipped_$PREV.txt" ]; then
  log "go146a.sh $T refused: the call $PREV before it was not made (item 309 (l)(2): the sealed order)"''')
d.rep('''  v145_*) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec";;
  w145_*) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD
          EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0";;''',
      '''  v146_*|r146_*) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec";;
  w146_*) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD
          EMUX="--emu-arg=--vulkan-validation --emu-arg=true"
          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP";;''')
d.rep('''  echo "DRY $T: level $LEVEL; stop file?; lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; $SC --check-seal; $SC --stop-check $T; cpu < 15;''',
      '''  echo "DRY $T: level $LEVEL; stop file?; lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; $SC --check-seal; $SC --stop-check $T; W of a pair: $SC --skip-w $T (rc 0 -> skipped_$T.txt, SKIPPED_V_NOT_ENTERED, no lock); cpu < 15;''')
d.rep('''cache manifest before (cachemf145); lock with winpid (runs145/lock.log UTC); fgcpu145 --save;''',
      '''cache manifest before (cachemf146); lock with winpid (runs146/lock.log UTC); fgcpu146 --save;''')
d.rep('''log sha; cache manifest after (cachemf145); glitch+sheet ${REC:-none}; $SC --tag $T; restore $BUILD_PINNED; fgcpu145 --since --chain-pid (times.txt row); unlock"''',
      '''log sha; cache manifest after (cachemf146); glitch+sheet+tiles146 ${REC:-none}; $SC --tag $T; restore $BUILD_PINNED; fgcpu146 --since --chain-pid (times.txt row); unlock"''')
d.rep('''  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\\$_.CommandLine -match 'mut_[a-z0-9_]*145|test_[a-z0-9_]*145|mutlib' -or''',
      '''  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { (\\$_.CommandLine -match 'mut_[a-z0-9_]*146|test_[a-z0-9_]*146|mutlib' -or''')
d.rep('''  # item 231 (z)(5): the BUSY row of step2/times.txt names the process of the last "procload: busy" line of go145a.log,
  # read by the same command that writes the row.
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go145a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | cut -c1-300)" >> $TIMES''',
      '''  # item 231 (z)(5) and "Process" 5 of s145 (item 309 (i)): the BUSY row of step2/times.txt carries the last "procload: busy"
  # line of go146a.log with every process name replaced by <app> (the pid and the rate stay), read by the same command.
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | sed -E "s/\\('[^']*'/('<app>'/g" | cut -c1-300)" >> $TIMES''')
d.rep('''if [ "$SRC" != "0" ]; then log "stop-check rc $SRC - not starting"; echo "stop-check failed"; exit 1; fi
''', '''if [ "$SRC" != "0" ]; then log "stop-check rc $SRC - not starting"; echo "stop-check failed"; exit 1; fi
case "$T" in
  w146_00) ;;
  w146_*)
    SKL=$(python $ROOT/$SC --skip-w $T 2>&1 | tail -1 | tr -d '\\r')
    SKR=$?
    case "$SKL" in
      SKIPPED_V_NOT_ENTERED*)
        echo "$SKL $(date -u +%Y-%m-%dT%H:%M:%SZ)" > skipped_$T.txt
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T SKIPPED_V_NOT_ENTERED (item 309 (k)(1); no lock, not an attempt): $SKL" >> $TIMES
        log "go146a.sh $T skipped: $SKL"; echo "$SKL"; exit 0;;
      RUN*) log "go146a.sh $T runs: $SKL";;
      *) log "go146a.sh $T refused: --skip-w answered '$SKL'"; echo "skip-w failed"; exit 1;;
    esac;;
esac
''')
d.t = d.t.replace('go145a $T', 'go146a $T')
d.rep('''python $ROOT/cachemf145.py $OUT/cache_$T.before.json''', '''python $ROOT/cachemf146.py $OUT/cache_$T.before.json''')
d.rep('''python $ROOT/cachemf145.py $OUT/cache_$T.after.json''', '''python $ROOT/cachemf146.py $OUT/cache_$T.after.json''')
d.rep('''  FG=$(python $ROOT/fgcpu145.py --since''', '''  FG=$(python $ROOT/fgcpu146.py --since''')
d.rep('''python $ROOT/fgcpu145.py --save''', '''python $ROOT/fgcpu146.py --save''')
d.rep('''log "files: $(sha256sum $SC test_$SC mut_$SC $PRED gates_default.txt enter_scene.py idle142.py procload.py go145a.sh sheet142.py fgcpu145.py cachemf145.py lockcheck145.py $VIDGLITCH | cut -c1-16,65- | tr '\\n' ';')"''',
      '''log "files: $(sha256sum $SC test_$SC mut_$SC $PRED gates_default.txt enter_scene.py idle142.py procload.py go146a.sh sheet142.py fgcpu146.py cachemf146.py lockcheck146.py tiles146.py $VIDGLITCH | cut -c1-16,65- | tr '\\n' ';')"''')
d.rep('''"rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt" "runs145/$T.score.json" \\
         "runs145/cache_$T.after.json" \\''', '''"rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt" "runs146/$T.score.json" \\
         "runs146/cache_$T.after.json" "tiles_$T.txt" "tiles_$T.png" \\''')
d.rep('''    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T sheet rc $SHRC sheet_$T.png sha256 $(sha sheet_$T.png)" >> $TIMES
''', '''    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T sheet rc $SHRC sheet_$T.png sha256 $(sha sheet_$T.png)" >> $TIMES
    python $ROOT/tiles146.py rec_$T.mp4 tiles_$T.txt --sheet tiles_$T.png > /dev/null 2>&1
    TLRC=$?
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T tiles rc $TLRC tiles_$T.txt sha256 $(sha tiles_$T.txt): $(head -1 tiles_$T.txt | cut -c1-160)" >> $TIMES
''')
d.rep('''  log "$SC --check-seal refused (see above) - not starting"''', '''  log "$SC --check-seal refused (see above) - not starting"''')
d.rep('''  log "go146a.sh $T refused (rc 5): a stop rule of item 273 (k)(4) (the control W, two W, three V, the window event - the stop-check lines above); question to the lead"''',
      '''  log "go146a.sh $T refused (rc 5): a stop rule of item 273 (k)(4), 309 (l)(5) (the control W, two W, three V, the window event - the stop-check lines above); question to the lead"''')
body = chr(10).join(x for x in d.t.split('# EXIT CODES:')[1].split(chr(10)) if not x.lstrip().startswith('#'))
for w in ('go145a', 's145', 'sc145', 'runs145', 'cachemf145', 'fgcpu145', 'lockcheck145', '9235a7ac'):
    if w in body:
        print('go146a.sh: %s left in the code' % w)
        OK[0] = False
d.write(S6 + '/go146a.sh')

# ---------------- step2 wrappers
d = Doc(S5 + '/step2/call_one.sh')
d.t = d.t.replace('Session 145 step 2 (step 0 HPP-350, ROADMAP s122 item 273 (k); port of the session-144 file, names moved to s145)',
                  'Session 146 step 2 (step 0 HPP-386, ROADMAP s122 item 309 (k)-(l); port of the session-145 file, names moved to s146)')
d.t = d.t.replace('pred/03_sc145.md', 'pred/01_sc146.md').replace('s145', 's146').replace('go145a', 'go146a')
d.write(S6 + '/step2/call_one.sh')
d = Doc(S5 + '/step2/wait_one.sh')
d.t = d.t.replace('Session 145 step 2 (step 0 HPP-350, ROADMAP s122 item 273 (k); port of the session-144 file, names moved to s145)',
                  'Session 146 step 2 (step 0 HPP-386, ROADMAP s122 item 309 (k)-(l); port of the session-145 file, names moved to s146)')
d.t = d.t.replace('s145', 's146').replace('go145a', 'go146a')
d.write(S6 + '/step2/wait_one.sh')
d = Doc(S5 + '/step2/pre_one.sh')
d.t = d.t.replace('# Session 145 step 2 (step 0 HPP-350; ROADMAP s122 item 273 (k)(4); port of the s144 file of item 266 (h))',
                  '# Session 146 step 2 (step 0 HPP-386; ROADMAP s122 item 273 (k)(4), 309 (k)(2); port of the s145 file)')
d.t = d.t.replace('sc145.py', 'sc146.py').replace('gate145.py', 'gate146.py').replace('s145', 's146')
d.write(S6 + '/step2/pre_one.sh')
d = Doc(S5 + '/step2/next_one.sh')
d.rep('''# Session 145 step 2 call wrapper (step 0 HPP-350, ROADMAP s122 item 273 (k); port of C:/kyty/s144/step2/next_one.sh):''',
      '''# Session 146 step 2 call wrapper (step 0 HPP-386, ROADMAP s122 item 309 (k)-(l); port of C:/kyty/s145/step2/next_one.sh;
# debt D-9 of s145 (item 309 (i)): the previous output step2/go_<tag>.out.txt of the tag is moved to step2/old/ before a new
# call - a file without its "rc=" line is a call still running: refused rc 1, wait with wait_one.sh):''')
d.rep('''  w145_00|w145_01|v145_0[2-9]|w145_0[2-9]|v145_1[0-7]|w145_1[0-7]) ;;
  *) echo "usage: next_one.sh w145_00|w145_01|v145_NN|w145_NN (NN 02..17) [<last comment id read>]"; exit 2;;''',
      '''  w146_00|r146_0[1-4]|v146_0[5-9]|w146_0[5-9]|v146_1[0-9]|w146_1[0-9]) ;;
  *) echo "usage: next_one.sh w146_00|r146_0N (N 1..4)|v146_NN|w146_NN (NN 05..19) [<last comment id read>]"; exit 2;;''')
d.rep('''echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP absent, no lock, api GO; call: PLWAIT=540 bash C:/kyty/s145/go145a.sh $T" >> $TIMES''',
      '''GO=C:/kyty/s146/step2/go_$T.out.txt
if [ -e $GO ]; then
  grep -q '^rc=' $GO || { echo "the previous call of $T has no rc line (running) - wait with wait_one.sh, no new call"; exit 1; }
  mkdir -p C:/kyty/s146/step2/old
  NEWN=C:/kyty/s146/step2/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  mv $GO $NEWN && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one previous output of $T moved to step2/old/$(basename $NEWN) (D-9)" >> $TIMES
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP absent, no lock, api GO; call: PLWAIT=540 bash C:/kyty/s146/go146a.sh $T" >> $TIMES''')
d.t = d.t.replace('apichk145.py', 'apichk146.py').replace('s145', 's146').replace('go145a', 'go146a')
d.write(S6 + '/step2/next_one.sh')

# ---------------- apichk146.py
d = Doc(S5 + '/step2/apichk145.py')
d.t = d.t.replace('apichk145', 'apichk146').replace('C:/kyty/s145', 'C:/kyty/s146').replace('go145a', 'go146a')
d.rep('''"""apichk146.py - the API check row of step 2 of session 145 (port of apichk144.py by HPP-350, names 144 -> 145;''',
      '''"""apichk146.py - the API check row of step 2 of session 146 (port of apichk145.py by HPP-386, names 145 -> 146; port of
apichk144.py by HPP-350, names 144 -> 145;''')
d.write(S6 + '/step2/apichk146.py')

# ---------------- lockcheck146.py
d = Doc(S5 + '/lockcheck145.py')
d.rep('''to s145 by HPP-350, names 143 -> 144 -> 145)''', '''to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146)''')
d.rep('''BUILD = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7\'''', '''BUILD = 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e\'''')
d.t = d.t.replace('lockcheck145', 'lockcheck146').replace('go145a', 'go146a').replace("'C:/kyty/s145'", "'C:/kyty/s146'").replace(
    'runs145', 'runs146').replace('the pinned 9235a7ac', 'the pinned dac02fb9')
d.write(S6 + '/lockcheck146.py')

# ---------------- fgcpu146.py: <app> in place of the process names ("Process" 5 of s145, item 309 (i))
d = Doc(S5 + '/fgcpu145.py')
d.rep('''to s145 by HPP-350, names 143 -> 144 -> 145)''', '''to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146)''')
d.t = d.t.replace('fgcpu145', 'fgcpu146').replace('go145a.sh', 'go146a.sh')
d.rep('''    return ', '.join('%s:%d:%.3f' % (n, p, r) for n, p, r in rows[:TOP]) or 'none\'''',
      '''    return ', '.join('<app>:%d:%.3f' % (p, r) for n, p, r in rows[:TOP]) or 'none\'''')
d.rep('''  (1) the processes alive at both ends (same pid and name):''', '''  (Session 146, "Process" 5 of s145: every process of the TOP lists is printed as <app>:<pid>:<rate> - no process name.)
  (1) the processes alive at both ends (same pid and name):''')
d.write(S6 + '/fgcpu146.py')

print('ALL OK' if OK[0] else 'SOME FAILED')
sys.exit(0 if OK[0] else 1)
