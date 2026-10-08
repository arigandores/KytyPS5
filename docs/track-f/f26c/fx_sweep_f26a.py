# F26a (HPP-688): fixture of sweep_f26a.py - synthetic plain and xz logs with known entries, holds, frames and signature;
# plus the two real logs with the B25 assert (positive control).  Prints 'ALL OK' when every member holds.
import json, lzma, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
work = os.path.join(here, 'fxwork')
os.makedirs(work, exist_ok=True)
NL = chr(10)
lines = [
    '[1][00:00:01.000] libkernel::x()',
    'GuestOut: Level has started: ps_logo',
    'FrameTrace: n=1 dt_us=16000 lat_us=0',
    '[1][00:00:10.000] libkernel::x()',
    'GuestOut: Level has started: intro_next',
    'FrameTrace: n=2 dt_us=17000 lat_us=0',
    'FrameTrace: n=3 dt_us=18000 lat_us=0',
    '[1][00:01:50.500] libkernel::x()',
    'ASSERT: D:\\asobi\\6.0\\source\\engine\\js\\src\\framework\\js\\gpu\\command\\_IMPL\\_PPR\\command_buffer_writer.ppr.cpp:31',
    '',
    'There are too many objects/batches in this scene.',
    'Unhandled host exception: type=1 code=3221225477 pc=0x00000009004a020e access=1 address=0xffffffffffffffff',
    '[1][00:02:00.000] libkernel::x()',
    'GuestOut: Level has started: worldmap',
    'FrameTrace: n=4 dt_us=99000 lat_us=0',
    '[1][00:02:30.000] libkernel::x()',
    'Event: quit',
]
body = (NL.join(lines) + NL).encode()
pa = os.path.join(work, 'log_fxa.txt').replace(os.sep, '/')
open(pa, 'wb').write(body)
pb = os.path.join(work, 'log_fxb.txt.xz').replace(os.sep, '/')
with lzma.open(pb, 'wb') as f:
    # pad so that the entry string crosses a 16 MiB chunk boundary of count_xz
    pad = b'x' * ((1 << 24) - 10) + NL.encode()
    f.write(pad + body)
pc = os.path.join(work, 'log_fxc.txt').replace(os.sep, '/')
open(pc, 'wb').write(('[1][00:00:01.000] a()' + NL + 'GuestOut: Level has started: ps_logo' + NL).encode())
lst = os.path.join(work, 'list.tsv')
real = ['C:/kyty/s59/log_sig1.txt.xz', 'C:/kyty/log_s14_s42_merged_cold.txt.xz']
with open(lst, 'w', encoding='utf-8', newline=NL) as f:
    for p in [pa, pb, pc] + real:
        f.write('%s\t%d\t0\tfx\t-%s' % (p, os.path.getsize(p), NL))
out = os.path.join(work, 'out.jsonl')
if os.path.exists(out):
    os.remove(out)
subprocess.check_call([sys.executable, '-I', os.path.join(here, 'sweep_f26a.py'), lst, out, '3'])
R = {json.loads(l)['path']: json.loads(l) for l in open(out, encoding='utf-8')}
ok = True
def chk(name, cond):
    global ok
    print(('ok   ' if cond else 'FAIL ') + name)
    ok &= bool(cond)
for p in (pa, pb):
    r = R[p]; w = r.get('walk', {})
    lv = w.get('levels', [])
    chk(p + ' counts E=1 S1=1 S2=1 S3=1', (r['E'], r['S1'], r['S2'], r['S3']) == (1, 1, 1, 1))
    chk(p + ' 3 levels', [x['name'] for x in lv] == ['ps_logo', 'intro_next', 'worldmap'])
    chk(p + ' intro t=10.0 next t=120.0', lv[1]['t'] == 10.0 and lv[2]['t'] == 120.0)
    chk(p + ' intro frames 2 sum 35000 first_n 2', (lv[1]['frames'], lv[1]['sum_us'], lv[1]['first_n']) == (2, 35000, 2))
    chk(p + ' last_t 150.0 quit line', w['last_t'] == 150.0 and w['quit_line'] == (18 if p == pb else 17))  # pb: +1 pad line
    chk(p + ' sig lines at t=110.5', [s[0] for s in w['sig_lines']] == [2, 1, 3] and all(s[2] == 110.5 for s in w['sig_lines']))
r = R[pc]
chk('no-intro log: no walk', (r['E'], r['S1'], r['S2'], r['S3']) == (0, 0, 0, 0) and 'walk' not in r)
r = R[real[0]]
chk('s59 sig1: E=1 S1=2 S3=1', (r['E'], r['S1'], r['S3']) == (1, 2, 1))
chk('s59 sig1: sig at 627192 t 82.06', any(s[1] == 627192 and abs(s[2] - 82.06) < 1e-6 for s in r['walk']['sig_lines']))
r = R[real[1]]
chk('s42 merged_cold: E=1 S1=1 S3=1', (r['E'], r['S1'], r['S3']) == (1, 1, 1))
chk('s42 merged_cold: sig at 4407364', any(s[1] == 4407364 for s in r['walk']['sig_lines']))
print('ALL OK' if ok else 'FAILED')
