"""Session 144 step 0 (HPP-330): build go144a.sh from C:/kyty/s143/go143a.sh (exact replacements, then the name moves
143 -> 144 of the chain, its tools, root and runs dir).  ASCII only, LF."""
import sys

t = open('C:/kyty/s143/go143a.sh', 'rb').read().decode('ascii')
assert '\r' not in t

HEAD = r'''#!/bin/bash
# Session 144 step 0 (HPP-330; ROADMAP s.0.1 "SESSION 122" item 254 (e), (k)(1)-(7); brief docs/next-session-144.md): the
# game chain of the SCENE_OK series sc144 on the INSTALLED build 9235a7ac with its shipped defaults (an EMPTY gate file).
# Port of C:/kyty/s143/go143a.sh (pred/02_sc143.md, link 1b HPP-321): the same lock, guards, one attempt, order, seal call
# line, stop file, cache count and manifests, foreign-CPU row, winpid lock line - with the 33 tags of item 254 (k)(1), the
# W form of item 254 (e) and the stop rules of item 254 (k)(4).  ASCII only.  No emulator code, no build.
#   TAGS AND ORDER (item 254 (k)(1); one call each, exactly this order):
#     w144_00            the control W on Sky Garden (underwater_aerial_garden)
#     w144_01..w144_08   W only: spring_punch_sky_aztec booster_construction mini_astro_clock_tower path_maker_mana_tree
#                        spring_punch_monster_cave gulliver_island booster_magic_lamp rocket_space_station (their V is
#                        v143_NN of session 143 - the cross-session pair of item 254 (e), read by sc144.py)
#     v144_NN, w144_NN   NN = 09..20, V then W per level: rocket_hourglass pot_treasure_cave bumper_enemy_snowy_canyon
#                        big_hand_pirate_island timestop_casino ice_iceberg sponge_dirty_bath hoover_beach volcano_mountain
#                        voxel_world enemy_gorilla mini_giants_garden (last)
#   V (item 254 (k)(2)): -lvl entry, shipped defaults, video KYTY_REC, hold VHOLD=330 s, --stable-draws 300 --timeout 480,
#     --attempts 1 (a repeated entry of the level: sc144.py marks its map row).
#   W (item 254 (e), (k)(2)): --vulkan-validation true with VK_LAYER_PATH and VK_LAYER_DUPLICATE_MESSAGE_LIMIT AND
#     KYTY_PIPELINE_PRECACHE=0 (positional, so enter_scene.py puts it into the env and the json), no video, hold WHOLD=310 s,
#     --stable-draws 300 --timeout 600, --attempts 1.
#   STOP RULES (item 254 (k)(4)): every call refuses rc 5 ("stop, question to the lead") when sc144.py --stop-check finds
#     the control W stopped, two W in a row stopped before the first GuestOut line with one key, or three V in a row not
#     entered with one marker before it.
#   The API check row of step 2 (MINOR-4 of audit 143) is written by step2/next_one.sh (step2/apichk144.py) before it
#     starts this script; this script is called only through step2/next_one.sh.
# Session 143 header (carried):
# Session 143 step 0 (HPP-297;'''

R = []


def rep(old, new):
    R.append((old, new))


rep('#!/bin/bash\n# Session 143 step 0 (HPP-297;', HEAD)
rep('SEQ="v143_01 w143_01 v143_02 w143_02 v143_03 w143_03 v143_04 w143_04 v143_05 w143_05 v143_06 w143_06 v143_07 w143_07 '
    'v143_08 w143_08 v143_09 w143_09 v143_10 w143_10"\n',
    'SEQ="w144_00 w144_01 w144_02 w144_03 w144_04 w144_05 w144_06 w144_07 w144_08 v144_09 w144_09 v144_10 w144_10 v144_11 '
    'w144_11 v144_12 w144_12 v144_13 w144_13 v144_14 w144_14 v144_15 w144_15 v144_16 w144_16 v144_17 w144_17 v144_18 '
    'w144_18 v144_19 w144_19 v144_20 w144_20"\n')
rep(r'''  v143_01|w143_01) LEVEL=spring_punch_sky_aztec;;
  v143_02|w143_02) LEVEL=booster_construction;;
  v143_03|w143_03) LEVEL=mini_astro_clock_tower;;
  v143_04|w143_04) LEVEL=path_maker_mana_tree;;
  v143_05|w143_05) LEVEL=spring_punch_monster_cave;;
  v143_06|w143_06) LEVEL=gulliver_island;;
  v143_07|w143_07) LEVEL=rocket_hourglass;;
  v143_08|w143_08) LEVEL=pot_treasure_cave;;
  v143_09|w143_09) LEVEL=booster_magic_lamp;;
  v143_10|w143_10) LEVEL=rocket_space_station;;
  *) echo "usage: go143a.sh v143_01|w143_01 .. v143_10|w143_10  (see the header)"; exit 2;;
''', r'''  w144_00) LEVEL=underwater_aerial_garden;;
  w144_01) LEVEL=spring_punch_sky_aztec;;
  w144_02) LEVEL=booster_construction;;
  w144_03) LEVEL=mini_astro_clock_tower;;
  w144_04) LEVEL=path_maker_mana_tree;;
  w144_05) LEVEL=spring_punch_monster_cave;;
  w144_06) LEVEL=gulliver_island;;
  w144_07) LEVEL=booster_magic_lamp;;
  w144_08) LEVEL=rocket_space_station;;
  v144_09|w144_09) LEVEL=rocket_hourglass;;
  v144_10|w144_10) LEVEL=pot_treasure_cave;;
  v144_11|w144_11) LEVEL=bumper_enemy_snowy_canyon;;
  v144_12|w144_12) LEVEL=big_hand_pirate_island;;
  v144_13|w144_13) LEVEL=timestop_casino;;
  v144_14|w144_14) LEVEL=ice_iceberg;;
  v144_15|w144_15) LEVEL=sponge_dirty_bath;;
  v144_16|w144_16) LEVEL=hoover_beach;;
  v144_17|w144_17) LEVEL=volcano_mountain;;
  v144_18|w144_18) LEVEL=voxel_world;;
  v144_19|w144_19) LEVEL=enemy_gorilla;;
  v144_20|w144_20) LEVEL=mini_giants_garden;;
  *) echo "usage: go144a.sh w144_00 .. w144_08 | v144_09|w144_09 .. v144_20|w144_20  (see the header)"; exit 2;;
''')
rep('the one attempt of $T was made (item 231 (i)(2): no repeat)"',
    'the one attempt of $T was made (item 254 (k)(2): --attempts 1, no repeat)"')
rep('the call $PREV before it was not made (item 231 (i)(1)-(2): per level V then W, the levels in order)"',
    'the call $PREV before it was not made (item 254 (k)(1): the sealed order)"')
rep('  v143_*) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec";;\n',
    '  v144_*) SD="--stable-draws 300 --timeout 480"; HOLD=$VHOLD; REC="--rec";;\n')
rep('  w143_*) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD\n',
    '  w144_*) SD="--stable-draws 300 --timeout 600"; HOLD=$WHOLD\n')
rep('          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP";;\n',
    '          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0";;\n')
rep('refused (rc 5): the stop rule of item 231 (i)(4) - three V in a row not entered with one marker; question to the lead"',
    'refused (rc 5): a stop rule of item 254 (k)(4) (the control W, two W, three V - the stop-check lines above); '
    'question to the lead"')
rep('PRED="pred/02_sc143.md"\n', 'PRED="pred/01_sc144.md"\n')
for old, new in R:
    n = t.count(old)
    if n != 1:
        print('ANCHOR COUNT %d: %r' % (n, old[:100]))
        sys.exit(1)
    t = t.replace(old, new)
# the name moves (after the header, which keeps the carried 143 text)
cut = t.index('# Session 143 header (carried):')
end = t.index('\nT=${1:-}\n')
body = t[end:]
for old, new in (('C:/kyty/s143', 'C:/kyty/s144'), ('/c/kyty/s143/', '/c/kyty/s144/'), ('go143a', 'go144a'),
                 ('fgcpu143', 'fgcpu144'), ('cachemf143', 'cachemf144'), ('lockcheck143', 'lockcheck144'),
                 ('runs143', 'runs144'), ('sc143.py', 'sc144.py'),
                 ("'mut_[a-z0-9_]*143|test_[a-z0-9_]*143|mutlib'", "'mut_[a-z0-9_]*144|test_[a-z0-9_]*144|mutlib'")):
    body = body.replace(old, new)
t = t[:end] + body
left = [l for l in body.split('\n') if '143' in l]
print('lines of the body still naming 143: %d' % len(left))
for l in left:
    print('  ' + l[:160])
t.encode('ascii')
open('C:/kyty/s144/go144a.sh', 'wb').write(t.encode('ascii'))
print('mk_go144a: %d replacements, %d bytes' % (len(R), len(t)))
