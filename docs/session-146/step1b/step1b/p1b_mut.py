"""s146 link 1b (HPP-395; ROADMAP s122 item 316 (d)): the edits of mut_sc146.py - g_pred re-anchored on the seal pred/02_sc146.md,
k_ne dropped with its line, 17 new mutants on the new lines of skip_w (item 316 (b)-(c)); every anchor checked to occur
exactly once in the edited sc146.py.  Prints the --only list.  LF in, LF out (write_bytes)."""
import hashlib

SC = open('C:/kyty/s146/sc146.py', 'rb').read().decode('ascii')
P = 'C:/kyty/s146/mut_sc146.py'
t = open(P, 'rb').read().decode('ascii')
assert '\r' not in t


def rep(old, new):
    global t
    c = t.count(old)
    assert c == 1, (c, old[:80])
    t = t.replace(old, new)


rep('''    ('g_pred', "PRED_PATH='C:/kyty/s146/pred/01_sc146.md'", "PRED_PATH='C:/kyty/s146/pred/02_sc146.md'"),\n''',
    '''    ('g_pred', "PRED_PATH='C:/kyty/s146/pred/02_sc146.md'", "PRED_PATH='C:/kyty/s146/pred/01_sc146.md'"),\n''')
KNE = '''    ('k_ne', "    if e['outcome'] == 'NOT_ENTERED':\\n        return True, 'SKIPPED_V_NOT_ENTERED", "    if e['outcome'] != 'NOT_ENTERED':\\n        return True, 'SKIPPED_V_NOT_ENTERED"),\n'''
NEW = [
    ('k_ne2', "    if e['outcome'] != 'NOT_ENTERED':\n        return False, 'RUN %s: its V %s outcome %s (%s)'",
     "    if e['outcome'] == 'NOT_ENTERED':\n        return False, 'RUN %s: its V %s outcome %s (%s)'"),
    ('k_ne_off', "    if e['outcome'] != 'NOT_ENTERED':\n        return False, 'RUN %s: its V %s outcome %s (%s)'",
     "    if False:\n        return False, 'RUN %s: its V %s outcome %s (%s)'"),
    ('k_key_src', "    key = e.get('key')\n", "    key = 'attempt:%s' % e.get('attempt_outcome')\n"),
    ('k_head', "    head = '%s: its V %s outcome NOT_ENTERED key %s (%s)' % (w, v, key, s)\n",
     "    head = '%s: its V %s outcome NOT_ENTERED (%s)' % (w, v, s)\n"),
    ('k_lp', "    lp = os.path.join(root, 'log_%s.txt' % v)\n", "    lp = os.path.join(root, 'log_%s.txt' % w)\n"),
    ('k_nolog', "    if not os.path.isfile(lp):\n        return False, 'RUN %s; no log_%s.txt",
     "    if False:\n        return False, 'RUN %s; no log_%s.txt"),
    ('k_nolog_rc', "        return False, 'RUN %s; no log_%s.txt", "        return True, 'RUN %s; no log_%s.txt"),
    ('k_size_src', "    size = os.path.getsize(lp)\n", "    size = 1\n"),
    ('k_fs_src', "    fs = sha_file(lp)\n", "    fs = e.get('log_sha')\n"),
    ('k_ts', "    ts = times_log_sha(root, v)\n", "    ts = fs\n"),
    ('k_size', "    if size == 0:\n        return False, 'RUN %s; log_%s.txt 0 bytes",
     "    if False:\n        return False, 'RUN %s; log_%s.txt 0 bytes"),
    ('k_size_rc', "        return False, 'RUN %s; log_%s.txt 0 bytes", "        return True, 'RUN %s; log_%s.txt 0 bytes"),
    ('k_sha', "    if fs != ts:\n", "    if False:\n"),
    ('k_sha_rc', "        return False, ('RUN %s; log_%s.txt sha256 %s != the", "        return True, ('RUN %s; log_%s.txt sha256 %s != the"),
    ('k_key', "    if not str(key).startswith('attempt:'):\n", "    if False:\n"),
    ('k_key_rc', "        return False, 'RUN %s; a death marker before", "        return True, 'RUN %s; a death marker before"),
    ('k_skip_rc', "    return True, ('SKIPPED_V_NOT_ENTERED %s; log_", "    return False, ('SKIPPED_V_NOT_ENTERED %s; log_"),
]
for name, old, new in NEW:
    assert SC.count(old) == 1, (name, SC.count(old))
    assert old != new
assert SC.count("PRED_PATH='C:/kyty/s146/pred/02_sc146.md'") == 1
rep(KNE, ''.join('    (%r, %r, %r),\n' % x for x in NEW))
rep('''Not mutated (proofs): (1) the dual position''',
    '''Link 1b (HPP-395, item 316 (b)-(d)): g_pred re-anchored on the seal pred/02_sc146.md (the same mutation, 02 -> 01); k_ne
dropped with its line; 17 new k_* mutants on the new lines of skip_w (the outcome test, the key, the head of the line, the log
path, its presence, size, sha now, the times.txt sha, the marker key, the rc of every branch); run --only over g_pred and
every k_* (item 316 (d)).  Not mutated on the new lines (proofs): "str(key)" -> "key" (key is a str whenever the outcome is
NOT_ENTERED - the key of outcome(): a marker kind or "attempt:<outcome>"); the texts after the head (each branch line is
read whole by F13-F13k, a change of text is killed by them but adds no member).
Not mutated (proofs): (1) the dual position''')
open(P, 'wb').write(t.encode('ascii'))
ns = [x[0] for x in NEW]
print('mutants new %d; mut_sc146.py sha256 %s' % (len(NEW), hashlib.sha256(t.encode('ascii')).hexdigest()))
print('ONLY ' + ','.join(['g_pred', 'k_file', 'k_pairv', 'k_none', 'k_main_rc'] + ns))
