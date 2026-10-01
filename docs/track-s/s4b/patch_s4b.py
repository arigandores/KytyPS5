#!/usr/bin/env python3
"""S4b (HPP-349, ROADMAP "SESSION 122" item 265): the edits of sc_s.py, test_sc_s.py, mut_sc_s.py, go_s.sh, test_go_s.py.
Every anchor must occur exactly once; LF written with write_bytes.  The real lines of the fixtures are read from
s4/log_c1_0.txt (sha256 checked first) and embedded as bytes literals (repr) - byte for byte."""
import hashlib
import sys

R = 'C:/kyty/s288/'
LOG = R + 's4/log_c1_0.txt'
LOG_SHA = '49d0a5222ef568553808c8c34989b1a743e860a2bc39fd2c33ee7a8b9032d902'
NL = chr(10)


def rd(p):
    b = open(R + p, 'rb').read()
    assert b'\r' not in b, p
    return b.decode('ascii')


def edit(text, pairs, name):
    for a, b in pairs:
        n = text.count(a)
        assert n == 1, (name, n, a[:120])
        text = text.replace(a, b)
    return text


def wr(p, text):
    text.encode('ascii')
    open(R + p, 'wb').write(text.encode('ascii'))


got = hashlib.sha256(open(LOG, 'rb').read()).hexdigest()
assert got == LOG_SHA, got
real = {}
with open(LOG, 'rb') as f:
    for i, line in enumerate(f, 1):
        if i in (232401, 232417, 232418, 232419):
            real[i] = line.rstrip(b'\n')
        if i > 232419:
            break
assert real[232419].startswith(b'AvTrace: shader ShaderRecompiler VS hash=')
assert real[232418].startswith(b'AvTrace: shader-spec ') and real[232417].startswith(b'AvTrace: shader-cache save ')
assert real[232401].startswith(b'AvTrace: shader-emit ')

# ------------------------------------------------------------------------------------------------ sc_s.py
sc = rd('sc_s.py')
sc = edit(sc, [
    ('      seal) and its admission row is the positive control - no "PipelinePrecache: N recipes ->" line in its log.' + NL,
     '      seal) and its admission row is the positive control - no "PipelinePrecache: N recipes ->" line in its log.' + NL +
     '  (13) item 265 (S4b, HPP-349): RX_SHADER reads a label with a space - the emulator writes "AvTrace: shader' + NL +
     '      ShaderRecompiler VS hash=..." (4fc501f4 pipelineCache.cpp:3916); the S4 seal is pred/03_s.md for the arms after' + NL +
     '      c1_0; the arms made under seal 02 (SEAL02_TAGS) are admitted against seal 02 (its pinned sha256 SHA_02, the row' + NL +
     '      "prereg = the seal of its run 02_s.md"); the S6 seal is pred/04_s.md (item 265 (e)); --json-out writes the score' + NL +
     '      json elsewhere (the files of seal 02 are not rewritten, item 265 (v)(7)).' + NL),
    ('    python sc_s.py --tag <tag>          score one arm (rc 0 = arm PASS)' + NL,
     '    python sc_s.py --tag <tag> [--json-out <path>]   score one arm (rc 0 = arm PASS); json default runs_s/<tag>.score.json' + NL),
    ("PRED_PATH = 'C:/kyty/s288/pred/02_s.md'   # S4: seal 02 of S3b (item 250 (i)-(k)); seal 01 no longer holds for S4" + NL +
     "PRED_S6 = 'C:/kyty/s288/pred/03_s.md'     # S6: a later seal after S5d with the line \"pcw binary: <sha> <path>\" (variant)" + NL,
     "PRED_PATH = 'C:/kyty/s288/pred/03_s.md'   # S4: seal 03 of S4b (item 265) for the arms after c1_0; 01 and 02 no longer hold" + NL +
     "PRED_02 = 'C:/kyty/s288/pred/02_s.md'     # seal 02 of S3b: the arms made under it are admitted against it (item 265 (g))" + NL +
     "SHA_02 = '829ac684f2de5311cda035b5135d6bb262448bf282f5a2e803a2e73e447c6515'" + NL +
     "SEAL02_TAGS = ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1', 'c1_0')   # the S4 arms made under seal 02 (S4 times.txt, item 265)" + NL +
     "SEAL_PREV = (PRED_02, SHA_02, SEAL02_TAGS)" + NL +
     "PRED_S6 = 'C:/kyty/s288/pred/04_s.md'     # S6: item 265 (e) - a later seal with the line \"pcw binary: <sha> <path>\"" + NL),
    ("RX_SHADER = re.compile(rb'AvTrace: shader (\\S+) hash=0x([0-9a-fA-F]+) translate_us=(\\d+) compile_us=(\\d+)')" + NL,
     "# item 265: the label may hold a space ('ShaderRecompiler VS', 4fc501f4 pipelineCache.cpp:3916 - \"AvTrace: shader %s hash=\")" + NL +
     "RX_SHADER = re.compile(rb'AvTrace: shader (.+?) hash=0x([0-9a-fA-F]+) translate_us=(\\d+) compile_us=(\\d+)')" + NL),
    ("def admit(spec, js, pred_sha, bin_sha, cj, cjs_of, pred_path=PRED_PATH):" + NL,
     "def admit(spec, js, pred_sha, bin_sha, cj, cjs_of, pred_path=PRED_PATH, prev_run=False):" + NL),
    ("    pr = js.get('prereg') or {}" + NL +
     "    add('prereg = the seal now', pred_sha is not None and pr.get('sha256') == pred_sha" + NL,
     "    pr = js.get('prereg') or {}" + NL +
     "    # item 265 (g): an arm made under seal 02 is admitted against seal 02 (the seal of its run), by name" + NL +
     "    pname = ('prereg = the seal of its run %s (item 265 (g))' % os.path.basename(pred_path)) if prev_run else \\" + NL +
     "        'prereg = the seal now'" + NL +
     "    add(pname, pred_sha is not None and pr.get('sha256') == pred_sha" + NL),
    ("def score_arm(tag, root_map=None, pred_sha=None, bin_sha=None, ix=None, pred_path=None):" + NL,
     "def score_arm(tag, root_map=None, pred_sha=None, bin_sha=None, ix=None, pred_path=None, prev_run=False):" + NL),
    ("    r['admit'] = admit(spec, js, pred_sha, bin_sha, cj, cjs_of, pred_path or pred_for(spec))" + NL,
     "    r['admit'] = admit(spec, js, pred_sha, bin_sha, cj, cjs_of, pred_path or pred_for(spec), prev_run)" + NL),
    ("def make_get(root_map, preds, ix):" + NL +
     "    \"\"\"preds: link -> seal path.  The S4 binary is 9235a7ac; the S6 binary is the \"pcw binary:\" line of its seal.\"\"\"" + NL,
     "def make_get(root_map, preds, ix, prev=None):" + NL +
     "    \"\"\"preds: link -> seal path.  The S4 binary is 9235a7ac; the S6 binary is the \"pcw binary:\" line of its seal.\"\"\"" + NL +
     "    # prev = (path, pinned sha256, tags): the arms made under an earlier seal are admitted against it (item 265 (g));" + NL +
     "    # a file whose sha256 is not the pinned one admits none of them" + NL),
    ("        sha, bsha, p = info[SPEC[t]['link']]" + NL +
     "            memo[t] = score_arm(t, root_map, sha, bsha, ix, p)" + NL,
     "        sha, bsha, p = info[SPEC[t]['link']]" + NL +
     "            if prev is not None and t in prev[2]:" + NL +
     "                now = sha_file(prev[0]) if os.path.isfile(prev[0]) else None" + NL +
     "                memo[t] = score_arm(t, root_map, now if now == prev[1] else None, bsha, ix, prev[0], True)" + NL +
     "            else:" + NL +
     "                memo[t] = score_arm(t, root_map, sha, bsha, ix, p)" + NL),
    ("def main(argv=None, root_map=None, pred=PRED_PATH, index=INDEX_PATH, base_logs=None, pred_s6=PRED_S6):" + NL,
     "def main(argv=None, root_map=None, pred=PRED_PATH, index=INDEX_PATH, base_logs=None, pred_s6=PRED_S6, prev=None):" + NL),
    ("    ap.add_argument('--regress', action='store_true')" + NL,
     "    ap.add_argument('--regress', action='store_true')" + NL +
     "    ap.add_argument('--json-out', default=None)" + NL),
    ("    get = make_get(root_map, {'s4': pred, 's6': pred_s6}, ix)" + NL,
     "    if prev is None and pred == PRED_PATH:" + NL +
     "        prev = SEAL_PREV                 # item 265 (g): the arms of seal 02 under the production seal 03" + NL +
     "    get = make_get(root_map, {'s4': pred, 's6': pred_s6}, ix, prev)" + NL),
    ("        d = os.path.join(link_dir(SPEC[a.tag], root_map), 'runs_s')" + NL +
     "        os.makedirs(d, exist_ok=True)" + NL,
     "        d = os.path.join(link_dir(SPEC[a.tag], root_map), 'runs_s')" + NL +
     "        jp = a.json_out or os.path.join(d, '%s.score.json' % a.tag)" + NL +
     "        os.makedirs(os.path.dirname(os.path.abspath(jp)), exist_ok=True)" + NL),
    ("        json.dump(dump, open(os.path.join(d, '%s.score.json' % a.tag), 'w', encoding='utf-8'), indent=1, default=list)" + NL,
     "        json.dump(dump, open(jp, 'w', encoding='utf-8'), indent=1, default=list)" + NL),
], 'sc_s.py')
# the four-space indent of the memo lines in make_get: check the replaced block parses
compile(sc, 'sc_s.py', 'exec')
wr('sc_s.py', sc)

# ------------------------------------------------------------------------------------------------ test_sc_s.py
ts = rd('test_sc_s.py')
SECTION = '''# ================================================================================================ 12 S4b (HPP-349, item 265)
# real lines of C:/kyty/s288/s4/log_c1_0.txt (sha256 49d0a522...2d902), byte for byte, by their line numbers
REAL_EMIT = %r     # line 232401
REAL_CSAVE = %r    # line 232417
REAL_SPEC = %r     # line 232418
REAL_SH = %r       # line 232419
m = S.RX_SHADER.search(REAL_SH)
ok &= case('S4b-1 RX_SHADER reads the real line 232419 of log_c1_0.txt (label with a space, 4fc501f4 pipelineCache.cpp:3916): '
           'label ShaderRecompiler VS, hash, translate_us 11705, compile_us 6169', m is not None
           and m.group(1) == b'ShaderRecompiler VS' and m.group(2) == b'960ad032acbd9134' and m.group(3) == b'11705'
           and m.group(4) == b'6169')
m1 = S.RX_SHADER.search(SH(0x55, 7, 8).encode('ascii'))
ok &= case('S4b-2 a one-word label (the former form) still reads: label VS, translate 7, compile 8', m1 is not None
           and m1.group(1) == b'VS' and m1.group(2) == b'0000000000000055' and m1.group(3) == b'7' and m1.group(4) == b'8')
p4b = BASE / 'logs' / 's4b_real.txt'
p4b.parent.mkdir(parents=True, exist_ok=True)
p4b.write_bytes(b'\\n'.join([REAL_EMIT, REAL_CSAVE, REAL_SPEC, REAL_SH, LOAD(9).encode('ascii')]) + b'\\n')
s = S.scan_s(str(p4b))
ok &= case('S4b-3 order of the branches: of the real shader-emit / shader-cache save / shader-spec / shader lines only the '
           '"AvTrace: shader " line enters s[sh] (label, hash, translate, compile, line 4); shader-cache load goes to s[load]',
           s['sh'] == [(0, 'ShaderRecompiler VS', '960ad032acbd9134', 11705, 6169, 4)] and s['load'] == [(0, 9)]
           and s['avtrace'] == 5)
real_post = [(16000, dict(skip=1, ev=[SKIP(8, 1, 2), REAL_EMIT.decode('ascii'), REAL_CSAVE.decode('ascii'),
                                       REAL_SPEC.decode('ascii'), REAL_SH.decode('ascii')])), (16000, dict(held=1)),
             (16000, dict(ev=[RSAVE(101)])), (16000, {})]
real_post += [(16000, dict(ev=[GFX(30000)])) for _ in range(10)]
mkarm('c1_0', t_lines('shuriken_ninja_castle', real_post), stdout_shaders=1)
r = arm('c1_0', ix=IX)
t3 = [x for x in r['ident'] if x[0].startswith('T-3')]
ok &= case('S4b-4 a T arm with the real lines: T-3 1 / 1 PASS, attribution determined, cold gate "cold" (perm 1, recipe +1, '
           'skip 1), arm PASS', r['fail'] == [] and r['attr_ok'] and t3 and t3[0][1] is True and t3[0][2] == '1 / 1'
           and r['gates']['cold_word'] == 'cold' and r['gates']['perm_after'] == 1 and r['gates']['rec_new_after'] == 1
           and r['gates']['skip_after'] == 1)
# item 265 (g): the arms made under an earlier seal are admitted against it, by name; the others against the seal now
PREV = (BASE / 'pred' / 'prev_s.md').as_posix()
Path(PREV).write_bytes(b'an earlier seal\\n')
PREV_SHA = hashlib.sha256(Path(PREV).read_bytes()).hexdigest()
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), js=js_for('sw_m1', prereg=dict(path=PREV, sha256=PREV_SHA)))
mkarm('c2_0', t_lines('shuriken_ninja_castle', cold_post), stdout_shaders=1)
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None, (PREV, PREV_SHA, ('sw_m1', 'c1_0')))
a1 = dict((x[0], x[1]) for x in get('sw_m1')['admit'])
a2 = dict((x[0], x[1]) for x in get('c2_0')['admit'])
ok &= case('S4b-5 an arm of the earlier seal: row "prereg = the seal of its run prev_s.md (item 265 (g))" PASS, arm PASS; '
           'an arm after it: row "prereg = the seal now" PASS', a1.get('prereg = the seal of its run prev_s.md (item 265 (g))')
           is True and 'prereg = the seal now' not in a1 and get('sw_m1')['fail'] == [] and a2.get('prereg = the seal now')
           is True)
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None, (PREV, '00' * 32, ('sw_m1', 'c1_0')))
ok &= case('S4b-5b the earlier seal whose sha256 is not the pinned one admits none: prereg row FAIL',
           dict((x[0], x[1]) for x in get('sw_m1')['admit']).get('prereg = the seal of its run prev_s.md (item 265 (g))')
           is False)
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)))
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None, (PREV, PREV_SHA, ('sw_m1', 'c1_0')))
ok &= case('S4b-5c an arm of the earlier seal list whose json names the seal now -> prereg row FAIL (routed to its run)',
           dict((x[0], x[1]) for x in get('sw_m1')['admit']).get('prereg = the seal of its run prev_s.md (item 265 (g))')
           is False)
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), js=js_for('sw_m1', prereg=dict(path=PREV, sha256=PREV_SHA)))
jo = BASE / 'out' / 'sw_m1.s03.json'
sj = Path(RM['s4'], 'runs_s', 'sw_m1.score.json')
if sj.exists():
    sj.unlink()
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc11 = S.main(['--tag', 'sw_m1', '--json-out', str(jo)], root_map=RM, pred=PRED4, pred_s6=PRED6,
                  prev=(PREV, PREV_SHA, ('sw_m1',)))
o = buf.getvalue()
OUTS.append(o)
ok &= case('S4b-6 main --tag --json-out: rc 0, the json at the given path, runs_s/<tag>.score.json not written',
           rc11 == 0 and jo.is_file() and json.load(open(jo, encoding='utf-8'))['tag'] == 'sw_m1' and not sj.exists()
           and 'PASS admit prereg = the seal of its run prev_s.md (item 265 (g))' in o)
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), js=js_for('sw_m1', prereg=dict(path=S.PRED_02, sha256=S.SHA_02)))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc12 = S.main(['--tag', 'sw_m1', '--json-out', str(jo)], root_map=RM, pred=S.PRED_PATH, pred_s6=PRED6)
o = buf.getvalue()
OUTS.append(o)
ok &= case('S4b-7 main under the production seal routes the seal 02 arms to the real pred/02_s.md (pinned 829ac684): '
           'prereg row PASS, rc 0', rc12 == 0 and 'PASS admit prereg = the seal of its run 02_s.md (item 265 (g)) (829ac684)' in o)

'''
SECTION = SECTION % (real[232401], real[232417], real[232418], real[232419])
ts = edit(ts, [
    ("ok &= case('A9 seal paths and links (S4 seal 02 of S3b, S6 a later seal 03)', S.PRED_PATH == 'C:/kyty/s288/pred/02_s.md'" + NL +
     "           and S.PRED_S6 == 'C:/kyty/s288/pred/03_s.md'" + NL,
     "ok &= case('A9 seal paths and links (item 265: S4 seal 03 of S4b, the seal 02 arms sw_m1..sw_t1 + c1_0 by seal 02 829ac684, S6 a '" + NL +
     "           'later seal 04)', S.PRED_PATH == 'C:/kyty/s288/pred/03_s.md'" + NL +
     "           and S.PRED_S6 == 'C:/kyty/s288/pred/04_s.md' and S.PRED_02 == 'C:/kyty/s288/pred/02_s.md'" + NL +
     "           and S.SHA_02 == '829ac684f2de5311cda035b5135d6bb262448bf282f5a2e803a2e73e447c6515'" + NL +
     "           and S.SEAL02_TAGS == ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1', 'c1_0') and S.SEAL_PREV == (S.PRED_02, S.SHA_02, S.SEAL02_TAGS)" + NL),
    ("try:" + NL + "    '\\n'.join(OUTS).encode('cp1250', errors='strict')" + NL,
     SECTION + "try:" + NL + "    '\\n'.join(OUTS).encode('cp1250', errors='strict')" + NL),
    ("The first output line names this suite and the scorer under test by sha256 (item 150 (v)); the output ends with ALL OK." + NL,
     "S4b (HPP-349, ROADMAP item 265): RX_SHADER on the real line 232419 of s4/log_c1_0.txt (a label with a space) and on a" + NL +
     "one-word label, the order of the branches on the real shader-emit / shader-cache / shader-spec lines, a T arm with the" + NL +
     "real lines (T-3, the cold gate), the admission of the seal 02 arms against seal 02, --json-out (section 12)." + NL +
     "The first output line names this suite and the scorer under test by sha256 (item 150 (v)); the output ends with ALL OK." + NL),
], 'test_sc_s.py')
compile(ts, 'test_sc_s.py', 'exec')
wr('test_sc_s.py', ts)

# ------------------------------------------------------------------------------------------------ mut_sc_s.py
ms = rd('mut_sc_s.py')
ms = edit(ms, [
    ("    ('rx_shader', \"translate_us=(\\\\d+) compile_us=(\\\\d+)')\", \"translate_us=(\\\\d+) compile_us=(\\\\d)')\")," + NL,
     "    ('rx_shader', \"translate_us=(\\\\d+) compile_us=(\\\\d+)')\", \"translate_us=(\\\\d+) compile_us=(\\\\d)')\")," + NL +
     "    # item 265 (S4b): the label group of RX_SHADER" + NL +
     "    ('rx_shader_label', \"RX_SHADER = re.compile(rb'AvTrace: shader (.+?) hash=\", \"RX_SHADER = re.compile(rb'AvTrace: shader (\\\\S+) hash=\")," + NL +
     "    ('rx_shader_label2', \"RX_SHADER = re.compile(rb'AvTrace: shader (.+?) hash=\", \"RX_SHADER = re.compile(rb'AvTrace: shader (\\\\S+ \\\\S+) hash=\")," + NL),
    ("    ('ad_pred', \"add('prereg = the seal now', pred_sha is not None and pr.get('sha256') == pred_sha\", \"add('prereg = the seal now', pred_sha is not None\")," + NL,
     "    ('ad_pred', \"add(pname, pred_sha is not None and pr.get('sha256') == pred_sha\", \"add(pname, pred_sha is not None\")," + NL +
     "    # item 265 (S4b): the seal 02 arms admitted against seal 02, the seal names, --json-out" + NL +
     "    ('prev_name', \"if prev_run else \\\\\", \"if False else \\\\\")," + NL +
     "    ('prev_route', \"if prev is not None and t in prev[2]:\", \"if False:\")," + NL +
     "    ('prev_pin', \"now if now == prev[1] else None, bsha\", \"now, bsha\")," + NL +
     "    ('prev_main', \"    if prev is None and pred == PRED_PATH:\", \"    if False:\")," + NL +
     "    ('prev_tags', \"SEAL02_TAGS = ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1', 'c1_0')\", \"SEAL02_TAGS = ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1')\")," + NL +
     "    ('prev_sha', \"SHA_02 = '829ac684\", \"SHA_02 = '829ac685\")," + NL +
     "    ('pred_03', \"PRED_PATH = 'C:/kyty/s288/pred/03_s.md'\", \"PRED_PATH = 'C:/kyty/s288/pred/02_s.md'\")," + NL +
     "    ('pred_s6_04', \"PRED_S6 = 'C:/kyty/s288/pred/04_s.md'\", \"PRED_S6 = 'C:/kyty/s288/pred/03_s.md'\")," + NL +
     "    ('json_out', \"jp = a.json_out or os.path.join\", \"jp = None or os.path.join\")," + NL),
], 'mut_sc_s.py')
compile(ms, 'mut_sc_s.py', 'exec')
wr('mut_sc_s.py', ms)

# ------------------------------------------------------------------------------------------------ go_s.sh (the seal names only)
gs = rd('go_s.sh')
gs = edit(gs, [
    ('the line "pcw binary: <sha256> <path>" of the seal pred/02_s.md' + NL,
     'the line "pcw binary: <sha256> <path>" of the seal pred/04_s.md' + NL),
    ('#     the link (S4 pred/02_s.md of S3b - seal 01 no longer holds for S4, item 250 (i); S6 pred/03_s.md, the later seal' + NL,
     '#     the link (S4 pred/03_s.md of S4b, item 265 - seals 01 and 02 no longer hold for S4; S6 pred/04_s.md, the later seal' + NL),
    ('  s4) PRED="pred/02_s.md";;' + NL + '  s6) PRED="pred/03_s.md";;' + NL,
     '  s4) PRED="pred/03_s.md";;' + NL + '  s6) PRED="pred/04_s.md";;' + NL),
    ('(S6 before pred/02_s.md)', '(S6 before pred/04_s.md)'),
], 'go_s.sh')
wr('go_s.sh', gs)

# ------------------------------------------------------------------------------------------------ test_go_s.py (the seal names only)
tg = rd('test_go_s.py')
assert tg.count('03_s.md') == 4 and tg.count('02_s.md') == 2, (tg.count('03_s.md'), tg.count('02_s.md'))
tg = tg.replace('03_s.md', '04_s.md').replace('02_s.md', '03_s.md')
wr('test_go_s.py', tg)
for p in ('sc_s.py', 'test_sc_s.py', 'mut_sc_s.py', 'go_s.sh', 'test_go_s.py'):
    print('%s sha256 %s' % (p, hashlib.sha256(open(R + p, 'rb').read()).hexdigest()))
print('PATCH OK')
