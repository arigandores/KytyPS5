"""gate145.py - the read-only gate of step 2 of session 145 (step 0 HPP-350; ROADMAP s122 item 273 (k)(3)-(4); port of
C:/kyty/s144/step2/gate144.py of item 266 (b)-(e), (g), (h)).  It reads the series files and the caches and writes ONE ascii
row into step2/times.txt:
    <UTC> GATE <what> PASS|STOP <reasons>; <details>
Modes (one per call):
  --start            before the first lock of step 2: (d) the sha256 of C:/kyty/s144/step2/times.txt and C:/kyty/s144/pred/
                     01_sc144.md (= their seal lines of pred/01_sc145.md) and of the V log v144_09 (= the last "go144a v144_09
                     enter_scene end" line of that times.txt); (c)(1) the live caches (_ShaderCache/PPSA21564, _PipelineCache,
                     GLCache: path, size, sha256 - not mtime) against C:/kyty/s144/runs144/cache_w144_20.after.json (the end
                     of the s144 series), with the header signature of pipelines.bin.
  --before <tag>     before the call of <tag> (after sc145.py --stop-check <tag>): a "GATE start PASS" row exists and every
                     made tag before <tag> has its own "GATE <tag> PASS" row (each call was gated);
                     on the made tag P right before <tag> in the sealed order: (w) a window event - a line "Window <id>
                     minimized" or "Recovering Vulkan swapchain" in log_P.txt or stdout_P.txt -> STOP (item 273 (k)(3): not an
                     outcome of the level, question to the lead about a repeat); (b) W - the lines "ShaderSeed:" and
                     "PipelinePrecache:" in log_P.txt and stdout_P.txt, >= 1 of either -> STOP; V - 0 "ShaderSeed:" lines in
                     log_P.txt -> STOP; (f) W - VK_LAYER_MESSAGE_ID_FILTER of its json env != sc145.VKFILTER -> STOP (item 273
                     (k)(2)); (e) V - the "admission:" line of score_P.txt failing by "V positive control" or "V shipped
                     defaults" -> STOP; (l) the control w145_00 made - its layer limit lines ("this will be the last time
                     reporting it", log and stdout) >= 1 -> STOP (item 273 (k)(2)); (c)(2) w145_00 made ->
                     runs145/cache_w145_00.before.json against the same s144 manifest; (g) the last two made W (the control
                     included) both with the key "attempt:timeout" (json outcome timeout, no death-marker key of sc145.py,
                     no GuestOut line in the log) -> STOP.
  --recheck144       (d) again (before every sc145.py --summary read for a verdict, after sc145.py --check-seal).
rc 0 PASS, rc 5 STOP, rc 2 usage.  READ ONLY on everything but the one times row.  ASCII only.
    python gate145.py --start | --before <tag> | --recheck144  [--root R] [--root144 R] [--times F] [--ref M]
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
S145 = os.path.dirname(HERE)
sys.path.insert(0, S145)
import sc145      # noqa: E402  (read only: entry_of / scan; profile 145 is the module default)
import cachemf145  # noqa: E402  (read only: manifest of the live caches)

ROOT = 'C:/kyty/s145'
ROOT144 = 'C:/kyty/s144'
TIMES = ROOT + '/step2/times.txt'
REF = ROOT144 + '/runs144/cache_w144_20.after.json'
PRED = ROOT + '/pred/01_sc145.md'
V144 = ('v144_09',)
SEED = b'ShaderSeed:'
PRE = b'PipelinePrecache:'
GUEST = b'GuestOut'
LIMIT = b'this will be the last time reporting it'
REC = b'Recovering Vulkan swapchain'
RX_MIN = re.compile(rb'Window \d+ minimized\b')
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


def count_lines(path, needles, rx=None):
    """{needle: number of lines carrying it} of a file read in binary chunks split at line ends (and 'rx': the number of
    lines matching the regex rx); None when absent."""
    if not os.path.isfile(path):
        return None
    n = dict((k, 0) for k in needles)
    n['rx'] = 0
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
                if rx is not None:
                    n['rx'] += len(rx.findall(whole))
            if not b:
                break
    return n


def seal_sha(pred, name):
    """The sha256 of the seal line naming <name> (pred/01_sc145.md), or None."""
    rx = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)\s*$')
    with open(pred, 'r', encoding='utf-8') as f:
        for line in f:
            m = rx.match(line.rstrip('\r\n'))
            if m and m.group(2) == name:
                return m.group(1)
    return None


def times144_log_sha(times144, tag):
    rx = re.compile(r'go144a %s enter_scene end rc \S+ log_%s\.txt sha256 ([0-9a-f]{64})' % (tag, tag))
    got = None
    with open(times144, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = rx.search(line)
            if m:
                got = m.group(1)
    return got


def check144(root144, pred):
    """(d): (bad reasons, detail) - the s144 times and seal sha against pred/01_sc145.md, the V log v144_09 against the last
    enter_scene end line of the s144 times."""
    bad, det = [], []
    tp = root144 + '/step2/times.txt'
    pp = root144 + '/pred/01_sc144.md'
    for p, name in ((tp, 'C:/kyty/s144/step2/times.txt'), (pp, 'C:/kyty/s144/pred/01_sc144.md')):
        want = seal_sha(pred, name)
        got = sha_file(p) if os.path.isfile(p) else None
        det.append('%s %s' % (p.replace(root144 + '/', 's144/'), (got or 'MISSING')[:16]))
        if got is None or got != want:
            bad.append('(d) %s sha %s != seal %s' % (p.replace(root144 + '/', 's144/'), (got or 'MISSING')[:16],
                                                      (want or 'none')[:16]))
    for t in V144:
        lp = '%s/log_%s.txt' % (root144, t)
        got = sha_file(lp) if os.path.isfile(lp) else None
        want = times144_log_sha(tp, t) if os.path.isfile(tp) else None
        det.append('%s %s' % (t, (got or 'MISSING')[:16]))
        if got is None or got != want:
            bad.append('(d) log_%s sha %s != s144 times %s' % (t, (got or 'MISSING')[:16], (want or 'none')[:16]))
    return bad, det


def mf_rows(files):
    """{(root, rel): (size, sha)} of the file rows of a manifest (mtime not read)."""
    return dict(((r[0], r[1]), (r[2], r[4])) for r in files)


def compare_manifest(files, ref_files):
    """(bad reasons, detail) of two manifests by path, size and sha256 per root."""
    a, b = mf_rows(files), mf_rows(ref_files)
    bad, det = [], []
    for root in cachemf145.ORDER:
        ka = set(k for k in a if k[0] == root)
        kb = set(k for k in b if k[0] == root)
        add, rem = ka - kb, kb - ka
        chg = [k for k in ka & kb if a[k] != b[k]]
        det.append('%s %d files (ref %d) +%d -%d changed %d' % (root, len(ka), len(kb), len(add), len(rem), len(chg)))
        if add or rem or chg:
            ex = sorted(add)[:2] + sorted(rem)[:2] + sorted(chg)[:2]
            bad.append('(c) %s differs from the s144 end: +%d -%d changed %d (%s)' % (
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
    """Item 266 (g): 'attempt:timeout' for a W whose json outcome is timeout, without the death-marker key of sc145.py and
    without a GuestOut line in its log; else the sc145 key or None."""
    jp = '%s/%s.json' % (root, t)
    if not os.path.isfile(jp):
        return None, 'no json'
    js = json.load(open(jp, encoding='utf-8'))
    oc = ((js.get('attempts') or [{}])[0] or {}).get('outcome')
    if oc != 'timeout':
        return None, 'outcome %s' % oc
    e = sc145.entry_of(t, root, pred_sha)
    if e is None:
        return None, 'no json'
    if e.get('wkey'):
        return e['wkey'], 'marker key'
    g = count_lines('%s/log_%s.txt' % (root, t), (GUEST,))
    if g is not None and g[GUEST] > 0:
        return None, 'timeout after GuestOut'
    return TIMEOUT_KEY, 'timeout before GuestOut%s' % ('' if g is not None else ' (no log)')


def window_lines(root, t):
    """(w): (minimized lines, Recovering lines) of log_<t>.txt and stdout_<t>.txt together; None when both are absent."""
    got = [count_lines('%s/%s_%s.txt' % (root, a, t), (REC,), RX_MIN) for a in ('log', 'stdout')]
    if got[0] is None and got[1] is None:
        return None
    return (sum(g['rx'] for g in got if g is not None), sum(g[REC] for g in got if g is not None))


def before(tag, root, times, ref, pred):
    bad, det = [], []
    seq = list(sc145.SEQ)
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
        wn = window_lines(root, p)
        det.append('%s window minimized/Recovering %s' % (p, 'MISSING' if wn is None else '%d/%d' % wn))
        if wn is None:
            bad.append('(w) %s: log and stdout missing - the window event not evaluable' % p)
        elif wn[0] + wn[1] > 0:
            bad.append('(w) window event on %s: minimized %d, Recovering Vulkan swapchain %d (item 273 (k)(3): not an outcome '
                       'of the level; question to the lead about a repeat)' % (p, wn[0], wn[1]))
        lp, sp = '%s/log_%s.txt' % (root, p), '%s/stdout_%s.txt' % (root, p)
        lc, sc = count_lines(lp, (SEED, PRE)), count_lines(sp, (SEED, PRE))
        fl = lambda c: 'MISSING' if c is None else '%d/%d' % (c[SEED], c[PRE])
        det.append('%s ShaderSeed/PipelinePrecache log %s stdout %s' % (p, fl(lc), fl(sc)))
        if p in sc145.W_TAGS:
            if lc is None or sc is None:
                bad.append('(b) W %s: log or stdout missing - member not evaluable' % p)
            elif lc[SEED] + lc[PRE] + sc[SEED] + sc[PRE] > 0:
                bad.append('(b) W %s: precache member of the emulator present (ShaderSeed/PipelinePrecache log %s stdout %s)'
                           % (p, fl(lc), fl(sc)))
            jp = '%s/%s.json' % (root, p)
            fv = ((json.load(open(jp, encoding='utf-8')).get('env') or {}).get('VK_LAYER_MESSAGE_ID_FILTER')
                  if os.path.isfile(jp) else 'NO JSON')
            det.append('%s filter %s' % (p, fv))
            if fv != sc145.VKFILTER:
                bad.append('(f) W %s: VK_LAYER_MESSAGE_ID_FILTER %s != %s (item 273 (k)(2))' % (p, fv, sc145.VKFILTER))
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
    c0 = sc145.CONTROL[0]
    if tag != c0 and made(c0, root):
        lim = [count_lines('%s/%s_%s.txt' % (root, a, c0), (LIMIT,)) for a in ('log', 'stdout')]
        nl = sum(x[LIMIT] for x in lim if x is not None)
        det.append('%s layer limit lines %d' % (c0, nl))
        if nl:
            bad.append('(l) the control W %s has %d layer limit line(s) (item 273 (k)(2): 0 required)' % (c0, nl))
        mp = '%s/runs145/cache_%s.before.json' % (root, c0)
        if not os.path.isfile(mp):
            bad.append('(c)(2) %s missing' % mp.replace(root + '/', ''))
        else:
            b2, d2 = compare_manifest(json.load(open(mp, encoding='utf-8'))['files'],
                                      json.load(open(ref, encoding='utf-8'))['files'])
            bad += [x.replace('(c)', '(c)(2)') for x in b2]
            det.append('cache_%s.before %s vs ref %s: %s' % (c0, sha_file(mp)[:16], sha_file(ref)[:16], '; '.join(d2)))
    ws = [t for t in prior if t in sc145.W_TAGS and made(t, root)][-2:]
    psha = sha_file(pred) if os.path.isfile(pred) else None
    keys = [(t,) + w_key(t, root, psha) for t in ws]
    det.append('W keys %s' % (', '.join('%s %s (%s)' % k for k in keys) or 'none'))
    if len(keys) == 2 and keys[0][1] == TIMEOUT_KEY and keys[1][1] == TIMEOUT_KEY:
        bad.append('(g) two W in a row with the key %s: %s,%s' % (TIMEOUT_KEY, keys[0][0], keys[1][0]))
    return bad, det


def start(root144, pred, ref, live):
    bad, det = check144(root144, pred)
    if live:
        files = json.load(open(live, encoding='utf-8'))['files']
        src = 'manifest %s' % os.path.basename(live)
    else:
        files = cachemf145.manifest(cachemf145.default_roots())[1]
        src = 'live caches'
    b2, d2 = compare_manifest(files, json.load(open(ref, encoding='utf-8'))['files'])
    bad += b2
    pb = [r for r in files if r[0] == 'shader' and r[1] == 'pipelines.bin']
    det.append('(c)(1) %s vs %s %s: %s; pipelines.bin %s sig %s' % (
        src, os.path.basename(ref), sha_file(ref)[:16], '; '.join(d2),
        (pb[0][4][:16] if pb else 'absent'),
        pipelines_sig(cachemf145.default_roots()['shader'] + '/pipelines.bin') if not live else 'n/a'))
    return bad, det


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--start', action='store_true')
    g.add_argument('--before')
    g.add_argument('--recheck144', action='store_true')
    ap.add_argument('--root', default=ROOT)
    ap.add_argument('--root144', default=ROOT144)
    ap.add_argument('--times', default=TIMES)
    ap.add_argument('--ref', default=REF)
    ap.add_argument('--live-manifest', default=None)
    ap.add_argument('--pred', default=PRED)
    a = ap.parse_args(argv)
    if a.start:
        what = 'start'
        bad, det = start(a.root144, a.pred, a.ref, a.live_manifest)
    elif a.recheck144:
        what = 'recheck144'
        bad, det = check144(a.root144, a.pred)
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
