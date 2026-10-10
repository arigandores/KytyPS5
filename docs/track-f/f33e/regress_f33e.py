"""F33e (HPP-746): regression of f33e_read.py on the real artefacts of fs11_v (FS11c, HPP-716: the same form on the installed FS11
ea51ae80, no KYTY_FIX_F21; the FS11 binary has no FixF21 line).  Expected: admission FAILS on the binary members (json binary, installed
during the tag = ea51ae80, installed before / after = FS10 abfded5e) and on the env (KYTY_FIX_F21 missing), nothing else; the members
read on the same log (members() called directly): every member of item 675 (d)(4) YES except 'FixF21: mode=1' (no line on FS11); every
member of the form fs11_v YES; the exit rows = the fs11_v json (close_rc 0, close_s 4.1).  Last line ALL OK.  ASCII only.
usage: python regress_f33e.py [<f33e_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f33e_read.py')
_spec = importlib.util.spec_from_file_location('f33e_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)
FS = 'C:/kyty/f287/fs11c'
D = FS + '/runs/fs11_v'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_f33e.py sha256 %s target f33e_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
p = dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
         glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
         log=FS + '/log_fs11_v.txt', stdout=FS + '/stdout_fs11_v.txt', run=FS + '/fs11_v.json', idx=FS + '/rec_fs11_v.mp4.idx',
         seal=FS + '/pred/fs11c_seal.md', bin='C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe')
ok = True
r = R.read_tag('f21_v', p)
bad = [a for a, b in r['admission'] if not b]
print('admission failed members: %d' % len(bad))
for a in bad:
    print('  NO %s' % a)
want = ('json binary_sha256', 'installed during the tag', 'installed before = after', 'env = the form')
ok &= r['status'] == 'INTERFERENCE' and len(bad) == 4 and all(any(a.startswith(w) for a in bad) for w in want)
ok &= any('missing KYTY_FIX_F21' in a for a in bad)
x = R.scan(p['log'])
att = json.load(open(p['run']))['attempts'][-1]
idx_n = sum(1 for _ in open(p['idx'], 'rb'))
gl = int(R.RX_GL.search(open(p['glitch']).read()).group(1))
so = R.stdout_scan(p['stdout'])
m, f, info = R.members(x, att, idx_n, gl, 'sheet', so)
for a, b in m + f:
    print('  [%s] %s' % ('YES' if b else 'NO', a))
mno = [a for a, b in m if not b]
ok &= len(mno) == 1 and mno[0].startswith('FixF21: mode=1')
ok &= all(b for a, b in f)
ok &= info['quit_ln'] is not None and info['fatal_after_quit'] == 0 and info['expired_log'] == 0 and info['expired_stdout'] == 0
ok &= r['exit']['close_rc'] == 0 and r['exit']['close_killed'] is False and r['exit']['close_s'] == 4.1
print('info hold_s %s frames_ge1s %s scene_frames %s quit_ln %s close_rc %s close_s %s' % (
    info['hold_s'], info['frames_ge1s'], info['scene_frames'], info['quit_ln'], r['exit']['close_rc'], r['exit']['close_s']))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
