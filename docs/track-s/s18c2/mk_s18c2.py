"""S18c2 (HPP-654; ROADMAP s122 item 586 (g)-(d)): derived copies of the S18c harness (C:/kyty/s288/s18c) for the one extra tag s18_w2 -
go_s18c2.sh (the tag s18_w2 only: input cat_full from the catalogue replay_known checked against the manifest c644e3ad, KYTY_SHADER_SEED=0,
form w), launch / wait / post / aside / idle scripts with the names, the tag and the root of S18c2, enter_scene.py and guard_s18c2.py with the
root moved to C:/kyty/s288/s18c2, byte copies of the helpers.  Every anchor must match the stated number of times; LF, ASCII.
usage: python mk_s18c2.py [<destination folder with a trailing slash>]"""
import shutil
import sys

S = 'C:/kyty/s288/s18c/'
D = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s18c2/'
TAGS25 = '|'.join(['s18_c%02d' % i for i in range(1, 20)] + ['s18_ks', 's18_r', 's18_e1', 's18_e2', 's18_v', 's18_w'])
KNOWN = ('replay.45.bin:12cb378741308d1a82133be521311882881d1bbf04aff649cccc6d8e6607fee1 '
         'replay.46.bin:332a2f2d6aef0e8b64ccfe366d87df3476117abaf3b6aaf736ffbec2befc7c9a '
         'replay.cur:a5331f18877e9e1543361e44b4cb0a1f5f0ed5f8297d850bf1fcc68bd7a3ab5f')


def load(name):
    return open(S + name, 'rb').read().decode('ascii').replace('\r\n', '\n')


def edit(s, old, new, count=1):
    n = s.count(old)
    if n != count:
        raise SystemExit('anchor count %d (want %d): %r' % (n, count, old[:80]))
    return s.replace(old, new)


def save(name, s):
    for ch in s:
        if ord(ch) > 127:
            raise SystemExit('non-ASCII in ' + name)
    open(D + name, 'wb').write(s.encode('ascii'))
    print('written', D + name, len(s))


# go_s18c2.sh
s = load('go_s18c.sh')
head, body = s.split('export PATH=/usr/bin:/mingw64/bin:$PATH\n', 1)
head = ('#!/bin/bash\n'
        '# Track S link S18c2 (HPP-654; ROADMAP s122 item 586 (g)-(d)): the one extra tag s18_w2 of the S-replay shipment series - W Sky Garden\n'
        '# with the rebuild under the validation layer on the S18a2 binary b3cee576.  Derived from the S18c harness go_s18c.sh by mk_s18c2.py:\n'
        '# the same lock, gate, guard of the user game (item 534, general rule 33), copy and return of the caches with the manifest equality\n'
        '# line (the manifest covers _ShaderCache with replay/, _PipelineCache, _SaveData, GLCache and _ShaderSeeds); changed: the tag s18_w2\n'
        '# only, the root C:/kyty/s288/s18c2, the seal pred/s18c2_seal.md, the input cat_full from the catalogue C:/kyty/s288/s18c/replay_known\n'
        '# (exactly the 3 files of the manifest c644e3ad by sha256, else exit 2 before the lock), KYTY_SHADER_SEED=0 (the seeds of _ShaderSeeds\n'
        '# are not installed - the model of a signature change, item 586 (g)), KYTY_S_REPLAY and KYTY_S_REPLAY_TEST never passed (the latter\n'
        '# refused in the calling environment, item 576 (e)(3)).  ONE TAG = ONE LOCK.\n'
        '# INPUT STATE cat_full (in the live _ShaderCache/PPSA21564 after the copy): variant_fixb26_fixb1b_fixf10_fixf19 and replay removed,\n'
        '#   replay <- C:/kyty/s288/s18c/replay_known.\n'
        '# FORM w: enter_scene.py s18_w2 --level underwater_aerial_garden --attempts 1 --stable-draws 100 --no-install --require-idle\n'
        '#   --gates-file gates_default.txt --pred <seal> --timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold 310\n'
        '#   KYTY_SHADER_SEED=0 VK_LAYER_PATH VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (KYTY_* and\n'
        '#   VK_LAYER_* unset before the call; precache at the default, no message filter).\n'
        '# usage: bash C:/kyty/s288/s18c2/go_s18c2.sh s18_w2      ASCII only.\n'
        '# S18C2_GO_ROOT / S18C2_GO_SRC (fixtures of test_tools_s18c2.py only) move the roots; every fixture call ends before the seal check.\n'
        '# EXIT: 0 tag made (read it with post_s18c2.sh); 1 hard refusal / return failed; 2 usage / the tag exists / input state / catalogue\n'
        '#   differs from the manifest; 3 lock / user process; 4 stop file; 5 procload busy.\n')
s = head + 'export PATH=/usr/bin:/mingw64/bin:$PATH\n' + body
s = edit(s, 'G=${S18C_GO_ROOT:-C:/kyty/s288/s18c}; S=C:/kyty/s288;',
         'G=${S18C2_GO_ROOT:-C:/kyty/s288/s18c2}; SRCG=${S18C2_GO_SRC:-C:/kyty/s288/s18c}; S=C:/kyty/s288;')
s = edit(s, 'SEAL=$G/pred/s18c_seal.md\n', 'SEAL=$G/pred/s18c2_seal.md\n')
a = s.index('case "$T" in\n  s18_c0[1-9]|s18_c1[0-9])\n')
b = s.index('esac\n', s.index('  *) echo "usage: go_s18c.sh s18_c01..s18_c19|s18_ks|s18_r|s18_e1|s18_e2|s18_v|s18_w"; exit 2;;\n')) + len('esac\n')
s = s[:a] + ('case "$T" in\n'
             '  s18_w2) LV=$SKY; IN=cat_full; FORM=w; H=310; KV="KYTY_SHADER_SEED=0"; VK="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000";;\n'
             '  *) echo "usage: go_s18c2.sh s18_w2"; exit 2;;\n'
             'esac\n') + s[b:]
s = edit(s, 'case "$IN" in cat_full|inst_cat) SRCD=$G/state/s18_c19;; esac\n',
         'SRCD=$SRCG/replay_known\n'
         'KNOWN="%s"\n' % KNOWN)
s = edit(s, 'log() { echo "$(u) S18c go_s18c $T $*" | tee -a $TIMES; }', 'log() { echo "$(u) S18c2 go_s18c2 $T $*" | tee -a $TIMES; }')
s = edit(s, 'case "$T" in s18_r|s18_e1|s18_e2|s18_v|s18_w)\n', 'case "$T" in s18_w2)\n')
a = s.index('case "$IN" in\n  cap_acc|cat_full|inst_cat) [ -f $SRCD/replay/replay.cur ]')
b = s.index('esac\n', a) + len('esac\n')
s = s[:a] + ('[ -d $SRCD ] || { echo "input state cat_full: $SRCD missing"; exit 2; }\n'
             '[ "$(ls $SRCD | tr \'\\n\' \' \')" = "replay.45.bin replay.46.bin replay.cur " ] || { log "input state cat_full: the files of $SRCD differ from the manifest c644e3ad - not starting"; exit 2; }\n'
             'for f in $KNOWN; do\n'
             '  [ "$(sha $SRCD/${f%%:*})" = "${f#*:}" ] || { log "input state cat_full: $SRCD/${f%%:*} sha256 differs from the manifest c644e3ad - not starting"; exit 2; }\n'
             'done\n') + s[b:]
s = edit(s, 'echo "S18c HPP-644 go_s18c.sh $T pid $$ $(u)" > $LOCK', 'echo "S18c2 HPP-654 go_s18c2.sh $T pid $$ $(u)" > $LOCK')
s = edit(s, 'guard_s18c.py', 'guard_s18c2.py', 10)
s = edit(s, '  cat_full) rm -rf "$F19" "$RP"; cp -a $SRCD/replay "$RP" ||', '  cat_full) rm -rf "$F19" "$RP"; cp -a $SRCD "$RP" ||')
s = edit(s, 'log "input state $IN: copy of $SRCD/replay failed - not starting"; exit 1; };;\n  inst_cat)',
         'log "input state $IN: copy of $SRCD failed - not starting"; exit 1; };;\n  inst_cat)')
save('go_s18c2.sh', s)

# launch_s18c2.sh
s = load('launch_s18c.sh')
s = edit(s, '# Track S link S18c (HPP-644; port of S17c2 launch_s17c2.sh): ONLY launches one detached call of go_s18c.sh <tag>',
         '# Track S link S18c2 (HPP-654; derived from S18c launch_s18c.sh by mk_s18c2.py): ONLY launches one detached call of go_s18c2.sh <tag>')
s = edit(s, 'go_s18c.sh', 'go_s18c2.sh', 3)
s = edit(s, 'wait_s18c.sh', 'wait_s18c2.sh', 2)
s = edit(s, 'guard_s18c.py', 'guard_s18c2.py', 5)
s = edit(s, 'G=C:/kyty/s288/s18c\n', 'G=C:/kyty/s288/s18c2\n')
s = edit(s, 'case "$T" in %s) ;;\n' % TAGS25, 'case "$T" in s18_w2) ;;\n')
s = edit(s, 'usage: launch_s18c.sh <tag of go_s18c2.sh>', 'usage: launch_s18c2.sh <tag of go_s18c2.sh>')
s = edit(s, 'S18C_DRYRUN', 'S18C2_DRYRUN', 2)
s = edit(s, ' S18c guard (item 534)', ' S18c2 guard (item 534)', 3)
s = edit(s, ' S18c launch_s18c ', ' S18c2 launch_s18c2 ', 2)
s = edit(s, 'moved to s18c/old/', 'moved to s18c2/old/')
save('launch_s18c2.sh', s)

# wait_s18c2.sh
s = load('wait_s18c.sh')
s = edit(s, '# Track S link S18c (HPP-644; port of S17c2 wait_s17c2.sh): foreground wait',
         '# Track S link S18c2 (HPP-654; derived from S18c wait_s18c.sh): foreground wait')
s = edit(s, 'F=C:/kyty/s288/s18c/go_$T.out.txt', 'F=C:/kyty/s288/s18c2/go_$T.out.txt')
save('wait_s18c2.sh', s)

# post_s18c2.sh
s = load('post_s18c.sh')
s = edit(s, '# Track S link S18c (HPP-644; port of S17c2 post_s17c2.sh; the video tags s18_e1, s18_e2, s18_v): the reading',
         '# Track S link S18c2 (HPP-654; derived from S18c post_s18c.sh; the tag s18_w2 has no video, reader s18c2_read.py): the reading')
s = edit(s, 'T=$1; G=C:/kyty/s288/s18c; D=$G/runs/$T', 'T=$1; G=C:/kyty/s288/s18c2; D=$G/runs/$T')
s = edit(s, 'python s18c_read.py $T --json', 'python s18c2_read.py $T --json')
s = edit(s, 'python s18c_read.py --table', 'python s18c2_read.py --table')
s = edit(s, ' S18c post_s18c $T', ' S18c2 post_s18c2 $T')
s = edit(s, '# usage: bash C:/kyty/s288/s18c/post_s18c.sh <tag>', '# usage: bash C:/kyty/s288/s18c2/post_s18c2.sh s18_w2')
save('post_s18c2.sh', s)

# aside_s18c2.sh
s = load('aside_s18c.sh')
s = edit(s, '# Track S link S18c (HPP-644): port of S17c2 aside_s17c2.sh - only the reason rep (a NOT_ADMITTED tag of S18c, one repeat by the same\n',
         '# Track S link S18c2 (HPP-654): derived from S18c aside_s18c.sh - only the reason rep (a NOT_ADMITTED tag of S18c2, one repeat by the same\n')
s = edit(s, 'G=${S18C_ROOT:-C:/kyty/s288/s18c}', 'G=${S18C2_ROOT:-C:/kyty/s288/s18c2}')
s = edit(s, 'case "$T" in %s) ;;\n' % TAGS25, 'case "$T" in s18_w2) ;;\n')
s = edit(s, 'usage: aside_s18c.sh <tag> rep', 'usage: aside_s18c2.sh <tag> rep', 2)
s = edit(s, ' S18c aside_s18c $T $WHY', ' S18c2 aside_s18c2 $T $WHY')
save('aside_s18c2.sh', s)

# idle_s18c2.sh
s = load('idle_s18c.sh')
s = edit(s, '# Track S link S18c (HPP-644): GPU idle window', '# Track S link S18c2 (HPP-654; derived from S18c idle_s18c.sh): GPU idle window')
s = edit(s, 'launch_s18c.sh', 'launch_s18c2.sh', 2)
s = edit(s, '# usage: bash idle_s18c.sh <tag>', '# usage: bash idle_s18c2.sh s18_w2')
s = edit(s, 'G=C:/kyty/s288/s18c\n', 'G=C:/kyty/s288/s18c2\n')
s = edit(s, 'case "$T" in s18_r|s18_e1|s18_e2|s18_v|s18_w) ;; *) echo "usage: idle_s18c.sh <tag>"; exit 2;; esac',
         'case "$T" in s18_w2) ;; *) echo "usage: idle_s18c2.sh s18_w2"; exit 2;; esac')
s = edit(s, ' S18c GPU idle window', ' S18c2 GPU idle window')
save('idle_s18c2.sh', s)

# enter_scene.py
s = load('enter_scene.py')
s = edit(s, "ROOT = pathlib.Path('C:/kyty/s288/s18c')\n", "ROOT = pathlib.Path('C:/kyty/s288/s18c2')\n")
s = edit(s, '# Track S link S18c (HPP-644): the S17c2 enter_scene.py with ROOT moved to C:/kyty/s288/s18c (nothing else changed).\n',
         '# Track S link S18c2 (HPP-654): the S18c enter_scene.py with ROOT moved to C:/kyty/s288/s18c2 (nothing else changed).\n')
save('enter_scene.py', s)

# guard_s18c2.py
s = load('guard_s18c.py')
s = edit(s, "G = 'C:/kyty/s288/s18c'\n", "G = 'C:/kyty/s288/s18c2'\n")
s = edit(s, '# Track S link S18c (HPP-644): guard_s17c2.py with G moved to C:/kyty/s288/s18c (nothing else changed).\n',
         '# Track S link S18c2 (HPP-654): guard_s18c.py with G moved to C:/kyty/s288/s18c2 (nothing else changed).\n')
save('guard_s18c2.py', s)

for f in ('procload.py', 'idle142.py', 'launch_run.py', 'manifest_fs4c.py', 'run_safety99.py', 'state_s17c.py', 'gates_default.txt'):
    shutil.copyfile(S + f, D + f)
    print('copied', D + f)
