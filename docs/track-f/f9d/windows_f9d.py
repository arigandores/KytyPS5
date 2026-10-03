"""F9d (HPP-421): the table "present -> event" by the life windows of the T6-format images, from extract.tsv and
life_cover.tsv of extract_f9d.py.  usage: python windows_f9d.py <extract_dir>
Window = one life of 0x53cc10000 960x540 tile 27 (create .. free) or of 0x538bc0000 480x270 tile 27; inside each window:
the counts of ImageWatch events by image, DumpCS groups by shader, BufferFillTrace lines covering the window's address.
Also: DumpCS group heads by shader; ImageLifeCover by size/format; BufferFillTrace covering 0x53cc10000 / 0x538bc0000.
Output <extract_dir>/windows.txt; ASCII only."""
import collections, re, sys

d = sys.argv[1]
R = [l.rstrip('\n').split('\t') for l in open(d + '/extract.tsv')][1:]
C = [l.rstrip('\n').split('\t') for l in open(d + '/life_cover.tsv')][1:]
out = open(d + '/windows.txt', 'w', newline='\n')

def p(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    out.write(s + '\n')

def vf(r):
    return int(r[5]) if r[5] not in ('', 'None') else None

T6 = {'0x000000053cc10000': '960x540@53cc10000', '0x0000000538bc0000': '480x270@538bc0000'}
wins = []
open_ = {}
for r in R:
    if r[1] != 'ImageLife' or not r[7].endswith('t27'):
        continue
    g = re.search(r'guest=(\S+)', r[8]).group(1)
    if g not in T6:
        continue
    ev = re.search(r'event=(\S+) reason=(\S+) line=(\d+)', r[8])
    if ev.group(1) == 'create':
        open_[g] = r
    else:
        c = open_.pop(g, None)
        wins.append((T6[g], c, r, '%s:%s' % (ev.group(2), ev.group(3))))
for g, c in open_.items():
    wins.append((T6[g], c, None, 'alive at the end'))
wins.sort(key=lambda w: vf(w[1]))
p('T6-format life windows (video frame v = present - 1; host s = .idx time)')
p('%-18s %6s %6s %6s %6s %9s %9s  %-22s %s' % ('image', 'v_from', 'v_to', 'p_from', 'p_to', 's_from', 's_to', 'end', 'ImageWatch upload of 0x53cc10000 in window'))
for name, c, f, how in wins:
    a, b = vf(c), (vf(f) if f else 10231)
    up = [r for r in R if r[1] == 'ImageWatch' and 'image=0x000000053cc10000' in r[8] and vf(r) is not None and a <= vf(r) <= b]
    p('%-18s %6s %6s %6s %6s %9s %9s  %-22s %s' % (name, a, b, c[4], f[4] if f else '-', c[6], f[6] if f else '-', how,
      ','.join('v%s(line %s)' % (r[5], r[0]) for r in up) or '-'))
p('')
p('ImageWatch events by image and event (all lines; the knob filters images covering 0x53cc10000)')
cnt = collections.Counter()
for r in R:
    if r[1] == 'ImageWatch':
        m = re.search(r'event=(\S+) image=(\S+) size=(\S+)', r[8])
        cnt[(m.group(2), m.group(3), m.group(1))] += 1
for k, v in sorted(cnt.items()):
    p('  %s size %s %-15s %d' % (k[0], k[1], k[2], v))
p('')
p('ImageWatch events on the image 0x53cc10000 itself by event: %s' % dict(collections.Counter(
    re.search(r'event=(\S+)', r[8]).group(1) for r in R if r[1] == 'ImageWatch' and 'image=0x000000053cc10000' in r[8])))
p('ImageWatchDraw lines: %d; DumpDraw lines: %d; DumpDispatch lines: %d' % tuple(
    sum(1 for r in R if r[1] == k) for k in ('ImageWatchDraw', 'DumpDraw', 'DumpDispatch')))
p('')
heads = [r for r in R if r[1] == 'DumpCS_head']
hs = collections.Counter(re.search(r'^(\S+).*shader=(\S+)', r[8]).groups() if re.search(r'shader=', r[8]) else (r[8][:40], '') for r in heads)
p('DumpCS groups (KYTY_DUMP_ADDRS; head line = the line before the group): %d' % len(heads))
for k, v in sorted(hs.items()):
    vs = [vf(r) for r in heads if k[1] and ('shader=' + k[1]) in r[8]]
    vs = [x for x in vs if x is not None]
    p('  %s shader %s groups %d v %s..%s' % (k[0], k[1], v, min(vs) if vs else '-', max(vs) if vs else '-'))
bufs = collections.Counter(re.search(r'usage=(\S+) addr=(\S+) .*size=(\S+)', r[8]).groups() for r in R if r[1] == 'DumpCS')
for k, v in sorted(bufs.items()):
    p('  DumpCS buffer usage=%s addr=%s size=%s lines %d' % (k[0], k[1], k[2], v))
p('')
p('BufferFillTrace lines whose range covers 0x53cc10000: %d; covers 0x538bc0000: %d; intersect a T6-format range: %d' % (
    sum(1 for r in R if r[1] == 'BufferFillTrace' and '0x53cc10000' in r[7].split(',')),
    sum(1 for r in R if r[1] == 'BufferFillTrace' and '0x538bc0000' in r[7].split(',')),
    sum(1 for r in R if r[1] == 'BufferFillTrace')))
p('')
cv = collections.Counter()
for r in C:
    m = re.search(r'event=(\S+) reason=(\S+) line=(\d+).*guest=(\S+) bytes=(\d+) w=(\d+) h=(\d+).*fmt=(\d+) tile=(\d+)', r[8])
    cv[(m.group(4), int(m.group(5)), m.group(6) + 'x' + m.group(7), m.group(8), m.group(9), m.group(1) + ':' + m.group(2) + ':' + m.group(3))] += 1
p('ImageLife of other images covering 0x53cc10000 or 0x538bc0000 (variant of the executor): %d lines' % len(C))
for k, v in sorted(cv.items()):
    p('  guest %s bytes 0x%x %s fmt %s tile %s %s: %d' % (k[0], k[1], k[2], k[3], k[4], k[5], v))
out.close()
