# F20a (HPP-551): fixture of sweep_f20a.py - a synthetic log with known scenes, frames and intervals; the record of the
# sweep is compared member by member.  The lock and STOP paths are pointed at absent files of the fixture directory.
# Usage: python fx_sweep_f20a.py <work dir>      prints 'ALL OK' and exits 0 when every member holds.
import json, os, subprocess, sys

wd = sys.argv[1]
os.makedirs(wd, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
L = []


def ft(n, dt, draws):
    L.append('FrameTrace: n=%d dt_us=%d cpu=1 draws=%d x=1' % (n, dt, draws))


L.append('Gate: titleasync=1')
L.append('S-pcw: KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=0')
L.append('GuestOut: Level has started: ')                 # empty name: counted, no scene
for n in range(1, 4):
    ft(n, 16000, 5)
L.append('[1][00:00:01.000] GuestOut: Level has started: underwater_aerial_garden')
ft(4, 500000, 50)                                          # before the first scene frame: not a slow row
ft(5, 700000, 150)                                         # the first scene frame (draws >= 100): not counted
for n in range(6, 606):                                    # 600 frames x 16 000 us = 9.6 s of scene time
    ft(n, 16000, 200)
L.append('PriorityStall: tick=1 unsub=0 us=150000 site=+0x10')
L.append('Read 16 bytes')
ft(606, 190000, 200)                                       # starts at 9.6 s: window, K3, PriorityStall only
ft(607, 300000, 200)                                       # starts at 9.79 s: window (straddles 10 s), nothing in the interval
L.append('Vulkan pipeline cache: saved 90629860 bytes to _PipelineCache\\PPSA21564.bin (92638 us)')
ft(608, 150000, 200)                                       # starts at 10.09 s: hold, pipeline cache save
L.append('BvhLoopCapTrip: trips=+1 total=1')
L.append('PriorityStall: tick=2 unsub=0 us=270000 site=+0x10')
ft(609, 299000, 200)                                       # hold, trip + stall
for i in range(30):
    L.append('%%%d   = BitCastF32U32 %%1 (F32; uses=1)' % i)
L.append('12: V_MAC_F32 v1, v2, v3')
ft(610, 1200000, 200)                                      # hold, >= 1 s, translation dump
for n in range(611, 700):
    ft(n, 16000, 200)
ft(700, 120000, 200)                                       # hold, nothing
L.append('Event: quit')
ft(701, 400000, 200)                                       # after quit: flagged, not counted
L.append('GuestOut: Level has started: intro_next')
ft(702, 16000, 300)                                        # first scene frame of intro_next
ft(703, 100000, 300)                                       # window K3 of intro_next (exactly the threshold)
ft(704, 99999, 300)                                        # below the threshold
p = wd + '/log_fx.txt'
with open(p, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(L) + '\n')
lst = wd + '/list.tsv'
with open(lst, 'w', encoding='utf-8', newline='\n') as f:
    f.write('%s\t%d\tsweep\n' % (p, os.path.getsize(p)))
    f.write('%s\t%d\thash\n' % (p + '.copy', os.path.getsize(p)))
with open(p + '.copy', 'wb') as f:
    f.write(open(p, 'rb').read())
out = wd + '/out.jsonl'
if os.path.exists(out):
    os.remove(out)
env = dict(os.environ, F20A_LOCK=wd + '/no.lock', F20A_STOP=wd + '/no.stop')
r = subprocess.run([sys.executable, os.path.join(here, 'sweep_f20a.py'), lst, out, '60'], capture_output=True, text=True, env=env)
ok = 'SWEEP COMPLETE' in r.stdout
recs = [json.loads(l) for l in open(out, encoding='utf-8')]
a, hb = recs[0], recs[1]
bad = []


def chk(name, got, want):
    if got != want:
        bad.append('%s: got %r want %r' % (name, got, want))


chk('complete', ok, True)
chk('hash mode sha', hb['sha256'], a['sha256'])
chk('hash mode keys', sorted(hb), ['mode', 'path', 'sha256', 'size', 'xz'])
chk('lines', a['lines'], len(L))
chk('ft_n', a['ft_n'], 704)
chk('n_first/n_last', (a['n_first'], a['n_last']), (1, 704))
chk('head', a['head'], ['Gate: titleasync=1', 'S-pcw: KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=0'])
chk('cnt', (a['cnt']['prio'], a['cnt']['trip'], a['cnt']['pcs'], a['cnt']['quit'], a['cnt']['lvl_empty']), (2, 1, 1, 1, 1))
chk('scenes', len(a['scenes']), 2)
s = a['scenes'][0]
chk('s0 level/first_n/ft_before', (s['level'], s['first_n'], s['ft_before']), ('underwater_aerial_garden', 5, 3))
chk('s0 frames', (s['frames'], s['frames_h'], s['last_n'], s['hold_first_n'], s['after_quit']), (695, 93, 700, 608, 1))
chk('s0 sum_us', s['sum_us'], 600 * 16000 + 190000 + 300000 + 150000 + 299000 + 1200000 + 89 * 16000 + 120000)
chk('s0 k', (s['k100_w'], s['k100_h'], s['k1s_w'], s['k1s_h'], s['max_w'], s['max_h']), (2, 4, 0, 1, 300000, 1200000))
s1 = a['scenes'][1]
chk('s1', (s1['level'], s1['first_n'], s1['frames'], s1['k100_w'], s1['k100_h'], s1['sum_us']), ('intro_next', 702, 2, 1, 0, 199999))
sl = a['slow']
chk('slow n', [x['n'] for x in sl], [606, 607, 608, 609, 610, 700, 701, 703])
chk('slow_n', (a['slow_n'], a['slow_over']), (8, 0))
chk('606', (sl[0]['prio'], sl[0]['prio_us'], sl[0]['io'], sl[0]['il'], sl[0]['t_before_us'], sl[0]['idx'], sl[0]['q'], sl[0]['pcs'], sl[0]['trip'], sl[0]['ir']),
    (1, 150000, 1, 2, 9600000, 601, 0, 0, 0, 0))
chk('607', (sl[1]['il'], sl[1]['prio'], sl[1]['top'], sl[1]['t_before_us']), (0, 0, [], 9790000))
chk('608', (sl[2]['pcs'], sl[2]['pcs_us'], sl[2]['prio'], sl[2]['t_before_us']), (1, 92638, 0, 10090000))
chk('609', (sl[3]['trip'], sl[3]['prio'], sl[3]['prio_us']), (1, 1, 270000))
chk('610', (sl[4]['ir'], sl[4]['gcn'], sl[4]['il'], sl[4]['dt_us']), (30, 1, 31, 1200000))
chk('700', (sl[5]['il'], sl[5]['prio'], sl[5]['pcs'], sl[5]['trip'], sl[5]['ir'], sl[5]['scene']), (0, 0, 0, 0, 0, 0))
chk('701', (sl[6]['q'], sl[6]['win'], sl[6]['scene']), (1, 1, 0))
chk('703', (sl[7]['scene'], sl[7]['dt_us'], sl[7]['t_before_us'], sl[7]['idx']), (1, 100000, 0, 1))
chk('line of 606', sl[0]['line'], L.index('FrameTrace: n=606 dt_us=190000 cpu=1 draws=200 x=1') + 1)
for b in bad:
    print('FAIL', b)
print('members', 22, 'failed', len(bad))
if not bad:
    print('ALL OK')
sys.exit(1 if bad else 0)
