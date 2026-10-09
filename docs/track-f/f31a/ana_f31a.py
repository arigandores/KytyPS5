# F31a: reading of sweep_f31a.jsonl - (a) every log with a B25 signature; (b) entries by scene and binary; (c) the entries of
# mini_giants_garden (hold by guest frames, binary, KYTY_RT_SKIP, signature).  Binary of a log: the tag json binary_sha256
# (sha8) if any, else the build line revision 'rev:<7>'.  'Line' binaries: the installed shipping binaries since 9235a7ac
# (CLAUDE.md state lines) by sha8, and by revision when the json is absent (the worktree HEAD of each shipping build).
import collections, json, sys
src = sys.argv[1]
LINE_SHA = {'9235a7ac': 'base128', 'dac02fb9': 'FSc', 'bbad499c': 'FS2', '4aa62e95': 'P23', '540c035a': 'FS3', '31cbfee8': 'FS4',
            '631ff987': 'FS5', 'adb0c82f': 'S12', '9325446c': 'FS6', '8df61c00': 'FS7', '2c9b69b9': 'FS8', 'b3cee576': 'S18',
            '3861eeea': 'FS9', 'abfded5e': 'FS10', 'ea51ae80': 'FS11'}
LINE_REV = {'4fc501f': '9235a7ac', '95eec77': 'dac02fb9', '9c9d86a': 'bbad499c', '4414e23': '4aa62e95', '3d0e46d': '31cbfee8',
            '0e72bc1': '631ff987', '4d9e8ab': 'adb0c82f', '3904522': '9325446c', 'd6ee2dc': '8df61c00', '302347b': '2c9b69b9',
            '0005e11': 'b3cee576', '11164d7': '3861eeea', 'dc5d471': 'abfded5e', 'ee9632b': 'ea51ae80'}
recs = [json.loads(l) for l in open(src, encoding='utf-8')]
def binof(r):
    sha = (r.get('binary_sha256') or '')[:8]
    rev = None
    b = r.get('build') or ''
    if 'KytyPS5 ' in b:
        rev = b.split('KytyPS5 ', 1)[1].strip()[:7]
    if sha:
        return sha, rev
    if rev in LINE_REV:
        return LINE_REV[rev], rev
    return 'rev:%s' % rev if rev else '?', rev
print('logs', len(recs), 'errors', sum(1 for r in recs if r.get('error')), 'empty', sum(1 for r in recs if r.get('empty')))
for r in recs:
    if r.get('error'):
        print('  error', r['path'], r['error'])
print()
print('(a) logs with any B25 signature')
for r in recs:
    if any(r.get('S') or []):
        b, rev = binof(r)
        ent = r['entries']
        print(' ', r['path'], 'S', r['S'], 'bin', b, LINE_SHA.get(b, ''), 'rev', rev, 'rtskip', r.get('rtskip'))
        for x in r['sig']:
            e = ent[x['ent']] if x.get('ent') is not None else None
            print('    sig', x['k'], 't', x['t'], 'entry', e['name'] if e else None, 'entry_t', e['t'] if e else None,
                  'frames_before', x.get('ent_frames'), 'hold_before_s', round(x.get('ent_us', 0) / 1e6, 1))
print()
cnt = collections.Counter(); hold = collections.Counter(); line_cnt = collections.Counter(); line_hold = collections.Counter()
for r in recs:
    b, rev = binof(r)
    for e in r.get('entries') or []:
        cnt[e['name']] += 1; hold[e['name']] += e['sum_us']
        if b in LINE_SHA:
            line_cnt[e['name']] += 1; line_hold[e['name']] += e['sum_us']
print('(b) entries by scene (all logs / line binaries), hold by guest frames in h; scenes', len(cnt))
for n, c in sorted(cnt.items(), key=lambda kv: -hold[kv[0]]):
    print('  %-40s %5d %8.2f h | line %5d %8.2f h' % (n, c, hold[n] / 3.6e9, line_cnt[n], line_hold[n] / 3.6e9))
print()
print('(c) mini_giants_garden entries')
rows = []
for r in recs:
    b, rev = binof(r)
    for i, e in enumerate(r.get('entries') or []):
        if e['name'] != 'mini_giants_garden':
            continue
        sig = [x for x in r.get('sig') or [] if x.get('ent') == i]
        env = r.get('env') or {}
        rows.append((r['path'], b, LINE_SHA.get(b, '-'), rev, env.get('KYTY_RT_SKIP', '-'), r.get('rtskip'), e['frames'],
                     round(e['sum_us'] / 1e6, 1), len(sig), r.get('n_error'), r.get('n_unhandled'),
                     ','.join(sorted(k for k in env if k not in ('KYTY_GUEST_ARGS', 'KYTY_REC', 'KYTY_FRAME_TRACE')))[:200]))
for x in sorted(rows):
    print('  ' + ' | '.join(str(v) for v in x))
n90 = [x for x in rows if x[7] >= 90]
print('mini_giants_garden entries', len(rows), 'hold >= 90 s', len(n90), 'sum hold h %.2f' % (sum(x[7] for x in rows) / 3600),
      'with signature', sum(1 for x in rows if x[8]))
lin = [x for x in rows if x[2] != '-']
print('  on line binaries', len(lin), 'hold >= 90 s', sum(1 for x in lin if x[7] >= 90), 'sum hold h %.2f' % (sum(x[7] for x in lin) / 3600))
