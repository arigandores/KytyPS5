"""FS13b (HPP-788, Red Team; copy of sanitize_fs13a.py with fs13a -> fs13b and the temp prefix paperclip-[a-z0-9-]+): replace the runner temp directory and the home prefix (they carry the user name) in the docs copies
docs/track-f/fs13b/** by <TEMP> / <HOME>/ before the commit; the local originals in C:/kyty/f287/fs13b are not changed.
Usage: python sanitize_fs13b.py <dir>"""
import os
import re
import sys

SEP = rb'[/\\]'
TEMP = re.compile(rb'C:' + SEP + rb'Users' + SEP + rb'[^/\\]+' + SEP + rb'AppData' + SEP + rb'Local' + SEP + rb'Temp' + SEP +
                  rb'paperclip-[A-Za-z0-9-]+', re.I)
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
