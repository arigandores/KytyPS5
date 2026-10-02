"""port_testgo146.py - session 146 step 0 (HPP-386): C:/kyty/s146/test_go146a.py from C:/kyty/s145/test_go145a.py.  Names move
145 -> 146; the cases of the order (35 tags: the control W, four V-only tags, then V then W per level), the W form of item 300
(b)(4) (no KYTY_PIPELINE_PRECACHE), the levels, the build dac02fb9, the BUSY row with <app>, the bad tags are changed; new
cases g51-g55: the skip of item 309 (k)(1) (the skipped marker as a made call of the order and as a refusal of a second call,
the --skip-w block before the lock, its times row), the tiles row of every V video, D-9 of next_one.sh.  LF, ASCII."""
import hashlib
import sys

SRC = 'C:/kyty/s145/test_go145a.py'
DST = 'C:/kyty/s146/test_go146a.py'
t = open(SRC, 'rb').read().decode('ascii')
OK = [True]


def rep(old, new, n=1):
    global t
    k = t.count(old)
    if k != n:
        print('ANCHOR %d != %d: %r' % (k, n, old[:90]))
        OK[0] = False
        return
    t = t.replace(old, new)


rep('''"""Fixtures of the chain go145a.sh (session 145 step 0, HPP-350;''', '''"""Fixtures of the chain go146a.sh (session 146 step 0, HPP-386; ROADMAP s122 item 309 (k), (l)(1)-(7), item 300 (b)(4)).
Port of C:/kyty/s145/test_go145a.py (names moved 145 -> 146; the order of the 35 tags, the W form without
KYTY_PIPELINE_PRECACHE, the levels, the build dac02fb9 and its pinned copy, the BUSY row with <app>, the bad tags - g1, g5, g6,
g8, g10, g11, g14, g15, g20, g27, g29, g38, g46, g47, g49 changed; g51-g55 new: the skip of item 309 (k)(1), the tiles row,
D-9 of next_one.sh).
Session 145 text (carried): Fixtures of the chain go145a.sh (session 145 step 0, HPP-350;''')
for a, b in (('fx_go145a', 'fx_go146a'), ('pred/03_sc145.md', 'pred/01_sc146.md'), ("'03_sc145.md'", "'01_sc146.md'"),
             ('apichk145', 'apichk146'), ('gate145', 'gate146'), ('fgcpu145', 'fgcpu146'), ('cachemf145', 'cachemf146'),
             ('runs145', 'runs146'), ('sc145', 'sc146'), ('go145a', 'go146a'), ('C:/kyty/s145', 'C:/kyty/s146'), ('/c/kyty/s145', '/c/kyty/s146'),
             ("'ROOT=C:/kyty/s146\\n'", "'ROOT=C:/kyty/s146\\n'"), ('test_go145a', 'test_go146a')):
    t = t.replace(a, b)
rep("""ok &= case('g1 an unknown tag (a tag of session 142, 143 or 144 - the V v144_09 of the pair is no chain tag -, a V of the '
           'control or of the W repeat, a tag past 17) -> rc 2 usage',
           call(r, 'x145')[0] == 2 and call(r, 'x145')[1].startswith('usage') and call(r, 'v142')[0] == 2 and
           call(r, 'v143_01')[0] == 2 and call(r, 'v144_09')[0] == 2 and call(r, 'w144_00')[0] == 2 and
           call(r, 'v145_00')[0] == 2 and call(r, 'v145_01')[0] == 2 and call(r, 'w145_18')[0] == 2 and
           call(r, 'v145_18')[0] == 2)""", """ok &= case('g1 an unknown tag (a tag of session 142-145, a V of the control, a W of a re-check, a tag past 19, the warm-up '
           'i146_v) -> rc 2 usage',
           call(r, 'x146')[0] == 2 and call(r, 'x146')[1].startswith('usage') and call(r, 'v142')[0] == 2 and
           call(r, 'v143_01')[0] == 2 and call(r, 'v144_09')[0] == 2 and call(r, 'w145_17')[0] == 2 and
           call(r, 'v146_00')[0] == 2 and call(r, 'w146_01')[0] == 2 and call(r, 'v146_04')[0] == 2 and
           call(r, 'w146_20')[0] == 2 and call(r, 'v146_20')[0] == 2 and call(r, 'r146_05')[0] == 2 and
           call(r, 'i146_v')[0] == 2)""")
t = t.replace("call(r, 'w145_00', DRY='1'", "call(r, 'w146_00', DRY='1'")
rep("""(r / 'attempt_w145_00.txt').write_text('made\\n')
rc, out = call(r, 'w146_00', DRY='1')
(r / 'attempt_w145_00.txt').unlink()
(r / 'w145_00.json').write_text('{}')
rc2, out2 = call(r, 'w146_00', DRY='1')
ok &= case('g5 one attempt: the marker or <tag>.json -> rc 1', rc == 1 and rc2 == 1 and 'attempt already made' in out + out2)""",
    """(r / 'attempt_w146_00.txt').write_text('made\\n')
rc, out = call(r, 'w146_00', DRY='1')
(r / 'attempt_w146_00.txt').unlink()
(r / 'w146_00.json').write_text('{}')
rc2, out2 = call(r, 'w146_00', DRY='1')
(r / 'w146_00.json').unlink()
(r / 'skipped_w146_00.txt').write_text('SKIPPED_V_NOT_ENTERED x\\n')
rc3, out3 = call(r, 'w146_00', DRY='1')
ok &= case('g5 one call: the marker, <tag>.json or the skipped marker of item 309 (k)(1) -> rc 1',
           rc == 1 and rc2 == 1 and rc3 == 1 and 'attempt already made' in out + out2 + out3)""")
rep("""rc, out = call(r, 'w145_01', DRY='1')
(r / 'attempt_w145_00.txt').write_text('made\\n')
rc2, out2 = call(r, 'w145_01', DRY='1')
rc3, out3 = call(r, 'v145_02', DRY='1')
(r / 'w145_01.json').write_text('{}')
rc4, out4 = call(r, 'v145_02', DRY='1')
rc5, out5 = call(r, 'w145_02', DRY='1')
rc6, out6 = call(r, 'v145_03', DRY='1')
ok &= case('g6 order: w145_01 before w145_00 -> rc 1; after the w145_00 marker -> DRY rc 0; v145_02 before w145_01 -> rc 1, '
           'after w145_01.json -> rc 0; w145_02 before v145_02 -> rc 1; v145_03 before w145_02 -> rc 1',
           rc == 1 and 'previous call not made' in out and rc2 == 0 and rc3 == 1 and rc4 == 0 and rc5 == 1 and rc6 == 1)""",
    """rc, out = call(r, 'r146_01', DRY='1')
(r / 'attempt_w146_00.txt').write_text('made\\n')
rc2, out2 = call(r, 'r146_01', DRY='1')
rc3, out3 = call(r, 'r146_02', DRY='1')
for x in ('r146_01', 'r146_02', 'r146_03'):
    (r / ('%s.json' % x)).write_text('{}')
rc4, out4 = call(r, 'v146_05', DRY='1')
(r / 'r146_04.json').write_text('{}')
rc4b, out4b = call(r, 'v146_05', DRY='1')
rc5, out5 = call(r, 'w146_05', DRY='1')
rc6, out6 = call(r, 'v146_06', DRY='1')
(r / 'attempt_v146_05.txt').write_text('made\\n')
(r / 'skipped_w146_05.txt').write_text('SKIPPED_V_NOT_ENTERED x\\n')
rc7, out7 = call(r, 'v146_06', DRY='1')
ok &= case('g6 order: r146_01 before w146_00 -> rc 1; after the w146_00 marker -> DRY rc 0; r146_02 before r146_01 -> rc 1; '
           'v146_05 before r146_04 -> rc 1, after it -> rc 0; w146_05 before v146_05 -> rc 1; v146_06 before w146_05 -> rc 1; '
           'after the skipped marker of w146_05 (item 309 (k)(1)) -> rc 0',
           rc == 1 and 'previous call not made' in out and rc2 == 0 and rc3 == 1 and rc4 == 1 and rc4b == 0 and rc5 == 1
           and rc6 == 1 and rc7 == 0)""")
t = t.replace("call(r, 'w145_00'", "call(r, 'w146_00'").replace("line('w145_00'", "line('w146_00'").replace(
    "line('w145_01')", "line('r146_01')").replace("go142a.sh w145_00", "go142a.sh w146_00")
rep("""ok &= case('g8 DRY rc 0 for every one of the 34 tags once its previous call is made', len(plans) == 34 and""",
    """ok &= case('g8 DRY rc 0 for every one of the 35 tags once its previous call is made', len(plans) == 35 and""")
rep("""         for v, lv in S.CENSUS)
ok &= case('g10 every V (the 16 of the census): its level of item 273 (k)(1), video, hold 330, stable-draws 300, timeout 480, '
           'no validation, no KYTY_PIPELINE_PRECACHE, no message filter (shipped defaults)', vv and len(S.CENSUS) == 16)""",
    """         for v, lv in [(x, S.level_of(x)) for x in S.V_TAGS])
ok &= case('g10 every V (the 4 re-check / second-hold V and the 15 of the census): its level of item 309 (l)(2), video, hold 330, '
           'stable-draws 300, timeout 480, no validation, no KYTY_PIPELINE_PRECACHE, no message filter (shipped defaults)',
           vv and len(S.V_TAGS) == 19 and len(S.CENSUS) == 15)""")
rep("""          and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_PIPELINE_PRECACHE=0 '
              'KYTY_GPU_CLOCK_PIN=1' in plans[w][1] and 'VK_LAYER_MESSAGE_ID_FILTER' not in plans[w][1]""",
    """          and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 '
              'KYTY_GPU_CLOCK_PIN=1' in plans[w][1] and 'VK_LAYER_MESSAGE_ID_FILTER' not in plans[w][1]
          and 'KYTY_PIPELINE_PRECACHE' not in plans[w][1]""")
rep("""ok &= case('g11 every W (the control, the W repeat and the 16 of the pairs): its level, validation true with the layer path '
           'and the duplicate limit 100000000, the form KYTY_PIPELINE_PRECACHE=0 positional before the clock pin, no message '
           'filter (item 295 (b)), hold 310, stable-draws 300, timeout 600, no video', ww and len(S.W_TAGS) == 18)""",
    """ok &= case('g11 every W (the control and the 15 of the pairs): its level, validation true with the layer path and the '
           'duplicate limit 100000000 positional before the clock pin, precache by default (no KYTY_PIPELINE_PRECACHE, item 300 '
           '(b)(4)), no message filter (item 295 (b)), hold 310, stable-draws 300, timeout 600, no video',
           ww and len(S.W_TAGS) == 16)""")
rep("""ok &= case('g13 SEQ of the chain = sc146.SEQ (the control W, the W repeat, then V then W per level, item 273 (k)(1))',""",
    """ok &= case('g13 SEQ of the chain = sc146.SEQ (the control W, the four V-only tags, then V then W per level, item 309 (l)(2))',""")
rep("""lv = re.findall(r'\\n  (v145_\\d\\d)\\|(w145_\\d\\d)\\) LEVEL=(\\w+);;', TEXT)
lw = re.findall(r'\\n  (w145_\\d\\d)\\) LEVEL=(\\w+);;', TEXT)
ok &= case('g14 the chain tag -> level map: the control W and the W repeat = sc146 (CONTROL, the W of the v144_09 pair), the '
           'sixteen V/W pairs = sc146.PAIRS[1:]',
           tuple(lv) == S.PAIRS[1:] and tuple(lw) == ((S.CONTROL[0], S.CONTROL[1]),) + tuple((w, x) for _, w, x in S.PAIRS[:1]))""",
    """lv = re.findall(r'\\n  (v146_\\d\\d)\\|(w146_\\d\\d)\\) LEVEL=(\\w+);;', TEXT)
lw = re.findall(r'\\n  ([wr]146_\\d\\d)\\) LEVEL=(\\w+);;', TEXT)
ok &= case('g14 the chain tag -> level map: the control W and the four V-only tags = sc146 (CONTROL, RECHECK), the fifteen V/W '
           'pairs = sc146.PAIRS', tuple(lv) == S.PAIRS and tuple(lw) == ((S.CONTROL[0], S.CONTROL[1]),) + tuple(S.RECHECK))""")
rep("""ok &= case('g15 constants: the installed build 9235a7ac and its pinned copy, the empty-file sha, s51_vidglitch.py of scripts',
           'BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"' in TEXT and
           'BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"' in TEXT and""",
    """ok &= case('g15 constants: the installed build dac02fb9 and its pinned copy of step 0, the empty-file sha, s51_vidglitch.py',
           'BUILD_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"' in TEXT and
           'BUILD_PINNED="/c/kyty/s146/kyty_emulator_dac02fb9.exe"' in TEXT and""")
rep("""all('date -u' in l for l in TEXT.split('\\n') if '>> $TIMES' in l) and TEXT.count('>> $TIMES') == 12)""",
    """all('date -u' in l for l in TEXT.split('\\n') if '>> $TIMES' in l) and TEXT.count('>> $TIMES') == 14)""")
rep("""ok &= case('g27 item 231 (z)(5): a procload refusal writes a BUSY row of step2/times.txt whose process name comes from the '
           'last "procload: busy" line of go146a.log, read by the same command',
           "echo \\"$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | "
           "cut -c1-300)\\" >> $TIMES" in TEXT and""",
    """ok &= case('g27 item 231 (z)(5) and "Process" 5 of s145: a procload refusal writes a BUSY row of step2/times.txt from the last '
           '"procload: busy" line of go146a.log with every process name replaced by <app> (sed), read by the same command',
           "echo \\"$(date -u +%Y-%m-%dT%H:%M:%SZ) go146a $T BUSY $1: $(grep 'procload: busy' $L 2>/dev/null | tail -1 | "
           "sed -E \\"s/\\\\('[^']*'/('<app>'/g\\" | cut -c1-300)\\" >> $TIMES" in TEXT and""")
rep("""ok &= case('g29 the levels of the chain are exactly sc146.LEVELS after the control level',
           [x[1] for x in lw] + [x[2] for x in lv] == [S.SKY] + list(S.LEVELS))""",
    """ok &= case('g29 the levels of the chain are exactly the control level, the RECHECK levels and sc146.LEVELS',
           [x[1] for x in lw] + [x[2] for x in lv] == [S.SKY] + [x[1] for x in S.RECHECK] + list(S.LEVELS))""")
rep("""ok &= case('g28 the name guard pattern watches the mutants and fixtures of 145 and the emulator',
           "'mut_[a-z0-9_]*145|test_[a-z0-9_]*145|mutlib'" in TEXT""", """ok &= case('g28 the name guard pattern watches the mutants and fixtures of 146 and the emulator',
           "'mut_[a-z0-9_]*146|test_[a-z0-9_]*146|mutlib'" in TEXT""")
rep("""for bad in ('v145_01', 'w145_18', 'v144_09', 'w144_09', 'v143_01', 'w143_01'):""",
    """for bad in ('v146_04', 'w146_04', 'w146_20', 'r146_05', 'w146_01', 'v145_02', 'w145_00', 'i146_v'):""")
rep("""    ok &= case('g38 next_one.sh refuses %s rc 2 (no V of the W repeat, no tag past 17, no tag of 144 or 143)' % bad,""",
    """    ok &= case('g38 next_one.sh refuses %s rc 2 (no tag outside the 35 of the chain)' % bad,""")
rep("""           'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0";;\\n' in CODE and""",
    """           'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP";;\\n' in CODE and 'KYTY_PIPELINE_PRECACHE' not in CODE.split('\\nunset ')[1].split('\\n', 1)[1] and""")
rep("""ok &= case('g47 the W EXTRA case is the w145_* branch, the V branch has no EXTRA (shipped defaults)',
           0 < CODE.find('  w145_*) SD=') < CODE.find('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP') and
           0 < CODE.find('  v145_*) SD=') < CODE.find('  w145_*) SD=') and
           'EXTRA=' not in CODE[CODE.find('  v145_*) SD='):CODE.find('  w145_*) SD=')])""",
    """ok &= case('g47 the W EXTRA case is the w146_* branch, the V branch (v146_* and r146_*) has no EXTRA (shipped defaults)',
           0 < CODE.find('  w146_*) SD=') < CODE.find('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP') and
           0 < CODE.find('  v146_*|r146_*) SD=') < CODE.find('  w146_*) SD=') and
           'EXTRA=' not in CODE[CODE.find('  v146_*|r146_*) SD='):CODE.find('  w146_*) SD=')])""")
rep("""ok &= case('g49 next_one.sh accepts exactly the 34 tags of the chain (its case pattern matches every SEQ tag and none of the bad '
           'tags)', all(any(FM(t, p) for p in PATS) for t in S.SEQ) and
           not any(FM(t, p) for t in ('v145_01', 'w145_18', 'v145_18', 'v144_09', 'w144_09', 'w145_1x', 'v145_00')
                   for p in PATS))""",
    """ok &= case('g49 next_one.sh accepts exactly the 35 tags of the chain (its case pattern matches every SEQ tag and none of the bad '
           'tags)', all(any(FM(t, p) for p in PATS) for t in S.SEQ) and
           not any(FM(t, p) for t in ('v146_04', 'w146_04', 'w146_01', 'w146_20', 'v146_20', 'r146_05', 'r146_00', 'v145_02',
                                      'w146_1x', 'v146_00', 'i146_v') for p in PATS))""")
rep("""ok &= case('g50 the command lines of the wrappers name only session 145 (no 144 outside the comment lines); apichk146 writes '
           'the s145 times', all('144' not in l for x in (nx, cl, wt) for l in x.split('\\n') if not l.startswith('#')) and
           "TIMES = 'C:/kyty/s146/step2/times.txt'" in ATEXT and 'C:/kyty/s144' not in ATEXT)""",
    """ok &= case('g50 the command lines of the wrappers name only session 146 (no 145 or 144 outside the comment lines); apichk146 '
           'writes the s146 times', all('145' not in l and '144' not in l for x in (nx, cl, wt) for l in x.split('\\n')
                                       if not l.startswith('#')) and
           "TIMES = 'C:/kyty/s146/step2/times.txt'" in ATEXT and 'C:/kyty/s145' not in ATEXT)
sk0 = CODE.find('  w146_00) ;;\\n  w146_*)\\n    SKL=$(python $ROOT/$SC --skip-w $T 2>&1')
ok &= case('g51 item 309 (k)(1): the skip block runs after the stop-check and before the CPU check, the lock and any install; '
           'the control W is outside it; a W of a pair asks sc146.py --skip-w; SKIPPED_V_NOT_ENTERED writes skipped_<tag>.txt '
           'and a date -u row and exits rc 0; RUN goes on; any other answer refuses rc 1',
           CODE.find('python $ROOT/$SC --stop-check $T >> $L 2>&1') < sk0 < CODE.find('CPU=$(powershell') <
           CODE.find('set -o noclobber') and
           '        echo "$SKL $(date -u +%Y-%m-%dT%H:%M:%SZ)" > skipped_$T.txt\\n' in CODE and
           'go146a $T SKIPPED_V_NOT_ENTERED (item 309 (k)(1); no lock, not an attempt): $SKL" >> $TIMES' in CODE and
           'log "go146a.sh $T skipped: $SKL"; echo "$SKL"; exit 0;;' in CODE and 'RUN*) log "go146a.sh $T runs: $SKL";;' in CODE
           and "*) log \\"go146a.sh $T refused: --skip-w answered '$SKL'\\"; echo \\"skip-w failed\\"; exit 1;;" in CODE)
ok &= case('g52 every DRY plan names the skip of a W of a pair', all('--skip-w' in o for _, o in plans.values()))
ok &= case('g53 the tiles row of item 309 (l)(4): after the sheet of a V video, tiles146.py writes tiles_<tag>.txt and its '
           'triples sheet; a date -u row with its rc (TLRC) and sha; the stale list moves old tiles files',
           CODE.find(' sheet rc $SHRC ') < CODE.find('python $ROOT/tiles146.py rec_$T.mp4 tiles_$T.txt --sheet tiles_$T.png') <
           CODE.find('    TLRC=$?\\n') < CODE.find(' tiles rc $TLRC tiles_$T.txt sha256 $(sha tiles_$T.txt)') and
           '"tiles_$T.txt" "tiles_$T.png"' in CODE)
ok &= case('g54 D-9 (item 309 (i)): next_one.sh moves the previous output of the tag to step2/old/ (a date -u row) after the API '
           'check and before the call row; an output without its rc= line (a call still running) refuses rc 1 without a call',
           nx.find('apichk146.py --tag $T') < nx.find('GO=C:/kyty/s146/step2/go_$T.out.txt') <
           nx.find("grep -q '^rc=' $GO || {") < nx.find('mv $GO $NEWN') <
           nx.find('api GO; call: PLWAIT=540 bash C:/kyty/s146/go146a.sh $T') and
           'no new call"; exit 1; }' in nx and 'previous output of $T moved to step2/old/' in nx)
ok &= case('g55 the chain names the files of the seal: tiles146.py and lockcheck146.py in the files line; the W hold 310 and V '
           'hold 330 unchanged', 'tiles146.py $VIDGLITCH' in CODE and 'lockcheck146.py' in CODE and 'VHOLD="330"' in CODE and
           'WHOLD="310"' in CODE)""")
if any(ord(c) > 127 for c in t):
    print('NON-ASCII')
    OK[0] = False
open(DST, 'wb').write(t.encode('ascii'))
print('port_testgo146: %s %s -> %s %s' % (SRC, hashlib.sha256(open(SRC, 'rb').read()).hexdigest()[:16], DST,
                                           hashlib.sha256(t.encode('ascii')).hexdigest()[:16]))
print('ALL OK' if OK[0] else 'SOME FAILED')
sys.exit(0 if OK[0] else 1)
