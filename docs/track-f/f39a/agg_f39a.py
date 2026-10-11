# F39a (HPP-767): summary of sweep_f39a.jsonl - witnesses of F24 (ROADMAP s122 item 691(zh)(3)): 'Controller <id>: removed'
# lines and 'MainTaskLate: us=<n>' >= 1 000 000; build of every log ('Fork build ... <hash>'), course-line builds marked,
# FixB24 mode; classes of every MainTaskLate >= 1 s: STARTUP (within 12 lines after the startup preparation
# wait end, or before the first level entry), STALL_TEST (MainStallTest queued in the log), STAND (TestHidLoss config in the
# log and the line between 'fire' and 'stat' of the stand), OTHER. Duplicates by (bytes, lines, hits) are counted once.
# Usage: python agg_f39a.py <sweep.jsonl> <out.txt>
import json, os, re, sys, collections

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
# course line (CLAUDE.md state line; F32a binmap.tsv) + FS12 = 730ed40 ('Fork build' hash, 7 chars)
COURSE = {'4fc501f': '9235a7ac', '95eec77': 'dac02fb9', '9c9d86a': 'FS2', '4414e23': 'P23', 'd515b90': 'FS3',
          '3d0e46d': 'FS4', '0e72bc1': 'FS5', '4d9e8ab': 'S12', '3904522': 'FS6', 'd6ee2dc': 'FS7', '302347b': 'FS8',
          '0005e11': 'S18', '11164d7': 'FS9', 'dc5d471': 'FS10', 'ee9632b': 'FS11', '730ed40': 'FS12'}
RX_BUILD = re.compile(r'Fork build \S+ ([0-9a-f]{7,12})')
RX_LATE = re.compile(r'MainTaskLate: us=(\d+)')


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        sys.exit(3)
    recs = {}
    for l in open(sys.argv[1], encoding='utf-8'):
        r = json.loads(l)
        recs[r['path']] = r
    out = open(sys.argv[2], 'w', encoding='utf-8', newline=chr(10))

    def p(*a):
        s = ' '.join(str(x) for x in a)
        print(s)
        out.write(s + chr(10))

    errs = [r for r in recs.values() if 'error' in r]
    ok = [r for r in recs.values() if 'error' not in r]
    uniq = {}
    for r in ok:
        key = (r['bytes'], r['lines'], json.dumps(r['hits'], sort_keys=True))
        uniq.setdefault(key, []).append(r['path'])
    p('records', len(recs), 'errors', len(errs), 'ok', len(ok), 'distinct logs', len(uniq))
    for r in errs:
        p('  ERROR', r['path'], r['error'])
    by_build = collections.Counter()
    course_logs = 0
    removed_logs, late_rows, connect_logs, unknown_logs = [], [], [], []
    b24 = collections.Counter()
    for key, paths in sorted(uniq.items(), key=lambda kv: kv[1][0]):
        r = next(x for x in ok if x['path'] == paths[0])
        h = r['hits']
        m = RX_BUILD.search(h['build'][0][1]) if 'build' in h else None
        build = m.group(1)[:7] if m else '?'
        name = COURSE.get(build, '')
        by_build[(build, name)] += 1
        if name:
            course_logs += 1
        fb = h.get('fixb24', [[0, '']])[0][1].strip() if 'fixb24' in h else 'none'
        b24[(bool(name), fb)] += 1
        tag = '%s %s [%s] b24=%s copies=%d' % (paths[0], build, name or 'not course', fb, len(paths))
        if 'removed' in h:
            removed_logs.append((tag, h['removed'], h.get('hidloss', [])))
        if 'connect' in h:
            connect_logs.append((tag, h['connect']))
        if 'unknown_id' in h:
            unknown_logs.append((tag, h['unknown_id']))
        for n, line in h.get('late', []):
            us = int(RX_LATE.search(line).group(1))
            if us < 1000000:
                continue
            prep = [x[0] for x in h.get('prepdone', [])]
            lvl = [x[0] for x in h.get('level', [])]
            fire = [x[0] for x in h.get('hidloss', []) if 'TestHidLoss: fire' in x[1]]
            stat = [x[0] for x in h.get('hidloss', []) if 'TestHidLoss: stat' in x[1]]
            if 'stall' in h:
                cls = 'STALL_TEST'
            elif fire and any(f <= n and (not stat or n <= max(stat)) for f in fire):
                cls = 'STAND'
            elif (prep and n <= max(prep) + 12) or (not lvl or n < lvl[0]):
                cls = 'STARTUP'
            else:
                cls = 'OTHER'
            late_rows.append((cls, us, n, tag))
    p('course-line logs (distinct)', course_logs)
    p('by build:')
    for (b, nm), c in sorted(by_build.items(), key=lambda kv: -kv[1]):
        p('  %s %-9s %d' % (b, nm or '-', c))
    p('FixB24 line by course/not:', dict(b24))
    p('')
    p('== Controller <id>: removed - logs:', len(removed_logs), 'lines:', sum(len(x[1]) for x in removed_logs))
    for tag, rows, hl in removed_logs:
        mode = [x[1] for x in hl if 'config' in x[1]]
        p('  ' + tag + ' stand=' + (mode[0].strip()[:80] if mode else 'none'))
        for n, line in rows:
            p('     line %d: %s' % (n, line.strip()[:120]))
    p('')
    cls_c = collections.Counter(x[0] for x in late_rows)
    p('== MainTaskLate >= 1 s - rows:', len(late_rows), 'logs:', len(set(x[3] for x in late_rows)), dict(cls_c))
    for cls, us, n, tag in sorted(late_rows, key=lambda x: (x[0], x[3], x[2])):
        p('  %-10s us=%-9d line %-9d %s' % (cls, us, n, tag))
    p('')
    p('== logs with a host pad (connect line):', len(connect_logs))
    for tag, rows in connect_logs:
        names = sorted(set(re.sub(r'path=.*', 'path=<masked>', x[1].strip())[:90] for x in rows))
        p('  ' + tag + ' n=' + str(len(rows)))
        for nm in names:
            p('     ' + nm)
    p('')
    p('== disconnect of unknown id:', len(unknown_logs))
    for tag, rows in unknown_logs:
        p('  ' + tag + ' line ' + str(rows[0][0]))
    out.close()


if __name__ == '__main__':
    main()
