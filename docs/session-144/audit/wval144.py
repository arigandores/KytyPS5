# wval144.py - Session Auditor s144 step 3 (HPP-333): the validation layer lines of the 21 W logs - severities, the duplicate
# message limit (the harness sets VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000) and where in the hold it was reached. READ ONLY.
import re, mmap, json, bisect

A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s144/step3/aud144.json'))}
RN = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
LIM = b'This VUID has now been reported'
nsat = 0
for i in range(0, 21):
    t = 'w144_%02d' % i
    L = A[('s144', t)]['log']
    with open('C:/kyty/s144/log_%s.txt' % t, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        c = {}
        for k in (b'[Vulkan][E]', b'[Vulkan][W]', b'[Vulkan][I]', b'[Vulkan][V]', b'[Vulkan][?]'):
            n = 0
            p = mm.find(k)
            while p != -1:
                n += 1
                p = mm.find(k, p + 1)
            c[k.decode()] = n
        sat = []
        p = mm.find(LIM)
        while p != -1:
            sat.append(p)
            p = mm.find(LIM, p + 1)
        rows = []
        p = mm.find(b'FrameTrace: n=')
        while p != -1:
            m = RN.match(mm[p:p + 60])
            if m:
                rows.append((p, int(m.group(2))))
            p = mm.find(b'FrameTrace: n=', p + 1)
        size = len(mm)
        mm.close()
    ep = L.get('entry_pos')
    tot = sum(dt for p, dt in rows if ep is not None and p > ep) / 1e6
    at = [sum(dt for p, dt in rows if ep is not None and ep < p < s) / 1e6 for s in sat]
    nsat += 1 if sat else 0
    print('WVAL %s %s: lines E %d W %d I %d V %d ?%d; duplicate-limit lines %d at bytes %s of %d; presented after the entry line at the limit %s s of %.1f s' % (
        t, A[('s144', t)]['level'], c['[Vulkan][E]'], c['[Vulkan][W]'], c['[Vulkan][I]'], c['[Vulkan][V]'], c['[Vulkan][?]'], len(sat), sat[:2], size,
        ['%.1f' % x for x in at[:2]], tot))
print('W with the duplicate message limit reached: %d of 21' % nsat)
print('ALL DONE')
