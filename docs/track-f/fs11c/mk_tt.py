t = open('C:/kyty/KytyPS5/docs/track-f/f29e/test_tools_f29e.py', encoding='ascii').read()
NL = chr(10)
R = [
('''"""F29e (HPP-704): fixtures of the harness tools - the dry run of go_f29e.sh for both tags (form, knobs, hold, video), refusals of
go / launch / post (usage), the launcher checks in fixture mode (F29E_DRYRUN=2 with a fake process list and a fake block), mfsub_f29e.py,
enter_scene.py (ROOT), the copies of the FS10c tools (only names moved), and strict cp1250 output of each tool without PYTHONIOENCODING.
Port of C:/kyty/f287/fs10c/test_tools_fs10c.py.''',
'''"""FS11c (HPP-716): fixtures of the harness tools - the dry run of go_fs11c.sh for the three tags (form, knobs, hold, video), refusals of
go / launch / post (usage), the launcher checks in fixture mode (FS11C_DRYRUN=2 with a fake process list and a fake block), mfsub_fs11c.py,
enter_scene.py (ROOT), the copies of the F29e tools (only names moved), and strict cp1250 output of each tool without PYTHONIOENCODING.
Port of C:/kyty/f287/f29e/test_tools_f29e.py (copy in git docs/track-f/f29e/).'''),
("M = 'C:/kyty/f287/fs10c'", "M = '@@M@@'"),
("""V = 'dryrun %s base b12_v level %s uf - sd 300 hold 330 timeout 480 rec --rec knobs KYTY_FIX_B12=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
W = ('dryrun %s base b12_w level %s uf - sd 100 hold 310 timeout 900 rec --emu-arg=--vulkan-validation --emu-arg=true knobs KYTY_FIX_B12=1 '
     'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0')
CASES = [('b12_v', V % ('b12_v', SKY)), ('b12_w', W % ('b12_w', SKY)), ('b12_v_r1', V % ('b12_v_r1', SKY)), ('b12_w_r3', W % ('b12_w_r3', SKY))]""",
"""V = 'dryrun %s base fs11_v level %s uf - sd 300 hold 330 timeout 480 rec --rec knobs KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
W = ('dryrun %s base fs11_w level %s uf - sd 100 hold 310 timeout 900 rec --emu-arg=--vulkan-validation --emu-arg=true knobs '
     'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0')
Z = 'dryrun %s base fs11_z level %s uf - sd 300 hold 150 timeout 480 rec --rec knobs KYTY_FIX_B12=0 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0'
CASES = [('fs11_v', V % ('fs11_v', SKY)), ('fs11_w', W % ('fs11_w', SKY)), ('fs11_z', Z % ('fs11_z', SKY)), ('fs11_v_r1', V % ('fs11_v_r1', SKY)),
         ('fs11_w_r3', W % ('fs11_w_r3', SKY)), ('fs11_z_r2', Z % ('fs11_z_r2', SKY))]"""),
("""          'KYTY_DIAG_B32' not in out and out.count('KYTY_FIX_') == 1 and 'GAME_PATCH' not in out)
for bad in ('fs10_v', 'b13_v', 'b12_v_r4', 'b12_x', ''):""",
"""          'KYTY_DIAG_B32' not in out and out.count('KYTY_FIX_') == (1 if '_z' in tag else 0) and 'GAME_PATCH' not in out)
for bad in ('fs10_v', 'b12_v', 'b12_w', 'fs11_v_r4', 'fs11_x', ''):"""),
("check('go: F29c full sha', 'TB=cabbd818397a8a299e7e64cf2d153197ad7e69e310015b5d473bb66f37802e95' in GOT)",
 "check('go: FS11 full sha', 'TB=ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce' in GOT)"),
("'BIN=$F/bin/kyty_emulator_cabbd818.exe' in GOT", "'BIN=$F/bin/kyty_emulator_ea51ae80.exe' in GOT"),
("check('go: no KYTY_GPU_CHECKPOINTS, no --rd, no fs10c path in the code lines', 'GPU_CHECKPOINTS' not in CODE and '--rd' not in CODE" + NL +
 "      and 'fs10c' not in CODE and '3861eeea' not in CODE)",
 "check('go: no KYTY_GPU_CHECKPOINTS, no --rd, no @@OLD@@ path in the code lines', 'GPU_CHECKPOINTS' not in CODE and '--rd' not in CODE" + NL +
 "      and '@@OLD@@' not in CODE and 'cabbd818' not in CODE and 'b12_' not in CODE)"),
("""# go = the FS10c chain with the binaries, the tags and the knob moved (the code lines after the header)
GS = open(os.path.join(M, 'go_fs10c.sh'), encoding='ascii').read()""",
"""# go = the F29e chain with the binary, the tags and the knobs moved (the code lines after the header)
GS = open(os.path.join(M, 'go_@@OLD@@.sh'), encoding='ascii').read()"""),
("""kept = [l for l in body_old.split('\\n') if 'fs10' not in l and 'FS10' not in l and 'FS9' not in l and 'STAND' not in l
        and not l.startswith(('TB=', 'BIN=', 'PINNED=')) and not l.lstrip().startswith('KN=')]
check('go: every FS10c code line without fs10 / FS9 / STAND is kept verbatim (%d lines)' % len(kept),""",
"""kept = [MOVE(l) for l in body_old.split('\\n') if 'b12_' not in l and 'F29c' not in l and 'cabbd818' not in l
        and not l.startswith(('TB=', 'BIN=')) and not l.lstrip().startswith('KN=')]
check('go: every F29e code line without b12_ / F29c / cabbd818 is kept verbatim with names moved (%d lines)' % len(kept),"""),
("rc, out, raw = sh([LA, 'b12_v'], X)" + NL + "check('launch: block not open", "rc, out, raw = sh([LA, 'fs11_v'], X)" + NL + "check('launch: block not open"),
("rc, out, raw = sh([LA, 'b12_v'], X)" + NL + "check('launch: open block", "rc, out, raw = sh([LA, 'fs11_z'], X)" + NL + "check('launch: open block"),
("rc, out, raw = sh([LA, 'b12_v'], X)" + NL + "check('launch: user emulator", "rc, out, raw = sh([LA, 'fs11_w'], X)" + NL + "check('launch: user emulator"),
("for bad in ('nope', 'fs10_v', 'b12_v_r4'):", "for bad in ('nope', 'b12_v', 'fs11_v_r4'):"),
("'C:/kyty/f287/fs10c/runs/fs10_v/sheet_fs10_v.png' in PT", "'@@PIN@@' in PT and 'pair_${T}_b12_v.png' in PT"),
("check('enter_scene: = the FS10c file with names moved', ES == ESM.replace('fs10c', 'f29e').replace('FS10C', 'F29E').replace('FS10c', 'F29e')" + NL +
 "      .replace('HPP-686', 'HPP-704'))",
 "check('enter_scene: = the F29e file with names moved', ES == MOVE(ESM))"),
("    check('copy %s = FS10c' % nm,", "    check('copy %s = F29e' % nm,"),
("""    o = open(os.path.join(M, '%s_fs10c.py' % nm), encoding='utf-8').read()
    check('copy %s_f29e.py = FS10c with names moved' % nm,
          t == o.replace('fs10c', 'f29e').replace('FS10C', 'F29E').replace('FS10c', 'F29e').replace('HPP-686', 'HPP-704'))
    check('%s_f29e.py has no fs10c path' % nm, 'f287/fs10c' not in t)""",
"""    o = open(os.path.join(M, '%s_@@OLD@@.py' % nm), encoding='utf-8').read()
    check('copy %s_f29e.py = F29e with names moved' % nm, t == MOVE(o))
    check('%s_f29e.py has no @@OLD@@ path' % nm, 'f287/@@OLD@@' not in t)"""),
("def sha(p):", "def MOVE(s):" + NL + "    for a, b in (('@@OLD@@', 'fs11c'), ('@@OLDU@@', 'FS11C'), ('@@OLDC@@', 'FS11c'), ('@@OLDH@@', 'HPP-716')):" + NL +
 "        s = s.replace(a, b)" + NL + "    return s" + NL + NL + NL + "def sha(p):"),
]
for a, b in R:
    c = t.count(a)
    assert c == 1, (c, a[:70])
    t = t.replace(a, b)
for a, b in (('f29e', 'fs11c'), ('F29E', 'FS11C'), ('F29e', 'FS11c'), ('HPP-704', 'HPP-716')):
    t = t.replace(a, b)
for a, b in (('@@M@@', 'C:/kyty/f287/f29e'), ('@@PIN@@', 'C:/kyty/f287/f29e/runs/b12_v/sheet_b12_v.png'), ('@@OLDU@@', 'F29E'),
             ('@@OLDC@@', 'F29e'), ('@@OLDH@@', 'HPP-704'), ('@@OLD@@', 'f29e')):
    t = t.replace(a, b)
open('test_tools_fs11c.py', 'w', encoding='ascii', newline=NL).write(t)
print('ok')
