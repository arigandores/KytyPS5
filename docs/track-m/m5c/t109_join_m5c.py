"""M5c (HPP-847), T109 2aaf0c9ba, ROADMAP p.767(e): join the pipeline recipe catalogue with the PS hash and the depth format.
Read-only. Record layout = recipes_m5a.py (M5a, KytyPS5 4c1327bc): graphics record = kind 1, VS key, u32, ps_active byte,
[PS key, u32], PipelineRenderingState (depth_format u32 at +32), vertex input, PipelineStaticParameters (125 bytes), VS/PS blobs.
Key = (stage u32, hash u64, udc u32, cs u32, n u32, n x u32).
Prints: (1) per file: graphics recipes, distinct PS hashes, and how many of them are names of eboot_text programs
(namespace check of the join key); (2) recipes per depth format whose PS exports Z (EXP MRTZ en bit0; list of 8 programs
from rc_mrtz_m5b.out.txt, M5b bc58c115); (3) whether PipelineStaticParameters / PipelineRenderingState carry any depth-bias
field (source text at --commit), and the dynamic-state list of pipeline creation (shaders.cpp).
Usage: python t109_join_m5c.py [--commit f7a5e258] > t109_join_m5c.out.txt"""
import os, sys, struct, hashlib, re, collections, subprocess
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
COMMIT = sys.argv[sys.argv.index('--commit') + 1] if '--commit' in sys.argv else 'f7a5e258'
MAGIC = b'KytyPR1\n'
VKF = {0: 'undef', 124: 'D16_UNORM', 125: 'X8_D24', 126: 'D32_SFLOAT', 127: 'S8', 128: 'D16S8', 129: 'D24S8', 130: 'D32S8'}
D32 = {'D32_SFLOAT', 'D32S8'}
FILES = ['C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19/pipelines.bin',
         'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19_mw1_33/pipelines.bin',
         'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/pipelines.bin']
ZPROGS = ['5514e10f1a60df83', '6d7e77c38d86c706', '74f85f6718ab66e0', 'be4c35a2031fd3f4', 'c67734666ad63e20',
          'e4774eac21e50915', 'e5e75159543da3d1', 'f25acd918dbac2b5']
EBOOT_TEXT = 'C:/kyty/f287/f23a/eboot_text/'
names = set(f[:16] for f in os.listdir(EBOOT_TEXT) if f.endswith('.bin'))
print('commit', COMMIT, 'eboot_text programs', len(names))


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
    p = 12 + ss
    (count,) = struct.unpack_from('<I', d, p); p += 4
    g = 0
    ps_set = set(); vs_set = set()
    zrec = collections.Counter(); zrec_clip = collections.Counter()
    all_fmt = collections.Counter()
    zpairs = collections.Counter()
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
                fmt = VKF.get(struct.unpack_from('<I', ren, 32)[0], '?')
                all_fmt[fmt] += 1
                g += 1
                vs_set.add('%016x' % vk[1])
                if pk:
                    ph = '%016x' % pk[1]
                    ps_set.add(ph)
                    if ph in ZPROGS:
                        zrec[(ph, fmt)] += 1
                        zrec_clip[(ph, st[1])] += 1
                        zpairs[(ph, '%016x' % vk[1], fmt)] += 1
            elif kind == 2:
                ck, p = key(d, p); p += 4 + CS
            else:
                err = 'bad kind %d at %d' % (kind, i); break
    except Exception as ex:
        err = repr(ex)
    print('  count', count, 'graphics', g, 'at_end', p == len(d), 'err', err)
    print('  depth formats of all graphics recipes', dict(sorted(all_fmt.items())))
    print('  distinct PS hashes', len(ps_set), 'of them eboot_text names', len(ps_set & names),
          '| distinct VS hashes', len(vs_set), 'of them eboot_text names', len(vs_set & names))
    tz = sum(zrec.values())
    print('  recipes whose PS exports Z:', tz, 'of them D32:', sum(v for (h, f), v in zrec.items() if f in D32))
    for h in ZPROGS:
        row = {f: v for (hh, f), v in zrec.items() if hh == h}
        clip = {c: v for (hh, c), v in zrec_clip.items() if hh == h}
        print('    PS %s recipes %d by depth format %s depth_clip_enable %s' % (h, sum(row.values()), row, clip))
    for (h, v, f), n in sorted(zpairs.items()):
        print('      pair ps=%s vs=%s depth=%s n=%d' % (h, v, f, n))


def show(path):
    return subprocess.run([GIT, '-C', REPO, 'show', COMMIT + ':' + path], capture_output=True, check=True).stdout.decode('utf-8')


h = show('src/graphics/host_gpu/renderer/pipeline/pipelineCache.h')
for sname in ('PipelineStaticParameters', 'PipelineRenderingState'):
    a = h.index('struct ' + sname + ' {')
    b = h.index(chr(10) + '};', a)
    body = h[a:b]
    decl = [ln.strip() for ln in body.split(chr(10))[1:] if ln.strip().endswith(';') and '(' not in ln]
    print('struct', sname, 'member declarations', len(decl))
    for ln in decl:
        print('   ', ln)
    print('  declarations containing bias/offset/poly:', [ln for ln in decl if re.search('bias|offset|poly', ln, re.I)])
s = show('src/graphics/host_gpu/renderer/pipeline/shaders.cpp')
dyn = re.findall(r'vk::DynamicState::(e\w+)', s)
print('shaders.cpp DynamicState names', sorted(set(dyn)))
print('  eDepthBias and eDepthBiasEnable dynamic:', 'eDepthBias' in dyn and 'eDepthBiasEnable' in dyn)
print('DONE')
