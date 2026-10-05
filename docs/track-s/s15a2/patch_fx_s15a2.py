"""patch_fx_s15a2.py - track S, link S15a2 (HPP-615; ROADMAP "SESSION 122" item 528 (b)(2)-(3)): inserts the fixtures H7, H8, M1
(fx_block_s15a2.txt) into s15/test_enter_scene_s15.py and the hand mutants e19-e21 (hmut_block_s15a2.txt) into s15/hmut_s15.py.
Exact anchors, each once; refuses when the lock exists; LF, ASCII.
    python patch_fx_s15a2.py
"""
import hashlib
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
D = 'C:/kyty/s288/s15'
HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)
FILES = {
    D + '/test_enter_scene_s15.py': ('102139070602c10c79f5d6fa8717d7a69ea42d44a1a489c8bf36084128e36ac1', [
        ("the cause \"met\", \"cap\", \"game ended\"; the json fields hold_end / hold_rule; without --hold-u the S9 hold.  Part 3 - the replay of\n",
         "the cause \"met\", \"cap\", \"game ended\"; the json fields hold_end / hold_rule; without --hold-u the S9 hold; S15a2 (HPP-615, item 528\n"
         "(b)(1)-(2)): the torn row of the probe P1 of S15r in the hold loop (H7) and in the poll after it (H8) -> the cause \"error ValueError\",\n"
         "the game closed, hold_exit recorded; main() with it (M1) -> <tag>.json full.  Part 3 - the replay of\n"),
        ("src = Path(SRC).read_text(encoding='ascii')\n", '@BLOCK@' + "src = Path(SRC).read_text(encoding='ascii')\n"),
    ], 'fx_block_s15a2.txt'),
    D + '/hmut_s15.py': ('87d52970552d11a275483735d467a12724a17eeb39c29d5aa3f37b43a58cc01c', [
        ("(argv[1]); a mutant must make the suite FAIL (rc != 0 and no \"ALL OK\").",
         "(argv[1]); a mutant must make the suite FAIL (rc != 0 and no \"ALL OK\").  S15a2 (HPP-615, item 528 (b)(3)): e19-e21."),
        ("    ('e18_parse_order', \"    if mn > cap or cap <= 0:\", \"    if cap <= 0:\"),\n]\n",
         "    ('e18_parse_order', \"    if mn > cap or cap <= 0:\", \"    if cap <= 0:\"),\n" + '@BLOCK@' + "]\n"),
    ], 'hmut_block_s15a2.txt'),
}


def main():
    if os.path.exists(LOCK):
        print('LOCKED - nothing written')
        return 5
    out = {}
    for path, (want, reps, block) in FILES.items():
        raw = open(path, 'rb').read()
        if hashlib.sha256(raw).hexdigest() != want:
            print('STOP: %s sha256 %s != %s' % (path, hashlib.sha256(raw).hexdigest(), want))
            return 1
        t = raw.decode('ascii')
        b = open(os.path.join(HERE, block), 'rb').read().decode('ascii').replace(chr(13), '')
        for k, (old, new) in enumerate(reps, 1):
            if t.count(old) != 1:
                print('STOP: %s anchor %d occurs %d times' % (path, k, t.count(old)))
                return 1
            t = t.replace(old, new.replace('@BLOCK@', b))
        t.encode('ascii')
        out[path] = t
    if os.path.exists(LOCK):
        print('LOCKED before the write - nothing written')
        return 5
    for path, t in out.items():
        with open(path, 'w', encoding='ascii', newline=NL) as f:
            f.write(t)
        print('PATCHED %s sha256 %s' % (path, hashlib.sha256(t.encode('ascii')).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
