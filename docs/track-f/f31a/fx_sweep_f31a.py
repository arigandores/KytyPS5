# F31a: fixture of sweep_f31a.one() on a synthetic log (two scenes, an empty 'Level has started:', frames, a signature
# inside the second scene, the build line).  Prints ALL OK.
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sweep_f31a as S

NL = chr(10)
lines = ['TITLE_ID, string = PPSA21564', 'Build', '  version: Fork build arigandores/KytyPS5 abc1234', '',
         '[1][00:00:10.000] libkernel::x()', 'GuestOut: Level has started:', 'GuestOut: Level has started: alpha',
         'FrameTrace: n=1 dt_us=1000 lat_us=1', 'FrameTrace: n=2 dt_us=2000 lat_us=1',
         '[1][00:01:00.500] libkernel::x()', 'GuestOut: Level has started: beta',
         'FrameTrace: n=3 dt_us=30000 lat_us=1', 'RtSkip: mode 5 ctx_slots=8', 'FrameTrace: n=4 dt_us=40000 lat_us=1',
         '[2][00:01:05.250] libkernel::y()',
         'ASSERT: D:/x/command_buffer_writer.ppr.cpp:31', '', 'There are too many objects/batches in this scene.',
         '--- Error ---', 'Unhandled host exception: type=1 code=3221225477 pc=0x00000009004a020e access=1', '']
d = tempfile.mkdtemp()
p = os.path.join(d, 'log_x.txt').replace(os.sep, '/')
open(p, 'wb').write(NL.join(lines).encode())
r = S.one([p, str(os.path.getsize(p)), 't', '-'])
ok = True
def chk(c, msg):
    global ok
    print(('ok   ' if c else 'FAIL ') + msg)
    ok &= bool(c)
if os.path.exists(S.LOCK) or os.path.exists(S.STOP):
    chk(r.get('skipped_lock') is True, 'lock present -> skipped')
else:
    chk(r['build'] == 'version: Fork build arigandores/KytyPS5 abc1234', 'build line')
    chk([e['name'] for e in r['entries']] == ['alpha', 'beta'], 'entries (empty name ignored)')
    chk(r['entries'][0]['frames'] == 2 and r['entries'][0]['sum_us'] == 3000, 'alpha frames/sum')
    chk(r['entries'][1]['frames'] == 2 and r['entries'][1]['sum_us'] == 70000, 'beta frames/sum')
    chk(abs(r['entries'][0]['t'] - 10.0) < 1e-6 and abs(r['entries'][1]['t'] - 60.5) < 1e-6, 'entry times')
    chk(r['S'] == [1, 1, 1], 'signature counts')
    chk(all(x['ent'] == 1 and x['ent_frames'] == 2 and x['ent_us'] == 70000 for x in r['sig']), 'signature -> entry beta, hold before it')
    chk(abs(r['sig'][0]['t'] - 65.25) < 1e-6, 'signature time')
    chk(r['n_error'] == 1 and r['n_unhandled'] == 1 and r['n_quit'] == 0, 'error counts')
    chk(r['rtskip'] == ['RtSkip: mode 5 ctx_slots=8'], 'rtskip line')
os.remove(p); os.rmdir(d)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
