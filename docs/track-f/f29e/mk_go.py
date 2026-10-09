import sys
src = open('C:/kyty/f287/fs10c/go_fs10c.sh', encoding='ascii').read()
NL = chr(10)
head_end = src.index('export PATH=/usr/bin:/mingw64/bin:$PATH')
HEAD = NL.join([
    '#!/bin/bash',
    '# Track F link F29e (HPP-704; ROADMAP s122 item 639 (e)(4), item 645 (a), item 646 (g)): one tag "no harm" of the F29c binary cabbd818',
    '# (FS10a dc5d4712 + 73a6e411 + c94c49e0 + 726e751e, worktree 673b780a; KYTY_FIX_B12=1 given, other defaults) - cabbd818 is installed for',
    '# the tag only, known by its full sha256; the installed FS10 abfded5e (item 627-628) is checked before and returned from its pinned copy',
    '# after.  ONE TAG = ONE LOCK.  Port of C:/kyty/f287/fs10c/go_fs10c.sh (FS10c, HPP-686): only the binaries, the tags b12_v / b12_w (the',
    '# forms fs10_v / fs10_w) and KYTY_FIX_B12=1 changed; the per-tag manifest and copy of the five folders before, return after, cmp EQUAL;',
    '# the display member (item 620 (g)(1), 623 (v)); the user game guard (item 534) and the user session guard (item 606 (v)(1)).',
    '# Level of both tags: underwater_aerial_garden.',
    '#   b12_v  form fs10_v: KYTY_FIX_B12=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, video, --stable-draws 300 --timeout 480, hold 330 s',
    '#   b12_w  form fs10_w: --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, no VK_LAYER_MESSAGE_ID_FILTER,',
    '#          precache at the default, KYTY_FIX_B12=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, --stable-draws 100 --timeout 900, hold 310 s',
    '# No RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no KYTY_FIX_* except KYTY_FIX_B12=1; KYTY_* and VK_LAYER_* of the shell are',
    '# unset before the call; the knobs go to enter_scene.py positionally.',
    '# usage: bash C:/kyty/f287/f29e/go_f29e.sh b12_v|b12_w      (repeats: <tag>_r1.._r3 by the lead\'s item)',
    '# EXIT: 0 tag made (read it with post_f29e.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run gone;',
    '#   4 stop file; 5 procload busy; 6 display not ON before the lock.  ASCII only.',
    ''])
body = src[head_end:]
R = [
    ('G=C:/kyty/f287/fs10c; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${FS10C_LOCK:-C:/kyty/SEALED_RUN.lock}',
     'G=C:/kyty/f287/f29e; F=C:/kyty/f287; EMU="C:/kyty/KytyPS5/ps5 em"; LOCK=${F29E_LOCK:-C:/kyty/SEALED_RUN.lock}'),
    ('FS9=3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5', 'FS10=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'),
    ('TB=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe', 'TB=cabbd818397a8a299e7e64cf2d153197ad7e69e310015b5d473bb66f37802e95'),
    ('BIN=$F/bin/kyty_emulator_abfded5e.exe', 'BIN=$F/bin/kyty_emulator_cabbd818.exe'),
    ('PINNED=$F/bin/kyty_emulator_3861eeea.exe', 'PINNED=$F/bin/kyty_emulator_abfded5e.exe'),
    ('SEAL=$G/pred/fs10c_seal.md', 'SEAL=$G/pred/f29e_seal.md'),
    ('  fs10_s[01]|fs10_f1|fs10_v|fs10_w|fs10_s[01]_r[1-3]|fs10_f1_r[1-3]|fs10_v_r[1-3]|fs10_w_r[1-3]) ;;\n  *) echo "usage: go_fs10c.sh fs10_s1|fs10_s0|fs10_f1|fs10_v|fs10_w[_r1..3]"; exit 2;;',
     '  b12_v|b12_w|b12_v_r[1-3]|b12_w_r[1-3]) ;;\n  *) echo "usage: go_f29e.sh b12_v|b12_w[_r1..3]"; exit 2;;'),
    ('STAND="KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3"\n', ''),
    ('  fs10_s1) UF="--user-form"; SD=300; H=150; TO=480; REC=""; KN="$STAND";;\n'
     '  fs10_s0) UF="--user-form"; SD=300; H=150; TO=480; REC=""; KN="$STAND KYTY_FIX_B36=0";;\n'
     '  fs10_f1) UF=""; SD=300; H=150; TO=480; REC="--rec"; KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22 $STAND";;\n'
     '  fs10_v) UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;\n'
     '  fs10_w) UF=""; SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"\n'
     '          KN="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;',
     '  b12_v) UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="KYTY_FIX_B12=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;\n'
     '  b12_w) UF=""; SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"\n'
     '         KN="KYTY_FIX_B12=1 VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;'),
    ('[ "${FS10C_DRYRUN:-}" = 1 ]', '[ "${F29E_DRYRUN:-}" = 1 ]'),
    ('log() { echo "$(u) FS10c go_fs10c $T $*" | tee -a $TIMES; }', 'log() { echo "$(u) F29e go_f29e $T $*" | tee -a $TIMES; }'),
    ('[ "$(sha "$BIN")" = "$TB" ] || { log "FS10 copy $BIN is not abfded5e - not starting"; exit 1; }\n'
     '[ "$(sha "$PINNED")" = "$FS9" ] || { log "pinned FS9 copy $PINNED is not 3861eeea - not starting"; exit 1; }',
     '[ "$(sha "$BIN")" = "$TB" ] || { log "F29c copy $BIN is not cabbd818 - not starting"; exit 1; }\n'
     '[ "$(sha "$PINNED")" = "$FS10" ] || { log "pinned FS10 copy $PINNED is not abfded5e - not starting"; exit 1; }'),
    ('[ "$WANT" = "$FS9" ] || { log "installed binary $WANT is not FS9 3861eeea - not starting (question to the lead)"; exit 1; }',
     '[ "$WANT" = "$FS10" ] || { log "installed binary $WANT is not FS10 abfded5e - not starting (question to the lead)"; exit 1; }'),
    ('echo "FS10c HPP-686 go_fs10c.sh $T pid $$ $(u)" > $LOCK', 'echo "F29e HPP-704 go_f29e.sh $T pid $$ $(u)" > $LOCK'),
    ('for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$FS9" ] && break; sleep 5; done\n'
     '    if [ "$(sha "$GAME")" = "$FS9" ]; then log "installed binary returned from the pinned FS9 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi',
     'for i in 1 2 3; do cp "$PINNED" "$GAME" 2>/dev/null && [ "$(sha "$GAME")" = "$FS10" ] && break; sleep 5; done\n'
     '    if [ "$(sha "$GAME")" = "$FS10" ]; then log "installed binary returned from the pinned FS10 copy"; else OK=0; log "RETURN OF THE BINARY FAILED: $(sha "$GAME")"; fi'),
    ('[ "$(cat $OUT/installed_after.txt)" = "$FS9" ] || { OK=0; log "INSTALLED BINARY IS NOT FS9 after the tag"; }',
     '[ "$(cat $OUT/installed_after.txt)" = "$FS10" ] || { OK=0; log "INSTALLED BINARY IS NOT FS10 after the tag"; }'),
    ('cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the FS10 copy failed - not starting"; exit 1; }',
     'cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the F29c copy failed - not starting"; exit 1; }'),
    ('log "installed the FS10 copy for the tag: $(cat $OUT/installed_sha.txt)"', 'log "installed the F29c copy cabbd818 for the tag: $(cat $OUT/installed_sha.txt)"'),
]
out = body
for a, b in R:
    c = out.count(a)
    if c != 1:
        print('anchor count %d: %s' % (c, a[:80]))
        sys.exit(1)
    out = out.replace(a, b)
for a, b in (('fs10c', 'f29e'), ('FS10C', 'F29E')):
    out = out.replace(a, b)
for bad in ('fs10', 'FS9', '3861eeea', 'HPP-686', 'STAND'):
    if bad in out:
        print('left: %s' % bad, [l for l in out.split(NL) if bad in l][:3])
        sys.exit(1)
out = HEAD + out
open(sys.argv[1], 'w', encoding='ascii', newline=NL).write(out)
print('written', len(out))
