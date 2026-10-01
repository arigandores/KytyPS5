"""w2_patch_go.py - F4c wake 4: go_f4c.sh under ROADMAP p.262 (d), (e), p.268 (v), p.270 (d).  Every anchor must occur
exactly once; LF written with write_bytes."""
import sys

P = 'C:/kyty/f287/f4c/go_f4c.sh'
s = open(P, 'rb').read().decode('ascii')
assert '\r' not in s
R = [
    ('#   TAGS (item 254 (zh)(2); one attempt each, a failure is data, no repeat); the order SEQ is the executor variant B4\n'
     '#   (the cheap control first) until the lead\'s answer:\n',
     '#   TAGS (item 254 (zh)(2); one attempt each, a failure is data, no repeat); the order SEQ - item 262 (e) (B4 accepted)\n'
     '#   for STAND=A; STAND=Bp (item 262 (g), only by a lead line in HPP-337) - (g) -> (b) -> (a) -> (v):\n'),
    ('#   SERIES STOP (f4c_read.py --stop-check): (b) without the stop of the same text -> the stand is empty, later tags not run;\n',
     '#   PRE-CHECK (item 262 (g)): before (b) and (a) the recipe file must hold a dual-source record (f4c_read.py --pre-check),\n'
     '#     else series stop before the tag, NOT EVALUABLE, question to the lead.\n'
     '#   SERIES STOP (f4c_read.py --stop-check): (b) without the stop of the same text -> NOT EVALUABLE, later tags not run\n'
     '#     (item 262 (e)); any NOT EVALUABLE (controls of item 262 (d));\n'),
    ('#   BINARY: BIN_F4C / BIN_EXPECT / FIXB26 - the lead\'s answer to B1 (F4b RC1); empty -> rc 2 (not configured).\n'
     '#   LOCK WINDOW (as item 256 (e)): right before the lock - no lock file, no stop file, HPP-332 neither in_progress nor done\n'
     '#     and without a run by the API answer (win332_f2c.py, a times line with the answer); else BUSY rc 4.\n',
     '#   BINARY: BIN_F4C / BIN_EXPECT - item 268 (v) (F4a2 report, c9a5e198); KYTY_FIX_B26 never passed (the binary does not\n'
     '#     read it); before the lock and the install the binary must hold the translation signature 699c1e4b... (STAND=A) and\n'
     '#     the string "DualSrcBlend: patched" (item 262 (v)); else rc 1.\n'
     '#   LOCK WINDOW (item 268 (d), 270 (d); variant of the executor for the P queue): right before the lock - no lock file, no\n'
     '#     stop file, HPP-333 and HPP-347 done without a run, HPP-328 (P10) neither todo nor in_progress and without a run, by\n'
     '#     the API answer (win_f4c.py, a times line with the answer); else BUSY rc 4.\n'),
    ('BIN_F4C=""\nBIN_EXPECT=""\n',
     'BIN_F4C="C:/kyty/f287/bin/kyty_emulator_c9a5e198.exe"\n'
     'BIN_EXPECT="c9a5e1986e254132f776f0c7f1c9446d0bdc862e199bbbc1d57aedf17d4c9f9b"\n'
     'SIGSTR="699c1e4b7db359067b461e029b913c4b6e78dc90"\n'
     'STAND="A"\n'),
    ('VHOLD="345"\nWHOLD="320"\nSEQ="f4c_b f4c_a f4c_v f4c_g"\n',
     'VHOLD="330"\nWHOLD="310"\n'
     'case "$STAND" in\n'
     '  A) SEQ="f4c_b f4c_a f4c_v f4c_g";;\n'
     '  Bp) SEQ="f4c_g f4c_b f4c_a f4c_v";;\n'
     '  *) SEQ="";;\n'
     'esac\n'),
    ('unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS\n'
     'if [ -z "$BIN_F4C" ] || [ -z "$BIN_EXPECT" ] || [ -z "$GLRESTORE" ]; then\n'
     '  log "go_f4c.sh refused: not configured (BIN_F4C/BIN_EXPECT/FIXB26 - lead\'s answer to B1, F4b RC1)"\n',
     'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW\n'
     'if [ -z "$BIN_F4C" ] || [ -z "$BIN_EXPECT" ] || [ -z "$GLRESTORE" ] || [ -z "$SEQ" ]; then\n'
     '  log "go_f4c.sh refused: not configured (BIN_F4C/BIN_EXPECT/GLRESTORE/STAND - item 262 (v), (g), 268 (v))"\n'),
    ('  echo "DRY series: tags $SEQ; stop file?; lock?; PLWAIT=$PLWAIT; procload --wait-s $PLWAIT; f4c_read --check-seal; cpu < 15; idle142; procload --wait-s 0; stop file?; HPP-332 window (win332_f2c); lock (lock.log UTC); shader cache list + copy to $SNAP (lists equal); GLCache manifest + copy (GLRESTORE=$GLRESTORE); fgcpu143 --save; install $BIN_F4C ($BIN_EXPECT); per tag: stop file?, recipes143 runs/recipes_<tag>.json, enter_scene.py',
     '  echo "DRY series: stand $STAND tags $SEQ; stop file?; lock?; PLWAIT=$PLWAIT; binary sha + strings (signature $SIGSTR if A, DualSrcBlend: patched); procload --wait-s $PLWAIT; f4c_read --check-seal; cpu < 15; idle142; procload --wait-s 0; stop file?; window HPP-333/HPP-347 done, HPP-328 not waiting (win_f4c); lock (lock.log UTC); shader cache list + copy to $SNAP (lists equal); GLCache manifest + copy (GLRESTORE=$GLRESTORE); fgcpu143 --save; install $BIN_F4C ($BIN_EXPECT); per tag: stop file?, recipes143 runs/recipes_<tag>.json, pre-check dual-source record (b, a), enter_scene.py'),
    ('=1) $B26X KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, log sha',
     '=1) KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, log sha'),
    ('if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then\n',
     'NSIG=$(LC_ALL=C grep -a -F -c "$SIGSTR" "$BIN_F4C")\n'
     'NPAT=$(LC_ALL=C grep -a -F -c "DualSrcBlend: patched" "$BIN_F4C")\n'
     'if [ "$NPAT" = "0" ] || { [ "$STAND" = "A" ] && [ "$NSIG" = "0" ]; }; then\n'
     '  log "go_f4c.sh refused: fix binary strings - signature $SIGSTR lines $NSIG, DualSrcBlend: patched lines $NPAT (stand $STAND)"\n'
     '  echo "fix binary strings bad"; exit 1\n'
     'fi\n'
     'if [ "$(sha "$GAME")" != "$BUILD_EXPECT" ]; then\n'),
    ('W332=$(python $ROOT/win332_f2c.py 2>&1 | tail -1 | tr -d \'\\r\')\n'
     'tl "lock window (as p.256(e)): $W332"\n'
     'case "$W332" in\n'
     '  *"-> open") ;;\n'
     '  *) busy "lock window closed or unknown: $W332";;\n',
     'WIN=$(python $ROOT/win_f4c.py 2>&1 | tail -1 | tr -d \'\\r\')\n'
     'tl "lock window (p.268(d), 270(d)): $WIN"\n'
     'case "$WIN" in\n'
     '  *"-> open") ;;\n'
     '  *) busy "lock window closed or unknown: $WIN";;\n'),
    ('log "go_f4c.sh series requested (fix binary $BIN_EXPECT, installed $BUILD_EXPECT, PLWAIT=$PLWAIT, seq $SEQ, b26 \'$B26X\')"\n',
     'log "go_f4c.sh series requested (fix binary $BIN_EXPECT, installed $BUILD_EXPECT, PLWAIT=$PLWAIT, stand $STAND seq $SEQ)"\n'),
    ('B26X=""\nif [ "$FIXB26_SET" = "1" ]; then B26X="KYTY_FIX_B26=$FIXB26"; fi\n', ''),
    ('FIXB26_SET=""\nFIXB26=""\n', ''),
    ('f4c_read.py recipes143.py shalist_f2c.py win332_f2c.py $PRED', 'f4c_read.py recipes143.py shalist_f2c.py win_f4c.py $PRED'),
    ('  tl "$C recipe file before the tag: $(head -1 runs/recipes_$C.out.txt | cut -c1-200); dual-source lines $(grep -c \'DUAL-SOURCE\' runs/recipes_$C.out.txt)"\n',
     '  tl "$C recipe file before the tag: $(head -1 runs/recipes_$C.out.txt | cut -c1-200); dual-source lines $(grep -c \'DUAL-SOURCE\' runs/recipes_$C.out.txt)"\n'
     '  case "$C" in\n'
     '    f4c_b|f4c_a)\n'
     '      PC=$(python $ROOT/f4c_read.py --pre-check $C 2>&1 | tail -1 | tr -d \'\\r\')\n'
     '      tl "$C pre-check (p.262(g)): $PC"\n'
     '      case "$PC" in\n'
     '        "continue"*) ;;\n'
     '        *) tl "$C series stop before the tag: $PC"; SERIES_RC=1; break;;\n'
     '      esac;;\n'
     '  esac\n'),
    ('  tl "$C enter_scene start (level $LV, hold $HOLD, extra \'$EXTRA $B26X\', emu \'$EMUX\')"\n',
     '  tl "$C enter_scene start (level $LV, hold $HOLD, extra \'$EXTRA\', emu \'$EMUX\')"\n'),
    ('--pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA $B26X KYTY_GPU_CLOCK_PIN=1',
     '--pred $ROOT/$PRED $REC $EMUX --hold $HOLD $EXTRA KYTY_GPU_CLOCK_PIN=1'),
]
for a, b in R:
    n = s.count(a)
    if n != 1:
        print('anchor count %d: %r' % (n, a[:80]))
        sys.exit(1)
    s = s.replace(a, b)
assert 'B26X' not in s and 'FIXB26' not in s and 'win332' not in s, 'leftover'
open(P, 'wb').write(s.encode('ascii'))
print('patched ok')
