import os, sys, struct, hashlib, re, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
# T109: graphics recipes of the pipeline catalogue (READ ONLY) - how many record depth_clip_enable = 0
# (guest PA_CL_CLIP_CNTL ZCLIP_NEAR_DISABLE or ZCLIP_FAR_DISABLE set, dd73d04d pipelineCache.cpp:5611,
# hardwareContext.h:336) and with which depth attachment format. Record format: recipes143.py (s143 audit),
# PipelineStaticParameters packed 125 bytes, depth_clip_enable at offset 1 (dd73d04d pipelineCache.h:52);
# PipelineRenderingState: 8 x u32 colour formats, u32 depth_format at 32, u32 stencil_format at 36, u32 color_count at 40.
MAGIC = b'KytyPR1\n'
VKF = {0: 'undef', 124: 'D16_UNORM', 125: 'X8_D24', 126: 'D32_SFLOAT', 127: 'S8', 128: 'D16S8', 129: 'D24S8', 130: 'D32S8'}
FILES = sys.argv[1:] or [
    'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19/pipelines.bin',
    'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/pipelines.bin']


def key(d, p):
    stage, h, udc, cs, n = struct.unpack_from('<IQIII', d, p)
    p += 24
    if n > 4096:
        raise ValueError('key n %d' % n)
    return (stage, h), p + 4 * n


for path in FILES:
    if not os.path.isfile(path):
        print('ABSENT', path); continue
    d = open(path, 'rb').read()
    print('=== FILE', path, 'size', len(d), 'sha256', hashlib.sha256(d).hexdigest())
    if d[:8] != MAGIC:
        print('  bad magic'); continue
    (ss,) = struct.unpack_from('<I', d, 8)
    sig = d[12:12 + ss]
    m = re.search(rb'(\d+):(\d+):(\d+):(\d+):(\d+):(\d+)$', sig)
    VS, PS, CS, REN, VIN, STA = (int(x) for x in m.groups())
    print('  layout', VS, PS, CS, REN, VIN, STA, 'signature', sig[:40])
    assert STA == 125, STA
    p = 12 + ss
    (count,) = struct.unpack_from('<I', d, p); p += 4
    g = c = 0
    by = collections.Counter()
    clipoff_ps = collections.Counter()
    n1t1 = collections.Counter()
    err = None
    try:
        for i in range(count):
            kind = d[p]; p += 1
            if kind == 1:
                vk, p = key(d, p)
                p += 4
                ps_active = d[p] != 0; p += 1
                pk = None
                if ps_active:
                    pk, p = key(d, p); p += 4
                ren = d[p:p + REN]; p += REN + VIN
                st = d[p:p + STA]; p += STA + VS + (PS if ps_active else 0)
                depth_fmt = struct.unpack_from('<I', ren, 32)[0]
                clip = st[1]
                n1 = st[0]
                by[(clip, VKF.get(depth_fmt, str(depth_fmt)))] += 1
                n1t1[(n1, clip)] += 1
                if clip == 0:
                    clipoff_ps[('%016x' % vk[1], ('%016x' % pk[1]) if pk else '-', VKF.get(depth_fmt, str(depth_fmt)))] += 1
                g += 1
            elif kind == 2:
                ck, p = key(d, p); p += 4 + CS; c += 1
            else:
                err = 'bad kind %d at %d' % (kind, i); break
    except Exception as e:
        err = repr(e)
    print('  count', count, 'graphics', g, 'compute', c, 'at_end', p == len(d), 'err', err)
    tot0 = sum(v for (cl, f), v in by.items() if cl == 0)
    print('  graphics recipes with depth_clip_enable=0:', tot0, 'of', g)
    for (cl, f), v in sorted(by.items()):
        print('    depth_clip_enable=%d depth_format=%-10s n=%d' % (cl, f, v))
    for (n1, cl), v in sorted(n1t1.items()):
        print('    negative_one_to_one=%d depth_clip_enable=%d n=%d' % (n1, cl, v))
    print('  distinct (vs, ps, depth_format) with clip off:', len(clipoff_ps))
    for k, v in clipoff_ps.most_common(15):
        print('    ', k, v)
print('DONE')
