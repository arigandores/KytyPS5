# F47a4 (HPP-818, ROADMAP s122 item 722(d)(1), (g)(1)-(2)): own field table of the blend-and-coverage member (sec. 5.2 of
# edition 4) checked [c] against two open descriptions of the GFX10 registers, written independently of the emulator:
#   M  Mesa  src/amd/registers/gfx10.json (gitlab.freedesktop.org mesa/mesa, main, commit bc09932e...)  - fields, enums
#   K  Linux drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h and drivers/gpu/drm/amd/include/navi10_enum.h
#      (github torvalds/linux, master, header commit 4504f143...)                                        - fields, enums
#   F  Mesa  src/amd/common/ac_formats.c, ac_translate_colorswap() (commit bfb6c41b...) - COMP_SWAP per channel count
# The sources are not in git (sizes); sha256 of each is a member (SRC_SHA). Read only; ASCII only; exits 3 on the lock.
# Usage:
#   python regs_f47a4.py check <source dir>   every field (bits), every enum value and every COMP_SWAP pattern of the own
#                                             table equals M and K (and F); prints ALL OK
#   python regs_f47a4.py neg <source dir>     each single mutation of the own table (field +1 bit, enum value +1, swap
#                                             pattern rotated) must fail check; prints ALL OK
#   python regs_f47a4.py perm <comp_swap> <format>   own permutation: logical component -> memory channel, or UNDETERMINED
import copy
import json
import os
import re
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3')
    sys.exit(3)

SRC_SHA = {
    'gfx10.json': 'f3435695c47c3c3b1d8329a96b098452d5909944ca2c99995520c22614617d48',
    'gc_10_1_0_sh_mask.h': 'cba20414ecf02e91bafdcfbff7d4ba686326f0bdaf236d1a883364f08410c167',
    'navi10_enum.h': '26bf943bd92a5282814385cf80f3c7ced99ba0c534ae1b932d1bf4293fa2feed',
    'ac_formats.c': 'e725f0d0d5f641148b59f7adeaad140e69086fbd3668efd2e7e65776e254fe5d',
}

# ---------------------------------------------------------------- own table (edition 4 sec. 5.2)
# register -> {field: (lo, hi)}; t-indexed registers are written for t = 0 (stride per register in the guest map).
FIELDS = {
    'CB_BLEND0_CONTROL': {'COLOR_SRCBLEND': (0, 4), 'COLOR_COMB_FCN': (5, 7), 'COLOR_DESTBLEND': (8, 12),
                          'ALPHA_SRCBLEND': (16, 20), 'ALPHA_COMB_FCN': (21, 23), 'ALPHA_DESTBLEND': (24, 28),
                          'SEPARATE_ALPHA_BLEND': (29, 29), 'ENABLE': (30, 30), 'DISABLE_ROP3': (31, 31)},
    'CB_COLOR_CONTROL': {'DEGAMMA_ENABLE': (3, 3), 'MODE': (4, 6), 'ROP3': (16, 23)},
    'CB_TARGET_MASK': {'TARGET%d_ENABLE' % t: (4 * t, 4 * t + 3) for t in range(8)},
    'CB_SHADER_MASK': {'OUTPUT%d_ENABLE' % t: (4 * t, 4 * t + 3) for t in range(8)},
    'CB_COLOR0_INFO': {'ENDIAN': (0, 1), 'FORMAT': (2, 6), 'NUMBER_TYPE': (8, 10), 'COMP_SWAP': (11, 12),
                       'BLEND_CLAMP': (15, 15), 'BLEND_BYPASS': (16, 16), 'ROUND_MODE': (18, 18)},
}
ENUMS = {
    'BlendOp': {0: 'BLEND_ZERO', 1: 'BLEND_ONE', 2: 'BLEND_SRC_COLOR', 3: 'BLEND_ONE_MINUS_SRC_COLOR', 4: 'BLEND_SRC_ALPHA',
                5: 'BLEND_ONE_MINUS_SRC_ALPHA', 6: 'BLEND_DST_ALPHA', 7: 'BLEND_ONE_MINUS_DST_ALPHA', 8: 'BLEND_DST_COLOR',
                9: 'BLEND_ONE_MINUS_DST_COLOR', 10: 'BLEND_SRC_ALPHA_SATURATE', 11: 'BLEND_BOTH_SRC_ALPHA',
                12: 'BLEND_BOTH_INV_SRC_ALPHA', 13: 'BLEND_CONSTANT_COLOR', 14: 'BLEND_ONE_MINUS_CONSTANT_COLOR',
                15: 'BLEND_SRC1_COLOR', 16: 'BLEND_INV_SRC1_COLOR', 17: 'BLEND_SRC1_ALPHA', 18: 'BLEND_INV_SRC1_ALPHA',
                19: 'BLEND_CONSTANT_ALPHA', 20: 'BLEND_ONE_MINUS_CONSTANT_ALPHA'},
    'CombFunc': {0: 'COMB_DST_PLUS_SRC', 1: 'COMB_SRC_MINUS_DST', 2: 'COMB_MIN_DST_SRC', 3: 'COMB_MAX_DST_SRC',
                 4: 'COMB_DST_MINUS_SRC'},
    'CBMode': {0: 'CB_DISABLE', 1: 'CB_NORMAL', 2: 'CB_ELIMINATE_FAST_CLEAR', 3: 'CB_RESOLVE', 4: 'CB_DECOMPRESS',
               5: 'CB_FMASK_DECOMPRESS', 6: 'CB_DCC_DECOMPRESS', 7: 'CB_RESERVED'},
    'SurfaceSwap': {0: 'SWAP_STD', 1: 'SWAP_ALT', 2: 'SWAP_STD_REV', 3: 'SWAP_ALT_REV'},
    'SurfaceNumber': {0: 'NUMBER_UNORM', 1: 'NUMBER_SNORM', 2: 'NUMBER_USCALED', 3: 'NUMBER_SSCALED', 4: 'NUMBER_UINT',
                      5: 'NUMBER_SINT', 6: 'NUMBER_SRGB', 7: 'NUMBER_FLOAT'},
    'ColorFormat': {0: 'COLOR_INVALID', 1: 'COLOR_8', 2: 'COLOR_16', 3: 'COLOR_8_8', 4: 'COLOR_32', 5: 'COLOR_16_16',
                    6: 'COLOR_10_11_11', 7: 'COLOR_11_11_10', 8: 'COLOR_10_10_10_2', 9: 'COLOR_2_10_10_10',
                    10: 'COLOR_8_8_8_8', 11: 'COLOR_32_32', 12: 'COLOR_16_16_16_16', 14: 'COLOR_32_32_32_32',
                    16: 'COLOR_5_6_5', 17: 'COLOR_1_5_5_5', 18: 'COLOR_5_5_5_1', 19: 'COLOR_4_4_4_4', 20: 'COLOR_8_24',
                    21: 'COLOR_24_8', 22: 'COLOR_X24_8_32_FLOAT', 31: 'COLOR_2_10_10_10_6E4'},
}
# only the values the member uses from enum ROP3 (Mesa only; not in navi10_enum.h)
ROP3 = {204: 'ROP3_COPY'}
# COMP_SWAP -> format swizzle as in ac_translate_colorswap (HAS_SWIZZLE(chan, swz): desc->swizzle[chan] == swz):
# position c = logical component c (R, G, B, A = export X, Y, Z, W), letter = memory channel it is stored in ('_' =
# absent); per channel count; a pair not named there is UNDETERMINED (no own permutation). 3 channels SWAP_STD has no
# comment in F: F gives only HAS_SWIZZLE(0, X) (pattern 'X..'), G and B follow the channel order of the format [I].
SWAP = {
    1: {'SWAP_STD': 'X___', 'SWAP_ALT_REV': '___X'},
    2: {'SWAP_STD': 'XY__', 'SWAP_STD_REV': 'YX__', 'SWAP_ALT': 'X__Y', 'SWAP_ALT_REV': 'Y__X'},
    3: {'SWAP_STD': 'XYZ', 'SWAP_STD_REV': 'ZYX'},
    4: {'SWAP_STD': 'XYZW', 'SWAP_STD_REV': 'WZYX', 'SWAP_ALT': 'ZYXW', 'SWAP_ALT_REV': 'YZWX'},
}
# channel count of a ColorFormat name (numeric groups after COLOR_); X24_8_32_FLOAT and 6E4 forms - UNDETERMINED
def channels(fmt_name):
    if fmt_name in ('COLOR_X24_8_32_FLOAT', 'COLOR_2_10_10_10_6E4', 'COLOR_INVALID') or 'RESERVED' in fmt_name:
        return None
    return len(fmt_name[len('COLOR_'):].split('_'))


# ---------------------------------------------------------------- sources
def sha256(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(src):
    out = {'sha': {}}
    for n in SRC_SHA:
        out['sha'][n] = sha256(os.path.join(src, n))
    m = json.load(open(os.path.join(src, 'gfx10.json'), encoding='utf-8'))
    out['M_fields'] = {k: {f['name']: tuple(f['bits']) for f in v['fields']} for k, v in m['register_types'].items()}
    out['M_enums'] = {k: {e['value']: e['name'] for e in v['entries']} for k, v in m['enums'].items()}
    kf = {}
    for line in open(os.path.join(src, 'gc_10_1_0_sh_mask.h'), encoding='utf-8', errors='replace'):
        mm = re.match(r'#define (\w+?)__(\w+)__SHIFT\s+0x([0-9a-fA-F]+)', line)
        if mm:
            kf.setdefault(mm.group(1), {}).setdefault(mm.group(2), {})['shift'] = int(mm.group(3), 16)
        mm = re.match(r'#define (\w+?)__(\w+)_MASK\s+0x([0-9a-fA-F]+)L', line)
        if mm:
            kf.setdefault(mm.group(1), {}).setdefault(mm.group(2), {})['mask'] = int(mm.group(3), 16)
    out['K_fields'] = kf
    ke = {}
    cur = None
    for line in open(os.path.join(src, 'navi10_enum.h'), encoding='utf-8', errors='replace'):
        mm = re.match(r'typedef enum (\w+) \{', line)
        if mm:
            cur = mm.group(1)
            ke[cur] = {}
            continue
        if cur and line.startswith('}'):
            cur = None
            continue
        mm = re.match(r'(\w+)\s+= 0x([0-9a-fA-F]+),', line)
        if cur and mm:
            ke[cur][int(mm.group(2), 16)] = mm.group(1)
    out['K_enums'] = ke
    out['F'] = open(os.path.join(src, 'ac_formats.c'), encoding='utf-8').read()
    return out


def k_bits(entry):
    if not entry or 'shift' not in entry or 'mask' not in entry:
        return None
    lo = entry['shift']
    m = entry['mask'] >> lo
    w = m.bit_length()
    return (lo, lo + w - 1) if m == (1 << w) - 1 else None


def colorswap_cases(text):
    """{channels: {SWAP_x: pattern}} from the comments of ac_translate_colorswap()."""
    body = text[text.index('ac_translate_colorswap(enum amd_gfx_level'):]
    body = body[:body.index('\n}\n')]
    res = {}
    cur = None
    pend = None
    last_cond = None
    for line in body.split('\n'):
        mm = re.match(r'\s*case (\d):', line)
        if mm:
            cur = int(mm.group(1))
            res[cur] = {}
            continue
        if cur is None:
            continue
        cond = re.findall(r'HAS_SWIZZLE\((\d), ([XYZW])\)', line)
        if cond and re.search(r'\bif\b', line):
            last_cond = cond
        c = re.search(r'/\* ([XYZW_]{3,4}) \*/', line)
        r = re.findall(r'V_028C70_(SWAP_\w+)', line)
        if r and not c and not pend and last_cond and r[-1] not in res[cur]:
            pat = ['.'] * cur
            for i, l in last_cond:
                if int(i) < cur:
                    pat[int(i)] = l
            res[cur][r[-1]] = ''.join(pat)  # condition-derived: '.' = not fixed by F
            continue
        if r and not c and not pend:
            continue  # a second return of an already named pair (do_endian_swap branch)
        if c and r:
            res[cur][r[-1]] = c.group(1)  # 'return X; /* pat */' or 'return (endian ? A : B); /* pat */' -> no endian swap: last
            pend = None
        elif c:
            pend = c.group(1)
        elif r and pend:
            res[cur][r[-1]] = pend
            pend = None
    return res


def check(src, own_fields=FIELDS, own_enums=ENUMS, own_swap=SWAP, verbose=True):
    S = load(src)
    ok = True
    for n, h in SRC_SHA.items():
        good = S['sha'][n] == h
        ok &= good
        if verbose:
            print('source %-22s sha256 %s %s' % (n, S['sha'][n][:16], 'ok' if good else 'BAD (expected %s)' % h[:16]))
    for reg, fields in own_fields.items():
        for f, bits in fields.items():
            mb = S['M_fields'].get(reg, {}).get(f)
            kb = k_bits(S['K_fields'].get(reg, {}).get(f))
            good = mb == bits and kb == bits
            ok &= good
            if verbose:
                print('field %s.%-22s own [%d:%d] M %s K %s %s' % (reg, f, bits[1], bits[0], mb, kb, 'ok' if good else 'BAD'))
    for en, vals in own_enums.items():
        for v, name in vals.items():
            mv = S['M_enums'].get(en, {}).get(v)
            kv = S['K_enums'].get(en, {}).get(v)
            good = mv == name and kv == name
            ok &= good
            if verbose and not good:
                print('enum %s %d own %s M %s K %s BAD' % (en, v, name, mv, kv))
        if verbose:
            print('enum %-13s %d values vs M and K %s' % (en, len(vals), 'ok' if all(S['M_enums'].get(en, {}).get(v) == n and
                                                                                    S['K_enums'].get(en, {}).get(v) == n
                                                                                    for v, n in vals.items()) else 'BAD'))
    for v, name in ROP3.items():
        good = S['M_enums'].get('ROP3', {}).get(v) == name
        ok &= good
        if verbose:
            print('enum ROP3 0x%02x own %s M %s %s' % (v, name, S['M_enums'].get('ROP3', {}).get(v), 'ok' if good else 'BAD'))
    F = colorswap_cases(S['F'])

    def same(a, b):
        if set(a or {}) != set(b or {}):
            return False
        return all(len(a[k]) == len(b[k]) and all(f == '.' or f == o for f, o in zip(b[k], a[k])) for k in a)

    good = set(F) == set(own_swap) and all(same(own_swap[n], F[n]) for n in F)
    ok &= good
    if verbose:
        for n in sorted(set(F) | set(own_swap)):
            print('colorswap %d channels own %s F %s %s' % (n, sorted(own_swap.get(n, {}).items()), sorted(F.get(n, {}).items()),
                                                            'ok' if same(own_swap.get(n), F.get(n)) else 'BAD'))
    if verbose:
        print('ALL OK' if ok else 'FAIL')
    return ok


def neg(src):
    muts = []
    for reg, fields in FIELDS.items():
        for f, (lo, hi) in fields.items():
            m = copy.deepcopy(FIELDS)
            m[reg][f] = (lo + 1, hi + 1)
            muts.append(('field %s.%s +1' % (reg, f), m, ENUMS, SWAP))
    for en, vals in ENUMS.items():
        for v in vals:
            m = copy.deepcopy(ENUMS)
            m[en] = {(k + 1 if k == v else k): n for k, n in vals.items()}
            if v + 1 in vals:
                m[en] = {k: (vals[v] if k == v + 1 else (vals[v + 1] if k == v else n)) for k, n in vals.items()}
            muts.append(('enum %s %d' % (en, v), FIELDS, m, SWAP))
    for n, pats in SWAP.items():
        for s, p in pats.items():
            m = copy.deepcopy(SWAP)
            m[n][s] = p[1:] + p[0]
            muts.append(('swap %d %s rotated' % (n, s), FIELDS, ENUMS, m))
    caught = 0
    for name, f, e, s in muts:
        bad = not check(src, f, e, s, verbose=False)
        caught += bad
        if not bad:
            print('mutant NOT caught: %s' % name)
    print('neg %d of %d mutants caught' % (caught, len(muts)))
    print('ALL OK' if caught == len(muts) else 'FAIL')
    return caught == len(muts)


def perm(comp_swap, fmt):
    """logical component index (0..3 = X..W of the export) -> memory channel index, or None (UNDETERMINED)."""
    name = ENUMS['ColorFormat'].get(fmt)
    n = channels(name) if name else None
    pat = SWAP.get(n, {}).get(ENUMS['SurfaceSwap'][comp_swap]) if n else None
    if pat is None:
        return None
    return {c: 'XYZW'.index(ch) for c, ch in enumerate(pat) if ch != '_'}


def main():
    mode = sys.argv[1]
    if mode == 'check':
        return 0 if check(sys.argv[2]) else 1
    if mode == 'neg':
        return 0 if neg(sys.argv[2]) else 1
    if mode == 'perm':
        p = perm(int(sys.argv[2], 0), int(sys.argv[3], 0))
        print('UNDETERMINED' if p is None else ' '.join('%s->m%d' % ('XYZW'[c], m) for c, m in sorted(p.items())))
        return 0
    return 2


if __name__ == '__main__':
    sys.exit(main())
