"""ident_s15.py - S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)(i)): the identities T-1, T-2, T-6 of the S13b logs by the
code of sc_s15.py (ident_lo, ident_rows: by the row that counts a line) beside the rows of item 404 (sc_s9.ident_domain, by frame=)
and the whole log - data, no game.  One line per log with its sha256; the last line "IDENT: <n> of <m> logs equal on T-1, T-2,
T-6 by the row".  Streaming, binary.  ASCII.
    python ident_s15.py <out> <tag> [<tag> ...]
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('sc15_ident', 'C:/kyty/s288/s15/sc_s15.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
A, S9 = S.A, S.S9
LOGS = 'C:/kyty/s288/s13'


def main():
    out = sys.argv[1]
    lines = []
    good = 0
    tags = sys.argv[2:]
    for t in tags:
        lp = '%s/log_%s.txt' % (LOGS, t)
        s = A.scan_s(lp)
        sy = S.scan_y(lp)
        std = A.scan_stdout('%s/stdout_%s.txt' % (LOGS, t))
        eg, end, fi = A.locate(s, S.SPEC[t]['level'])
        ident = [x for x in A.identities(s, std, S.SPEC[t]['cls']) if not x[0].startswith('T-4')]
        ident = S9.ident_domain(ident, s, fi)
        lo = S.ident_lo(s, fi, eg)
        rows = S.ident_rows(ident, s, sy, lo)
        new = [(n.split(' ')[0], ok, d) for n, ok, d in rows if n.startswith(('T-1 sum', 'T-2 min', 'T-6 distinct'))]
        old = [d for n, ok, d in rows if n.startswith('T-1 / T-2 / T-6 by frame=')]
        eq = all(ok is True for _, ok, _ in new)
        good += eq
        lines.append('%s %-30s log sha256 %s; fi %s eg %s lo %d; by the row: %s; item 404 / whole log (data): %s; %s' % (
            t, S.SPEC[t]['level'], s['sha256'], fi, eg, lo, '; '.join('%s %s (%s)' % (n, 'ok' if ok else ok, d) for n, ok, d in new),
            old[0] if old else '-', 'EQUAL' if eq else 'NOT EQUAL'))
    lines.append('IDENT: %d of %d logs equal on T-1, T-2, T-6 by the row' % (good, len(tags)))
    txt = '\n'.join(lines) + '\n'
    txt.encode('ascii')
    open(out, 'w', encoding='ascii', newline='\n').write(txt)
    print(txt)
    return 0 if good == len(tags) else 1


if __name__ == '__main__':
    sys.exit(main())
