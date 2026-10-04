# F22a fixture for sweep_f22a.py: a synthetic log with every marker and edge, swept with a 4096-byte block, with the
# default block and as '.xz'; the three records must be equal member by member and equal to the expected values.
# Edges: direct read failed before and after a level line, followed by a KernelPread line and by a KernelRead line;
# a malformed drf line; Read lines of all forms incl. n == 0; a Recvfrom block, a Sendto block, an Accept block
# (addrlen after 'addr    ='); APR lines; PRINT_NAME lines with CRLF and LF and a read-ish and a plain function;
# StreamRead with TORN; a stdout file with two SysFileRead lines; the last line without a newline.
# Usage: python fx_sweep_f22a.py <work dir>   -> prints 'ALL OK' or the failing members
import json, os, subprocess, sys

work = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(work, exist_ok=True)
T = chr(9)
L = []
L.append('boot line')
L.append('[1][00:00:01.000] libkernel::libkernel::KernelRead()')
L.append(T + 'Read 100 bytes from: /app0/a.bin')
L.append('KernelRead: direct read failed, dst=0x0000000200001000 size=0x10000: reading through a host buffer')
L.append(T + 'Read 65536 bytes (pos = 4096) from: /app0/b.bin')
L.append('Level has started: lvl_a')
for i in range(300):
    L.append('filler line %d with Read inside but no tab' % i)
L.append('KernelRead: direct read failed, dst=0x0000000200002000 size=0x20')
L.append('KernelRead: direct read failed, dst=0x0000000200003000 size=0x400: reading through a host buffer')
L.append(T + 'Read 0 bytes from: /app0/c.bin')
L.append(T + 'Read 0 bytes (pos = 77) from: /app0/d.bin')
L.append(T + 'Read 48 directory bytes from: /app0/dir')
L.append(T + 'Read 16 random bytes from: /dev/urandom')
L.append(T + ' s     = 5')
L.append(T + ' buf   = 0x0000000300000000')
L.append(T + ' len   = 64')
L.append(T + ' flags = 0x00000000')
L.append(T + ' addr  = 0x0000000000000000')
L.append(T + ' addrlen = 0x0000000000000000')
L.append(T + ' s     = 5')
L.append(T + ' addr  = 0x0000000000000000')
L.append(T + ' addrlen = 16')
L.append(T + ' s       = 5')
L.append(T + ' addr    = 0x0000000000000000')
L.append(T + ' addrlen = 0x0000000000000000')
L.append(T + 'APR submit read failed: id=0x00000001, result=0x80020002, path=x')
L.append(T + 'APR read missing host file: x')
L.append('[2][00:00:02.000] libkernel::libkernel::KernelAioSubmitReadCommands()' + chr(13))
L.append('[2][00:00:02.001] libkernel::libkernel::PthreadMutexLock()')
L.append('StreamRead: #1 tid=3 dst=0x1 size=0x2 x TORN:gpu-dirty-after-read')
L.append('StreamRead: #2 tid=3 dst=0x1 size=0x2 x')
L.append('--- Fatal Error ---')
L.append('last line no newline')
text = (chr(10).join(L)).encode()
logp = os.path.join(work, 'log_fx22.txt')
with open(logp, 'wb') as f:
    f.write(text)
sop = os.path.join(work, 'stdout_fx22.txt')
with open(sop, 'wb') as f:
    f.write(b'x\nSysFileRead: ReadFile failed, error=998 size=65536 data=0000\nSysFileRead: ReadFile failed, error=998 size=4096 data=0001\n')
subprocess.run(['xz', '-kf', logp], check=True)
lst = os.path.join(work, 'list.tsv')
with open(lst, 'w', encoding='utf-8', newline='\n') as f:
    f.write(T.join([logp.replace(chr(92), '/'), str(len(text)), 'sample', 'fx', '0', sop.replace(chr(92), '/'), '1']) + chr(10))
lstx = os.path.join(work, 'listx.tsv')
with open(lstx, 'w', encoding='utf-8', newline='\n') as f:
    f.write(T.join([logp.replace(chr(92), '/') + '.xz', str(len(text)), 'sample', 'fx', '0', sop.replace(chr(92), '/'), '1']) + chr(10))
recs = []
for name, lp, blk in (('b4096', lst, '4096'), ('default', lst, None), ('xz', lstx, None)):
    o = os.path.join(work, 'out_%s.jsonl' % name)
    if os.path.exists(o):
        os.remove(o)
    env = dict(os.environ)
    env['F22A_LOCK'] = os.path.join(work, 'nolock')
    env['F22A_STOP'] = os.path.join(work, 'nostop')
    if blk:
        env['F22A_BLOCK'] = blk
    r = subprocess.run([sys.executable, os.path.join(here, 'sweep_f22a.py'), lp, o, '600'], env=env, capture_output=True, text=True)
    assert 'SWEEP COMPLETE' in r.stdout, r.stdout + r.stderr
    recs.append(json.loads(open(o, encoding='utf-8').read().strip()))
bad = []
keys = [k for k in recs[0] if k not in ('path', 'size_now', 'xz_rc')]
for k in keys:
    if not (recs[0][k] == recs[1][k] == recs[2].get(k)):
        bad.append(('block/xz differ', k, recs[0][k], recs[1][k], recs[2].get(k)))
r = recs[0]
exp = {'lines': len(L), 'drf_n': 3, 'drf_bad': 1, 'rd_file': 2, 'rd_file0': 1, 'rd_pos': 2, 'rd_pos0': 1, 'rd_dir': 1,
       'rd_rand': 1, 'rd_other': 0, 'recv_n': 1, 'send_n': 1, 'addrlen_other': 1, 'pn_n': 3, 'pn_funcs': 3,
       'pn_read': {'KernelRead': 1, 'KernelAioSubmitReadCommands': 1}, 'stream_n': 2, 'torn_n': 1, 'sfr_log': 0,
       'fatal': 1, 'apr': {'APR submit read failed': 1, 'APR read missing host file': 1},
       'recv_levels': {'lvl_a': 1}, 'recv_first': 318, 'levels': [{'level': 'lvl_a', 'line': 6}]}
for k, v in exp.items():
    if r.get(k) != v:
        bad.append((k, r.get(k), v))
d = r['drf']
want_drf = [{'line': 4, 'dst': '0000000200001000', 'size': 65536, 'level': '', 'next_read': ['pos', 65536, 5]},
            {'line': 308, 'dst': '0000000200003000', 'size': 1024, 'level': 'lvl_a', 'next_read': ['file', 0, 309]}]
if d != want_drf:
    bad.append(('drf', d, want_drf))
so = r['stdout']
if len(so) != 1 or so[0]['sfr_n'] != 2 or so[0]['sfr_err'] != {'998': 2} or so[0]['sfr_size'] != {'65536': 1, '4096': 1}:
    bad.append(('stdout', so))
if recs[2].get('xz_rc') != 0:
    bad.append(('xz_rc', recs[2].get('xz_rc')))
for b in bad:
    print('FAIL', b)
print('members checked', len(keys) + len(exp) + 3)
print('ALL OK' if not bad else 'NOT OK')
