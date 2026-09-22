"""Session 102: copy the small result files into git (docs/session-102/results) and hash the large local ones."""
import glob
import hashlib
import json
import os
import shutil

os.chdir('C:/kyty/s102')
dst = 'C:/kyty/KytyPS5/docs/session-102/results'
os.makedirs(dst, exist_ok=True)
files = [f.replace(os.sep, '/') for f in glob.glob('runs102/*.json') if 'manifest' not in f]
files += ['m5/real/m5_102_result.json', 'm5/real/m5_102_result.stdout.txt', 'm5/real/equal_m5cap102.json',
          'm5/real/plan_m5cap102.json', 'm5/regs.json', 'm5/v2s_table.md', 'm5/layout_check.json',
          'accept_ckpt102_entry1.txt', 'accept_dab102a.txt', 'SEALS102.txt', 'README.md', 'M5_RUNBOOK.md']
man = {}
for f in files:
    if not os.path.exists(f):
        print('missing', f)
        continue
    size = os.path.getsize(f)
    if size > 1_500_000:
        print('skip big', f, size)
        continue
    shutil.copy2(f, os.path.join(dst, f.replace('/', '__')))
    man[f] = {'bytes': size, 'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest()}
big = ['m5/real/bench_m5cap102.json', 'm5/real/find_m5cap102.json', 'log_ckpt102.txt', 'log_ckpt102_entry1.txt',
       'log_dab102a.txt', 'log_m5cap102.txt', 'log_m5cap102b.txt',
       'C:/Users/<user>/OneDrive/Desktop/ps5 em/_RenderDoc/kyty_1790110985179586_capture.rdc']
for f in big:
    if os.path.exists(f):
        h = hashlib.sha256()
        with open(f, 'rb') as fh:
            for chunk in iter(lambda: fh.read(1 << 24), b''):
                h.update(chunk)
        man['LOCAL:' + f] = {'bytes': os.path.getsize(f), 'sha256': h.hexdigest()}
for path in (os.path.join(dst, 'manifest102.json'), 'runs102/manifest102.json'):
    with open(path, 'w') as fh:
        json.dump(man, fh, indent=1)
print(len(man))
for k in man:
    print(k, man[k]['bytes'])
