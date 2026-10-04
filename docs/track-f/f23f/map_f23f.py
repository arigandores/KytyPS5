"""F23f (HPP-592, ROADMAP s122 item 498(g)(2)): map of the 17 covered form-A programs - which SPIR-V module of the captures
f12_rd_k05 / f13_rd is a translation of which (stage, hash16, state16, permutation, signature), and what the INSTALLED S12
translation (signature 26ce5fc7..., directory variant_fixb26_fixb1b_fixf10 of the emulator cache) holds for the same
(stage, hash16, state16). Offline, no GPU. Reader of the cache file = F23c run_f23c_inv.py index_cache_file (copied).

Output: map_f23f.out.txt, map_f23f.json; the S12 modules are extracted to s12spv/<stage>_<hash>_<state>_p<k>.spv."""
import hashlib
import json
import os
import re
import struct
import sys

D = 'C:/kyty/f287/f23f/'
INV = 'C:/kyty/f287/f23c/inv/'
CAPS = ['f12_rd_k05.rdc', 'f13_rd.rdc']
PROGS = 'C:/kyty/f287/f23c/inv_f23c_programs.tsv'
TREES = ['C:/kyty/KytyPS5/ps5 em/_ShaderCache', 'C:/kyty/f287', 'C:/kyty/s288']
S12DIR = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10'
S12SIG = '26ce5fc78ea3b20be537c7696be041f5e97d9e58'
MAGIC = b'\x03\x02\x23\x07'
CACHE_RE = re.compile(r'^(ps|cs|vs|gs|hs|ms|es|ls)_([0-9a-f]{16})_([0-9a-f]{16})\.bin$')
NL = chr(10)


def spirv_walk_len(buf, p, limit):
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


def read_cache(path):
    data = open(path, 'rb').read()
    nl = data.find(b'\n')
    if not data.startswith(b'KytySC') or nl < 0:
        return None
    sig = data[:nl].decode('latin1')
    pay = nl + 1 + 8
    stage, ghash = struct.unpack_from('<IQ', data, pay)
    mods = []
    i = data.find(MAGIC, pay)
    while i >= 0:
        cnt = struct.unpack_from('<I', data, i - 4)[0]
        if 5 < cnt and i + 4 * cnt <= len(data) and spirv_walk_len(data, i, i + 4 * cnt) == 4 * cnt:
            mods.append(data[i:i + 4 * cnt])
            i = data.find(MAGIC, i + 4 * cnt)
            continue
        i = data.find(MAGIC, i + 4)
    return sig, '%016x' % ghash, mods


def walk(roots, hashes):
    for root in roots:
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in ('wt', 'build', '.git', '__pycache__')]
            for f in fs:
                m = CACHE_RE.match(f)
                if m and m.group(2) in hashes:
                    yield os.path.join(d, f).replace(chr(92), '/'), m


def main():
    progs = {}
    for line in open(PROGS, encoding='utf-8').read().splitlines()[1:]:
        st, h, fb, caps = line.split(chr(9))
        if caps != '-':
            progs[h] = st
    assert len(progs) == 17, len(progs)
    caps = {c: set(m['sha'] for m in json.load(open(INV + c + '.json'))['modules']) for c in CAPS}
    idx = {}
    s12 = {}
    os.makedirs(D + 's12spv', exist_ok=True)
    nfiles = 0
    for path, m in walk(TREES, set(progs)):
        nfiles += 1
        r = read_cache(path)
        if r is None:
            continue
        sig, gh, mods = r
        sigid = sig.split(':')[1] if ':' in sig else sig
        for k, mod in enumerate(mods):
            sha = hashlib.sha256(mod).hexdigest()
            idx.setdefault(sha, set()).add((m.group(1), gh, m.group(3), k, sigid[:8]))
        if path.startswith(S12DIR + '/'):
            assert sigid == S12SIG, (path, sigid)
            for k, mod in enumerate(mods):
                fn = '%s_%s_%s_p%d.spv' % (m.group(1), gh, m.group(3), k)
                open(D + 's12spv/' + fn, 'wb').write(mod)
                s12[(m.group(1), gh, m.group(3), k)] = (hashlib.sha256(mod).hexdigest(), len(mod), fn)
    out = []
    res = {}
    out.append('cache files read (17 programs, 3 trees): %d; S12 modules: %d' % (nfiles, len(s12)))
    for h in sorted(progs, key=lambda x: (progs[x], x)):
        st = progs[h]
        out.append('%s %s' % (st, h))
        res[h] = {'stage': st, 'captures': {}, 's12': {}}
        for key, v in sorted(s12.items()):
            if key[1] == h:
                out.append('  S12 %s state %s p%d sha %s bytes %d' % (key[0], key[2], key[3], v[0][:16], v[1]))
                res[h]['s12']['%s|%d' % (key[2], key[3])] = {'sha': v[0], 'bytes': v[1], 'file': v[2]}
        for c in CAPS:
            hits = []
            for sha in caps[c]:
                for (s, gh, state, k, sig) in idx.get(sha, ()):
                    if gh == h:
                        hits.append((sha, state, k, sig))
            for sha, state, k, sig in sorted(hits):
                s = s12.get((st, h, state, k))
                eq = 'S12=' if s and s[0] == sha else ('S12!=' if s else 'S12-none')
                out.append('  %s module sha %s state %s p%d sig %s %s' % (c, sha[:16], state, k, sig, eq))
                res[h]['captures'].setdefault(c, []).append({'sha': sha, 'state': state, 'perm': k, 'sig': sig,
                                                              'equal_s12': bool(s and s[0] == sha)})
    open(D + 'map_f23f.out.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(out) + NL)
    json.dump(res, open(D + 'map_f23f.json', 'w'), indent=1, sort_keys=True)
    print(NL.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
