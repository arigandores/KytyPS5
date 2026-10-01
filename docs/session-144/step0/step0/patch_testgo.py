p = 'C:/kyty/s144/test_go144a.py'
t = open(p, 'rb').read().decode('ascii').replace('\r\n', '\n')
R = [
(r"""ok &= case('g1 an unknown tag (and a tag of session 142) -> rc 2 usage', call(r, 'x144')[0] == 2 and
           call(r, 'x144')[1].startswith('usage') and call(r, 'v142')[0] == 2 and call(r, 'v144_11')[0] == 2)""",
r"""ok &= case('g1 an unknown tag (a tag of session 142 or 143, a V of the eight W-only levels, a tag past 20) -> rc 2 usage',
           call(r, 'x144')[0] == 2 and call(r, 'x144')[1].startswith('usage') and call(r, 'v142')[0] == 2 and
           call(r, 'v143_01')[0] == 2 and call(r, 'v144_08')[0] == 2 and call(r, 'v144_00')[0] == 2 and
           call(r, 'w144_21')[0] == 2)"""),
(r"""'after w144_01.json -> rc 0; w144_03 before w144_09 -> rc 1; w144_09 before w144_02 -> rc 1',""",
 r"""'after w144_01.json -> rc 0; w144_03 before w144_02 -> rc 1; w144_09 before v144_09 -> rc 1',"""),
(r"""ok &= case('g8 DRY rc 0 for every one of the 20 tags once its previous call is made', len(plans) == 20 and""",
 r"""ok &= case('g8 DRY rc 0 for every one of the 33 tags once its previous call is made', len(plans) == 33 and"""),
(r"""ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal 02_sc144, no""",
 r"""ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal 01_sc144, no"""),
(r"""          and 'vulkan-validation' not in plans[v][1] and 'VK_LAYER_PATH' not in plans[v][1]) for v, _, lv in S.PAIRS)
ok &= case('g10 every V: its level of item 231 (i)(1), video, hold 330, stable-draws 300, timeout 480, no validation', vv)""",
r"""          and 'vulkan-validation' not in plans[v][1] and 'VK_LAYER_PATH' not in plans[v][1]
          and 'KYTY_PIPELINE_PRECACHE' not in plans[v][1]) for v, lv in S.CENSUS)
ok &= case('g10 every V (the 12 of the census): its level of item 254 (k)(1), video, hold 330, stable-draws 300, timeout 480, '
           'no validation, no KYTY_PIPELINE_PRECACHE (shipped defaults)', vv and len(S.CENSUS) == 12)"""),
(r"""          and '--stable-draws 300 --timeout 600' in plans[w][1]) for _, w, lv in S.PAIRS)
ok &= case('g11 every W: the level of its V, validation true with the layer path and the duplicate limit, hold 310, '
           'stable-draws 300, timeout 600, no video', ww)""",
r"""          and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000 KYTY_PIPELINE_PRECACHE=0 KYTY_GPU_CLOCK_PIN=1' in plans[w][1]
          and '--stable-draws 300 --timeout 600' in plans[w][1]) for w, lv in [(x, S.level_of(x)) for x in S.W_TAGS])
ok &= case('g11 every W (the control and the 20 of the pairs): its level, validation true with the layer path and the duplicate '
           'limit, the form KYTY_PIPELINE_PRECACHE=0 of item 254 (e) positional before the clock pin, hold 310, stable-draws 300, '
           'timeout 600, no video', ww and len(S.W_TAGS) == 21)"""),
(r"""ok &= case('g13 SEQ of the chain = sc144.SEQ (V then W per level, item 231 (i)(1) order)', m is not None and""",
 r"""ok &= case('g13 SEQ of the chain = sc144.SEQ (the control W, eight W, then V then W per level, item 254 (k)(1))', m is not None and"""),
(r"""lv = re.findall(r'\n  (v144_\d\d)\|(w144_\d\d)\) LEVEL=(\w+);;', TEXT)
ok &= case('g14 the chain tag -> level map = sc144.PAIRS (ten pairs)', tuple(lv) == S.PAIRS)""",
r"""lv = re.findall(r'\n  (v144_\d\d)\|(w144_\d\d)\) LEVEL=(\w+);;', TEXT)
lw = re.findall(r'\n  (w144_\d\d)\) LEVEL=(\w+);;', TEXT)
ok &= case('g14 the chain tag -> level map: the control W and eight W-only tags = sc144 (CONTROL, the W of the eight v143 pairs), '
           'the twelve V/W pairs = sc144.PAIRS[8:]',
           tuple(lv) == S.PAIRS[8:] and tuple(lw) == ((S.CONTROL[0], S.CONTROL[1]),) + tuple((w, x) for _, w, x in S.PAIRS[:8]))"""),
(r"""ok &= case('g29 the levels of the chain are exactly sc144.LEVELS', [x[2] for x in lv] == list(S.LEVELS))""",
 r"""ok &= case('g29 the levels of the chain are exactly sc144.LEVELS after the control level',
           [x[1] for x in lw] + [x[2] for x in lv] == [S.SKY] + list(S.LEVELS))"""),
]
for a, b in R:
    assert t.count(a) == 1, a[:80]
    t = t.replace(a, b)
open(p, 'wb').write(t.encode('ascii'))
print('ok', len(R))
