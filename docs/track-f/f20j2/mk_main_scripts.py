# F20j2 (HPP-633): copies of the F20j main-tree scripts (mk_wtm, build_f20jm.cmd, bstepm.sh) for main 18dd03a6.
s = 'C:/kyty/f287/f20j/'
d = 'C:/kyty/f287/f20j2/'
BS = chr(92)
for a, b in [('mk_wtm_f20j.sh', 'mk_wtm_f20j2.sh'), ('build_f20jm.cmd', 'build_f20j2m.cmd'), ('bstepm.sh', 'bstepm.sh')]:
    t = open(s + a, 'rb').read().decode().replace('\r\n', '\n')
    t = t.replace('f20j' + BS, 'f20j2' + BS).replace('f20j' + BS + BS, 'f20j2' + BS + BS)
    t = t.replace('f20j/', 'f20j2/').replace('build_f20jm', 'build_f20j2m').replace('watch_f20j.py', 'watch_f20j2.py')
    t = t.replace('C=9bd96f44', 'C=18dd03a6').replace('api_chk.sh', 'api_chk.sh')
    lines = t.split('\n')
    hdr = ('rem ' if b.endswith('.cmd') else '# ') + 'F20j2 (HPP-633, ROADMAP s122 item 552(d)): copy of the F20j ' + a + \
        ' for main 18dd03a6 (compile check of the cherry-pick of 61b410bf).'
    lines.insert(1, hdr)
    t = '\n'.join(lines)
    open(d + b, 'wb').write((t.replace('\n', '\r\n') if b.endswith('.cmd') else t).encode())
print('ok')
