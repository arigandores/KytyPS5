# FS10a (HPP-684): fix the first history line of the scripts copied from fs9a by sed (fs9a -> fs10a): the line that said
# "FS9a (HPP-671): ..." keeps that text after "FS10a (HPP-684): copy of the FS9a <file> (fs9a -> fs10a). Was:".
import sys

d = 'C:/kyty/f287/fs10a/'
import sys as _s
ALL = [('api_chk.sh', 'api_chk.sh'), ('watch_fs10a.py', 'watch_fs9a.py'), ('bstep.sh', 'bstep.sh'),
       ('sstep.sh', 'sstep.sh'), ('mk_wt_fs10a.sh', 'mk_wt_fs9a.sh'), ('build_fs10a.cmd', 'build_fs9a.cmd')]
# run 1 handled the first four (then stopped at mk_wt: its line says "FS9a (HPP-671, ROADMAP ..."); run 2: the rest
for new, old in [x for x in ALL if x[0] in _s.argv[1:]]:
    raw = open(d + new, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
    hits = [i for i, l in enumerate(lines) if 'FS10a (HPP-684' in l]
    assert hits, new
    i = hits[0]
    l = lines[i]
    pre = 'rem ' if l.startswith('rem ') else '# '
    body = l[len(pre):].replace('FS10a (HPP-684', 'FS9a (HPP-671', 1).replace('fs10a', 'fs9a')
    lines[i] = pre + 'FS10a (HPP-684): copy of the FS9a ' + old + ' (fs9a -> fs10a, FS9a -> FS10a, HPP-671 -> HPP-684). Was:'
    lines.insert(i + 1, pre + body)
    t = '\n'.join(lines)
    if crlf:
        t = t.replace('\n', '\r\n')
    open(d + new, 'wb').write(t.encode('utf-8'))
    print(new, i)
