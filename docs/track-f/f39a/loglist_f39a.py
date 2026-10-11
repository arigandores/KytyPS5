# F39a (HPP-767): list of emulator logs for the witness inventory of F24 (ROADMAP s122 item 691(zh)(3)).
# Walks C:/kyty (without games/, .git, the KytyPS5 repo except its "ps5 em" folder, _cleanup401), takes files whose name
# is an emulator log (log_*.txt, log.txt, _kyty*.txt, *_kyty.txt, abort_*.txt, and the same with .xz) and mtime >= the
# given UTC date. Writes: path, size, mtime (UTC ISO). Usage: python loglist_f39a.py <YYYY-MM-DD> <out.tsv>
import os, sys, fnmatch, datetime

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
ROOT = 'C:/kyty'
PAT = ['log_*.txt', 'log.txt', '_kyty*.txt', '*_kyty.txt', 'abort_*.txt']
SKIP_DIRS = {'games', '.git', '_cleanup401', '__pycache__', 'node_modules'}


def is_log(name):
    base = name[:-3] if name.endswith('.xz') else name
    return any(fnmatch.fnmatch(base, p) for p in PAT)


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        sys.exit(3)
    since = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp()
    out = sys.argv[2]
    rows = []
    for dp, dns, fns in os.walk(ROOT):
        norm = dp.replace(chr(92), '/')
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not (norm == 'C:/kyty/KytyPS5' and d != 'ps5 em')
                  and not (norm.startswith('C:/kyty/KytyPS5/ps5 em') and d == 'games')]
        for fn in fns:
            if not is_log(fn):
                continue
            p = norm + '/' + fn
            try:
                st = os.stat(p)
            except OSError:
                continue
            if st.st_mtime < since:
                continue
            rows.append((p, st.st_size, datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')))
    rows.sort()
    with open(out, 'w', encoding='utf-8', newline=chr(10)) as o:
        for r in rows:
            o.write('%s\t%d\t%s\n' % r)
    print('files', len(rows), 'bytes', sum(r[1] for r in rows), 'xz', sum(1 for r in rows if r[0].endswith('.xz')))


if __name__ == '__main__':
    main()
