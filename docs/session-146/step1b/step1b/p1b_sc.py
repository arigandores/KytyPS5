"""s146 link 1b (HPP-395; ROADMAP s122 item 316 (b)-(d)): the edits of sc146.py - skip_w only on positive evidence and only
on the V key attempt:<outcome>; the seal path pred/02_sc146.md; the --skip-w help text.  LF in, LF out (write_bytes)."""
import hashlib

P = 'C:/kyty/s146/sc146.py'
t = open(P, 'rb').read().decode('ascii')
assert '\r' not in t
n = 0


def rep(old, new):
    global t, n
    c = t.count(old)
    assert c == 1, (c, old[:80])
    t = t.replace(old, new)
    n += 1


rep("""  --skip-w <w>     rc 0 "SKIPPED_V_NOT_ENTERED" when the V of the pair is NOT_ENTERED (from its score.json, else its log); rc 1
                   otherwise (the W runs).
""", """  --skip-w <w>     rc 0 "SKIPPED_V_NOT_ENTERED" only on positive evidence (item 316 (b)-(d)): the V of the pair is NOT_ENTERED
                   (from its score.json, else its log) with the key attempt:<outcome>, and log_<V>.txt is present, > 0 bytes
                   and its sha256 = the "enter_scene end" line of step2/times.txt; the line names the V key; rc 1 otherwise -
                   the W runs (no log, an empty log, another sha, a death marker key K1 / K2 / VALIDATION_STOP, an entered V).
""")
rep("P146 = dict(ROOT='C:/kyty/s146', PRED_PATH='C:/kyty/s146/pred/01_sc146.md', CHAIN='go146a', RUNS='runs146',",
    "P146 = dict(ROOT='C:/kyty/s146', PRED_PATH='C:/kyty/s146/pred/02_sc146.md', CHAIN='go146a', RUNS='runs146',")
rep('''def skip_w(w, root, pred_sha, src='json'):
    """Item 309 (k)(1): (skip, line) - skip the W when the V of its pair is NOT_ENTERED (from its score.json, else its log)."""
    v = pair_v(w)
    if v is None:
        return False, 'RUN %s: no pair V (not a pair W)' % w
    e, s = entry_src(v, root, pred_sha, src)
    if e is None:
        return False, 'RUN %s: its V %s has no reading (%s)' % (w, v, s)
    if e['outcome'] == 'NOT_ENTERED':
        return True, 'SKIPPED_V_NOT_ENTERED %s: its V %s outcome NOT_ENTERED (%s; item 309 (k)(1))' % (w, v, s)
    return False, 'RUN %s: its V %s outcome %s (%s)' % (w, v, e['outcome'], s)
''', '''def skip_w(w, root, pred_sha, src='json'):
    """Item 309 (k)(1) as item 316 (b)-(d) reads it: (skip, line) - skip the W only on positive evidence that the V of its
    pair did not enter: its reading (score.json, else its log) is NOT_ENTERED with the key attempt:<outcome> (a death marker
    key - K1, K2, VALIDATION_STOP - before the entry line runs the W, item 316 (c)), and log_<V>.txt is present, > 0 bytes
    and its sha256 now = the "enter_scene end" line of step2/times.txt (item 316 (b); the json reading is taken only when
    its log sha = that line, the log reading is the file itself).  Else RUN.  Every NOT_ENTERED line names the V key (item
    316 (d))."""
    v = pair_v(w)
    if v is None:
        return False, 'RUN %s: no pair V (not a pair W)' % w
    e, s = entry_src(v, root, pred_sha, src)
    if e is None:
        return False, 'RUN %s: its V %s has no reading (%s)' % (w, v, s)
    if e['outcome'] != 'NOT_ENTERED':
        return False, 'RUN %s: its V %s outcome %s (%s)' % (w, v, e['outcome'], s)
    key = e.get('key')
    head = '%s: its V %s outcome NOT_ENTERED key %s (%s)' % (w, v, key, s)
    lp = os.path.join(root, 'log_%s.txt' % v)
    if not os.path.isfile(lp):
        return False, 'RUN %s; no log_%s.txt - no positive evidence (item 316 (b))' % (head, v)
    size = os.path.getsize(lp)
    fs = sha_file(lp)
    ts = times_log_sha(root, v)
    if size == 0:
        return False, 'RUN %s; log_%s.txt 0 bytes - no positive evidence (item 316 (b))' % (head, v)
    if fs != ts:
        return False, ('RUN %s; log_%s.txt sha256 %s != the enter_scene end line of step2/times.txt %s - no positive '
                       'evidence (item 316 (b))' % (head, v, fs[:16], (ts or 'none')[:16]))
    if not str(key).startswith('attempt:'):
        return False, 'RUN %s; a death marker before the entry line - the W runs (item 316 (c))' % head
    return True, ('SKIPPED_V_NOT_ENTERED %s; log_%s.txt %d bytes sha256 %s = the enter_scene end line of step2/times.txt, no '
                  'entry line (item 309 (k)(1), 316 (b)-(d))' % (head, v, size, fs[:16]))
''')
open(P, 'wb').write(t.encode('ascii'))
print('edits %d; sc146.py sha256 %s' % (n, hashlib.sha256(t.encode('ascii')).hexdigest()))
