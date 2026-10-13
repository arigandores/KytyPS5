import os, sys, re, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
# One streaming pass per log: sums of per-frame counters of FrameTrace-draw / FrameTrace-x lines that touch
# the themes (deferred-mip clamp views T021, DWORD-fill clears T313/T179), plus counts of fatal / trace markers.
LOGS = sys.argv[1:] or ['C:/kyty/m657/m3a/log_m3_sg_v_r1.txt',
                        'C:/kyty/m657/m3a/log_m3_hb_f.txt',
                        'C:/kyty/m657/m3a/log_m3_mg_v.txt']
DRAW_KEYS = [b'img_up', b'img_defer', b'img_defer_kb', b'img_minlod']
X_KEYS = [b'clr_ok', b'clr_ok_kb', b'clr_ambig', b'clr_none', b'clr_decode', b'clr_over', b'clr_taken_img',
          b'clr_taken_meta']
MARKS = [b'invalid image view', b'Fatal Error', b'ImgUploadWhy', b'gpu-invalidate', b'MipDefer',
         b'TextureCache: invalid', b'texture minimum LOD', b'unsupported texture mip view']
rx = {k: re.compile(rb' ' + k + rb'=(\d+)') for k in DRAW_KEYS + X_KEYS}
for path in LOGS:
    s = collections.Counter(); frames_draw = frames_x = 0
    nz = collections.Counter()
    marks = collections.Counter(); ex = collections.defaultdict(list)
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace-draw:'):
                frames_draw += 1
                for k in DRAW_KEYS:
                    m = rx[k].search(line)
                    if m:
                        v = int(m.group(1)); s[k] += v; nz[k] += v != 0
            elif line.startswith(b'FrameTrace-x:'):
                frames_x += 1
                for k in X_KEYS:
                    m = rx[k].search(line)
                    if m:
                        v = int(m.group(1)); s[k] += v; nz[k] += v != 0
            else:
                for mk in MARKS:
                    if mk in line:
                        marks[mk] += 1
                        if len(ex[mk]) < 3:
                            ex[mk].append(line[:300].decode('utf-8', 'replace').rstrip())
    print('=== LOG', path, 'size', os.stat(path).st_size, 'FrameTrace-draw', frames_draw, 'FrameTrace-x', frames_x)
    for k in DRAW_KEYS + X_KEYS:
        print('  sum %-15s %12d  frames_nonzero %d' % (k.decode(), s[k], nz[k]))
    for mk in MARKS:
        print('  mark %-30s %d' % (mk.decode(), marks[mk]))
        for e in ex[mk]:
            print('     ex:', e)
print('DONE')
