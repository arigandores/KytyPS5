# FS12a (HPP-750): port of the FS11a helper scripts (docs/track-f/fs11a/) to C:/kyty/f287/fs12a: the leading history
# comment block is kept as is, one history line is put above it; outside that block fs11a -> fs12a, FS11a -> FS12a,
# HPP-714 -> HPP-750; in mk_wt the default base dc5d4712 (FS10) -> ee9632be (FS11a worktree HEAD, item 656(g), 683(g)(1)).
import sys

SRC = 'C:/kyty/KytyPS5/docs/track-f/fs11a/'
DST = 'C:/kyty/f287/fs12a/'
FILES = ['api_chk.sh', 'watch_fs11a.py', 'bstep.sh', 'sstep.sh', 'mk_wt_fs11a.sh', 'build_fs11a.cmd']
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
    out.append(pre + 'FS12a (HPP-750): copy of the FS11a ' + f + ' (fs11a -> fs12a, FS11a -> FS12a, HPP-714 -> HPP-750). Was:')
    out += lines[start:end]
    for l in lines[end:]:
        l = l.replace('fs11a', 'fs12a').replace('FS11a', 'FS12a').replace('HPP-714', 'HPP-750')
        if f.startswith('mk_wt'):
            l = l.replace('C=${2:-dc5d4712}', 'C=${2:-ee9632be}')
        out.append(l)
    t = '\n'.join(out)
    if crlf:
        t = t.replace('\n', '\r\n')
    n = f.replace('fs11a', 'fs12a')
    open(DST + n, 'wb').write(t.encode('utf-8'))
    print(n, 'header lines', end - start, 'crlf' if crlf else 'lf')
