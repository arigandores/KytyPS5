"""dt_f47g.py - reader of the "F47dt:" lines of KYTY_DIAG_F47DT (track F, F47g HPP-824, ROADMAP s122 item 740(v)(1)),
own code: the rule of the outcome is item 740(v)(6), the form item 740(v)(5).

    python dt_f47g.py table <log> [--files DIR] [--block N,N,...] [--white N,...] [--stand PATH] [--enum PATH]
                                   [--cfmt PATH] [--out PATH]
    python dt_f47g.py selftest      fixtures of every member of rule (6), mutations of (v)(1); prints ALL OK

table: one row per draw of the PS H (key n, d) with the comparisons of form (5) and the verdict of the draw; with --block
(present numbers n of the black series, the video detector of the tag) and --white (white series) the reading of rule
(6): DEFECT (1) / NOT_A_DEFECT (2) / DEAD_END (3) / UNDETERMINED (4). --stand: the output of run_stand_f47g.py of the
binary of the tag (its last line must be ALL OK). --files: the _f47dt/ directory of the tag; every file named by a line
must hash (XXH3-64) to the hash of the line, and the N+- member (one byte of a copy of a block (i) file flipped at 10
positions -> a different hash 10 of 10) is evaluated there.

Own decoding (not the emulator's): T# format codes - IMG_FMT_* of the Linux header navi10_enum.h (source K of F47a4, sha256
26bf943b...); colour target formats - ColorFormat / SurfaceNumber of Mesa gfx10.json (source M, f3435695...); register
fields - the table of F47a4 section 5.1 (CB_BLEND, CB_COLOR_CONTROL, CB_TARGET_MASK, CB_COLOR<t>_INFO) and the GFX10
fields named in the code below (PA_CL_VPORT_*, PA_SC_*_SCISSOR_*, PA_SC_WINDOW_OFFSET, PA_SC_MODE_CNTL_0, DB_DEPTH_CONTROL,
PA_SU_SC_MODE_CNTL, DB_ALPHA_TO_MASK).

Comparison results: eq / ne / und (not determined, with the reason) / na (not applicable). A draw is ne when any member is
ne, und when any member is und and none ne, else eq. Rule (6)(4): a show with eq and und draws is und; the line reads by
the worst show of the block; ne in any block show is (1).
"""
import hashlib
import json
import os
import random
import re
import shutil
import struct
import sys
import tempfile

import xxhash

ENUM_DEFAULT = 'C:/kyty/f287/f47a4/src/navi10_enum.h'
CFMT_DEFAULT = 'C:/kyty/f287/f47a4/src/gfx10.json'


def xxh(data):
    return '%016x' % xxhash.xxh3_64_intdigest(data)


# ------------------------------------------------------------------------------------------------------------------
# Parsing

def tokens(rest):
    out = {}
    for tok in rest.split():
        if tok == '|' or '=' not in tok:
            continue
        k, v = tok.split('=', 1)
        out[k] = v
    return out


def parse(lines):
    """Returns dict with draws {(n,d): {...}}, srcres {useq: (sst, sh)}, capped [..], stat {..}, mode {..}, errors []."""
    res = {'draws': {}, 'srcres': {}, 'capped': [], 'stat': None, 'mode': None, 'errors': [], 'orphans': []}
    for raw in lines:
        i = raw.find('F47dt')
        if i < 0:
            continue
        line = raw[i:].strip()
        if line.startswith('F47dtStat:'):
            res['stat'] = tokens(line[len('F47dtStat:'):])
            continue
        if not line.startswith('F47dt: '):
            continue
        rest = line[len('F47dt: '):]
        if rest.startswith('capped'):
            res['capped'].append(tokens(rest))
            continue
        if rest.startswith('mode='):
            res['mode'] = tokens(rest)
            continue
        t = tokens(rest)
        kind = t.get('kind')
        if kind == 'srcres':
            res['srcres'][t['useq']] = (t['sst'], t['sh'])
            continue
        if kind not in ('draw', 'img', 'buf', 'srt', 'reg', 'vk'):
            res['errors'].append('unknown line: ' + line[:80])
            continue
        key = (int(t['n']), int(t['d']))
        g = res['draws'].setdefault(key, {'draw': [], 'img': [], 'buf': [], 'srt': [], 'reg': [], 'vk': []})
        if kind == 'reg':
            regs = {k: v for k, v in t.items() if k not in ('kind', 'n', 'd', 'resets')}
            g['reg'].append(regs)
        elif kind == 'vk':
            g['vk'].append(parse_vk(rest))
        else:
            g[kind].append(t)
    # integrity: one header, one srt / reg / vk line, counts of img / buf lines = the header
    for key, g in res['draws'].items():
        if len(g['draw']) != 1:
            res['errors'].append('INTEGRITY %s: %d draw headers' % (key, len(g['draw'])))
            continue
        h = g['draw'][0]
        if len(g['img']) != int(h['images']) or len(g['buf']) != int(h['buffers']):
            res['errors'].append('INTEGRITY %s: img %d/%s buf %d/%s' % (key, len(g['img']), h['images'], len(g['buf']),
                                                                       h['buffers']))
        for k in ('reg', 'vk', 'srt'):
            if len(g[k]) != 1:
                res['errors'].append('INTEGRITY %s: %d %s lines' % (key, len(g[k]), k))
    return res


def parse_vk(rest):
    vk = {'slots': {}, 'rts': {}}
    for tok in rest.split():
        m = re.match(r'^t(\d+):(.*)$', tok)
        if m:
            vk['slots'][int(m.group(1))] = dict(x.split('=', 1) for x in m.group(2).split(','))
            continue
        m = re.match(r'^rt(\d+):(.*)$', tok)
        if m:
            vk['rts'][int(m.group(1))] = dict(x.split('=', 1) for x in m.group(2).split(','))
            continue
        if tok.startswith('depth='):
            vk['depth'] = dict(x.split(':', 1) for x in tok[len('depth='):].split(','))
            continue
        if '=' in tok:
            k, v = tok.split('=', 1)
            vk[k] = v
    return vk


# ------------------------------------------------------------------------------------------------------------------
# Own decoding tables

TYPE_VK = {'UNORM': 'Unorm', 'SNORM': 'Snorm', 'UINT': 'Uint', 'SINT': 'Sint', 'FLOAT': 'Sfloat', 'SRGB': 'Srgb',
           'USCALED': 'Uscaled', 'SSCALED': 'Sscaled'}


def img_name_to_vk(name):
    """IMG_FMT name without prefix -> (vk::to_string name, channel count) or (None, None)."""
    m = re.match(r'^BC([1-7])_(UNORM|SRGB|SNORM|UFLOAT|SFLOAT)$', name)
    if m:
        n, ty = int(m.group(1)), m.group(2)
        if n == 6:
            return ('Bc6H' + ty.capitalize() + 'Block', 3)
        if ty not in ('UNORM', 'SRGB', 'SNORM'):
            return (None, None)
        if n == 1:
            return ('Bc1Rgba' + TYPE_VK[ty] + 'Block', 4)
        return ('Bc%d%sBlock' % (n, TYPE_VK[ty]), {2: 4, 3: 4, 4: 1, 5: 2, 7: 4}[n])
    parts = name.split('_')
    ty = parts[-1]
    bits = parts[:-1]
    if ty not in TYPE_VK or not bits or not all(b.isdigit() for b in bits) or len(set(bits)) != 1 or len(bits) > 4:
        return (None, None)
    return (''.join('RGBA'[i] + bits[i] for i in range(len(bits))) + TYPE_VK[ty], len(bits))


def load_img_formats(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    table = {}
    for m in re.finditer(r'IMG_FMT_(\w+)\s*=\s*0x([0-9a-fA-F]+)', text):
        table[int(m.group(2), 16)] = m.group(1)
    return table


def load_color_formats(path):
    d = json.load(open(path, encoding='utf-8'))
    fmts = {e['value']: e['name'] for e in d['enums']['ColorFormat']['entries']}
    nums = {e['value']: e['name'] for e in d['enums']['SurfaceNumber']['entries']}
    return fmts, nums


def color_to_vk(fmt_name, num_name):
    m = re.match(r'^COLOR_([0-9_]+)$', fmt_name or '')
    ty = {'NUMBER_UNORM': 'UNORM', 'NUMBER_SNORM': 'SNORM', 'NUMBER_UINT': 'UINT', 'NUMBER_SINT': 'SINT',
          'NUMBER_FLOAT': 'FLOAT', 'NUMBER_SRGB': 'SRGB'}.get(num_name)
    if not m or ty is None:
        return (None, None)
    return img_name_to_vk(m.group(1) + '_' + ty)


BLEND_VK = {0: 'Zero', 1: 'One', 2: 'SrcColor', 3: 'OneMinusSrcColor', 4: 'SrcAlpha', 5: 'OneMinusSrcAlpha',
            6: 'DstAlpha', 7: 'OneMinusDstAlpha', 8: 'DstColor', 9: 'OneMinusDstColor', 10: 'SrcAlphaSaturate',
            13: 'ConstantColor', 14: 'OneMinusConstantColor', 15: 'Src1Color', 16: 'OneMinusSrc1Color',
            17: 'Src1Alpha', 18: 'OneMinusSrc1Alpha', 19: 'ConstantAlpha', 20: 'OneMinusConstantAlpha'}
COMB_VK = {0: 'Add', 1: 'Subtract', 2: 'Min', 3: 'Max', 4: 'ReverseSubtract'}
ZFUNC_VK = {0: 'Never', 1: 'Less', 2: 'Equal', 3: 'LessOrEqual', 4: 'Greater', 5: 'NotEqual', 6: 'GreaterOrEqual',
            7: 'Always'}
# COMP_SWAP of a 4-channel target: export component i (R, G, B, A) -> memory channel (F47a4 section 5.1, source F)
SWAP4 = {0: (0, 1, 2, 3), 1: (2, 1, 0, 3), 2: (3, 2, 1, 0), 3: (1, 2, 3, 0)}


def bits(v, lo, hi):
    return (v >> lo) & ((1 << (hi - lo + 1)) - 1)


def f32(word):
    return struct.unpack('<f', struct.pack('<I', word))[0]


# ------------------------------------------------------------------------------------------------------------------
# Comparisons of one draw (form (5))

class Ctx:
    def __init__(self, img_fmts, cfmts, srcres):
        self.img_fmts = img_fmts
        self.cfmts = cfmts
        self.srcres = srcres


def worst(results):
    vals = [r for r, _ in results if r != 'na']
    if 'ne' in vals:
        return 'ne'
    if 'und' in vals:
        return 'und'
    return 'eq'


def cmp_image_bytes(t, ctx):
    if 'ih' not in t:
        return ('und', 'no binding')
    if t['ih'] == '-':
        return ('und', 'no (i): ' + t.get('ihow', '?'))
    if t.get('gpumod') == '1':
        return ('und', 'gpu-modified image')
    if t.get('sk') in (None, 'norecord'):
        return ('und', 'no upload record')

    def src(p):
        st, h = t.get(p + 'st'), t.get(p + 'h')
        if st == 'pending':
            st, h = ctx.srcres.get(t.get(p + 'seq'), ('pending', '-'))
        return st, h

    cst, ch = src('s')
    if cst != 'hashed':
        return ('und', 'source %s (%s)' % (cst, t.get('swhy')))
    partial = t.get('spend', '0') != '0'
    if ch != t['ih']:
        if partial:
            return ('und', 'partial upload, (i) differs')
        return ('ne', 'image 0x%s: (i) %s != source (ii) %s (%s)' % (t.get('img', '?'), t['ih'], ch, t['sk']))
    if 'pk' in t:
        pst, ph = src('p')
        if pst != 'hashed' or ph != t['ih']:
            return ('und', 'earlier part of a deferred upload differs or not hashed')
    if partial:
        return ('und', 'partial upload')
    return ('eq', '')


def cmp_view(t, ctx):
    if t.get('cls') != 'sampled':
        return ('na', '')
    if 'fmt' not in t or t.get('view') != '1':
        return ('und', 'no T# or no view object')
    name = ctx.img_fmts.get(int(t['fmt']))
    exp, chans = img_name_to_vk(name) if name else (None, None)
    if exp is None:
        return ('und', 'T# format %s not decoded (%s)' % (t['fmt'], name))
    if t.get('bcsw', '0') != '0':
        return ('und', 'BC_SWIZZLE %s' % t['bcsw'])
    out = []
    if t['vfmt'] != exp:
        out.append(('ne', 'view format %s != T# %s (%s)' % (t['vfmt'], exp, name)))
    sel = {0: '0', 1: '1', 4: 'r', 5: 'g', 6: 'b', 7: 'a'}
    ds = [int(x) for x in t['dstsel'].split(',')]
    if any(x not in sel for x in ds):
        out.append(('und', 'dst_sel %s' % t['dstsel']))
    else:
        def norm(c):
            if c in 'rgba' and 'rgba'.index(c) >= chans:
                return '1' if c == 'a' else '0'
            return c
        expect = ''.join(norm(sel[x]) for x in ds)
        got = ''.join(norm('rgba'[k] if c == 'i' else c) for k, c in enumerate(t['vmap']))
        if expect != got:
            out.append(('ne', 'view swizzle %s != T# dst_sel %s' % (t['vmap'], expect)))
    lo, hi = (int(x) for x in t['lv'].split('..'))
    vb, vc = (int(x) for x in t['vlev'].split('+'))
    if hi >= int(t.get('ilv', '99')):
        out.append(('und', 'T# last level %d >= image levels %s' % (hi, t.get('ilv'))))
    elif (vb, vc) != (lo, hi - lo + 1):
        out.append(('ne', 'view levels %d+%d != T# %d..%d' % (vb, vc, lo, hi)))
    if not out:
        return ('eq', '')
    r = worst(out)
    return (r, '; '.join(x[1] for x in out if x[0] == r))


def cmp_buffer(t):
    if 'gh' not in t:
        return ('und', 'no binding')
    if t.get('given') == 'null' or t['gh'] == '-' and t.get('ghow') == 'zero':
        return ('na', '')
    if t['gh'] == '-':
        return ('und', 'guest range not read: ' + t.get('ghow', '?'))
    if t.get('given') != 'ring_copy':
        return ('und', 'given %s (%s)' % (t.get('given'), t.get('gvh')))
    if not re.match(r'^[0-9a-f]{16}$', t.get('gvh', '')):
        return ('und', 'ring bytes %s' % t.get('gvh'))
    if t['gvh'] != t['gh']:
        return ('ne', 'buffer 0x%s: guest %s != given %s' % (t.get('addr', '?'), t['gh'], t['gvh']))
    return ('eq', '')


def cmp_srt(t):
    out = []
    if t.get('fresh') != 'ok':
        out.append(('und', 'SRT guest now: %s' % t.get('fresh')))
    else:
        for k in ('same_srt', 'same_img', 'same_buf', 'same_smp', 'same_ud'):
            if t.get(k) != '1':
                out.append(('ne', 'snapshot of the draw != materialization from guest now (%s=0)' % k))
    if t.get('given') == 'ring_copy' and re.match(r'^[0-9a-f]{16}$', t.get('gvh', '')) and t['gvh'] != t.get('snaph'):
        out.append(('ne', 'SRT ring bytes %s != snapshot %s' % (t['gvh'], t.get('snaph'))))
    if not out:
        return ('eq', '')
    r = worst(out)
    return (r, '; '.join(x[1] for x in out if x[0] == r))


def reg(regs, name):
    v = regs.get(name)
    if v is None or v in ('U', 'R'):
        return None
    return int(v, 16)


def cmp_so(regs, vk, ctx):
    """Blend, mask, colour format, viewport, scissor, depth, cull, alpha-to-mask: registers (own decoding) vs Vulkan."""
    out = []
    if vk.get('key') != '1':
        return [('und', 'no pipeline key')]
    mode = reg(regs, 'CB_COLOR_CONTROL')
    tmask = reg(regs, 'CB_TARGET_MASK')
    for slot, s in sorted(vk['slots'].items()):
        rt = next((r for r in vk['rts'].values() if int(r['slot']) == slot), None)
        if rt is None:
            continue
        bc = reg(regs, 'CB_BLEND%d_CONTROL' % slot)
        info = reg(regs, 'CB_COLOR%d_INFO' % slot)
        if bc is None or info is None or tmask is None or mode is None:
            out.append(('und', 'slot %d: register word not written / cleared' % slot))
            continue
        # colour target format
        fname = ctx.cfmts[0].get(bits(info, 2, 6))
        nname = ctx.cfmts[1].get(bits(info, 8, 10))
        exp, _ = color_to_vk(fname, nname)
        swap = bits(info, 11, 12)
        if exp is None:
            out.append(('und', 'slot %d: target format %s/%s not decoded' % (slot, fname, nname)))
        elif s['fmt'] != exp:
            out.append(('und' if swap != 0 else 'ne', 'slot %d: target format %s != %s/%s (swap %d)' % (slot, s['fmt'],
                                                                                                     fname, nname, swap)))
        # CB mode and ROP3
        if bits(mode, 4, 6) == 0 and rt['cwe'] == '1':
            out.append(('ne', 'CB_COLOR_CONTROL.MODE DISABLE but colour write enabled'))
        elif bits(mode, 4, 6) not in (0, 1):
            out.append(('und', 'CB_COLOR_CONTROL.MODE %d' % bits(mode, 4, 6)))
        if bits(mode, 16, 23) not in (0xCC, 0):
            out.append(('und', 'ROP3 0x%02x' % bits(mode, 16, 23)))
        # write enable and mask (item 722(d)(2) / F47a4 section 5.3)
        nib = (tmask >> (4 * slot)) & 0xF
        if (nib != 0) != (rt['cwe'] == '1'):
            out.append(('ne', 'slot %d: TARGET_ENABLE %x vs colour write enable %s' % (slot, nib, rt['cwe'])))
        vmask = int(s['mask'], 16)
        moved = 0
        for i in range(4):
            if nib >> i & 1:
                moved |= 1 << SWAP4[swap][i]
        if moved == vmask:
            pass
        elif nib == vmask:
            out.append(('und', 'slot %d: mask %x equals the guest mask only without the COMP_SWAP transfer' % (slot, vmask)))
        else:
            out.append(('ne', 'slot %d: mask %x != guest %x (moved %x)' % (slot, vmask, nib, moved)))
        # blend
        enable = bits(bc, 30, 30) == 1 and bits(info, 16, 16) == 0
        if enable != (s['be'] == '1'):
            out.append(('ne', 'slot %d: blend enable guest %d vk %s' % (slot, enable, s['be'])))
        elif enable:
            sep = bits(bc, 29, 29)
            cs, co, cd = bits(bc, 0, 4), bits(bc, 5, 7), bits(bc, 8, 12)
            as_, ao, ad = (bits(bc, 16, 20), bits(bc, 21, 23), bits(bc, 24, 28)) if sep else (cs, co, cd)
            want = {'cs': BLEND_VK.get(cs), 'cd': BLEND_VK.get(cd), 'co': COMB_VK.get(co),
                    'as': BLEND_VK.get(as_), 'ad': BLEND_VK.get(ad), 'ao': COMB_VK.get(ao)}
            for k, v in want.items():
                if v is None:
                    out.append(('und', 'slot %d: %s guest code not in the table' % (slot, k)))
                elif s[k] != v:
                    out.append(('ne', 'slot %d: %s vk %s != guest %s' % (slot, k, s[k], v)))
    # viewport 0
    vp = [reg(regs, n) for n in ('PA_CL_VPORT_XSCALE', 'PA_CL_VPORT_XOFFSET', 'PA_CL_VPORT_YSCALE', 'PA_CL_VPORT_YOFFSET')]
    if vk.get('vp0') == 'clip_disable':
        out.append(('und', 'viewport: clip disable'))
    elif None in vp or 'vp0' not in vk:
        out.append(('und', 'viewport register not written'))
    else:
        xs, xo, ys, yo = (f32(v) for v in vp)
        want = (xo - xs, yo - ys, 2 * xs, 2 * ys)
        got = tuple(float(x) for x in vk['vp0'].split(','))
        if any(abs(a - b) > 1e-3 * max(1.0, abs(a)) for a, b in zip(want, got)):
            out.append(('ne', 'viewport %s != guest %s' % (vk['vp0'], ','.join('%g' % x for x in want))))
    # scissor 0
    out.append(cmp_scissor(regs, vk))
    # depth
    dc = reg(regs, 'DB_DEPTH_CONTROL')
    d = vk.get('depth')
    if d is not None and d.get('img') == '1':
        if dc is None:
            out.append(('und', 'DB_DEPTH_CONTROL not written'))
        else:
            z, zw, zf = bits(dc, 1, 1), bits(dc, 2, 2), bits(dc, 4, 6)
            if str(z) != d['test']:
                out.append(('ne', 'depth test vk %s guest %d' % (d['test'], z)))
            elif z and d['op'] != ZFUNC_VK[zf]:
                out.append(('ne', 'depth op vk %s guest %s' % (d['op'], ZFUNC_VK[zf])))
            if str(zw if z else 0) != d['write']:
                out.append(('und', 'depth write vk %s guest %d (other registers can disable it)' % (d['write'], zw)))
    # cull
    mc = reg(regs, 'PA_SU_SC_MODE_CNTL')
    if mc is None:
        out.append(('und', 'PA_SU_SC_MODE_CNTL not written'))
    else:
        for k, b in (('cull_front', 0), ('cull_back', 1), ('face', 2)):
            if vk.get(k) is not None and vk[k] != str(bits(mc, b, b)):
                out.append(('ne', '%s vk %s guest %d' % (k, vk[k], bits(mc, b, b))))
    # alpha to mask
    am = reg(regs, 'DB_ALPHA_TO_MASK')
    if am is not None and am & 1 and vk.get('samples', '1') != '1':
        out.append(('und', 'alpha to mask enabled with samples %s' % vk.get('samples')))
    return out


def cmp_scissor(regs, vk):
    if 'sc0' not in vk or vk['sc0'] == '-' or 'ext' not in vk:
        return ('und', 'no scissor / extent in the vk line')
    names = ('PA_SC_SCREEN_SCISSOR_TL', 'PA_SC_SCREEN_SCISSOR_BR', 'PA_SC_WINDOW_SCISSOR_TL', 'PA_SC_WINDOW_SCISSOR_BR',
             'PA_SC_GENERIC_SCISSOR_TL', 'PA_SC_GENERIC_SCISSOR_BR', 'PA_SC_VPORT_SCISSOR_0_TL',
             'PA_SC_VPORT_SCISSOR_0_BR', 'PA_SC_WINDOW_OFFSET', 'PA_SC_MODE_CNTL_0')
    v = {n: reg(regs, n) for n in names}
    if v['PA_SC_SCREEN_SCISSOR_TL'] is None or v['PA_SC_SCREEN_SCISSOR_BR'] is None:
        return ('und', 'screen scissor not written')
    ox = v['PA_SC_WINDOW_OFFSET'] or 0
    off_x, off_y = struct.unpack('<hh', struct.pack('<I', ox))

    def rect(tl, br, mask, offset):
        x0, y0 = tl & mask, (tl >> 16) & mask
        x1, y1 = br & mask, (br >> 16) & mask
        if offset and not (tl >> 31) & 1:
            x0, x1, y0, y1 = x0 + off_x, x1 + off_x, y0 + off_y, y1 + off_y
        return [x0, y0, x1, y1]

    r = rect(v['PA_SC_SCREEN_SCISSOR_TL'], v['PA_SC_SCREEN_SCISSOR_BR'], 0xFFFF, False)
    parts = [('PA_SC_WINDOW_SCISSOR_TL', 'PA_SC_WINDOW_SCISSOR_BR'), ('PA_SC_GENERIC_SCISSOR_TL', 'PA_SC_GENERIC_SCISSOR_BR')]
    mc0 = v['PA_SC_MODE_CNTL_0']
    if mc0 is not None and (mc0 >> 1) & 1:
        parts.append(('PA_SC_VPORT_SCISSOR_0_TL', 'PA_SC_VPORT_SCISSOR_0_BR'))
    for tl, br in parts:
        if v[tl] is None or v[br] is None:
            continue  # never written in this context: the reset value (no restriction) [I]
        q = rect(v[tl], v[br], 0x7FFF, True)
        r = [max(r[0], q[0]), max(r[1], q[1]), min(r[2], q[2]), min(r[3], q[3])]
    w, h = (int(x) for x in vk['ext'].split(','))
    r = [max(r[0], 0), max(r[1], 0), min(r[2], w), min(r[3], h)]
    if r[2] < r[0]:
        r[2] = r[0]
    if r[3] < r[1]:
        r[3] = r[1]
    got = [int(x) for x in vk['sc0'].split(',')]
    if got != r:
        return ('ne', 'scissor vk %s != guest %s' % (vk['sc0'], ','.join(map(str, r))))
    return ('eq', '')


def evaluate_draw(g, ctx):
    rows = []
    for t in g['img']:
        rows.append(('img%s:bytes' % t['i'],) + cmp_image_bytes(t, ctx))
        rows.append(('img%s:view' % t['i'],) + cmp_view(t, ctx))
    for t in g['buf']:
        rows.append(('buf%s' % t['i'],) + cmp_buffer(t))
    if g['srt']:
        rows.append(('srt',) + cmp_srt(g['srt'][0]))
    if g['reg'] and g['vk']:
        for r in cmp_so(g['reg'][0], g['vk'][0], ctx):
            rows.append(('so',) + r)
    verdict = worst([(r[1], r[2]) for r in rows])
    return verdict, rows


def signature(g):
    """The measured values of a draw record (for P1): user data, image ranges and (i), buffer (i), SRT, raw registers."""
    h = g['draw'][0]
    sig = [h.get('ud')]
    sig += [(t.get('img'), t.get('ih')) for t in g['img']]
    sig += [(t.get('addr'), t.get('gh')) for t in g['buf']]
    sig += [g['srt'][0].get('snaph') if g['srt'] else None]
    sig += [tuple(sorted(g['reg'][0].items())) if g['reg'] else None]
    return tuple(sig)


# ------------------------------------------------------------------------------------------------------------------
# Files and N+-

def check_files(res, files_dir):
    """Every file a line names (ifile / gfile new or dup) exists and hashes to the hash of the line."""
    errs, checked = [], 0
    for key, g in res['draws'].items():
        for kind, hk, fk, ak in (('img', 'ih', 'ifile', 'img'), ('buf', 'gh', 'gfile', 'addr')):
            for t in g[kind]:
                if t.get(fk) not in ('new', 'dup'):
                    continue
                addr = int(t[ak].split('+')[0], 16)
                path = os.path.join(files_dir, '%016x_%s.bin' % (addr, t[hk]))
                if not os.path.exists(path):
                    errs.append('FILE_MISSING %s %s' % (key, path))
                    continue
                checked += 1
                if xxh(open(path, 'rb').read()) != t[hk]:
                    errs.append('FILE_MISMATCH %s %s' % (key, path))
    return errs, checked


def npm(res, files_dir, block, seed=740):
    """N+-: one byte of a copy of a block-show (i) file flipped at 10 positions -> a hash != the line, 10 of 10."""
    paths = []
    for (n, d), g in sorted(res['draws'].items()):
        if n not in block:
            continue
        for t in g['img']:
            if t.get('ifile') in ('new', 'dup'):
                p = os.path.join(files_dir, '%016x_%s.bin' % (int(t['img'].split('+')[0], 16), t['ih']))
                if os.path.exists(p):
                    paths.append((p, t['ih']))
    if not paths:
        return 0, 'no block (i) file'
    rnd = random.Random(seed)
    hit = 0
    for k in range(10):
        p, h = paths[k % len(paths)]
        data = bytearray(open(p, 'rb').read())
        pos = rnd.randrange(len(data))
        data[pos] ^= 1 << rnd.randrange(8)
        if xxh(bytes(data)) != h:
            hit += 1
    return hit, '%d files' % len(set(x[0] for x in paths))


# ------------------------------------------------------------------------------------------------------------------
# Rule (6)

def read_rule(res, ctx, block, white, stand_ok, files_dir):
    lines = []
    draws = {k: g for k, g in res['draws'].items() if not any(e.startswith('INTEGRITY %s' % (k,)) for e in res['errors'])}
    evals = {k: evaluate_draw(g, ctx) for k, g in draws.items()}
    ne = []
    shows = {}
    for (n, d), (v, rows) in sorted(evals.items()):
        if n in block:
            shows.setdefault(n, []).append(v)
            for r in rows:
                if r[1] == 'ne':
                    ne.append('n=%d d=%d %s: %s' % (n, d, r[0], r[2]))
    capped = len(res['capped']) > 0 or (res['stat'] is not None and res['stat'].get('capped') == '1')
    file_errs, checked = check_files(res, files_dir) if files_dir else ([], 0)
    hit, why = npm(res, files_dir, block) if files_dir else (0, 'no --files')
    black_sigs = {signature(draws[k]) for k in draws if k[0] in block}
    white_sigs = {signature(draws[k]) for k in draws if k[0] in white}
    p1 = bool(white_sigs) and bool(white_sigs - black_sigs)
    show_v = {n: ('ne' if 'ne' in vs else ('und' if 'und' in vs else 'eq')) for n, vs in shows.items()}
    lines.append('shows of the block with H draws: %s; without: %s' % (
        ' '.join('%d:%s' % (n, show_v[n]) for n in sorted(show_v)),
        ' '.join(str(n) for n in sorted(set(block) - set(show_v))) or '-'))
    lines.append('integrity errors %d; files checked %d, file errors %d; capped %d; N+- %d of 10 (%s); stand %s; P1 %s'
                 ' (white draws %d, signatures not in black %d)' % (
                     len(res['errors']), checked, len(file_errs), 1 if capped else 0, hit, why,
                     'ALIVE' if stand_ok else 'DEAD', 'ALIVE' if p1 else 'DEAD',
                     sum(1 for k in draws if k[0] in white), len(white_sigs - black_sigs)))
    if res['errors'] or file_errs:
        return 'INVALID', lines + res['errors'] + file_errs
    if ne:
        return 'DEFECT (6)(1)', lines + ne
    dead = []
    if not shows:
        dead.append('no H record in the block shows')
    if capped:
        dead.append('capped')
    if not stand_ok:
        dead.append('stand dead')
    if hit != 10:
        dead.append('N+- %d of 10' % hit)
    if not p1:
        dead.append('P1 dead')
    if dead:
        return 'DEAD_END (6)(3)', lines + dead
    missing = sorted(set(block) - set(show_v))
    if all(v == 'eq' for v in show_v.values()) and not missing:
        return 'NOT_A_DEFECT (6)(2)', lines
    # A block show without an H record is not evaluated: "und" (rule (6)(4) reads the worst show).
    und = ['n=%d: no H record in this block show' % n for n in missing]
    und += ['n=%d d=%d %s: %s' % (n, d, r[0], r[2]) for (n, d), (v, rows) in sorted(evals.items()) if n in block
            for r in rows if r[1] == 'und']
    return 'UNDETERMINED (6)(4)', lines + und[:50]


def table(res, ctx):
    out = []
    for (n, d), g in sorted(res['draws'].items()):
        if len(g['draw']) != 1:
            continue
        v, rows = evaluate_draw(g, ctx)
        counts = {}
        for r in rows:
            counts[r[1]] = counts.get(r[1], 0) + 1
        out.append('n=%d d=%d ps=%s ready=%s images=%s buffers=%s verdict=%s eq=%d ne=%d und=%d na=%d' % (
            n, d, g['draw'][0]['ps'], g['draw'][0]['ready'], g['draw'][0]['images'], g['draw'][0]['buffers'], v,
            counts.get('eq', 0), counts.get('ne', 0), counts.get('und', 0), counts.get('na', 0)))
        for r in rows:
            if r[1] in ('ne', 'und'):
                out.append('    %s %s: %s' % (r[1], r[0], r[2]))
    return out


def stand_alive(path):
    if not path or not os.path.exists(path):
        return False
    lines = [l.strip() for l in open(path, encoding='utf-8', errors='replace') if l.strip()]
    return bool(lines) and lines[-1] == 'ALL OK'


def main_table(argv):
    log = argv[0]
    opts = {'--files': None, '--block': '', '--white': '', '--stand': None, '--enum': ENUM_DEFAULT,
            '--cfmt': CFMT_DEFAULT, '--out': None}
    i = 1
    while i < len(argv):
        opts[argv[i]] = argv[i + 1]
        i += 2
    res = parse(open(log, 'rb').read().decode('utf-8', 'replace').split('\n'))
    ctx = Ctx(load_img_formats(opts['--enum']), load_color_formats(opts['--cfmt']), res['srcres'])
    out = ['log %s sha256 %s' % (log, hashlib.sha256(open(log, 'rb').read()).hexdigest()),
           'enum %s sha256 %s; cfmt %s sha256 %s' % (opts['--enum'], hashlib.sha256(open(opts['--enum'], 'rb').read()).hexdigest()[:16],
                                                    opts['--cfmt'], hashlib.sha256(open(opts['--cfmt'], 'rb').read()).hexdigest()[:16]),
           'mode %s' % res['mode'], 'stat %s' % res['stat'], 'capped lines %d' % len(res['capped'])]
    out += table(res, ctx)
    if opts['--block']:
        block = [int(x) for x in opts['--block'].split(',') if x]
        white = [int(x) for x in opts['--white'].split(',') if x]
        verdict, lines = read_rule(res, ctx, block, white, stand_alive(opts['--stand']), opts['--files'])
        out.append('RULE (6): ' + verdict)
        out += ['    ' + l for l in lines]
    text = '\n'.join(out) + '\n'
    sys.stdout.write(text)
    if opts['--out']:
        open(opts['--out'], 'w', encoding='utf-8', newline='\n').write(text)


# ------------------------------------------------------------------------------------------------------------------
# Fixtures (synthetic logs in the exact line forms of diagF47Dt.cpp) and mutations

def fx_ctx():
    img = {0xb6: 'BC7_SRGB', 0xaf: 'BC4_UNORM', 0x38: '8_8_8_8_UNORM', 0x82: '8_8_8_8_SRGB'}
    cf = ({0x0c: 'COLOR_16_16_16_16', 0x0a: 'COLOR_8_8_8_8'}, {0: 'NUMBER_UNORM', 7: 'NUMBER_FLOAT'})
    return img, cf


REGS_OK = {
    'CB_BLEND0_CONTROL': (1 << 30) | (1 << 29) | 1 | (0 << 5) | (5 << 8) | (0 << 16) | (0 << 21) | (5 << 24),
    'CB_TARGET_MASK': 0xF, 'CB_SHADER_MASK': 0xF, 'CB_COLOR_CONTROL': (1 << 4) | (0xCC << 16),
    'CB_COLOR0_INFO': (0x0c << 2) | (7 << 8), 'DB_ALPHA_TO_MASK': 0,
    'PA_CL_VPORT_XSCALE': struct.unpack('<I', struct.pack('<f', 1920.0))[0],
    'PA_CL_VPORT_XOFFSET': struct.unpack('<I', struct.pack('<f', 1920.0))[0],
    'PA_CL_VPORT_YSCALE': struct.unpack('<I', struct.pack('<f', 1080.0))[0],
    'PA_CL_VPORT_YOFFSET': struct.unpack('<I', struct.pack('<f', 1080.0))[0],
    'PA_SC_SCREEN_SCISSOR_TL': 0, 'PA_SC_SCREEN_SCISSOR_BR': (2160 << 16) | 3840,
    'PA_SC_WINDOW_OFFSET': 0, 'PA_SC_WINDOW_SCISSOR_TL': 1 << 31, 'PA_SC_WINDOW_SCISSOR_BR': (2160 << 16) | 3840,
    'PA_SC_GENERIC_SCISSOR_TL': 1 << 31, 'PA_SC_GENERIC_SCISSOR_BR': (2160 << 16) | 3840,
    'PA_SC_MODE_CNTL_0': 0, 'DB_DEPTH_CONTROL': 0, 'PA_SU_SC_MODE_CNTL': 0}


def fx_draw(n, d, files, data, ud='00000001,00000002', reg_over=None, img_over=None, buf_over=None, srt_over=None,
            vk_over=None):
    """Lines of one draw: 1 image (BC7 atlas), 1 buffer (ring copy), srt, reg, vk. data: bytes of the image range."""
    ih = xxh(data)
    addr = 0x1000000 + 0x100000 * (d % 7)
    fname = os.path.join(files, '%016x_%s.bin' % (addr, ih))
    if not os.path.exists(fname):
        open(fname, 'wb').write(data)
    img = {'kind': 'img', 'n': n, 'd': d, 'i': 0, 'cls': 'sampled', 'raw': '0,0,0,0,0,0,0,0', 'base': '0x%010x' % addr,
           'fmt': 182, 'w': 1920, 'h': 2048, 'dep': 1, 'lv': '0..11', 'maxmip': 11, 'tile': 27, 'type': 9,
           'dstsel': '4,5,6,7', 'minlod': 0, 'bcsw': 0, 'pitchx': 0, 'id': 5, 'img': '0x%010x+0x%x' % (addr, len(data)),
           'pix': 'Bc7SrgbBlock', 'ilv': 12, 'ilay': 1, 'view': 1, 'vfmt': 'Bc7SrgbBlock', 'vmap': 'iiii',
           'vtype': '2D', 'vlev': '0+12', 'vlay': '0+1', 'vminlod': 0, 'mipviews': 0, 'cpu': 0, 'maybe': 0, 'bufmod': 0,
           'gpumod': 0, 'cache_ok': 1, 'pend': 0, 'ih': ih, 'ihow': 'map', 'igc': 1, 'ifile': 'new', 'sk': 'import',
           'sst': 'hashed', 'swhy': 'import_at_record', 'sh': ih, 'sexact': 0, 'sn': 5, 'sd': 1, 'sseq': 1,
           'slv': '0+12', 'spend': 0, 'scomp': 0, 'cmp': 'eq', 'upl_now': 0}
    img.update(img_over or {})
    buf = {'kind': 'buf', 'n': n, 'd': d, 'i': 0, 'rw': 0, 'raw': '0,0,0,0', 'base': '0x000002000000', 'stride': 16,
           'records': 4, 'vsize': '0x40', 'fmt': 0, 'addr': '0x000002000000', 'size': '0x40', 'gh': '1111111111111111',
           'ghow': 'map', 'gfile': '-', 'given': 'ring_copy', 'goff': '0x0', 'grange': '0x40', 'gvh': '1111111111111111'}
    buf.update(buf_over or {})
    srt = {'kind': 'srt', 'n': n, 'd': d, 'words': 8, 'snaph': '2222222222222222', 'given': 'ring_copy',
           'gvh': '2222222222222222', 'fresh': 'ok', 'fh': '2222222222222222', 'same_srt': 1, 'same_img': 1,
           'same_buf': 1, 'same_smp': 1, 'same_ud': 1, 'shader_data': 0, 'sdh': '-'}
    srt.update(srt_over or {})
    regs = dict(REGS_OK)
    regs.update(reg_over or {})
    vk = {'t0': 'fmt=R16G16B16A16Sfloat,mask=f,be=1,cs=One,cd=OneMinusSrcAlpha,co=Add,as=Zero,ad=OneMinusSrcAlpha,'
                'ao=Add,g=1/0/5/0/0/5/1',
          'rt0': 'slot=0,img=0x0003000000,vfmt=R16G16B16A16Sfloat,cwe=1,export=0x00', 'vp0': '0,0,3840,2160',
          'sc0': '0,0,3840,2160', 'ext': '3840,2160', 'colors': 1, 'samples': 1, 'cull_front': 0, 'cull_back': 0,
          'face': 0, 'poly': 'Fill', 'dfmt': 'Undefined', 'depth': 'img:0,test:0,write:0,op:Never'}
    vk.update(vk_over or {})

    def kv(dct):
        return ' '.join('%s=%s' % (k, v) for k, v in dct.items())

    lines = ['F47dt: kind=draw n=%d d=%d gf=1 submit=1 draw=DrawIndex ps=45942b26d9ffbe8e vs=0000000000000001 idx=6 '
             'inst=1 ready=1 images=1 buffers=1 samplers=1 ud=2:%s' % (n, d, ud)]
    lines.append('F47dt: ' + kv(img))
    lines.append('F47dt: ' + kv(buf))
    lines.append('F47dt: ' + kv(srt))
    lines.append('F47dt: kind=reg n=%d d=%d ' % (n, d) + ' '.join(
        '%s=%s' % (k, v if isinstance(v, str) else '%08x' % v) for k, v in regs.items()) + ' resets=0')
    vk_line = 'F47dt: kind=vk n=%d d=%d key=1 colors=%s samples=%s cull_front=%s cull_back=%s face=%s poly=%s dfmt=%s ' % (
        n, d, vk['colors'], vk['samples'], vk['cull_front'], vk['cull_back'], vk['face'], vk['poly'], vk['dfmt'])
    vk_line += 't0:%s rt0:%s depth=%s vp0=%s sc0=%s ext=%s' % (vk['t0'], vk['rt0'], vk['depth'], vk['vp0'], vk['sc0'],
                                                             vk['ext'])
    lines.append(vk_line)
    return lines


def fx_log(files, black=(757, 772), white=(764,), **over):
    """A tag log: H draws in the black shows (data B) and the white show (data W, other user data)."""
    lines = ['F47dt: mode=1 ps=45942b26d9ffbe8e frames=700-1000 hash=xxh3_64 cap=2147483648 dir=_f47dt']
    data_b = bytes((i * 7) & 0xFF for i in range(4096))
    data_w = bytes((i * 11) & 0xFF for i in range(4096))
    for n in black:
        lines += fx_draw(n, 3, files, data_b, **over)
    for n in white:
        lines += fx_draw(n, 3, files, data_w, ud='00000001,00000009')
    lines.append('F47dtStat: when=exit draws=3 frames=3 files=2 bytes=8192 capped=0 imgs=3 bufs=3 pending=0')
    return lines


def run_fx(lines, files, stand=True, block=(757, 772), white=(764,)):
    img, cf = fx_ctx()
    res = parse(lines)
    ctx = Ctx(img, cf, res['srcres'])
    return read_rule(res, ctx, list(block), list(white), stand, files)


def selftest():
    ok = True
    tmp = tempfile.mkdtemp(prefix='dt_f47g_')

    def files():
        d = tempfile.mkdtemp(dir=tmp)
        return d

    def check(name, got, want_prefix):
        nonlocal ok
        good = got[0].startswith(want_prefix)
        ok &= good
        print('%s %s -> %s' % ('OK  ' if good else 'FAIL', name, got[0]))
        if not good:
            for l in got[1][:12]:
                print('      ' + l)

    # (2) everything equal, controls alive
    f = files()
    check('F2 all equal, stand / P1 / N+- alive', run_fx(fx_log(f), f), 'NOT_A_DEFECT')
    # (1) members
    cases = [
        ('F1a image (i) != source (ii)', {'img_over': {'sh': 'deadbeefdeadbeef'}}),
        ('F1b buffer guest != given', {'buf_over': {'gvh': '3333333333333333'}}),
        ('F1c view format != T#', {'img_over': {'vfmt': 'Bc7UnormBlock'}}),
        ('F1d view swizzle != T# dst_sel', {'img_over': {'vmap': 'grba'}}),
        ('F1e view levels != T#', {'img_over': {'vlev': '1+11'}}),
        ('F1f blend factor != CB_BLEND0', {'vk_over': {'t0': 'fmt=R16G16B16A16Sfloat,mask=f,be=1,cs=SrcAlpha,'
                                                             'cd=OneMinusSrcAlpha,co=Add,as=Zero,ad=OneMinusSrcAlpha,'
                                                             'ao=Add,g=4/0/5/0/0/5/1'}}),
        ('F1g write mask != CB_TARGET_MASK', {'vk_over': {'t0': 'fmt=R16G16B16A16Sfloat,mask=7,be=1,cs=One,'
                                                                'cd=OneMinusSrcAlpha,co=Add,as=Zero,'
                                                                'ad=OneMinusSrcAlpha,ao=Add,g=1/0/5/0/0/5/1'}}),
        ('F1h blend enable != CB_BLEND0.ENABLE', {'reg_over': {'CB_BLEND0_CONTROL': REGS_OK['CB_BLEND0_CONTROL'] & ~(1 << 30)}}),
        ('F1i viewport != PA_CL_VPORT', {'vk_over': {'vp0': '0,0,1920,1080'}}),
        ('F1j scissor != PA_SC_*', {'vk_over': {'sc0': '0,0,1920,2160'}}),
        ('F1k snapshot != guest now (SRT)', {'srt_over': {'same_srt': 0}}),
        ('F1l target format != CB_COLOR0_INFO', {'vk_over': {'t0': 'fmt=R8G8B8A8Unorm,mask=f,be=1,cs=One,'
                                                                   'cd=OneMinusSrcAlpha,co=Add,as=Zero,'
                                                                   'ad=OneMinusSrcAlpha,ao=Add,g=1/0/5/0/0/5/1'}}),
        ('F1m colour write enable != TARGET_ENABLE', {'reg_over': {'CB_TARGET_MASK': 0}}),
    ]
    for name, over in cases:
        f = files()
        check(name, run_fx(fx_log(f, **over), f), 'DEFECT')
    # (3)
    f = files()
    check('F3a no H record in the block shows', run_fx(fx_log(f), f, block=(800,)), 'DEAD_END')
    f = files()
    lines = fx_log(f)
    lines.insert(1, 'F47dt: capped n=757 d=3 addr=0x0001000000 size=0x1000 bytes=0 cap=0')
    check('F3b capped', run_fx(lines, f), 'DEAD_END')
    f = files()
    check('F3c stand dead', run_fx(fx_log(f), f, stand=False), 'DEAD_END')
    f = files()
    check('F3d P1 dead (white = black)', run_fx(fx_log(f, white=()), f, white=(757,)), 'DEAD_END')
    f = files()
    lines = [l.replace('ifile=new', 'ifile=capped') for l in fx_log(f)]
    check('F3e N+- dead (no (i) file)', run_fx(lines, f), 'DEAD_END')
    # (4)
    f = files()
    check('F4 und member (no plan for the SRT)', run_fx(fx_log(f, srt_over={'fresh': 'unmeasured:no_plan'}), f),
          'UNDETERMINED')
    f = files()
    check('F4b source pending without resolution', run_fx(fx_log(f, img_over={'sst': 'pending', 'sh': '-'}), f),
          'UNDETERMINED')
    # pending resolved by a srcres line
    f = files()
    lines = fx_log(f, img_over={'sst': 'pending', 'sh': '-', 'sseq': 77})
    ih = re.search(r' ih=([0-9a-f]{16})', lines[2]).group(1)
    lines.insert(1, 'F47dt: kind=srcres useq=77 addr=0x0001000000 size=0x1000 sst=hashed sh=%s n_res=757' % ih)
    check('F2b pending source resolved by srcres', run_fx(lines, f), 'NOT_A_DEFECT')

    # mutations of (v)(1)
    f = files()
    base = run_fx(fx_log(f), f)
    # m-file: one byte of an (i) file
    p = sorted(os.listdir(f))[0]
    data = bytearray(open(os.path.join(f, p), 'rb').read())
    data[100] ^= 0x01
    open(os.path.join(f, p), 'wb').write(bytes(data))
    check('M1 one byte of an (i) file corrupted', run_fx(fx_log(f), f), 'INVALID')
    # m-hash: the source hash of one line substituted
    f = files()
    check('M2 source hash substituted', run_fx(fx_log(f, img_over={'sh': '0123456789abcdef'}), f), 'DEFECT')
    # m-shift: n of one line shifted -> integrity; n of a whole draw shifted out of the block -> outcome changes
    f = files()
    lines = fx_log(f)
    lines[2] = lines[2].replace('n=757 ', 'n=758 ', 1)
    check('M3a n of one line shifted', run_fx(lines, f), 'INVALID')
    f = files()
    lines = [l.replace('n=772 ', 'n=773 ') for l in fx_log(f)]
    check('M3b n of a whole draw shifted out of a block show', run_fx(lines, f), 'UNDETERMINED')
    # m-perm: components of the view permuted
    f = files()
    check('M4 view components permuted', run_fx(fx_log(f, img_over={'vmap': 'bgra'}), f), 'DEFECT')

    # own decoding tables against the sources (when present)
    if os.path.exists(ENUM_DEFAULT):
        t = load_img_formats(ENUM_DEFAULT)
        good = (t.get(0xb6) == 'BC7_SRGB' and t.get(0xaf) == 'BC4_UNORM' and t.get(0x38) == '8_8_8_8_UNORM'
                and img_name_to_vk('BC7_SRGB') == ('Bc7SrgbBlock', 4) and img_name_to_vk('BC4_UNORM') == ('Bc4UnormBlock', 1)
                and img_name_to_vk('8_8_8_8_SRGB') == ('R8G8B8A8Srgb', 4)
                and img_name_to_vk('16_16_16_16_FLOAT') == ('R16G16B16A16Sfloat', 4)
                and img_name_to_vk('5_6_5_UNORM') == (None, None))
        ok &= good
        print('%s T1 IMG_FMT table of navi10_enum.h (BC7_SRGB 0xb6, BC4_UNORM 0xaf, 8_8_8_8_UNORM 0x38)' % ('OK  ' if good else 'FAIL'))
    if os.path.exists(CFMT_DEFAULT):
        fm, nm = load_color_formats(CFMT_DEFAULT)
        inv = {v: k for k, v in fm.items()}
        good = color_to_vk('COLOR_16_16_16_16', 'NUMBER_FLOAT') == ('R16G16B16A16Sfloat', 4) and 'COLOR_16_16_16_16' in inv \
            and nm.get(7) == 'NUMBER_FLOAT'
        ok &= good
        print('%s T2 ColorFormat / SurfaceNumber of gfx10.json (COLOR_16_16_16_16 = %s, NUMBER_FLOAT = 7)' % (
            'OK  ' if good else 'FAIL', inv.get('COLOR_16_16_16_16')))
    shutil.rmtree(tmp, ignore_errors=True)
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'selftest':
        sys.exit(selftest())
    if len(sys.argv) >= 3 and sys.argv[1] == 'table':
        main_table(sys.argv[2:])
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
