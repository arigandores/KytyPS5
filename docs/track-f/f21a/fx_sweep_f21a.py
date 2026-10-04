# F21a (HPP-563): fixture of sweep_f21a.py - a synthetic log with every marker and every edge: stub lines of two
# libraries before and after a level line, a <bad-record> line, the printf form, an index restart, CRLF, a Windows
# program path, an empty level line, the four skip classes, miss / hit lines, 'shader CFG build failed' inside and
# outside a CsPretranslate line, PLT / non-PLT relocation lines, Late-resolved lines, a 'FrameTrace: n=' text that
# does not start a line, a last line without a newline.  The log is swept with a 4096-byte block (every marker
# crosses block borders somewhere in the padding), with the default block and as '.xz'; the three records must be
# equal member by member and equal to the expected values.  Prints one line per member and 'ALL OK'.
# Usage: python fx_sweep_f21a.py [work dir]
import hashlib, json, lzma, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace(chr(92), '/')
W = (sys.argv[1] if len(sys.argv) > 1 else HERE + '/fxwork').rstrip('/')
os.makedirs(W, exist_ok=True)
NL = chr(10)
BSL = chr(92)
L = []
ln = {}


def add(text, key=None):
    L.append(text)
    if key:
        ln[key] = len(L)


def pad(k):
    for i in range(k):
        add('Read 0x%08x bytes filler line %d of the padding block' % (i * 4096, i))


REL = 'Relocate: unresolved %s patched to stub [%d] [0000000908e34c90] <- 0000000200000000, %s, Func, Global, C:/g/eboot.bin'
STUB = 'Unresolved import stub called [%d]: patch_vaddr=0x0000000908e36f50 jmprela_index=1241 symbol=%s type=Func bind=Global program=%s'
S1 = 'S1nid[LibA_v1][LibA_v1.0][Func]'
S2 = 'S2nid[AudioPropagation_v1][AudioPropagation_v1.0][Func]'
S3 = 'S3nid[LibA_v1][LibA_v1.0][Func]'
add('Kyty header line')
add(REL % ('PLT import', 1, 'N1[Net_v1][Net_v1.1][Func]'))
add(REL % ('PLT import', 2, 'N2[Net_v1][Net_v1.1][Func]'))
add(REL % ('non-PLT function', 3, 'F1[Foo_v1][Foo_v1.0][Func]'))
add('FixB9a: on')
add('prefix FixB9a: not at the line start')
add('CsPretranslate: skipped hash=1111111111111111 reason=X.cpp:171 shader resource tracking: something')
add('CsPretranslate: skipped hash=2222222222222222 reason=T.h:21 speculative translation budget exceeded')
add('CsPretranslate: skipped hash=3333333333333333 reason=C.cpp:44 shader CFG build failed: unsupported family=VOPC opcode=0xf3 raw=[0x1]')
add('CsPretranslate: skipped hash=4444444444444444 reason=R.cpp:173 shader resource tracking: pc=0x1a0 GetBufferResource dword 1 is not a valid runtime value')
add('CsPretranslate: enqueue skipped hash=6666666666666666 reason=x')
add('CsPretranslate: summary queued=4 done=0')
pad(120)
add('GuestOut: Level has started: ')
add(STUB % (0, S1, 'C:/g/eboot.bin'), 's1a')
add('GuestOut: Level has started: lvl_one', 'lvl_one')
add('FrameTrace: n=1 dt_us=1000 draws=5')
pad(150)
add('FrameTrace: n=2 dt_us=1000 draws=5')
add('xFrameTrace: n=9 dt_us=5 draws=1')
add(STUB % (1, S1, 'C:/g/eboot.bin'))
add(STUB % (2, S2, 'C:/g/eboot.bin'), 's2')
add('CsPretranslate: miss hash=1111111111111111 reason=absent', 'miss1')
add('CsPretranslate: hit hash=5555555555555555 saved_us=10 hits=1', 'hit5')
add('CsPretranslate: miss hash=5555555555555555 reason=not-ready')
add('shader CFG build failed: boom outside', 'cfgout')
add('Late-resolved import: L1[LibB_v1][LibB_v1.0][Func] -> name [0x0000000000000001]')
add('Late-resolved import: L1[LibB_v1][LibB_v1.0][Func] -> name [0x0000000000000001]')
add('=== Stubbed function, returning OK ===')
add('FrameTrace: n=3 dt_us=1000 draws=5')
pad(200)
add('GuestOut: Level has started: lvl_two', 'lvl_two')
add('FrameTrace: n=4 dt_us=2000 draws=5')
add('Unresolved import stub called [3]: record_id=7 symbol=<bad-record>')
add('Unresolved import stub called: plainname')
add(STUB % (0, S3, 'C:' + BSL + 'g' + BSL + 'sub' + BSL + 'eboot.bin') + chr(13), 's3')
add('--- Fatal Error ---')
add('FrameTrace: n=5 dt_us=2000 draws=5')
pad(90)
add('FrameTrace: n=7 dt_us=7000 draws=1')
text = NL.join(L).encode('utf-8')          # no newline after the last line
plain = W + '/log_fx.txt'
open(plain, 'wb').write(text)
with lzma.open(W + '/log_fxz.txt.xz', 'wb') as f:
    f.write(text)
sha = hashlib.sha256(text).hexdigest()


def run(path, block):
    lst = W + '/l.tsv'
    out = W + '/o.jsonl'
    open(lst, 'w', encoding='utf-8', newline=NL).write('%s%s%d%s' % (path, chr(9), os.path.getsize(path), NL))
    if os.path.exists(out):
        os.remove(out)
    env = dict(os.environ)
    env['F21A_LOCK'] = W + '/no_lock'
    env['F21A_STOP'] = W + '/no_stop'
    if block:
        env['F21A_BLOCK'] = str(block)
    else:
        env.pop('F21A_BLOCK', None)
    o = subprocess.run([sys.executable, HERE + '/sweep_f21a.py', lst, out, '100'], capture_output=True, text=True, env=env)
    assert 'SWEEP COMPLETE' in o.stdout, o.stdout + o.stderr
    return json.loads(open(out, encoding='utf-8').read())


a = run(plain, 4096)
b = run(plain, 0)
c = run(W + '/log_fxz.txt.xz', 4096)
ok = True


def chk(name, got, want):
    global ok
    good = got == want
    ok &= good
    print('%s %s: %r%s' % ('ok  ' if good else 'FAIL', name, got, '' if good else ' expected %r' % (want,)))


stub = {s['symbol']: s for s in a['stub']}
chk('block 4096 == default block', a, b)
chk('xz record == plain record (but path, size, xz, sha256, sha256_text, xz_rc)',
    {k: v for k, v in c.items() if k not in ('path', 'size', 'xz', 'sha256', 'sha256_text', 'xz_rc')},
    {k: v for k, v in a.items() if k not in ('path', 'size', 'xz', 'sha256')})
chk('sha256 of the plain log', a['sha256'], sha)
chk('sha256_text of the xz log', c['sha256_text'], sha)
chk('xz_rc', c['xz_rc'], 0)
chk('lines', a['lines'], len(L))
chk('ft_n (the text inside a line is not a frame, the last line without a newline is)', a['ft_n'], 6)
chk('ft_us', a['ft_us'], 14000)
chk('stub_lines', a['stub_lines'], 5)
chk('stub_plain (printf form)', a['stub_plain'], 1)
chk('stub_bad', a['stub_bad'], 1)
chk('stub_unparsed', a['stub_unparsed'], 0)
chk('stub_max_idx', a['stub_max_idx'], 3)
chk('stub_idx_restart', a['stub_idx_restart'], 1)
chk('stub symbols', sorted(stub), sorted([S1, S2, S3]))
chk('S1 n / levels / first_line / idx', (stub[S1]['n'], stub[S1]['levels'], stub[S1]['first_line'], stub[S1]['first_idx'], stub[S1]['last_idx']),
    (2, {'': 1, 'lvl_one': 1}, ln['s1a'], 0, 1))
chk('S2 lib / n / levels / first_line', (stub[S2]['lib'], stub[S2]['n'], stub[S2]['levels'], stub[S2]['first_line']),
    ('AudioPropagation_v1', 1, {'lvl_one': 1}, ln['s2']))
chk('S3 (CRLF, Windows path) program / nid / module / levels / first_line', (stub[S3]['program'], stub[S3]['nid'], stub[S3]['module'], stub[S3]['levels'], stub[S3]['first_line'], stub[S3]['type'], stub[S3]['bind']),
    ('eboot.bin', 'S3nid', 'LibA_v1.0', {'lvl_two': 1}, ln['s3'], 'Func', 'Global'))
chk('levels', a['levels'], [
    {'level': 'lvl_one', 'line': ln['lvl_one'], 'ft_before': 0, 'frames': 3, 'sum_us': 3000, 'stub_before': 1},
    {'level': 'lvl_two', 'line': ln['lvl_two'], 'ft_before': 3, 'frames': 3, 'sum_us': 11000, 'stub_before': 3}])
chk('lvl_empty', a['lvl_empty'], 1)
chk('cs_skipped', a['cs_skipped'], {'1111111111111111': 'RESTRACK', '2222222222222222': 'BUDGET', '3333333333333333': 'OP_VOPC_0xf3',
                                   '4444444444444444': 'RESTRACK_GBR1'})
chk('cs_req', a['cs_req'], {'1111111111111111': [1, 0, ln['miss1'], 'absent'], '5555555555555555': [1, 1, ln['hit5'], 'not-ready']})
chk('cs_enq / cs_summary / cs_other', (a['cs_enq'], a['cs_summary'], a['cs_other']), (1, 'summary queued=4 done=0', 0))
chk('cfg_in / cfg_out / first', (a['cfg_in'], a['cfg_out'], a['cfg_out_first']), (1, 1, [ln['cfgout'], 'shader CFG build failed: boom outside']))
chk('rel_plt / rel_nonplt / rel_libs', (a['rel_plt'], a['rel_nonplt'], a['rel_libs']), (2, 1, {'Net_v1': [2, 0, 2], 'Foo_v1': [0, 1, 1]}))
chk('late_n / late', (a['late_n'], a['late']), (2, ['L1[LibB_v1][LibB_v1.0][Func]']))
chk('sfn / b9a_n / b9a_first / fatal', (a['sfn'], a['b9a_n'], a['b9a_first'], a['fatal']), (1, 1, 'FixB9a: on', 1))
chk('identity stub_lines == sum(n) + bad + unparsed', a['stub_lines'], sum(s['n'] for s in a['stub']) + a['stub_bad'] + a['stub_unparsed'])
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
