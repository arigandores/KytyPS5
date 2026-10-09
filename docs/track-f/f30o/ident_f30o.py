# F30o (HPP-725): identity of binary T3 - sha256, version strings, marker counts, signature (ROADMAP s122 item 664(e)(3), (4)).
# A copy of docs/track-f/f30k/ident_f30k.py with the paths and markers changed.
# Usage: python ident_f30o.py <main commit> <worktree commit> [--copy]
import hashlib, re, sys, pathlib, shutil

exe = pathlib.Path('C:/kyty/f287/f30o/build/install/kyty_emulator.exe')
data = exe.read_bytes()
sha = hashlib.sha256(data).hexdigest()
out = []
out.append('F30o (HPP-725): binary T3 - worktree C:/kyty/f287/f30o/wt (T2 6fbdcf67 + cherry-pick of main %s = %s)' % (sys.argv[1], sys.argv[2]))
out.append('sha256 %s build/install/kyty_emulator.exe (%d bytes)' % (sha, len(data)))
dst = pathlib.Path('C:/kyty/f287/bin/kyty_emulator_%s.exe' % sha[:8])
if '--copy' in sys.argv:
    if dst.exists():
        raise SystemExit('copy exists: %s' % dst)
    shutil.copyfile(exe, dst)
    if hashlib.sha256(dst.read_bytes()).hexdigest() != sha:
        raise SystemExit('copy sha mismatch')
out.append('copy %s exists=%s' % (dst.as_posix(), dst.exists()))
for m in sorted(set(re.findall(rb'KytyPS5-\d{4}-\d\d-\d\d-[0-9a-f]+-\d+-g[0-9a-f]+', data))):
    out.append('version strings %s' % m.decode())
# names of the FrameTrace-x table are separate C strings: counted with their terminating NUL (rts_bad_r is a prefix of
# rts_bad_rx, rts_bad_s of nothing printed, but counted the same way for uniformity)
NUL = chr(0)
names = ['rts_bad_b', 'rts_bad_rx', 'rts_bad_r', 'rts_bad_xr', 'rts_bad_xc', 'rts_bad_xe', 'rts_bad_s', 'rts_bad_p',
         'rts_bad_m', 'rts_bad_l', 'rts_bad_noreg', 'rts_inj', 'rts_inj_s', 'rts_inj_race', 'rts_inj_nos',
         'rts_inj_none']
for s in ['KYTY_RT_SKIP', 'rtskip'] + [n + NUL for n in names] + ['RtSkipVerify: MISMATCH', 'RtSkip: mode ',
          'KYTY_FIX_B36', 'KYTY_FIX_B13', 'KYTY_FIX_B12', 'KYTY_DIAG_B32', 'KYTY_DIAG_F5', 'KYTY_DIAG_F6', 'LogAsync: mode=',
          '9177b4267de1fb8bac7d1113afd8733210addfac']:
    out.append('count %r %d' % (s.rstrip(NUL) + ('\\0' if s.endswith(NUL) else ''), data.count(s.encode())))
hdr = pathlib.Path('C:/kyty/f287/f30o/build')
for h in hdr.rglob('kytyGitVersion.h'):
    for l in h.read_text().splitlines():
        if l.startswith('#define'):
            out.append('kytyGitVersion.h: %s' % l)
    break
text = '\n'.join(out) + '\n'
pathlib.Path('C:/kyty/f287/f30o/binary_f30o.txt').write_bytes(text.encode())
print(text)
