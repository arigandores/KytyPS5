# FS7a (HPP-565): port of the FS6a step scripts (build_fs6a.cmd, bstep.sh, api_chk.sh, watch_fs6a.py) to fs7a - paths and
# names fs6a -> fs7a, FS6a -> FS7a, one "Was:" header line added. LF output (write_bytes).
import sys
SRC = 'C:/kyty/f287/fs6a/'
DST = 'C:/kyty/f287/fs7a/'
NL = chr(10)
for name, new, head in (
        ('build_fs6a.cmd', 'build_fs7a.cmd', 'rem FS7a (HPP-565, ROADMAP s122 items 467(g)(1), 487(g)(1)): copy of build_fs6a.cmd with SRC/BUILD set to fs7a. Was:'),
        ('bstep.sh', 'bstep.sh', '# FS7a (HPP-565): copy of the FS6a bstep.sh, paths changed. Was:'),
        ('api_chk.sh', 'api_chk.sh', '# FS7a (HPP-565): copy of the FS6a api_chk.sh, names changed. Was:'),
        ('watch_fs6a.py', 'watch_fs7a.py', '# FS7a (HPP-565): copy of watch_fs6a.py, times lines say FS7a. Was:')):
    t = open(SRC + name, 'rb').read().decode('utf-8').replace('\r\n', NL)
    lines = t.split(NL)
    body = NL.join(lines[1:] if lines[0].startswith('#!') or lines[0] == '@echo off' else lines)
    body = body.replace('fs6a', 'fs7a').replace('FS6a', 'FS7a').replace('HPP-555', 'HPP-565')
    first = lines[0] if (lines[0].startswith('#!') or lines[0] == '@echo off') else None
    out = ([first] if first else []) + [head] + body.split(NL)
    open(DST + new, 'wb').write(NL.join(out).encode('utf-8'))
    print('ported', name, '->', new)
