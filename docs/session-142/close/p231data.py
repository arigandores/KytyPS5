# s142 close (HPP-281, lead): per-tag rows for map (A) and new (B) rows, from the scorer summary printed with --sheet viewed.
import re, sys
p = 'C:/kyty/s142/step4/summary142_viewed.txt'
t = open(p, encoding='utf-8', errors='replace').read()
blocks = re.split(r'(?m)^TAG ', t)[1:]
for b in blocks:
    b = b.split('\nSCENE_OK')[0].split('\nCENSUS')[0]
    tag = b.split()[0]
    lv = re.search(r'level (\S+)', b).group(1)
    oc = re.search(r'outcome (\S+)', b).group(1)
    ff = re.search(r'first scene frame \(n, dt_us, draws\): (\([^)]*\))', b)
    pt = re.search(r'after the first scene frame ([\d.]+) s over (\d+) frames; dt_us median (\d+) max (\d+)', b)
    k3w = re.search(r'K3 entry window[^:]*: (.*)', b).group(1)
    k3h = re.search(r'\n  K3 hold: (.*)', b).group(1)
    sk = re.search(r'skipped draw: (\d+) lines, (\d+) frames', b)
    op = re.search(r'opcode not implemented: (\d+) lines; against 96/1/4: (\S+)', b)
    st = re.search(r'Stubbed function: (\d+)', b)
    ps = re.search(r'PriorityStall > 50 ms: (\d+)(?: \(lines \d+, max (\d+) us\))?', b)
    bv = re.search(r'BvhLoopCapTrip: (\d+)', b)
    ve = re.search(r'\[Vulkan\]\[E\]: (\d+)', b)
    vd = re.search(r'video: frames (\d+)', b)
    gl = re.search(r'glitches s51_vidglitch.py 4 6: (\d+) of', b)
    dm = re.search(r'death markers \(in order\): (.*)', b).group(1)
    print('|'.join(str(x) for x in [tag, lv, oc, ff.group(1) if ff else '-',
          pt.groups() if pt else '-', 'K3w=' + k3w, 'K3h=' + k3h,
          'skip=%s/%s' % sk.groups() if sk else 'skip=-', 'op=%s/%s' % op.groups() if op else 'op=-',
          'stub=' + (st.group(1) if st else '-'), 'ps=%s/%s' % ps.groups() if ps else 'ps=-',
          'bvh=' + (bv.group(1) if bv else '-'), 'vkE=' + (ve.group(1) if ve else '-'),
          'video=' + (vd.group(1) if vd else '-'), 'gl=' + (gl.group(1) if gl else '-'), 'death=' + dm]))
