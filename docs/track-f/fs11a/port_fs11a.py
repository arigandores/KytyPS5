# FS11a (HPP-714): port of the FS10a helper scripts (docs/track-f/fs10a/) to C:/kyty/f287/fs11a: the leading history
# comment block is kept as is, one history line is put above it; outside that block fs10a -> fs11a, FS10a -> FS11a,
# HPP-684 -> HPP-714; in mk_wt the default base 11164d72 (FS9) -> dc5d4712 (FS10a worktree HEAD, item 627(g)).
import sys

SRC = 'C:/kyty/KytyPS5/docs/track-f/fs10a/'
DST = 'C:/kyty/f287/fs11a/'
FILES = ['api_chk.sh', 'watch_fs10a.py', 'bstep.sh', 'sstep.sh', 'mk_wt_fs10a.sh', 'build_fs10a.cmd']
for f in FILES:
    raw = open(SRC + f, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
    pre = 'rem ' if f.endswith('.cmd') else '# '
    start = 1 if lines[0].startswith('#!') or lines[0].startswith('@echo') else 0
    end = start
    while end < len(lines) and (lines[end].startswith(pre) or (pre == 'rem ' and lines[end] == 'rem')):
        end += 1
    out = lines[:start]
    out.append(pre + 'FS11a (HPP-714): copy of the FS10a ' + f + ' (fs10a -> fs11a, FS10a -> FS11a, HPP-684 -> HPP-714). Was:')
    out += lines[start:end]
    for l in lines[end:]:
        l = l.replace('fs10a', 'fs11a').replace('FS10a', 'FS11a').replace('HPP-684', 'HPP-714')
        if f.startswith('mk_wt'):
            l = l.replace('C=${2:-11164d72}', 'C=${2:-dc5d4712}')
        out.append(l)
    t = '\n'.join(out)
    if crlf:
        t = t.replace('\n', '\r\n')
    n = f.replace('fs10a', 'fs11a')
    open(DST + n, 'wb').write(t.encode('utf-8'))
    print(n, 'header lines', end - start, 'crlf' if crlf else 'lf')
