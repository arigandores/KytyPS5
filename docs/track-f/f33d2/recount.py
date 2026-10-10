# F33d2 (HPP-749): own recount of the CN/C members from the raw .err files (not via the driver's parse) + rc/dur from TSV.
import csv, glob, os, sys
for d in ('runs', 'runs_b007', 'runs_m4b', 'runs_m4a'):
    for arm in ('CN', 'C'):
        tsv = '%s/fix1/stand_%s.tsv' % (d, arm)
        if not os.path.exists(tsv):
            continue
        rows = {r['seed']: r for r in csv.DictReader(open(tsv, encoding='utf-8'), delimiter='\t')}
        agg = {'n': 0, 'pass': 0, 'walks!=1': 0, 'nested': 0, 'reenter<2': 0, 'expired': 0, 'expired_seen': 0,
               'rc!=321': 0, 'dur>=6': 0, 'done_seen': 0, 'nf!=1': 0}
        for s, r in rows.items():
            t = open('%s/fix1/%s/%s.err' % (d, arm, s), encoding='utf-8').read().splitlines()
            c = lambda p: sum(1 for x in t if x.startswith(p))
            w = c('ExitFatal: walk_begin'); ne = sum(1 for x in t if x.startswith('ExitFatal: walk_begin') and ' nested=1 ' in x)
            f = {'walks!=1': w != 1, 'nested': ne > 0, 'reenter<2': c('ExitFatal: reenter') < (2 if arm == 'CN' else 1),
                 'expired': c('FixF21: wait_expired') > 0, 'expired_seen': c('ExitFatal: expired_seen') > 0,
                 'rc!=321': (int(r['rc']) & 0xffffffff) != 321 if r['rc'] else True, 'dur>=6': float(r['dur_s']) >= 6.0,
                 'done_seen': c('ExitFatal: done_seen') > 0, 'nf!=1': c('ExitFatal: nested_fatal') != (1 if arm == 'CN' else 0)}
            agg['n'] += 1
            for k, v in f.items():
                agg[k] += int(v)
            members = [k for k in f if k not in ('nf!=1',) and (arm == 'C' or k != 'done_seen')]
            agg['pass'] += int(not any(f[k] for k in members))
        print(d, arm, agg)
