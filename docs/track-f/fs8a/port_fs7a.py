# FS8a (HPP-571, ROADMAP s122 items 471(g)(1), 522(d)): port of the FS7a helper scripts to FS8a - paths fs7a -> fs8a,
# names FS7a -> FS8a, HPP-565 -> HPP-571; mk_wt: base FS7a worktree d6ee2dc8 + cherry-pick 082d1612 (F14e), f98e842c (F14e2)
# and the FS8a main commit. A header line names the source. LF output (write_bytes). Prints PORT OK.
import os, sys

S = 'C:/kyty/f287/fs7a'
D = 'C:/kyty/f287/fs8a'
NL = chr(10)


def port(name, new_name, extra=()):
    text = open(os.path.join(S, name), 'rb').read().decode('utf-8').replace(chr(13), '')
    for a, b in extra:
        if a not in text:
            print('EXTRA ANCHOR FAIL', name, repr(a))
            sys.exit(2)
        text = text.replace(a, b)
    text = text.replace('fs7a', 'fs8a').replace('FS7a', 'FS8a').replace('HPP-565', 'HPP-571')
    lines = text.split(NL)
    head = 'FS8a (HPP-571): copy of the FS7a ' + name + ', paths and names changed. Was:'
    if name.endswith('.cmd'):
        hdr = 'rem ' + head
        lines.insert(1, hdr)
    else:
        hdr = '# ' + head
        if lines[0].startswith('#!'):
            lines.insert(1, hdr)
        else:
            lines.insert(0, hdr)
    open(os.path.join(D, new_name), 'wb').write(NL.join(lines).encode('utf-8'))
    print('ported', name, '->', new_name)


port('watch_fs7a.py', 'watch_fs8a.py')
port('api_chk.sh', 'api_chk.sh')
port('bstep.sh', 'bstep.sh')
port('sstep.sh', 'sstep.sh')
port('build_fs7a.cmd', 'build_fs8a.cmd')
port('mk_wt_fs7a.sh', 'mk_wt_fs8a.sh', extra=[
    ('C=3904522d', 'C=d6ee2dc8'),
    ('for P in 10a4800b 9c726d74 919c1a19 $FS7A; do', 'for P in 082d1612 f98e842c $FS7A; do'),
    ('"$G" -C $WT log -6', '"$G" -C $WT log -5'),
])
print('PORT OK')
