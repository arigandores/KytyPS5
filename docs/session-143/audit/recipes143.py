# recipes143.py - Session Auditor, s143 step 3 (HPP-300), ROADMAP s122 item 249 (v): provenance of the startup graphics
# pipeline with a dual-source blend factor. Parses the pipeline recipe files of the emulator (format by the code of the
# installed build, 4fc501f4:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp RecipeWriter / RecordGraphicsRecipe /
# WriteRecipes): magic "KytyPR1\n", u32 signature size, signature, u32 count, records.
#   kind 1 (graphics): key vs, u32 vs_index, u8 ps_active, [key ps, u32 ps_index], rendering, vertex_input, static_params,
#                      vs_info, [ps_info];   kind 2 (compute): key, u32 index, cs_info
#   key: u32 stage, u64 hash, u32 user_data_count, u32 code_size, u32 n, n * u32
# The struct sizes come from the tail of the signature (RecipeLayoutSignature: vs:ps:cs:rendering:vertex_input:static).
# READ ONLY. Usage: python recipes143.py <out.json> <name>=<path> ...
import sys, struct, hashlib, json, re, os

MAGIC = b'KytyPR1\n'
DUAL = {0x0f: 'kSrc1Color?', 0x10: 'kOneMinusSrc1Color?', 0x11: 'kSrc1Alpha', 0x12: 'kOneMinusSrc1Alpha'}
# PipelineStaticParameters (packed, 125 bytes; 4fc501f4:pipelineCache.h:44): offsets of the per-attachment arrays (8 each)
O_SRC, O_FCN, O_DST, O_ASRC, O_AFCN, O_ADST, O_SEP, O_EN = 61, 69, 77, 85, 93, 101, 109, 117


def key(d, p):
    stage, h, udc, cs, n = struct.unpack_from('<IQIII', d, p)
    p += 24
    if n > 4096:
        raise ValueError('key n %d' % n)
    return (stage, h, udc, cs, n), p + 4 * n


def parse(path):
    d = open(path, 'rb').read()
    R = {'path': path, 'size': len(d), 'sha256': hashlib.sha256(d).hexdigest(), 'mtime_ns': os.stat(path).st_mtime_ns}
    if d[:8] != MAGIC:
        R['error'] = 'bad magic'
        return R, []
    (ss,) = struct.unpack_from('<I', d, 8)
    sig = d[12:12 + ss]
    R['signature'] = sig.decode('ascii', 'replace').replace('\n', '|')
    m = re.search(rb'(\d+):(\d+):(\d+):(\d+):(\d+):(\d+)$', sig)
    VS, PS, CS, REN, VIN, STA = (int(x) for x in m.groups())
    R['layout'] = [VS, PS, CS, REN, VIN, STA]
    p = 12 + ss
    (count,) = struct.unpack_from('<I', d, p)
    p += 4
    R['count'] = count
    R['header_bytes'] = p
    recs = []  # (index, kind, begin, end, sha1)
    flagged = []
    g = c = 0
    try:
        for i in range(count):
            b = p
            kind = d[p]
            p += 1
            if kind == 1:
                vk, p = key(d, p)
                (vi,) = struct.unpack_from('<I', d, p)
                p += 4
                ps_active = d[p] != 0
                p += 1
                pk, pi = None, None
                if ps_active:
                    pk, p = key(d, p)
                    (pi,) = struct.unpack_from('<I', d, p)
                    p += 4
                ren = d[p:p + REN]
                p += REN + VIN
                st = d[p:p + STA]
                p += STA + VS + (PS if ps_active else 0)
                fm = struct.unpack_from('<8I', ren, 0)
                cc = struct.unpack_from('<I', ren, 40)[0]
                hit = []
                for a in range(8):
                    f = [st[O_SRC + a], st[O_DST + a]] + ([st[O_ASRC + a], st[O_ADST + a]] if st[O_SEP + a] else [])
                    if any(x in DUAL for x in f):
                        hit.append(a)
                if hit:
                    flagged.append({'index': i, 'begin': b, 'end': p, 'graphics_before': g, 'compute_before': c,
                                    'vs_hash': '%016x' % vk[1], 'vs_index': vi,
                                    'ps_hash': ('%016x' % pk[1]) if pk else None, 'ps_index': pi,
                                    'color_count': cc, 'formats': list(fm), 'attachments_hit': hit,
                                    'hit_within_color_count': [a for a in hit if a < cc],
                                    'srcblend': list(st[O_SRC:O_SRC + 8]), 'comb_fcn': list(st[O_FCN:O_FCN + 8]),
                                    'destblend': list(st[O_DST:O_DST + 8]), 'alpha_src': list(st[O_ASRC:O_ASRC + 8]),
                                    'alpha_dest': list(st[O_ADST:O_ADST + 8]), 'separate': list(st[O_SEP:O_SEP + 8]),
                                    'blend_enable': list(st[O_EN:O_EN + 8]),
                                    'record_sha1': hashlib.sha1(d[b:p]).hexdigest()})
                g += 1
            elif kind == 2:
                ck, p = key(d, p)
                p += 4 + CS
                c += 1
            else:
                R['error'] = 'bad kind %d at record %d offset %d' % (kind, i, b)
                break
            if p > len(d):
                R['error'] = 'truncated at record %d' % i
                break
            recs.append((i, kind, b, p, hashlib.sha1(d[b:p]).hexdigest()))
    except (struct.error, ValueError, IndexError) as e:
        R['error'] = 'parse stopped: %r' % (e,)
    R['parsed'] = len(recs)
    R['graphics'] = g
    R['compute'] = c
    R['end_offset'] = p
    R['at_end'] = (p == len(d))
    R['flagged'] = flagged
    return R, recs


def main():
    outp = sys.argv[1]
    files = [a.split('=', 1) for a in sys.argv[2:]]
    res = {}
    allrecs = {}
    for name, path in files:
        if not os.path.isfile(path):
            res[name] = {'path': path, 'error': 'absent'}
            continue
        R, recs = parse(path)
        res[name] = R
        allrecs[name] = recs
        print('%s: %s size %d sha256 %s count %s parsed %s (graphics %s compute %s) at_end %s %s' % (
            name, path, R['size'], R['sha256'][:16], R.get('count'), R.get('parsed'), R.get('graphics'), R.get('compute'),
            R.get('at_end'), R.get('error', '')))
        print('   layout', R.get('layout'), 'signature', R.get('signature'))
        for f in R.get('flagged', []):
            print('   DUAL-SOURCE recipe index %d bytes [%d, %d) graphics_before %d compute_before %d vs %s#%d ps %s#%s '
                  'color_count %d hit %s (within count %s) src %s dst %s fcn %s sep %s asrc %s adst %s enable %s fmt %s sha1 %s' % (
                      f['index'], f['begin'], f['end'], f['graphics_before'], f['compute_before'], f['vs_hash'], f['vs_index'],
                      f['ps_hash'], f['ps_index'], f['color_count'], f['attachments_hit'], f['hit_within_color_count'],
                      f['srcblend'], f['destblend'], f['comb_fcn'], f['separate'], f['alpha_src'], f['alpha_dest'],
                      f['blend_enable'], f['formats'], f['record_sha1'][:12]))
    # prefix relations between the files (records compared by sha1 in order)
    names = [n for n, _ in files if n in allrecs]
    rel = {}
    for a in names:
        for b in names:
            if a == b:
                continue
            ra, rb = allrecs[a], allrecs[b]
            k = 0
            while k < len(ra) and k < len(rb) and ra[k][4] == rb[k][4]:
                k += 1
            sb = set(x[4] for x in rb)
            rel['%s in %s' % (a, b)] = {'common_prefix_records': k, 'records_a': len(ra), 'records_b': len(rb),
                                        'a_records_present_in_b': sum(1 for x in ra if x[4] in sb)}
    res['_relations'] = rel
    for k, v in rel.items():
        print('REL %s: common prefix %d of %d / %d; present anywhere %d' % (
            k, v['common_prefix_records'], v['records_a'], v['records_b'], v['a_records_present_in_b']))
    # boundaries: the byte end of every record of the first file, to map a manifest size to a record count
    if names:
        res['_ends_' + names[0]] = [x[3] for x in allrecs[names[0]]]
    json.dump(res, open(outp, 'w', encoding='ascii'), ensure_ascii=True)
    print('ALL DONE')


if __name__ == '__main__':
    main()
