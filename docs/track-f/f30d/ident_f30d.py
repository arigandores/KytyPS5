# F30d (HPP-709): identity of binary T - sha256, version strings, marker counts, signature (ROADMAP s122 item 643(v)(3)-(4)).
import hashlib, re, sys, pathlib, shutil

exe = pathlib.Path('C:/kyty/f287/f30d/build/install/kyty_emulator.exe')
data = exe.read_bytes()
sha = hashlib.sha256(data).hexdigest()
out = []
out.append('F30d (HPP-709): binary T - worktree C:/kyty/f287/f30d/wt (FS10a dc5d4712 + cherry-pick of main 585d997d = a1d1d863)')
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
for s in ['KYTY_RT_SKIP', 'rtskip', 'rts_bad_b', 'rts_bad_rx', 'rts_bad_noreg', 'RtSkipVerify: MISMATCH', 'RtSkip: mode ',
          'KYTY_FIX_B36', 'KYTY_FIX_B13', 'KYTY_FIX_B12', 'KYTY_DIAG_B32', 'KYTY_DIAG_F5', 'KYTY_DIAG_F6', 'LogAsync: mode=',
          '9177b4267de1fb8bac7d1113afd8733210addfac']:
    out.append('count %r %d' % (s, data.count(s.encode())))
hdr = pathlib.Path('C:/kyty/f287/f30d/build')
for h in hdr.rglob('kytyGitVersion.h'):
    for l in h.read_text().splitlines():
        if l.startswith('#define'):
            out.append('kytyGitVersion.h: %s' % l)
    break
text = '\n'.join(out) + '\n'
pathlib.Path('C:/kyty/f287/f30d/binary_f30d.txt').write_bytes(text.encode())
print(text)
