# scout3.py - nonzero fields of the FrameTrace family on skip frames / held flips / long frames of one log (S0, HPP-294)
import re, sys, collections
path = sys.argv[1]
rxkv = re.compile(rb' ([a-z0-9_]+)=(-?\d+)')
cur = {}; frames = []
order = []
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace'):
            k = line[:line.find(b':')]
            if k in (b'FrameTrace', b'FrameTrace-draw', b'FrameTrace-x', b'FrameTrace-rp'):
                d = {a.decode(): int(b) for a, b in rxkv.findall(line)}
                if k == b'FrameTrace':
                    if cur:
                        frames.append(cur)
                    cur = {'_main': d}
                else:
                    cur[k.decode()] = d
if cur:
    frames.append(cur)
print('frames', len(frames))
def flat(fr):
    o = {}
    for k, d in fr.items():
        for a, b in d.items():
            o[(k, a)] = b
    return o
sk = [fr for fr in frames if fr.get('FrameTrace-x', {}).get('skc_ap_skip', 0) > 0]
hd = [fr for fr in frames if fr.get('FrameTrace-x', {}).get('skc_held_inc', 0) > 0]
lg = [fr for fr in frames if fr['_main'].get('dt_us', 0) >= 100000 and fr['_main'].get('n', 0) > 200]
pc = [fr for fr in frames if fr.get('FrameTrace-x', {}).get('pg_cold_n', 0) > 0]
print('skip frames', len(sk), 'held', len(hd), 'long(n>200)', len(lg), 'pg_cold frames', len(pc))
# fields whose name suggests creation/cold/new
names = collections.Counter()
for fr in frames:
    for (k, a), b in flat(fr).items():
        if b and re.search(r'cold|new|miss|skip|held|perm|spec|insts|_up|imp|obj|pipe|prog|fail', a):
            names[(k, a)] += 1
print('candidate fields (frames nonzero):')
for (k, a), c in sorted(names.items()):
    print('   ', k, a, c)
def show(title, lst, lim):
    print('==', title)
    for fr in lst[:lim]:
        m = fr['_main']
        x = fr.get('FrameTrace-x', {}); d = fr.get('FrameTrace-draw', {})
        print('  n=%d dt=%d draws=%s cpu_main=%s cpu_gpu=%s cpu_pres=%s semwait=%s gpu_busy=%s faults=%s | skip=%s held=%s pg_cold=%s | img_new=%s img_up=%s img_up_kb=%s img_imp_kb=%s buf_new=%s srt_miss=%s memo_miss=%s m_insts=%s da_miss=%s' % (
            m.get('n'), m.get('dt_us'), m.get('draws'), m.get('cpu_main_us'), m.get('cpu_gpu_us'), m.get('cpu_present_us'), m.get('semwait_us'), m.get('gpu_busy_us'), m.get('faults'),
            x.get('skc_ap_skip'), x.get('skc_held_inc'), x.get('pg_cold_n'), d.get('img_new'), d.get('img_up'), d.get('img_up_kb'), d.get('img_imp_kb'), d.get('buf_new'), d.get('srt_miss'), d.get('memo_miss'), d.get('m_insts'), d.get('da_miss')))
show('skip frames', sk, 80)
show('held', hd, 80)
show('long', lg, 40)
show('pg_cold', pc, 60)
