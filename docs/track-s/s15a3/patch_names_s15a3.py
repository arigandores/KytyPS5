"""patch_names_s15a3.py - track S, link S15a3 (HPP-617; ROADMAP "SESSION 122" item 529 (b)(1), (3)): the names of the seal and
of its edition in the code of S15 -> pred/16_s.md / pred/16b_s.md.  Exact anchors, each with its expected count; nothing else
changes (the logic, the members, the constants of the rules; enter_scene_s15.py is not touched).  The fixture of the edge G18e
of test_go_s15.py (item 529 (b)(3)) is inserted after G18d.  Refuses when the lock or the stop file exists.  LF, ASCII.
    python patch_names_s15a3.py
"""
import hashlib
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
D = 'C:/kyty/s288/s15'
NL = chr(10)
if os.path.exists(LOCK) or os.path.exists(STOP):
    print('STOP: the lock or the stop file exists')
    sys.exit(5)

G18E = NL.join([
    "sp_rc = {}",
    "for sp in ('pred/14_s.md', 'pred/14b_s.md', 'pred/15_s.md', 'pred/15b_s.md', 'pred/16_s.md', 'pred/16b_s.md'):",
    "    (B3 / 's15' / 'sc_s15.py').write_text(NL.join(['import sys', 'a = sys.argv[1:]', \"if a[:1] == ['--seal-path']:\",",
    "                                                   '    print(%r)' % sp, '    sys.exit(0)',",
    "                                                   \"print('s15 lvl T u 300 - 100 600 1 0 -')\", 'sys.exit(0)', '']),",
    "                                          encoding='ascii')",
    "    sp_rc[sp] = go('u_01', dry='2', base=B3)",
    "ok &= case('G18e S15a3 (item 529 (b)(3)): the seal path of --seal-path pred/14_s.md, pred/14b_s.md, pred/15_s.md or '",
    "           'pred/15b_s.md -> rc 1 \"seal path bad\" before the lock, no plan; pred/16_s.md and pred/16b_s.md -> rc 0, the DRY=2 plan '",
    "           'names that seal', all(sp_rc[s][0] == 1 and 'seal path bad' in sp_rc[s][1] and 'PLAN ' not in sp_rc[s][1]",
    "                                  for s in ('pred/14_s.md', 'pred/14b_s.md', 'pred/15_s.md', 'pred/15b_s.md')) and",
    "           all(sp_rc[s][0] == 0 and sp_rc[s][1].startswith('PLAN u_01: link s15, seal %s, ' % s)",
    "               for s in ('pred/16_s.md', 'pred/16b_s.md')) and not Path(FXLOCK).exists())",
    ""])
G18D_END = "           all(hu_rc[f][0] == 2 and 'bad hold rule' in hu_rc[f][1] for f in ('x', '120:3000', '', '1x:2:3', '120:3000:300x')))" + NL
DOC_GO = 'The first output line names this suite and the harness by sha256; the output ends with ALL OK.' + NL
DOC_GO_NEW = ('S15a3 (HPP-617, item 529 (b)(1), (3)): the names of the seal are pred/16_s.md / pred/16b_s.md; G18e - the seal path of '
              'the harness:' + NL + 'pred/14_s.md, pred/14b_s.md, pred/15_s.md, pred/15b_s.md -> rc 1 "seal path bad"; pred/16_s.md, '
              'pred/16b_s.md -> the plan.' + NL + DOC_GO)

PLAN = {
    'sc_s15.py': [
        ("SEAL_BASE = 'C:/kyty/s288/pred/14_s.md' ", "SEAL_BASE = 'C:/kyty/s288/pred/16_s.md' ", 1),
        ("SEAL_B = 'C:/kyty/s288/pred/14b_s.md' ", "SEAL_B = 'C:/kyty/s288/pred/16b_s.md' ", 1),
        ("SEAL_BASE_REL = 'pred/14_s.md' ", "SEAL_BASE_REL = 'pred/16_s.md' ", 1),
    ],
    'go_s15.sh': [
        ('  pred/14_s.md|pred/14b_s.md) ;;' + NL, '  pred/16_s.md|pred/16b_s.md) ;;' + NL, 1),
        ('the seal path is not pred/14_s.md or pred/14b_s.md ($PRED)', 'the seal path is not pred/16_s.md or pred/16b_s.md ($PRED)', 1),
    ],
    'test_sc_s15.py': [
        ('14b_s.md', '16b_s.md', 3),
        ('14_s.md', '16_s.md', 10),
    ],
    'test_go_s15.py': [
        ('14b_s.md', '16b_s.md', 7),
        ('14_s.md', '16_s.md', 7),
        (G18D_END, G18D_END + G18E, 1),
        (DOC_GO, DOC_GO_NEW, 1),
    ],
    'mut_sc_s15.py': [
        ('# item 436 (b)(6), RC6: the line "edition: base pred/14_s.md sha256 <sha>"',
         '# item 436 (b)(6), RC6: the line "edition: base pred/16_s.md sha256 <sha>"', 1),
        ("('ed6_rel', \"SEAL_BASE_REL = 'pred/14_s.md' \", \"SEAL_BASE_REL = 'pred/13_s.md' \"),",
         "('ed6_rel', \"SEAL_BASE_REL = 'pred/16_s.md' \", \"SEAL_BASE_REL = 'pred/15_s.md' \"),", 1),
    ],
}

new = {}
for name, reps in PLAN.items():
    p = D + '/' + name
    raw = open(p, 'rb').read()
    t = raw.decode('ascii')
    if chr(13) in t:
        print('STOP: CR in %s' % name)
        sys.exit(1)
    before = hashlib.sha256(raw).hexdigest()
    for old, rep, want in reps:
        c = t.count(old)
        if c != want:
            print('STOP: %s: anchor found %d times (want %d): %r' % (name, c, want, old[:100]))
            sys.exit(1)
        t = t.replace(old, rep)
    for bad in ('14_s.md', '14b_s.md') if name in ('test_sc_s15.py', 'mut_sc_s15.py') else ():   # G18e names 14 / 15 itself
        if bad in t:
            print('STOP: %s still names %s' % (name, bad))
            sys.exit(1)
    new[name] = (before, t.encode('ascii'))
for name, (before, b) in new.items():
    open(D + '/' + name, 'wb').write(b)
    print('PATCHED s15/%s %s -> %s' % (name, before, hashlib.sha256(b).hexdigest()))
print('DONE %d files' % len(new))
