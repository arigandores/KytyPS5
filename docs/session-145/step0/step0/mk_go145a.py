"""Session 145 step 0 (HPP-350): build go145a.sh from C:/kyty/s144/go144a.sh (exact replacements; then the name moves
144 -> 145 of the chain, its tools, root and runs dir).  ASCII only, LF."""
import sys

t = open('C:/kyty/s144/go144a.sh', 'rb').read().decode('ascii')
assert '\r' not in t

HEAD = r'''#!/bin/bash
# Session 145 step 0 (HPP-350; ROADMAP s.0.1 "SESSION 122" item 273 (k)(1)-(7); brief docs/next-session-145.md): the
# game chain of the SCENE_OK series sc145 on the INSTALLED build 9235a7ac with its shipped defaults (an EMPTY gate file).
# Port of C:/kyty/s144/go144a.sh (pred/01_sc144.md): the same lock, guards, one attempt, order, seal call line, stop file,
# cache count and manifests, foreign-CPU row, winpid lock line - with the 34 tags of item 273 (k)(1), the W form of item
# 273 (k)(2) (validation, KYTY_PIPELINE_PRECACHE=0 and the filter of ONE message) and the stop rules of item 273 (k)(4).
# ASCII only.  No emulator code, no build.
#   TAGS AND ORDER (item 273 (k)(1); one call each, exactly this order):
#     w145_00            the control W on Sky Garden (underwater_aerial_garden)
#     w145_01            the W repeat of rocket_hourglass (its V is v144_09 of session 144 - the cross-session pair of
#                        item 254 (e), read by sc145.py; "Process" 1: a disturbance of the run, not an attempt of the level)
#     v145_NN, w145_NN   NN = 02..17, V then W per level, COLD first entries: small_pot_lava spin_drill_natural_cave
#                        enemy_taco jack_in_the_box final_shooting picup_light enemy_snake light_gadget_graveyard
#                        shuriken_ninja_castle final_stage mini_rocket_chain enemy_chameleon bonus_path_maker_mix enemy_bird
#                        cymbal_party_land enemy_final (last)
#   V (item 273 (k)(2)): -lvl entry, shipped defaults, video KYTY_REC, hold VHOLD=330 s, --stable-draws 300 --timeout 480,
#     --attempts 1 (the first entry of a never-entered level: the census of sc145.py goes into the cold pools).
#   W (item 254 (e), 273 (k)(2)): --vulkan-validation true with VK_LAYER_PATH and VK_LAYER_DUPLICATE_MESSAGE_LIMIT,
#     KYTY_PIPELINE_PRECACHE=0 AND VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER (the VUID string of the F6 warning, the one message
#     on which 13 W of s144 reached the duplicate limit; no other id) - positional, so enter_scene.py puts them into the env
#     and the json; no video, hold WHOLD=310 s, --stable-draws 300 --timeout 600, --attempts 1.
#   STOP RULES (item 273 (k)(4)): every call refuses rc 5 ("stop, question to the lead") when sc145.py --stop-check finds
#     the control W stopped (incl. its layer limit lines), two W in a row stopped before the first GuestOut line with one
#     key, three V in a row not entered with one marker, or a window event on the made tag right before.
#   The API check row of step 2 is written by step2/next_one.sh (step2/apichk145.py) before it starts this script; the
#     gate step2/gate145.py runs in step2/pre_one.sh; this script is called only through step2/next_one.sh.
# Session 144 header (carried):
# Session 144 step 0 (HPP-330;'''

R = []


def rep(old, new):
    R.append((old, new))


rep('#!/bin/bash\n# Session 144 step 0 (HPP-330;', HEAD)
rep('SEQ="w144_00 w144_01 w144_02 w144_03 w144_04 w144_05 w144_06 w144_07 w144_08 v144_09 w144_09 v144_10 w144_10 v144_11 '
    'w144_11 v144_12 w144_12 v144_13 w144_13 v144_14 w144_14 v144_15 w144_15 v144_16 w144_16 v144_17 w144_17 v144_18 '
    'w144_18 v144_19 w144_19 v144_20 w144_20"\n',
    'SEQ="w145_00 w145_01 ' + ' '.join('v145_%02d w145_%02d' % (i, i) for i in range(2, 18)) + '"\n')
LV = ('small_pot_lava', 'spin_drill_natural_cave', 'enemy_taco', 'jack_in_the_box', 'final_shooting', 'picup_light',
      'enemy_snake', 'light_gadget_graveyard', 'shuriken_ninja_castle', 'final_stage', 'mini_rocket_chain',
      'enemy_chameleon', 'bonus_path_maker_mix', 'enemy_bird', 'cymbal_party_land', 'enemy_final')
i0 = t.index('  w144_00) LEVEL=underwater_aerial_garden;;\n')
i1 = t.index('  *) echo "usage: go144a.sh')
rep(t[i0:i1], '  w145_00) LEVEL=underwater_aerial_garden;;\n  w145_01) LEVEL=rocket_hourglass;;\n' + ''.join(
    '  v145_%02d|w145_%02d) LEVEL=%s;;\n' % (i + 2, i + 2, lv) for i, lv in enumerate(LV)))
rep('  *) echo "usage: go144a.sh w144_00 .. w144_08 | v144_09|w144_09 .. v144_20|w144_20  (see the header)"; exit 2;;\n',
    '  *) echo "usage: go145a.sh w145_00 | w145_01 | v145_02|w145_02 .. v145_17|w145_17  (see the header)"; exit 2;;\n')
rep('VKDUP="1000000"\n', 'VKDUP="1000000"\nVKFILTER="Undefined-Value-ShaderOutputNotConsumed-DynamicRendering"\n')
rep('          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0";;\n',
    '          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0 '
    'VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER";;\n')
rep('''  log "go144a.sh $T refused (rc 5): a stop rule of item 254 (k)(4) (the control W, two W, three V - the stop-check lines above); question to the lead"''',
    '''  log "go144a.sh $T refused (rc 5): a stop rule of item 273 (k)(4) (the control W, two W, three V, the window event - the stop-check lines above); question to the lead"''')
rep('''  log "go144a.sh $T refused: $MARK or $T.json exists - the one attempt of $T was made (item 254 (k)(2): --attempts 1, no repeat)"''',
    '''  log "go144a.sh $T refused: $MARK or $T.json exists - the one attempt of $T was made (item 273 (k)(2): --attempts 1, no repeat)"''')
rep('''  log "go144a.sh $T refused: the call $PREV before it was not made (item 254 (k)(1): the sealed order)"''',
    '''  log "go144a.sh $T refused: the call $PREV before it was not made (item 273 (k)(1): the sealed order)"''')
for old, new in R:
    n = t.count(old)
    if n != 1:
        print('ANCHOR COUNT %d: %r' % (n, old[:100]))
        sys.exit(1)
    t = t.replace(old, new)
hs = t.index('# Session 144 header (carried):\n')
he = t.index('\nT=${1:-}\n')
body = t[he:]
for a, b in (('go144a', 'go145a'), ('fgcpu144', 'fgcpu145'), ('cachemf144', 'cachemf145'), ('lockcheck144', 'lockcheck145'),
             ('runs144', 'runs145'), ('C:/kyty/s144', 'C:/kyty/s145'), ('/c/kyty/s144/STOP', '/c/kyty/s145/STOP'),
             ('pred/01_sc144.md', 'pred/01_sc145.md'), ('SC="sc144.py"', 'SC="sc145.py"'),
             ('  v144_*) SD=', '  v145_*) SD='), ('  w144_*) SD=', '  w145_*) SD='),
             ("'mut_[a-z0-9_]*144|test_[a-z0-9_]*144|mutlib'", "'mut_[a-z0-9_]*145|test_[a-z0-9_]*145|mutlib'")):
    body = body.replace(a, b)
t = t[:he] + body
left = [x for x in body.split('\n') if '144' in x]
if left:
    print('LEFT 144 in the body:', left)
    sys.exit(1)
t.encode('ascii')
open('C:/kyty/s145/go145a.sh', 'wb').write(t.encode('ascii'))
print('mk_go145a: %d replacements, %d bytes' % (len(R), len(t)))
