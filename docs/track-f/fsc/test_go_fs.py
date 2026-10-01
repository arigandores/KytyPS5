"""test_go_fs.py - fixtures of go_fs.sh (FSc, HPP-370): the static form of the script (constants of p.282(g)(3), p.281(g),
p.286(v) N1, p.273(k)(2): binary copy dac02fb9, no KYTY_FIX_* except fs_d KYTY_FIX_B1B=0, W form with precache by default and
the F6 filter, holds, binary check before every tag, cache and directory lists, GLCache return, lock window, seal call, pair
sheets against v142 and f4c_g, stop rules) and the cheap refusals: usage, not configured, seal call line, one attempt, lock
held, stop file, DRY plan, missing shipment binary.  A copy of the script with LOCK, STOPF, TIMES and ROOT moved into fx/go -
no real lock, no guard, no install, no game.  Last line: ALL OK."""
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, 'fx', 'go').replace('\\', '/')
BASH = 'C:/Program Files/Git/bin/bash.exe'
N = [0]
FAIL = []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL %s %s' % (name, detail))


def unix(p):
    return '/' + p[0].lower() + p[2:] if p[1] == ':' else p


def case_body(s, tag):
    i = s.index('    %s) ' % tag)
    return s[i:s.index(';;', i)]


src = open(os.path.join(HERE, 'go_fs.sh'), 'rb').read().decode('ascii')
code = '\n'.join(l for l in src.split('\n') if not l.startswith('#') and not l.startswith('  echo "DRY'))
print('suite test_go_fs.py sha256 %s target go_fs.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_fs.sh'))))
check('script is ASCII', all(ord(c) < 128 for c in src))
check('script is LF', '\r' not in src)
check('KYTY_GPU_CHECKPOINTS never set', 'KYTY_GPU_CHECKPOINTS=' not in src)
check('every run KYTY_GPU_CLOCK_PIN=1', src.count('KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 >') == 1)
check('no mutlib word in a command', 'mutlib ' not in src.replace("'mut_[a-z0-9_]*|test_[a-z0-9_]*fs|mutlib'", ''))
check('no tail -F', 'tail -F' not in src)
check('restore in the EXIT trap', 'trap finish EXIT' in src and 'restore_bin' in src)
check('p.286(v) N1 binary constant = FSa copy dac02fb9', 'BIN_FS="C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe"\n' in src
      and 'BIN_EXPECT="dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e"\n' in src)
check('FSb rebuild 2fc78597 never named', '2fc78597' not in src)
check('installed build constant 9235a7ac and its pinned copy', 'BUILD_EXPECT="9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7"\n' in src
      and 'BUILD_PINNED="/c/kyty/s128/kyty_emulator_9235a7ac.exe"\n' in src)
check('binary check before every tag', src.index('binary check failed (p.286(v) N1)') > src.index('for C in $SEQ; do\n  if [ -e $STOPF ]')
      and '[ "$(sha "$BIN_FS")" != "$BIN_EXPECT" ] || [ "$(sha "$GAME")" != "$BIN_EXPECT" ]' in src)
check('no build command', 'build_local' not in src and 'cmake' not in src and 'ninja' not in src)
check('GLRESTORE=1', 'GLRESTORE="1"\n' in src)
check('failed return writes the stop file', src.count('RETFAIL=1') == 7 and '> $STOPF' in src)
check('_PipelineCache moved and returned, never rm -rf (member [I])', 'rm -rf "$PCDIR"' not in src and 'mv "$PCDIR" "$PCKEEP/"' in src
      and '[ "$PCB" = "$PC_BEFORE" ]' in src and '[ "$PC_SNAP" = "$PC_BEFORE" ]' in src and src.index('PCSNAPPED=1') < src.index('INSTALLED=1' + chr(10) + 'cp'))
check('p.277(b)(2) directory list before and after', 'DIRS_BEFORE=$(dirlist "$CACHE")' in src and
      '[ "$DIRS_BACK" = "$DIRS_BEFORE" ]' in src and '[ "$DIRS_SNAP" = "$DIRS_BEFORE" ]' in src)
check('cache is moved, never rm -rf on the game cache', 'rm -rf "$CACHE"' not in src and 'mv "$CACHE" "$KEEP/"' in src)
check('GLCache is moved, never rm -rf', 'rm -rf "$GLDIR"' not in src and 'mv "$GLDIR" "$GLKEEP/"' in src)
check('lock window right before the lock', src.index('win_fs.py 2>&1') < src.index('set -o noclobber')
      and src.index('busy "stop file $STOPF appeared before the lock"') < src.index('win_fs.py 2>&1'))
check('window closed or unknown -> busy', '*"-> open") ;;' in src and 'busy "lock window closed or unknown' in src)
check('seq of p.282(g)(3)', 'SEQ="fs_a fs_b fs_v fs_g fs_d"\n' in src)
check('levels', 'SKY=underwater_aerial_garden\n' in src and 'MGG=mini_giants_garden\n' in src)
check('holds 330 / 310', 'VHOLD="330"\n' in src and 'WHOLD="310"\n' in src)
check('F6 filter and duplicate limit as sc145', 'VKFILTER="Undefined-Value-ShaderOutputNotConsumed-DynamicRendering"\n' in src
      and 'VKDUP="1000000"\n' in src and
      'WX="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP VK_LAYER_MESSAGE_ID_FILTER=$VKFILTER"' in src)
for t, lv in (('fs_a', '$SKY'), ('fs_v', '$MGG')):
    b = case_body(src, t)
    check('%s W: level %s, validation, hold 310, the layer env, no video, no knob' % (t, lv),
          'LV=%s;' % lv in b and 'HOLD=$WHOLD' in b and '--emu-arg=--vulkan-validation --emu-arg=true' in b and 'EXTRA="$WX"' in b
          and 'REC=' not in b and 'KYTY_' not in b and '--timeout 600' in b, b)
for t, lv in (('fs_b', '$SKY'), ('fs_g', '$MGG')):
    b = case_body(src, t)
    check('%s V: level %s, video, hold 330, stable 300, no validation, no knob' % (t, lv),
          'LV=%s;' % lv in b and 'HOLD=$VHOLD' in b and 'REC="--rec"' in b and 'vulkan' not in b and 'EXTRA' not in b
          and '--stable-draws 300' in b, b)
b = case_body(src, 'fs_d')
check('fs_d V Sky Garden KYTY_FIX_B1B=0 exactly, no video, hold 330, variant directory variant_fixb26',
      'LV=$SKY' in b and 'EXTRA="KYTY_FIX_B1B=0"' in b and 'REC=' not in b and 'HOLD=$VHOLD' in b and 'VDIR=variant_fixb26' in b, b)
check('KYTY_FIX_* passed only in fs_d (outside the header and the DRY line)', code.count('KYTY_FIX_') == code.count('unset KYTY_GATE_SCHEDULE') * 4 + 1
      and code.count('KYTY_FIX_B1B=0') == 1, code.count('KYTY_FIX_'))
check('KYTY_PIPELINE_PRECACHE never passed (precache by default, p.281(g))', 'KYTY_PIPELINE_PRECACHE=' not in src)
check('EXTRA reset before every tag', 'REC=""; EMUX=""; EXTRA=""' in src)
check('knob and layer variables unset at the start', 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_B1B KYTY_FIX_DUALSRC KYTY_FIX_MINIMIZE' in src
      and 'VK_LAYER_MESSAGE_ID_FILTER VK_LAYER_DUPLICATE_MESSAGE_LIMIT\n' in src)
check('pair sheet b against v142, g against f4c_g, sheet142 for g', 'REFV=C:/kyty/s142/rec_v142.mp4\n' in src and
      'REFG=C:/kyty/f287/f4c/rec_f4c_g.mp4\n' in src and 'if [ "$C" = "fs_b" ]; then REF=$REFV; else REF=$REFG; fi' in src and
      'sheetpair_f3d.py $REF rec_$C.mp4 sheetpair_$C.png' in src and 'sheet142.py rec_$C.mp4 sheet_$C.png' in src)
check('glitch 4 6 for every video', 'python $VIDGLITCH rec_$C.mp4 4 6' in src)
check('recipe file of the variant directory parsed before the tag when present', 'if [ -f "$CACHE/$VDIR/pipelines.bin" ]; then' in src
      and src.index('recipes143.py runs/recipes_$C.json') < src.index('runtag ""'))
check('stop check after every tag', 'fs_read.py --stop-check runs/$C.read.json' in src)
check('enter_scene rc != 0 stops unless a validation stop', 'series stop: enter_scene rc $RC' in src and '"continue: validation"*)' in src)
check('summary at the end', 'fs_read.py --summary > summary_fs.txt' in src)
check('one retry of a BUSY refusal', src.count('runtag ""' + chr(10)) == 1 and src.count('runtag " (retry after a BUSY refusal)"') == 1)
check('idle wait before every tag', src.index('if ! idlewait $C; then') < src.index('runtag ""'))
check('lock.log UTC lines', 'echo "lock taken series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src and
      'echo "lock released series $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $LOCKLOG' in src)
check('times lines UTC to C:/kyty/f287/times.txt', 'TIMES=/c/kyty/f287/times.txt\n' in src and 'date -u +%Y-%m-%dT%H:%M:%SZ) FSc go_fs' in src)


def make(binf='', bexp='', glr='', pred=None):
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    s = src.replace('ROOT=C:/kyty/f287/fsc', 'ROOT=%s' % FX)
    s = s.replace('LOCK=/c/kyty/SEALED_RUN.lock', 'LOCK=%s/LOCK' % unix(FX))
    s = s.replace('STOPF=/c/kyty/f287/STOP', 'STOPF=%s/STOP' % unix(FX))
    s = s.replace('TIMES=/c/kyty/f287/times.txt', 'TIMES=%s/times.txt' % unix(FX))
    s = re.sub(r'(?m)^BIN_FS=".*"$', 'BIN_FS="%s"' % binf, s, count=1)
    s = re.sub(r'(?m)^BIN_EXPECT=".*"$', 'BIN_EXPECT="%s"' % bexp, s, count=1)
    s = re.sub(r'(?m)^GLRESTORE=".*"$', 'GLRESTORE="%s"' % glr, s, count=1)
    open(os.path.join(FX, 'go_fs.sh'), 'wb').write(s.encode('ascii'))
    if pred is not None:
        os.makedirs(os.path.join(FX, 'pred'))
        open(os.path.join(FX, 'pred', '01_fs.md'), 'wb').write(pred.encode('ascii'))


def run(*args, env_add=None):
    env = dict(os.environ)
    env.pop('PLWAIT', None)
    env.pop('DRY', None)
    env.update(env_add or {})
    p = subprocess.run([BASH, FX + '/go_fs.sh'] + list(args), capture_output=True, env=env)
    return p.returncode, p.stdout.decode('ascii', 'replace')


CALL = 'go_fs call: PLWAIT=540 bash C:/kyty/f287/fsc/go_fs.sh series\n'
make()
rc, out = run()
check('usage rc 2', rc == 2 and 'usage' in out, (rc, out))
rc, out = run('fs_a')
check('a tag instead of series rc 2', rc == 2, (rc, out))
rc, out = run('series')
check('not configured rc 2', rc == 2 and 'not configured' in out, (rc, out))
make('x.exe', 'ab', '')
rc, out = run('series')
check('GLRESTORE empty -> not configured rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '1')
rc, out = run('series')
check('configured, no seal -> rc 1', rc == 1 and 'seal' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('DRY with the seal line rc 0', rc == 0 and out.startswith('DRY series'), (rc, out))
check('DRY plan names the tags, the knob of fs_d, the filter and the window', 'fs_a fs_b fs_v fs_g fs_d' in out and 'KYTY_FIX_B1B=0' in out and
      'VK_LAYER_MESSAGE_ID_FILTER=' in out and 'win_fs' in out and 'KYTY_PIPELINE_PRECACHE' not in out, out)
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='100'))
check('PLWAIT other than the seal rc 1', rc == 1, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='600'))
check('PLWAIT above 540 rc 2', rc == 2, (rc, out))
rc, out = run('series', env_add=dict(DRY='1', PLWAIT='x'))
check('PLWAIT not a number rc 2', rc == 2, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL + CALL)
rc, out = run('series', env_add=dict(DRY='1'))
check('two seal call lines rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL.replace('fsc/go_fs.sh', 'f3d/go_f3d.sh'))
rc, out = run('series', env_add=dict(DRY='1'))
check('another call line rc 1', rc == 1, (rc, out))
for t in ('fs_a', 'fs_d'):
    make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
    open(os.path.join(FX, 'attempt_%s.txt' % t), 'w').write('x')
    rc, out = run('series', env_add=dict(DRY='1'))
    check('attempt marker %s -> rc 1 (one attempt)' % t, rc == 1 and 'attempt' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
open(os.path.join(FX, 'fs_g.json'), 'w').write('{}')
rc, out = run('series', env_add=dict(DRY='1'))
check('a tag json -> rc 1', rc == 1, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
open(os.path.join(FX, 'LOCK'), 'w').write('someone')
rc, out = run('series', env_add=dict(DRY='1'))
check('lock held -> rc 4 before anything', rc == 4 and 'lock held' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
open(os.path.join(FX, 'STOP'), 'w').write('p.999')
rc, out = run('series', env_add=dict(DRY='1'))
check('stop file -> rc 4', rc == 4 and 'stop file' in out and 'p.999' in out, (rc, out))
make('x.exe', 'ab', '1', pred='# seal\n' + CALL)
rc, out = run('series')
check('configured, real path: missing shipment binary -> rc 1 before any lock', rc == 1 and 'shipment binary bad' in out
      and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
