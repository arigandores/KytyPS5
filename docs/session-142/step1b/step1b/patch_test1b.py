"""Link 1b (HPP-282): patch test_sc142.py for item 224 (a) - the changed expectations (o7b replaced by h1, o7c, k6, k11b, m4,
m8), the W validation lines, the sheet/video/times files of mkrun, the new pair() parameters, and the new block
step1b/fx1b_block.py before the final count.  Every anchor must hit exactly once; LF written."""
from pathlib import Path

P = Path('C:/kyty/s142/test_sc142.py')
t = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
BLOCK = Path('C:/kyty/s142/step1b/fx1b_block.py').read_bytes().decode('utf-8').replace('\r\n', '\n')


def rep(a, b):
    global t
    assert t.count(a) == 1, a[:80]
    t = t.replace(a, b)


rep('"""Offline fixtures of sc142.py (the scorer of the scene census sc142 and of SCENE_OK on Sky Garden; session 142 step 0,\n'
    'HPP-277;',
    '"""Offline fixtures of sc142.py (the scorer of the scene census sc142 and of SCENE_OK on Sky Garden; session 142 step 0,\n'
    'HPP-277; link 1b HPP-282: the RC1-RC10 terms of item 224 (a) in the block "link 1b" at the end;')
rep("import shutil\nimport sys\n", "import shutil\nimport sys\nimport hashlib as _h\n")
rep("""    if sheet:
        (root / ('sheet_%s.png' % tag)).write_bytes(b'png')
    return str(root)""",
    """    if sheet:
        (root / ('sheet_%s.png' % tag)).write_bytes(b'png')
        (root / ('rec_%s.mp4' % tag)).write_bytes(('mp4 ' + tag).encode())
        (root / 'step2').mkdir(exist_ok=True)
        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
            f.write('2026-09-30T00:00:00Z go142a %s s51_vidglitch rc 0 glitch_%s.txt sha256 %s rec_%s.mp4 sha256 %s\\n' % (
                tag, tag, 'ab' * 32, tag, _h.sha256(('mp4 ' + tag).encode()).hexdigest()))
            f.write('2026-09-30T00:00:00Z go142a %s sheet rc 0 sheet_%s.png sha256 %s\\n' % (
                tag, tag, _h.sha256(b'png').hexdigest()))
    if not stdout:
        (root / ('stdout_%s.txt' % tag)).unlink()
    return str(root)""")
rep("def mkrun(root, tag, lines, js=None, stdout_lines=(), es_lines=(), glitch=(3200, 0), sheet=True, log=True):",
    "def mkrun(root, tag, lines, js=None, stdout_lines=(), es_lines=(), glitch=(3200, 0), sheet=True, log=True, stdout=True):")
rep("""e = census('o7b', LONG, js=js_for('c142_01', attempt=dict(ft_tail=None, hold_s=None, outcome='timeout')))
ok &= case('o7b ft_tail None -> no tail stall; timeout of enter_scene is not a marker', not e['tail_stall']
           and e['outcome'] == 'HOLDS_120')
""", "")
rep("""ok &= case('o7c ft_tail 0 without a hold (hold_s None) -> no tail stall', not e['tail_stall'] and e['outcome'] == 'HOLDS_120')""",
    """ok &= case('o7c ft_tail 0 without a hold (hold_s None) -> no tail stall; no stable -> NOT_EVALUABLE (item 224 (a)(4))',
           not e['tail_stall'] and e['outcome'] == 'NOT_EVALUABLE')""")
rep("W_LINES = scene_lines(SKY, [150000] * 2000) + ['[Vulkan][W][2]: vkCmdDrawIndexed(): warn'] * 3\n",
    "VF = 'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features, version = 2'\n"
    "VW = '[Vulkan][W][2]: vkCmdDrawIndexed(): warn'\n"
    "W_BASE = scene_lines(SKY, [150000] * 2000)\n"
    "W_LINES = [VF] + W_BASE + [VW] * 3\n")
rep("""def pair(name, v_lines=None, w_lines=None, v_js=None, w_js=None, v_glitch=(3200, 0), w_extra=(), v_std=(), w_es=()):
    root = BASE / name
    mkrun(root, 'v142', v_lines if v_lines is not None else scene_lines(SKY, v_post()), js=v_js, glitch=v_glitch,
          stdout_lines=v_std)
    mkrun(root, 'w142', (w_lines if w_lines is not None else W_LINES) + list(w_extra), js=w_js, glitch=None, sheet=False,
          es_lines=w_es)""",
    """def pair(name, v_lines=None, w_lines=None, v_js=None, w_js=None, v_glitch=(3200, 0), w_extra=(), v_std=(), w_es=(),
         w_std=(), v_es=()):
    root = BASE / name
    mkrun(root, 'v142', v_lines if v_lines is not None else scene_lines(SKY, v_post()), js=v_js, glitch=v_glitch,
          stdout_lines=v_std, es_lines=v_es)
    mkrun(root, 'w142', (w_lines if w_lines is not None else W_LINES) + list(w_extra), js=w_js, glitch=None, sheet=False,
          es_lines=w_es, stdout_lines=w_std)""")
rep("""ok &= case('k6 V hold_exit', fails('k6', 'V 0 death markers', v_js=js_for('v142', attempt=dict(hold_exit=1))))""",
    """v, w = pair('k6', v_js=js_for('v142', attempt=dict(hold_exit=1)))
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('k6 V hold_exit -> the death row and the attempt row (item 224 (a)(4)) fail', word == 'NO' and
           row_ok(rows, 'V 0 death markers') is False and row_ok(rows, 'V attempt ok') is False
           and sum(1 for r in rows if not r[1]) == 2)""")
rep("""ok &= case('k11b V glitch file missing', fails('k11b', 'V 0 one-frame', v_glitch=None))""",
    """v, w = pair('k11b', v_glitch=None)
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('k11b V glitch file missing -> the glitch, video and coverage rows fail', word == 'NO' and
           row_ok(rows, 'V 0 one-frame') is False and row_ok(rows, 'V video >= 3000') is False and
           row_ok(rows, 'V video frames >=') is False and sum(1 for r in rows if not r[1]) == 3)""")
rep("""           and 'CENSUS made 4 of 10, admitted 3' in out2)""",
    """           and 'CENSUS made 4 of 10 (of them attempt made without json 0), admitted 3' in out2)""")
rep("""S.PRED_PATH == 'C:/kyty/s142/pred/01_sc142.md')""", """S.PRED_PATH == 'C:/kyty/s142/pred/02_sc142.md')""")
rep("print('checks: %d' % N_CASES[0])\n", BLOCK + "print('checks: %d' % N_CASES[0])\n")
P.write_bytes(t.encode('utf-8'))
print('patched', len(t))
