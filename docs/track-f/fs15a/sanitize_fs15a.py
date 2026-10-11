"""FS15a (HPP-820; copy of the FS13a sanitize_fs15a.py): replace the runner temp directory and the home prefix (they carry the user name) in the docs copies
docs/track-f/fs15a/** by <TEMP> / <HOME>/ before the commit; the local originals in C:/kyty/f287/fs15a are not changed.
Usage: python sanitize_fs15a.py <dir>"""
import os
import re
import sys

SEP = rb'[/\\]'
TEMP = re.compile(rb'C:' + SEP + rb'Users' + SEP + rb'[^/\\]+' + SEP + rb'AppData' + SEP + rb'Local' + SEP + rb'Temp' + SEP +
                  rb'paperclip-run-hpp-820-[A-Za-z0-9-]+', re.I)
HOME = re.compile(rb'C:' + SEP + rb'Users' + SEP + rb'[^/\\<>"\s]+' + SEP, re.I)
n = 0
for d, _, fs in os.walk(sys.argv[1]):
    for f in fs:
        p = os.path.join(d, f)
        b = open(p, 'rb').read()
        nb = HOME.sub(b'<HOME>/', TEMP.sub(b'<TEMP>', b))
        if nb != b:
            open(p, 'wb').write(nb)
            n += 1
            print('sanitized', p)
print('files', n)
