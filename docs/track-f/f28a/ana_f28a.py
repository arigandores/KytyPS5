# F28a (HPP-698, ROADMAP s122 item 638(v)(2)-(4)): reading of sweep_f28a.jsonl.
# Scope of the count (item 638(v)(2)): logs whose translation-cache line names a variant with 'fixb1b' (KYTY_FIX_B1B in
# effect, shaderTranslationCache.cpp) AND whose startup line is "BvhLoopCap: cap=65536 token=''" (limiter at its default,
# counters armed) AND whose tag json does not set KYTY_BVH_LOOP_CAP*.  Logs without fixb1b - reference ("before F9").
# Entry = a 'Level has started: <name>' line with a non-empty name.  Signs that 380bb9d636390bae ran (named, [c] of code):
#   FU  'ShaderFirstUse: hash=380bb9d636390bae stage=4'   - PipelineCache Get() of the dispatch path (KYTY_SHADER_REGISTER_TRACE)
#   PF  'AsyncCompute: prefetch hash=0x380bb9d636390bae'  - PM4 lookahead found a dispatch of the program in a submitted buffer
#   PM  'CsPretranslate: miss hash=380bb9d636390bae'      - pretranslation lookup of the dispatch path
#   TR  'BvhLoopCap: shader=0x380bb9d636390bae loops=..'  - translation of the program after the entry line (cold entry)
# An entry has sign E when one of them is attributed to it (between its line and the next entry line).  Sign L: no E in
# this entry, but the level has E in some log of the list (any binary) - [I] same level, same program.
# Markers per entry: TRIP 'BvhLoopCapTrip:' lines, BLT / BLN non-zero 'bl_trip=' / 'bl_near=' FrameTrace fields,
# HANG 'GpuHangAbort:' / 'ErrorDeviceLost', CRASH 'Unhandled exception:' / '--- Fatal Error ---' / '--- Error ---'.
# Duplicates (the same log copied to two places): key (size, entry positions, t_end); the first path is kept.
# usage: python ana_f28a.py <sweep.jsonl> <entries.tsv>
import collections, json, re, sys

FIXTURE = re.compile(r'/(fx[^/]*|fixt[^/]*)/')  # fixture logs (copies with edited lines, F26a/F26c/P5 readers)

COURSE = {'dac02fb9': 'dac02fb9 (FSa)', 'bbad499c': 'FS2', '4aa62e95': 'P23', '540c035a': 'FS3', '31cbfee8': 'FS4',
          '631ff987': 'FS5', 'adb0c82f': 'S12', '9325446c': 'FS6', '8df61c00': 'FS7', '2c9b69b9': 'FS8',
          'b3cee576': 'S18', '3861eeea': 'FS9', 'abfded5e': 'FS10'}


def lvl(e):
    return e['line'].split('Level has started: ', 1)[1].strip()


def main():
    R = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
    out_tsv = sys.argv[2]
    seen = {}
    dups = []
    for r in R:
        k = (r['size'], tuple(e['pos'] for e in r.get('entries', [])), r.get('t_end'))
        if k in seen and r.get('entries'):
            dups.append((r['path'], seen[k]))
            r['dup'] = True
        else:
            seen[k] = r['path']
    print('logs', len(R), 'duplicates (same size, entry positions, end time)', len(dups))
    for a, b in dups[:20]:
        print('   dup', a, '=', b)

    def signs(r):
        L = r.get('lines', {})
        s = collections.defaultdict(set)
        for j, l in L.get('P380', []):
            if 'ShaderFirstUse' in l and 'stage=4' in l:
                s[j].add('FU')
            elif 'AsyncCompute: prefetch' in l:
                s[j].add('PF')
            elif 'CsPretranslate: miss' in l:
                s[j].add('PM')
        for j, l in L.get('CAP', []):
            if 'shader=0x380bb9d636390bae' in l:
                s[j].add('TR')
        return s

    lvl_e = collections.defaultdict(set)
    for r in R:
        s = signs(r)
        for j, v in s.items():
            if j >= 0:
                n = lvl(r['entries'][j])
                if n:
                    lvl_e[n].add(r['path'])
    print('levels with sign E in some log:', len(lvl_e))

    rows = []
    glob = collections.Counter()
    ref = collections.Counter()
    nfx = 0
    for r in R:
        if r.get('dup') or r.get('empty'):
            continue
        if FIXTURE.search(r['path']):
            nfx += 1
            continue
        L = r.get('lines', {})
        tc = [l for _, l in L.get('TC', [])]
        b1b = any('fixb1b' in l for l in tc)
        capl = [l for _, l in L.get('CAP', []) if 'shader=' not in l]
        cap_def = any("cap=65536 token=''" in l for l in capl)
        env_cap = r.get('env_cap') or []
        cnt = r.get('counts', {})
        tot = {k: sum(cnt.get(k, {}).values()) for k in ('TRIP', 'BLT', 'BLN', 'HANG', 'CRASH')}
        if not b1b:
            for k, v in tot.items():
                ref[k] += v
            ref['logs'] += 1
            ref['logs_with_TRIP'] += tot['TRIP'] > 0
            continue
        scope = cap_def and not env_cap
        glob['b1b_logs'] += 1
        glob['b1b_logs_in_scope'] += scope
        for k, v in tot.items():
            glob[k + (' in_scope' if scope else ' out_scope')] += v
        sha = (r.get('binary_sha256') or '')[:8]
        binn = COURSE.get(sha, sha or '?')
        s = signs(r)
        for j, e in enumerate(r.get('entries', [])):
            n = lvl(e)
            if not n:
                continue
            c = {k: cnt.get(k, {}).get(str(j), 0) for k in ('TRIP', 'BLT', 'BLN', 'HANG', 'CRASH')}
            sg = ','.join(sorted(s.get(j, set())))
            cls = 'E' if sg else ('L' if n in lvl_e else '-')
            rows.append((r['path'], binn, n, e['hold_s'], cls, sg or '-', c, scope, r.get('env_hang')))
    print('fixture logs excluded', nfx)
    print('reference (logs without fixb1b, before F9 or KYTY_FIX_B1B=0):', dict(ref))
    print('logs with fixb1b:', dict(glob))
    with open(out_tsv, 'w', encoding='utf-8', newline='\n') as f:
        f.write('path\tbinary\tlevel\thold_s\tsign\tsign_kinds\tTRIP\tBLT\tBLN\tHANG\tCRASH\tin_scope\tenv_hang\n')
        for p, b, n, h, cls, sg, c, sc, eh in rows:
            f.write('%s\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n' % (
                p, b, n, '%.1f' % h if h is not None else '-', cls, sg, c['TRIP'], c['BLT'], c['BLN'], c['HANG'], c['CRASH'],
                int(sc), ','.join(eh or []) or '-'))
    ins = [x for x in rows if x[7]]
    print('entries (non-empty level) on fixb1b logs', len(rows), 'in scope', len(ins))
    for lab, sel in (('all', ins), ('hold>=120', [x for x in ins if x[3] is not None and x[3] >= 120]),
                     ('hold>=300', [x for x in ins if x[3] is not None and x[3] >= 300])):
        byc = collections.Counter(x[4] for x in sel)
        mk = collections.Counter()
        for x in sel:
            for k, v in x[6].items():
                mk[k] += v
        print('  %-10s entries %4d  sign E %4d  L %4d  none %4d  markers %s' % (lab, len(sel), byc['E'], byc['L'], byc['-'], dict(mk)))
    course = set(COURSE.values())
    for lab, sel in (('course-line binaries, hold>=120', [x for x in ins if x[1] in course and (x[3] or 0) >= 120]),
                     ('other binaries (tests), hold>=120', [x for x in ins if x[1] not in course and (x[3] or 0) >= 120])):
        byc = collections.Counter(x[4] for x in sel)
        print('  %-36s entries %4d  E %4d  L %4d  none %4d  logs %d' % (lab, len(sel), byc['E'], byc['L'], byc['-'],
                                                                     len({x[0] for x in sel})))
    e = [x for x in ins if x[4] == 'E']
    with open(out_tsv.replace('.tsv', '_E.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for x in sorted(e, key=lambda x: (x[1], x[0])):
            f.write('\t'.join([x[0], x[1], x[2], '%.1f' % (x[3] or 0), x[5]]) + '\n')
    print('  E entries by binary', collections.Counter(x[1] for x in e).most_common())
    print('  E entries by level', collections.Counter(x[2] for x in e).most_common())
    print('  E entries by sign kinds', collections.Counter(x[5] for x in e).most_common())
    print('  E entries hold', sorted(round(x[3] or 0) for x in e))
    bad = [x for x in ins if any(x[6].values())]
    print('  in-scope entries with any marker:', len(bad))
    for x in bad:
        print('    ', x[0], x[1], x[2], x[3], x[4], x[6])
    badl = [x for x in rows if not x[7] and any(x[6].values())]
    print('  out-of-scope fixb1b entries with any marker:', len(badl))
    for x in badl[:20]:
        print('    ', x[0], x[1], x[2], x[3], x[4], x[6])


if __name__ == '__main__':
    main()
