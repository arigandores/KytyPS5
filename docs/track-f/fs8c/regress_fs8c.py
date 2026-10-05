"""Track F link FS8c (HPP-573): regression of fs8c_read.py on the real logs of F14g (f19_v1, f19_w1, f19_ef; binary c01bde0c at
KYTY_FIX_F19=1, installed S12 adb0c82f; F14g section 8.1, item 471 (a)(5)): the reader paths are the F14g files (run dir, log, stdout, json,
video index), the seal and binary of F14g.  Expected: the numbers of the F14g table (hold, frames >= 1 s, video records 10 255 / 20 248,
[Vulkan][E] 0, [Vulkan][W] 925 381, DualSrcBlend before the first GuestOut, every directory line _fixf19); admission NO (binary c01bde0c,
revision 082d161, env KYTY_FIX_F19=1, cold form absent - YES); form NO (installed adb0c82f, not FS6); the word NOT_ADMITTED; the members
FixB4 / FixF8 printed as they are on that binary (data); the Fix members on the real log fs7_h of the FS7 base (FS7c) - YES.  Reads 3 logs of 0.4-0.6 GB (stream).  The first output line names the script and
the target with their sha256; the last line is ALL OK.  ASCII only."""
import hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs8c_read.py')
sys.path.insert(0, HERE)
import fs8c_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite regress_fs8c.py sha256 %s target fs8c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
F = 'C:/kyty/f287/f14g'
ok = True
N = 0


def check(name, cond):
    global ok, N
    N += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    ok &= bool(cond)


def fpaths(old, new):
    d = os.path.join(F, 'runs', old)
    p = dict((n, os.path.join(d, n + '.txt')) for n in ('installed_sha', 'installed_before', 'installed_after', 'cold', 'manifest_cmp',
                                                       'glitch', 'sheet'))
    p.update(log=os.path.join(F, 'log_%s.txt' % old), stdout=os.path.join(F, 'stdout_%s.txt' % old), run=os.path.join(F, '%s.json' % old),
             idx=os.path.join(F, 'rec_%s.mp4.idx' % old), seal=os.path.join(F, 'pred', 'f14g_seal.md'),
             bin='C:/kyty/f287/bin/kyty_emulator_c01bde0c.exe')
    return p


for old, new, video in (('f19_v1', 'fs8_v', 10255), ('f19_w1', 'fs8_w', None), ('f19_ef', 'fs8_ef', 20248)):
    res = R.read(fpaths(old, new), new)
    rows = R.rows(res)
    for x in rows:
        if x.startswith(('  ADMIT', '  FORM', '  MEMBER', '  REPORT', '  READING', '  Fix lines', '  entry line', '  W:', '  video')):
            print('   ' + R.asc(x))
    adm = dict(res['rows']['ADMIT'])
    form = dict(res['rows']['FORM'])
    mem = dict(res['rows']['MEMBER'])
    a = list(adm.values())
    check('%s as %s: word NOT_ADMITTED' % (old, new), res['reading'] == 'NOT_ADMITTED')
    check('%s binary row NO (c01bde0c)' % old, a[0] is False)
    check('%s version row NO (no -1889-g302347b4 in c01bde0c)' % old, a[1] is False)
    check('%s revision row NO (082d161)' % old, a[2] is False and any(t == '082d161' for _, _, t in res['rev']))
    check('%s prereg row YES (F14g seal)' % old, a[3] is True)
    check('%s env row NO (KYTY_FIX_F19=1)' % old, a[4] is False and 'KYTY_FIX_F19' in res['env_info'])
    check('%s cold row YES' % old, a[5] is True)
    check('%s interference row YES' % old, a[6] is True)
    f = list(form.values())
    check('%s form: installed before / after NO (adb0c82f), manifest YES' % old, f[0] is False and f[1] is False and f[2] is True)
    m = list(mem.values())
    check('%s entered, directory _fixf19 every line, hold, lived' % old, m[0] is True and m[1] is True and m[4] is True and m[5] is True)
    check('%s frames >= 1 s after the first scene frame 0 (F14g: 0)' % old, res['k2_after'] == 0)
    if video:
        check('%s video records %d, glitches 0, death 0, sheet' % (old, video), res['idx_records'] == video and res['glitches'] == 0
              and not res['death'] and res['sheet'] is not None)
    else:
        check('%s W: [Vulkan][E] 0, VUID-06479 0, [Vulkan][W] 925 381, DualSrcBlend YES' % old, res['vke'] == 0 and res['vke_06479'] == 0
              and res['vkw'] == 925381 and m[8] is True)
    print('   Fix lines on c01bde0c (data): B4 %s F8 %s B24 %s first GuestOut %s'
          % (res['fixl']['B4'][:2], res['fixl']['F8'][:2], res['fixl']['B24'][:2], res['first_guest']))
# the Fix members on a real log of the FS7 base (fs7_h, binary 8df61c00 at its defaults, FS7c; FixB4 line 15, FixF8 line 11 024, first GuestOut
# line 12 298 - the FS7c read): the member rows of this reader give YES on it
r7 = R.scan('C:/kyty/f287/fs7c/log_fs7_h.txt', R.SKY)
b4 = R.fix_member(r7['fixl']['B4'], r7['first_guest'])
f8 = R.fix_member(r7['fixl']['F8'], r7['first_guest'])
b24 = R.fix_member(r7['fixl']['B24'], r7['first_guest'])
print('   fs7_h Fix lines: B4 %s F8 %s B24 %s first GuestOut %s' % (r7['fixl']['B4'], r7['fixl']['F8'], r7['fixl']['B24'], r7['first_guest']))
check('fs7_h (FS7 base): FixB4 YES, FixF8 YES (letter), FixB24 YES', b4[0] is True and f8[0] is True and b24[0] is True
      and r7['fixl']['B4'] == [(15, '1')] and r7['fixl']['F8'] == [(11024, '1')] and r7['first_guest'] == 12298)
check('fs7_h revision text d6ee2dc (another build for this reader)', [t for _, _, t in r7['rev']] == ['d6ee2dc'])
print('checks %d' % N)
print('ALL OK' if ok else 'SOME FAILED')
