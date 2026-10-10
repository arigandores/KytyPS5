# F32a (HPP-733): map of the course-line binaries (pinned copies) to the build hash printed in the log line
# 'version: Fork build <owner>/<repo> <hash>'. The hash is read from the executable bytes (git describe string);
# sha256 of every pinned copy is printed with it. Usage: python binmap_f32a.py <out.tsv>
import os, re, sys, hashlib

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
# installed order (CLAUDE.md state line): name, pinned copy
COURSE = [
    ('9235a7ac', 'C:/kyty/s128/kyty_emulator_9235a7ac.exe'),
    ('dac02fb9', 'C:/kyty/s146/kyty_emulator_dac02fb9.exe'),
    ('FS2 bbad499c', 'C:/kyty/f287/bin/kyty_emulator_bbad499c.exe'),
    ('P23 4aa62e95', 'C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe'),
    ('FS3 540c035a', 'C:/kyty/f287/bin/kyty_emulator_540c035a.exe'),
    ('FS4 31cbfee8', 'C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe'),
    ('FS5 631ff987', 'C:/kyty/f287/bin/kyty_emulator_631ff987.exe'),
    ('S12 adb0c82f', 'C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe'),
    ('FS6 9325446c', 'C:/kyty/f287/bin/kyty_emulator_9325446c.exe'),
    ('FS7 8df61c00', 'C:/kyty/f287/bin/kyty_emulator_8df61c00.exe'),
    ('FS8 2c9b69b9', 'C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe'),
    ('S18 b3cee576', 'C:/kyty/s288/bin/kyty_emulator_b3cee576.exe'),
    ('FS9 3861eeea', 'C:/kyty/f287/bin/kyty_emulator_3861eeea.exe'),
    ('FS10 abfded5e', 'C:/kyty/f287/bin/kyty_emulator_abfded5e.exe'),
    ('FS11 ea51ae80', 'C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe'),
]
# the TITLE string that the log prints as 'version: Fork build <owner>/<repo> <hash>' (owner not kept)
RX = [re.compile(rb'Fork build \S+ ([0-9a-f]{7,12})\x00')]


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        sys.exit(3)
    out = sys.argv[1]
    rows = []
    for name, p in COURSE:
        if not os.path.exists(p):
            rows.append((name, p, 'MISSING', '-', '-'))
            continue
        b = open(p, 'rb').read()
        sha = hashlib.sha256(b).hexdigest()
        found = []
        for rx in RX:
            for m in rx.finditer(b):
                h = m.group(1).decode()[:7]
                if h not in found:
                    found.append(h)
        rows.append((name, p, sha[:8], ','.join(found) or '?', 'OK' if sha[:8] == name.split()[-1] else 'SHA_NAME_DIFF'))
    with open(out, 'w', encoding='utf-8', newline=chr(10)) as o:
        for r in rows:
            o.write(chr(9).join(r) + chr(10))
            print(*r)


if __name__ == '__main__':
    main()
