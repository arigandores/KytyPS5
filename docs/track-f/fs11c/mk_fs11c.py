"""FS11c (HPP-716): port of the F29e harness (C:/kyty/f287/f29e) to C:/kyty/f287/fs11c.  Copies, renamed copies, go_fs11c.sh,
launch / post / chk / wait.  Every replacement is by an anchor with an exact count check.  The reader and the suites are written apart.
ASCII only.  usage: python mk_fs11c.py"""
import os
import shutil
import sys

S = 'C:/kyty/f287/f29e'
D = 'C:/kyty/f287/fs11c'
NL = chr(10)
TB_OLD = 'cabbd818397a8a299e7e64cf2d153197ad7e69e310015b5d473bb66f37802e95'
TB_NEW = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'
TAGS_OLD = 'b12_v|b12_w|b12_v_r[1-3]|b12_w_r[1-3]'
TAGS_NEW = 'fs11_v|fs11_w|fs11_z|fs11_v_r[1-3]|fs11_w_r[1-3]|fs11_z_r[1-3]'


def names(t):
    for a, b in (('f29e', 'fs11c'), ('F29E', 'FS11C'), ('F29e', 'FS11c'), ('HPP-704', 'HPP-716')):
        t = t.replace(a, b)
    return t


def rep(t, R, what):
    for a, b in R:
        c = t.count(a)
        if c != 1:
            print('%s: anchor count %d: %s' % (what, c, a[:90]))
            sys.exit(1)
        t = t.replace(a, b)
    return t


def left(t, what, bad):
    for x in bad:
        if x in t:
            print('%s left: %s' % (what, x), [l for l in t.split(NL) if x in l][:3])
            sys.exit(1)


def wr(name, t):
    open(os.path.join(D, name), 'w', encoding='ascii', newline=NL).write(t)


if os.path.exists(D + '/go_fs11c.sh'):
    print('fs11c exists - not overwritten')
    sys.exit(2)
for sub in ('', 'base', 'pred', 'runs', 'old'):
    os.makedirs(os.path.join(D, sub), exist_ok=True)
for nm in ('dispstate.py', 'manifest_fs4c.py', 'procload.py', 'idle142.py', 'sheet142.py', 'gates_default.txt', 'launch_run.py',
           'run_safety99.py'):
    shutil.copyfile(os.path.join(S, nm), os.path.join(D, nm))
open(os.path.join(D, 'enter_scene.py'), 'w', encoding='utf-8', newline='').write(names(open(os.path.join(S, 'enter_scene.py'), encoding='utf-8', newline='').read()))
for nm in ('guard', 'hold', 'runchk', 'queue', 'tempo', 'snap', 'mfsub'):
    t = open(os.path.join(S, '%s_f29e.py' % nm), encoding='utf-8', newline='').read()
    open(os.path.join(D, '%s_fs11c.py' % nm), 'w', encoding='utf-8', newline='').write(names(t))

# wait, chk: names only
WT = open('C:/kyty/KytyPS5/docs/track-f/f29e/wait_f29e.sh', encoding='ascii').read()
wr('wait_fs11c.sh', names(WT))
wr('chk_fs11c.sh', names(open(os.path.join(S, 'chk_f29e.sh'), encoding='ascii').read()))

# launch: tags + names
LA = open(os.path.join(S, 'launch_f29e.sh'), encoding='ascii').read()
LA = rep(LA, [
    ('# Track F link F29e (HPP-704; port of F25m launch_f25m.sh, names moved, no level argument)',
     '# Track F link FS11c (HPP-716; port of F29e launch_f29e.sh, names and tags moved; before: F25m launch_f25m.sh)'),
    ('  ' + TAGS_OLD + ') ;;\n  *) echo "usage: launch_f29e.sh b12_v|b12_w[_r1..3]"; exit 2;;',
     '  ' + TAGS_NEW + ') ;;\n  *) echo "usage: launch_fs11c.sh fs11_v|fs11_w|fs11_z[_r1..3]"; exit 2;;'),
], 'launch')
LA = names(LA)
left(LA, 'launch', ('b12_', 'f29e', 'HPP-704'))
wr('launch_fs11c.sh', LA)

# post: tags, pair with b12_v (item 647 (d)(3): the lead sheet beside b12_v)
PO = open(os.path.join(S, 'post_f29e.sh'), encoding='ascii').read()
PO = rep(PO, [
    ('# Track F link F29e (HPP-704; port of FS10c post_fs10c.sh): the reading of a made tag outside the lock.  The tag with a video (b12_v):\n'
     '# s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; the pair image\n'
     '# pair_b12_v_fs10_v.png = the sheet of b12_v left of the sheet of fs10_v (FS10c, the same form on FS10 without KYTY_FIX_B12).  Then\n',
     '# Track F link FS11c (HPP-716; port of F29e post_f29e.sh): the reading of a made tag outside the lock.  Tags with a video (fs11_v,\n'
     '# fs11_z): s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; fs11_v - the pair\n'
     '# image pair_fs11_v_b12_v.png = the sheet of fs11_v left of the sheet of b12_v (F29e, item 647 (d)(3): the lead sheet beside b12_v).  Then\n'),
    ('  ' + TAGS_OLD + ') ;;\n  *) echo "usage: post_f29e.sh <tag>"; exit 2;;',
     '  ' + TAGS_NEW + ') ;;\n  *) echo "usage: post_fs11c.sh <tag>"; exit 2;;'),
    ('  case "$T" in b12_v*)', '  case "$T" in fs11_v*)'),
    ('-i C:/kyty/f287/fs10c/runs/fs10_v/sheet_fs10_v.png', '-i C:/kyty/f287/f29e/runs/b12_v/sheet_b12_v.png'),
    ('$D/pair_${T}_fs10_v.png > $D/pair.txt 2>&1 \\\n        && echo "pair: $D/pair_${T}_fs10_v.png (left $T, right fs10_v)" >> $D/pair.txt',
     '$D/pair_${T}_b12_v.png > $D/pair.txt 2>&1 \\\n        && echo "pair: $D/pair_${T}_b12_v.png (left $T, right b12_v)" >> $D/pair.txt'),
], 'post')
PIN = 'C:/kyty/f287/f29e/runs/b12_v/sheet_b12_v.png'
PO = PO.replace(PIN, '@@PIN@@')
PO = names(PO).replace('@@PIN@@', PIN)
left(PO.replace(PIN, ''), 'post', ('f29e', 'HPP-704', 'fs10_v', 'b12_v|'))
wr('post_fs11c.sh', PO)

# go
src = open(os.path.join(S, 'go_f29e.sh'), encoding='ascii').read()
head_end = src.index('export PATH=/usr/bin:/mingw64/bin:$PATH')
HEAD = NL.join([
    '#!/bin/bash',
    '# Track F link FS11c (HPP-716; ROADMAP s122 item 647 (d)(3), item 652): one tag of the FS11 shipping binary ea51ae80 (FS10 dc5d4712 +',
    '# 73a6e411 + c94c49e0 + 726e751e + 0db3b3eb + cb022252, worktree C:/kyty/f287/fs11a/wt HEAD ee9632be; the default KYTY_FIX_B12=1) -',
    '# ea51ae80 is installed for the tag only, known by its full sha256; the installed FS10 abfded5e (item 627-628) is checked before and',
    '# returned from its pinned copy after.  ONE TAG = ONE LOCK.  Port of C:/kyty/f287/f29e/go_f29e.sh (F29e, HPP-704): only the tag binary,',
    '# the tags fs11_v / fs11_w / fs11_z and the knobs changed; the per-tag manifest and copy of the five folders before, return after, cmp',
    '# EQUAL; the display member (item 620 (g)(1), 623 (v)); the user game guard (item 534) and the user session guard (item 606 (v)(1)).',
    '# Level of every tag: underwater_aerial_garden.',
    '#   fs11_v  form b12_v / fs10_v without a KYTY_FIX_* knob (the default): KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, video,',
    '#           --stable-draws 300 --timeout 480, hold 330 s',
    '#   fs11_w  form b12_w / fs10_w without a KYTY_FIX_* knob: --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000,',
    '#           no VK_LAYER_MESSAGE_ID_FILTER, precache at the default, KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, --stable-draws 100 --timeout 900,',
    '#           hold 310 s',
    '#   fs11_z  the rollback control KYTY_FIX_B12=0, V Sky Garden: KYTY_FIX_B12=0 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0, video,',
    '#           --stable-draws 300 --timeout 480, hold 150 s (>= 120 s after the first scene frame)',
    '# No RenderDoc, no KYTY_GPU_CHECKPOINTS, no KYTY_GAME_PATCH, no KYTY_FIX_* except KYTY_FIX_B12=0 at fs11_z; KYTY_* and VK_LAYER_* of the',
    '# shell are unset before the call; the knobs go to enter_scene.py positionally.',
    '# usage: bash C:/kyty/f287/fs11c/go_fs11c.sh fs11_v|fs11_w|fs11_z      (repeats: <tag>_r1.._r3 by the lead\'s item)',
    '# EXIT: 0 tag made (read it with post_fs11c.sh); 1 hard refusal / return failed; 2 usage / the tag exists; 3 lock / user process / run gone;',
    '#   4 stop file; 5 procload busy; 6 display not ON before the lock.  ASCII only.',
    ''])
body = src[head_end:]
body = rep(body, [
    ('TB=' + TB_OLD, 'TB=' + TB_NEW),
    ('BIN=$F/bin/kyty_emulator_cabbd818.exe', 'BIN=$F/bin/kyty_emulator_ea51ae80.exe'),
    ('  ' + TAGS_OLD + ') ;;\n  *) echo "usage: go_f29e.sh b12_v|b12_w[_r1..3]"; exit 2;;',
     '  ' + TAGS_NEW + ') ;;\n  *) echo "usage: go_fs11c.sh fs11_v|fs11_w|fs11_z[_r1..3]"; exit 2;;'),
    ('  b12_v) UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="KYTY_FIX_B12=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;\n'
     '  b12_w) UF=""; SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"\n'
     '         KN="KYTY_FIX_B12=1 VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;',
     '  fs11_v) UF=""; SD=300; H=330; TO=480; REC="--rec"; KN="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;\n'
     '  fs11_w) UF=""; SD=100; H=310; TO=900; REC="--emu-arg=--vulkan-validation --emu-arg=true"\n'
     '          KN="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;\n'
     '  fs11_z) UF=""; SD=300; H=150; TO=480; REC="--rec"; KN="KYTY_FIX_B12=0 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0";;'),
    ('[ "$(sha "$BIN")" = "$TB" ] || { log "F29c copy $BIN is not cabbd818 - not starting"; exit 1; }',
     '[ "$(sha "$BIN")" = "$TB" ] || { log "FS11 copy $BIN is not ea51ae80 - not starting"; exit 1; }'),
    ('cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the F29c copy failed - not starting"; exit 1; }',
     'cp "$BIN" "$GAME" && [ "$(sha "$GAME")" = "$TB" ] || { log "install of the FS11 copy failed - not starting"; exit 1; }'),
    ('log "installed the F29c copy cabbd818 for the tag: $(cat $OUT/installed_sha.txt)"',
     'log "installed the FS11 copy ea51ae80 for the tag: $(cat $OUT/installed_sha.txt)"'),
], 'go')
body = names(body)
left(body, 'go', ('f29e', 'F29e', 'F29E', 'F29c', 'cabbd818', 'b12_', 'HPP-704'))
wr('go_fs11c.sh', HEAD + body)
for nm in ('go_fs11c.sh', 'launch_fs11c.sh', 'post_fs11c.sh', 'wait_fs11c.sh', 'chk_fs11c.sh'):
    os.chmod(os.path.join(D, nm), 0o755)
print('written', sorted(os.listdir(D)))
