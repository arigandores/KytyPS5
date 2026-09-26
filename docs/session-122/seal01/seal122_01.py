"""Session 122 seal 01 (map122): writes SEALS122.txt - sha256 of every sealed file (the idiom of seal121_01.py)."""
import hashlib
from pathlib import Path

R = Path('C:/kyty/s122')
FILES = ['pred/01_map122.md', 'design/design122.md', 'design/burn.md', 'map122_format_contract.md', 'map122.py',
         'test_map122.py', 'mut_map122.py', 'gates_base.txt', 'go122a.sh', 'enter_scene.py', 'procload.py',
         'hostdev122.py', 'test_hostdev122.py', 'chk_map122.py', 'mk_checks122.py', 'checks/map122_checks.json',
         'mut_map122.sealed.txt', 'kyty_emulator_2baf8742.exe', 'C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py']
NL = chr(10)
lines = ['# Session 122 seal 01 (map122) - sha256 of every sealed file; written by patches/seal122_01.py', '']
for f in FILES:
    p = Path(f) if ':' in f else R / f
    if not p.is_file():
        raise SystemExit('missing %s' % p)
    lines.append('%s  %s' % (hashlib.sha256(p.read_bytes()).hexdigest(), f))
lines += ['',
          'map122: mutlib 4.1 FULL --control --no-memo --work-dir C:/kyty/s122/mutwork --cache-dir C:/kyty/s122/mutcache '
          '(no --changed-from) on the sealed copy: 294 mutants, 294 killed (14 by a suite crash), 0 survived, '
          '0 unresolved; controls 3 of 3 survived; report mut_map122.sealed.txt, log mut_run_sealed.log',
          'fixtures on the sealed copy: test_map122.py 194 fixtures ALL OK (196 with --real: log_bsky122.txt, '
          'C:/kyty/s121/log_shp121.txt)',
          'decided before the seal by the UNSEALED smoke csky122 (ROADMAP s122 item 13 (a)/(b)): code 7 armed, '
          'burn_s_main = 0 in every block => the skym122 arm left the map; codes 5 and 6 armed cleanly',
          'item 18 (c) in the scorer: HEADROOM by the base-arm window share of dt_us < 25 000 >= 0.95 (no base arm => '
          'NOT_EVALUABLE)',
          'sealed tags: sky122, skyp122, des122, atl122, ght122, dnn122 (+ mgg122 hub122 hov122 ice122), each with <tag>r',
          '']
out = R / 'SEALS122.txt'
if out.exists():
    raise SystemExit('SEALS122.txt exists - a seal is never rewritten; append a new seal by hand-reviewed script')
out.write_bytes(NL.join(lines).encode('utf-8'))
print(NL.join(lines))
