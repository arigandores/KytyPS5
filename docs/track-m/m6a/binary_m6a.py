"""M6a (HPP-848): strings of the M6a test exe against the MS1 copy ea35b679 (port of m2d/binary_m2d.py). Members: the knob
name and every new line format present in M6a and absent in MS1; the MS1 markers (themes, FS15 bases) the same count in
both; the shader source hash of MS1 8dcf3177... in both (signature set untouched); the M6a version string present.
    python binary_m6a.py <M6a exe> <MS1 exe> <M6a version string>   Prints the table and ALL OK / FAIL."""
import hashlib
import sys

m6, ms1, ver = sys.argv[1], sys.argv[2], sys.argv[3]
a, b = open(m6, 'rb').read(), open(ms1, 'rb').read()
print('M6a %s sha256 %s' % (m6, hashlib.sha256(a).hexdigest()))
print('MS1 %s sha256 %s' % (ms1, hashlib.sha256(b).hexdigest()))
NEW = ['KYTY_DIAG_M5W2', 'M5W2: mode=%d', 'M5W2Stat: when=%s', 'M5W2Clr: when=%s', 'GuestPrintf: negative precision',
       'AmprRecordSpace: refused why=%s', 'AmprWriteAddress: refused why=%s', 'AgcReserveDW: cursor state class=%s']
SAME = ['MWave1: mask=', 'MT265: mode=', 'MT272: mode=', 'MT231: mode=', 'KYTY_M_T306', 'FixF20: mode=', 'FixF24: mode=',
        'FixF29: mode=', 'FixF25: mode=', 'FixF21: mode=', 'FixB12: mode=', 'KYTY_S_REPLAY',
        '8dcf31779bbcb7c6e605653a138dae162f645a46']
ok = True
for s in NEW:
    na, nb = a.count(s.encode()), b.count(s.encode())
    good = na >= 1 and nb == 0
    ok &= good
    print('%s %-45s M6a x%d MS1 x%d' % ('OK  ' if good else 'FAIL', s, na, nb))
for s in SAME:
    na, nb = a.count(s.encode()), b.count(s.encode())
    good = na == nb >= 1
    ok &= good
    print('%s %-45s M6a x%d MS1 x%d' % ('OK  ' if good else 'FAIL', s, na, nb))
nv = a.count(ver.encode())
good = nv >= 1
ok &= good
print('%s %-45s M6a x%d' % ('OK  ' if good else 'FAIL', ver, nv))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
