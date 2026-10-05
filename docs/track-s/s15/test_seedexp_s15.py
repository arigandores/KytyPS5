"""Offline fixtures of seedexp_s15.py - S15a (HPP-601): the port of s13/test_seedexp_s13.py; the S13 text follows.
Port header: Offline fixtures of seedexp_s13.py (track S, link S13a, HPP-498; ROADMAP "SESSION 122" item 408 (l), (z)) WITHOUT the game:
a fixture link directory with a post copy cat/k_19 made by the manifest code of cachex_s.py, the json and the log of k_19, a
seal in force (the real sc_s15.py with its seal moved into the fixture), a stand-in of tools/shader_seed.py (copies the stage,
writes manifest.json and compatibility.txt from the log line) and of recipes_s7.parse; the real cachex_s.py verify and the real
offline install check (signature + XXH3).  Cases: the lock refusal before any write; the seal PENDING -> rc 6; the post copy
other than app_post_copy, or its files changed -> rc 1; no variant directory -> rc 1; the log of another binary, with a patch,
on another signature -> rc 1; an existing output -> rc 1; the tool refusing -> rc 6; a clean export -> EXPORT: OK with the lines
sc_s15.export_state reads (source arm, compatibility.txt, removed duplicates, SEEDS manifest) and export_state OK on it; a
compatibility line other than the log -> CHECK FAILED; a shader file with a bad checksum -> CHECK FAILED; duplicate keys counted;
a tool that rewrites pipelines.bin -> "removed duplicates (F17): UNDETERMINED".  The first output line names this suite and the
export script by sha256; the output ends with ALL OK.
    python C:/kyty/s288/s15/test_seedexp_s15.py
"""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import struct
import sys
from pathlib import Path

import xxhash

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'seedexp_s15.py')
print('suite test_seedexp_s15.py sha256 %s target seedexp_s15.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
NL = chr(10)
_s = importlib.util.spec_from_file_location('seedexp_under_test', SRC)
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)
_c = importlib.util.spec_from_file_location('cachex_fx_e', 'C:/kyty/s288/cachex_s.py')
CX = importlib.util.module_from_spec(_c)
_c.loader.exec_module(CX)
SC13 = os.path.join(HERE, 'sc_s15.py').replace(chr(92), '/')
BASE = Path('C:/kyty/s288/s15/fx_seedexp_s15')
N = [0]
INST = 'ef' * 32
SIG = 'KytySC3:feed:robust:fixf10'
VAR = 'variant_q'
LAYOUT = '10288:376'


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def shader(payload):
    sigb = (SIG + NL).encode('ascii')
    return sigb + struct.pack('<Q', xxhash.xxh3_64_intdigest(payload)) + payload


def recipes_bin(n):
    body = (SIG + NL + LAYOUT).encode('ascii')
    return b'KytyPR1' + NL.encode() + struct.pack('<I', len(body)) + body + bytes([n])


def setup(seal_line=None, recs=2, dup=0):
    shutil.rmtree(BASE, ignore_errors=True)
    link = BASE / 's15'
    v = link / 'cat' / 'k_19' / 'ShaderCache_PPSA21564' / VAR
    v.mkdir(parents=True)
    (v / 'vs_0001.bin').write_bytes(shader(b'vertex'))
    (v / 'ps_0002.bin').write_bytes(shader(b'pixel'))
    (v / 'pipelines.bin').write_bytes(recipes_bin(recs))
    (link / 'cat' / 'k_19' / 'PipelineCache').mkdir()
    (link / 'cat' / 'k_19' / 'PipelineCache' / 'PPSA21564.bin').write_bytes(b'driver blob')
    text, msha = CX.app_manifest((link / 'cat' / 'k_19').as_posix())
    (link / 'cat' / 'k_19' / 'MANIFEST.txt').write_bytes(text.encode('ascii'))
    (link / 'runs_s').mkdir()
    (link / 'runs_s' / 'k_19.cache.json').write_text(json.dumps(dict(app_post_copy=dict(sha=msha))))
    (link / 'k_19.json').write_text(json.dumps(dict(binary_sha256=INST, env=dict(KYTY_GUEST_ARGS='-lvl x'))))
    (link / 'log_k_19.txt').write_text('a' + NL + 'ShaderSeed: compatibility=KytySeed1:PPSA21564:1:%s::%s:000010de' % (SIG, LAYOUT) +
                                       NL, encoding='ascii')
    (BASE / 'pred').mkdir()
    (BASE / 'pred' / '09_s.md').write_text((seal_line or 'installed: %s %s %s' % (INST, SIG, VAR)) + NL, encoding='ascii')
    (BASE / 'sc13.py').write_text(
        "import importlib.util\ns = importlib.util.spec_from_file_location('sc13r', %r)\nm = importlib.util.module_from_spec(s)\n"
        "s.loader.exec_module(m)\nm.SEAL_BASE = %r\nm.SEAL_B = %r\ncurrent_seal = m.current_seal\nseal_installed = m.seal_installed\n"
        % (SC13, (BASE / 'pred' / '09_s.md').as_posix(), (BASE / 'pred' / '09b_s.md').as_posix()), encoding='ascii')
    (BASE / 'recipes.py').write_text(
        "def parse(path):\n    d = open(path, 'rb').read()\n    n = d[-1]\n"
        "    recs = [dict(kind=1, i=i, ren=b'r', vin=b'v', sta=b's', vk=(1, 1), vi=0, pk=(2, 2), pi=0) for i in range(n)]\n"
        "    for i in range(%d):\n        recs[i]['ren'] = b'r%%d' %% i\n"
        "    return dict(count=n, at_end=True), recs\n"
        "def path_name(k):\n    return {1: 'vs_0001.bin', 2: 'ps_0002.bin'}[k[0]]\n" % (recs - dup), encoding='ascii')
    return link


def tool(mode=''):
    p = BASE / ('tool%s.py' % mode)
    p.write_text(
        "import json, os, shutil, sys\na = sys.argv\nst, lg, out = a[a.index('--cache') + 1], a[a.index('--log') + 1], "
        "a[a.index('--output') + 1]\n"
        "if %r == 'refuse':\n    print('refused'); sys.exit(2)\n"
        "os.makedirs(out)\nfiles = sorted(os.listdir(st))\n"
        "for f in files:\n    shutil.copy2(os.path.join(st, f), os.path.join(out, f))\n"
        "if %r == 'rewrite':\n    open(os.path.join(out, 'pipelines.bin'), 'ab').write(b'#')\n"
        "line = [x for x in open(lg) if x.startswith('ShaderSeed: compatibility=')][0].split('=', 1)[1].strip()\n"
        "if %r == 'compat':\n    line = line + 'X'\n"
        "open(os.path.join(out, 'compatibility.txt'), 'w').write(line + chr(10))\n"
        "sh = [f for f in files if f != 'pipelines.bin']\n"
        "json.dump(dict(files=files, shaders=len(sh), recipes=open(os.path.join(st, 'pipelines.bin'), 'rb').read()[-1]), "
        "open(os.path.join(out, 'manifest.json'), 'w'))\nprint('Exported')\n" % (mode, mode, mode), encoding='ascii')
    return p.as_posix()


def run(link, tl, **kw):
    buf = []
    rc = E.main(link=link.as_posix(), tool=tl, sc13=(BASE / 'sc13.py').as_posix(), recipes=(BASE / 'recipes.py').as_posix(),
                pr=buf.append, **kw)
    return rc, buf


ok = True
ok &= case('X1 seedexp_s15.py is ASCII only', all(b < 128 for b in Path(SRC).read_bytes()))
link = setup()
FXLOCK = (BASE / 'LOCK').as_posix()
E.LOCK = FXLOCK
Path(FXLOCK).write_text('x')
rc, out = run(link, tool())
ok &= case('X2 the lock -> rc 5 before any write (no stage, no output)', rc == 5 and not (link / 'stage').exists() and
           not (link / 'seeds').exists())
Path(FXLOCK).unlink()
rc, out = run(link, tool())
ok &= case('X3 a clean export -> rc 0, EXPORT: OK, the lines export_state reads', rc == 0 and out[-1] == 'EXPORT: OK' and
           any(x.startswith('source arm k_19 app_post_copy ') for x in out) and
           any(x.startswith('compatibility.txt: KytySeed1:') for x in out) and
           any(x.startswith('removed duplicates (F17): 0 ') for x in out) and
           any(x.startswith('SEEDS manifest %s/seeds_manifest.txt files 5 sha256 ' % link.as_posix()) for x in out) and
           any('R_DUP_GFX 0, R_DUP_CS 0' in x for x in out))
(link / 'seedexp_s15.out.txt').write_text(NL.join(out) + NL, encoding='ascii')
_t = importlib.util.spec_from_file_location('sc13x', SC13)
S = importlib.util.module_from_spec(_t)
_t.loader.exec_module(S)
good, rows, d = S.export_state(link.as_posix(), (link / 'seedexp_s15.out.txt').as_posix(), (link / 'seeds_manifest.txt').as_posix(),
                               (link / 'seeds').as_posix())
ok &= case('X4 sc_s15.export_state reads the clean export as OK (the source, the manifest, the live catalogue)', good and
           d['dup'] == '0' and d['compat'].startswith('KytySeed1:'))
rc, out = run(link, tool())
ok &= case('X5 a second export (the output exists) -> rc 1', rc == 1 and any('the export runs once' in x for x in out))
link = setup(seal_line='installed: PENDING')
rc, out = run(link, tool())
ok &= case('X6 the seal PENDING -> rc 6', rc == 6 and any('names no installed binary' in x for x in out))
link = setup()
cj = json.loads((link / 'runs_s' / 'k_19.cache.json').read_text())
(link / 'runs_s' / 'k_19.cache.json').write_text(json.dumps(dict(app_post_copy=dict(sha='0' * 64))))
rc, out = run(link, tool())
ok &= case('X7 app_post_copy other than the post copy -> rc 1', rc == 1 and any('is not the one the harness noted' in x for x in out))
(link / 'runs_s' / 'k_19.cache.json').write_text(json.dumps(cj))
(link / 'cat' / 'k_19' / 'ShaderCache_PPSA21564' / VAR / 'extra.bin').write_bytes(b'z')
rc, out = run(link, tool())
ok &= case('X8 a file added to the post copy after the arm -> cachex verify fails -> rc 1', rc == 1)
link = setup(seal_line='installed: %s %s variant_other' % (INST, SIG))
rc, out = run(link, tool())
ok &= case('X9 no variant directory of the seal in the post copy -> rc 1', rc == 1 and any('no variant directory' in x for x in out))
link = setup()
(link / 'k_19.json').write_text(json.dumps(dict(binary_sha256='0' * 64, env={})))
rc, out = run(link, tool())
ok &= case('X10 the log of another binary -> rc 1', rc == 1)
(link / 'k_19.json').write_text(json.dumps(dict(binary_sha256=INST, env=dict(KYTY_GAME_PATCH='p'))))
rc, out = run(link, tool())
ok &= case('X11 a log with KYTY_GAME_PATCH -> rc 1', rc == 1)
link = setup(seal_line='installed: %s KytySC3:other %s' % (INST, VAR))
rc, out = run(link, tool())
ok &= case('X12 a log on another signature -> rc 1', rc == 1 and any('on its signature' in x for x in out))
link = setup()
rc, out = run(link, tool('refuse'))
ok &= case('X13 the tool refuses -> rc 6, no code change', rc == 6 and any('TOOL REFUSED' in x for x in out))
link = setup()
rc, out = run(link, tool('compat'))
ok &= case('X14 compatibility.txt other than the log line -> CHECK FAILED rc 1', rc == 1 and out[-1] == 'EXPORT: CHECK FAILED' and
           any(x.endswith(': DIFFERENT') for x in out))
link = setup()
p = link / 'cat' / 'k_19' / 'ShaderCache_PPSA21564' / VAR / 'vs_0001.bin'
d = bytearray(p.read_bytes())
d[-1] ^= 1
p.write_bytes(bytes(d))
text, msha = CX.app_manifest((link / 'cat' / 'k_19').as_posix())
(link / 'cat' / 'k_19' / 'MANIFEST.txt').write_bytes(text.encode('ascii'))
(link / 'runs_s' / 'k_19.cache.json').write_text(json.dumps(dict(app_post_copy=dict(sha=msha))))
rc, out = run(link, tool())
ok &= case('X15 a shader file with a bad checksum -> CHECK FAILED', rc == 1 and any('bad signature or checksum 1' in x for x in out))
link = setup(recs=3, dup=2)
rc, out = run(link, tool())
ok &= case('X16 duplicate graphics keys counted (R_DUP_GFX 1 of 3 recipes with two equal keys)', any('R_DUP_GFX 1, R_DUP_CS 0' in x
                                                                                                   for x in out))
link = setup()
tl = tool('rewrite')
rc, out = run(link, tl)
ok &= case('X17 a tool that changes pipelines.bin -> "removed duplicates (F17): UNDETERMINED", CHECK FAILED', rc == 1 and
           any(x.startswith('removed duplicates (F17): UNDETERMINED') for x in out))
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
