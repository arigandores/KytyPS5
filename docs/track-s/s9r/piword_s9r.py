"""piword_s9r.py - S9r: sc_s9.pi_word against an independent encoding of item 355 (g)(1)-(3) and item 362 (v), all 16 series
combinations x 4 load combinations (64 cases).  No process, no file."""
import importlib.util
import itertools

spec = importlib.util.spec_from_file_location('sc9', 'C:/kyty/s288/s9/sc_s9.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def mine(w1, r1, w0, r0, l1, l0):
    both = l1 and l0
    if r1 and not r0:
        return 'READ_1'                                  # (1): a series in pi_r1, none in pi_r0 (no load condition)
    if (not (w1 or r1 or w0 or r0)) or (r1 and r0):
        return 'READ_2' if both else 'READ_OTHER'        # (2): none in the four, or in both R; AND both R loaded
    if r0 and not r1:
        return 'READ_3' if both else 'READ_OTHER'        # (3): only in pi_r0 among R (with or without W, item 362 (v))
    if (w1 or w0) and not r1 and not r0:
        return 'READ_3' if both else 'READ_OTHER'        # (3): only in W arms
    return 'READ_OTHER'


bad = 0
n = 0
for w1, r1, w0, r0, l1, l0 in itertools.product((False, True), repeat=6):
    hz = dict(pi_w1=w1, pi_r1=r1, pi_w0=w0, pi_r0=r0)
    got = S.pi_word(hz, {'pi_r1': l1, 'pi_r0': l0})
    want = mine(w1, r1, w0, r0, l1, l0)
    n += 1
    if got != want:
        bad += 1
        print('DIFF', hz, l1, l0, got, want)
print('pi_word cases %d, differences %d -> %s' % (n, bad, 'ALL OK' if bad == 0 else 'DIVERGENCE'))
