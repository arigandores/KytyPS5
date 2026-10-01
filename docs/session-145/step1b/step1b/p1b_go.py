"""Link 1b of s145 (HPP-379; ROADMAP s122 item 295 (b)): exact edits of go145a.sh, test_go145a.py and step2/call_one.sh.
ASCII only.  python p1b_go.py"""
import hashlib
import sys

N = [0]


def edit(path, pairs):
    src = open(path, 'rb').read().decode('utf-8')
    assert '\r' not in src
    for old, new in pairs:
        c = src.count(old)
        if c != 1:
            print('ANCHOR COUNT %d in %s: %r' % (c, path, old[:120]))
            sys.exit(1)
        src = src.replace(old, new)
        N[0] += 1
    open(path, 'wb').write(src.encode('ascii'))
    print('%s sha256 %s' % (path, hashlib.sha256(src.encode('ascii')).hexdigest()))


edit('C:/kyty/s145/go145a.sh', [
    ('''# cache count and manifests, foreign-CPU row, winpid lock line - with the 34 tags of item 273 (k)(1), the W form of item
# 273 (k)(2) (validation, KYTY_PIPELINE_PRECACHE=0 and the filter of ONE message) and the stop rules of item 273 (k)(4).
''', '''# cache count and manifests, foreign-CPU row, winpid lock line - with the 34 tags of item 273 (k)(1), the W form of item
# 273 (k)(2) as changed by item 295 (b) (link 1b HPP-379: validation, KYTY_PIPELINE_PRECACHE=0, the duplicate limit
# 100000000 and NO message filter) and the stop rules of item 273 (k)(4) with the W form member of item 295 (v).
'''),
    ('''#   W (item 254 (e), 273 (k)(2)): --vulkan-validation true with VK_LAYER_PATH and VK_LAYER_DUPLICATE_MESSAGE_LIMIT,
#     KYTY_PIPELINE_PRECACHE=0 AND VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER (the VUID string of the F6 warning, the one message
#     on which 13 W of s144 reached the duplicate limit; no other id) - positional, so enter_scene.py puts them into the env
#     and the json; no video, hold WHOLD=310 s, --stable-draws 300 --timeout 600, --attempts 1.
''', '''#   W (item 254 (e), 273 (k)(2), 295 (b)): --vulkan-validation true with VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=
#     $VKDUP (100000000: above the F6 lines of a hold, so the layer reports to the end of the hold - the positive control of
#     item 295 (b)(3)) and KYTY_PIPELINE_PRECACHE=0; NO VK_LAYER_MESSAGE_ID_FILTER (removed by item 295 (b)) - positional, so
#     enter_scene.py puts them into the env and the json (sc145.py reads the form line "W form: limit=100000000
#     filter=none" from it, item 295 (b)(4)); no video, hold WHOLD=310 s, --stable-draws 300 --timeout 600, --attempts 1.
'''),
    ('''VKDUP="1000000"
VKFILTER="Undefined-Value-ShaderOutputNotConsumed-DynamicRendering"
PRED="pred/02_sc145.md"
''', '''VKDUP="100000000"
PRED="pred/03_sc145.md"
'''),
    ('''          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0 VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER";;
''', '''          EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0";;
'''),
])

edit('C:/kyty/s145/step2/call_one.sh', [('(pred/02_sc145.md)', '(pred/03_sc145.md)')])

edit('C:/kyty/s145/test_go145a.py', [
    ('''W, the W repeat w145_01, then V then W per level), the W form with the filter of one message of item 273 (k)(2), the levels
of the control W, of the W repeat and of the pairs, the bad tags and the step 2 wrappers with the gate are the cases changed
or added - g1, g6, g8, g10, g11, g14, g38, g46-g50).
''', '''W, the W repeat w145_01, then V then W per level), the W form of item 273 (k)(2), the levels of the control W, of the W
repeat and of the pairs, the bad tags and the step 2 wrappers with the gate are the cases changed or added - g1, g6, g8,
g10, g11, g14, g38, g46-g50).  Link 1b (HPP-379, item 295 (b)): the W form without the message filter and with the
duplicate limit 100000000, the seal pred/03_sc145.md - g9, g11, g25, g46, g47 changed.
'''),
    ("    (root / 'pred' / '02_sc145.md').write_text(", "    (root / 'pred' / '03_sc145.md').write_text("),
    ("and '--pred %s/pred/02_sc145.md' % rp in o", "and '--pred %s/pred/03_sc145.md' % rp in o"),
    ("the empty gate file, the seal 02_sc145, no checkpoints/schedule, '", "the empty gate file, the seal 03_sc145, no checkpoints/schedule, '"),
    ('''          and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000' in plans[w][1]
          and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000 KYTY_PIPELINE_PRECACHE=0 VK_LAYER_MESSAGE_ID_FILTER='
              'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering KYTY_GPU_CLOCK_PIN=1' in plans[w][1]
''', '''          and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_PIPELINE_PRECACHE=0 '
              'KYTY_GPU_CLOCK_PIN=1' in plans[w][1] and 'VK_LAYER_MESSAGE_ID_FILTER' not in plans[w][1]
'''),
    ('''ok &= case('g11 every W (the control, the W repeat and the 16 of the pairs): its level, validation true with the layer path '
           'and the duplicate limit, the form KYTY_PIPELINE_PRECACHE=0 and the one message filter of item 273 (k)(2) positional '
           'before the clock pin, hold 310, stable-draws 300, timeout 600, no video', ww and len(S.W_TAGS) == 18)
''', '''ok &= case('g11 every W (the control, the W repeat and the 16 of the pairs): its level, validation true with the layer path '
           'and the duplicate limit 100000000, the form KYTY_PIPELINE_PRECACHE=0 positional before the clock pin, no message '
           'filter (item 295 (b)), hold 310, stable-draws 300, timeout 600, no video', ww and len(S.W_TAGS) == 18)
'''),
    ('''ok &= case('g25 the chain reads the seal pred/02_sc145.md and the scorer sc145.py', 'PRED="pred/02_sc145.md"' in TEXT
''', '''ok &= case('g25 the chain reads the seal pred/03_sc145.md and the scorer sc145.py', 'PRED="pred/03_sc145.md"' in TEXT
'''),
    ('''VKF = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
CODE = '\\n'.join(x for x in TEXT.split('\\n') if not x.lstrip().startswith('#'))
ok &= case('g46 the filter of item 273 (k)(2): one constant VKFILTER = the VUID string of sc145.VKFILTER, used once, in the W '
           'EXTRA only; no other VK_LAYER_MESSAGE_ID_FILTER in the code lines (comments aside); no V plan carries it, every W '
           'plan exactly once',
           'VKFILTER="%s"\\n' % VKF in CODE and S.VKFILTER == VKF and CODE.count('$VKFILTER') == 1 and
           CODE.count('VK_LAYER_MESSAGE_ID_FILTER=') == 1 and 'VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER";;\\n' in CODE and
           all(o.count('VK_LAYER_MESSAGE_ID_FILTER=%s ' % VKF) == 1 for t, (_, o) in plans.items() if t in S.W_TAGS) and
           not any('VK_LAYER_MESSAGE_ID_FILTER' in o for t, (_, o) in plans.items() if t not in S.W_TAGS))
ok &= case('g47 the W EXTRA case is the w145_* branch, the V branch has no EXTRA (shipped defaults)',
           0 < CODE.find('  w145_*) SD=') < CODE.find('VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER') and
''', '''CODE = '\\n'.join(x for x in TEXT.split('\\n') if not x.lstrip().startswith('#'))
ok &= case('g46 the W form of item 295 (b): one constant VKDUP="100000000" used once, in the W EXTRA; no VKFILTER and no '
           'VK_LAYER_MESSAGE_ID_FILTER in the code lines (comments aside); no plan carries the filter; the scorer reads the '
           'form line "W form: limit=100000000 filter=none"',
           'VKDUP="100000000"\\n' in CODE and CODE.count('$VKDUP') == 1 and 'VKFILTER' not in CODE and
           'VK_LAYER_MESSAGE_ID_FILTER' not in CODE and
           'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0";;\\n' in CODE and
           not any('VK_LAYER_MESSAGE_ID_FILTER' in o for t, (_, o) in plans.items()) and
           all(o.count('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 ') == 1 for t, (_, o) in plans.items() if t in S.W_TAGS)
           and S.W_FORM_LINE == 'W form: limit=100000000 filter=none')
ok &= case('g47 the W EXTRA case is the w145_* branch, the V branch has no EXTRA (shipped defaults)',
           0 < CODE.find('  w145_*) SD=') < CODE.find('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP') and
'''),
])
print('edits %d' % N[0])
