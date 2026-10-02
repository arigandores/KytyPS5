"""Track S, S7 (HPP-319), S0 section 8(8) / ROADMAP p.241(i): which recipes the startup precache skips and why.

Simulates PipelineCache::StartPrecache of the binary that ran on snap0 (4fc501f4 = 9235a7ac,
pipelineCache.cpp:6211-6401, Resolve :4488-4521, ShaderTranslationCache::Load / PathOf) on a
recipe file and a translation-cache directory, starting from an empty program cache:
  R_NOFILE   translation file of a stored key absent              -> Resolve false (:6262 / :6350)
  R_STALE    file present, signature line != expected              -> Load false -> Resolve false
  R_INDEX    permutation index >= permutations of the file         -> Resolve false (:4514)
  R_DUP_GFX  graphics key (rendering, vertex_input, static_params, vs id, ps id) already queued (:6276)
  R_DUP_CS   compute program id already queued (:6358)
The pipeline key equality is approximated by raw bytes of rendering / vertex_input / static_params
(operator== of the structs may ignore some bytes - printed as a caveat, checked by the count).
Permutation counts come from the S7 tests binary (KYTY_RECOMPILE probe '999', ReadFileUnchecked).
READ ONLY on the inputs. ASCII output only.
Usage: python recipes_s7.py <name> <pipelines.bin> <translation dir> <expected signature> <out prefix>
"""
import collections
import hashlib
import json
import os
import re
import struct
import subprocess
import sys

import xxhash

BIN = 'C:/kyty/s288/s7/bin/shader_cfg_tests_949f8e51.exe'
MAGIC = b'KytyPR1\n'
STAGE_NAME = {1: 'vs', 2: 'ps'}  # PathOf: Vertex -> vs, Pixel -> ps, anything else -> cs


def stored_key(d, p):
    stage, h, udc, cs, n = struct.unpack_from('<IQIII', d, p)
    p += 24
    if n > 4096:
        raise ValueError('key n %d' % n)
    state = d[p:p + 4 * n]
    return (stage, h, udc, cs, state), p + 4 * n


def path_name(k):
    stage, h, udc, cs, state = k
    x = xxhash.xxh3_64()
    x.update(struct.pack('<I', udc))
    x.update(struct.pack('<I', cs))
    if state:
        x.update(state)
    return '%s_%016x_%016x.bin' % (STAGE_NAME.get(stage, 'cs'), h, x.intdigest())


def parse(path):
    d = open(path, 'rb').read()
    if d[:8] != MAGIC:
        raise SystemExit('bad magic ' + path)
    (ss,) = struct.unpack_from('<I', d, 8)
    sig = d[12:12 + ss]
    m = re.search(rb'(\d+):(\d+):(\d+):(\d+):(\d+):(\d+)$', sig)
    VS, PS, CS, REN, VIN, STA = (int(x) for x in m.groups())
    p = 12 + ss
    (count,) = struct.unpack_from('<I', d, p)
    p += 4
    recs = []
    for i in range(count):
        b = p
        kind = d[p]
        p += 1
        if kind == 1:
            vk, p = stored_key(d, p)
            (vi,) = struct.unpack_from('<I', d, p)
            p += 4
            ps_active = d[p] != 0
            p += 1
            pk, pi = None, None
            if ps_active:
                pk, p = stored_key(d, p)
                (pi,) = struct.unpack_from('<I', d, p)
                p += 4
            ren = d[p:p + REN]
            p += REN
            vin = d[p:p + VIN]
            p += VIN
            sta = d[p:p + STA]
            p += STA + VS + (PS if ps_active else 0)
            recs.append({'i': i, 'kind': 1, 'vk': vk, 'vi': vi, 'pk': pk, 'pi': pi, 'ren': ren, 'vin': vin, 'sta': sta,
                         'sha1': hashlib.sha1(d[b:p]).hexdigest()})
        elif kind == 2:
            ck, p = stored_key(d, p)
            (ci,) = struct.unpack_from('<I', d, p)
            p += 4 + CS
            recs.append({'i': i, 'kind': 2, 'ck': ck, 'ci': ci, 'sha1': hashlib.sha1(d[b:p]).hexdigest()})
        else:
            raise SystemExit('bad kind %d at %d' % (kind, i))
    return {'signature': sig.decode('ascii', 'replace').replace('\n', '|'), 'count': count, 'at_end': p == len(d),
            'sha256': hashlib.sha256(d).hexdigest(), 'size': len(d)}, recs


def file_info(dirpath, name, expected, cache):
    if name in cache:
        return cache[name]
    path = dirpath + '/' + name
    if not os.path.isfile(path):
        r = ('R_NOFILE', None)
    else:
        with open(path, 'rb') as f:
            sig = f.read(512).split(b'\n', 1)[0].decode('latin1')
        if sig != expected:
            r = ('R_STALE', sig)
        else:
            dummy = 'C:/kyty/s288/s7/work/probe/empty.bin'
            p = subprocess.run([BIN], env=dict(os.environ, KYTY_RECOMPILE='%s;%s;%s;999' % (
                dummy, path, 'C:/kyty/s288/s7/work/probe/rcp.spv')), capture_output=True)
            m = re.search(rb'permutation 999 of (\d+)', p.stderr)
            r = ('OK', int(m.group(1)) if m else None)
    cache[name] = r
    return r


def main():
    name, pipes, tdir, expected, outp = sys.argv[1:6]
    head, recs = parse(pipes)
    print('%s: recipes %s count %d at_end %s sha256 %s' % (name, pipes, head['count'], head['at_end'], head['sha256']))
    print('  recipe signature', head['signature'])
    cache = {}
    loaded = set()        # program keys already in the program cache
    perms = {}
    gfx_keys = {}
    cs_ids = {}
    out = []
    cnt = collections.Counter()

    def resolve(k, idx):
        nm = path_name(k)
        if k not in loaded:
            st, n = file_info(tdir, nm, expected, cache)
            if st != 'OK' or not n:
                return st if st != 'OK' else 'R_NOFILE', nm
            loaded.add(k)
            perms[k] = n
        if idx >= perms[k]:
            return 'R_INDEX', nm
        return 'OK', nm

    for r in recs:
        if r['kind'] == 1:
            s1, n1 = resolve(r['vk'], r['vi'])
            s2, n2 = ('OK', None)
            if s1 == 'OK' and r['pk'] is not None:
                s2, n2 = resolve(r['pk'], r['pi'])
            if s1 != 'OK' or s2 != 'OK':
                reason = s1 if s1 != 'OK' else s2
                why = n1 if s1 != 'OK' else n2
            else:
                key = (r['ren'], r['vin'], r['sta'], (r['vk'], r['vi']),
                       (r['pk'], r['pi']) if r['pk'] is not None else None)
                if key in gfx_keys:
                    reason, why = 'R_DUP_GFX', 'first record %d' % gfx_keys[key]
                else:
                    gfx_keys[key] = r['i']
                    reason, why = 'QUEUED_GFX', ''
            stage = 'gfx vs=%016x/%d ps=%s' % (r['vk'][1], r['vi'],
                                              ('%016x/%d' % (r['pk'][1], r['pi'])) if r['pk'] else '-')
        else:
            s1, n1 = resolve(r['ck'], r['ci'])
            if s1 != 'OK':
                reason, why = s1, n1
            else:
                key = (r['ck'], r['ci'])
                if key in cs_ids:
                    reason, why = 'R_DUP_CS', 'first record %d' % cs_ids[key]
                else:
                    cs_ids[key] = r['i']
                    reason, why = 'QUEUED_CS', ''
            stage = 'cs %016x/%d stage=%d' % (r['ck'][1], r['ci'], r['ck'][0])
        cnt[reason] += 1
        out.append({'record': r['i'], 'what': stage, 'reason': reason, 'detail': why if isinstance(why, str) else str(why),
                    'record_sha1': r['sha1']})
    skipped = [o for o in out if not o['reason'].startswith('QUEUED')]
    print('  simulated: queued gfx %d cs %d skipped %d by reason %s' % (cnt['QUEUED_GFX'], cnt['QUEUED_CS'], len(skipped),
          dict((k, v) for k, v in cnt.items() if not k.startswith('QUEUED'))))
    stale = collections.Counter(c[1].split(':')[1][:8] for c in cache.values() if c[0] == 'R_STALE')
    print('  stale translation files referenced (signature):', dict(stale))
    print('  missing translation files referenced:', sum(1 for c in cache.values() if c[0] == 'R_NOFILE'))
    with open(outp + '.tsv', 'w', encoding='ascii', newline='\n') as f:
        f.write('record\twhat\treason\tdetail\trecord_sha1\n')
        for o in skipped:
            f.write('%d\t%s\t%s\t%s\t%s\n' % (o['record'], o['what'], o['reason'], o['detail'], o['record_sha1']))
    with open(outp + '.tsv', 'rb') as f:
        print('  skipped list', outp + '.tsv', 'sha256', hashlib.sha256(f.read()).hexdigest())
    for o in skipped[:60]:
        print('   ', o['record'], o['what'], o['reason'], o['detail'])


if __name__ == '__main__':
    main()
