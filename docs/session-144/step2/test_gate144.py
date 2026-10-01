"""test_gate144.py - the fixtures of step2/gate144.py (HPP-332; ROADMAP s122 item 266 (h)) on REAL logs:
  g1  w143_01 (W with the start precache, stopped before "recipes ->") as w144_01      -> STOP by (b)
  g2  w142 (Sky Garden W with precache, held 310 s) as the control w144_00              -> STOP by (b)
  g3  f2c_b (W in the form of item 254 (e), KYTY_PIPELINE_PRECACHE=0) as w144_01        -> PASS
  g4  v143_01 (V) as v144_09                                                             -> PASS
  g5  v143_01 with its "ShaderSeed:" lines cut                                           -> STOP by (b)
  g6  a manifest with one changed sha256 (start and (c)(2))                              -> STOP by (c); unchanged -> PASS
  g7  two W jsons with outcome timeout before GuestOut                                   -> STOP by (g); different keys,
      timeout after GuestOut                                                             -> PASS
  g8  a V score rejected by "V positive control" / "V shipped defaults"                  -> STOP by (e)
  g9  (d): a seal copy with another s143 times sha                                       -> STOP; the real one -> PASS
  g10 a made tag without its GATE row, no start row, the tag before not made             -> STOP
  g11 ascii output under a strict cp1250 console without PYTHONIOENCODING
Work dir C:/kyty/s144/step2/fx_gate (hard links to the real logs; the cut copy of g5 is removed at the end).  Ends ALL OK.
    python test_gate144.py > test_gate144.out.txt
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
sys.path.insert(0, HERE)
import gate144 as G  # noqa: E402

FX = HERE + '/fx_gate'
REF = G.REF
NCHECK = [0]
FAILS = []


def sha(p):
    return G.sha_file(p)


def check(name, cond, info=''):
    NCHECK[0] += 1
    print('%s %s %s' % ('ok  ' if cond else 'FAIL', name, G.asc(info)[:400]))
    if not cond:
        FAILS.append(name)


def fresh(name):
    d = FX + '/' + name
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d + '/runs144')
    os.makedirs(d + '/step2')
    return d


def link(src, dst):
    try:
        os.link(src, dst)
    except OSError:
        shutil.copyfile(src, dst)


def put_tag(root, src_root, src, dst, extra_env=None):
    js = json.load(open('%s/%s.json' % (src_root, src), encoding='utf-8'))
    js['tag'] = dst
    if extra_env:
        js['env'] = dict(js.get('env') or {}, **extra_env)
    json.dump(js, open('%s/%s.json' % (root, dst), 'w', encoding='utf-8'))
    for a in ('log_%s.txt', 'stdout_%s.txt', '%s.stdout.txt'):
        if os.path.isfile(src_root + '/' + a % src):
            link(src_root + '/' + a % src, root + '/' + a % dst)


def synth_w(root, dst, outcome, log_lines=(), std_lines=()):
    json.dump(dict(tag=dst, attempts=[dict(outcome=outcome, level=G.sc144.level_of(dst))], env={}, cmdline=[]),
              open('%s/%s.json' % (root, dst), 'w', encoding='utf-8'))
    open('%s/log_%s.txt' % (root, dst), 'wb').write(b''.join(x + b'\n' for x in log_lines))
    open('%s/stdout_%s.txt' % (root, dst), 'wb').write(b''.join(x + b'\n' for x in std_lines))


def rows(root, *what):
    with open(root + '/step2/times.txt', 'a', encoding='ascii') as f:
        for w in what:
            f.write('2026-10-01T00:00:00Z GATE %s PASS; fixture row\n' % w)


def run(root, *argv):
    t = root + '/step2/times.txt'
    rc = G.main(list(argv) + ['--root', root, '--times', t])
    last = open(t, encoding='ascii').read().splitlines()[-1]
    return rc, last


def reasons(last):
    head = last.split(' | ')[0]
    return head


def main():
    me = os.path.abspath(__file__).replace('\\', '/')
    print('suite test_gate144.py sha256 %s target gate144.py sha256 %s' % (sha(me), sha(HERE + '/gate144.py')))
    if os.path.isdir(FX):
        shutil.rmtree(FX)
    os.makedirs(FX)
    # g1: w143_01 as w144_01
    r = fresh('g1')
    rows(r, 'start', 'w144_01')
    put_tag(r, 'C:/kyty/s143', 'w143_01', 'w144_01', dict(KYTY_PIPELINE_PRECACHE='0'))
    rc, last = run(r, '--before', 'w144_02')
    check('g1 w143_01 as w144_01 -> STOP', rc == 5, last)
    check('g1 reason (b) W w144_01 precache member', '(b) W w144_01: precache member' in last, reasons(last))
    check('g1 the log has 0 "recipes ->" lines and >= 1 ShaderSeed: (the review A)',
          G.count_lines('C:/kyty/s143/log_w143_01.txt', (b'recipes ->', G.SEED)) == {b'recipes ->': 0, G.SEED: 1})
    # g2: w142 as w144_00, before w144_01 (the cache check of (c)(2) given the reference itself)
    r = fresh('g2')
    rows(r, 'start', 'w144_00')
    put_tag(r, 'C:/kyty/s142', 'w142', 'w144_00')
    shutil.copyfile(REF, r + '/runs144/cache_w144_00.before.json')
    rc, last = run(r, '--before', 'w144_01')
    check('g2 w142 as w144_00 -> STOP', rc == 5, last)
    check('g2 reason (b) W w144_00', '(b) W w144_00: precache member' in last, reasons(last))
    check('g2 (c)(2) same manifest passes', '(c)(2)' not in reasons(last), reasons(last))
    # g3: f2c_b as w144_01 -> PASS
    r = fresh('g3')
    rows(r, 'start', 'w144_01')
    put_tag(r, 'C:/kyty/f287/f2c', 'f2c_b', 'w144_01')
    rc, last = run(r, '--before', 'w144_02')
    check('g3 f2c_b as w144_01 -> PASS', rc == 0 and ' GATE w144_02 PASS' in last, last)
    check('g3 detail 0/0 in log and stdout', 'w144_01 ShaderSeed/PipelinePrecache log 0/0 stdout 0/0' in last, last)
    # g4: v143_01 as v144_09 -> PASS
    r = fresh('g4')
    rows(r, 'start', 'v144_09')
    put_tag(r, 'C:/kyty/s143', 'v143_01', 'v144_09')
    shutil.copyfile('C:/kyty/s143/score_v143_01.txt', r + '/score_v144_09.txt')
    rc, last = run(r, '--before', 'w144_09')
    check('g4 v143_01 as v144_09 -> PASS', rc == 0 and ' GATE w144_09 PASS' in last, last)
    # g5: v143_01 with the ShaderSeed: lines cut
    r = fresh('g5')
    rows(r, 'start', 'v144_09')
    put_tag(r, 'C:/kyty/s143', 'v143_01', 'v144_09')
    os.remove(r + '/log_v144_09.txt')
    cut = 0
    with open('C:/kyty/s143/log_v143_01.txt', 'rb') as fi, open(r + '/log_v144_09.txt', 'wb') as fo:
        for line in fi:
            if G.SEED in line:
                cut += 1
                continue
            fo.write(line)
    shutil.copyfile('C:/kyty/s143/score_v143_01.txt', r + '/score_v144_09.txt')
    rc, last = run(r, '--before', 'w144_09')
    check('g5 %d ShaderSeed: line(s) cut' % cut, cut >= 1, str(cut))
    check('g5 V without ShaderSeed: -> STOP (b)', rc == 5 and '(b) V v144_09: 0 ShaderSeed: lines' in last, reasons(last))
    os.remove(r + '/log_v144_09.txt')
    # g6: manifests
    r = fresh('g6')
    ref = json.load(open(REF, encoding='utf-8'))
    same = r + '/same.json'
    json.dump(ref, open(same, 'w', encoding='utf-8'))
    ch = json.loads(json.dumps(ref))
    i = [k for k, x in enumerate(ch['files']) if x[0] == 'shader' and x[1] == 'pipelines.bin'][0]
    ch['files'][i][4] = '0' * 64
    chp = r + '/changed.json'
    json.dump(ch, open(chp, 'w', encoding='utf-8'))
    rc, last = run(r, '--start', '--live-manifest', same)
    check('g6 start with the reference manifest -> PASS', rc == 0 and ' GATE start PASS' in last, last)
    rc, last = run(r, '--start', '--live-manifest', chp)
    check('g6 start with one changed sha -> STOP (c)', rc == 5 and '(c) shader differs from the s143 end: +0 -0 changed 1 '
          '(pipelines.bin)' in last, reasons(last))
    mt = json.loads(json.dumps(ref))
    mt['files'][i][3] = 1
    mtp = r + '/mtime.json'
    json.dump(mt, open(mtp, 'w', encoding='utf-8'))
    rc, last = run(r, '--start', '--live-manifest', mtp)
    check('g6 another mtime only -> PASS (content, not mtime)', rc == 0, reasons(last))
    gl = json.loads(json.dumps(ref))
    j = [k for k, x in enumerate(gl['files']) if x[0] == 'glcache'][0]
    del gl['files'][j]
    glp = r + '/gl.json'
    json.dump(gl, open(glp, 'w', encoding='utf-8'))
    rc, last = run(r, '--start', '--live-manifest', glp)
    check('g6 a glcache file missing -> STOP (c) glcache', rc == 5 and '(c) glcache differs' in last, reasons(last))
    r2 = fresh('g6b')
    rows(r2, 'start', 'w144_00')
    synth_w(r2, 'w144_00', 'ok')
    shutil.copyfile(chp, r2 + '/runs144/cache_w144_00.before.json')
    rc, last = run(r2, '--before', 'w144_01')
    check('g6 (c)(2) cache_w144_00.before with one changed sha -> STOP', rc == 5 and '(c)(2) shader differs' in last,
          reasons(last))
    os.remove(r2 + '/runs144/cache_w144_00.before.json')
    rc, last = run(r2, '--before', 'w144_01')
    check('g6 (c)(2) manifest missing -> STOP', rc == 5 and '(c)(2) runs144/cache_w144_00.before.json missing' in last,
          reasons(last))
    # g7: W keys
    r = fresh('g7')
    rows(r, 'start', 'w144_00', 'w144_01')
    synth_w(r, 'w144_00', 'timeout', [b'some line'], [b'x'])
    synth_w(r, 'w144_01', 'timeout', [b'other line'], [b'y'])
    shutil.copyfile(REF, r + '/runs144/cache_w144_00.before.json')
    rc, last = run(r, '--before', 'w144_02')
    check('g7 two W timeout before GuestOut -> STOP (g)', rc == 5 and '(g) two W in a row with the key attempt:timeout: '
          'w144_00,w144_01' in last, reasons(last))
    synth_w(r, 'w144_01', 'exited', [b'other line'], [b'y'])
    rc, last = run(r, '--before', 'w144_02')
    check('g7 timeout then exited (different keys) -> PASS', rc == 0, last)
    synth_w(r, 'w144_01', 'timeout', [b'[1][00:00:01] GuestOut: hello'], [b'y'])
    rc, last = run(r, '--before', 'w144_02')
    check('g7 timeout after GuestOut has no key -> PASS', rc == 0 and 'timeout after GuestOut' in last, last)
    synth_w(r, 'w144_01', 'timeout', [b'ShaderSeed: compatibility=x'], [b'y'])
    rc, last = run(r, '--before', 'w144_02')
    check('g7 synthetic W with a ShaderSeed: line -> STOP (b) too', rc == 5 and '(b) W w144_01' in last, reasons(last))
    # g8: V admission
    r = fresh('g8')
    rows(r, 'start', 'v144_09')
    put_tag(r, 'C:/kyty/s143', 'v143_01', 'v144_09')
    for k in ('V positive control', 'V shipped defaults'):
        open(r + '/score_v144_09.txt', 'w', encoding='ascii').write(
            'TAG v144_09 ...\n  admission: FAIL %s: x (log 0)\n' % k)
        rc, last = run(r, '--before', 'w144_09')
        check('g8 %s -> STOP (e)' % k, rc == 5 and '(e) V v144_09 rejected by a form member: %s' % k in last, reasons(last))
    open(r + '/score_v144_09.txt', 'w', encoding='ascii').write('  admission: FAIL video KYTY_REC (x)\n')
    rc, last = run(r, '--before', 'w144_09')
    check('g8 another admission failure -> not a form stop', rc == 0, reasons(last))
    os.remove(r + '/score_v144_09.txt')
    rc, last = run(r, '--before', 'w144_09')
    check('g8 score missing -> STOP (e)', rc == 5 and 'score_v144_09.txt missing' in last, reasons(last))
    # g9: (d)
    r = fresh('g9')
    pred = open(G.PRED, encoding='utf-8').read()
    real = G.seal_sha(G.PRED, 'C:/kyty/s143/step2/times.txt')
    open(r + '/pred.md', 'w', encoding='utf-8').write(pred.replace(real, 'f' * 64))
    rc, last = run(r, '--recheck143', '--pred', r + '/pred.md')
    check('g9 seal copy with another s143 times sha -> STOP (d)', rc == 5 and '(d) s143/step2/times.txt sha' in last,
          reasons(last))
    rc, last = run(r, '--recheck143')
    check('g9 the real s143 files -> PASS', rc == 0 and ' GATE recheck143 PASS' in last, last)
    # g10: rows
    r = fresh('g10')
    synth_w(r, 'w144_00', 'ok')
    shutil.copyfile(REF, r + '/runs144/cache_w144_00.before.json')
    rc, last = run(r, '--before', 'w144_01')
    check('g10 no start row and an ungated call -> STOP', rc == 5 and 'no "GATE start PASS"' in last
          and 'made tag w144_00 has no "GATE w144_00 PASS"' in last, reasons(last))
    rows(r, 'start', 'w144_00')
    rc, last = run(r, '--before', 'w144_02')
    check('g10 the tag before not made -> STOP', rc == 5 and 'the tag w144_01 before w144_02 was not made' in last,
          reasons(last))
    rc, last = run(r, '--before', 'w144_01')
    check('g10 clean control -> PASS', rc == 0, last)
    rc, last = run(r, '--before', 'x144_99')
    check('g10 unknown tag -> STOP', rc == 5, reasons(last))
    # g11: ascii under strict cp1250
    env = dict(os.environ)
    env.pop('PYTHONIOENCODING', None)
    env.pop('PYTHONUTF8', None)
    p = subprocess.run([sys.executable, HERE + '/gate144.py', '--recheck143', '--root', r, '--times',
                        r + '/step2/times.txt'], capture_output=True, env=env, timeout=300)
    try:
        p.stdout.decode('cp1250', 'strict')
        dec = True
    except UnicodeDecodeError:
        dec = False
    check('g11 subprocess rc 0, stdout strict cp1250 and ascii, no stderr', p.returncode == 0 and dec
          and all(b < 128 for b in p.stdout) and not p.stderr, p.stderr.decode('ascii', 'replace')[:200])
    check('g11 the times file is ascii', all(b < 128 for b in open(r + '/step2/times.txt', 'rb').read()))
    print('checks: %d / %s' % (NCHECK[0], 'ALL OK' if not FAILS else 'FAILED %d: %s' % (len(FAILS), ', '.join(FAILS))))
    if not FAILS:
        print('ALL OK')
    return 0 if not FAILS else 1


if __name__ == '__main__':
    sys.exit(main())
