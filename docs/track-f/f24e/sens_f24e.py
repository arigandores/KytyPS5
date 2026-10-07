"""Manual sensitivity of the suite test_f24e_read.py (F24e HPP-664; form of F15e sens_f15e.py): each edit of f24e_read.py below must make
the suite fail (exit != 0).  Prints one line per edit (CAUGHT / MISSED) and ALL OK when every edit is caught.  ASCII only.
usage: python sens_f24e.py"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f24e_read.py')
SUITE = os.path.join(HERE, 'test_f24e_read.py')
EDITS = [
    ("BIN_EXPECT = '91f155b7", "BIN_EXPECT = '2c9b69b9"),
    ("VERSION = b'KytyPS5-2026-09-15-6a2987a-1899-gfbae3a68'", "VERSION = b'KytyPS5-2026-09-15-6a2987a-1897-g0005e11f'"),
    ("WANT = 'b3cee576", "WANT = '2c9b69b9"),
    ("if env.get('KYTY_FIX_B13') != '1':", "if env.get('KYTY_FIX_B13') not in ('0', '1'):"),
    ("if k.startswith('KYTY_FIX_') and k != 'KYTY_FIX_B13']", "if k.startswith('KYTY_FIX_X')]"),
    ("NO_ENV = ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS', 'KYTY_SHADER_SEED',", "NO_ENV = ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS',"),
    ("if vk.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') != LIMIT:", "if False:"),
    ("        if val != 'true':", "        if val is None:"),
    ("        bad += ['VK_LAYER_* %s' % k for k in sorted(vk)]", "        pass"),
    ("and all(mm == 1 for _, mm in r['b13'])", "and r['b13'][0][1] == 1"),
    ("and r['guest_first'] is not None and r['b13'][0][0] < r['guest_first'])", "and r['guest_first'] is not None)"),
    ("if md and int(md.group(1)) >= 100:", "if md and int(md.group(1)) >= 99:"),
    ("if dt >= K2_US:", "if dt > K2_US:"),
    ("HOLD_V_US = 300000000", "HOLD_V_US = 299999999"),
    ("HOLD_W_S = 310", "HOLD_W_S = 300"),
    ("elif r['scene_change_line'] is None:", "elif False:"),
    ("lived_v = att.get('outcome') == 'ok' and att.get('hold_exit') is None", "lived_v = att.get('outcome') == 'ok'"),
    ("DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---',", "DEATH = (b'Unhandled exception:', b'--- Fatal Error ---',"),
    ("death.append(('stdout', d.decode(), i))", "pass"),
    ("VIDEO_MIN = 3000", "VIDEO_MIN = 2999"),
    ("res['glitches'] == 0)", "res['glitches'] <= 1)"),
    ("if b'[Vulkan][E]' in raw:", "if b'[Vulkan][E] X' in raw:"),
    ("r['vk_limit'] += 1", "pass"),
    ("res['dual_ok']),", "True),"),
    ("and x[0] < r['guest_first'] and x[1] == 1 and x[2] == 1]", "and x[1] == 1]"),
    ("validation_stop=None if lived_w is None else (r['vke'] > 0 and not lived_w),", "validation_stop=False,"),
    ("mc.startswith('manifest cmp EQUAL')", "mc.startswith('manifest cmp')"),
    ("not res['win'].get('minimized') and not res['recovering'] and not res['gamepatch']", "not res['win'].get('minimized') and not res['recovering']"),
    ("lived_w = lived_v and (att.get('hold_s') or 0) >= HOLD_W_S", "lived_w = lived_v"),
    ("entered = r['entry_line'] is not None and att.get('outcome') == 'ok'", "entered = r['entry_line'] is not None"),
]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    print('suite sens_f24e.py sha256 %s target f24e_read.py sha256 %s suite test_f24e_read.py sha256 %s' % (
        sha(os.path.abspath(__file__)), sha(TARGET), sha(SUITE)))
    src = open(TARGET, 'rb').read().decode('ascii')
    tmp = tempfile.mkdtemp(prefix='f24e_sens_')
    missed = 0
    try:
        base = subprocess.run([sys.executable, SUITE, TARGET], capture_output=True)
        ok0 = base.returncode == 0 and b'ALL OK' in base.stdout
        print('control (unchanged reader): %s' % ('PASS' if ok0 else 'FAIL'))
        if not ok0:
            missed += 1
        for i, (a, b) in enumerate(EDITS, 1):
            n = src.count(a)
            if n != 1:
                print('edit %02d: anchor found %d times - BAD EDIT' % (i, n))
                missed += 1
                continue
            mp = os.path.join(tmp, 'f24e_read.py')
            open(mp, 'wb').write(src.replace(a, b).encode('ascii'))
            p = subprocess.run([sys.executable, SUITE, mp], capture_output=True)
            caught = p.returncode != 0
            fails = [x for x in p.stdout.decode('ascii', 'replace').split('\n') if x.startswith('FAIL ')]
            print('edit %02d: %s (%d failing checks) | %s' % (i, 'CAUGHT' if caught else 'MISSED', len(fails), a[:70]))
            if not caught:
                missed += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('edits %d missed %d' % (len(EDITS), missed))
    print('ALL OK' if missed == 0 else 'FAILED')
    return 0 if missed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
