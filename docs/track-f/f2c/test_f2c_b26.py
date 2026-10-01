"""Fixtures of f2c_b26.py (F2c, HPP-310): each member of the reading and each edge. Output ASCII; last line ALL OK."""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f2c_b26 as F  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f2c_b26.py sha256 %s target f2c_b26.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                        sha(os.path.join(HERE, 'f2c_b26.py'))))
FX = os.path.join(HERE, 'fx')
os.makedirs(FX, exist_ok=True)
H96, H5 = F.load_hashes()
ok = True
n = 0


def check(name, cond, detail=''):
    global ok, n
    n += 1
    if not cond:
        ok = False
    print('%s %s %s' % ('ok  ' if cond else 'FAIL', name, detail))


CFG = (r'CsPretranslate: skipped hash=%s reason=C:\kyty\KytyPS5\src\graphics\shader\recompiler\frontend\cfg\ShaderCFG.cpp:44 '
       r'shader CFG build failed: unsupported decoded instruction in CFG at pc 0x%08x: 0x%08x: unsupported family=%s '
       r'opcode=%s raw=[0x7dc60004] reason=%s opcode is not implemented')
RT = (r'CsPretranslate: skipped hash=%s reason=C:\kyty\KytyPS5\src\graphics\shader\recompiler\ir\passes\ResourceTracking.cpp:173 '
      r'shader resource tracking: hash=0x%s stage=compute pc=0x%08x GetBufferResource dword 1 is not a valid runtime value')
READY = 'CsPretranslate: ready hash=%s us=312 kb=40 ready_kb=40'
ROOT = r'Shader translation cache: _ShaderCache\PPSA21564'
VAR = r'Shader translation cache: _ShaderCache\PPSA21564\variant_fixb26'
PHI = 'descriptor word at pc 0x000001a0 comes from a uniform branch, lowered its phi to a host-evaluated select'
B = '57c4d5848e02ecdc'
VOPC4 = sorted(h for h in H5 if H5[h][0] == 'VOPC')
A96 = sorted(H96)


def cfg(h, fam, op, pc):
    return CFG % (h, pc, pc, fam, op, fam)


def base96():
    return [cfg(h, 'SOP1', '0x21', 0x74) for h in A96]


def log0():
    L = [ROOT] + base96() + [cfg(B, 'SOP1', '0x0c', 0x168)]
    L += [cfg(h, 'VOPC', '0xe3', H5[h][2]) for h in VOPC4]
    return L


def log1_pred():
    L = [VAR] + base96() + [RT % (B, B, 0x1a0), PHI, PHI, PHI]
    pcs = {'433e4cede34ca4c3': 0xc0, '4468d53059c03cba': 0x294, '7bb50479b3a32c7c': 0x324, 'f8e350383290ff7b': 0xfc}
    L += [cfg(h, 'VOPC', '0xf3', pcs[h]) for h in VOPC4]
    return L


def log1_ideal():
    return [VAR] + base96() + [READY % h for h in sorted(H5)]


def run(name, lines, fix, crlf=False, filler=0):
    p = os.path.join(FX, name + '.txt')
    sep = '\r\n' if crlf else '\n'
    with open(p, 'wb') as f:
        f.write(('FrameTrace: n=1 dt_us=16000 draws=5' + sep).encode())
        for ln in lines:
            if ln == 'FILLER':
                f.write(('x' * 100 + sep).encode() * filler)
            else:
                f.write((ln + sep).encode())
    res = F.scan(p, H96, H5)
    return res, F.judge(res, fix, H5)


# tables
check('tsv: 96 hashes of SOP1 0x21', len(H96) == 96, len(H96))
check('tsv: 5 B26b hashes (1 SOP1 0x0c + 4 VOPC 0xe3)', len(H5) == 5 and len(VOPC4) == 4 and H5[B] == ('SOP1', '0x0c', 0x168))
check('tsv: VOPC fix places 0x24/0x1d4/0x264/0x24', sorted(H5[h][2] for h in VOPC4) == [0x24, 0x24, 0x1d4, 0x264])

# (v) control =0
r, o = run('c0', log0(), '0')
check('=0 baseline profile 96/1/4, 0xf3 0', (o['n21'], o['n0c'], o['ne3'], o['nf3']) == (96, 1, 4, 0))
check('=0 baseline knob 0 from the root cache line', o['knob'] == '0' and o['knob_ok'])
check('=0 baseline -> CONTROL RETURNS', o['verdict_letter'] == 'CONTROL RETURNS', o['verdict_letter'])
check('=0 baseline letter count 0 of 5', o['letter5'] == 0 and o['variant5'] == 0)
r, o = run('c0x', log0() + [cfg('1111111111111111', 'VOPC', '0xf3', 0x10)], '0')
check('=0 with an extra 0xf3 line -> CONTROL FAILS', o['verdict_letter'] == 'CONTROL FAILS')
r, o = run('c0y', log0()[:-1], '0')
check('=0 with 3 x 0xe3 -> CONTROL FAILS', o['ne3'] == 3 and o['verdict_letter'] == 'CONTROL FAILS')
r, o = run('c0z', log0()[:50] + log0()[51:], '0')
check('=0 with 95 x 0x21 -> CONTROL FAILS', o['n21'] == 95 and o['verdict_letter'] == 'CONTROL FAILS')
r, o = run('c0w', log0() + [cfg('2222222222222222', 'VOP3', '0x1ff', 0x10)], '0')
check('=0 with another family/opcode -> CONTROL FAILS, listed', o['verdict_letter'] == 'CONTROL FAILS' and o['other_ops'])

# (a) fix =1
r, o = run('c1i', log1_ideal(), '1')
check('=1 ideal: 5 ready -> letter 5 of 5 PASS', o['letter5'] == 5 and o['verdict_letter'] == 'PASS', o['verdict_letter'])
check('=1 ideal: knob 1 from variant_fixb26', o['knob'] == '1' and o['knob_ok'])
r, o = run('c1p', log1_pred(), '1')
check('=1 predicted: profile 96/0/0, 0xf3 4 (pair, not family)', (o['n21'], o['n0c'], o['ne3'], o['nf3']) == (96, 0, 0, 4))
check('=1 predicted: profile ok', o['profile_ok'])
check('=1 predicted: letter 4 of 5 (ResourceTracking is not an opcode) -> FAIL', o['letter5'] == 4 and o['verdict_letter'] == 'FAIL')
check('=1 predicted: RC1 reviewer variant 5 of 5 -> PASS', o['variant5'] == 5 and o['verdict_variant'] == 'PASS')
check('=1 predicted: 57c4 skip mechanism and pc printed', 'ResourceTracking.cpp:173 pc 0x1a0' in o['per5'][B]['state'], o['per5'][B]['state'])
check('=1 predicted: phi lines counted 3, not a marker', o['phi'] == 3 and o['deaths'] == 0)
L = log1_pred()
L[-1] = cfg(VOPC4[-1], 'VOPC', '0xe3', H5[VOPC4[-1]][2])
r, o = run('c1e', L, '1')
check('=1 with a remaining 0xe3 -> profile fail, letter 3 (57c4 and that hash)', not o['profile_ok'] and o['letter5'] == 3
      and o['ne3'] == 1 and o['verdict_letter'] == 'FAIL', (o['letter5'], o['ne3']))
L = log1_ideal()
L[0] = ROOT
r, o = run('c1k', L, '1')
check('=1 run with the root cache line -> INVALID RUN (knob)', o['verdict_letter'].startswith('INVALID RUN'), o['verdict_letter'])
r, o = run('c1k2', log1_ideal() + [ROOT], '1')
check('two cache lines -> knob None -> INVALID RUN', o['knob'] is None and o['verdict_letter'].startswith('INVALID RUN'))
r, o = run('c1k3', [r'Shader translation cache: _ShaderCache\PPSA21564\variant_bvhcap'] + log1_ideal()[1:], '1')
check('other variant directory -> knob None', o['knob'] is None)
r, o = run('c0k', [VAR] + log0()[1:], '0')
check('=0 run with variant_fixb26 line -> INVALID RUN', o['verdict_letter'].startswith('INVALID RUN'))

# one line per hash
r, o = run('c1d', log1_ideal() + [cfg(B, 'SOP1', '0x0c', 0x168)], '1')
check('hash with ready + skipped -> NOT COUNTED', o['per5'][B]['state'] == 'NOT COUNTED' and o['letter5'] == 4)
L = [x for x in log1_ideal() if B not in x]
r, o = run('c1n', L, '1')
check('hash without a line -> NOT COUNTED (no false success)', o['per5'][B]['state'] == 'NOT COUNTED' and o['letter5'] == 4)
r, o = run('c1rr', log1_ideal() + [READY % B], '1')
check('hash with two ready lines -> NOT COUNTED', o['per5'][B]['state'] == 'NOT COUNTED')

# variant edges
L = log1_pred()
i = [k for k, x in enumerate(L) if VOPC4[1] in x][0]
L[i] = cfg(VOPC4[1], 'VOPC', '0xf3', H5[VOPC4[1]][2])
r, o = run('c1v', L, '1')
check('0xf3 skip at pc == fix place: letter yes, variant no', o['per5'][VOPC4[1]]['letter'] and not o['per5'][VOPC4[1]]['variant'])
L = [VAR] + base96() + [(RT % (B, B, 0x1a0)).replace('pc=0x000001a0 ', '')] + log1_pred()[98:]
r, o = run('c1np', L, '1')
check('other mechanism without pc: letter no, variant no', not o['per5'][B]['letter'] and not o['per5'][B]['variant'])
L = [VAR] + base96() + [RT % (B, B, 0x100)] + log1_pred()[101:]
r, o = run('c1lo', L, '1')
check('other mechanism at pc < fix place: variant no', not o['per5'][B]['variant'], o['per5'][B]['state'])
L = [VAR] + base96() + [cfg(B, 'SOP1', '0x0c', 0x168)] + log1_pred()[101:]
r, o = run('c1same', L, '1')
check('skip with the fixed opcode itself: letter no, variant no', not o['per5'][B]['letter'] and not o['per5'][B]['variant'])

# (g) B26a reopen
r, o = run('r0', log0(), '0')
check('no reopen on the baseline', not o['reopen_any'] and o['reopen'] == dict(mh=0, cfg_outside=0, translator_deaths=0))
r, o = run('r1', log0() + ['CsPretranslate: miss hash=%s reason=not ready' % A96[0]], '0')
check('miss of a 96 hash -> REOPEN', o['reopen']['mh'] == 1 and o['reopen_any'])
r, o = run('r2', log0() + ['CsPretranslate: hit hash=%s saved_us=10 hits=1' % A96[5]], '0')
check('hit of a 96 hash -> REOPEN', o['reopen']['mh'] == 1)
r, o = run('r3', log0() + ['CsPretranslate: miss hash=%s reason=not ready' % B], '0')
check('miss of a non-96 hash -> no reopen', o['reopen']['mh'] == 0)
r, o = run('r4', log0() + ['Pipeline: shader CFG build failed: unsupported decoded instruction at pc 0x74'], '0')
check('CFG failed outside CsPretranslate -> counted', o['reopen']['cfg_outside'] == 1 and o['reopen_any'])
r, o = run('r5', log0() + ['--- Fatal Error ---'], '0')
check('death right after translator lines -> translator death 1', o['reopen']['translator_deaths'] == 1 and o['deaths'] == 1)
r, o = run('r6', log0() + ['FILLER', '--- Fatal Error ---'], '0', filler=100)
check('death 10 KB after the last translator line -> death 1, translator 0', o['deaths'] == 1 and o['reopen']['translator_deaths'] == 0)

# form p.254(e): W without the precache line, V with it
PRE = ('PipelinePrecache: 1604 recipes -> 1500 graphics + 90 compute pipelines queued, 14 skipped, 300 sources loaded, '
       'complete, 812 ms (scratch: 3 pipelines, max 64 dwords/thread)')
r, o = run('fw0', log1_ideal(), '1')
check('form: no --arm -> not judged, verdict unchanged', o['form_ok'] is None and o['verdict_letter'] == 'PASS')
r, o = run('fw1', log1_ideal(), '1')
o = F.judge(r, '1', H5, 'W')
check('form W: 0 precache lines -> ok, PASS kept', o['form_ok'] is True and o['verdict_letter'] == 'PASS', o['verdict_letter'])
r, o = run('fw2', [PRE] + log1_ideal(), '1')
o = F.judge(r, '1', H5, 'W')
check('form W: precache line present -> FAIL (form)', o['form_ok'] is False and o['verdict_letter'].startswith('FAIL (form')
      and o['verdict_variant'].startswith('FAIL (form') and o['precache_lines'] == 1, o['verdict_letter'])
o = F.judge(r, '1', H5, 'V')
check('form V: precache line present -> ok, PASS', o['form_ok'] is True and o['verdict_letter'] == 'PASS')
r, o = run('fv0', log0(), '0')
o = F.judge(r, '0', H5, 'V')
check('form V: no precache line -> FAIL (form) also on control =0', o['form_ok'] is False and o['verdict_letter'].startswith('FAIL (form'))
r, o = run('fv1', [PRE, PRE] + log0(), '0')
o = F.judge(r, '0', H5, 'V')
check('form V: two precache lines -> ok, CONTROL RETURNS', o['form_ok'] is True and o['precache_lines'] == 2
      and o['verdict_letter'] == 'CONTROL RETURNS')
r, o = run('fw3', ['PipelinePrecache: disabled (recipes file absent)'] + log1_ideal(), '1')
o = F.judge(r, '1', H5, 'W')
check('form W: other PipelinePrecache line (no "N recipes ->") is not the summary -> ok', o['form_ok'] is True
      and o['precache_lines'] == 0)
r, o = run('fw4', [PRE] + log1_ideal()[1:] + [ROOT], '1')
o = F.judge(r, '1', H5, 'W')
check('form W: knob invalid wins over form', o['verdict_letter'].startswith('INVALID RUN'))
p = subprocess.run([sys.executable, os.path.join(HERE, 'f2c_b26.py'), os.path.join(FX, 'fw2.txt'), '1', '--arm', 'W'],
                   capture_output=True)
check('main --arm W on a log with the precache line -> FAIL (form) printed', p.returncode == 0
      and b'verdict letter: FAIL (form' in p.stdout, p.returncode)
p = subprocess.run([sys.executable, os.path.join(HERE, 'f2c_b26.py'), os.path.join(FX, 'fw2.txt'), '1', '--arm', 'X'],
                   capture_output=True)
check('main --arm X -> rc 2', p.returncode == 2)
p = subprocess.run([sys.executable, os.path.join(HERE, 'f2c_b26.py'), os.path.join(FX, 'fw2.txt'), '1', '--arm'],
                   capture_output=True)
check('main --arm without value -> rc 2', p.returncode == 2)

# reading form
r, o = run('crlf', log1_pred(), '1', crlf=True)
check('CRLF log reads the same', (o['n21'], o['nf3'], o['letter5'], o['variant5'], o['knob']) == (96, 4, 4, 5, '1'))
old = F.CHUNK
F.CHUNK = 97
r2, o2 = run('chunk', log1_pred() + ['FILLER'] + log1_pred()[1:2], '1', filler=3)
F.CHUNK = old
r3, o3 = run('chunk', log1_pred() + ['FILLER'] + log1_pred()[1:2], '1', filler=3)
check('chunk boundary 97 B = 64 MB reading', (o2['n21'], o2['nf3'], o2['per5'], r2['sha256']) == (o3['n21'], o3['nf3'], o3['per5'], r3['sha256']))
check('97 x 0x21 lines counted (dup line)', o3['n21'] == 97 and not o3['profile_ok'])

# cp1250 strict output without PYTHONIOENCODING
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
p = subprocess.run([sys.executable, os.path.join(HERE, 'f2c_b26.py'), os.path.join(FX, 'c1p.txt'), '1'], capture_output=True, env=env)
try:
    txt = p.stdout.decode('cp1250', errors='strict')
    good = p.returncode == 0 and 'letter 4 of 5' in txt and txt.isascii()
except UnicodeDecodeError:
    good = False
check('main output: rc 0, ASCII, strict cp1250, no PYTHONIOENCODING', good, p.returncode)
p = subprocess.run([sys.executable, os.path.join(HERE, 'f2c_b26.py'), os.path.join(FX, 'c1p.txt'), '2'], capture_output=True, env=env)
check('main: bad knob value -> rc 2', p.returncode == 2)

print('checks %d' % n)
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
