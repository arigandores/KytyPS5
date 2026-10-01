#!/usr/bin/env python3
"""snapidx_s.py - track S, link S3 (HPP-313; ROADMAP "SESSION 122" item 241 (v)(7), (e); S1 RC9, RC12): a read-only index
of the snapshot C:/kyty/s288/snap0 for the scorer sc_s.py.
  shaders - every translation-cache file <stage>_<hash16>_<key16>.bin: stage, hash, whether its first line is the CURRENT
            translator signature (S1 RC12: 707 of 1 181 files carry it, 474 are old signatures that LoadEntry rejects);
  pairs   - every graphics recipe of ShaderCache_PPSA21564/pipelines.bin as (vs hash, ps hash or 0) - the recipe format of
            a2849aec:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp RecordGraphicsRecipe / the precache reader:
            magic "KytyPR1\\n", U32 signature size, signature (translator signature + layout "a:b:c:d:e:f" = sizeof of
            vertex info, pixel info, compute info, rendering state, vertex input state, static parameters), U32 count,
            records: U8 kind; kind 1 = Key(vs) U32 U8(ps_active) [Key(ps) U32] Pod(rendering) Pod(vertex input)
            Pod(static) Info(vs) [Info(ps)]; kind 2 = Key U32 Info(cs); Key = U32 stage, U64 hash, U32, U32, U32 n, n*U32.
Output: C:/kyty/s288/s3/snap0_index.json (sorted, deterministic) and one ASCII summary line.  The snapshot is only read.
    python snapidx_s.py [--out <path>]
"""
import json
import os
import struct
import sys

SNAP = 'C:/kyty/s288/snap0'
SIG = b'KytySC3:699c1e4b7db359067b461e029b913c4b6e78dc90:robust:ftz:cbank\n'
MAGIC = b'KytyPR1\n'


def parse_recipes(data):
    """(signature, count, gfx pairs [(vs, ps)], cs hashes, records parsed) of a pipelines.bin byte string."""
    if data[:8] != MAGIC:
        raise ValueError('bad magic')
    p = 8
    (n,) = struct.unpack_from('<I', data, p)
    p += 4
    sig = data[p:p + n].decode('latin1')
    p += n
    lay = [int(x) for x in sig.rsplit('\n', 1)[1].split(':')]
    vs_info, ps_info, cs_info, rend, vin, stat = lay
    (count,) = struct.unpack_from('<I', data, p)
    p += 4

    def key(p):
        stage, h, _, _, k = struct.unpack_from('<IQIII', data, p)
        return stage, h, p + 24 + 4 * k
    pairs = []
    cs = []
    done = 0
    for _ in range(count):
        kind = data[p]
        p += 1
        if kind == 1:
            _, vh, p = key(p)
            p += 4
            act = data[p]
            p += 1
            ph = 0
            if act:
                _, ph, p = key(p)
                p += 4
            p += rend + vin + stat + vs_info + (ps_info if act else 0)
            pairs.append((vh, ph))
        elif kind == 2:
            _, ch, p = key(p)
            p += 4 + cs_info
            cs.append(ch)
        else:
            raise ValueError('bad kind %d at record %d' % (kind, done))
        if p > len(data):
            raise ValueError('record %d runs past the end' % done)
        done += 1
    return sig, count, pairs, cs, done, p == len(data)


def build(snap=SNAP):
    cdir = os.path.join(snap, 'ShaderCache_PPSA21564')
    shaders = []
    for name in sorted(os.listdir(cdir)):
        if name == 'pipelines.bin' or not name.endswith('.bin'):
            continue
        parts = name[:-4].split('_')
        if len(parts) != 3:
            continue
        with open(os.path.join(cdir, name), 'rb') as f:
            head = f.read(len(SIG))
        shaders.append(dict(stage=parts[0], hash=parts[1], key=parts[2], current=head == SIG))
    data = open(os.path.join(cdir, 'pipelines.bin'), 'rb').read()
    sig, count, pairs, cs, done, exact = parse_recipes(data)
    return dict(snap=snap, signature_current=SIG.decode().strip(), recipes_signature=sig.replace('\n', '|'),
                recipes=count, recipes_parsed=done, recipes_exact_end=exact,
                pairs=sorted('%016x/%016x' % (a, b) for a, b in set(pairs)), gfx_records=len(pairs),
                cs_records=len(cs), shaders=shaders)


def main(argv=None):
    a = argv if argv is not None else sys.argv[1:]
    out = a[a.index('--out') + 1] if '--out' in a else 'C:/kyty/s288/s3/snap0_index.json'
    ix = build()
    text = json.dumps(ix, indent=0, sort_keys=True)
    with open(out, 'wb') as f:
        f.write(text.encode('ascii'))
    cur = sum(1 for s in ix['shaders'] if s['current'])
    print('snap0 index: files %d (current signature %d, hashes current %d), recipes %d parsed %d exact end %s, gfx %d '
          '(pairs %d) cs %d -> %s' % (len(ix['shaders']), cur, len(set(s['hash'] for s in ix['shaders'] if s['current'])),
                                      ix['recipes'], ix['recipes_parsed'], ix['recipes_exact_end'], ix['gfx_records'],
                                      len(ix['pairs']), ix['cs_records'], out))
    return 0 if ix['recipes_parsed'] == ix['recipes'] and ix['recipes_exact_end'] else 1


if __name__ == '__main__':
    sys.exit(main())
