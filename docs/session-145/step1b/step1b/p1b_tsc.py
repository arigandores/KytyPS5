"""Link 1b of s145 (HPP-379; ROADMAP s122 item 295 (b), (g), (d), (e)): exact edits of C:/kyty/s145/test_sc145.py - PART E:
the W form without the filter (rows 295 (b)(1)-(4)), the window kinds and the nearest window line, the alignment of the
continuity, the regression rows NEW295; each anchor must occur once.  ASCII only.  python p1b_tsc.py"""
import hashlib
import sys

P = 'C:/kyty/s145/test_sc145.py'
src = open(P, 'rb').read().decode('utf-8')
assert '\r' not in src
N = [0]


def rep(old, new):
    global src
    c = src.count(old)
    if c != 1:
        print('ANCHOR COUNT %d: %r' % (c, old[:160]))
        sys.exit(1)
    N[0] += 1
    src = src.replace(old, new)


rep('''summary lines, the regression of profile 144 on a synthetic profile, the real constants, ASCII.
Session 144 header (carried): PARTS A-C: the whole
''', '''summary lines, the regression of profile 144 on a synthetic profile, the real constants, ASCII.
Link 1b of s145 (HPP-379, ROADMAP item 295): PART E drops the filter of one message; the W form rows 295 (b)(1)-(4) (held /
not held, the 10 s edge of (b)(3), the third field 2 exactly, the form line edges), the window lines by kind and the
nearest one to every K2 / K3 frame (+-2 s edges, entry / hold, stdout lines not positioned), the alignment of the video
continuity (shares within 8 ms, the best shift and its tie rule, the 10 % mark), the summary lines, the NEW295 rows of the
regression of profile 144 (cases E34-E44).
Session 144 header (carried): PARTS A-C: the whole
''')
rep('''ok &= case('E2 the root, seal, chain, runs dir, scorer of 145; the V of another session: v144_09 from root s144, chain go144a, '
           'seal pred/01_sc144.md; its sheet row fixed viewed by item 273 (a); halves of eight; the filter id; the flags',
           S.ROOT == 'C:/kyty/s145' and S.PRED_PATH == 'C:/kyty/s145/pred/02_sc145.md' and S.CHAIN == 'go145a' and
''', '''ok &= case('E2 the root, seal, chain, runs dir, scorer of 145; the V of another session: v144_09 from root s144, chain go144a, '
           'seal pred/01_sc144.md; its sheet row fixed viewed by item 273 (a); halves of eight; the W form line; the flags',
           S.ROOT == 'C:/kyty/s145' and S.PRED_PATH == 'C:/kyty/s145/pred/03_sc145.md' and S.CHAIN == 'go145a' and
''')
rep('''           S.W_STOP_RUN == 2 and S.HALF == 8 and S.NUMW == {5: 'five', 6: 'six'} and S.VKFILTER == FILT)
''', '''           S.W_STOP_RUN == 2 and S.HALF == 8 and S.NUMW == {5: 'five', 6: 'six'} and
           S.W_FORM_LINE == 'W form: limit=100000000 filter=none')
''')
rep('''           S.M_REC == b'Recovering Vulkan swapchain')
''', '''           S.M_REC == b'Recovering Vulkan swapchain')
ok &= case('E3c the constants of item 295: the end of the hold 10 s, +-2 s of the window line, 8 ms, +-50 ms, 600 rows, 10 %, the '
           '15 window kinds of window.cpp, the s144 W not held',
           S.LAYER_END_US == 10000000 and S.WIN_NEAR_US == 2000000 and S.VQ_NEAR == 0.008 and S.VQ_SHIFT_MS == 50 and
           S.VQ_ROWS == 600 and S.VQ_MARK == 0.10 and
           S.WIN_ALL == ('shown', 'hidden', 'exposed', 'moved to', 'resized', 'size changed', 'minimized', 'maximized',
                         'restored', 'gained keyboard focus', 'lost keyboard focus', 'closed', 'got unknown event',
                         'Mouse entered window', 'Mouse left window') and
           S.REGRESS144_NOTHELD == ('w144_09', 'w144_20') and S.REGRESS144_B3 == S.REGRESS144_LIMIT)
''')
rep('''          'step2/apichk145.py', 'step2/gate145.py', 'step2/test_gate145.py', 'C:/kyty/s144/step2/times.txt',
          'C:/kyty/s144/pred/01_sc144.md')
ok &= case('E6 the seal of 145 names the harness, scorer, fixtures, mutants, enter_scene.py, sheet142.py, s51_vidglitch.py, the '
           'tools, the step 2 wrappers with the API check and the gate, and the s144 times.txt and seal the pair reads; no '
           'name of 144', all(n in S.SEALED_NAMES for n in REQ145) and len(S.SEALED_NAMES) == 27 and
''', '''          'step2/apichk145.py', 'step2/gate145.py', 'step2/test_gate145.py', 'C:/kyty/s144/step2/times.txt',
          'C:/kyty/s144/pred/01_sc144.md', 'C:/kyty/s144/runs144/cache_w144_20.after.json')
ok &= case('E6 the seal of 145 names the harness, scorer, fixtures, mutants, enter_scene.py, sheet142.py, s51_vidglitch.py, the '
           'tools, the step 2 wrappers with the API check and the gate, the s144 times.txt and seal the pair reads and the '
           'reference of the gate (item 295 (e)); no name of 144', all(n in S.SEALED_NAMES for n in REQ145) and
           len(S.SEALED_NAMES) == 28 and
''')
rep('''def js145(tag, attempt=None, form=True, filt=FILT, **over):
''', '''def js145(tag, attempt=None, form=True, filt=None, dup='100000000', **over):
''')
rep('''        if filt is not None:
            env['VK_LAYER_MESSAGE_ID_FILTER'] = filt
    else:
''', '''        if filt is not None:
            env['VK_LAYER_MESSAGE_ID_FILTER'] = filt
        if dup is not None:
            env['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = dup
    else:
''')
rep('''ok &= case('E7 good control W, W repeat and the V and W of a pair are admitted; each W carries one filter row and the window '
           'row, the V the filter row of the shipped defaults and the window row',
           all(adm_ok(e) for e in eE.values()) and
           all(len(adm_rows(eE[t], 'W filter: ')) == 1 and len(adm_rows(eE[t], 'window event: ')) == 1
               for t in ('w145_00', 'w145_01', 'w145_02')) and
''', '''ok &= case('E7 good control W, W repeat and the V and W of a pair are admitted; each W carries the four rows of item 295 (b) '
           'and the window row, no filter row; the V the filter row of the shipped defaults and the window row',
           all(adm_ok(e) for e in eE.values()) and
           all([a[0][:11] for a in adm_rows(eE[t], 'W 295(b)(')] == ['W 295(b)(4)', 'W 295(b)(1)', 'W 295(b)(2)',
                                                                     'W 295(b)(3)'] and
               len(adm_rows(eE[t], 'window event: ')) == 1 and not adm_rows(eE[t], 'W filter')
               for t in ('w145_00', 'w145_01', 'w145_02')) and
''')
rep('''BADF = [('W without the filter', js145('w145_02', filt=None)),
        ('W filtering another id', js145('w145_02', filt='VUID-VkSwapchainCreateInfoKHR-imageExtent-01689')),
        ('W filtering the id and another one', js145('w145_02', filt=FILT + ',VUID-vkCmdDraw-None-02699')),
        ('W filtering the id with a blank', js145('w145_02', filt=FILT + ' ')),
        ('W filtering the hashed number', js145('w145_02', filt='0x5a3b6b9e'))]
for i, (name, js) in enumerate(BADF):
    e = S.entry_of('w145_02', mk145(BASE / ('E8_%d' % i), 'w145_02', js=js), SH5)
    ok &= case('E8 the W filter of item 273 (k)(2) violated -> the tag is not admitted by the filter row only: %s' % name,
               not adm_ok(e) and [a[0][:9] for a in e['admit'] if not a[1]] == ['W filter:'])
''', '''BADF = [('W with the filter of step 0', js145('w145_02', filt=FILT)),
        ('W with the limit of s144 (1000000)', js145('w145_02', dup='1000000')),
        ('W without the limit', js145('w145_02', dup=None)),
        ('W with the limit and a blank', js145('w145_02', dup='100000000 ')),
        ('W with a filter "none" in the env', js145('w145_02', filt='none')),
        ('W with an empty filter in the env', js145('w145_02', filt=''))]
for i, (name, js) in enumerate(BADF):
    e = S.entry_of('w145_02', mk145(BASE / ('E8_%d' % i), 'w145_02', js=js), SH5)
    ok &= case('E8 the W form line of item 295 (b)(4) violated -> the tag is not admitted by the row (b)(4) only: %s' % name,
               not adm_ok(e) and [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(4)'])
''')
rep('''ok &= case('E18 a non-control W with two limit lines -> admitted, printed LAYER TRUNCATED, the outcome by the letter: the pair '
           '(V v144_09 + W w145_01) YES; the LAYER LIMIT line names it; the control PASS',
           adm_ok(e18) and e18['limit'] == 2 and any(x.endswith('2 - LAYER TRUNCATED (the outcome stands by the letter)')
                                                     for x in S.fmt_entry(e18)) and
           '  layer limit lines ("this will be the last time reporting it", item 273 (k)(2)): 0' in S.fmt_entry(
               eE['w145_02']) and
           'SCENE_OK rocket_hourglass: YES' in o18 and
''', '''ok &= case('E18 a non-control W with two limit lines -> not admitted by the row (b)(1) only (item 295 (b)(1)), printed LAYER '
           'TRUNCATED: the pair (V v144_09 + W w145_01) NO; the LAYER LIMIT line names it; the control PASS',
           not adm_ok(e18) and [a[0][:11] for a in e18['admit'] if not a[1]] == ['W 295(b)(1)'] and e18['limit'] == 2 and
           any(x.endswith('2 - LAYER TRUNCATED (the outcome stands by the letter)') for x in S.fmt_entry(e18)) and
           '  layer limit lines ("this will be the last time reporting it", item 273 (k)(2)): 0' in S.fmt_entry(
               eE['w145_02']) and
           'SCENE_OK rocket_hourglass: NO' in o18 and
''')
rep('''ok &= case('E19 the F6 text lines (2) and the validation-type lines (bit 2 of the type: [2] x5 incl. the 3 of wl and F6 x2, '
           '[3]; not [1], [4]) are counted for the print, not the verdict',
           e['f6'] == 2 and e['vkval'] == 6 and adm_ok(e) and any(
               x == '  message filter (item 273 (k)(2)): lines of the filtered F6 text ("... and this write is unused.") 2; '
               '[Vulkan][ lines of the validation type (bit 2) 6 (info, not in the verdict)' for x in S.fmt_entry(e)))
''', '''ok &= case('E19 the F6 text lines (2), the validation-type lines (bit 2 of the type: [2] x5 incl. the 3 of wl and F6 x2, [3]; '
           'not [1], [4]) and the validation-layer lines of item 295 (b)(2) (third field 2 exactly: 5) are printed; the W form '
           'print of item 295 (b)',
           e['f6'] == 2 and e['vkval'] == 6 and e['vk2'] == 5 and adm_ok(e) and any(
               x == '  W form of item 295 (b): held; the form line "W form: limit=100000000 filter=none" (PASS); '
               'validation-layer lines [W][2] / [E][2] 5 (log and stdout); the last one of the log 0.000 s before the last '
               'FrameTrace row of the hold; F6 text lines ("... and this write is unused.") 2; [Vulkan][ lines of the '
               'validation type (bit 2) 6 (info)' for x in S.fmt_entry(e)))
''')
rep('''    mk145(R24, t, lines=lines, extra=[LIM] if t == 'w145_02' else ())
''', '''    mk145(R24, t, lines=lines)
''')
rep('''ok &= case('E24b the new summary lines: window events none, layer limit (control PASS, w145_02 truncated), the W filter 3 of 3 '
           'and V 3 of 3, the video continuity line; the W FORM line of 254 (e) still printed',
''', '''ok &= case('E24b the new summary lines: window events none, layer limit (control PASS, none truncated), the W FORM 295 line 3 '
           'of 3 and V 3 of 3, the window lines by kind, near none, the alignment none, the video continuity line; the W FORM '
           'line of 254 (e) still printed',
''')
rep('''           'LAYER LIMIT (item 273 (k)(2)): control W w145_00: 0 lines -> PASS; other W with layer limit lines (layer truncated, '
           'the outcome by the letter): w145_02' in o24 and
           'W FILTER (item 273 (k)(2)): VK_LAYER_MESSAGE_ID_FILTER=%s in 3 of 3 made W; V without it 3 of 3 made; violated: '
           'none; lines of the filtered F6 text in the W (info): w145_00 0, w145_01 0, w145_02 0' % FILT in o24 and
''', '''           'LAYER LIMIT (item 273 (k)(2)): control W w145_00: 0 lines -> PASS; other W with layer limit lines (layer truncated, '
           'the outcome by the letter): none' in o24 and
           'W FORM 295 (item 295 (b)(1)-(4): 0 layer limit lines, validation active by [W][2] / [E][2] lines, the last one '
           'within 10 s of the hold end, the form line W form: limit=100000000 filter=none): every row passed by 3 of 3 made W; '
           'failing: none; not held (rows (1)-(3) n/a): none; V without VK_LAYER_MESSAGE_ID_FILTER 3 of 3 made, violated: none; '
           'F6 text lines in the W (info): w145_00 0, w145_01 0, w145_02 0' in o24 and
           'WINDOW LINES BY KIND (item 295 (g); log and stdout; data): v145_03: restored 1' in o24 and
           'WINDOW LINE NEAR A K2 / K3 FRAME (item 295 (g); within 2 s; data): none' in o24 and
           'VIDEO CONTINUITY ALIGNMENT (item 295 (d); data, not a gate): V whose count at the best anchor shift differs by more '
           'than 10 % [I]: none' in o24 and
''')
rep('''mk145(R24, 'w145_02', js=js145('w145_02', filt=None))
o24f = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24c a W without the filter in the summary: the W FILTER line names it, its level NO by "W admitted"',
           any(x.startswith('W FILTER (item 273 (k)(2)):') and 'in 2 of 3 made W' in x and 'violated: w145_02;' in x
               for x in o24f) and 'SCENE_OK small_pot_lava: NO' in o24f)
''', '''mk145(R24, 'w145_02', js=js145('w145_02', filt=FILT))
o24f = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24c a W with the filter of step 0 in the summary: the W FORM 295 line names it by (b)(4), its level NO by "W '
           'admitted"', any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'every row passed by 2 of 3 made W; failing: '
                            'w145_02 (b)(4);' in x for x in o24f) and 'SCENE_OK small_pot_lava: NO' in o24f)
''')
rep('''ok &= case('E24d a V with the filter in the summary: the W FILTER line counts it among the V and names it after the W',
           any(x.startswith('W FILTER (item 273 (k)(2)):') and 'V without it 2 of 3 made' in x and
               'violated: w145_02,v145_03;' in x for x in o24g))
''', '''ok &= case('E24d a V with the filter in the summary: the W FORM 295 line counts it among the V and names it',
           any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'V without VK_LAYER_MESSAGE_ID_FILTER 2 of 3 made, '
               'violated: v145_03;' in x for x in o24g))
mk145(R24, 'w145_02', extra=[LIM])
o24h = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24e a W with a limit line in the summary: the W FORM 295 line names it by (b)(1), the LAYER LIMIT line names it, '
           'its level NO', any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'failing: w145_02 (b)(1);' in x
                               for x in o24h) and 'SCENE_OK small_pot_lava: NO' in o24h and any(
               x.startswith('LAYER LIMIT (item 273 (k)(2)):') and x.endswith('the outcome by the letter): w145_02') for x in o24h))
mk145(R24, 'w145_02', js=js145('w145_02', attempt=dict(outcome='timeout')))
o24i = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24f a W not held (timeout) in the summary: the W FORM 295 line names it among the not held',
           any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'not held (rows (1)-(3) n/a): w145_02;' in x for x in o24i))
''')
rep('''S.REGRESS144_WINEV, S.REGRESS144_LIMIT = ('w144_09',), ('w144_09',)
XB = dict(S.XSRC)
''', '''S.REGRESS144_WINEV, S.REGRESS144_LIMIT = ('w144_09',), ('w144_09',)
NOTHELD_REAL, B3_REAL = S.REGRESS144_NOTHELD, S.REGRESS144_B3
S.REGRESS144_NOTHELD, S.REGRESS144_B3 = (), ()
XB = dict(S.XSRC)
''')
rep('''           'NEW ROWS of profile 145 on the same logs (not in the regression file; item 273 (k)(2)-(3)):' in l4 and
''', '''           'NEW ROWS of profile 145 on the same logs (not in the regression file; item 273 (k)(2)-(3)):' in l4 and
           'NEW295 ROWS held: W not held (rows (1)-(3) n/a) none (expected : stopped by validation) -> PASS' in l4 and
           any(x.startswith('NEW295 ROWS (b)(1) layer limit lines 0:') and x.endswith('failing 1 w144_09 -> PASS') for x in l4)
           and any(x.startswith('NEW295 ROWS (b)(4) the form line:') and x.endswith('failing 2 w144_00,w144_09 -> PASS')
                   for x in l4) and
           any(x.startswith('NEW295 w144_09 W: held; (b)(1) 1 -> FAIL; (b)(2) ') for x in l4) and
           any(x.startswith('NEW295 v144_09 V: window lines ') for x in l4) and
''')
rep('''old = S.profile(S.P144)
mk144(RG4, 'w144_00', lines=wl(SKY) + [LIM], js=dict(js144('w144_00'), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
''', '''S.REGRESS144_B3 = ('w144_09',)
ok4j, l4j = S.regress144(str(EX4), str(VX4))
S.REGRESS144_B3, S.REGRESS144_NOTHELD = (), ('w144_09',)
ok4k, l4k = S.regress144(str(EX4), str(VX4))
S.REGRESS144_NOTHELD = ()
ok &= case('E29c the NEW295 rows decide alone (the old rows pass): another expected set of (b)(3) -> FAIL; another not-held '
           'set -> FAIL', not ok4j and any(x.startswith('NEW295 ROWS (b)(3)') and x.endswith('-> FAIL') for x in l4j) and
           all(not x.endswith('-> FAIL') for x in l4j if not x.startswith('NEW295 ROWS (b)(3)')) and not ok4k and
           any(x.startswith('NEW295 ROWS held:') and x.endswith('-> FAIL') for x in l4k) and
           all(not x.endswith('-> FAIL') for x in l4k if not x.startswith('NEW295 ROWS held:')))
old = S.profile(S.P144)
mk144(RG4, 'w144_09', lines=wl('rocket_hourglass')[:30] + [WMIN, WREC, LIM] + wl('rocket_hourglass')[30:],
      js=dict(js144('w144_09', attempt=dict(hold_exit=5.0)), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
S.profile(old)
S.REGRESS144_NOTHELD = ('w144_09',)
ok4m, l4m = S.regress144(str(EX4), str(VX4))
S.REGRESS144_NOTHELD = ()
ok &= case('E29d a W of the profile 144 not held (hold_exit) -> the held row names it and passes when expected; its rows '
           '(1)-(3) are n/a', 'NEW295 ROWS held: W not held (rows (1)-(3) n/a) w144_09 (expected w144_09: stopped by '
           'validation) -> PASS' in l4m and any(x.startswith('NEW295 w144_09 W: NOT held (hold_exit / ENDED / exited); (b)(1) '
                                                             'n/a (W not held: hold_exit / ENDED / exited) -> PASS') for x in l4m))
old = S.profile(S.P144)
mk144(RG4, 'w144_00', lines=wl(SKY) + [LIM], js=dict(js144('w144_00'), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
''')
rep('''S.P144 = P144_REAL
S.REGRESS144_WINEV, S.REGRESS144_LIMIT = WINEV_REAL, LIMIT_REAL
''', '''S.P144 = P144_REAL
S.REGRESS144_WINEV, S.REGRESS144_LIMIT = WINEV_REAL, LIMIT_REAL
S.REGRESS144_NOTHELD, S.REGRESS144_B3 = NOTHELD_REAL, B3_REAL
''')

NEW = r'''# ---------------- link 1b (HPP-379, item 295): the W form rows (b)(1)-(4), the window kinds and the nearest window line, the
# alignment of the video continuity
RE34 = BASE / 'E34'
LV2 = 'small_pot_lava'


def w34(name, lines, std=(), js=None):
    return S.entry_of('w145_02', mk145(BASE / name, 'w145_02', lines=lines, std=std, js=js), SH5)


def row34(e, k):
    x = [a for a in e['admit'] if a[0].startswith('W 295(b)(%d)' % k)]
    return (x[0][1], x[0][2]) if len(x) == 1 else None


def ins_after(lines, n, text):
    i = [k for k, x in enumerate(lines) if x.startswith('FrameTrace: n=%d ' % n)][0]
    return lines[:i + 1] + [text] + lines[i + 1:]


l34 = [VF, VW] + scene_lines(LV2, [150000] * 100 + [100000] * 100)
e = w34('E34a', ins_after(l34, 114, VW))
ok &= case('E34 (b)(3): the LAST validation-layer line (an earlier one before the entry line aside) followed by rows of exactly '
           '10 000 000 us to the hold end -> PASS (the edge of 10 s); (b)(1), (b)(2) pass',
           row34(e, 3) == (True, '10000000 us') and row34(e, 1) == (True, '0') and row34(e, 2) == (True, '2') and adm_ok(e))
l34b = [VF] + scene_lines(LV2, [150000] * 100 + [100000] * 99 + [100001])
e = w34('E34b', ins_after(l34b, 114, VW))
ok &= case('E34b (b)(3): 1 us more (10 000 001 us) -> FAIL, the only failing row', row34(e, 3) == (False, '10000001 us') and
           [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(3)'])
e = w34('E34c', [VF, '[Vulkan][W][1]: Removing layer X because it is a duplicate', '[Vulkan][W][3]: y', '[Vulkan][I][2]: z',
                 '[Vulkan][W][12]: q'] + scene_lines(LV2, [150000] * 50))
ok &= case('E34c (b)(2): only loader [W][1], [W][3], [I][2] and [W][12] lines -> (b)(2) FAIL with 0, (b)(3) FAIL with none; '
           'the old row "validation active" still passes on the loader line', row34(e, 2) == (False, '0') and
           row34(e, 3) == (False, 'none') and [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(2)', 'W 295(b)(3)']
           and e['val']['ok'] is True)
e = w34('E34d', [VF] + scene_lines(LV2, [150000] * 50) + ['[Vulkan][E][2]: vkCmdDraw(): an error'])
ok &= case('E34d (b)(2)-(3): one [Vulkan][E][2] line after the last row -> both pass (1; 0 us)', row34(e, 2) == (True, '1')
           and row34(e, 3) == (True, '0 us'))
e = w34('E34e', [VF] + scene_lines(LV2, [150000] * 50), std=['[Vulkan][W][2]: in the stdout only'])
ok &= case('E34e a validation-layer line in the emulator stdout only: (b)(2) PASS (log and stdout), (b)(3) FAIL (the log has '
           'none)', row34(e, 2) == (True, '1') and row34(e, 3) == (False, 'none'))
e = w34('E34f', [VF] + scene_lines(LV2, [150000] * 50) + [VW], std=[LIM])
e2 = w34('E34g', [VF] + scene_lines(LV2, [150000] * 50) + [VW, LIM])
ok &= case('E34f (b)(1): a limit line in the stdout or in the log -> FAIL with 1, the only failing row',
           row34(e, 1) == (False, '1') and row34(e2, 1) == (False, '1') and
           [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(1)'] and
           [a[0][:11] for a in e2['admit'] if not a[1]] == ['W 295(b)(1)'])
l35 = [VF, '[Vulkan][W][2]: early, before the entry line'] + scene_lines(LV2, [150000] * 80)
e = w34('E35', l35)
ok &= case('E35 (b)(3): the only layer line before the entry line -> the whole hold after it (12 000 000 us + the first frame '
           'and the loading rows) -> FAIL', row34(e, 3)[0] is False and int(row34(e, 3)[1].split()[0]) > 10000000)
l35b = [VF] + scene_lines(LV2, [150000] * 80) + [start('another_level'), VW, ft(200, 150000)]
e = w34('E35b', l35b)
ok &= case('E35b (b)(3): the layer line after a scene change -> the rows after the change are not the hold -> 0 us, PASS',
           row34(e, 3) == (True, '0 us'))
for i, (name, lines, js, why) in enumerate((
        ('a death marker with a [Vulkan][E] report (VALIDATION_STOP)', [VF] + scene_lines(LV2, [150000] * 20) + [
            '--- Error ---', '[Vulkan][E][2]: vkCreateGraphicsPipelines(): bad', LIM], None, 'death marker --- Error ---'),
        ('the attempt outcome timeout', [VF, 'x'], js145('w145_02', attempt=dict(outcome='timeout')),
         'attempt outcome timeout'),
        ('hold_exit set', [VF] + scene_lines(LV2, [150000] * 20), js145('w145_02', attempt=dict(hold_exit=12.0)),
         'hold_exit / ENDED / exited'),
        ('the attempt outcome exited', [VF] + scene_lines(LV2, [150000] * 20), js145('w145_02', attempt=dict(
            outcome='exited')), 'hold_exit / ENDED / exited'))):
    e = w34('E36_%d' % i, lines, js=js)
    ok &= case('E36 a W not held (%s): the rows (1)-(3) print n/a and pass, (b)(4) is still read; the print says NOT held' % name,
               all(row34(e, k) == (True, 'n/a (W not held: %s)' % why) for k in (1, 2, 3)) and row34(e, 4)[0] is True and
               e['held'] == (False, why) and any(x.startswith('  W form of item 295 (b): NOT held (%s) - rows (1)-(3) n/a;' % why)
                                                 for x in S.fmt_entry(e)))
pd = mk145(BASE / 'E36d', 'w145_02')
os.remove(pd + '/log_w145_02.txt')
e = S.entry_of('w145_02', pd, SH5)
ok &= case('E36d a W without its log -> not held (log missing), rows (1)-(3) n/a', e['held'] == (False, 'log missing') and
           row34(e, 3) == (True, 'n/a (W not held: log missing)'))
e = w34('E36e', [VF, VW, 'x'])
e2 = w34('E36f', [VF, start(LV2), VW])
ok &= case('E36e (b)(3) on a held W without the entry line, and with the entry line but no hold row -> FAIL with none',
           row34(e, 3) == (False, 'none') and row34(e2, 3) == (False, 'none') and e['held'][0] and e2['held'][0])
e = w34('E36b', [VF, 'x'], js=js145('w145_02', attempt=dict(outcome='timeout'), filt=FILT))
ok &= case('E36b a W not held with the filter in its env -> the row (b)(4) FAIL', row34(e, 4) == (
    False, 'W form: limit=100000000 filter=%s' % FILT))
ok &= case('E36c w_form4: the form line from the env; the key present with the value "none" or "" fails',
           S.w_form4({'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000'}) == (True, 'W form: limit=100000000 filter=none') and
           S.w_form4({'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000', 'VK_LAYER_MESSAGE_ID_FILTER': 'none'}) == (
               False, 'W form: limit=100000000 filter=none') and
           S.w_form4({'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000', 'VK_LAYER_MESSAGE_ID_FILTER': ''}) == (
               False, 'W form: limit=100000000 filter=') and S.w_form4({}) == (False, 'W form: limit=None filter=none'))
KINDS = ['Window 1 shown', 'Window 1 hidden', 'Window 1 exposed', 'Window 1 moved to 10,10', 'Window 1 resized to 1280x720',
         'Window 1 size changed to 1280x720', 'Window 1 minimized', 'Window 1 maximized', 'Window 1 restored',
         'Window 1 gained keyboard focus', 'Window 1 lost keyboard focus', 'Window 1 closed', 'Window 1 got unknown event 7',
         'Mouse entered window 1', 'Mouse left window 12']
e = w34('E37', wl(LV2) + KINDS[:8] + ['Mouse entered window', 'Window x closed', 'window 1 shown', 'Window 1 shownX'],
        std=KINDS[8:] + KINDS[:1])
ok &= case('E37 the 15 window kinds of window.cpp are counted in the log and the stdout (shown twice); "Mouse entered window" '
           'without an id, "Window x", lower case and "shownX" are not',
           e['winall'] == dict((k, 2 if k == 'shown' else 1) for k in S.WIN_ALL) and
           any(x == '  window lines by kind (item 295 (g); log and stdout; data): shown 2, hidden 1, exposed 1, moved to 1, '
               'resized 1, size changed 1, minimized 1, maximized 1, restored 1, gained keyboard focus 1, lost keyboard focus '
               '1, closed 1, got unknown event 1, Mouse entered window 1, Mouse left window 1' for x in S.fmt_entry(e)))
CH6 = S.CHUNK
S.CHUNK = 41
sc37 = S.scan(str(BASE / 'E37' / 'log_w145_02.txt'))
S.CHUNK = CH6
ok &= case('E37b the window kinds and their positions across 41-byte chunks: 8 lines once each',
           sum(sc37['winall'].values()) == 8 and len(sc37['winpos']) == 8 and
           [k for k, _ in sc37['winpos']] == list(S.WIN_ALL[:8]))
post38 = [16667] * 10 + [150000] + [50000] * 40 + [16667] * 200 + [150000] + [50000] * 39 + [50001] + [16667] * 320 + \
         [1500000] + [16667] * 500 + [1200000] + [16667] * 10
l38 = [PRE] + scene_lines(LV2, post38)
l38 = ins_after(l38, 65, 'Mouse entered window 1')
l38 = ins_after(l38, 306, 'Window 1 moved to 5,5')
l38 = ins_after(l38, 626, 'Window 1 lost keyboard focus')
e38 = S.entry_of('v145_02', mk145(BASE / 'E38', 'v145_02', lines=l38, std=['Window 1 hidden']), SH5)
ok &= case('E38 the nearest window line of each K2 / K3 frame: a line exactly 2 s after a K3 frame -> found (+2.000 s); a line '
           '2.000001 s after the next one -> none; a line right before a K2 frame -> 0 s; a K2 frame with only a stdout line '
           '-> none; entry / hold by the 599 rows of the window',
           e38['winnear'] == [(25, 150000, 'K3', 'entry', ('Mouse entered window', 2000000)), (266, 150000, 'K3', 'entry', None),
                              (627, 1500000, 'K2', 'hold', ('lost keyboard focus', 0)), (1128, 1200000, 'K2', 'hold', None)]
           and e38['winall']['hidden'] == 1 and
           any(x == '  window line nearest each K2 / K3 frame after the first scene frame (item 295 (g); +-2 s of presented time '
               'by byte position in the log; data): K2 2 frames, K3 2 frames; with a window line within 2 s: n 25 K3 entry dt '
               '150000 -> Mouse entered window +2.000 s; n 627 K2 hold dt 1500000 -> lost keyboard focus +0.000 s; K2 without '
               'one: n 1128 K2 hold dt 1200000 -> none; K3 without one (none): 1' for x in S.fmt_entry(e38)))
l38b = ins_after(scene_lines(LV2, [16667] * 10 + [1500000] + [400000] * 4 + [16667] * 200 + [100000] + [16667] * 200 +
                             [1000000] + [16667] * 182 + [150000] + [16667] * 5), 26, 'Window 1 exposed')
l38b = [PRE] + ins_after(l38b, 24, 'Window 1 shown')
e38b = S.entry_of('v145_02', mk145(BASE / 'E38b', 'v145_02', lines=l38b), SH5)
ok &= case('E38b a line at the end of the row before a frame is at 0 for that frame; a line at the end of a frame is at 0 for it '
           'and for the next; a line before a frame is negative; the nearest wins (a line 1.9 s before loses to one at 0.4 s)',
           e38b['winnear'] == [
               (25, 1500000, 'K2', 'entry', ('shown', 0)), (26, 400000, 'K3', 'entry', ('exposed', 0)),
               (27, 400000, 'K3', 'entry', ('exposed', 0)), (28, 400000, 'K3', 'entry', ('exposed', -400000)),
               (29, 400000, 'K3', 'entry', ('exposed', -800000)), (230, 100000, 'K3', 'entry', None),
               (431, 1000000, 'K2', 'entry', None), (614, 150000, 'K3', 'hold', None)])
e38d = S.entry_of('v145_02', mk145(BASE / 'E38d', 'v145_02', lines=[PRE] + scene_lines(LV2, [16667] * 10) + [
    start('another_level'), ft(100, 1500000)]), SH5)
ok &= case('E38d a K2 frame after a scene change is not a frame of the hold: no K2 / K3 frame', e38d['winnear'] == [])
XS38 = S.XSRC
S.XSRC = {'v144_09': dict(root=(BASE / 'E38' / 'none').as_posix(), chain='go144a', pred='none.md')}
o38 = S.summary(str(BASE / 'E38'), SH5, None)[0]
S.XSRC = XS38
ok &= case('E38c the summary names the K2 / K3 frames with a window line within 2 s and the tags by kind',
           'WINDOW LINE NEAR A K2 / K3 FRAME (item 295 (g); within 2 s; data): v145_02 n 25 K3 entry -> Mouse entered window '
           '+2.000 s; v145_02 n 627 K2 hold -> lost keyboard focus +0.000 s' in o38 and
           'WINDOW LINES BY KIND (item 295 (g); log and stdout; data): v145_02: hidden 1, moved to 1, lost keyboard focus 1, '
           'Mouse entered window 1' in o38)
rq = rows_at([0.1 * i for i in range(21)])
iq = sorted([0.1 * i - 0.0105 for i in range(20) if i not in (5, 6, 7)] + [2.0])
q = S.vquality(rq, iq, 2)
ok &= case('E39 vquality: records 10.5 ms before the row ends except the anchor; rows 5..7 without a record: within 8 ms 1 of 21 '
           'at shift 0, the best shift -3 ms (18 rows; a plateau -8..-3 ms, the smaller |shift|), the continuity count 3 at '
           'both, no mark; the 600 rows after the first scene frame are 19 (from it on: 20)',
           q == dict(rows=21, near=1, n600=19, near600=1, n600f=20, near600f=1, shift=-3, near_best=18, after0=3,
                     after_best=3, mark=False))
ok &= case('E39b the print of the alignment', S.fmt_vq(q) == 'rows with a .idx record within 8 ms: 1 of 21 (4.8 %); in the 19 '
           'rows after the first scene frame 1 (5.3 %) [from the first scene frame on: 1 of 20]; best shift of the anchor in '
           '+-50 ms -3 ms (18 rows within 8 ms); rows without a record after the first scene frame: 3 at shift 0, 3 at the best '
           'shift' and S.fmt_vq(None).startswith('n/a'))
iq2 = [0.1 * i - 0.0105 for i in range(20)] + [2.0]
q2 = S.vquality(rq, iq2, 2)
iq3 = [0.1 * i + 0.0105 for i in range(20)] + [2.0]
q3 = S.vquality(rq, iq3, 2)
ok &= case('E39c the best shift: -3 ms for records 10.5 ms early, +3 ms for records 10.5 ms late (symmetric); 21 of 21 within '
           '8 ms there', q2['shift'] == -3 and q2['near_best'] == 21 and q3['shift'] == 3 and q3['near_best'] == 21)
iq4 = [0.1 * i for i in range(21)]
q4 = S.vquality(rq, iq4, 2)
ok &= case('E39d exact records: shift 0 (a plateau -8..+8 ms, the smaller |shift| wins), all rows within 8 ms; 19 of the 19 '
           'rows after the first scene frame, 20 of 20 from it on',
           q4['shift'] == 0 and q4['near'] == 21 and q4['near_best'] == 21 and q4['n600'] == 19 and q4['near600'] == 19 and
           q4['n600f'] == 20 and q4['near600f'] == 20)
ok &= case('E39f near_count: exactly 8 ms is within, 8.1 ms is not; the record before and the record after are both looked at; '
           'beyond the last record or before the first',
           S.near_count([0.0], [0.008]) == 1 and S.near_count([0.0], [0.0081]) == 0 and
           S.near_count([1.0], [0.995, 1.5]) == 1 and S.near_count([1.0], [0.5, 1.004]) == 1 and
           S.near_count([3.0], [1.0, 2.0]) == 0 and S.near_count([0.0], [1.0]) == 0 and
           S.near_count([1.0, 1.5, 2.0], [1.0, 2.0]) == 2)
iq5 = [0.1 * i - 0.0105 if i % 2 == 0 else 0.1 * i + 0.0105 for i in range(20)] + [2.0]
q5 = S.vquality(rq, iq5, 2)
ok &= case('E39g a tie between -3 and +3 ms (records of even rows early, of odd rows late; 11 rows each) -> the negative shift',
           q5['shift'] == -3 and q5['near_best'] == 11)
iq6 = [0.1 * i - 0.0125 for i in range(20)] + [2.0]
q6 = S.vquality(rq, iq6, 2)
ok &= case('E39h records 12.5 ms early: at shift 0 every row ends 12.5 ms inside a gap of 100 ms (18 rows after the first scene '
           'frame), at the best shift -5 ms (21 rows within 8 ms) 7.5 ms inside the margin (0 rows) -> mark [I] and printed',
           q6 == dict(rows=21, near=1, n600=19, near600=1, n600f=20, near600f=1, shift=-5, near_best=21, after0=18,
                      after_best=0, mark=True) and S.fmt_vq(q6).endswith(
               'rows without a record after the first scene frame: 18 at shift 0, 0 at the best shift - [I] the counts differ '
               'by more than 10 %'))
ok &= case('E39e vquality None without rows, records, a first scene frame or its row',
           S.vquality([], iq, 2) is None and S.vquality(rq, [], 2) is None and S.vquality(rq, iq, None) is None and
           S.vquality(rq, iq, 99) is None)
VC_REAL = S.vcont
for a0, ab, mk in ((10, 11, False), (10, 12, True), (10, 9, False), (10, 8, True), (0, 0, False), (0, 1, True)):
    seq = iter([a0, ab])
    S.vcont = lambda *a, **k: dict(after=next(seq))
    qm = S.vquality(rq, iq, 2)
    S.vcont = VC_REAL
    ok &= case('E40 the mark of item 295 (d): %d at shift 0, %d at the best shift -> mark %s (more than 10 %% of the first; 0 '
               'against > 0)' % (a0, ab, mk), qm['mark'] is mk and qm['after0'] == a0 and qm['after_best'] == ab)
rr40 = rows_at([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
ok &= case('E40b vcont with a shift moves every row end after the anchoring: 0 -> 2 rows (n 4, 5); -0.05 s -> 4 (n 4, 5, 6 in '
           'the long gap, n 7 in the last); +0.25 s -> 1 (n 4 in the last gap; n 1..3 in the long gap are before the first '
           'scene frame)',
           S.vcont(rr40, [0.0, 0.1, 0.2, 0.5, 0.6], 3, 0.0)['after'] == 2 and
           S.vcont(rr40, [0.0, 0.1, 0.2, 0.5, 0.6], 3, -0.05)['after'] == 4 and
           S.vcont(rr40, [0.0, 0.1, 0.2, 0.5, 0.6], 3, 0.25)['after'] == 1)
e41 = S.entry_of('v145_02', str(R22), SH5)
ok &= case('E41 a V with a .idx prints the alignment line next to the continuity line (the record lacking three frames: the '
           'count 3 at shift 0); a V without K2 / K3 frames prints so', e41['vq'] is not None and e41['vq']['after0'] == 3 and
           any(x.startswith('  video continuity alignment (item 295 (d); data, not a gate): rows with a .idx record within '
                            '8 ms: ') for x in S.fmt_entry(e41)) and
           '  window line nearest each K2 / K3 frame after the first scene frame (item 295 (g); +-2 s of presented time by '
           'byte position in the log; data): no K2 / K3 frame after the first scene frame' in S.fmt_entry(e41))
'''
rep('''try:
    ('\\n'.join(o14 + o18 + o23 + o24 + o24f + fE10 + l4 + l4b + l4d + r16[1].split('\\n') + r25[1].split('\\n') +
               S.fmt_entry(e22))).encode('cp1250', errors='strict')
''', NEW + '''try:
    ('\\n'.join(o14 + o18 + o23 + o24 + o24f + fE10 + l4 + l4b + l4d + r16[1].split('\\n') + r25[1].split('\\n') +
               S.fmt_entry(e22) + o24h + o38 + S.fmt_entry(e38) + S.fmt_entry(e41))).encode('cp1250', errors='strict')
''')
rep('''           not any(s in x for x in out4 for s in ('WINDOW EVENT', 'LAYER LIMIT', 'W FILTER', 'VIDEO CONTINUITY', 'window events',
                                                 'layer limit', 'cold first entry', 'COLD first', 'video continuity',
                                                 'message filter', 'item 273')) and
''', '''           not any(s in x for x in out4 for s in ('WINDOW EVENT', 'LAYER LIMIT', 'W FILTER', 'VIDEO CONTINUITY', 'window events',
                                                 'layer limit', 'cold first entry', 'COLD first', 'video continuity',
                                                 'message filter', 'item 273', 'W FORM 295', 'WINDOW LINE', 'window line',
                                                 'item 295', 'W 295')) and
''')
open(P, 'wb').write(src.encode('ascii'))
print('edits %d; test_sc145.py sha256 %s' % (N[0], hashlib.sha256(src.encode('ascii')).hexdigest()))
