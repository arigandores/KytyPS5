"""gate144.py - the read-only gate of step 2 of session 144 (HPP-332; ROADMAP s122 item 266 (b)-(e), (g), (h)).
It executes RC1-RC4 and the answer to B1 of the step-1 review (docs/session-144/review144.md) WITHOUT touching the sealed
files (pred/01_sc144.md stays); it reads the series files and the caches and writes ONE ascii row into step2/times.txt:
    <UTC> GATE <what> PASS|STOP <reasons>; <details>
Modes (one per call):
  --start            before the first lock of step 2: (d) the sha256 of C:/kyty/s143/step2/times.txt, C:/kyty/s143/pred/
                     02_sc143.md (= their seal lines of pred/01_sc144.md s.7) and of the 8 V logs v143_01..06, 09, 10 (= the
                     last "go143a v143_NN enter_scene end" line of that times.txt); (c)(1) the live caches (_ShaderCache/
                     PPSA21564, _PipelineCache, GLCache: path, size, sha256 - not mtime) against C:/kyty/s143/runs143/
                     cache_w143_10.after.json, with the header signature of pipelines.bin.
  --before <tag>     before the call of <tag> (after sc144.py --stop-check <tag>): a "GATE start PASS" row exists and
                     every made tag before <tag> has its own "GATE <tag> PASS" row (each call was gated);
                     on the made tag P right before <tag> in the sealed order: (b) W - the lines "ShaderSeed:" and
                     "PipelinePrecache:" in log_P.txt and stdout_P.txt, >= 1 of either -> STOP; V - 0 "ShaderSeed:" lines
                     in log_P.txt -> STOP; (e) V - the "admission:" line of score_P.txt failing by "V positive control"
                     or "V shipped defaults" -> STOP; (c)(2) w144_00 made -> runs144/cache_w144_00.before.json against the
                     same s143 manifest; (g) the last two made W (the control included) both with the key
                     "attempt:timeout" (json outcome timeout, no death-marker key of sc144.py, no GuestOut line in the
                     log) -> STOP.
  --recheck143       (d) again (before every sc144.py --summary read for a verdict, after sc144.py --check-seal).
rc 0 PASS, rc 5 STOP, rc 2 usage.  READ ONLY on everything but the one times row.  ASCII only.
    python gate144.py --start | --before <tag> | --recheck143  [--root R] [--root143 R] [--times F] [--ref M]
                      [--live-manifest M] [--pred P]          (the bracketed options are for the fixtures)
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
S144 = os.path.dirname(HERE)
sys.path.insert(0, S144)
import sc144      # noqa: E402  (read only: entry_of / scan; profile 144 is the module default)
import cachemf144  # noqa: E402  (read only: manifest of the live caches)

ROOT = 'C:/kyty/s144'
ROOT143 = 'C:/kyty/s143'
TIMES = ROOT + '/step2/times.txt'
REF = ROOT143 + '/runs143/cache_w143_10.after.json'
PRED = ROOT + '/pred/01_sc144.md'
V143 = ('v143_01', 'v143_02', 'v143_03', 'v143_04', 'v143_05', 'v143_06', 'v143_09', 'v143_10')
SEED = b'ShaderSeed:'
PRE = b'PipelinePrecache:'
GUEST = b'GuestOut'
CHUNK = 1 << 26
TIMEOUT_KEY = 'attempt:timeout'


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def asc(s):
    return str(s).encode('ascii', 'replace').decode('ascii')


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def count_lines(path, needles):
    """{needle: number of lines carrying it} of a file read in binary chunks split at line ends; None when absent."""
    if not os.path.isfile(path):
        return None
    n = dict((k, 0) for k in needles)
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf
                    continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if whole:
                for line in (whole.split(b'\n') if any(k in whole for k in needles) else ()):
                    for k in needles:
                        if k in line:
                            n[k] += 1
            if not b:
                break
    return n


def seal_sha(pred, name):
    """The sha256 of the seal line naming <name> (pred/01_sc144.md s.7), or None."""
    rx = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)\s*$')
    with open(pred, 'r', encoding='utf-8') as f:
        for line in f:
            m = rx.match(line.rstrip('\r\n'))
            if m and m.group(2) == name:
                return m.group(1)
    return None


def times143_log_sha(times143, tag):
    rx = re.compile(r'go143a %s enter_scene end rc \S+ log_%s\.txt sha256 ([0-9a-f]{64})' % (tag, tag))
    got = None
    with open(times143, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = rx.search(line)
            if m:
                got = m.group(1)
    return got


def check143(root143, pred):
    """Item 266 (d): (bad reasons, detail) - the s143 times and seal sha against pred/01_sc144.md, the 8 V logs against
    the last enter_scene end line of the s143 times."""
    bad, det = [], []
    tp = root143 + '/step2/times.txt'
    pp = root143 + '/pred/02_sc143.md'
    for p, name in ((tp, 'C:/kyty/s143/step2/times.txt'), (pp, 'C:/kyty/s143/pred/02_sc143.md')):
        want = seal_sha(pred, name)
        got = sha_file(p) if os.path.isfile(p) else None
        det.append('%s %s' % (p.replace(root143 + '/', 's143/'), (got or 'MISSING')[:16]))
        if got is None or got != want:
            bad.append('(d) %s sha %s != seal %s' % (p.replace(root143 + '/', 's143/'), (got or 'MISSING')[:16],
                                                      (want or 'none')[:16]))
    for t in V143:
        lp = '%s/log_%s.txt' % (root143, t)
        got = sha_file(lp) if os.path.isfile(lp) else None
        want = times143_log_sha(tp, t) if os.path.isfile(tp) else None
        det.append('%s %s' % (t, (got or 'MISSING')[:16]))
        if got is None or got != want:
            bad.append('(d) log_%s sha %s != s143 times %s' % (t, (got or 'MISSING')[:16], (want or 'none')[:16]))
    return bad, det


def mf_rows(files):
    """{(root, rel): (size, sha)} of the file rows of a manifest (mtime not read)."""
    return dict(((r[0], r[1]), (r[2], r[4])) for r in files)


def compare_manifest(files, ref_files):
    """(bad reasons, detail) of two manifests by path, size and sha256 per root."""
    a, b = mf_rows(files), mf_rows(ref_files)
    bad, det = [], []
    for root in cachemf144.ORDER:
        ka = set(k for k in a if k[0] == root)
        kb = set(k for k in b if k[0] == root)
        add, rem = ka - kb, kb - ka
        chg = [k for k in ka & kb if a[k] != b[k]]
        det.append('%s %d files (ref %d) +%d -%d changed %d' % (root, len(ka), len(kb), len(add), len(rem), len(chg)))
        if add or rem or chg:
            ex = sorted(add)[:2] + sorted(rem)[:2] + sorted(chg)[:2]
            bad.append('(c) %s differs from the s143 end: +%d -%d changed %d (%s)' % (
                root, len(add), len(rem), len(chg), ', '.join(k[1] for k in ex)))
    return bad, det


def pipelines_sig(path):
    """The signature of the header of pipelines.bin (the text after 'KytySC3:' up to ':'), or a note."""
    try:
        with open(path, 'rb') as f:
            h = f.read(256)
    except OSError:
        return 'absent'
    i = h.find(b'KytySC3:')
    if i < 0:
        return 'no KytySC3 header'
    return asc(h[i + 8:].split(b':')[0][:16].decode('ascii', 'replace'))


def made(t, root):
    return os.path.isfile('%s/%s.json' % (root, t)) or os.path.isfile('%s/attempt_%s.txt' % (root, t))


def gate_rows(times):
    """{what: last verdict} of the GATE rows of times.txt."""
    got = {}
    if not os.path.isfile(times):
        return got
    rx = re.compile(r'^\S+ GATE (\S+) (PASS|STOP)\b')
    with open(times, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = rx.match(line)
            if m:
                got[m.group(1)] = m.group(2)
    return got


def admission_bad(score):
    """(b)/(e): the form members failing in the admission line of a V score, [] when it passes them; None without a file."""
    if not os.path.isfile(score):
        return None
    with open(score, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            s = line.strip()
            if s.startswith('admission:'):
                return [k for k in ('V positive control', 'V shipped defaults') if k in s]
    return ['no admission line']


def w_key(t, root, pred_sha):
    """Item 266 (g): 'attempt:timeout' for a W whose json outcome is timeout, without the death-marker key of sc144.py and
    without a GuestOut line in its log; else the sc144 key or None."""
    jp = '%s/%s.json' % (root, t)
    if not os.path.isfile(jp):
        return None, 'no json'
    js = json.load(open(jp, encoding='utf-8'))
    oc = ((js.get('attempts') or [{}])[0] or {}).get('outcome')
    if oc != 'timeout':
        return None, 'outcome %s' % oc
    e = sc144.entry_of(t, root, pred_sha)
    if e is None:
        return None, 'no json'
    if e.get('wkey'):
        return e['wkey'], 'marker key'
    g = count_lines('%s/log_%s.txt' % (root, t), (GUEST,))
    if g is not None and g[GUEST] > 0:
        return None, 'timeout after GuestOut'
    return TIMEOUT_KEY, 'timeout before GuestOut%s' % ('' if g is not None else ' (no log)')


def before(tag, root, times, ref, pred):
    bad, det = [], []
    seq = list(sc144.SEQ)
    if tag not in seq:
        return ['tag %s not in the sealed order' % tag], det
    prior = seq[:seq.index(tag)]
    gr = gate_rows(times)
    if gr.get('start') != 'PASS':
        bad.append('no "GATE start PASS" row in times.txt (start gate %s)' % gr.get('start', 'not run'))
    for t in [t for t in prior if made(t, root)]:
        if gr.get(t) != 'PASS':
            bad.append('made tag %s has no "GATE %s PASS" row (ungated call)' % (t, t))
    p = prior[-1] if prior else None
    if p is not None and not made(p, root):
        bad.append('the tag %s before %s was not made' % (p, tag))
        p = None
    if p is not None:
        lp, sp = '%s/log_%s.txt' % (root, p), '%s/stdout_%s.txt' % (root, p)
        lc, sc = count_lines(lp, (SEED, PRE)), count_lines(sp, (SEED, PRE))
        fl = lambda c: 'MISSING' if c is None else '%d/%d' % (c[SEED], c[PRE])
        det.append('%s ShaderSeed/PipelinePrecache log %s stdout %s' % (p, fl(lc), fl(sc)))
        if p in sc144.W_TAGS:
            if lc is None or sc is None:
                bad.append('(b) W %s: log or stdout missing - member not evaluable' % p)
            elif lc[SEED] + lc[PRE] + sc[SEED] + sc[PRE] > 0:
                bad.append('(b) W %s: precache member of the emulator present (ShaderSeed/PipelinePrecache log %s stdout %s)'
                           % (p, fl(lc), fl(sc)))
        else:
            if lc is None:
                bad.append('(b) V %s: log missing' % p)
            elif lc[SEED] == 0:
                bad.append('(b) V %s: 0 ShaderSeed: lines in the log' % p)
            ab = admission_bad('%s/score_%s.txt' % (root, p))
            det.append('%s admission form members %s' % (p, 'score MISSING' if ab is None else (','.join(ab) or 'pass')))
            if ab is None:
                bad.append('(e) V %s: score_%s.txt missing' % (p, p))
            elif ab:
                bad.append('(e) V %s rejected by a form member: %s' % (p, ', '.join(ab)))
    c0 = sc144.CONTROL[0]
    if tag != c0 and made(c0, root):
        mp = '%s/runs144/cache_%s.before.json' % (root, c0)
        if not os.path.isfile(mp):
            bad.append('(c)(2) %s missing' % mp.replace(root + '/', ''))
        else:
            b2, d2 = compare_manifest(json.load(open(mp, encoding='utf-8'))['files'],
                                      json.load(open(ref, encoding='utf-8'))['files'])
            bad += [x.replace('(c)', '(c)(2)') for x in b2]
            det.append('cache_%s.before %s vs ref %s: %s' % (c0, sha_file(mp)[:16], sha_file(ref)[:16], '; '.join(d2)))
    ws = [t for t in prior if t in sc144.W_TAGS and made(t, root)][-2:]
    psha = sha_file(pred) if os.path.isfile(pred) else None
    keys = [(t,) + w_key(t, root, psha) for t in ws]
    det.append('W keys %s' % (', '.join('%s %s (%s)' % k for k in keys) or 'none'))
    if len(keys) == 2 and keys[0][1] == TIMEOUT_KEY and keys[1][1] == TIMEOUT_KEY:
        bad.append('(g) two W in a row with the key %s: %s,%s' % (TIMEOUT_KEY, keys[0][0], keys[1][0]))
    return bad, det


def start(root143, pred, ref, live):
    bad, det = check143(root143, pred)
    if live:
        files = json.load(open(live, encoding='utf-8'))['files']
        src = 'manifest %s' % os.path.basename(live)
    else:
        files = cachemf144.manifest(cachemf144.default_roots())[1]
        src = 'live caches'
    b2, d2 = compare_manifest(files, json.load(open(ref, encoding='utf-8'))['files'])
    bad += b2
    pb = [r for r in files if r[0] == 'shader' and r[1] == 'pipelines.bin']
    det.append('(c)(1) %s vs %s %s: %s; pipelines.bin %s sig %s' % (
        src, os.path.basename(ref), sha_file(ref)[:16], '; '.join(d2),
        (pb[0][4][:16] if pb else 'absent'),
        pipelines_sig(cachemf144.default_roots()['shader'] + '/pipelines.bin') if not live else 'n/a'))
    return bad, det


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--start', action='store_true')
    g.add_argument('--before')
    g.add_argument('--recheck143', action='store_true')
    ap.add_argument('--root', default=ROOT)
    ap.add_argument('--root143', default=ROOT143)
    ap.add_argument('--times', default=TIMES)
    ap.add_argument('--ref', default=REF)
    ap.add_argument('--live-manifest', default=None)
    ap.add_argument('--pred', default=PRED)
    a = ap.parse_args(argv)
    if a.start:
        what = 'start'
        bad, det = start(a.root143, a.pred, a.ref, a.live_manifest)
    elif a.recheck143:
        what = 'recheck143'
        bad, det = check143(a.root143, a.pred)
    else:
        what = a.before
        bad, det = before(a.before, a.root, a.times, a.ref, a.pred)
    line = '%s GATE %s %s%s; %s' % (utc(), what, 'STOP ' if bad else 'PASS', '; '.join(bad), ' | '.join(det))
    line = asc(line)
    with open(a.times, 'a', encoding='ascii') as f:
        f.write(line + '\n')
    print(line)
    return 5 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
