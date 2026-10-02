"""gate146.py - the read-only gate of step 2 of session 146 (step 0 HPP-386; ROADMAP s122 item 273 (k)(3)-(4), 295 (v)-(e),
309 (k), (l)(5), 300 (b)(2)-(4); port of C:/kyty/s145/step2/gate145.py).  It reads the series files and the caches and writes
ONE ascii row into step2/times.txt:
    <UTC> GATE <what> PASS|STOP <reasons>; <details>
Modes (one per call):
  --start            before the first lock of step 2: (r) the sha256 of the reference runs146/cache_i146_v.after.json (the
                     cache manifest at the end of the warm-up i146_v of step 0, written by go146i.sh) = its seal line of
                     pred/02_sc146.md, else STOP; (s) the free space of the disk C: below 60 GiB -> STOP; (c)(1) the live caches
                     (path, size, sha256 - not mtime) against the reference: the translation cache _ShaderCache/PPSA21564 (its
                     root files and the variant directory variant_fixb26_fixb1b with its pipelines.bin) differs -> STOP (item
                     288 (v)(1)); _PipelineCache and GLCache differ -> the data segment "(c)(1) info driver caches: ..." (item 288
                     (v)(2)); then it WRITES the start manifest runs146/cache_start.json and names its sha256 in its row.
  --before <tag>     before the call of <tag> (after sc146.py --stop-check <tag>): a "GATE start PASS" row exists and every
                     made tag before <tag> has its own "GATE <tag> PASS" row; on the made tag P right before <tag> in the
                     sealed order (a W skipped by item 309 (k)(1) - skipped_<w>.txt - is passed over to the made tag before
                     it): (w) a window event -> STOP; (b) W - its json env carries KYTY_PIPELINE_PRECACHE (the W form of item
                     300 (b)(4): precache by default) -> STOP, the ShaderSeed: / PipelinePrecache: lines of log and stdout are
                     printed as data; V - 0 "ShaderSeed:" lines in log_P.txt -> STOP; (f) W - the form line of item 295 (b)(4)
                     failing -> STOP; (v) W - a failing row "W 295(b)(N)" in the admission line of score_P.txt (or the file /
                     the line missing) -> STOP; (e) V - the admission line of score_P.txt failing by "V positive control" or
                     "V shipped defaults" -> STOP; (l) the control w146_00 made - its layer limit lines >= 1 -> STOP; (c)(2)
                     w146_00 made -> runs146/cache_w146_00.before.json against the start manifest; (g) the last two made W
                     both with the key "attempt:timeout" -> STOP.
rc 0 PASS, rc 5 STOP, rc 2 usage.  READ ONLY on everything but the one times row and (--start only) the start manifest.  ASCII.
    python gate146.py --start | --before <tag>  [--root R] [--times F] [--ref M] [--live-manifest M] [--pred P]
Session 145 header (carried):
gate145.py - the read-only gate of step 2 of session 145 (step 0 HPP-350; ROADMAP s122 item 273 (k)(3)-(4); link 1b
HPP-379, item 295 (v), (e); port of C:/kyty/s144/step2/gate144.py of item 266 (b)-(e), (g), (h)).  It reads the series files
and the caches and writes ONE ascii row into step2/times.txt:
    <UTC> GATE <what> PASS|STOP <reasons>; <details>
Modes (one per call):
  --start            before the first lock of step 2: (d) the sha256 of C:/kyty/s144/step2/times.txt and C:/kyty/s144/pred/
                     01_sc144.md (= their seal lines of pred/03_sc145.md) and of the V log v144_09 (= the last "go144a v144_09
                     enter_scene end" line of that times.txt); (r) item 295 (e): the sha256 of the reference
                     C:/kyty/s144/runs144/cache_w144_20.after.json = its seal line, else STOP; (s) item 295 (v): the free
                     space of the disk C: below 60 GiB (MIN_FREE; the units of df -h the lead read 349 G in; the row prints
                     the bytes, GiB and GB) -> STOP; (c)(1) the live caches (path, size, sha256 - not mtime)
                     against C:/kyty/s144/runs144/cache_w144_20.after.json (the end of the s144 series), split by ROADMAP s122
                     item 288 (v): the translation cache _ShaderCache/PPSA21564 with pipelines.bin differs -> STOP (c)(1)
                     (item 288 (v)(1)); _PipelineCache and GLCache differ -> the data segment "(c)(1) info driver caches: ..."
                     with the names and sha256 (16 hex) of the added, removed and changed files, not STOP (item 288 (v)(2));
                     with the header signature of pipelines.bin; then it WRITES the start manifest runs145/cache_start.json
                     (the live manifest it read; the reference of continuity within the series, item 288 (v)(3)) and names
                     its sha256 in its row ("start manifest runs145/cache_start.json sha256 <64 hex>").
  --before <tag>     before the call of <tag> (after sc145.py --stop-check <tag>): a "GATE start PASS" row exists and every
                     made tag before <tag> has its own "GATE <tag> PASS" row (each call was gated);
                     on the made tag P right before <tag> in the sealed order: (w) a window event - a line "Window <id>
                     minimized" or "Recovering Vulkan swapchain" in log_P.txt or stdout_P.txt -> STOP (item 273 (k)(3): not an
                     outcome of the level, question to the lead about a repeat); (b) W - the lines "ShaderSeed:" and
                     "PipelinePrecache:" in log_P.txt and stdout_P.txt, >= 1 of either -> STOP; V - 0 "ShaderSeed:" lines in
                     log_P.txt -> STOP; (f) W - the form line of item 295 (b)(4) built from its json env (sc145.w_form4:
                     "W form: limit=100000000 filter=none", no VK_LAYER_MESSAGE_ID_FILTER key) failing -> STOP; (v) W (the
                     control or another) - item 295 (v): any row "W 295(b)(N)" failing in the "admission:" line of
                     score_P.txt (the sealed scorer's rows of item 295 (b)(1)-(4)), the score file or its admission line
                     missing -> STOP (an instrument stop, question to the lead); (e) V - the "admission:" line of score_P.txt
                     failing by "V positive control" or "V shipped
                     defaults" -> STOP; (l) the control w145_00 made - its layer limit lines ("this will be the last time
                     reporting it", log and stdout) >= 1 -> STOP (item 273 (k)(2)); (c)(2) w145_00 made ->
                     runs145/cache_w145_00.before.json against the start manifest runs145/cache_start.json, every root
                     (item 288 (v)(3)-(4)); the start manifest missing, or its sha256 != the one named by the last "GATE
                     start PASS" row -> STOP; (g) the last two made W (the control
                     included) both with the key "attempt:timeout" (json outcome timeout, no death-marker key of sc145.py,
                     no GuestOut line in the log) -> STOP.
  --recheck144       (d) again (before every sc145.py --summary read for a verdict, after sc145.py --check-seal).
rc 0 PASS, rc 5 STOP, rc 2 usage.  READ ONLY on everything but the one times row and (--start only) the start manifest
runs145/cache_start.json.  ASCII only.
    python gate145.py --start | --before <tag> | --recheck144  [--root R] [--root144 R] [--times F] [--ref M]
                      [--live-manifest M] [--pred P]          (the bracketed options are for the fixtures)
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time

sys.dont_write_bytecode = True
S146 = 'C:/kyty/s146'                 # absolute: a copy of this file elsewhere (a mutant) reads the same sc146 / cachemf146
sys.path.insert(0, S146)
import sc146      # noqa: E402  (read only: entry_of / scan / w_form4; profile 146 is the module default)
import cachemf146  # noqa: E402  (read only: manifest of the live caches)

ROOT = 'C:/kyty/s146'
TIMES = ROOT + '/step2/times.txt'
REF = ROOT + '/runs146/cache_i146_v.after.json'
PRED = ROOT + '/pred/02_sc146.md'
REF_SEAL = 'runs146/cache_i146_v.after.json'                 # the name of its seal line (relative to the root)
MIN_FREE = 60 * 2 ** 30                                      # item 295 (v): 60 GiB free on C:
DISK = 'C:/'
SEED = b'ShaderSeed:'
PRE = b'PipelinePrecache:'
GUEST = b'GuestOut'
LIMIT = b'this will be the last time reporting it'
REC = b'Recovering Vulkan swapchain'
RX_MIN = re.compile(rb'Window \d+ minimized\b')
CHUNK = 1 << 26
TIMEOUT_KEY = 'attempt:timeout'
STRICT = ('shader',)               # item 288 (v)(1): the translation cache of the root with pipelines.bin -> STOP
DRIVER = ('pipeline', 'glcache')   # item 288 (v)(2): the driver caches -> a data segment, not STOP
START_MF = 'runs146/cache_start.json'
RX_START = re.compile(r'^\S+ GATE start PASS\b.*start manifest runs146/cache_start\.json sha256 ([0-9a-f]{64})')


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
    """The sha256 of the seal line naming <name> (pred/02_sc146.md), or None."""
    rx = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)\s*$')
    with open(pred, 'r', encoding='utf-8') as f:
        for line in f:
            m = rx.match(line.rstrip('\r\n'))
            if m and m.group(2) == name:
                return m.group(1)
    return None


def mf_rows(files):
    """{(root, rel): (size, sha)} of the file rows of a manifest (mtime not read)."""
    return dict(((r[0], r[1]), (r[2], r[4])) for r in files)


def compare_manifest(files, ref_files, roots=cachemf146.ORDER, what='(c) %s differs from the end of the warm-up i146_v'):
    """(bad reasons, detail) of two manifests by path, size and sha256 per root of <roots>."""
    a, b = mf_rows(files), mf_rows(ref_files)
    bad, det = [], []
    for root in roots:
        ka = set(k for k in a if k[0] == root)
        kb = set(k for k in b if k[0] == root)
        add, rem = ka - kb, kb - ka
        chg = [k for k in ka & kb if a[k] != b[k]]
        det.append('%s %d files (ref %d) +%d -%d changed %d' % (root, len(ka), len(kb), len(add), len(rem), len(chg)))
        if add or rem or chg:
            ex = sorted(add)[:2] + sorted(rem)[:2] + sorted(chg)[:2]
            bad.append((what % root) + ': +%d -%d changed %d (%s)' % (
                len(add), len(rem), len(chg), ', '.join(k[1] for k in ex)))
    return bad, det


def driver_info(files, ref_files):
    """Item 288 (v)(2): the data segment of the driver caches against the reference - per root the counts and every added
    (+name new sha), removed (-name old sha) and changed (~name old sha->new sha) file, sha256 to 16 hex."""
    a, b = mf_rows(files), mf_rows(ref_files)
    parts = []
    for root in DRIVER:
        ka = set(k for k in a if k[0] == root)
        kb = set(k for k in b if k[0] == root)
        add, rem = sorted(ka - kb), sorted(kb - ka)
        chg = sorted(k for k in ka & kb if a[k] != b[k])
        items = (['+%s %s' % (k[1], str(a[k][1])[:16]) for k in add] + ['-%s %s' % (k[1], str(b[k][1])[:16]) for k in rem] +
                 ['~%s %s->%s' % (k[1], str(b[k][1])[:16], str(a[k][1])[:16]) for k in chg])
        parts.append('%s +%d -%d changed %d%s' % (root, len(add), len(rem), len(chg),
                                                  (' (%s)' % ', '.join(items)) if items else ''))
    return '(c)(1) info driver caches: %s (item 288 (v)(2): data, not STOP)' % '; '.join(parts)


def start_sha(times):
    """The sha256 of the start manifest named by the last "GATE start PASS" row of times.txt, or None."""
    got = None
    if os.path.isfile(times):
        with open(times, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                m = RX_START.match(line)
                if m:
                    got = m.group(1)
    return got


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


def disk_free(path):
    """Item 295 (v): the free bytes of the disk of path (the fixtures replace this function)."""
    return shutil.disk_usage(path).free


def w_admission_bad(score):
    """Item 295 (v): the members '(b)(N)' of the failing rows "W 295(b)(N) ..." in the admission line of a W score, [] when
    none fails; None without the file; ['no admission line'] without the line."""
    if not os.path.isfile(score):
        return None
    with open(score, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            s = line.strip()
            if s.startswith('admission:'):
                return re.findall(r'W 295(\(b\)\(\d\))', s)
    return ['no admission line']


def made(t, root):
    return os.path.isfile('%s/%s.json' % (root, t)) or os.path.isfile('%s/attempt_%s.txt' % (root, t))


def skipped(t, root):
    """Item 309 (k)(1): the W was not called (its V NOT_ENTERED) - the chain's marker skipped_<w>.txt."""
    return os.path.isfile('%s/skipped_%s.txt' % (root, t))


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
    """Item 266 (g): 'attempt:timeout' for a W whose json outcome is timeout, without the death-marker key of sc146.py and
    without a GuestOut line in its log; else the sc146 key or None."""
    jp = '%s/%s.json' % (root, t)
    if not os.path.isfile(jp):
        return None, 'no json'
    js = json.load(open(jp, encoding='utf-8'))
    oc = ((js.get('attempts') or [{}])[0] or {}).get('outcome')
    if oc != 'timeout':
        return None, 'outcome %s' % oc
    e = sc146.entry_of(t, root, pred_sha)
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
    seq = list(sc146.SEQ)
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
    while p is not None and not made(p, root) and skipped(p, root):
        det.append('%s SKIPPED_V_NOT_ENTERED (item 309 (k)(1)) - passed over' % p)
        k = prior.index(p)
        p = prior[k - 1] if k > 0 else None
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
        if p in sc146.W_TAGS:
            jp = '%s/%s.json' % (root, p)
            env = (json.load(open(jp, encoding='utf-8')).get('env') or {}) if os.path.isfile(jp) else None
            if env is None:
                bad.append('(b) W %s: no json - the W form not evaluable' % p)
            elif 'KYTY_PIPELINE_PRECACHE' in env:
                bad.append('(b) W %s: KYTY_PIPELINE_PRECACHE=%s in its env - the W form of item 300 (b)(4) is precache by '
                           'default' % (p, env.get('KYTY_PIPELINE_PRECACHE')))
            f4 = sc146.w_form4(env) if env is not None else (False, 'NO JSON')
            det.append('%s %s' % (p, f4[1]))
            if not f4[0]:
                bad.append('(f) W %s: the form line "%s" != "%s" or VK_LAYER_MESSAGE_ID_FILTER in its env (item 295 (b)(4))' % (
                    p, f4[1], sc146.W_FORM_LINE))
            wb = w_admission_bad('%s/score_%s.txt' % (root, p))
            det.append('%s W form rows of item 295 (b) %s' % (p, 'score MISSING' if wb is None else (','.join(wb) or 'pass')))
            if wb is None:
                bad.append('(v) W %s: score_%s.txt missing - the W form rows of item 295 (b) not evaluable' % (p, p))
            elif wb:
                bad.append('(v) W %s fails the W form row(s) %s of item 295 (b) (an instrument stop, question to the lead; item '
                           '295 (v))' % (p, ','.join(wb)))
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
    c0 = sc146.CONTROL[0]
    if tag != c0 and made(c0, root):
        lim = [count_lines('%s/%s_%s.txt' % (root, a, c0), (LIMIT,)) for a in ('log', 'stdout')]
        nl = sum(x[LIMIT] for x in lim if x is not None)
        det.append('%s layer limit lines %d' % (c0, nl))
        if nl:
            bad.append('(l) the control W %s has %d layer limit line(s) (item 273 (k)(2): 0 required)' % (c0, nl))
        mp = '%s/runs146/cache_%s.before.json' % (root, c0)
        sp = '%s/%s' % (root, START_MF)
        want = start_sha(times)
        sgot = sha_file(sp) if os.path.isfile(sp) else None
        if sgot is None:
            bad.append('(c)(2) %s missing' % START_MF)
        elif want is None:
            bad.append('(c)(2) no "GATE start PASS" row naming the sha256 of %s' % START_MF)
        elif sgot != want:
            bad.append('(c)(2) %s sha256 %s != the GATE start row %s (the reference was rewritten)' % (
                START_MF, sgot[:16], want[:16]))
        if not os.path.isfile(mp):
            bad.append('(c)(2) %s missing' % mp.replace(root + '/', ''))
        elif sgot is not None:
            b2, d2 = compare_manifest(json.load(open(mp, encoding='utf-8'))['files'],
                                      json.load(open(sp, encoding='utf-8'))['files'],
                                      what='(c)(2) %s differs from the start manifest')
            bad += b2
            det.append('cache_%s.before %s vs start manifest %s: %s' % (c0, sha_file(mp)[:16], sgot[:16], '; '.join(d2)))
    ws = [t for t in prior if t in sc146.W_TAGS and made(t, root)][-2:]
    psha = sha_file(pred) if os.path.isfile(pred) else None
    keys = [(t,) + w_key(t, root, psha) for t in ws]
    det.append('W keys %s' % (', '.join('%s %s (%s)' % k for k in keys) or 'none'))
    if len(keys) == 2 and keys[0][1] == TIMEOUT_KEY and keys[1][1] == TIMEOUT_KEY:
        bad.append('(g) two W in a row with the key %s: %s,%s' % (TIMEOUT_KEY, keys[0][0], keys[1][0]))
    return bad, det


def start(root, pred, ref, live):
    bad, det = [], []
    want = seal_sha(pred, REF_SEAL) if os.path.isfile(pred) else None
    got = sha_file(ref) if os.path.isfile(ref) else None
    det.append('(r) reference %s sha256 %s (seal %s)' % (os.path.basename(ref), (got or 'MISSING')[:16], (want or 'none')[:16]))
    if got is None or got != want:
        bad.append('(r) the reference %s sha256 %s != its seal line %s (item 295 (e))' % (
            os.path.basename(ref), (got or 'MISSING')[:16], (want or 'none')[:16]))
    fr = disk_free(DISK)
    det.append('(s) free on %s %d bytes = %.1f GiB = %.1f GB (STOP below %d bytes = 60 GiB)' % (DISK, fr, fr / 2.0 ** 30,
                                                                                              fr / 1e9, MIN_FREE))
    if fr < MIN_FREE:
        bad.append('(s) free space on %s %.1f GiB < 60 GiB (item 295 (v))' % (DISK, fr / 2.0 ** 30))
    if got is None:
        det.append('(c)(1) not evaluable: the reference is missing; no start manifest written')
        return bad, det
    if live:
        js = json.load(open(live, encoding='utf-8'))
        rrows, files = js.get('roots'), js['files']
        src = 'manifest %s' % os.path.basename(live)
    else:
        rrows, files = cachemf146.manifest(cachemf146.default_roots())
        src = 'live caches'
    rf = json.load(open(ref, encoding='utf-8'))['files']
    b2, d2 = compare_manifest(files, rf, roots=STRICT, what='(c) %s differs from the end of the warm-up i146_v')
    bad += b2
    d3 = compare_manifest(files, rf, roots=DRIVER)[1]
    pb = [r for r in files if r[0] == 'shader' and r[1] == 'variant_fixb26_fixb1b/pipelines.bin']
    det.append('(c)(1) %s vs %s %s: %s; pipelines.bin %s sig %s' % (
        src, os.path.basename(ref), sha_file(ref)[:16], '; '.join(d2 + d3),
        (pb[0][4][:16] if pb else 'absent'),
        pipelines_sig(cachemf146.default_roots()['shader'] + '/variant_fixb26_fixb1b/pipelines.bin') if not live else 'n/a'))
    det.append(driver_info(files, rf))
    mp = '%s/%s' % (root, START_MF)
    os.makedirs(os.path.dirname(mp), exist_ok=True)
    with open(mp, 'w', encoding='ascii') as f:
        json.dump(dict(taken_utc=utc(), source=src, roots=rrows, files=files), f)
    det.append('(c)(2) reference: start manifest %s sha256 %s' % (START_MF, sha_file(mp)))
    return bad, det


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--start', action='store_true')
    g.add_argument('--before')
    ap.add_argument('--root', default=ROOT)
    ap.add_argument('--times', default=TIMES)
    ap.add_argument('--ref', default=REF)
    ap.add_argument('--live-manifest', default=None)
    ap.add_argument('--pred', default=PRED)
    a = ap.parse_args(argv)
    if a.start:
        what = 'start'
        bad, det = start(a.root, a.pred, a.ref, a.live_manifest)
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
