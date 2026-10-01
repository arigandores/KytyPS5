"""table144.py - the per-tag table of step 2 of s144 from step2/times.txt, score_<tag>.txt and runs144/lock.log (read only).
ASCII only.  python table144.py > step2/table144.txt"""
import re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s144')
import sc144
R = 'C:/kyty/s144'
T = open(R + '/step2/times.txt', encoding='utf-8', errors='replace').read().splitlines()
def last(rx):
    got = None
    for l in T:
        m = re.search(rx, l)
        if m:
            got = (l[:20],) + m.groups()
    return got
busy = [l for l in T if ' BUSY ' in l or 'refused BUSY' in l]
print('BUSY refusals before the lock (no attempt made): %d' % len(busy))
for l in busy:
    print('  ' + l[:200])
for t in sc144.SEQ:
    s = open('%s/score_%s.txt' % (R, t), encoding='utf-8', errors='replace').read().splitlines()
    head = s[0]
    oc = re.search(r'outcome (\S+)', head).group(1)
    g = lambda k: next((x.strip() for x in s if x.strip().startswith(k)), '')
    st = last(r'go144a %s enter_scene start' % t)
    en = last(r'go144a %s enter_scene end rc (\S+) log_\S+ sha256 ([0-9a-f]{64})' % t)
    vg = last(r'go144a %s s51_vidglitch rc (\S+) glitch_\S+ sha256 ([0-9a-f]{64}) rec_\S+ sha256 ([0-9a-f]{64})' % t)
    sh = last(r'go144a %s sheet rc (\S+) sheet_\S+ sha256 ([0-9a-f]{64})' % t)
    gl = re.search(r'glitches s51_vidglitch.py 4 6: (.*?);', g('glitches'))
    vke = g('[Vulkan][E]:').split(' first')[0]
    print('%s %s | start %s end %s rc %s | %s | log %s | %s | %s | glitches %s | video %s | glitch file %s | sheet %s (rc %s)' % (
        t, sc144.level_of(t), st[0] if st else '-', en[0] if en else '-', en[1] if en else '-', oc,
        en[2] if en else '-', g('admission:'), vke, gl.group(1) if gl else 'n/a',
        vg[3] if vg else '-', vg[2] if vg else '-', sh[2] if sh else '-', sh[1] if sh else '-'))
print('lock.log:')
print(open(R + '/runs144/lock.log', encoding='utf-8').read().strip())
