# F32a (HPP-733): per-log occurrences of K1-K4 marker signatures in the delta sweep (reads the sweep_f32a segments).
# Usage: python ana_f32a.py [out_tsv]   -> one row per (marker, unique log): marker, path:first_line, count, build, levels, group
import os, sys, json, pickle, hashlib, re, collections

OUT = os.environ.get('F32A_OUT', 'C:/kyty/f287/f32a')
SEG = OUT + '/seg'
LOCK = os.environ.get('F32A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F32A_STOP', 'C:/kyty/f287/STOP')
TAB = chr(9)
NL = chr(10)
SEG_BYTES = int(os.environ.get('F32A_SEG_BYTES', 256 << 20))
# marker name -> regex over the normalized signature (bytes)
MARKERS = [
    ('fatal', rb'^--- Fatal Error ---'),
    ('error', rb'^--- Error ---'),
    ('cond', rb'Error: condition|Assertion failed'),
    ('b25_assert', rb'too many objects/batches'),
    ('host_exc', rb'Unhandled host exception'),
    ('unh_exc', rb'^Unhandled exception'),
    ('hang', rb'GpuHangAbort'),
    ('devlost', rb'ErrorDeviceLost'),
    ('vk_e', rb'^\[Vulkan\]\[E\]'),
    ('bvh_trip', rb'^BvhLoopCapTrip:'),
    ('op_ni', rb'^OPCODE_NI'),
    ('stub_called', rb'^Unresolved import stub called'),
    ('stubbed', rb'Stubbed function'),
    ('kread', rb'^KernelRead: direct read failed'),
    ('audio_q', rb'^AudioOut: SDL_QueueAudio failed'),
    ('audio_open', rb'^AudioOut: SDL_OpenAudioDevice failed'),
    ('ooc', rb'eErrorOutOfDateKHR'),
    ('cfg_fail', rb'shader CFG build failed'),
    ('eval_fail', rb'shader resource evaluation failed'),
]
MRE = [(n, re.compile(p)) for n, p in MARKERS]


def gate():
    if os.path.exists(STOP):
        sys.exit(4)
    if os.path.exists(LOCK):
        sys.exit(3)


def main():
    gate()
    out = sys.argv[1] if len(sys.argv) > 1 else OUT + '/markers_f32a.tsv'
    recs = json.load(open(OUT + '/agg_f32a.json', encoding='utf-8'))
    rows = []
    tot = collections.Counter()
    for r in recs:
        if r['dup_of'] or r['in_f0']:
            continue
        p = r['path']
        md = hashlib.md5(p.encode('utf-8')).hexdigest()
        whole = r['kind'] == 'xz' or r['size'] <= SEG_BYTES
        nseg = 1 if whole else (r['size'] + SEG_BYTES - 1) // SEG_BYTES
        off = 0
        hit = {}
        for i in range(nseg):
            s = pickle.load(open('%s/%s_%d.pkl' % (SEG, md, i), 'rb'))
            for k, v in s['sigs'].items():
                for n, rx in MRE:
                    if rx.search(k):
                        e = hit.get((n, k))
                        if e is None:
                            hit[(n, k)] = [v[0], v[1] + off, v[2]]
                        else:
                            e[0] += v[0]
            off += s['lines']
        for (n, k), v in sorted(hit.items(), key=lambda x: (x[0][0], x[1][1])):
            tot[n] += 1
            rows.append([n, '%s:%d' % (p, v[1]), str(v[0]), r['build'], ','.join(r['levels'][:3]) or '-', r['group'],
                         k.decode('latin1')[:160].replace(TAB, ' '), v[2].decode('utf-8', 'replace')[:240].replace(TAB, ' ')])
    with open(out, 'w', encoding='utf-8', newline=NL) as o:
        o.write(TAB.join(['marker', 'path:first_line', 'count', 'build', 'levels', 'group', 'signature', 'example']) + NL)
        for x in rows:
            o.write(TAB.join(x) + NL)
    for n, _ in MARKERS:
        print('marker', n, 'logs', tot[n])


if __name__ == '__main__':
    main()
