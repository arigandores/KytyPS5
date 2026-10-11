"""F42c (HPP-781): regression of f42c_read.py on the real artefacts of the nearest forms (read-only), three sources:
  fs13_v (FS13c, binary FS13 abab2196, no KYTY_FIX_*, installed FS12 46892c20)   read as f20_v
  fs13_w (FS13c, the same, --vulkan-validation true)                                read as f20_w
  fs4_hb (FS4c, binary FS4 31cbfee8, -lvl hoover_beach, --shader-validation true)  read as f20_hb - the scene part only
Expected for fs13_v / fs13_w: admission FAILS exactly on 5 members - json binary_sha256, installed during the tag, installed before = after
(FS12, not FS13), env (missing KYTY_FIX_F20) and the series member (no series_taken / same_cmp file in FS13c) - and nothing else; the
members read on the same log (members() called directly): every member of both groups YES except the FixF20 ones (no FixF20 line in FS13 -
live members): f20_v - 'FixF20: mode=1', the three exit-line members and N1; f20_w - N1, 'FixF20: mode=1' and the two exit-line members.
fs4_hb: the hoover_beach entry line, the first scene frame and the hold equal the FS4c reader (entry line 345794, first scene frame n 211,
hold 335.9 s, frames >= 1 s 0; seal of FS4c runs/fs4_hb/read.txt) - the level hoover_beach of f20_hb is read by the same rule; the
admission rows are printed (FS4 has no LogAsync / FixB12 / FixB13 / FixF21 lines and runs --shader-validation true - not a check).
Last line ALL OK.  ASCII only.
usage: python regress_f42c.py [<f42c_read.py>]"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f42c_read.py')
_spec = importlib.util.spec_from_file_location('f42c_read_r', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def pmap(root, tag, seal, binp):
    D = root + '/runs/' + tag
    p = dict((nm, D + '/' + nm + '.txt') for nm in ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level',
                                                    'sheet', 'series_taken', 'same_cmp'))
    p.update(log=root + '/log_%s.txt' % tag, stdout=root + '/stdout_%s.txt' % tag, run=root + '/%s.json' % tag,
             idx=root + '/rec_%s.mp4.idx' % tag, seal=root + '/' + seal, bin=binp, cache_before=D + '/cache_before.tsv',
             cache_after=D + '/cache_after.tsv')
    return p


print('suite regress_f42c.py sha256 %s target f42c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
ok = True
FS13C = 'C:/kyty/f287/fs13c'
want_adm = ('json binary_sha256', 'installed during the tag', 'installed before = after', 'env = the form')
for src, tag, ser, want_no in (
        ('fs13_v', 'f20_v', 'series snapshot taken', ('FixF20: mode=1', 'FixF20Stat exit line: unmatched 0',
                                                      'FixF20Stat exit line: modules_bound = modules', 'FixF20Stat exit line: rewritten',
                                                      'N1 (item 705 (v))')),
        ('fs13_w', 'f20_w', 'caches before the tag = after', ('N1 (item 705 (v))', 'FixF20: mode=1', 'FixF20Stat exit line: unmatched 0',
                                                              'FixF20Stat exit line: modules_bound = modules'))):
    p = pmap(FS13C, src, 'pred/fs13c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_abab2196.exe')
    r = R.read_tag(tag, p)
    bad = [a for a, b in r['admission'] if not b]
    print('%s (from log_%s.txt): admission failed members %d' % (tag, src, len(bad)))
    for a in bad:
        print('  NO %s' % a)
    c = r['status'] == 'NOT_ADMITTED' and len(bad) == 5 and all(any(a.startswith(w) for a in bad) for w in want_adm)
    c = c and any(a.startswith(ser) for a in bad) and any('missing KYTY_FIX_F20' in a for a in bad) and any('46892c20' in a for a in bad)
    print('  admission as expected: %s' % c)
    ok &= c
    kind = R.kind_of(R.base_of(tag))
    x = R.scan(p['log'], R.LEVEL_OF[kind])
    att = json.load(open(p['run']))['attempts'][-1]
    idx_n = sum(1 for _ in open(p['idx'], 'rb')) if os.path.exists(p['idx']) else None
    gl = None
    if os.path.exists(p['glitch']):
        mg = R.RX_GL.search(open(p['glitch']).read())
        gl = int(mg.group(1)) if mg else None
    so = R.stdout_scan(p['stdout'])
    m, f, info = R.members(kind, x, att, idx_n, gl, 'sheet', so)
    for a, b in m + f:
        print('  [%s] %s' % ('YES' if b else 'NO', a[:150]))
    mno = [a for a, b in m + f if not b]
    c = len(mno) == len(want_no) and all(any(a.startswith(w) for a in mno) for w in want_no)
    print('  members as expected (only the FixF20 members and N1 NO): %s' % c)
    ok &= c
    fr = r['f20_rows']
    print('  rows: prep ms %s; PipelinePrecache %s lines; Vulkan pipeline cache %s lines; FixF20Stat lines %s; quit line %s' % (
        fr['prep_ms'], fr['precache_n'], fr['vk_pipeline_cache_n'], fr['f20stat_lines'], x['quit_ln']))
    c = fr['f20stat_lines'] == 0 and fr['f20_mode_lines'] == 0 and fr['precache_n'] >= 1 and len(fr['prep_ms']) == 1 and x['quit_ln'] is not None
    print('  rows as expected (no FixF20 line in FS13; precache and preparation lines present; Event: quit present): %s' % c)
    ok &= c
# fs4_hb as f20_hb: the scene part
p = pmap('C:/kyty/f287/fs4c', 'fs4_hb', 'pred/fs4c_seal.md', 'C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe')
r = R.read_tag('f20_hb', p)
print('f20_hb (from log_fs4_hb.txt): status %s; admission failed members %d (rows, FS4 form)' % (r['status'], len([a for a, b in r['admission'] if not b])))
for a, b in r['admission']:
    if not b:
        print('  NO %s' % a[:150])
x = R.scan(p['log'], R.HB)
i, hold, ge1, ge1_with_first, info = R.scene(x)
print('  entry line %s; first scene frame n %s; hold %.1f s; frames >= 1 s %d' % (x['entry_ln'], info['first_scene_n'], hold / 1e6, ge1))
c = x['entry_ln'] == 345794 and info['first_scene_n'] == 211 and info['hold_s'] == 335.9 and ge1 == 0
print('  scene part = FS4c reader (345794 / 211 / 335.9 / 0): %s' % c)
ok &= c
xs = R.scan(p['log'], R.SKY)
print('  the same log read with the Sky Garden level: entry line %s (no Sky Garden entry in fs4_hb)' % xs['entry_ln'])
ok &= xs['entry_ln'] is None
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
