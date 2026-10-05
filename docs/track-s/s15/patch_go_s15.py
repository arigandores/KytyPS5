"""patch_go_s15.py - S15a (HPP-601): the changes of item 511 (z)(3)-(4) on the mechanical port go_s15.sh.  Every anchor once.
    python patch_go_s15.py <go_s15.sh>
"""
import sys

NL = chr(10)
P = sys.argv[1]
t = open(P, 'rb').read().decode('ascii').replace(chr(13) + NL, NL)
R = [
    ('''#!/bin/bash
# Track S, link S13a (HPP-498;''', '''#!/bin/bash
# Track S, link S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)): the port of s13/go_s13.sh (seal 13) for link S15b - the
# directory C:/kyty/s288/s15, the seal pred/14_s.md or its edition pred/14b_s.md (pred/13_s.md and pred/13b_s.md are not in force
# for these arms); item 511 (z)(3): the collection arms hold 300 s (sc_s15.py HOLD_K); item 511 (z)(4)-(5): a U arm runs
# s15/enter_scene_s15.py with --hold-u <the 11th field of its plan> (120:3000:300 - held while the presented time after the first
# scene frame (or the entry line) is < 120 s or the video < 3 000 frames, at most 300 s); k_NN and w13 carry "-" (a fixed hold).
# Everything else is the S13 harness unchanged; its header follows.
# Port header: Track S, link S13a (HPP-498;'''),
    ('''# S13a4 (HPP-553, item 452 (d)(2)): the seal in force is pred/14_s.md or its edition pred/14b_s.md (pred/14_s.md and
# pred/11_s.md are not in force).''', '''# S13a4 (HPP-553, item 452 (d)(2)): the seal in force was pred/13_s.md or its edition pred/13b_s.md (pred/12_s.md and
# pred/11_s.md were not in force); S15a: pred/14_s.md or pred/14b_s.md.'''),
    ('ENTERPY=$ROOT/s9/enter_scene_s9.py', 'ENTERPY=$ROOT/s15/enter_scene_s15.py'),
    ('LEVEL=$2; CLS=$3; MODE=$4; HOLD=$5; SRC=$6; SDRAWS=$7; TOUT=$8; REC=$9; VAL=${10}',
     'LEVEL=$2; CLS=$3; MODE=$4; HOLD=$5; SRC=$6; SDRAWS=$7; TOUT=$8; REC=$9; VAL=${10}; HU=${11:-}\n'
     'if [ "$HU" = "-" ]; then HUX=""\n'
     'elif [[ "$HU" =~ ^[0-9]+:[0-9]+:[0-9]+$ ]]; then HUX="--hold-u $HU"\n'
     'else log0 "go_s15.sh $T refused: the hold rule field of the plan is not N:N:N or - ($PLAN)"; echo "bad hold rule"; exit 2\n'
     'fi'),
    ('--pred $ROOT/$PRED $RECX --hold $HOLD $VALX KYTY_GPU_CLOCK_PIN=1',
     '--pred $ROOT/$PRED $RECX --hold $HOLD $HUX $VALX KYTY_GPU_CLOCK_PIN=1'),
]
for old, new in R:
    c = t.count(old)
    if c != 1:
        print('STOP: anchor found %d times: %r' % (c, old[:120]))
        sys.exit(1)
    t = t.replace(old, new)
t.encode('ascii')
open(P, 'wb').write(t.encode('ascii'))
print('PATCHED %s: %d replacements' % (P, len(R)))
