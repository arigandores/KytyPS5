# Session 127 audit (HPP-112): independent count of Vulkan validation lines in s5s127 (rtskip=0) / s6s127 (rtskip=1),
# item 83(b)(2)-(4). Own crude class = text after '[Vulkan][W]' with hex handles, the first '[N]' and '(N)' removed.
# No code shared with val127.py.
import collections, re


def scan(t):
    E = W = dup = 0
    cls = collections.Counter()
    for l in open('C:/kyty/s127/log_%s.txt' % t, 'rb'):
        if b'[Vulkan][E]' in l: E += 1
        if b'duplicate_message_limit' in l: dup += 1
        if b'[Vulkan][W]' in l:
            W += 1
            s = l.split(b'[Vulkan][W]', 1)[1]
            s = re.sub(rb'0x[0-9a-fA-F]+', b'H', s)
            s = re.sub(rb'\[\d+\]', b'', s, count=1)
            s = re.sub(rb'\(\d+\)', b'', s)
            cls[s[:260]] += 1
    return E, W, dup, cls


a = scan('s5s127'); b = scan('s6s127')
print('s5s127 [E] %d [W] %d duplicate_message_limit %d classes %d' % (a[0], a[1], a[2], len(a[3])))
print('s6s127 [E] %d [W] %d duplicate_message_limit %d classes %d' % (b[0], b[1], b[2], len(b[3])))
print('s6 classes not in s5: %d; s5 classes not in s6: %d' % (len(set(b[3]) - set(a[3])), len(set(a[3]) - set(b[3]))))
