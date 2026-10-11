"""F40c (HPP-772): regression of f40c_read.py on the real artefacts of the nearest form (read-only):
  fs12_v (FS12c, binary FS12 46892c20, no KYTY_FIX_F24, installed FS11 ea51ae80)   read as f24_n1
Expected: admission FAILS exactly on 5 members - json binary_sha256, installed during the tag, installed before = after (FS11, not FS12),
env (missing KYTY_FIX_F24), the line FixF24: mode=1 b24=1 (FS12 has no such line) - and nothing else; the members read on the same log
(judge_n1 called directly): every member YES except the three FixF24 members of the binary (init, init_owner alive, init_owner owners -
no such lines in FS12: live members) and the admission row; the form group fs12_v all YES; 0 'TestHidLoss:' lines.  Last line ALL OK.
ASCII only.
usage: python regress_f40c.py [<f40c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f40c_read.py')
_spec = importlib.util.spec_from_file_location('f40c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_f40c.py sha256 %s target f40c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
root = 'C:/kyty/f287/fs12c'
D = root + '/runs/fs12_v'
p = dict(installed_before=D + '/installed_before.txt', installed_after=D + '/installed_after.txt', manifest_cmp=D + '/manifest_cmp.txt',
         glitch=D + '/glitch.txt', installed_sha=D + '/installed_sha.txt', level=D + '/level.txt', sheet=D + '/sheet.txt',
         log=root + '/log_fs12_v.txt', stdout=root + '/stdout_fs12_v.txt', run=root + '/fs12_v.json', idx=root + '/rec_fs12_v.mp4.idx',
         seal=root + '/pred/fs12c_seal.md')
want = ('json binary_sha256', 'installed during the tag', 'installed before = after', 'env = the form', 'FixF24: mode=1 b24=1')
ok = True
r = R.read_tag('f24_n1', p)
bad = [a for a, b in r['admission'] if not b]
print('f24_n1 (from log_fs12_v.txt): admission failed members %d' % len(bad))
for a in bad:
    print('  NO %s' % a[:160])
c = r['status'] == 'NOT_ADMITTED' and len(bad) == len(want) and all(any(a.startswith(w) for a in bad) for w in want)
c = c and any('missing KYTY_FIX_F24' in a for a in bad) and any('ea51ae80' in a for a in bad)
print('  admission as expected: %s' % c)
ok &= c
x = R.scan(p['log'])
att = json.load(open(p['run']))['attempts'][-1]
so = R.stdout_scan(p['stdout'])
o, alive, same = R.owner_parts(x)
res = {}
word, mem, _ = R.judge_n1(x, att, so, o, alive, same, p, res)
for a, b in mem + [tuple(f) for f in res['form_members']]:
    print('  [%s] %s' % ('YES' if b else 'NO', a[:150]))
mno = [a for a, b in mem if not b]
c = (len(mno) == 3 and mno[0].startswith('FixF24: init before') and 'witness alive' in mno[1] and mno[2].startswith('init_owner hid = helper')
     and res['form_ok'] is True and word == 'WITNESS_DEAD')
print('  members as expected (only the three FixF24 members NO, form fs12_v ALL YES, word WITNESS_DEAD on FS12): %s (%s)' % (c, word))
ok &= c
c = x['thl'] == 0 and x['stand'] == 0 and so['stand'] == 0 and not x['mode'] and not x['owner']
print('  no TestHidLoss / ExitFatal / FixF24 lines in FS12: %s; %s' % (c, res.get('row_n1')))
ok &= c
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
