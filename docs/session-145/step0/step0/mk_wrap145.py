"""Session 145 step 0 (HPP-350): build test_go145a.py and the step 2 wrappers (next_one.sh, pre_one.sh, call_one.sh,
wait_one.sh, apichk145.py) from their s144 files: the name move 144 -> 145, then exact replacements of the cases and lines
that depend on the 34 tags of item 273 (k)(1) and the W form of item 273 (k)(2).  ASCII only, LF."""
import sys

S4 = 'C:/kyty/s144/'
S5 = 'C:/kyty/s145/'


def load(p):
    t = open(p, 'rb').read().decode('ascii')
    assert '\r' not in t
    return t


def apply(t, R, name):
    for old, new in R:
        n = t.count(old)
        if n != 1:
            print('%s ANCHOR COUNT %d: %r' % (name, n, old[:100]))
            sys.exit(1)
        t = t.replace(old, new)
    t.encode('ascii')
    return t


# ---------------- test_go145a.py
t = load(S4 + 'test_go144a.py').replace('144', '145')
R = []
R.append(('''"""Fixtures of the chain go145a.sh (session 145 step 0, HPP-330; ROADMAP s122 item 254 (e), (k)(1)-(4), item 105 (v), general
rule 26, item 231 (z)(5)).  Port of C:/kyty/s143/test_go143a.py (names moved 143 -> 145; the order, the 33 tags, the W form''',
          '''"""Fixtures of the chain go145a.sh (session 145 step 0, HPP-350; ROADMAP s122 item 273 (k)(1)-(4), item 105 (v), general
rule 26, item 231 (z)(5)).  Port of C:/kyty/s144/test_go144a.py (names moved 144 -> 145; the order of the 34 tags (the control
W, the W repeat w145_01, then V then W per level), the W form with the filter of one message of item 273 (k)(2), the levels
of the control W, of the W repeat and of the pairs, the bad tags and the step 2 wrappers with the gate are the cases changed
or added - g1, g6, g8, g10, g11, g14, g38, g46-g50).
Session 144 text (carried): port of C:/kyty/s143/test_go143a.py (names moved 143 -> 144; the order, the 33 tags, the W form'''))
R.append(('''ok &= case('g1 an unknown tag (a tag of session 142 or 143, a V of the eight W-only levels, a tag past 20) -> rc 2 usage',
           call(r, 'x145')[0] == 2 and call(r, 'x145')[1].startswith('usage') and call(r, 'v142')[0] == 2 and
           call(r, 'v143_01')[0] == 2 and call(r, 'v145_08')[0] == 2 and call(r, 'v145_00')[0] == 2 and
           call(r, 'w145_21')[0] == 2)''',
          '''ok &= case('g1 an unknown tag (a tag of session 142, 143 or 144 - the V v144_09 of the pair is no chain tag -, a V of the '
           'control or of the W repeat, a tag past 17) -> rc 2 usage',
           call(r, 'x145')[0] == 2 and call(r, 'x145')[1].startswith('usage') and call(r, 'v142')[0] == 2 and
           call(r, 'v143_01')[0] == 2 and call(r, 'v144_09')[0] == 2 and call(r, 'w144_00')[0] == 2 and
           call(r, 'v145_00')[0] == 2 and call(r, 'v145_01')[0] == 2 and call(r, 'w145_18')[0] == 2 and
           call(r, 'v145_18')[0] == 2)'''))
R.append(('''rc, out = call(r, 'w145_01', DRY='1')
(r / 'attempt_w145_00.txt').write_text('made\\n')
rc2, out2 = call(r, 'w145_01', DRY='1')
rc3, out3 = call(r, 'w145_02', DRY='1')
(r / 'w145_01.json').write_text('{}')
rc4, out4 = call(r, 'w145_02', DRY='1')
rc5, out5 = call(r, 'w145_03', DRY='1')
rc6, out6 = call(r, 'w145_09', DRY='1')
ok &= case('g6 order: w145_01 before w145_00 -> rc 1; after the w145_00 marker -> DRY rc 0; w145_02 before w145_01 -> rc 1, '
           'after w145_01.json -> rc 0; w145_03 before w145_02 -> rc 1; w145_09 before v145_09 -> rc 1',''',
          '''rc, out = call(r, 'w145_01', DRY='1')
(r / 'attempt_w145_00.txt').write_text('made\\n')
rc2, out2 = call(r, 'w145_01', DRY='1')
rc3, out3 = call(r, 'v145_02', DRY='1')
(r / 'w145_01.json').write_text('{}')
rc4, out4 = call(r, 'v145_02', DRY='1')
rc5, out5 = call(r, 'w145_02', DRY='1')
rc6, out6 = call(r, 'v145_03', DRY='1')
ok &= case('g6 order: w145_01 before w145_00 -> rc 1; after the w145_00 marker -> DRY rc 0; v145_02 before w145_01 -> rc 1, '
           'after w145_01.json -> rc 0; w145_02 before v145_02 -> rc 1; v145_03 before w145_02 -> rc 1','''))
R.append(("ok &= case('g8 DRY rc 0 for every one of the 33 tags once its previous call is made', len(plans) == 33 and",
          "ok &= case('g8 DRY rc 0 for every one of the 34 tags once its previous call is made', len(plans) == 34 and"))
R.append(('''          and 'KYTY_PIPELINE_PRECACHE' not in plans[v][1]) for v, lv in S.CENSUS)
ok &= case('g10 every V (the 12 of the census): its level of item 254 (k)(1), video, hold 330, stable-draws 300, timeout 480, '
           'no validation, no KYTY_PIPELINE_PRECACHE (shipped defaults)', vv and len(S.CENSUS) == 12)''',
          '''          and 'KYTY_PIPELINE_PRECACHE' not in plans[v][1] and 'VK_LAYER_MESSAGE_ID_FILTER' not in plans[v][1])
         for v, lv in S.CENSUS)
ok &= case('g10 every V (the 16 of the census): its level of item 273 (k)(1), video, hold 330, stable-draws 300, timeout 480, '
           'no validation, no KYTY_PIPELINE_PRECACHE, no message filter (shipped defaults)', vv and len(S.CENSUS) == 16)'''))
R.append(('''          and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000 KYTY_PIPELINE_PRECACHE=0 KYTY_GPU_CLOCK_PIN=1' in plans[w][1]''',
          '''          and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000 KYTY_PIPELINE_PRECACHE=0 VK_LAYER_MESSAGE_ID_FILTER='
              'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering KYTY_GPU_CLOCK_PIN=1' in plans[w][1]'''))
R.append(('''ok &= case('g11 every W (the control and the 20 of the pairs): its level, validation true with the layer path and the duplicate '
           'limit, the form KYTY_PIPELINE_PRECACHE=0 of item 254 (e) positional before the clock pin, hold 310, stable-draws 300, '
           'timeout 600, no video', ww and len(S.W_TAGS) == 21)''',
          '''ok &= case('g11 every W (the control, the W repeat and the 16 of the pairs): its level, validation true with the layer path '
           'and the duplicate limit, the form KYTY_PIPELINE_PRECACHE=0 and the one message filter of item 273 (k)(2) positional '
           'before the clock pin, hold 310, stable-draws 300, timeout 600, no video', ww and len(S.W_TAGS) == 18)'''))
R.append(('''ok &= case('g13 SEQ of the chain = sc145.SEQ (the control W, eight W, then V then W per level, item 254 (k)(1))', m is not None and''',
          '''ok &= case('g13 SEQ of the chain = sc145.SEQ (the control W, the W repeat, then V then W per level, item 273 (k)(1))',
           m is not None and'''))
R.append(('''ok &= case('g14 the chain tag -> level map: the control W and eight W-only tags = sc145 (CONTROL, the W of the eight v143 pairs), '
           'the twelve V/W pairs = sc145.PAIRS[8:]',
           tuple(lv) == S.PAIRS[8:] and tuple(lw) == ((S.CONTROL[0], S.CONTROL[1]),) + tuple((w, x) for _, w, x in S.PAIRS[:8]))''',
          '''ok &= case('g14 the chain tag -> level map: the control W and the W repeat = sc145 (CONTROL, the W of the v144_09 pair), the '
           'sixteen V/W pairs = sc145.PAIRS[1:]',
           tuple(lv) == S.PAIRS[1:] and tuple(lw) == ((S.CONTROL[0], S.CONTROL[1]),) + tuple((w, x) for _, w, x in S.PAIRS[:1]))'''))
R.append(('''for bad in ('v145_08', 'w145_21', 'v143_01', 'w143_01'):''',
          '''for bad in ('v145_01', 'w145_18', 'v144_09', 'w144_09', 'v143_01', 'w143_01'):'''))
R.append(('''    ok &= case('g38 next_one.sh refuses %s rc 2 (no V of the eight W-only levels, no tag past 20, no tag of 143)' % bad,''',
          '''    ok &= case('g38 next_one.sh refuses %s rc 2 (no V of the W repeat, no tag past 17, no tag of 144 or 143)' % bad,'''))
NEW = '''VKF = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
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
           0 < CODE.find('  v145_*) SD=') < CODE.find('  w145_*) SD=') and
           'EXTRA=' not in CODE[CODE.find('  v145_*) SD='):CODE.find('  w145_*) SD=')])
PR = Path(HERE, 'step2', 'pre_one.sh').read_bytes().decode('utf-8')
ok &= case('g48 pre_one.sh: ASCII and LF; the stop file and the lock first, then sc145.py --stop-check <tag> (its output and a '
           'times row with rc and sha), rc 5 on a stop, the lock again, then step2/gate145.py --before <tag>, rc 5 on its STOP',
           all(ord(c) < 128 for c in PR) and '\\r' not in PR and
           PR.find('[ -e C:/kyty/s145/STOP ]') < PR.find('[ -e C:/kyty/SEALED_RUN.lock ]') <
           PR.find('python sc145.py --stop-check $T > step2/stopcheck_$T.txt 2>&1') <
           PR.find('pre_one sc145.py --stop-check $T rc $SRC') < PR.find('[ "$SRC" != "0" ] && exit 5') <
           PR.find('python step2/gate145.py --before $T || exit 5') and 'mutlib' not in PR and
           'sc144' not in PR and 'gate144' not in PR)
PATS = re.search(r'\\n  ([^)]*)\\) ;;\\n', nx).group(1).split('|')
FM = __import__('fnmatch').fnmatchcase
ok &= case('g49 next_one.sh accepts exactly the 34 tags of the chain (its case pattern matches every SEQ tag and none of the bad '
           'tags)', all(any(FM(t, p) for p in PATS) for t in S.SEQ) and
           not any(FM(t, p) for t in ('v145_01', 'w145_18', 'v145_18', 'v144_09', 'w144_09', 'w145_1x', 'v145_00')
                   for p in PATS))
ok &= case('g50 the command lines of the wrappers name only session 145 (no 144 outside the comment lines); apichk145 writes '
           'the s145 times', all('144' not in l for x in (nx, cl, wt) for l in x.split('\\n') if not l.startswith('#')) and
           "TIMES = 'C:/kyty/s145/step2/times.txt'" in ATEXT and 'C:/kyty/s144' not in ATEXT)
'''
R.append(("print('checks: %d' % N[0])\nif ok:\n    print('ALL OK')\nsys.exit(0 if ok else 1)\n",
          NEW + "print('checks: %d' % N[0])\nif ok:\n    print('ALL OK')\nsys.exit(0 if ok else 1)\n"))
t = apply(t, R, 'test_go145a')
open(S5 + 'test_go145a.py', 'wb').write(t.encode('ascii'))
print('test_go145a.py %d replacements' % len(R))

# ---------------- the step 2 wrappers
for n in ('call_one.sh', 'wait_one.sh', 'pre_one.sh', 'next_one.sh', 'apichk144.py'):
    t = load(S4 + 'step2/' + n)
    R = []
    if n == 'next_one.sh':
        R.append(('  w144_0[0-8]|v144_09|w144_09|v144_1[0-9]|w144_1[0-9]|v144_20|w144_20) ;;\n',
                  '  w145_00|w145_01|v145_0[2-9]|w145_0[2-9]|v145_1[0-7]|w145_1[0-7]) ;;\n'))
        R.append(('  *) echo "usage: next_one.sh w144_00..w144_08|v144_NN|w144_NN (NN 09..20) [<last comment id read>]"; exit 2;;\n',
                  '  *) echo "usage: next_one.sh w145_00|w145_01|v145_NN|w145_NN (NN 02..17) [<last comment id read>]"; exit 2;;\n'))
        R.append(('# Session 144 step 2 call wrapper (step 0 HPP-330, ROADMAP s122 item 254 (i), (k); port of C:/kyty/s143/step2/next_one.sh):',
                  '# Session 145 step 2 call wrapper (step 0 HPP-350, ROADMAP s122 item 273 (k); port of C:/kyty/s144/step2/next_one.sh):'))
    elif n == 'pre_one.sh':
        R.append(('# Session 144 step 2 (HPP-332; ROADMAP s122 item 266 (h)): the checks before the call of one tag, in the order of the lead\'s',
                  '# Session 145 step 2 (step 0 HPP-350; ROADMAP s122 item 273 (k)(4); port of the s144 file of item 266 (h)): the checks\n'
                  '# before the call of one tag, in the order of the lead\'s'))
    elif n == 'apichk144.py':
        R.append(('"""apichk144.py - the API check row of step 2 of session 144 (MINOR-4 of audit 143, ROADMAP s122 item 254 (i); the line of',
                  '"""apichk145.py - the API check row of step 2 of session 145 (port of apichk144.py by HPP-350, names 144 -> 145;\n'
                  'MINOR-4 of audit 143, ROADMAP s122 item 254 (i); the line of'))
    else:
        R.append(('# Session 144 step 2 (step 0 HPP-330, ROADMAP s122 item 254 (k); port of the session-143 file, names moved to s144):',
                  '# Session 145 step 2 (step 0 HPP-350, ROADMAP s122 item 273 (k); port of the session-144 file, names moved to s145):'))
    t = apply(t, R, n)
    head, sep, rest = t.partition('\n') if n != 'pre_one.sh' else ('', '', t)
    t = t.replace('144', '145')
    for keep in ('port of C:/kyty/s145/step2/next_one.sh', 'port of the session-145 file', 'port of the s145 file',
                 'port of apichk145.py by HPP-350, names 145 -> 145', 'the session-145 file, names moved to s145'):
        pass
    t = t.replace('port of C:/kyty/s145/step2/next_one.sh', 'port of C:/kyty/s144/step2/next_one.sh')
    t = t.replace('port of the session-145 file, names moved to s145', 'port of the session-144 file, names moved to s145')
    t = t.replace('port of the s145 file of item 266 (h)', 'port of the s144 file of item 266 (h)')
    t = t.replace('port of apichk145.py by HPP-350, names 145 -> 145', 'port of apichk144.py by HPP-350, names 144 -> 145')
    t.encode('ascii')
    open(S5 + 'step2/' + n.replace('144', '145'), 'wb').write(t.encode('ascii'))
    print('step2/%s %d replacements' % (n.replace('144', '145'), len(R)))
