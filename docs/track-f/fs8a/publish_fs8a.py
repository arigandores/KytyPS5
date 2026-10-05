"""FS8a (HPP-571): copies the link files to docs/track-f/fs8a/ (LF for text), masks the agent address
(rule 28), writes SHA256SUMS_fs8a.txt of the local originals and the binaries. Prints PUBLISH OK."""
import hashlib
import os
import shutil
import sys

SRC = 'C:/kyty/f287/fs8a'
DST = 'C:/kyty/KytyPS5/docs/track-f/fs8a'
REPORT_DST = 'C:/kyty/KytyPS5/docs/track-f/fs8a.md'
MASK = (b'<agent-address>', b'<agent-email>')  # address masked in the copy (rule 28)
FILES = ['api_chk.sh', 'bstep.sh', 'sstep.sh', 'watch_fs8a.py', 'build_fs8a.cmd', 'port_fs7a.py', 'patch_fs8a.py',
         'patch_fs8a_tests.py', 'mk_wt_fs8a.sh', 'cp523.sh', 'cp523b.sh', 'gpu_fs8a.sh', 'suite_fs8a.py', 'knobs_fs8a.py',
         'verify_fs8a.py', 'mk_wt.log', 'conflict_082d1612.diff', 'cp523.log', 'cp523b.log', 'patch_main.out.txt',
         'patch_tests_main.out.txt', 'patch_tests_wt.out.txt', 'gate_order_main.out.txt', 'gate_order_wt.out.txt',
         'gate_order_wt2.out.txt', 'eprime.out.txt', 'gpu_fs8a_r1.out.txt', 'gpu_fs8a.out.txt', 'knobs_fs8a.out.txt',
         'verify_fs8a.out.txt', 'diffstat_vs_d6ee2dc8.txt', 'fs8a_vs_d6ee2dc8.diff', 'kytyGitVersion_fs8.h',
         'commit_msg_code.txt', 'commit_msg_tests.txt']
EXTRA = [('runs/log_suite_r1.txt', 'log_suite_r1.txt'), ('runs/log_suite.txt', 'log_suite.txt')] + \
        [('gpu/%s/run.log' % n, 'gpu/%s/run.log' % n) for n in ('gu', 'g1', 'g0', 'c1', 'c0')]
BINS = ['C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe', 'C:/kyty/f287/bin/kyty_emulator_aed92dc1.exe',
        SRC + '/build/install/kyty_emulator.exe', SRC + '/build/shader_cfg_tests.exe',
        SRC + '/build/shader_recompiler_compute_tests.exe']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


os.makedirs(DST, exist_ok=True)
sums = []
for src_rel, dst_rel in [(f, f) for f in FILES] + EXTRA + [('fs8a.md', None)]:
    sp = SRC + '/' + src_rel
    data = open(sp, 'rb').read()
    sums.append('%s  %s' % (sha(sp), src_rel))
    data = data.replace(b'\r\n', b'\n').replace(MASK[0], MASK[1])
    dp = REPORT_DST if dst_rel is None else DST + '/' + dst_rel
    os.makedirs(os.path.dirname(dp), exist_ok=True)
    open(dp, 'wb').write(data)
for b in BINS:
    sums.append('%s  %s' % (sha(b), b))
open(DST + '/SHA256SUMS_fs8a.txt', 'wb').write(('\n'.join(sums) + '\n').encode())
left = [f for f in os.listdir(DST) if os.path.isfile(DST + '/' + f) and MASK[0] in open(DST + '/' + f, 'rb').read()]
print('files', len(FILES) + len(EXTRA) + 1, 'address left in', left)
print('PUBLISH OK' if not left else 'FAILED')
sys.exit(0 if not left else 1)
