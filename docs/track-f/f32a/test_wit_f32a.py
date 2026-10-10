# Fixtures for wit_f32a.py (F32a, HPP-733): synthetic log (plain LF, plain CRLF, .xz; last line without newline); last line ALL OK.
import os, sys, json, lzma, hashlib, tempfile, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, 'wit_f32a.py')
ok = True


def check(name, cond):
    global ok
    print(('OK   ' if cond else 'FAIL ') + name)
    ok &= bool(cond)


L = [
    'Build',
    'CsPretranslate: skipped hash=433e4cede34ca4c3 reason=X.cpp:44 shader CFG build failed: unsupported family=VOPC opcode=0xf3 raw=[1]',
    'CsPretranslate: skipped hash=AAAA000000000001 reason=R.cpp:1 shader resource tracking: something',
    'CsPretranslate: skipped hash=aaaa000000000002 reason=T.h:2 speculative translation budget exceeded',
    'CsPretranslate: miss hash=433e4cede34ca4c3 reason=not-ready',
    'CsPretranslate: hit hash=bbbb000000000003 us=5',
    'shader CFG build failed: outside the pretranslate thread',
    '	 len   = 64',
    '	 len   = 0x0000000000000040',
    '\tRead 0 bytes from: x',
    'Controller 3: removed',
    '[Vulkan][E] VUID-vkCmdDraw-None-06479 something',
    'Patch tls at addr: [0000000906479641]',
    'MainTaskLate: us=1200000 site=x',
    'MainTaskLate: us=999999 site=x',
    'Event: quit',
    '--- Fatal Error ---',
    'plain line',
]
tmp = tempfile.mkdtemp(prefix='f32a_wit_').replace(chr(92), '/')
paths = []
for i, (nl, xz) in enumerate([(chr(10), False), (chr(13) + chr(10), False), (chr(10), True)]):
    data = nl.join(L).encode()  # last line without newline
    p = tmp + '/log_%d.txt' % i + ('.xz' if xz else '')
    if xz:
        with lzma.open(p, 'wb') as o:
            o.write(data)
    else:
        open(p, 'wb').write(data)
    paths.append(p)
env = dict(os.environ, F32A_OUT=tmp + '/out', F32A_LOCK=tmp + '/LOCK', F32A_STOP=tmp + '/STOP', PYTHONIOENCODING='utf-8')
res = []
for p in paths:
    r = subprocess.run([sys.executable, S, 'one', p], env=env, capture_output=True, text=True, encoding='utf-8')
    check('one rc 0 ' + os.path.basename(p), r.returncode == 0)
    res.append(json.load(open('%s/out/wit/%s.json' % (tmp, hashlib.md5(p.encode('utf-8')).hexdigest()), encoding='utf-8')))
for i, r in enumerate(res):
    t = '[%d] ' % i
    check(t + 'skipped 3 with classes', r['skipped'] == {'433e4cede34ca4c3': 'op:VOPC:0xf3', 'aaaa000000000001': 'resource_tracking',
                                                       'aaaa000000000002': 'budget'})
    check(t + 'take miss+hit', r['take'] == {'433e4cede34ca4c3': 1, 'bbbb000000000003': 1} and r['take_lines'] == 2)
    check(t + 'cfg outside 1 (inside not counted)', len(r['cfg_out']) == 1 and r['cfg_out'][0].startswith('7:'))
    check(t + 'sock 1 (decimal len only) line 8', r['sock'] == 1 and r['sock_ex'].startswith('8:'))
    check(t + 'read0 1', r['read0'] == 1)
    check(t + 'ctl removed 1', r['ctl_removed'] == 1)
    check(t + 'vuid 06479 1', r['vuid06479'] == 1)
    check(t + 'late >= 1 s only 1', r['late_ge1s'] == 1)
    check(t + 'quit 1', r['quit'] == 1)
    check(t + 'fatal 1 line 15', r['fatal'] == 1 and r['fatal_ex'].startswith('17:'))
    check(t + 'lines 18', r['lines'] == 18)
# lock gate
open(tmp + '/LOCK', 'w').close()
r = subprocess.run([sys.executable, S, 'one', paths[0]], env=env, capture_output=True, text=True)
check('lock -> exit 3', r.returncode == 3)
shutil.rmtree(tmp, ignore_errors=True)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
