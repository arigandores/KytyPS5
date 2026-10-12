"""Track M, M2b (HPP-839, ROADMAP s122 item 756(v)(2)(iii)): frames of large sceFont text in an FS15 log.

The FS15 log has no function names for sceFont (PRINT_NAME is off); sceFontSetScalePixel and sceFontSetupRenderScalePixel
print the same line "\\t handle = 0x..., w = <w>, h = <h>" (libFont.cpp). Every such line with w >= <min> or h >= <min> is
listed with the guest frame around it: the n of the last "FrameTrace: n=" line before it and of the first after it, the
last "StartLevel <name>" GuestOut line before it, the font size of the open before it ("size = <bytes>" of
sceFontOpenFontMemory) and the first glyph render after it (code, x, y of sceFontRenderCharGlyphImageHorizontal).

Usage: frames_t231.py <log> <out.tsv> [min=200]
Output TSV: line, w, h, frame_before, frame_after, level, font_size, first_render; last line "frames=<sorted unique
frame_after>" and ALL OK (>= 1 line) or FAIL.
"""
import re
import sys

PAT_WH = re.compile(rb'^\t handle = 0x([0-9a-f]+), w = ([0-9.]+), h = ([0-9.]+)\r?$')
PAT_FT = re.compile(rb'^FrameTrace: n=(\d+) ')
PAT_LV = re.compile(rb'StartLevel (\S+)')
PAT_OPEN = re.compile(rb'^\t library = 0x[0-9a-f]+, data = 0x[0-9a-f]+, size = (\d+), font_set')
PAT_RENDER = re.compile(rb'^\t handle = 0x([0-9a-f]+), code = 0x([0-9a-f]+), surf = 0x[0-9a-f]+, x = ([0-9.-]+), '
                        rb'y = ([0-9.-]+), result')


def main():
    log, out = sys.argv[1], sys.argv[2]
    lim = float(sys.argv[3]) if len(sys.argv) > 3 else 200.0
    rows = []
    pending = []
    last_frame = None
    level = '-'
    font_size = '-'
    with open(log, 'rb') as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip(b'\n')
            m = PAT_FT.match(line)
            if m:
                fr = int(m.group(1))
                for r in pending:
                    r['after'] = fr
                pending = []
                last_frame = fr
                continue
            m = PAT_LV.search(line)
            if m and line.startswith(b'GuestOut:'):
                level = m.group(1).decode()
                continue
            m = PAT_OPEN.match(line)
            if m:
                font_size = m.group(1).decode()
                continue
            m = PAT_RENDER.match(line)
            if m:
                for r in rows:
                    if r['render'] == '-' and r['handle'] == m.group(1).decode():
                        r['render'] = 'code=%s x=%s y=%s' % (m.group(2).decode(), m.group(3).decode(), m.group(4).decode())
                continue
            m = PAT_WH.match(line)
            if m:
                w, h = float(m.group(2)), float(m.group(3))
                if w >= lim or h >= lim:
                    r = {'line': n, 'handle': m.group(1).decode(), 'w': w, 'h': h, 'before': last_frame, 'after': None,
                         'level': level, 'font': font_size, 'render': '-'}
                    rows.append(r)
                    pending.append(r)
    frames = sorted({r['after'] for r in rows if r['after'] is not None})
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('line\tw\th\tframe_before\tframe_after\tlevel\tfont_size\tfirst_render\n')
        for r in rows:
            f.write('%d\t%g\t%g\t%s\t%s\t%s\t%s\t%s\n' % (r['line'], r['w'], r['h'], r['before'], r['after'], r['level'],
                                                         r['font'], r['render']))
        f.write('frames=%s\n' % ','.join(str(x) for x in frames))
        f.write('ALL OK\n' if rows else 'FAIL (no line)\n')
    print('lines=%d frames=%s' % (len(rows), ','.join(str(x) for x in frames)))
    print('ALL OK' if rows else 'FAIL (no line)')


if __name__ == '__main__':
    main()
