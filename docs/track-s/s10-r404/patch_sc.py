"""Item 404 (g): the domain identities T-1 / T-6 of an entered S10 arm in s9/sc_s9.py (LF, write_bytes)."""
import hashlib
import os
import shutil
import sys

P = 'C:/kyty/s288/s9/sc_s9.py'
ORIG = 'b8f5e3faed8c512873553293372e509e4ccfafaedb5d0e4d216da3ead580e39a'
b = open(P, 'rb').read()
if hashlib.sha256(b).hexdigest() != ORIG:
    sys.exit('sc_s9.py is not b8f5e3fa - refuse')
os.makedirs('C:/kyty/s288/s10/r404/orig', exist_ok=True)
shutil.copyfile(P, 'C:/kyty/s288/s10/r404/orig/sc_s9.py')
t = b.decode('ascii')
assert '\r' not in t

NEW_FN = '''

def ident_domain(ident, s, fi):
    """Item 404 (v): on an entered arm (a first scene frame, row fi) the rows T-1 and T-6 of sc_s.identities() are replaced by
    the same identities on the domain of the arm: T-1 - the lines "AsyncPipelines: skipped draw" with frame= >= the first scene
    frame n = the sum of skc_ap_skip of the FrameTrace rows with n >= it; T-6 - the distinct frame= >= it = the sum of
    skc_held_inc of the same rows.  The threshold SKIP_LINES_MAX of sc_s is unchanged (it counts the lines of the whole log: the
    emulator stops the lines per process).  The whole-log values of sc_s are printed beside as one data row ("T-1 / T-6 whole
    log (data, item 404)", ok None - not a member).  A not entered arm (fi None) keeps the whole-log rows (item 404 (v))."""
    if fi is None:
        return ident
    f0 = s['rows'][fi][0]
    xs = [s['x'].get(r[0]) for r in s['rows'] if r[0] >= f0]
    sk = sum((t[0] or 0) for t in xs if t)
    hi = sum((t[1] or 0) for t in xs if t)
    dom = [e for e in s['skips'] if e[1] is not None and e[1] >= f0]
    frames = set(e[1] for e in dom)
    nof = sum(1 for e in s['skips'] if e[1] is None)
    under = len(s['skips']) < A.SKIP_LINES_MAX
    out = []
    whole = []
    for name, ok, det in ident:
        if name.startswith('T-1 '):
            whole.append('T-1 %s' % det)
            out.append(('T-1 sum skc_ap_skip = skipped-draw lines, on the domain frame >= the first scene frame %d (item 404)' % f0,
                        (sk == len(dom)) if under else None, '%d / %d (lines without frame= %d)' % (sk, len(dom), nof)))
        elif name.startswith('T-6 '):
            whole.append('T-6 %s' % det)
            out.append(('T-6 distinct frame= of skipped draws = sum skc_held_inc (main), on the domain frame >= the first scene '
                        'frame %d (item 404)' % f0, (len(frames) == hi) if under else None, '%d / %d' % (len(frames), hi)))
        else:
            out.append((name, ok, det))
    out.append(('T-1 / T-6 whole log (data, item 404)', None, '; '.join(whole)))
    return out
'''

A1 = "    return q is not None and pre == q[1] + q[2], '%d / %s' % (pre, (q[1] + q[2]) if q else 'no queued line')\n"
assert t.count(A1) == 1
t = t.replace(A1, A1 + NEW_FN, 1)

A2 = "    ident = [x for x in A.identities(s, std, spec['cls']) if not x[0].startswith('T-4')]\n"
assert t.count(A2) == 1
t = t.replace(A2, A2 + "    ident = ident_domain(ident, s, fi)                                     # item 404 (v)\n", 1)

A3 = "PRED_PATH = 'C:/kyty/s288/pred/06b_s.md'                       # item 371 (g), item 377 (b)(4)\n"
assert t.count(A3) == 1
t = t.replace(A3, "PRED_PATH = 'C:/kyty/s288/pred/07_s.md'                        # item 371 (g), item 377 (b)(4), item 404 (g)\n", 1)

A4 = "logic are used as they are; this file only adds the arms of S10, their admission and the readings of item 355.\n"
assert t.count(A4) == 1
t = t.replace(A4, A4 + "Item 404: on an entered arm the identities T-1 and T-6 are read on the domain from the first scene frame (ident_domain);\n"
              "the whole-log values are a data row; a not entered arm keeps the whole-log identities.\n", 1)

A5 = "    add('prereg = the seal now', pred_sha is not None and pr.get('sha256') == pred_sha and\n"
assert t.count(A5) == 1
t = t.replace(A5, "    prior = spec['tag'] in PRIOR_TAGS and pr.get('sha256') == PRIOR_SHA and \\\n"
              "        (pr.get('path') or '').replace('\\\\', '/') == PRIOR_PATH                      # item 404 (g)\n"
              "    add('prereg = the seal now (or the seal 06b for the five arms made under it, item 404 (g))',\n"
              "        prior or pred_sha is not None and pr.get('sha256') == pred_sha and\n", 1)

A6 = "BIN_S = 'f3b3aa3b"
assert t.count(A6) == 1
t = t.replace(A6, "PRIOR_PATH = 'C:/kyty/s288/pred/06b_s.md'                      # item 404 (g): the seal the five made arms ran under\n"
              "PRIOR_SHA = '605ebfa5440ea1ac318749250c625b022f873d0237b37294cc97ffb069e3560b'\n"
              "PRIOR_TAGS = ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0', 'c5_0')\n" + A6, 1)
open(P, 'wb').write(t.encode('ascii'))
print('patched sha256', hashlib.sha256(t.encode('ascii')).hexdigest())
