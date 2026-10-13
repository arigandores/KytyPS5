import os, sys, hashlib, collections, re
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
# One streaming pass over a few M3 logs (binary, line by line). Counts lines carrying the
# substrings below and keeps the first examples of each.
LOGS = sys.argv[1:] or ['C:/kyty/m657/m3a/log_m3_sg_v_r1.txt',
                        'C:/kyty/m657/m3a/log_m3_hb_f.txt',
                        'C:/kyty/m657/m3a/log_m3_mg_v.txt']
PATS = [b'ClearDecodeFail', b'BufferFillTrace', b'clr_ok', b'clr_decode', b'T# MIN_LOD',
        b'image_view_min_lod', b'epthClamp', b'epth_clamp', b'epthClip', b'MipDefer',
        b'minLod', b'06456', b'ImgMinLod', b'img_minlod', b'min_lod', b'FrameStats',
        b'ClearConsumed', b'VK_EXT_depth_clip', b'DepthClip', b'ZCLIP', b'clip_ext',
        b'Vulkan VK_EXT', b'texel', b'NativeStorage', b'B2R', b'b2r', b'SameBacking',
        b'InvalidateMemoryFromGPU', b'Expand']
KEEP = 4
for path in LOGS:
    cnt = collections.Counter()
    ex = collections.defaultdict(list)
    nlines = 0
    with open(path, 'rb') as f:
        for line in f:
            nlines += 1
            for p in PATS:
                if p in line:
                    cnt[p] += 1
                    if len(ex[p]) < KEEP:
                        ex[p].append(line[:400].decode('utf-8', 'replace').rstrip())
    st = os.stat(path)
    print('=== LOG', path, 'size', st.st_size, 'lines', nlines)
    for p in PATS:
        print('  count', p.decode(), cnt[p])
        for e in ex[p]:
            print('     ex:', e)
print('DONE')
