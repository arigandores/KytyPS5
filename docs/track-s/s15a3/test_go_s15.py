"""Offline fixtures of go_s15.sh - S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)(3)-(4)): the port of s13/test_go_s13.py;
G14, G16, G17 (the holds 300 / 300 + --hold-u / 330), G18c (the 39 plans: --hold-u on the 19 U plans only, enter_scene_s15.py),
G18d (the 11th field of the plan: "-", N:N:N, else rc 2 by an anchored regex), GL5 (--hold-u reaches enter_scene).  The S13 text
follows.
Port header: Offline fixtures of go_s13.sh (track S, link S13a, HPP-498; ROADMAP "SESSION 122" item 408 (l), item 414) WITHOUT the game -
the port of C:/kyty/s288/s9/test_go_s9.py.  Part 1: a copy of the harness with ROOT, the lock and the stop file moved into a
fixture directory runs its cheap refusals and its DRY plans (usage, stop file, lock, the guards s4 / s6 / s10 / s13, PLWAIT, the
seal path, the seal line "installed: PENDING" -> rc 6, the seal call line, an attempt already made, the plan of every arm kind:
the collection chain k_01 <- empty, k_02 <- cat/k_01, class M without video; u: class T, the empty app caches, the seed path and
prepare-cold, video; w13: validation with VK_LAYER_PATH and the duplicate limit, no video, stable 300).  Part 2: a second copy
runs its whole path INSIDE a fixture lock with stubs (the game, procload, idle142, fgcpu143, powershell; sc_s15.py real for --plan,
--seal-path and --installed, a stub for the rest; cachex_s.py real): k_01 (the game sees the empty app caches, GLCache as found;
the post copy cat/k_01 holds what it wrote; the installed caches back), k_02 (the game sees what k_01 left), u_01 (the empty app
caches, the catalogue noted), the installed binary never replaced and checked before / after, the lock rows, the GamePatch
interference, IN_ARM written and removed, a hanging IN_ARM -> rc 1, an installed binary other than the seal line -> rc 1 inside
the lock; S9r2 observation 1 - a failed return leaves IN_ARM and RETURN_FAILED; observation 2 - the lock line names the seal.
S13a2 (item 419 (v) Z3, item 428 (v)(1)): every plan of the 39 arms names KYTY_S_PCW=1 once; the caller's KYTY_S_PCW,
KYTY_S_PCW_FORCE_MS and KYTY_FIX_* never reach the game, KYTY_S_PCW=1 goes positionally to enter_scene_s9.py.
S13a3 (item 436 (b)(5), RC5): the guards are any <root>/*/RETURN_FAILED and <root>/*/IN_ARM - s12 (S12c) and a link directory
never named before refuse rc 1 before the lock (G5, GL15-GL17); a file one level deeper is not a guard (G5b); S13a4 (item 452 (d)(2)): the seal is 13.
S15a3 (HPP-617, item 529 (b)(1), (3)): the names of the seal are pred/16_s.md / pred/16b_s.md; G18e - the seal path of the harness:
pred/14_s.md, pred/14b_s.md, pred/15_s.md, pred/15b_s.md -> rc 1 "seal path bad"; pred/16_s.md, pred/16b_s.md -> the plan.
The first output line names this suite and the harness by sha256; the output ends with ALL OK.
    python C:/kyty/s288/s15/test_go_s15.py
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'go_s15.sh')
print('suite test_go_s15.py sha256 %s target go_s15.sh sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
NL = chr(10)
BASE = Path('C:/kyty/s288/s15/fx_go_s15')
shutil.rmtree(BASE, ignore_errors=True)
(BASE / 'pred').mkdir(parents=True)
(BASE / 's15').mkdir()
FXLOCK = (BASE / 'LOCK').as_posix()
FXSTOP = (BASE / 'STOP').as_posix()
text = Path(SRC).read_text(encoding='ascii')
for a, b in (('ROOT=C:/kyty/s288' + NL, 'ROOT=%s' % BASE.as_posix() + NL), ('LOCK=/c/kyty/SEALED_RUN.lock' + NL, 'LOCK=%s' % FXLOCK + NL),
             ('STOPF=/c/kyty/s288/STOP' + NL, 'STOPF=%s' % FXSTOP + NL)):
    assert text.count(a) == 1, a
    text = text.replace(a, b)
(BASE / 's15' / 'go_s15.sh').write_bytes(text.encode('ascii'))
SC13 = os.path.join(HERE, 'sc_s15.py').replace(chr(92), '/')
INST = 'cd' * 32
SIG = 'KytySC3:1234:robust'
VAR = 'variant_x'


def stub_real(base, seal_rel):
    """The real scorer for --plan / --seal-path / --installed with its seal moved into the fixture."""
    return ("import importlib.util, sys\n"
            "s = importlib.util.spec_from_file_location('sc13', %r)\nm = importlib.util.module_from_spec(s)\n"
            "s.loader.exec_module(m)\nm.ROOT = %r\nm.SEAL_BASE = %r\nm.SEAL_B = %r\n"
            "sys.exit(m.main(sys.argv[1:], %r))\n" % (SC13, base.as_posix(), (base / 'pred' / '16_s.md').as_posix(),
                                                     (base / 'pred' / '16b_s.md').as_posix(), (base / 's15').as_posix()))


(BASE / 's15' / 'sc_s15.py').write_bytes(stub_real(BASE, 'pred/16_s.md').encode('ascii'))
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name), flush=True)
    if not cond and os.environ.get('FX_FAST') == '1' and not name.startswith('U15 '):
        sys.exit(1)        # S15a hand mutants (hmut_s15.py): stop at the first failing case; the full suite never sets it
    return bool(cond)


def go(tag, dry='1', plwait='540', base=BASE):
    env = dict(os.environ)
    env['DRY'] = dry
    env['PLWAIT'] = plwait
    env['PATH'] = '/usr/bin:/mingw64/bin:' + env.get('PATH', '')
    p = subprocess.run([BASH, (base / 's15' / 'go_s15.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=180)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!' + NL, '')


def seal(lines, name='16_s.md'):
    (BASE / 'pred' / name).write_text(NL.join(lines) + NL, encoding='ascii')


ok = True
try:
    Path(SRC).read_bytes().decode('ascii')
    asc = True
except UnicodeError:
    asc = False
ok &= case('G1 go_s15.sh is ASCII only', asc)
rc, o = go('Bad-Tag')
ok &= case('G2 a tag with other characters -> rc 2 usage', rc == 2 and 'usage' in o)
Path(FXSTOP).write_text('408 test' + NL)
rc, o = go('k_01')
ok &= case('G3 the stop file -> rc 4 BUSY before anything', rc == 4 and 'stop file' in o)
Path(FXSTOP).unlink()
Path(FXLOCK).write_text('go_fs5c.sh fs5_v pid 1' + NL)
rc, o = go('k_01')
ok &= case('G4 a foreign lock -> rc 4 BUSY (lock held) before any process', rc == 4 and 'lock held: go_fs5c.sh fs5_v' in o)
Path(FXLOCK).unlink()
for gd in ('s4/RETURN_FAILED', 's6/RETURN_FAILED', 's10/RETURN_FAILED', 's10/IN_ARM', 's15/RETURN_FAILED', 's15/IN_ARM',
           's12/RETURN_FAILED', 's12/IN_ARM', 's14z/RETURN_FAILED', 's14z/IN_ARM'):
    (BASE / gd).parent.mkdir(parents=True, exist_ok=True)
    (BASE / gd).write_text('guard' + NL)
    rc, o = go('k_01')
    ok &= case('G5 the guard %s -> rc 1 before the lock' % gd, rc == 1 and 'return failed guard' in o and gd in o)
    (BASE / gd).unlink()
(BASE / 'sx' / 'deeper').mkdir(parents=True)
(BASE / 'sx' / 'deeper' / 'RETURN_FAILED').write_text('not a guard' + NL)
(BASE / 'sx' / 'deeper' / 'IN_ARM').write_text('not a guard' + NL)
rc, o = go('k_01')
ok &= case('G5b RC5 the edge: RETURN_FAILED / IN_ARM one level deeper (sx/deeper/) are not guards -> the call goes past the guards '
           '(here to the seal check)', 'return failed guard' not in o and rc != 0)
(BASE / 'sx' / 'deeper' / 'RETURN_FAILED').unlink()
(BASE / 'sx' / 'deeper' / 'IN_ARM').unlink()
rc, o = go('k_01', plwait='x')
ok &= case('G6 PLWAIT not a number -> rc 2; above 540 -> rc 2', rc == 2 and 'bad PLWAIT' in o and go('k_01', plwait='541')[0] == 2)
rc, o = go('zz_9')
ok &= case('G7 an unknown tag -> rc 2', rc == 2 and 'unknown tag' in o)
TAGS = ['k_%02d' % i for i in range(1, 20)] + ['u_%02d' % i for i in range(1, 20)] + ['w13']
CALLS = ['go_s15 call: PLWAIT=540 bash C:/kyty/s288/s15/go_s15.sh %s' % t for t in TAGS]
seal(CALLS + ['installed: PENDING'])
rc, o = go('k_01')
ok &= case('G8 the seal line "installed: PENDING" -> rc 6 before the lock (an edition names the binary)', rc == 6 and
           'PENDING' in o and not Path(FXLOCK).exists())
seal(CALLS)
rc, o = go('k_01')
ok &= case('G9 no line "installed:" -> rc 1', rc == 1 and 'no installed line' in o)
seal(CALLS + ['installed: PENDING'])
seal(CALLS[1:] + ['installed: %s %s %s' % (INST, SIG, VAR)], '16b_s.md')
rc, o = go('k_01')
ok &= case('G10 the edition 12b in force without the call line of k_01 -> rc 1 (PLWAIT differs from the seal)', rc == 1 and
           'PLWAIT differs' in o)
seal(CALLS + ['installed: %s %s %s' % (INST, SIG, VAR)], '16b_s.md')
seal(CALLS[:1] + CALLS + ['installed: %s %s %s' % (INST, SIG, VAR)], '16b_s.md')
rc, o = go('k_01')
ok &= case('G11 two call lines of one tag -> rc 1', rc == 1)
seal(CALLS + ['installed: %s %s %s' % (INST, SIG, VAR)], '16b_s.md')
rc, o = go('k_01', plwait='300')
ok &= case('G12 PLWAIT other than the call line -> rc 1', rc == 1 and 'PLWAIT differs' in o)
out = dict((t, go(t)) for t in ('k_01', 'k_02', 'k_19', 'u_01', 'u_19', 'w13'))
ok &= case('G13 DRY=1 of every arm kind -> rc 0 with a DRY line naming the installed line of the edition 12b',
           all(v[0] == 0 and v[1].startswith('DRY %s:' % k) and ('installed %s %s %s' % (INST, SIG, VAR)) in v[1]
               for k, v in out.items()))
k1, k2, k19 = out['k_01'][1], out['k_02'][1], out['k_19'][1]
B = BASE.as_posix()
ok &= case('G14 k_01: class M (no trace), mode cat, the app caches from s15/empty_app, GLCache as found, hold 180, stable 100, '
           'timeout 600, no video, no validation, no seed path; the seal 11b; item 511 (z)(3): hold 300, no --hold-u', 'mode cat' in k1 and
           ('restore app <- %s/s15/empty_app;' % B) in k1 and 'glc as found' in k1 and '--hold 300 ' in k1 and '--hold-u' not in k1 and
           '--stable-draws 100 --timeout 600' in k1 and ' --rec ' not in k1 and 'vulkan-validation' not in k1 and
           'KYTY_AV_TRACE' not in k1 and 'SEED_PATH' not in k1 and '--level title_controller_ship' in k1 and
           ('--pred %s/pred/16b_s.md' % B) in k1 and ('%s/s15/enter_scene_s15.py k_01' % B) in k1 and
           ('--root %s/s15' % B) in k1 and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in k1)
ok &= case('G15 k_02 from the post copy cat/k_01; k_19 from cat/k_18 on enemy_gorilla', ('restore app <- %s/s15/cat/k_01;' % B) in k2
           and ('restore app <- %s/s15/cat/k_18;' % B) in k19 and '--level enemy_gorilla' in k19)
u1, w13 = out['u_01'][1], out['w13'][1]
ok &= case('G16 u_01: class T, the empty app caches, the seed path s15/seeds and prepare-cold, video, hold 300 with --hold-u '
           '120:3000:300 (item 511 (z)(4)), no validation',
           ('restore app <- %s/s15/empty_app;' % B) in u1 and 'KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1' in u1 and
           'KYTY_SHADER_SEED_PATH=C:/kyty/s288/s15/seeds KYTY_CACHE_MODE=prepare-cold' in u1 and ' --rec ' in u1 and
           '--hold 300 --hold-u 120:3000:300 ' in u1 and 'vulkan-validation' not in u1 and '--level enemy_gorilla' in out['u_19'][1])
ok &= case('G17 w13: validation true, VK_LAYER_PATH and the duplicate limit 100000000, the seed path and prepare-cold, no video, '
           'hold 330, stable 300, Sky Garden', '--emu-arg=--vulkan-validation --emu-arg=true' in w13 and
           'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000' in w13 and
           'VK_LAYER_MESSAGE_ID_FILTER' not in w13 and ' --rec ' not in w13 and '--hold 330 ' in w13 and '--hold-u' not in w13 and
           '--stable-draws 300 --timeout 600' in w13 and '--level underwater_aerial_garden' in w13 and
           'KYTY_SHADER_SEED_PATH=C:/kyty/s288/s15/seeds' in w13 and 'KYTY_AV_TRACE' not in w13)
ok &= case('G18 every arm kind names KYTY_S_PCW=1 once (item 419 (v) Z3, item 428 (v)(1)); none names KYTY_S_PCW_FORCE_MS, '
           'KYTY_GAME_PATCH or KYTY_FIX_', all(v[1].count(' KYTY_S_PCW=1 ') == 1 and v[1].count('KYTY_S_PCW') == 1 and
                                              'GAME_PATCH' not in v[1] and 'KYTY_FIX_' not in v[1] for v in out.values()))
plans2 = dict((tg, go(tg, dry='2')) for tg in TAGS)
ok &= case('G18b DRY=2 of all 39 arms: rc 0, each plan names KYTY_S_PCW=1 once and no other S knob', len(plans2) == 39 and all(
    v[0] == 0 and v[1].count(' KYTY_S_PCW=1 ') == 1 and v[1].count('KYTY_S_PCW') == 1 for v in plans2.values()))
ok &= case('G18c item 511 (z)(3)-(4) over the 39 DRY=2 plans: the 19 U plans "--hold 300 --hold-u 120:3000:300", the 19 k plans '
           '"--hold 300" and w13 "--hold 330" without --hold-u; the plan runs s15/enter_scene_s15.py',
           sum(1 for tg, v in plans2.items() if tg.startswith('u_') and '--hold 300 --hold-u 120:3000:300 ' in v[1]) == 19 and
           sum(1 for tg, v in plans2.items() if tg.startswith('k_') and '--hold 300 ' in v[1] and '--hold-u' not in v[1]) == 19 and
           '--hold 330 ' in plans2['w13'][1] and '--hold-u' not in plans2['w13'][1] and
           all('/s15/enter_scene_s15.py %s ' % tg in v[1] for tg, v in plans2.items()))
B3 = BASE / 'b3'
(B3 / 's15').mkdir(parents=True)
(B3 / 'pred').mkdir()
(B3 / 's15' / 'go_s15.sh').write_bytes(text.replace('ROOT=%s' % BASE.as_posix() + NL, 'ROOT=%s' % B3.as_posix() + NL).encode('ascii'))
hu_rc = {}
for fld in ('-', '120:3000:300', 'x', '120:3000', '', '1x:2:3', '120:3000:300x'):
    (B3 / 's15' / 'sc_s15.py').write_text(NL.join(['import sys', 'a = sys.argv[1:]', "if a[:1] == ['--seal-path']:",
                                                   "    print('pred/16_s.md')", '    sys.exit(0)',
                                                   "print('s15 lvl T u 300 - 100 600 1 0 %s')" % fld, 'sys.exit(0)', '']),
                                          encoding='ascii')
    hu_rc[fld] = go('u_01', dry='2', base=B3)
ok &= case('G18d the hold-rule field of the plan: "-" -> no --hold-u; N:N:N -> --hold-u N:N:N; "x", "120:3000" or none -> rc 2 '
           '"bad hold rule" before the lock; "1x:2:3" and "120:3000:300x" too (the anchored regex)', hu_rc['-'][0] == 0 and '--hold-u' not in hu_rc['-'][1] and
           hu_rc['120:3000:300'][0] == 0 and '--hold 300 --hold-u 120:3000:300 ' in hu_rc['120:3000:300'][1] and
           all(hu_rc[f][0] == 2 and 'bad hold rule' in hu_rc[f][1] for f in ('x', '120:3000', '', '1x:2:3', '120:3000:300x')))
sp_rc = {}
for sp in ('pred/14_s.md', 'pred/14b_s.md', 'pred/15_s.md', 'pred/15b_s.md', 'pred/16_s.md', 'pred/16b_s.md'):
    (B3 / 's15' / 'sc_s15.py').write_text(NL.join(['import sys', 'a = sys.argv[1:]', "if a[:1] == ['--seal-path']:",
                                                   '    print(%r)' % sp, '    sys.exit(0)',
                                                   "print('s15 lvl T u 300 - 100 600 1 0 -')", 'sys.exit(0)', '']),
                                          encoding='ascii')
    sp_rc[sp] = go('u_01', dry='2', base=B3)
ok &= case('G18e S15a3 (item 529 (b)(3)): the seal path of --seal-path pred/14_s.md, pred/14b_s.md, pred/15_s.md or '
           'pred/15b_s.md -> rc 1 "seal path bad" before the lock, no plan; pred/16_s.md and pred/16b_s.md -> rc 0, the DRY=2 plan '
           'names that seal', all(sp_rc[s][0] == 1 and 'seal path bad' in sp_rc[s][1] and 'PLAN ' not in sp_rc[s][1]
                                  for s in ('pred/14_s.md', 'pred/14b_s.md', 'pred/15_s.md', 'pred/15b_s.md')) and
           all(sp_rc[s][0] == 0 and sp_rc[s][1].startswith('PLAN u_01: link s15, seal %s, ' % s)
               for s in ('pred/16_s.md', 'pred/16b_s.md')) and not Path(FXLOCK).exists())
rc, o = go('k_01', dry='2')
ok &= case('G19 DRY=2 right after the lock check prints the plan', rc == 0 and o.startswith('PLAN k_01: link s15, seal pred/16b_s.md'))
(BASE / 's15' / 'attempt_k_01.txt').write_text('x')
rc, o = go('k_01')
ok &= case('G20 an attempt already made -> rc 1, no repeat', rc == 1 and 'attempt already made' in o)
(BASE / 's15' / 'attempt_k_01.txt').unlink()
ok &= case('G21 no lock file was created by any DRY call', not Path(FXLOCK).exists())
src_t = Path(SRC).read_text(encoding='ascii')
ok &= case('G22 the shipped harness unsets KYTY_GAME_PATCH and KYTY_S_PCW, guards any */RETURN_FAILED and */IN_ARM (item 436 '
           '(b)(5)), writes the lock line '
           '"go_s.sh <tag> " naming the seal $PRED (S9r2 observation 2), reads the seal path from the scorer',
           'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA VK_LAYER_MESSAGE_ID_FILTER KYTY_GAME_PATCH KYTY_S_PCW KYTY_S_PCW_FORCE_MS'
           + NL in src_t and '  for G in $ROOT/*/RETURN_FAILED $ROOT/*/IN_ARM; do' + NL in src_t and
           'if [ -e "$G" ]; then' in src_t and '$ROOT/s4/RETURN_FAILED' not in src_t and
           'echo "go_s.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S) (go_s15.sh seal $PRED)"' in src_t and
           'PRED=$(python $SC --seal-path' in src_t and src_t.count('guardfiles' + NL) == 2 and 'seal 06' not in src_t and
           'for V in $(compgen -e); do case "$V" in KYTY_FIX_*) unset "$V";; esac; done' + NL in src_t and
           ('SPCW=1 ' in src_t) and 'KYTY_GPU_MARKERS=0 KYTY_S_PCW=$SPCW $CLSX' in src_t)
ok &= case('G23 S9r2 observation 1 in the shipped harness: return_failed sets RETFAIL=1 and the guard is removed only with RETFAIL=0',
           'return_failed() {' + NL + '  RETFAIL=1' + NL in src_t and '[ "$RETFAIL" = "0" ]' in src_t)

# ============================================================== part 2: the path INSIDE the lock, stubbed
B2 = Path('C:/kyty/s288/s15/fx_go_lock15')
shutil.rmtree(B2, ignore_errors=True)
for d in ('pred', 'bin', 'game', 'emu', 'lad/NVIDIA/GLCache', 's15', 's9'):
    (B2 / d).mkdir(parents=True)
EMU2, LAD2, GLC2 = B2 / 'emu', B2 / 'lad', B2 / 'lad' / 'NVIDIA' / 'GLCache'
LOCK2, STOP2, GAME2 = (B2 / 'LOCK').as_posix(), (B2 / 'STOP').as_posix(), B2 / 'game' / 'kyty_emulator.exe'
ENV2 = dict(CACHEX_EMU=str(EMU2), CACHEX_GLC=str(GLC2), CACHEX_LOCK=LOCK2, CACHEX_KNOWN_LAD=str(LAD2), LOCALAPPDATA=str(LAD2),
            FX_GAME=str(GAME2))
os.environ.update(ENV2)
_cs = importlib.util.spec_from_file_location('cachex_fx13', 'C:/kyty/s288/cachex_s.py')
CX = importlib.util.module_from_spec(_cs)
_cs.loader.exec_module(CX)


def put2(p, data):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def sha2(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


put2(EMU2 / '_PipelineCache' / 'PPSA21564.bin', b'installed drv')
put2(EMU2 / '_ShaderCache' / 'PPSA21564' / 'variant_x' / 'installed.bin', b'installed state')
put2(GLC2 / 'x' / 'y.bin', b'glc found')
PRE_APP, PRE_GLC = CX.app_manifest(None)[1], CX.glc_manifest(str(GLC2))[1]
INSTX = hashlib.sha256(b'installed build X').hexdigest()
put2(GAME2, b'installed build X')
put2(B2 / 'gates_default.txt', b'')
for name, body in (('procload.py', 'import sys' + NL + 'sys.exit(0)' + NL), ('idle142.py', 'import sys' + NL + 'sys.exit(0)' + NL),
                   ('fgcpu143.py', "print('fgcpu stub')" + NL), ('sheet142.py', "print('sheet stub')" + NL)):
    put2(B2 / name, body.encode('ascii'))
put2(B2 / 'bin' / 'powershell', ('#!/bin/sh' + NL + 'echo 0' + NL).encode('ascii'))
shutil.copy2('C:/kyty/s288/cachex_s.py', B2 / 'cachex_s.py')
REAL = stub_real(B2, 'pred/16_s.md').replace('sys.exit(m.main(', 'REAL = lambda: sys.exit(m.main(')
put2(B2 / 's15' / 'sc_s15.py', (REAL +
                                "import os\na = sys.argv[1:]\n"
                                "if a[:1] in (['--plan'], ['--seal-path'], ['--installed']):\n    REAL()\n"
                                "if '--check-seal' in a:\n    print('SEAL: PASS (fixture stub)')\n    sys.exit(0)\n"
                                "if a[:1] == ['--allowed']:\n    print('ALLOWED %s: yes (fixture stub)' % a[1])\n    sys.exit(0)\n"
                                "if '--seeds-check' in a:\n    x = os.environ.get('FX_SEEDS', 'ab' * 32)\n"
                                "    print('seeds sha %s files 3 (seeds_manifest.txt x) %s' % (x, 'MATCH' if x == 'ab' * 32 else "
                                "'DIFF'))\n    sys.exit(0 if x == 'ab' * 32 else 1)\n"
                                "print('ARM stub')\nsys.exit(0)\n").encode('ascii'))
put2(B2 / 's15' / 'enter_scene_s15.py', (
    "import hashlib, json, os, sys\ntag = sys.argv[1]\nroot = sys.argv[sys.argv.index('--root') + 1]\n"
    "emu, glc = os.environ['CACHEX_EMU'], os.environ['CACHEX_GLC']\n"
    "seen = sorted(os.path.relpath(os.path.join(d, f), emu).replace(os.sep, '/') for d, _, fs in os.walk(emu) for f in fs)\n"
    "open(os.path.join(root, 'log_%s.txt' % tag), 'w').write('log of the stub')\n"
    "ia = open(os.path.join(root, 'IN_ARM')).read() if os.path.exists(os.path.join(root, 'IN_ARM')) else None\n"
    "json.dump({'tag': tag, 'gp': os.environ.get('KYTY_GAME_PATCH'), 'spcw': os.environ.get('KYTY_S_PCW'), 'seen': seen, "
    "'fix': sorted(k for k in os.environ if k.startswith('KYTY_FIX_') or k == 'KYTY_S_PCW_FORCE_MS'), "
    "'in_arm': ia, 'argv': sys.argv[1:], 'lock': open(os.environ['CACHEX_LOCK']).read(), "
    "'game': hashlib.sha256(open(os.environ['FX_GAME'], 'rb').read()).hexdigest(), "
    "'glc': sorted(os.listdir(os.path.join(glc, 'x')))}, open(os.path.join(root, '%s.json' % tag), 'w'))\n"
    "os.makedirs(os.path.join(emu, '_ShaderCache', 'PPSA21564', 'variant_x'), exist_ok=True)\n"
    "open(os.path.join(emu, '_ShaderCache', 'PPSA21564', 'variant_x', 'from_%s.bin' % tag), 'wb').write(tag.encode())\n"
    "open(os.path.join(glc, 'x', 'game.bin'), 'wb').write(b'the game wrote GLCache')\n"
    "if os.environ.get('FX_MODE') == 'gamepatch':\n"
    "    open(os.path.join(root, 'log_%s.txt' % tag), 'wb').write(b'x\\nGamePatch: applied 4 pokes\\n')\n"
    "if os.environ.get('FX_MODE') == 'breakcx':\n"
    "    import shutil\n    shutil.rmtree(os.path.join(os.path.dirname(root), 's15', 'installed_pre'))\n"
    "print('VERDICT: stub')\n").encode('ascii'))
text2 = Path(SRC).read_text(encoding='ascii')
for a, b in (('ROOT=C:/kyty/s288' + NL, 'ROOT=%s' % B2.as_posix() + NL), ('LOCK=/c/kyty/SEALED_RUN.lock' + NL, 'LOCK=%s' % LOCK2 + NL),
             ('STOPF=/c/kyty/s288/STOP' + NL, 'STOPF=%s' % STOP2 + NL),
             ('GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"' + NL, 'GAME="%s"' % GAME2.as_posix() + NL),
             ('RSLEEP=5' + NL, 'RSLEEP=0' + NL)):
    assert text2.count(a) == 1, a
    text2 = text2.replace(a, b)
(B2 / 's15' / 'go_s15.sh').write_bytes(text2.encode('ascii'))
TAGS2 = ('k_01', 'k_02', 'u_01', 'w13', 'k_03')
(B2 / 'pred' / '16_s.md').write_bytes((''.join('go_s15 call: PLWAIT=540 bash C:/kyty/s288/s15/go_s15.sh %s\n' % t for t in TAGS2) +
                                       'installed: %s %s %s\n' % (INSTX, SIG, VAR)).encode('ascii'))
BINP = '/' + B2.as_posix()[0].lower() + B2.as_posix()[2:] + '/bin'


def go2(tag, mode='', **env_over):
    env = dict(os.environ)
    env.update(ENV2)
    env.update(DRY='0', PLWAIT='540', FX_MODE=mode, PATH=BINP + ':/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    env.update(env_over)
    p = subprocess.run([BASH, (B2 / 's15' / 'go_s15.sh').as_posix(), tag], capture_output=True, text=True, env=env, timeout=300)
    return p.returncode, (p.stdout + p.stderr).replace('bash.exe: warning: could not find /tmp, please create!' + NL, '')


def cj2(tag):
    p = B2 / 's15' / 'runs_s' / ('%s.cache.json' % tag)
    return json.loads(p.read_text()) if p.exists() else {}


def js2(tag):
    p = B2 / 's15' / ('%s.json' % tag)
    return json.loads(p.read_text()) if p.exists() else {}


def lockrows():
    p = B2 / 's15' / 'runs_s' / 'lock.log'
    return p.read_text().splitlines() if p.exists() else []


EMPTY = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
rc, o = go2('k_01', KYTY_S_PCW='0', KYTY_S_PCW_FORCE_MS='15000', KYTY_FIX_B42='1')
c = cj2('k_01')
j = js2('k_01')
ok &= case('GL1 k_01 inside the lock: the installed binary NOT replaced (the game ran it), checked before and after',
           rc == 0 and j.get('game') == INSTX and GAME2.read_bytes() == b'installed build X' and
           c.get('installed_before', {}).get('sha') == INSTX and c.get('installed_after', {}).get('sha') == INSTX)
ok &= case('GL2 k_01: the game saw NO app cache file (the empty set), GLCache as found (no restore), KYTY_S_PCW / '
           'KYTY_S_PCW_FORCE_MS / KYTY_FIX_B42 of the caller not seen, KYTY_S_PCW=1 passed positionally; the installed caches and '
           'GLCache back after', j.get('seen') == [] and 'y.bin' in j.get('glc', []) and
           j.get('spcw') is None and j.get('fix') == [] and 'KYTY_S_PCW=1' in j.get('argv', []) and c.get('restore_app', {}).get('got') == EMPTY and 'restore_glc' not in c and
           c.get('man_launch_glc', {}).get('sha') == c.get('man_pre_glc', {}).get('sha') and
           CX.app_manifest(None)[1] == PRE_APP and CX.glc_manifest(str(GLC2))[1] == PRE_GLC)
ok &= case('GL3 k_01: the post copy s15/cat/k_01 holds what the game wrote (its variant file) and app_post_copy is noted',
           (B2 / 's15' / 'cat' / 'k_01' / 'ShaderCache_PPSA21564' / 'variant_x' / 'from_k_01.bin').read_bytes() == b'k_01' and
           c.get('app_post_copy', {}).get('sha') == sha2(B2 / 's15' / 'cat' / 'k_01' / 'MANIFEST.txt'))
rc, o = go2('k_02')
c = cj2('k_02')
j = js2('k_02')
ok &= case('GL4 k_02: the game saw the catalogue k_01 left (restore = app_post_copy of k_01); cat/k_02 holds both files; '
           'everything back after', rc == 0 and j.get('seen') == ['_ShaderCache/PPSA21564/variant_x/from_k_01.bin'] and
           c.get('restore_app', {}).get('got') == cj2('k_01').get('app_post_copy', {}).get('sha') and
           sorted(os.listdir(B2 / 's15' / 'cat' / 'k_02' / 'ShaderCache_PPSA21564' / 'variant_x')) ==
           ['from_k_01.bin', 'from_k_02.bin'] and CX.app_manifest(None)[1] == PRE_APP and
           CX.glc_manifest(str(GLC2))[1] == PRE_GLC)
rc, o = go2('u_01')
c = cj2('u_01')
j = js2('u_01')
ok &= case('GL5 u_01 form U: the empty app caches, GLCache as found, the catalogue sha noted, no post copy, the seed path in the '
           'call, everything back after', rc == 0 and j.get('seen') == [] and 'game.bin' not in j.get('glc', []) and
           c.get('seeds', {}).get('sha') == 'ab' * 32 and 'app_post_copy' not in c and not (B2 / 's15' / 'cat' / 'u_01').exists()
           and 'KYTY_SHADER_SEED_PATH=C:/kyty/s288/s15/seeds' in j.get('argv', []) and CX.app_manifest(None)[1] == PRE_APP and
           j.get('argv', [])[j.get('argv', []).index('--hold-u') + 1] == '120:3000:300' and '--hold' in j.get('argv', []))
rc, o = go2('w13')
j = js2('w13')
ok &= case('GL6 w13: validation passed to enter_scene (--emu-arg), VK_LAYER_* positional', rc == 0 and
           '--emu-arg=--vulkan-validation' in j.get('argv', []) and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000' in j.get('argv', [])
           and 'KYTY_S_PCW=1' in j.get('argv', []) and 'KYTY_S_PCW=1' in js2('u_01').get('argv', []))
lr = lockrows()
ok &= case('GL7 four arms - four taken / released pairs, no lock file, no guard', len(lr) == 8 and
           lr[0].startswith('lock taken k_01 ') and lr[-1].startswith('lock released w13 ') and not Path(LOCK2).exists() and
           not (B2 / 's15' / 'RETURN_FAILED').exists() and not (B2 / 's15' / 'IN_ARM').exists())
ia1 = js2('k_01').get('in_arm') or ''
t4 = (B2 / 's15' / 'times.txt').read_text()
ok &= case('GL8 IN_ARM: the game saw it (the tag, the installed sha, man_pre_app / man_pre_glc) and the successful return removed it',
           ia1.startswith('IN_ARM k_01 ') and ('installed: %s (copy' % INSTX) in ia1 and
           ('man_pre_app: %s ' % cj2('k_01').get('man_pre_app', {}).get('sha', 'x')) in ia1 and
           'removed after the successful return' in t4)
for f in ('attempt_u_01.txt', 'u_01.json'):
    os.replace(str(B2 / 's15' / f), str(B2 / 's15' / ('old_' + f)))
n_lock = len(lockrows())
rc, o = go2('u_01', FX_SEEDS='cd' * 32)
ok &= case('GL9 a u arm with a catalogue other than seeds_manifest.txt -> rc 1 "seeds bad" before the lock', rc == 1 and
           'seeds bad' in o and len(lockrows()) == n_lock)
rc, o = go2('u_01', mode='gamepatch', KYTY_GAME_PATCH='C:/x/p.txt')
t3 = (B2 / 's15' / 'times.txt').read_text()
ok &= case('GL10 KYTY_GAME_PATCH of the caller not seen by the game; a GamePatch: log line -> rc 7, the caches returned',
           rc == 7 and js2('u_01').get('gp') is None and 'GAMEPATCH interference: 1 lines' in o and
           'item 342 (e): lines beginning GamePatch: in log_u_01.txt: 1' in t3 and CX.app_manifest(None)[1] == PRE_APP and
           GAME2.read_bytes() == b'installed build X' and not Path(LOCK2).exists())
lk = js2('k_01').get('lock') or ''
ok &= case('GL11 S9r2 observation 2: the lock line the game saw begins "go_s.sh k_01 " and names go_s15.sh and the seal file in '
           'force', lk.startswith('go_s.sh k_01 pid ') and '(go_s15.sh seal pred/16_s.md)' in lk)
(B2 / 's15' / 'IN_ARM').write_text('IN_ARM k_03 2026-10-04T00:00:00Z pid 1 - a hard kill left it' + NL)
n_lock = len(lockrows())
rc, o = go2('k_03')
ok &= case('GL12 a hanging IN_ARM -> rc 1 before the lock: no lock row, no attempt, the guard kept', rc == 1 and
           'return failed guard' in o and len(lockrows()) == n_lock and not (B2 / 's15' / 'attempt_k_03.txt').exists() and
           (B2 / 's15' / 'IN_ARM').exists())
(B2 / 's15' / 'IN_ARM').unlink()
put2(GAME2, b'another installed build')
n_lock = len(lockrows())
rc, o = go2('k_03')
t5 = (B2 / 's15' / 'times.txt').read_text()
ok &= case('GL13 an installed binary other than the seal line -> rc 1 inside the lock: no IN_ARM, no attempt, the lock taken and '
           'released, the row in times.txt', rc == 1 and 'installed binary not' in o and
           GAME2.read_bytes() == b'another installed build' and not (B2 / 's15' / 'IN_ARM').exists() and
           not (B2 / 's15' / 'attempt_k_03.txt').exists() and len(lockrows()) == n_lock + 2 and not Path(LOCK2).exists() and
           ('!= %s (seal line installed:) - no arm' % INSTX) in t5)
put2(GAME2, b'installed build X')
for k, gd in enumerate(('s12/RETURN_FAILED', 's12/IN_ARM', 's14z/IN_ARM')):
    (B2 / gd).parent.mkdir(parents=True, exist_ok=True)
    (B2 / gd).write_text('guard of another link' + NL)
    n_lock = len(lockrows())
    rc, o = go2('k_03')
    ok &= case('GL%d RC5 (item 436 (b)(5)): the guard %s of another link -> rc 1 before the lock: no lock row, no attempt, no '
               'IN_ARM of s13, the guard kept' % (15 + k, gd), rc == 1 and 'return failed guard' in o and gd in o and
               len(lockrows()) == n_lock and not (B2 / 's15' / 'attempt_k_03.txt').exists() and
               not (B2 / 's15' / 'IN_ARM').exists() and (B2 / gd).exists())
    (B2 / gd).unlink()
rc, o = go2('k_03', mode='breakcx')
ok &= case('GL14 S9r2 observation 1: a failed return (the copy installed_pre gone) -> rc 1, RETURN_FAILED written, IN_ARM KEPT '
           '(a later return of the same run does not remove it), the lock released', rc == 1 and
           (B2 / 's15' / 'RETURN_FAILED').exists() and (B2 / 's15' / 'IN_ARM').exists() and not Path(LOCK2).exists())
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
