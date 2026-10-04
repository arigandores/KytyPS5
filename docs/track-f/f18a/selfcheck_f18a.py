# F18a (HPP-535): self-check of sweep_f18a.py on synthetic logs (plain and '.xz'), block border included.
# Usage: python selfcheck_f18a.py <work_dir>      (prints 'ALL OK' and exits 0, else the failed member and exit 1)
import json, os, subprocess, sys

work = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(work, exist_ok=True)
ok = True


def chk(name, cond, got=None):
    global ok
    print(('ok   ' if cond else 'FAIL ') + name + ('' if cond else ' got %r' % (got,)))
    ok &= bool(cond)


Q = 'AudioOut: SDL_QueueAudio failed: Invalid audio device ID'
head = ['TITLE, string = ASTRO BOT',
        '[3][00:00:10.191] libkernel::libkernel::PthreadMutexInitNamed()',
        'AudioOut: opened SDL device "(system default)" (48000 Hz, 2 ch, format 0x8120)',
        'AudioOut: opened SDL device "(system default)" (48000 Hz, 2 ch, format 0x8120)',
        '[7][00:00:12.000] libAudio::AudioOut::AudioOutOpen()',
        'AudioOut: vibration port 3 (48000 Hz, 2 ch, 512 frames, float) -> pad haptics',
        'Level has started: underwater_aerial_garden',
        'FrameTrace: n=1 dt_us=16000 lat_us=1',
        'FrameTrace: n=2 dt_us=17000 lat_us=1',
        '[7][00:12:54.500] libkernel::libkernel::Usleep()',
        'some line before the failure']
# log A: failures with one other error text and a sound line after the first failure
a = head + [Q, Q, 'AudioOut: SDL_QueueAudio failed: Audio device has a callback, queueing not allowed', 'after one',
            'FrameTrace: n=3 dt_us=20000 lat_us=1', Q, 'AudioIn: capture stopped; using silence',
            '[7][00:13:10.250] libkernel::libkernel::Usleep()', Q, 'Haptics: pad audio queue failed: Invalid audio device ID',
            'Window 1 minimized', 'Event: quit']
# log B: no failures
b = head + ['FrameTrace: n=3 dt_us=20000 lat_us=1', '[7][00:05:00.000] libkernel::libkernel::Usleep()']
# log C: a block border - padding larger than one 64 MiB block before the failure (written sparsely by repetition)
pad = ('x' * 255 + '\n') * (1 << 12)  # 1 MiB of lines
paths = {}
for name, lines in (('log_a.txt', a), ('log_b.txt', b)):
    p = os.path.join(work, name).replace(os.sep, '/')
    with open(p, 'wb') as f:
        f.write(('\n'.join(lines) + '\n').encode('utf-8'))
    paths[name] = p
pc = os.path.join(work, 'log_c.txt').replace(os.sep, '/')
with open(pc, 'wb') as f:
    f.write(('\n'.join(head) + '\n').encode('utf-8'))
    for _ in range(66):
        f.write(pad.encode('ascii'))
    f.write(('[9][00:20:00.000] libkernel::libkernel::Usleep()\nline c1\n' + Q + '\n' + Q + '\ntrailer without newline').encode('utf-8'))
paths['log_c.txt'] = pc
# log D: log A through xz
pd = os.path.join(work, 'log_d.txt').replace(os.sep, '/')
with open(pd, 'wb') as f:
    f.write(('\n'.join(a) + '\n').encode('utf-8'))
if os.path.exists(pd + '.xz'):
    os.remove(pd + '.xz')
subprocess.run(['xz', '-k', pd], check=True)
paths['log_d.txt.xz'] = pd + '.xz'

lst = os.path.join(work, 'list.tsv')
with open(lst, 'w', encoding='utf-8', newline='\n') as f:
    for k in ('log_a.txt', 'log_b.txt', 'log_c.txt', 'log_d.txt.xz'):
        f.write('%s\t%d\n' % (paths[k], os.path.getsize(paths[k])))
    f.write('%s\t%d\n' % (work.replace(os.sep, '/') + '/log_missing.txt', 5))
out = os.path.join(work, 'out.jsonl')
if os.path.exists(out):
    os.remove(out)
env = dict(os.environ, F18A_LOCK=os.path.join(work, 'NO_LOCK'), F18A_STOP=os.path.join(work, 'NO_STOP'))
r = subprocess.run([sys.executable, os.path.join(here, 'sweep_f18a.py'), lst, out, '300'], capture_output=True, text=True, env=env)
chk('sweep rc 0 and COMPLETE', r.returncode == 0 and 'SWEEP COMPLETE' in r.stdout, (r.returncode, r.stdout[-300:], r.stderr[-300:]))
recs = {}
for l in open(out, encoding='utf-8'):
    d = json.loads(l)
    recs[os.path.basename(d['path'])] = d
A, B, C, D = recs['log_a.txt'], recs['log_b.txt'], recs['log_c.txt'], recs['log_d.txt.xz']
chk('A qfail 5', A['qfail'] == 5, A['qfail'])
chk('A qfail_inv 4', A['qfail_inv'] == 4, A['qfail_inv'])
chk('A qtexts sum == qfail', sum(A['qtexts'].values()) + A['qtexts_over'] == A['qfail'], A['qtexts'])
chk('A qfirst line 12', A['qfirst'][0] == 12, A['qfirst'])
chk('A qfirst ts 774500', A['qfirst'][1] == (12 * 60 + 54) * 1000 + 500, A['qfirst'])
chk('A qfirst ft 2 / 33000', A['qfirst'][2:] == [2, 33000], A['qfirst'])
chk('A qlast line 20 ts 790250 ft 3 / 53000', A['qlast'] == [20, 790250, 3, 53000], A['qlast'])
chk('A ctx ends with the line before', A['ctx'][-1] == 'some line before the failure' and len(A['ctx']) == 11, A['ctx'][-2:])
chk('A after', A['after'][:2] == ['after one', 'FrameTrace: n=3 dt_us=20000 lat_us=1'], A['after'])
ev = [e[4] for e in A['ev']]
chk('A ev texts', ev == ['AudioOut: opened SDL device "(system default)" (48000 Hz, 2 ch, format 0x8120)'] * 2 +
    ['AudioOut: vibration port 3 (48000 Hz, 2 ch, 512 frames, float) -> pad haptics', 'Level has started: underwater_aerial_garden',
     'AudioIn: capture stopped; using silence', 'Haptics: pad audio queue failed: Invalid audio device ID', 'Window 1 minimized',
     'Event: quit'], ev)
chk('A ev lines increase', all(x[0] < y[0] for x, y in zip(A['ev'], A['ev'][1:])), [e[0] for e in A['ev']])
chk('A vibration ev line 6 ts 12000', A['ev'][2][:2] == [6, 12000], A['ev'][2])
chk('A snd', A['snd'].get('AudioOut: opened SDL device "(system default)" (# Hz, # ch, format #x#)') == 2 and len(A['snd']) == 4, A['snd'])
chk('A lvl', A['lvl'] == ['underwater_aerial_garden'], A['lvl'])
chk('A ts first/last', (A['ts_first'], A['ts_last']) == (10191, 790250), (A['ts_first'], A['ts_last']))
chk('A ft', (A['ft_n'], A['ft_us']) == (3, 53000), (A['ft_n'], A['ft_us']))
chk('A lines 23', A['lines'] == 23, A['lines'])
chk('B qfail 0, no ctx', B['qfail'] == 0 and B['qfirst'] is None and B['ctx'] == [] and B['qfail_inv'] == 0, B['qfail'])
chk('B ts_last 300000', B['ts_last'] == 300000, B['ts_last'])
chk('C qfail 2 across the block border', C['qfail'] == 2 and C['qfail_inv'] == 2, C['qfail'])
chk('C qfirst line', C['qfirst'][0] == len(head) + 66 * (1 << 12) + 3, C['qfirst'])
chk('C qfirst ts 1200000 ft 2 / 33000', C['qfirst'][1:] == [1200000, 2, 33000], C['qfirst'])
chk('C ctx last line', C['ctx'][-1] == 'line c1' and len(C['ctx']) == 60, C['ctx'][-2:])
chk('C after: trailer without newline', C['after'] == ['trailer without newline'], C['after'])
chk('C lines', C['lines'] == len(head) + 66 * (1 << 12) + 5, C['lines'])
chk('D (xz) == A but path, size, sha, xz', all(D[k] == A[k] for k in A if k not in ('path', 'size', 'sha256', 'xz')) and D['xz'] and D.get('xz_rc') == 0,
    [k for k in A if k not in ('path', 'size', 'sha256', 'xz') and D.get(k) != A[k]])
chk('D sha256_text == sha256 of the plain log', D.get('sha256_text') == A['sha256'], D.get('sha256_text'))
chk('missing file record', recs['log_missing.txt'].get('missing') is True)
# resumable: a second call does nothing
r = subprocess.run([sys.executable, os.path.join(here, 'sweep_f18a.py'), lst, out, '300'], capture_output=True, text=True, env=env)
chk('second call: left 0', 'left 0' in r.stdout and 'SWEEP COMPLETE' in r.stdout, r.stdout[-200:])
# lock stops between files
out2 = os.path.join(work, 'out2.jsonl')
if os.path.exists(out2):
    os.remove(out2)
lk = os.path.join(work, 'FAKE_LOCK')
open(lk, 'w').close()
r = subprocess.run([sys.executable, os.path.join(here, 'sweep_f18a.py'), lst, out2, '300'], capture_output=True, text=True,
                   env=dict(env, F18A_LOCK=lk))
os.remove(lk)
chk('lock: rc 3, nothing written', r.returncode == 3 and not os.path.exists(out2), (r.returncode, r.stdout[-200:]))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
