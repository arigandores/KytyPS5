"""s145 step 0b (HPP-350, ROADMAP s122 item 288 (v)): fixtures of the split gate member (c)(1) and the start manifest in
C:/kyty/s145/step2/test_gate145.py (LF), every anchor exactly once."""
P = 'C:/kyty/s145/step2/test_gate145.py'
t = open(P, 'rb').read().decode('ascii')
assert '\r' not in t


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep('''  g6  a manifest with one changed sha256 (start and (c)(2)) against the s144 end          -> STOP by (c); unchanged -> PASS
''', '''  g6  a manifest with one changed sha256 of pipelines.bin (start) against the s144 end    -> STOP by (c)(1); unchanged ->
      PASS; a GLCache file missing -> PASS with the info segment (item 288 (v)(2)); (c)(2) against the start manifest
''')
rep('''  g13 the control w145_00 with a layer limit line in its log or its stdout                -> STOP by (l); 0 -> PASS
''', '''  g13 the control w145_00 with a layer limit line in its log or its stdout                -> STOP by (l); 0 -> PASS
  g14 item 288 (v): a translation cache file changed -> STOP (c)(1); pipelines.bin changed -> STOP (c)(1); only
      _PipelineCache / GLCache changed -> PASS with "(c)(1) info driver caches:" naming the files and sha; a GLCache file
      added / removed -> PASS with the info; unchanged -> the info with zeros; the shader root gone -> STOP; --start writes
      runs145/cache_start.json (= the manifest read) and names its sha256 in its row; (c)(2) reads it: the control's
      manifest = start -> PASS, = the s144 end (driver caches differ from start) -> STOP, start manifest rewritten -> STOP,
      missing -> STOP, a start row without the sha -> STOP
''')
rep('''def rows(root, *what):
    with open(root + '/step2/times.txt', 'a', encoding='ascii') as f:
        for w in what:
            f.write('2026-10-01T00:00:00Z GATE %s PASS; fixture row\\n' % w)
''', '''def rows(root, *what):
    """GATE <what> PASS rows; the start row also gets the start manifest runs145/cache_start.json (= the s144 end, as a
    clean --start would write it) and names its sha256 like gate145.py --start."""
    with open(root + '/step2/times.txt', 'a', encoding='ascii') as f:
        for w in what:
            if w == 'start':
                shutil.copyfile(REF, root + '/' + G.START_MF)
                f.write('2026-10-01T00:00:00Z GATE start PASS; fixture row | (c)(2) reference: start manifest %s sha256 %s\\n'
                        % (G.START_MF, sha(root + '/' + G.START_MF)))
            else:
                f.write('2026-10-01T00:00:00Z GATE %s PASS; fixture row\\n' % w)
''')
rep('''    check('g6 a glcache file missing -> STOP (c) glcache', rc == 5 and '(c) glcache differs' in last, reasons(last))
''', '''    check('g6 a glcache file missing -> PASS with the info segment (item 288 (v)(2))', rc == 0 and
          '(c)(1) info driver caches: pipeline +0 -0 changed 0; glcache +0 -1 changed 0 (-%s %s)' % (
              ref['files'][j][1], ref['files'][j][4][:16]) in last and '(c) glcache' not in last, last)
''')
rep('''    print('checks: %d / %s' % (NCHECK[0], 'ALL OK' if not FAILS else 'FAILED %d: %s' % (len(FAILS), ', '.join(FAILS))))
''', '''    # g14: item 288 (v) - the split of (c)(1) and the start manifest
    r = fresh('g14')
    sp = seal144(r + '/pred.md')

    def mf(name, edit):
        m = json.loads(json.dumps(ref))
        edit(m)
        p = r + '/' + name + '.json'
        json.dump(m, open(p, 'w', encoding='utf-8'))
        return p

    def idx(root, rel=None, skip=None):
        return [k for k, x in enumerate(ref['files']) if x[0] == root and (rel is None or x[1] == rel)
                and (skip is None or x[1] != skip)][0]

    ish, ipb = idx('shader', skip='pipelines.bin'), idx('shader', 'pipelines.bin')
    ipl, igl = idx('pipeline', 'PPSA21564.bin'), idx('glcache')
    F = ref['files']
    tr = mf('tr', lambda m: m['files'][ish].__setitem__(4, '1' * 64))
    rc, last = run(r, '--start', '--live-manifest', tr, '--pred', sp)
    check('g14 a translation cache file changed -> STOP (c)(1) shader', rc == 5 and
          '(c) shader differs from the s144 end: +0 -0 changed 1 (%s)' % F[ish][1] in last, reasons(last))
    pbm = mf('pb', lambda m: m['files'][ipb].__setitem__(2, m['files'][ipb][2] + 1))
    rc, last = run(r, '--start', '--live-manifest', pbm, '--pred', sp)
    check('g14 pipelines.bin changed (size) -> STOP (c)(1) shader', rc == 5 and
          '(c) shader differs from the s144 end: +0 -0 changed 1 (pipelines.bin)' in last, reasons(last))

    def drv_edit(m):
        m['files'][ipl][4] = '2' * 64
        m['files'][igl][4] = '3' * 64
    drv = mf('drv', drv_edit)
    rc, last = run(r, '--start', '--live-manifest', drv, '--pred', sp)
    check('g14 only _PipelineCache and GLCache changed -> PASS', rc == 0 and ' GATE start PASS' in last, reasons(last))
    check('g14 the info segment names both files with the old and new sha',
          '(c)(1) info driver caches: pipeline +0 -0 changed 1 (~PPSA21564.bin %s->%s); glcache +0 -0 changed 1 (~%s %s->%s) '
          '(item 288 (v)(2): data, not STOP)' % (F[ipl][4][:16], '2' * 16, F[igl][1], F[igl][4][:16], '3' * 16) in last, last)
    add = mf('add', lambda m: m['files'].append(['glcache', 'x/new.bin', 5, 1, '4' * 64]))
    rc, last = run(r, '--start', '--live-manifest', add, '--pred', sp)
    check('g14 a GLCache file added -> PASS with the info', rc == 0 and
          'glcache +1 -0 changed 0 (+x/new.bin %s)' % ('4' * 16) in last, last)
    rem = mf('rem', lambda m: m['files'].__delitem__(ipl))
    rc, last = run(r, '--start', '--live-manifest', rem, '--pred', sp)
    check('g14 a _PipelineCache file removed -> PASS with the info', rc == 0 and
          'pipeline +0 -1 changed 0 (-PPSA21564.bin %s)' % F[ipl][4][:16] in last, last)
    rc, last = run(r, '--start', '--live-manifest', same, '--pred', sp)
    check('g14 unchanged -> PASS, the info with zeros', rc == 0 and
          '(c)(1) info driver caches: pipeline +0 -0 changed 0; glcache +0 -0 changed 0 (item 288' in last, last)
    nosh = mf('nosh', lambda m: m.__setitem__('files', [x for x in m['files'] if x[0] != 'shader']))
    rc, last = run(r, '--start', '--live-manifest', nosh, '--pred', sp)
    check('g14 the shader root gone -> STOP (c)(1)', rc == 5 and '(c) shader differs from the s144 end: +0 -%d' % sum(
        1 for x in F if x[0] == 'shader') in last, reasons(last))
    r2 = fresh('g14b')
    smf = r2 + '/' + G.START_MF
    rc, last = run(r2, '--start', '--live-manifest', drv, '--pred', sp)
    sm = json.load(open(smf, encoding='utf-8'))
    check('g14 --start writes the start manifest = the manifest read and names its sha256 in its row',
          rc == 0 and sm['files'] == json.load(open(drv, encoding='utf-8'))['files'] and
          'start manifest runs145/cache_start.json sha256 %s' % sha(smf) in last and G.start_sha(r2 + '/step2/times.txt')
          == sha(smf), last)
    rows(r2, 'w145_00')
    synth_w(r2, 'w145_00', 'ok')
    shutil.copyfile(drv, r2 + '/runs145/cache_w145_00.before.json')
    rc, last = run(r2, '--before', 'w145_01')
    check('g14 (c)(2) the control manifest = the start manifest -> PASS', rc == 0 and 'cache_w145_00.before %s vs start '
          'manifest %s' % (sha(drv)[:16], sha(smf)[:16]) in last, last)
    shutil.copyfile(REF, r2 + '/runs145/cache_w145_00.before.json')
    rc, last = run(r2, '--before', 'w145_01')
    check('g14 (c)(2) the control manifest = the s144 end (driver caches differ from the start) -> STOP',
          rc == 5 and '(c)(2) pipeline differs from the start manifest: +0 -0 changed 1 (PPSA21564.bin)' in last and
          '(c)(2) glcache differs from the start manifest' in last and '(c)(2) shader' not in last, reasons(last))
    shutil.copyfile(drv, r2 + '/runs145/cache_w145_00.before.json')
    json.dump(sm, open(smf, 'w', encoding='ascii'), indent=1)
    rc, last = run(r2, '--before', 'w145_01')
    check('g14 (c)(2) the start manifest rewritten after its row -> STOP', rc == 5 and '(c)(2) runs145/cache_start.json '
          'sha256' in last and '(the reference was rewritten)' in last, reasons(last))
    os.remove(smf)
    rc, last = run(r2, '--before', 'w145_01')
    check('g14 (c)(2) the start manifest missing -> STOP', rc == 5 and '(c)(2) runs145/cache_start.json missing' in last,
          reasons(last))
    r3 = fresh('g14c')
    with open(r3 + '/step2/times.txt', 'a', encoding='ascii') as f:
        f.write('2026-10-01T00:00:00Z GATE start PASS; fixture row without the sha\\n')
    shutil.copyfile(REF, r3 + '/' + G.START_MF)
    rows(r3, 'w145_00')
    synth_w(r3, 'w145_00', 'ok')
    shutil.copyfile(REF, r3 + '/runs145/cache_w145_00.before.json')
    rc, last = run(r3, '--before', 'w145_01')
    check('g14 (c)(2) a start row without the sha of the start manifest -> STOP', rc == 5 and
          '(c)(2) no "GATE start PASS" row naming the sha256 of runs145/cache_start.json' in last, reasons(last))
    print('checks: %d / %s' % (NCHECK[0], 'ALL OK' if not FAILS else 'FAILED %d: %s' % (len(FAILS), ', '.join(FAILS))))
''')
open(P, 'wb').write(t.encode('ascii'))
print('test_gate145.py patched')
