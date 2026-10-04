"""F23c (HPP-587, ROADMAP s122 item 493(g)(2)): coverage of the 38 form-A programs (docs/track-f/f23a/b8_forms_normal.tsv) by the
existing RenderDoc snapshots of the three allowed directories (C:/kyty/KytyPS5/ps5 em/_RenderDoc/, C:/kyty/f287/, C:/kyty/s288/;
no 'find /'), by the sha256 of the SPIR-V module.

Step A - index sha256(SPIR-V) -> (stage, guest hash16, translator signature) from every translation-cache file
  <stage>_<hash16>_<state16>.bin under the same three trees (files with equal bytes are read once). A cache file holds the key
  (u32 stage, u64 guest hash, ...) after the signature line and the 8-byte payload hash, and each permutation's SPIR-V as a
  u32 word count followed by the words (shaderTranslationCache.cpp ReadFileUnchecked / Save); the SPIR-V is found by its magic
  with the count word right before it.
Step B - every .rdc: the frame-capture section is read as a stream (RenderDoc 1.46: section header after the file header,
  LZ4 blocks of 1 MiB, each an i32 compressed size + data, dictionary = previous block); every SPIR-V module in it is found by
  its magic, its length is the u64 byte count that precedes the 64-byte-aligned module (it is checked against an instruction
  walk that ends on OpFunctionEnd); sha256 of the module bytes -> index. No replay, no GPU.
  'present' = the module is in the capture (the pipeline existed at capture time), not 'executed in the captured frame'.
Positive control: the SPIR-V of 380bb9d636390bae of F12d (sha 3e034e54...) is dispatched in f12_rd_k02..k04 by F12f's replay
  (KytyPS5 docs/track-f/f12f.md) - the scan has to find it there.
Output: inv_f23c.out.txt, inv_f23c_programs.tsv, inv/<capture>.json (resumable: a capture with a json is not rescanned)."""
import hashlib
import json
import os
import re
import struct
import sys
import time
from multiprocessing import Pool

import lz4.block

D = 'C:/kyty/f287/f23c/'
INV = D + 'inv/'
TREES = ['C:/kyty/KytyPS5/ps5 em/_ShaderCache', 'C:/kyty/KytyPS5/ps5 em/_RenderDoc', 'C:/kyty/f287', 'C:/kyty/s288']
RDC_TREES = ['C:/kyty/KytyPS5/ps5 em/_RenderDoc', 'C:/kyty/f287', 'C:/kyty/s288']
FORMS = 'C:/kyty/KytyPS5/docs/track-f/f23a/b8_forms_normal.tsv'
MAGIC = b'\x03\x02\x23\x07'
CACHE_RE = re.compile(r'^(ps|cs|vs|gs|hs|ms|es|ls)_([0-9a-f]{16})_([0-9a-f]{16})\.bin$')
STAGE_NAMES = {}
CONTROL_380B = '3e034e543b3c8d5cac27a617bcc2c0ac6282f71556b8c5cbdf2122daf305d6f6'


def walk_files(roots, pred):
    for root in roots:
        if not os.path.isdir(root):
            continue
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in ('wt', 'build', '.git', '__pycache__')]
            for f in fs:
                if pred(f):
                    yield os.path.join(d, f).replace('\\', '/')


def spirv_walk_len(buf, p, limit):
    """byte length of a SPIR-V module at p by an instruction walk ending on the last OpFunctionEnd; 0 if invalid"""
    j = p + 20
    end = 0
    while j + 4 <= limit:
        hw = struct.unpack_from('<I', buf, j)[0]
        wc = hw >> 16
        op = hw & 0xffff
        if wc == 0 or j + 4 * wc > limit:
            break
        j += 4 * wc
        if op == 56:
            end = j
            if j + 4 > limit or (struct.unpack_from('<I', buf, j)[0] & 0xffff) != 54:
                break
    return end - p if end else 0


def index_cache_file(path):
    data = open(path, 'rb').read()
    nl = data.find(b'\n')
    if not data.startswith(b'KytySC') or nl < 0:
        return None
    sig = data[:nl].decode('latin1')
    pay = nl + 1 + 8
    stage, ghash = struct.unpack_from('<IQ', data, pay)
    out = []
    i = data.find(MAGIC, pay)
    while i >= 0:
        cnt = struct.unpack_from('<I', data, i - 4)[0]
        if 5 < cnt and i + 4 * cnt <= len(data) and spirv_walk_len(data, i, i + 4 * cnt) == 4 * cnt:
            mod = data[i:i + 4 * cnt]
            out.append((hashlib.sha256(mod).hexdigest(), 4 * cnt))
            i = data.find(MAGIC, i + 4 * cnt)
            continue
        i = data.find(MAGIC, i + 4)
    return sig, stage, '%016x' % ghash, out


def build_index():
    seen = {}
    idx = {}
    nfiles = 0
    for path in walk_files(TREES, lambda f: CACHE_RE.match(f) is not None):
        nfiles += 1
        st = os.stat(path)
        m = CACHE_RE.match(os.path.basename(path))
        key = (st.st_size, m.group(0))
        data_sha = None
        if key in seen:
            data_sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
            if data_sha in seen[key]:
                continue
        r = index_cache_file(path)
        if data_sha is None:
            data_sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        seen.setdefault(key, set()).add(data_sha)
        if r is None:
            continue
        sig, stage, ghash, mods = r
        if ghash != m.group(2):
            continue
        for sha, n in mods:
            idx.setdefault(sha, set()).add((m.group(1), ghash, sig.split(':')[1] if ':' in sig else sig))
    return idx, nfiles, sum(len(v) for v in seen.values())


def rdc_modules(path):
    f = open(path, 'rb')
    f.seek(12)
    hl = struct.unpack('<I', f.read(4))[0]
    f.seek(hl)
    h = f.read(40)
    st, clen, ulen, ver, flags, nlen = struct.unpack_from('<IQQQII', h, 4)
    name = f.read(nlen).rstrip(b'\0').decode('latin1')
    info = {'section': name, 'clen': clen, 'ulen': ulen, 'flags': flags}
    if flags != 2:
        info['error'] = 'unsupported section flags %d' % flags
        return info, []
    B = 1 << 20
    prev = b''
    tot = 0
    buf = bytearray()
    base = 0
    pos = 0
    mods = {}
    pending = None  # (i, candidate byte lengths) of a magic whose module may extend past the buffer
    while tot < ulen:
        cs = struct.unpack('<i', f.read(4))[0]
        data = f.read(cs)
        n = min(B, ulen - tot)
        d = lz4.block.decompress(data, uncompressed_size=n, dict=prev[-65536:])
        prev = d
        tot += n
        buf += d
        last = tot >= ulen
        while True:
            if pending is None:
                i = buf.find(MAGIC, pos)
                if i < 0:
                    pos = max(pos, len(buf) - 3)
                    break
                pre = bytes(buf[max(0, i - 128):i])
                # candidates for the u64 byte count serialized before the 64-byte-aligned module: any qword of the
                # 128 bytes before the magic in [20, 64 MiB] and a multiple of 4; the one that the instruction walk confirms wins
                cands = sorted({c for c in (struct.unpack_from('<Q', pre, o)[0] for o in range(0, len(pre) - 7))
                                if 20 <= c <= (1 << 26) and c % 4 == 0})
                if not cands:
                    pos = i + 4
                    continue
                pending = (i, cands)
            i, cands = pending
            if i + max(cands) > len(buf) and not last:
                break
            L = 0
            for c in sorted(cands, reverse=True):
                if i + c <= len(buf) and spirv_walk_len(buf, i, i + c) == c:
                    L = c
                    break
            pending = None
            if not L:
                pos = i + 4
                continue
            mod = bytes(buf[i:i + L])
            sha = hashlib.sha256(mod).hexdigest()
            e = mods.setdefault(sha, [L, 0, base + i])
            e[1] += 1
            pos = i + L
        # keep memory bounded: drop consumed bytes (keep 256 bytes of context)
        keep_from = (pending[0] if pending is not None else pos) - 256
        if keep_from > 4 * B:
            buf = buf[keep_from:]
            base += keep_from
            pos -= keep_from
            if pending is not None:
                pending = (pending[0] - keep_from, pending[1])
    info['decompressed'] = tot
    return info, [{'sha': s, 'bytes': v[0], 'copies': v[1], 'first_offset': v[2]} for s, v in mods.items()]


def scan_capture(path):
    out = INV + os.path.basename(path) + '.json'
    if os.path.exists(out):
        return path, 'cached'
    t0 = time.time()
    info, mods = rdc_modules(path)
    info['wall_s'] = round(time.time() - t0, 1)
    info['path'] = path
    info['size'] = os.path.getsize(path)
    info['modules'] = mods
    tmp = out + '.tmp'
    json.dump(info, open(tmp, 'w'))
    os.replace(tmp, out)
    return path, 'scanned %d modules in %.1f s' % (len(mods), info['wall_s'])


def main():
    os.makedirs(INV, exist_ok=True)
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    rdcs = sorted(walk_files(RDC_TREES, lambda f: f.lower().endswith('.rdc')))
    log('captures %d (%.1f GB) in %s' % (len(rdcs), sum(os.path.getsize(p) for p in rdcs) / 1e9, RDC_TREES))
    t0 = time.time()
    with Pool(int(os.environ.get('INV_JOBS', '4'))) as pool:
        for path, msg in pool.imap_unordered(scan_capture, rdcs):
            log('  %s: %s' % (path, msg))
    log('scan wall %.1f s' % (time.time() - t0))
    if '--scan-only' in sys.argv:
        return
    t0 = time.time()
    idx, nfiles, nuniq = build_index()
    log('index: cache files %d, distinct contents %d, distinct SPIR-V %d, built in %.1f s' % (nfiles, nuniq, len(idx), time.time() - t0))
    forms = []
    for line in open(FORMS, encoding='utf-8').read().splitlines()[1:]:
        if line.strip():
            stage, h16, fb = line.split('\t')[:3]
            forms.append((stage, h16, fb))
    assert len(forms) == 38, len(forms)
    form_keys = {(s, h) for s, h, _ in forms}
    cover = {(s, h): [] for s, h, _ in forms}
    for path in rdcs:
        info = json.load(open(INV + os.path.basename(path) + '.json'))
        mods = info['modules']
        ident = 0
        hit = set()
        ctl = False
        for m in mods:
            if m['sha'] == CONTROL_380B:
                ctl = True
            owners = idx.get(m['sha'], set())
            if owners:
                ident += 1
            for st, gh, sig in owners:
                if (st, gh) in form_keys:
                    hit.add((st, gh))
        for k in hit:
            cover[k].append(os.path.basename(path))
        log('%-22s %6.2f GB  section %s flags %d  decompressed %.1f GB  modules %d  identified %d (%.1f %%)  form-A programs %d  control 380b %s  %s' % (
            os.path.basename(path), info['size'] / 1e9, info.get('section'), info.get('flags', -1), info.get('decompressed', 0) / 1e9, len(mods), ident,
            100.0 * ident / max(1, len(mods)), len(hit), 'yes' if ctl else 'no', ','.join(sorted(h for s, h in hit))))
    with open(D + 'inv_f23c_programs.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('stage\thash16\tformB\tcaptures_present\n')
        for s, h, fb in forms:
            f.write('%s\t%s\t%s\t%s\n' % (s, h, fb, ','.join(cover[(s, h)]) or '-'))
    ncov = sum(1 for k in cover if cover[k])
    log('form-A programs present in >= 1 capture: %d of 38 (PS %d of 20, CS %d of 18)' % (
        ncov, sum(1 for (s, h) in cover if cover[(s, h)] and s == 'ps'), sum(1 for (s, h) in cover if cover[(s, h)] and s == 'cs')))
    # index coverage of the 38 programs themselves (can a program be recognised at all?)
    in_idx = {(s, h) for owners in idx.values() for s, h, sig in owners}
    log('form-A programs with >= 1 SPIR-V in the index: %d of 38' % sum(1 for k in form_keys if k in in_idx))
    open(D + 'inv_f23c.out.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
