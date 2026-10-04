# F15d (HPP-515): kernel_file_system_tests of the own clean build (fix/) and of the F15c base build (C:/kyty/f287/f15c/base/)
# at KYTY_FIX_B4 unset / 0 / 1, --filesystem-only and full; every KYTY_* removed from the environment first.
import os, subprocess, re, hashlib
exes = {'own_fix': 'C:/kyty/f287/f15d/fix/kernel_file_system_tests.exe', 'base_4d9e8ab7': 'C:/kyty/f287/f15c/base/kernel_file_system_tests.exe'}
os.makedirs('C:/kyty/f287/f15d/kfs_cwd', exist_ok=True)
for name, exe in exes.items():
    print(name, hashlib.sha256(open(exe, 'rb').read()).hexdigest()[:8])
    for fix in ('none', '0', '1'):
        for args in (['--filesystem-only'], []):
            env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
            if fix != 'none':
                env['KYTY_FIX_B4'] = fix
            p = subprocess.run([exe] + args, cwd='C:/kyty/f287/f15d/kfs_cwd', env=env, capture_output=True, timeout=300)
            out = (p.stdout + p.stderr).decode('utf-8', 'replace')
            failed = [l for l in out.splitlines() if 'failed' in l.lower()]
            tail = [l for l in out.splitlines() if l.strip()][-1:] 
            print('  fix=%s %-18s rc=%s failed-lines=%d last=%r' % (fix, ' '.join(args) or '(full)', p.returncode, len(failed), tail[0][:100] if tail else ''))
            for l in failed[:3]:
                print('     ', l[:140])
