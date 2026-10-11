# F40a2 (HPP-785): copies the F40a build tools into C:/kyty/f287/f40a2 - executable lines f40a -> f40a2, F40a -> F40a2,
# HPP-770 -> HPP-785; comment lines kept; one header line "F40a2 (HPP-785): copy of the F40a <name>. Was:" on top.
import os
import re

SRC = 'C:/kyty/f287/f40a'
DST = 'C:/kyty/f287/f40a2'
NAMES = ['mk_wt_f40a.sh', 'build_f40a.cmd', 'bstep.sh', 'api_chk.sh', 'watch_f40a.py', 'run_tests_f40a.py',
         'binary_f40a.py']


def conv(line):
    s = line.lstrip()
    if s.startswith('#') or s.lower().startswith('rem ') or s.startswith('@echo'):
        return line
    line = re.sub(r'f40a(?!2)', 'f40a2', line)
    line = re.sub(r'F40a(?!2)', 'F40a2', line)
    return line.replace('HPP-770', 'HPP-785')


for name in NAMES:
    text = open(os.path.join(SRC, name), 'rb').read().decode('utf-8').replace('\r\n', '\n')
    lines = text.split('\n')
    out = [conv(l) for l in lines]
    if name.endswith('.cmd'):
        hdr = 'rem F40a2 (HPP-785): copy of the F40a %s, executable lines f40a -> f40a2 (paths, names). Was:' % name
        i = 1 if out and out[0].startswith('@echo') else 0
    else:
        hdr = '# F40a2 (HPP-785): copy of the F40a %s, executable lines f40a -> f40a2 (paths, names). Was:' % name
        i = 1 if out and out[0].startswith('#!') else 0
    out.insert(i, hdr)
    dname = name.replace('f40a', 'f40a2')
    data = '\n'.join(out)
    if name.endswith('.cmd'):
        data = data.replace('\n', '\r\n')
    open(os.path.join(DST, dname), 'wb').write(data.encode('utf-8'))
    print('wrote', dname, len(out))
