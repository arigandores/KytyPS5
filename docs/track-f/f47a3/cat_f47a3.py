# F47a3 (HPP-816, ROADMAP s122 item 718(v)(1)-(4)): own parser of the translation catalog files and the matcher of a
# snapshot module against them. Read only; ASCII only; exits 3 when C:/kyty/SEALED_RUN.lock exists.
#
# File format (shaderTranslationCache.cpp Save / ReadFileUnchecked at the commit of the installed binary):
#   signature line "KytySC<ver>:<translator hash>[:...]\n" | u64 XXH3-64(payload) | payload
#   payload = u32 stage | u64 hash H | u32 user_data_count | u32 code_size | u32 n + n*u32 static_state
#           | plan (not parsed) | u32 count | count * (specialization | compiled info | u32 L + L*u32 spirv)
# The parser does not re-implement the plan / specialization / compiled-info readers: it finds every SPIR-V module of
# the payload as "u32 L, then L words starting with 0x07230203 whose instruction stream (word counts from word 5) ends
# exactly at word L", non-overlapping, left to right. Members of the file: the payload hash matches; the key fields read;
# >= 1 module; the last module ends exactly at the payload end (the spirv vector is the last field of the last
# permutation). A file that fails any member is BAD and its modules are not used.
#
# Usage:
#   python cat_f47a3.py index  <catalog dir> [--out <tsv>]            one line per permutation module
#   python cat_f47a3.py find   <catalog dir> <module.spv> [--dual]    matches of a module: exact words, and with
#                                                                     --dual also after the own Location1->Index1
#                                                                     rewrite of every catalog module and by words
#                                                                     without Location/Index decorations of outputs
#   python cat_f47a3.py selftest <catalog dir>                        positive / negative controls of the parser
import hashlib
import os
import struct
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3')
    sys.exit(3)

import xxhash

MAGIC = 0x07230203
MAGIC_B = struct.pack('<I', MAGIC)
STAGES = {'vs', 'ps', 'cs'}


def walk_ok(words):
    """True when words is one SPIR-V module: magic, bound > 0, instruction word counts end exactly at len(words)."""
    if len(words) < 5 or words[0] != MAGIC or words[3] == 0:
        return False
    i = 5
    n = len(words)
    while i < n:
        c = words[i] >> 16
        if c == 0 or i + c > n:
            return False
        i += c
    return i == n


def parse_file(path):
    """Returns dict(ok, why, sig, stage, hash, udc, code_size, modules=[(offset, words tuple)])."""
    b = open(path, 'rb').read()
    r = dict(path=path, ok=False, why='', modules=[])
    nl = b.find(bytes([10]))
    if nl < 0 or not b.startswith(b'KytySC'):
        r['why'] = 'no_signature'
        return r
    r['sig'] = b[:nl].decode('ascii', 'replace')
    p0 = nl + 1
    if len(b) < p0 + 8 + 24:
        r['why'] = 'short'
        return r
    stored = struct.unpack_from('<Q', b, p0)[0]
    payload = b[p0 + 8:]
    if xxhash.xxh3_64_intdigest(payload) != stored:
        r['why'] = 'payload_hash'
        return r
    stage, h, udc, code_size, nss = struct.unpack_from('<IQIII', payload, 0)
    r.update(stage=stage, hash='%016x' % h, udc=udc, code_size=code_size, n_static=nss)
    mods = []
    pos = 24 + 4 * nss
    while True:
        i = payload.find(MAGIC_B, pos)
        if i < 0:
            break
        if i >= 4:
            L = struct.unpack_from('<I', payload, i - 4)[0]
            if 5 <= L and i + 4 * L <= len(payload):
                words = struct.unpack_from('<%dI' % L, payload, i)
                if walk_ok(words):
                    mods.append((i, words))
                    SHA[id(words)] = sha(words)
                    pos = i + 4 * L
                    continue
        pos = i + 1
    r['modules'] = mods
    if not mods:
        r['why'] = 'no_module'
        return r
    last_off, last_words = mods[-1]
    if last_off + 4 * len(last_words) != len(payload):
        r['why'] = 'last_module_not_at_end'
        return r
    r['ok'] = True
    return r


def catalog(root):
    files = []
    for fn in sorted(os.listdir(root)):
        if not fn.endswith('.bin') or fn.split('_')[0] not in STAGES:
            continue
        files.append(parse_file(os.path.join(root, fn).replace(os.sep, '/')))
    return files


# ---------------------------------------------------------------- dual-source rewrite (own, written anew from the
# contract of DualSrcBlend::RewriteLocation1ToIndex1: the one OpDecorate <output var> Location 1 -> Location 0, then
# OpDecorate <var> Index 1 inserted right after it; no new id)
OP_VARIABLE, OP_DECORATE, OP_MEMBER_DECORATE = 59, 71, 72
SC_OUTPUT, DEC_LOCATION, DEC_INDEX = 3, 30, 32


def instrs(words):
    i = 5
    while i < len(words):
        c = words[i] >> 16
        yield i, words[i] & 0xffff, c
        i += c


def outputs(words):
    return {words[i + 2] for i, op, c in instrs(words) if op == OP_VARIABLE and c >= 4 and words[i + 3] == SC_OUTPUT}


def rewrite_loc1(words):
    """Returns (outcome, new words or None)."""
    outv = outputs(words)
    locs = []
    for i, op, c in instrs(words):
        if op == OP_DECORATE and c >= 3:
            if words[i + 2] == DEC_INDEX:
                return 'has_index', None
            if words[i + 2] == DEC_LOCATION:
                if c != 4:
                    return 'malformed', None
                locs.append((i, words[i + 1], words[i + 3]))
        elif op == OP_MEMBER_DECORATE and c >= 4 and words[i + 3] in (DEC_LOCATION, DEC_INDEX):
            return 'member_decoration', None
    loc1 = None
    loc0 = False
    for i, t, loc in locs:
        if t not in outv:
            continue
        if loc >= 2:
            return 'location_above1', None
        if loc == 0:
            loc0 = True
        elif loc1 is not None:
            return 'multiple_location1', None
        else:
            loc1 = i
    if loc1 is None:
        return 'no_location1', None
    if not loc0:
        return 'no_location0', None
    t = words[loc1 + 1]
    out = list(words[:loc1 + 4])
    out[loc1 + 3] = 0
    out += [(4 << 16) | OP_DECORATE, t, DEC_INDEX, 1]
    out += list(words[loc1 + 4:])
    return 'patched', tuple(out)


def strip_out_decorations(words):
    """Words without the OpDecorate Location / Index of Output variables (comparison of RC2(2), second form)."""
    outv = outputs(words)
    keep = list(words[:5])
    for i, op, c in instrs(words):
        if op == OP_DECORATE and c >= 3 and words[i + 2] in (DEC_LOCATION, DEC_INDEX) and words[i + 1] in outv:
            continue
        keep += words[i:i + c]
    return tuple(keep)


SHA = {}
DUAL = {}


def msha(w):
    return SHA.get(id(w)) or sha(w)


def dual_shas(w):
    k = id(w)
    if k not in DUAL:
        oc, nw = rewrite_loc1(w)
        DUAL[k] = (sha(nw) if oc == 'patched' else None, sha(strip_out_decorations(w)))
    return DUAL[k]


def sha(words):
    return hashlib.sha256(struct.pack('<%dI' % len(words), *words)).hexdigest()


def load_spv(path):
    b = open(path, 'rb').read()
    return struct.unpack('<%dI' % (len(b) // 4), b)


def find(files, target, dual=False):
    """Matches: exact (file, k); with dual also rewritten (catalog module rewritten == target) and stripped."""
    t_sha = sha(target)
    t_strip = sha(strip_out_decorations(target)) if dual else None
    exact, rew, strp = [], [], []
    for f in files:
        if not f['ok']:
            continue
        for k, (off, w) in enumerate(f['modules']):
            if msha(w) == t_sha:
                exact.append((f, k))
            if dual:
                rs, ss = dual_shas(w)
                if rs == t_sha:
                    rew.append((f, k))
                if ss == t_strip:
                    strp.append((f, k))
    return exact, rew, strp


def fname(f):
    return os.path.basename(f['path'])


def main():
    if len(sys.argv) < 3:
        print(__doc__ if __doc__ else 'usage: index|find|selftest <dir>')
        return 2
    mode, root = sys.argv[1], sys.argv[2]
    files = catalog(root)
    bad = [f for f in files if not f['ok']]
    print('catalog %s files %d ok %d bad %d modules %d' % (root, len(files), len(files) - len(bad), len(bad),
                                                          sum(len(f['modules']) for f in files if f['ok'])))
    for f in bad:
        print('BAD %s %s' % (fname(f), f['why']))
    if mode == 'index':
        out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
        lines = ['file\tstage\thash\tudc\tk\tn_perm\twords\tsha256']
        for f in files:
            if f['ok']:
                for k, (off, w) in enumerate(f['modules']):
                    lines.append('%s\t%d\t%s\t%d\t%d\t%d\t%d\t%s' % (fname(f), f['stage'], f['hash'], f['udc'], k,
                                                                    len(f['modules']), len(w), sha(w)))
        if out:
            open(out, 'w', encoding='ascii', newline='\n').write(chr(10).join(lines) + chr(10))
            print('index rows %d -> %s' % (len(lines) - 1, out))
        return 0 if not bad else 1
    if mode == 'find':
        target = load_spv(sys.argv[3])
        dual = '--dual' in sys.argv
        exact, rew, strp = find(files, target, dual)
        print('target %s words %d walk_ok %d' % (sha(target)[:16], len(target), walk_ok(target)))
        for name, lst in (('exact', exact), ('rewritten', rew), ('stripped', strp)):
            if name != 'exact' and not dual:
                continue
            hs = sorted({f['hash'] for f, k in lst})
            print('%s %d hashes %s %s' % (name, len(lst), hs, ['%s#%d' % (fname(f), k) for f, k in lst][:8]))
        n = len(exact) if not dual else (len(exact) + len(rew))
        print('MATCH_ONE' if n == 1 else ('MATCH_NONE' if n == 0 else 'MATCH_MANY'))
        return 0
    if mode == 'selftest':
        return selftest(files, bad)
    return 2


def selftest(files, bad):
    ok = not bad
    ok_files = [f for f in files if f['ok']]
    # (1) every module of the catalog by sha: how many places share it (positive control 'exactly one' is per module)
    where = {}
    for f in ok_files:
        for k, (off, w) in enumerate(f['modules']):
            where.setdefault(msha(w), []).append((f, k))
    dup = {s: l for s, l in where.items() if len(l) > 1}
    dup_cross_h = {s: l for s, l in dup.items() if len({f['hash'] for f, k in l}) > 1}
    n_mod = sum(len(f['modules']) for f in ok_files)
    print('modules %d unique sha %d shared by >1 place %d (of them across different H %d)' % (
        n_mod, len(where), len(dup), len(dup_cross_h)))
    ps_mods = [(f, k, w) for f in ok_files if fname(f).startswith('ps_') for k, (o, w) in enumerate(f['modules'])]
    one_place = sum(1 for f, k, w in ps_mods if len(where[msha(w)]) == 1)
    one_h = sum(1 for f, k, w in ps_mods if len({g['hash'] for g, j in where[msha(w)]}) == 1)
    print('PS modules %d: found at exactly one place %d; all places of one H %d; places of >1 H %d' % (
        len(ps_mods), one_place, one_h, len(ps_mods) - one_h))
    for s_, l in sorted(dup_cross_h.items()):
        print('  across H %s %s' % (s_[:16], ['%s#%d' % (fname(f), k) for f, k in l]))
    for s, l in sorted(dup.items())[:10]:
        print('  shared %s %s' % (s[:16], ['%s#%d' % (fname(f), k) for f, k in l]))
    # (2) positive: every PS module found by find() exactly at its own place (or at all places of its sha group)
    ps = [(f, k, w) for f in ok_files if fname(f).startswith('ps_') for k, (o, w) in enumerate(f['modules'])]
    pos_fail = 0
    for f, k, w in ps:
        exact, _, _ = find(ok_files, w)
        if (f, k) not in [(g, j) for g, j in exact] or len(exact) != len(where[msha(w)]):
            pos_fail += 1
    print('positive: PS modules %d found at own place (and only at its sha group) %d fail %d' % (len(ps), len(ps) - pos_fail, pos_fail))
    ok &= pos_fail == 0
    # (3) negative: one word changed (last word of the module xor 1, and the bound word +1) -> 0 exact matches
    neg_fail = 0
    for f, k, w in ps[:60]:
        for m in (list(w[:-1]) + [w[-1] ^ 1], list(w[:3]) + [w[3] + 1] + list(w[4:])):
            exact, _, _ = find(ok_files, tuple(m))
            neg_fail += len(exact) != 0
    print('negative: 2 mutations x %d PS modules, matches found %d (must be 0)' % (min(60, len(ps)), neg_fail))
    ok &= neg_fail == 0
    # (4) dual-source path: catalog PS with Output Location 1; own rewrite; rewritten module: exact 0 (RC2(b) by
    # construction), rewritten-path 1 group, stripped >= 1 and contains the source
    oc_count = {}
    dual_fail = rew_one = strp_one = 0
    n_patched = 0
    for f, k, w in ps:
        oc, nw = rewrite_loc1(w)
        oc_count[oc] = oc_count.get(oc, 0) + 1
        if oc != 'patched':
            continue
        n_patched += 1
        ex, rew, strp = find(ok_files, nw, dual=True)
        good = (len(ex) == 0 and (f, k) in [(g, j) for g, j in rew] and (f, k) in [(g, j) for g, j in strp])
        dual_fail += not good
        rew_one += len({g['hash'] for g, j in rew}) == 1 and len(rew) == len(where[msha(w)])
        strp_one += len(strp) == len(where[msha(w)])
    print('dual: rewrite outcomes %s; checked %d patched: exact 0 and found by rewrite and by stripped - fail %d' % (
        sorted(oc_count.items()), n_patched, dual_fail))
    print('dual: rewritten-path matches = own sha group (one H) %d of %d; stripped matches = own sha group %d of %d' % (
        rew_one, n_patched, strp_one, n_patched))
    ok &= dual_fail == 0
    # (5) parser against the file key: H of the file name = H of the payload; stage name = stage field
    key_fail = 0
    for f in ok_files:
        if fname(f).split('_')[1] != f['hash']:
            key_fail += 1
    print('key: file name H = payload H fail %d' % key_fail)
    ok &= key_fail == 0
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
