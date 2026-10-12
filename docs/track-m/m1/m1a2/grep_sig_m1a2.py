"""M1a2 (HPP-837, ROADMAP p.756(b)(1)): search our logs for the failure signatures of the A-reserve themes
(signatures.tsv next to this file) - the text search that lets the reopening rule of track F (p.749) find the upstream fix.
Why a separate searcher: for 23 of the 48 FATAL/RT themes the log line that carries the signature does not match KEY of
docs/track-f/f0/sweep_f0.py (sweep_f48a sees only the common title '--- Error ---' / '--- Fatal Error ---'), and 11 rows
print to stderr (_run_stdout.txt), which sweep_f48a does not read (signatures.tsv, columns поток / ключ_свипа).
Needles = every non-'-' signature (print prefix kept) and every companion text of column в_логе. A hit on a line that starts
with 'CsPretranslate: skipped' is counted apart (pretranslation skip, not a fatal of the run).
Usage:
  python grep_sig_m1a2.py selftest            - positive control: a printed line per site (form of our print) is found
                                                 for every theme with a printed signature; negative lines give 0 hits
  python grep_sig_m1a2.py <file|dir> ...      - files log_*.txt, _kyty*.txt, *stdout*.txt (also .xz) under the dirs;
                                                 prints per theme: fatal hits / pretranslate hits / first file:line
Read-only; exit 3 under C:/kyty/SEALED_RUN.lock, exit 4 under C:/kyty/m657/STOP."""
import collections, csv, lzma, os, re, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP present - exit 4'); sys.exit(4)
HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = list(csv.DictReader(open(os.path.join(HERE, 'signatures.tsv'), encoding='utf-8'), delimiter='\t',
                           quoting=csv.QUOTE_NONE))
needles = collections.defaultdict(set)  # needle bytes -> themes
for r in ROWS:
    if r['сигнатура'] != '-':
        needles[r['сигнатура'].encode('utf-8')].add(r['тема'])
    if r['в_логе'] != '-':
        needles[r['в_логе'].split('«')[1].rstrip('»').encode('utf-8')].add(r['тема'])
ALT = re.compile(b'|'.join(re.escape(n) for n in sorted(needles, key=len, reverse=True)))
PRE = b'CsPretranslate: skipped'
NAME = re.compile(r'^(log_.*\.txt|_kyty.*\.txt|.*stdout.*\.txt)(\.xz)?$')


def scan_bytes(data, label, out):
    for m in ALT.finditer(data):
        ls = data.rfind(b'\n', 0, m.start()) + 1
        le = data.find(b'\n', m.end())
        line = data[ls:le if le != -1 else len(data)]
        pre = PRE in line
        # every needle present on this line (a line can carry two)
        for n, themes in needles.items():
            if n in line:
                for t in themes:
                    c = out[t]
                    c['pre' if pre else 'fatal'] += 1
                    if 'first' not in c:
                        c['first'] = '%s:%d' % (label, data.count(b'\n', 0, ls) + 1)


def files_of(args):
    for a in args:
        if os.path.isfile(a):
            yield a
        else:
            for d, _, fs in os.walk(a):
                for f in fs:
                    if NAME.match(f):
                        yield os.path.join(d, f).replace('\\', '/')


def read(p):
    return lzma.open(p).read() if p.endswith('.xz') else open(p, 'rb').read()


def selftest():
    ok = True
    printed = []
    for r in ROWS:
        s = r['сигнатура']
        if s == '-':
            continue
        k = r['печать']
        if k == 'EXIT_IF':
            line = 'Error: ' + (s if s.startswith('condition (') else 'condition (x && ' + s + ' && y) is true')
        elif k == 'EXIT_NOT_IMPLEMENTED':
            line = s if s.startswith('Not implemented (') else 'Not implemented (a ' + s + ' b)'
        elif k == 'Fail':
            line = 'shader resource tracking: hash=0x0123456789abcdef stage=PS pc=0x00000040 GetImageResource dword 3 ' + s \
                if 'runtime value' in s else 'shader resource specialization failed: ' + s
        else:
            line = 'prefix ' + s + ' 0x12'
        printed.append((r['тема'], line))
    data = ('\n'.join(l for _, l in printed) + '\n').encode('utf-8')
    out = collections.defaultdict(collections.Counter)
    scan_bytes(data, 'selftest', out)
    want = {t for t, _ in printed}
    miss = sorted(t for t in want if out[t]['fatal'] == 0)
    print('positive control: themes with printed signature', len(want), 'found', len(want) - len(miss), 'missing', miss)
    ok &= not miss
    pre = ('CsPretranslate: skipped hash=0011 reason=x.cpp:1 shader resource tracking: hash=0x0 stage=CS pc=0x0 '
           'GetImageResource dword 0 is not a valid runtime value\n').encode('utf-8')
    out2 = collections.defaultdict(collections.Counter)
    scan_bytes(pre, 'pre', out2)
    pre_ok = all(c['fatal'] == 0 for c in out2.values()) and sum(c['pre'] for c in out2.values()) > 0
    print('pretranslate line counted apart:', pre_ok)
    ok &= pre_ok
    neg = ('FrameTrace: n=1 dt_us=16667 draws=300\nLevel has started: hoover_beach\nGraphicsRenderDispatchDirect: skipping '
           'zero-sized dispatch groups=0x1x1 mode=0x0000a041\nEvent: quit\n').encode('utf-8')
    out3 = collections.defaultdict(collections.Counter)
    scan_bytes(neg, 'neg', out3)
    print('negative lines hits:', sum(sum(v for k, v in c.items() if k != 'first') for c in out3.values()))
    ok &= not out3
    return ok


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    if sys.argv[1] == 'selftest':
        good = selftest()
        print('ALL OK' if good else 'NOT OK')
        sys.exit(0 if good else 1)
    out = collections.defaultdict(collections.Counter)
    n = 0
    for p in files_of(sys.argv[1:]):
        scan_bytes(read(p), p, out)
        n += 1
    print('files', n)
    for t in sorted(out):
        c = out[t]
        print('%s\tfatal=%d\tpretranslate=%d\tfirst=%s' % (t, c['fatal'], c['pre'], c.get('first', '-')))
    print('themes with fatal hits:', sorted(t for t in out if out[t]['fatal']))
