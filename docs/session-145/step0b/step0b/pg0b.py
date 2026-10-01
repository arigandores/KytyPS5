"""s145 step 0b (HPP-350, ROADMAP s122 item 288 (v), (d)): the gate member (c)(1) split; the seal path 01 -> 02.
Edits C:/kyty/s145/step2/gate145.py in place (LF), every anchor exactly once."""
import sys

P = 'C:/kyty/s145/step2/gate145.py'
t = open(P, 'rb').read().decode('ascii')
assert '\r' not in t


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep('''  --start            before the first lock of step 2: (d) the sha256 of C:/kyty/s144/step2/times.txt and C:/kyty/s144/pred/
                     01_sc144.md (= their seal lines of pred/01_sc145.md) and of the V log v144_09 (= the last "go144a v144_09
                     enter_scene end" line of that times.txt); (c)(1) the live caches (_ShaderCache/PPSA21564, _PipelineCache,
                     GLCache: path, size, sha256 - not mtime) against C:/kyty/s144/runs144/cache_w144_20.after.json (the end
                     of the s144 series), with the header signature of pipelines.bin.
''', '''  --start            before the first lock of step 2: (d) the sha256 of C:/kyty/s144/step2/times.txt and C:/kyty/s144/pred/
                     01_sc144.md (= their seal lines of pred/02_sc145.md) and of the V log v144_09 (= the last "go144a v144_09
                     enter_scene end" line of that times.txt); (c)(1) the live caches (path, size, sha256 - not mtime)
                     against C:/kyty/s144/runs144/cache_w144_20.after.json (the end of the s144 series), split by ROADMAP s122
                     item 288 (v): the translation cache _ShaderCache/PPSA21564 with pipelines.bin differs -> STOP (c)(1)
                     (item 288 (v)(1)); _PipelineCache and GLCache differ -> the data segment "(c)(1) info driver caches: ..."
                     with the names and sha256 (16 hex) of the added, removed and changed files, not STOP (item 288 (v)(2));
                     with the header signature of pipelines.bin; then it WRITES the start manifest runs145/cache_start.json
                     (the live manifest it read; the reference of continuity within the series, item 288 (v)(3)) and names
                     its sha256 in its row ("start manifest runs145/cache_start.json sha256 <64 hex>").
''')
rep('''                     reporting it", log and stdout) >= 1 -> STOP (item 273 (k)(2)); (c)(2) w145_00 made ->
                     runs145/cache_w145_00.before.json against the same s144 manifest; (g) the last two made W (the control
''', '''                     reporting it", log and stdout) >= 1 -> STOP (item 273 (k)(2)); (c)(2) w145_00 made ->
                     runs145/cache_w145_00.before.json against the start manifest runs145/cache_start.json, every root
                     (item 288 (v)(3)-(4)); the start manifest missing, or its sha256 != the one named by the last "GATE
                     start PASS" row -> STOP; (g) the last two made W (the control
''')
rep('''rc 0 PASS, rc 5 STOP, rc 2 usage.  READ ONLY on everything but the one times row.  ASCII only.''',
    '''rc 0 PASS, rc 5 STOP, rc 2 usage.  READ ONLY on everything but the one times row and (--start only) the start manifest
runs145/cache_start.json.  ASCII only.''')
rep("PRED = ROOT + '/pred/01_sc145.md'\n", "PRED = ROOT + '/pred/02_sc145.md'\n")
rep("TIMEOUT_KEY = 'attempt:timeout'\n", """TIMEOUT_KEY = 'attempt:timeout'
STRICT = ('shader',)               # item 288 (v)(1): the translation cache of the root with pipelines.bin -> STOP
DRIVER = ('pipeline', 'glcache')   # item 288 (v)(2): the driver caches -> a data segment, not STOP
START_MF = 'runs145/cache_start.json'
RX_START = re.compile(r'^\\S+ GATE start PASS\\b.*start manifest runs145/cache_start\\.json sha256 ([0-9a-f]{64})')
""")
rep('''    """The sha256 of the seal line naming <name> (pred/01_sc145.md), or None."""''',
    '''    """The sha256 of the seal line naming <name> (pred/02_sc145.md), or None."""''')
rep('''    """(d): (bad reasons, detail) - the s144 times and seal sha against pred/01_sc145.md, the V log v144_09 against the last''',
    '''    """(d): (bad reasons, detail) - the s144 times and seal sha against pred/02_sc145.md, the V log v144_09 against the last''')
rep('''def compare_manifest(files, ref_files):
    """(bad reasons, detail) of two manifests by path, size and sha256 per root."""
    a, b = mf_rows(files), mf_rows(ref_files)
    bad, det = [], []
    for root in cachemf145.ORDER:
''', '''def compare_manifest(files, ref_files, roots=cachemf145.ORDER, what='(c) %s differs from the s144 end'):
    """(bad reasons, detail) of two manifests by path, size and sha256 per root of <roots>."""
    a, b = mf_rows(files), mf_rows(ref_files)
    bad, det = [], []
    for root in roots:
''')
rep('''            bad.append('(c) %s differs from the s144 end: +%d -%d changed %d (%s)' % (
                root, len(add), len(rem), len(chg), ', '.join(k[1] for k in ex)))
    return bad, det
''', '''            bad.append((what % root) + ': +%d -%d changed %d (%s)' % (
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
''')
rep('''        mp = '%s/runs145/cache_%s.before.json' % (root, c0)
        if not os.path.isfile(mp):
            bad.append('(c)(2) %s missing' % mp.replace(root + '/', ''))
        else:
            b2, d2 = compare_manifest(json.load(open(mp, encoding='utf-8'))['files'],
                                      json.load(open(ref, encoding='utf-8'))['files'])
            bad += [x.replace('(c)', '(c)(2)') for x in b2]
            det.append('cache_%s.before %s vs ref %s: %s' % (c0, sha_file(mp)[:16], sha_file(ref)[:16], '; '.join(d2)))
''', '''        mp = '%s/runs145/cache_%s.before.json' % (root, c0)
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
''')
rep('''def start(root144, pred, ref, live):
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
''', '''def start(root, root144, pred, ref, live):
    bad, det = check144(root144, pred)
    if live:
        js = json.load(open(live, encoding='utf-8'))
        rrows, files = js.get('roots'), js['files']
        src = 'manifest %s' % os.path.basename(live)
    else:
        rrows, files = cachemf145.manifest(cachemf145.default_roots())
        src = 'live caches'
    rf = json.load(open(ref, encoding='utf-8'))['files']
    b2, d2 = compare_manifest(files, rf, roots=STRICT, what='(c) %s differs from the s144 end')
    bad += b2
    d3 = compare_manifest(files, rf, roots=DRIVER)[1]
    pb = [r for r in files if r[0] == 'shader' and r[1] == 'pipelines.bin']
    det.append('(c)(1) %s vs %s %s: %s; pipelines.bin %s sig %s' % (
        src, os.path.basename(ref), sha_file(ref)[:16], '; '.join(d2 + d3),
        (pb[0][4][:16] if pb else 'absent'),
        pipelines_sig(cachemf145.default_roots()['shader'] + '/pipelines.bin') if not live else 'n/a'))
    det.append(driver_info(files, rf))
    mp = '%s/%s' % (root, START_MF)
    os.makedirs(os.path.dirname(mp), exist_ok=True)
    with open(mp, 'w', encoding='ascii') as f:
        json.dump(dict(taken_utc=utc(), source=src, roots=rrows, files=files), f)
    det.append('(c)(2) reference: start manifest %s sha256 %s' % (START_MF, sha_file(mp)))
    return bad, det
''')
rep('''        bad, det = start(a.root144, a.pred, a.ref, a.live_manifest)''',
    '''        bad, det = start(a.root, a.root144, a.pred, a.ref, a.live_manifest)''')
open(P, 'wb').write(t.encode('ascii'))
print('gate145.py patched')
