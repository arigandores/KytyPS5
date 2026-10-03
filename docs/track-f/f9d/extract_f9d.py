"""F9d (HPP-421, ROADMAP s122 item 349 (v')(1)): streaming extract of the diagnostic lines of one run with the present
time and number.  usage: python extract_f9d.py <run_dir> <out_dir>
Pass 1: FrameTrace rows (line, n, dt_us) and the T6-format images: ImageLife lines with fmt=97 (RGBA16F, bpp 8) and
960x540 or 480x270 -> the set of their guest ranges [guest, guest+bytes).
Pass 2: every line with ImageWatch: / ImageWatchDraw: / DumpDraw / DumpDispatch (all; the address filter is the knob),
DumpCS lines and the line before the first DumpCS of a group (variant of the executor: the KYTY_DUMP_ADDRS knob printed
DumpCS, not DumpDispatch), BufferFillTrace: whose [addr, addr+size) intersects a T6-format range, ImageLife: of the T6
format; and (variant of the executor, separate file) ImageLife: of every other image whose range covers 0x53cc10000 or
0x538bc0000.
Present clock (the method of sc146.py vcont / F9a table_user.py): the FrameTrace rows and the .idx records on one clock
anchored at their ends; an event line belongs to the first FrameTrace row AFTER it (the row is printed at the end of its
frame); its present = the .idx record nearest to the end of that row; video frame v = present - 1.
Output: <out>/extract.tsv, <out>/life_cover.tsv, <out>/rows.json (summary). ASCII only."""
import bisect, json, os, re, sys

run, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
log = os.path.join(run, 'log.txt')
idx = []
for line in open(os.path.join(run, 'rec.mp4.idx')):
    a = line.split()
    if len(a) >= 3:
        idx.append((int(a[0]), int(a[1]), float(a[2])))
it = [t for _, _, t in idx]
WATCH = (0x53cc10000, 0x538bc0000)
KV = re.compile(rb'(\w+)=(\S+)')

def kv(line):
    return {k.decode(): v.decode() for k, v in KV.findall(line)}

rows = []
t6 = {}
with open(log, 'rb') as f:
    for ln, line in enumerate(f, 1):
        if line.startswith(b'FrameTrace: n='):
            m = re.match(rb'FrameTrace: n=(\d+) dt_us=(\d+)', line)
            rows.append((ln, int(m.group(1)), int(m.group(2))))
        elif line.startswith(b'ImageLife:'):
            d = kv(line)
            if d.get('fmt') == '97' and (d.get('w'), d.get('h')) in (('960', '540'), ('480', '270')):
                g = int(d['guest'], 16)
                t6[(g, int(d['bytes']))] = (d['w'], d['h'], d['tile'])
ends = [0.0] * len(rows)
t = it[-1]
for k in range(len(rows) - 1, -1, -1):
    ends[k] = t
    t -= rows[k][2] / 1e6
rlines = [r[0] for r in rows]
ranges = sorted(t6)

def where(ln):
    k = bisect.bisect_right(rlines, ln)
    if k >= len(rows):
        return None, None, None, None
    e = ends[k]
    j = bisect.bisect_left(it, e)
    if j >= len(it):
        j = len(it) - 1
    if j > 0 and abs(it[j - 1] - e) < abs(it[j] - e):
        j -= 1
    v, p, tt = idx[j]
    return rows[k][1], p, v, tt

def t6_hit(a, s):
    return [(g, b) for g, b in ranges if a < g + b and g < a + s]

counts = {}
fx = open(os.path.join(out, 'extract.tsv'), 'w', newline='\n')
fc = open(os.path.join(out, 'life_cover.tsv'), 'w', newline='\n')
hdr = 'line\tkind\tframe\tft_n\tpresent\tvideo_f\tvideo_s\tt6\ttext\n'
fx.write(hdr)
fc.write(hdr)
prev = b''
in_cs = False
with open(log, 'rb') as f:
    for ln, line in enumerate(f, 1):
        kind = None
        tag = ''
        dst = fx
        s = line.lstrip()
        if s.startswith(b'ImageWatchDraw:'):
            kind = 'ImageWatchDraw'
        elif s.startswith(b'ImageWatch:'):
            kind = 'ImageWatch'
        elif s.startswith(b'DumpDraw'):
            kind = 'DumpDraw'
        elif s.startswith(b'DumpDispatch'):
            kind = 'DumpDispatch'
        elif s.startswith(b'DumpCS'):
            kind = 'DumpCS'
            if not in_cs:
                n_, p_, v_, t_ = where(ln - 1)
                fx.write('%d\tDumpCS_head\t\t%s\t%s\t%s\t%s\t\t%s\n' % (ln - 1, n_, p_, v_, '' if t_ is None else '%.3f' % t_,
                         prev.decode('latin1').rstrip().replace('\t', ' ')))
        elif s.startswith(b'BufferFillTrace:'):
            d = kv(s)
            h = t6_hit(int(d['addr'], 16), int(d['size'], 16))
            if h:
                kind = 'BufferFillTrace'
                tag = ','.join('0x%x' % g for g, _ in h)
        elif s.startswith(b'ImageLife:'):
            d = kv(s)
            g, b = int(d['guest'], 16), int(d['bytes'])
            if (g, b) in t6:
                kind = 'ImageLife'
                tag = '%sx%s/t%s' % t6[(g, b)]
            elif any(g <= w < g + b for w in WATCH):
                kind = 'ImageLifeCover'
                dst = fc
        in_cs = s.startswith(b'DumpCS')
        prev = line
        if kind is None:
            continue
        counts[kind] = counts.get(kind, 0) + 1
        d = kv(s)
        n_, p_, v_, t_ = where(ln)
        dst.write('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (ln, kind, d.get('frame', ''), n_, p_, v_,
                  '' if t_ is None else '%.3f' % t_, tag, s.decode('latin1').rstrip().replace('\t', ' ')))
fx.close()
fc.close()
json.dump({'rows': len(rows), 'idx': len(idx), 'first_row': rows[0][:2], 'last_row': rows[-1][:2],
           'anchor_first_row_end_s': round(ends[0], 3), 'idx_first_s': it[0], 'idx_last_s': it[-1],
           't6_ranges': ['0x%x+0x%x %sx%s/t%s' % ((g, b) + t6[(g, b)]) for g, b in ranges], 'counts': counts},
          open(os.path.join(out, 'rows.json'), 'w'), indent=1)
print(json.dumps(counts))
print('rows %d idx %d t6 ranges %d' % (len(rows), len(idx), len(ranges)))
