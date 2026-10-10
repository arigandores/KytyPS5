# FS12b (HPP-751, Red Team, ROADMAP s122 item 683(g)(2)): own reader of my stand run on the FS12 binary 46892c20 without
# KYTY_FIX_F21 (the default). Independent of read_fs12a.py: reads the TSV of the driver (copy of run_stand_fs12a.py) and the
# kept _kyty.txt of every trial. Members (item 675(d)(1) with 680(b), 681(v)(1)), the plan of my comment d100e476:
#   every default trial: cfg_fix == 1, one line 'FixF21: mode=1' in the log, leftover 0;
#   P2 (default, N >= 200): second = crash = hang = cut = expired = 0 in every trial; control count printed (>= 1 required);
#   H  (default, N >= 20):  expired >= 1 in every trial; second = crash = hang = cut = 0;
#   CN (default, N >= 20):  walks 1, nested 0, reenter >= 2, expired 0, expired_seen 0, rc 321, dur_s < 6, hang 0, crash 0,
#                           nested_fatal 1 (the stand's own control);
#   control =0 P2 (N >= 20): cfg_fix == 0, 'FixF21: mode=0' in every log, sum(second) >= 1.
# Usage: python read_fs12b.py <runs dir>  -> prints one line per member and MEMBERS ALL YES / MEMBERS NOT ALL
import csv
import os
import sys

NEED = {'P2': 200, 'H': 20, 'CN': 20}


def rows(path):
    if not os.path.exists(path):
        return []
    return list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'))


def mode_lines(runs, fix, arm, seed):
    p = '%s/fix%s/%s/%s.log' % (runs, fix, arm, seed)
    if not os.path.exists(p):
        return None
    t = open(p, 'rb').read().decode('utf-8', 'replace')
    return [l.strip() for l in t.splitlines() if l.startswith('FixF21: mode=')]


def i(r, k):
    v = r.get(k, '')
    return int(v) if v not in ('', None) else None


def u32(v):
    return None if v is None else v & 0xffffffff


def read(runs):
    res = []

    def mem(name, cond, detail):
        res.append((name, bool(cond), detail))

    for arm, n in NEED.items():
        rs = rows('%s/fixd/stand_%s.tsv' % (runs, arm))
        mem('%s N >= %d' % (arm, n), len(rs) >= n, 'N %d' % len(rs))
        bad_cfg = [r['seed'] for r in rs if r.get('cfg_fix') != '1']
        bad_mode = [r['seed'] for r in rs if mode_lines(runs, 'd', arm, r['seed']) is None or
                    len(mode_lines(runs, 'd', arm, r['seed'])) != 1 or not mode_lines(runs, 'd', arm, r['seed'])[0].startswith('FixF21: mode=1 ')]
        bad_left = [r['seed'] for r in rs if r.get('leftover') != '0']
        mem('%s cfg_fix=1 and one FixF21: mode=1 line, leftover 0, in every trial' % arm, rs and not bad_cfg and not bad_mode and not bad_left,
            'bad cfg %s mode %s leftover %s' % (bad_cfg[:5], bad_mode[:5], bad_left[:5]))
        if arm == 'P2':
            bad = [r['seed'] for r in rs if any(i(r, k) != 0 for k in ('second', 'crash', 'hang', 'cut', 'expired'))]
            ctl = sum(i(r, 'control') or 0 for r in rs)
            codes = sorted(set(str(u32(i(r, 'rc'))) for r in rs))
            mem('P2 second=crash=hang=cut=expired=0 in every trial; control >= 1', rs and not bad and ctl >= 1,
                'bad %s control %d codes %s' % (bad[:5], ctl, codes))
        if arm == 'H':
            bad = [r['seed'] for r in rs if (i(r, 'expired') or 0) < 1 or any(i(r, k) != 0 for k in ('second', 'crash', 'hang', 'cut'))]
            codes = {}
            for r in rs:
                codes[str(u32(i(r, 'rc')))] = codes.get(str(u32(i(r, 'rc'))), 0) + 1
            mem('H expired>=1, second=crash=hang=cut=0 in every trial', rs and not bad,
                'bad %s codes %s control %d' % (bad[:5], codes, sum(i(r, 'control') or 0 for r in rs)))
        if arm == 'CN':
            def ok_cn(r):
                return (i(r, 'walks') == 1 and i(r, 'nested') == 0 and (i(r, 'reenter') or 0) >= 2 and i(r, 'expired') == 0 and
                        i(r, 'expired_seen') == 0 and u32(i(r, 'rc')) == 321 and float(r['dur_s']) < 6.0 and i(r, 'hang') == 0 and
                        i(r, 'crash') == 0 and i(r, 'nested_fatal') == 1)
            bad = [r['seed'] for r in rs if not ok_cn(r)]
            durs = [float(r['dur_s']) for r in rs]
            mem('CN walks 1, nested 0, reenter>=2, expired 0, expired_seen 0, rc 321, dur<6 s, hang 0, crash 0, nested_fatal 1',
                rs and not bad, 'bad %s dur %s-%s reenter min %s' % (bad[:5], min(durs) if durs else '-', max(durs) if durs else '-',
                                                                     min((i(r, 'reenter') for r in rs), default='-')))
    rs = rows('%s/fix0/stand_P2.tsv' % runs)
    bad_cfg = [r['seed'] for r in rs if r.get('cfg_fix') != '0']
    bad_mode = [r['seed'] for r in rs if not (mode_lines(runs, '0', 'P2', r['seed']) or [''])[0].startswith('FixF21: mode=0 ')]
    sec = sum(i(r, 'second') or 0 for r in rs)
    mem('control =0 P2: N >= 20, cfg_fix=0 and mode=0 in every trial, second >= 1', len(rs) >= 20 and not bad_cfg and not bad_mode and sec >= 1,
        'N %d second %d bad cfg %s mode %s' % (len(rs), sec, bad_cfg[:5], bad_mode[:5]))
    return res


def main():
    res = read(sys.argv[1])
    for name, good, detail in res:
        print(('YES ' if good else 'NO  ') + name + ' - ' + detail)
    allok = all(g for _, g, _ in res)
    print('MEMBERS ALL YES' if allok else 'MEMBERS NOT ALL')
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
