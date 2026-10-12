"""dt_f47g2.py - reader of the "F47dt:" lines of KYTY_DIAG_F47DT (track F, F47g2 HPP-828, ROADMAP s122 item 742(v), (g);
port of dt_f47g.py of F47g HPP-824), own code: the rule of the outcome is item 740(v)(6) with the answers of item 742(g),
the form item 740(v)(5) with the reading lines of item 741(v).

    python dt_f47g2.py table <log> [--files DIR] [--block Q,Q,...] [--white Q,...] [--stand PATH] [--window A-B]
                                    [--enum PATH] [--cfmt PATH] [--out PATH]
    python dt_f47g2.py flips <log> --window A-B     the admission member of F47i (item 742(e)): ADMISSION OK / FAIL
    python dt_f47g2.py selftest      fixtures of every member of rule (6), mutations of (v)(1); prints ALL OK

table: one row per draw of the PS H (key q, d - q is the show the draw lands in, the q of the flip line of its frame,
RC1 of F47h) with the comparisons of form (5) and the verdict of the draw; with --block (show numbers of the black
series - the FrameTrace n of those shows, the video detector of the tag) and --white (white series) the reading of rule
(6): DEFECT (1) / NOT_A_DEFECT (2) / DEAD_END (3) / UNDETERMINED (4) / INVALID (not an outcome: stop and lead item,
item 742(g)(2)). --stand: the output of run_stand_f47g2.py of the binary of the tag (its last line must be ALL OK).
--files: the _f47dt/ directory of the tag; every file named by a line must hash (XXH3-64) to the hash of the line, and
the N+- member (one byte of a copy of a block (i) file flipped at 10 positions -> a different hash 10 of 10) is
evaluated there. --window: also print the admission member (flips).

Reading lines of item 742(g) and 741(v): P1 is read NARROWED (742(g)(1)): a white record is alive only when it differs
from the black records with the same draw number d by a value that is the SAME in all those black records (both
readings printed, the outcome by the narrowed one); "ne" of image bytes with cpu=1 or maybe=1 is "und" (742(g)(3));
blend factors with the constant colour (codes 13, 14, 19, 20) and dual-source (15-18) are "und" (RC5); a buffer with
ggpu=1, a ring copy the GPU made (gvh not a hash) and an SRT ring copy not hashed are "und" (RC3); an image whose
record belongs to another image (sk=other_image, sid != id) is "und" (RC2). The members of (6)(3) (records, capped,
stand, N+-, P1) are printed at every outcome.

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
    res = {'draws': {}, 'srcres': {}, 'capped': [], 'stat': None, 'mode': None, 'errors': [], 'orphans': [],
           'flips': [], 'shown': [], 'frametrace': []}
    for raw in lines:
        j = raw.find('FrameTrace: n=')
        if j >= 0:
            m = re.match(r'FrameTrace: n=(\d+)', raw[j:])
            if m:
                res['frametrace'].append(int(m.group(1)))
            continue
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
        if kind == 'flip':
            res['flips'].append((int(t['q']), int(t['rid']), int(t.get('path', '-1'))))
            continue
        if kind == 'shown':
            res['shown'].append((int(t['n']), int(t['rid'])))
            continue
        if kind == 'ringstand':
            continue
        if kind not in ('draw', 'img', 'buf', 'srt', 'reg', 'vk'):
            res['errors'].append('unknown line: ' + line[:80])
            continue
        if 'q' not in t:
            res['errors'].append('INTEGRITY line without q (not the F47g2 form): ' + line[:80])
            continue
        # RC1 of F47h: the key is the show q the draw lands in, not the n of the last present.
        key = (int(t['q']), int(t['d']))
        g = res['draws'].setdefault(key, {'draw': [], 'img': [], 'buf': [], 'srt': [], 'reg': [], 'vk': [], 'ns': set()})
        g['ns'].add(t.get('n'))
        if kind == 'reg':
            regs = {k: v for k, v in t.items() if k not in ('kind', 'q', 'n', 'd', 'resets')}
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
        if len(g['ns']) != 1:
            res['errors'].append('INTEGRITY %s: lines of one draw with different n %s' % (key, sorted(g['ns'], key=str)))
    return res


def admission(res, a, b):
    """Item 742(e) (RC1 of F47h): the flip lines with q in [a, b] go consecutively, and every one of them has the shown
    line of its request (rid) with n = q; the FrameTrace lines carry these n.  Returns (ok, lines)."""
    fl = sorted(f for f in res['flips'] if a <= f[0] <= b)
    qs = [f[0] for f in fl]
    shown = {}
    for n, rid in res['shown']:
        shown.setdefault(rid, []).append(n)
    ft = set(res['frametrace'])
    out = []
    ok = True
    if qs != list(range(a, b + 1)):
        ok = False
        missing = sorted(set(range(a, b + 1)) - set(qs))
        out.append('flip q in [%d, %d]: %d lines, missing %s, duplicates %d' % (
            a, b, len(qs), missing[:10] if missing else '-', len(qs) - len(set(qs))))
    bad = []
    for q, rid, path in fl:
        ns = shown.get(rid, [])
        if ns != [q]:
            bad.append('q=%d rid=%d shown n=%s' % (q, rid, ns or '-'))
    if bad:
        ok = False
        out.append('flip q != shown n of the same request: %d (%s)' % (len(bad), '; '.join(bad[:5])))
    no_ft = [q for q in qs if q not in ft]
    if res['frametrace'] and no_ft:
        ok = False
        out.append('q without a FrameTrace n line: %d (%s)' % (len(no_ft), no_ft[:10]))
    out.insert(0, 'ADMISSION %s: flips %d in [%d, %d], paths %s, shown lines %d, FrameTrace lines %d' % (
        'OK' if ok else 'FAIL', len(fl), a, b, sorted(set(f[2] for f in fl)), len(res['shown']),
        len(res['frametrace'])))
    return ok, out


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
BLEND_CONST = {13, 14, 19, 20}  # constant colour / alpha factors (RC5 of F47h)
BLEND_DUAL = {15, 16, 17, 18}   # dual-source factors (RC5 of F47h)
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
    if t.get('sk') == 'other_image' or (t.get('sid') not in (None, '-') and t.get('id') is not None
                                         and t['sid'].split(':')[0] != t['id']):
        # RC2 of F47h: the record belongs to another image of the same range.
        return ('und', 'record of another image (sid %s, bound id %s)' % (t.get('sid'), t.get('id')))

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
        if t.get('cpu') == '1' or t.get('maybe') == '1':
            # Item 742(g)(3) (F3): the tracker already saw a guest write after the last upload when the draw was
            # processed - (i) may carry bytes written after the draw was queued; not a defect candidate.
            return ('und', 'F3: (i) != (ii) with cpu=%s maybe=%s (image 0x%s)' % (t.get('cpu'), t.get('maybe'),
                                                                                  t.get('img', '?')))
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
    if t.get('ggpu') != '0':
        # RC3 of F47h: the range has GPU writes (or the flag is missing) - the guest bytes are not what the GPU holds.
        return ('und', 'guest range written by the GPU (ggpu=%s)' % t.get('ggpu'))
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
    if t.get('given') == 'ring_copy':
        if not re.match(r'^[0-9a-f]{16}$', t.get('gvh', '')):
            # RC3(v) of F47h: a ring copy that is not hashed is "not determined", not silently "equal".
            out.append(('und', 'SRT ring bytes %s' % t.get('gvh')))
        elif t['gvh'] != t.get('snaph'):
            out.append(('ne', 'SRT ring bytes %s != snapshot %s' % (t['gvh'], t.get('snaph'))))
    elif t.get('given') not in ('none',):
        out.append(('und', 'SRT given %s' % t.get('given')))
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
            codes = {'cs': cs, 'cd': cd, 'as': as_, 'ad': ad}
            for k, v in want.items():
                if k in codes and codes[k] in BLEND_CONST:
                    # RC5 of F47h, item 741(v)(5): the blend constant is not printed - not determined.
                    out.append(('und', 'slot %d: %s guest code %d uses the blend constant' % (slot, k, codes[k])))
                elif k in codes and codes[k] in BLEND_DUAL:
                    # RC5 of F47h: the dual-source rewrite is not reflected in the line - not determined.
                    out.append(('und', 'slot %d: %s guest code %d is dual-source' % (slot, k, codes[k])))
                elif v is None:
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


def components(g):
    """The measured values of a draw record (for P1): user data, per image the range, (i), raw T# and the view, per
    buffer the raw V#, range and (i), the SRT snapshot, the raw registers. A dict component -> value."""
    h = g['draw'][0]
    c = {('ud',): h.get('ud')}
    for t in g['img']:
        for k in ('img', 'ih', 'raw', 'vfmt', 'vmap', 'vlev', 'vtype', 'vlay'):
            c[('img', t.get('i'), k)] = t.get(k)
    for t in g['buf']:
        for k in ('raw', 'addr', 'gh'):
            c[('buf', t.get('i'), k)] = t.get(k)
    if g['srt']:
        c[('srt', 'snaph')] = g['srt'][0].get('snaph')
    if g['reg']:
        for k, v in g['reg'][0].items():
            c[('reg', k)] = v
    return c


def signature(g):
    """The full signature (the F47g reading of P1, printed as a reference)."""
    return tuple(sorted(components(g).items(), key=lambda kv: str(kv[0])))


def p1_narrowed(draws, block, white):
    """Item 742(g)(1): a white record is alive when it differs from the black records with the same draw number d by a
    value that is the SAME in all those black records (a value changing inside the black series does not count).
    Returns (alive, compared, example)."""
    black_by_d = {}
    for (q, d), g in draws.items():
        if q in block:
            black_by_d.setdefault(d, []).append(components(g))
    const_by_d = {}
    for d, comps in black_by_d.items():
        first = comps[0]
        const_by_d[d] = {k: v for k, v in first.items() if all(k in c and c[k] == v for c in comps[1:])}
    alive, compared, example = 0, 0, '-'
    for (q, d), g in sorted(draws.items()):
        if q not in white or d not in const_by_d:
            continue
        compared += 1
        wc = components(g)
        diff = [k for k, v in const_by_d[d].items() if wc.get(k) != v]
        if diff:
            alive += 1
            if example == '-':
                example = 'q=%d d=%d %s' % (q, d, '/'.join(str(x) for x in diff[0]))
    return alive, compared, example


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
    for (q, d), g in sorted(res['draws'].items()):
        if q not in block:
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

def ne_kind(row):
    name = row[0]
    if name.endswith(':bytes'):
        return 'img_bytes'
    if name.endswith(':view'):
        return 'img_view'
    return re.sub(r'\d+$', '', name)


def read_rule(res, ctx, block, white, stand_ok, files_dir):
    lines = []
    draws = {k: g for k, g in res['draws'].items() if not any(e.startswith('INTEGRITY %s' % (k,)) for e in res['errors'])}
    evals = {k: evaluate_draw(g, ctx) for k, g in draws.items()}
    ne = []
    shows = {}
    kinds = {}
    for (q, d), (v, rows) in sorted(evals.items()):
        if q in block:
            shows.setdefault(q, []).append(v)
            for r in rows:
                if r[1] == 'ne':
                    ne.append('q=%d d=%d %s: %s' % (q, d, r[0], r[2]))
                    kinds.setdefault(q, {}).setdefault(ne_kind(r), 0)
                    kinds[q][ne_kind(r)] += 1
                elif r[1] == 'und' and r[2].startswith('F3:'):
                    kinds.setdefault(q, {}).setdefault('img_bytes_cpu_F3', 0)
                    kinds[q]['img_bytes_cpu_F3'] += 1
    capped = len(res['capped']) > 0 or (res['stat'] is not None and res['stat'].get('capped') == '1')
    file_errs, checked = check_files(res, files_dir) if files_dir else ([], 0)
    hit, why = npm(res, files_dir, block) if files_dir else (0, 'no --files')
    black_sigs = {signature(draws[k]) for k in draws if k[0] in block}
    white_sigs = {signature(draws[k]) for k in draws if k[0] in white}
    p1_full = bool(white_sigs) and bool(white_sigs - black_sigs)
    alive, compared, example = p1_narrowed(draws, block, white)
    p1 = alive > 0
    show_v = {q: ('ne' if 'ne' in vs else ('und' if 'und' in vs else 'eq')) for q, vs in shows.items()}
    lines.append('shows of the block with H draws: %s; without: %s' % (
        ' '.join('%d:%s' % (q, show_v[q]) for q in sorted(show_v)),
        ' '.join(str(q) for q in sorted(set(block) - set(show_v))) or '-'))
    lines.append('ne by kind per show (F3 - ne with cpu=1/maybe=1 read as und): %s' % (
        ' '.join('%d:%s' % (q, ','.join('%s=%d' % kv for kv in sorted(kinds[q].items()))) for q in sorted(kinds)) or '-'))
    # The members of (6)(3) at every outcome (RC5 of F47h).
    lines.append('members (6)(3): H records in block shows %d; integrity errors %d; files checked %d, file errors %d;'
                 ' capped %d; N+- %d of 10 (%s); stand %s; P1 narrowed %s (white records compared %d, alive %d, e.g. %s);'
                 ' P1 full signature (reference) %s (white draws %d, signatures not in black %d)' % (
                     sum(len(v) for v in shows.values()), len(res['errors']), checked, len(file_errs), 1 if capped else 0,
                     hit, why, 'ALIVE' if stand_ok else 'DEAD', 'ALIVE' if p1 else 'DEAD', compared, alive, example,
                     'ALIVE' if p1_full else 'DEAD', sum(1 for k in draws if k[0] in white), len(white_sigs - black_sigs)))
    if res['errors'] or file_errs:
        # Item 742(g)(2) (F2): not an outcome of (6) - stop reading, lead item; a second INVALID of the same binary
        # for the same cause -> (6)(3).
        return 'INVALID', lines + ['stop: not an outcome of rule (6); lead item (item 742(g)(2))'] + res['errors'] + file_errs
    if ne:
        dead = [m for m, bad in (('stand dead', not stand_ok), ('N+- %d of 10' % hit, hit != 10), ('P1 dead', not p1),
                                 ('capped', capped)) if bad]
        if dead:
            lines.append('ne with a dead control member: %s (second reading for F47j)' % ', '.join(dead))
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
        dead.append('P1 dead (narrowed, item 742(g)(1))')
    if dead:
        return 'DEAD_END (6)(3)', lines + dead
    missing = sorted(set(block) - set(show_v))
    if all(v == 'eq' for v in show_v.values()) and not missing:
        return 'NOT_A_DEFECT (6)(2)', lines
    # A block show without an H record is not evaluated: "und" (rule (6)(4) reads the worst show).
    und = ['q=%d: no H record in this block show' % q for q in missing]
    und += ['q=%d d=%d %s: %s' % (q, d, r[0], r[2]) for (q, d), (v, rows) in sorted(evals.items()) if q in block
            for r in rows if r[1] == 'und']
    return 'UNDETERMINED (6)(4)', lines + und[:50]


def table(res, ctx):
    out = []
    for (q, d), g in sorted(res['draws'].items()):
        if len(g['draw']) != 1:
            continue
        v, rows = evaluate_draw(g, ctx)
        counts = {}
        for r in rows:
            counts[r[1]] = counts.get(r[1], 0) + 1
        out.append('q=%d n=%s d=%d ps=%s ready=%s images=%s buffers=%s verdict=%s eq=%d ne=%d und=%d na=%d' % (
            q, g['draw'][0].get('n'), d, g['draw'][0]['ps'], g['draw'][0]['ready'], g['draw'][0]['images'],
            g['draw'][0]['buffers'], v, counts.get('eq', 0), counts.get('ne', 0), counts.get('und', 0), counts.get('na', 0)))
        for r in rows:
            if r[1] in ('ne', 'und'):
                out.append('    %s %s: %s' % (r[1], r[0], r[2]))
    return out


def stand_alive(path):
    if not path or not os.path.exists(path):
        return False
    lines = [l.strip() for l in open(path, encoding='utf-8', errors='replace') if l.strip()]
    return bool(lines) and lines[-1] == 'ALL OK'


def window(text):
    a, b = text.split('-')
    return int(a), int(b)


def main_table(argv):
    log = argv[0]
    opts = {'--files': None, '--block': '', '--white': '', '--stand': None, '--enum': ENUM_DEFAULT,
            '--cfmt': CFMT_DEFAULT, '--out': None, '--window': None}
    i = 1
    while i < len(argv):
        opts[argv[i]] = argv[i + 1]
        i += 2
    res = parse(open(log, 'rb').read().decode('utf-8', 'replace').split('\n'))
    ctx = Ctx(load_img_formats(opts['--enum']), load_color_formats(opts['--cfmt']), res['srcres'])
    out = ['log %s sha256 %s' % (log, hashlib.sha256(open(log, 'rb').read()).hexdigest()),
           'reader %s sha256 %s' % (os.path.basename(__file__), hashlib.sha256(open(__file__, 'rb').read()).hexdigest()),
           'enum %s sha256 %s; cfmt %s sha256 %s' % (opts['--enum'], hashlib.sha256(open(opts['--enum'], 'rb').read()).hexdigest()[:16],
                                                    opts['--cfmt'], hashlib.sha256(open(opts['--cfmt'], 'rb').read()).hexdigest()[:16]),
           'mode %s' % res['mode'], 'stat %s' % res['stat'], 'capped lines %d' % len(res['capped'])]
    if opts['--window']:
        out += admission(res, *window(opts['--window']))[1]
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


def main_flips(argv):
    log = argv[0]
    opts = {'--window': None}
    i = 1
    while i < len(argv):
        opts[argv[i]] = argv[i + 1]
        i += 2
    res = parse(open(log, 'rb').read().decode('utf-8', 'replace').split('\n'))
    ok, lines = admission(res, *window(opts['--window']))
    sys.stdout.write('\n'.join(lines) + '\n')
    return 0 if ok else 1


# ------------------------------------------------------------------------------------------------------------------
# Fixtures (synthetic logs in the exact line forms of diagF47Dt.cpp F47g2) and mutations

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


def fx_draw(q, d, files, data, ud='00000001,00000002', reg_over=None, img_over=None, buf_over=None, srt_over=None,
            vk_over=None, n=None):
    """Lines of one draw: 1 image (BC7 atlas), 1 buffer (ring copy), srt, reg, vk. data: bytes of the image range.
    q: the show (key); n: the present number of the line (default q - 2: the draw is processed before its show)."""
    n = q - 2 if n is None else n
    ih = xxh(data)
    addr = 0x1000000 + 0x100000 * (d % 7)
    fname = os.path.join(files, '%016x_%s.bin' % (addr, ih))
    if not os.path.exists(fname):
        open(fname, 'wb').write(data)
    img = {'kind': 'img', 'q': q, 'n': n, 'd': d, 'i': 0, 'cls': 'sampled', 'raw': '0,0,0,0,0,0,0,0',
           'base': '0x%010x' % addr, 'fmt': 182, 'w': 1920, 'h': 2048, 'dep': 1, 'lv': '0..11', 'maxmip': 11, 'tile': 27,
           'type': 9, 'dstsel': '4,5,6,7', 'minlod': 0, 'bcsw': 0, 'pitchx': 0, 'id': 5,
           'img': '0x%010x+0x%x' % (addr, len(data)), 'pix': 'Bc7SrgbBlock', 'ilv': 12, 'ilay': 1, 'view': 1,
           'vfmt': 'Bc7SrgbBlock', 'vmap': 'iiii', 'vtype': '2D', 'vlev': '0+12', 'vlay': '0+1', 'vminlod': 0,
           'mipviews': 0, 'cpu': 0, 'maybe': 0, 'bufmod': 0, 'gpumod': 0, 'cache_ok': 1, 'pend': 0, 'ih': ih,
           'ihow': 'map', 'igc': 1, 'ifile': 'new', 'sid': '5:1', 'rlast': '5:1', 'sk': 'import', 'sst': 'hashed',
           'swhy': 'import_at_record', 'sh': ih, 'sexact': 0, 'sq': q, 'sn': 5, 'sd': 1, 'sseq': 1, 'slv': '0+12',
           'spend': 0, 'scomp': 0, 'cmp': 'eq', 'upl_now': 0}
    img.update(img_over or {})
    buf = {'kind': 'buf', 'q': q, 'n': n, 'd': d, 'i': 0, 'rw': 0, 'raw': '0,0,0,0', 'base': '0x000002000000',
           'stride': 16, 'records': 4, 'vsize': '0x40', 'fmt': 0, 'addr': '0x000002000000', 'size': '0x40',
           'gh': '1111111111111111', 'ghow': 'map', 'ggpu': 0, 'gfile': '-', 'given': 'ring_copy', 'goff': '0x0',
           'grange': '0x40', 'gvh': '1111111111111111'}
    buf.update(buf_over or {})
    srt = {'kind': 'srt', 'q': q, 'n': n, 'd': d, 'words': 8, 'snaph': '2222222222222222', 'given': 'ring_copy',
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

    lines = ['F47dt: kind=draw q=%d n=%d d=%d gf=1 submit=1 draw=DrawIndex ps=45942b26d9ffbe8e vs=0000000000000001 '
             'idx=6 inst=1 ready=1 images=1 buffers=1 samplers=1 ud=2:%s' % (q, n, d, ud)]
    lines.append('F47dt: ' + kv(img))
    lines.append('F47dt: ' + kv(buf))
    lines.append('F47dt: ' + kv(srt))
    lines.append('F47dt: kind=reg q=%d n=%d d=%d ' % (q, n, d) + ' '.join(
        '%s=%s' % (k, v if isinstance(v, str) else '%08x' % v) for k, v in regs.items()) + ' resets=0')
    vk_line = 'F47dt: kind=vk q=%d n=%d d=%d key=1 colors=%s samples=%s cull_front=%s cull_back=%s face=%s poly=%s ' \
              'dfmt=%s ' % (q, n, d, vk['colors'], vk['samples'], vk['cull_front'], vk['cull_back'], vk['face'],
                            vk['poly'], vk['dfmt'])
    vk_line += 't0:%s rt0:%s depth=%s vp0=%s sc0=%s ext=%s' % (vk['t0'], vk['rt0'], vk['depth'], vk['vp0'], vk['sc0'],
                                                             vk['ext'])
    lines.append(vk_line)
    return lines


def fx_log(files, black=(757, 772), white=(764,), white_ud='00000001,00000009', black_ud=None, **over):
    """A tag log: H draws in the black shows (data B) and the white show (data W, other user data).
    black_ud: a function q -> user data of the black draw (a value changing inside the black series)."""
    lines = ['F47dt: mode=1 ps=45942b26d9ffbe8e frames=700-1000 hash=xxh3_64 cap=2147483648 dir=_f47dt']
    data_b = bytes((i * 7) & 0xFF for i in range(4096))
    data_w = bytes((i * 11) & 0xFF for i in range(4096))
    for q in black:
        extra = dict(over)
        if black_ud is not None:
            extra['ud'] = black_ud(q)
        lines += fx_draw(q, 3, files, data_b, **extra)
    for q in white:
        lines += fx_draw(q, 3, files, data_w if white_ud != 'same_data' else data_b,
                         ud=white_ud if white_ud != 'same_data' else '00000001,00000002')
    lines.append('F47dtStat: when=exit draws=3 frames=3 files=2 bytes=8192 capped=0 imgs=3 bufs=3 pending=0 flips=0 '
                 'ring_gpu_notes=0')
    return lines


def run_fx(lines, files, stand=True, block=(757, 772), white=(764,)):
    img, cf = fx_ctx()
    res = parse(lines)
    ctx = Ctx(img, cf, res['srcres'])
    return read_rule(res, ctx, list(block), list(white), stand, files)


def fx_flips(a, b, skip=None, shift=None):
    """Flip / shown / FrameTrace lines of the shows a..b (skip: a q without a flip line; shift: a q whose shown n is
    q + 1)."""
    lines = []
    for q in range(a, b + 1):
        if q == skip:
            continue
        rid = 1000 + q
        lines.append('F47dt: kind=flip q=%d path=0 rid=%d n=%d' % (q, rid, q - 2))
        lines.append('F47dt: kind=shown n=%d rid=%d' % (q + 1 if q == shift else q, rid))
        lines.append('FrameTrace: n=%d dt_us=16667 lat_us=0' % q)
    return lines


def selftest():
    ok = True
    tmp = tempfile.mkdtemp(prefix='dt_f47g2_')

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

    def check_true(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        print('%s %s %s' % ('OK  ' if cond else 'FAIL', name, detail))

    # (2) everything equal, controls alive
    f = files()
    check('F2 all equal, stand / P1 / N+- alive', run_fx(fx_log(f), f), 'NOT_A_DEFECT')
    # (1) members
    cases = [
        ('F1a image (i) != source (ii), cpu=0 maybe=0 (m8: the defect candidate)', {'img_over': {'sh': 'deadbeefdeadbeef'}}),
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
    lines.insert(1, 'F47dt: kind=srcres useq=77 sid=5:1 addr=0x0001000000 size=0x1000 sst=hashed sh=%s q_res=757 '
                    'n_res=755' % ih)
    check('F2b pending source resolved by srcres', run_fx(lines, f), 'NOT_A_DEFECT')

    # F47g2: RC1 - the key is q, not n
    f = files()
    lines = fx_log(f)
    # the black draw of show 757 with the defect is processed while n = 755 (before its show): read by q it is in the
    # block; a reader keyed by n (m6 of the reader) would not see it
    lines = [l for l in lines if ' q=757 ' not in l] + fx_draw(757, 3, f, bytes((i * 7) & 0xFF for i in range(4096)),
                                                               img_over={'sh': 'deadbeefdeadbeef'}, n=755)
    check('G1 (RC1) ne of a draw with n=755 in the block show q=757 -> DEFECT by q', run_fx(lines, f), 'DEFECT')
    f = files()
    lines = [l.replace(' n=755 ', ' n=757 ', 1) if 'kind=buf' in l and ' q=757 ' in l else l for l in fx_log(f)]
    check('G1b (RC1) lines of one draw with different n -> INVALID', run_fx(lines, f), 'INVALID')
    res = parse(fx_flips(700, 710))
    check_true('G2 (RC1) admission: consecutive flips, shown n = q -> OK', admission(res, 700, 710)[0])
    res = parse(fx_flips(700, 710, skip=705))
    check_true('G2b (RC1) admission: a missing flip -> FAIL', not admission(res, 700, 710)[0])
    res = parse(fx_flips(700, 710, shift=703))
    check_true('G2c (RC1) admission: shown n != q of the same request -> FAIL', not admission(res, 700, 710)[0])
    # RC2 - a record of another image
    f = files()
    check('G3 (RC2) sk=other_image -> UNDETERMINED',
          run_fx(fx_log(f, img_over={'sk': 'other_image', 'sid': '9:1', 'sst': '-', 'sh': '-'}), f), 'UNDETERMINED')
    f = files()
    check('G3b (RC2) sid != bound id (m7 of the code read by the reader) -> UNDETERMINED',
          run_fx(fx_log(f, img_over={'sid': '9:1'}), f), 'UNDETERMINED')
    # RC3 - ring copies on the GPU, GPU-written guest ranges, the SRT ring not hashed
    f = files()
    check('G4 (RC3) buffer gvh=unmeasured:gpu_copy -> UNDETERMINED',
          run_fx(fx_log(f, buf_over={'gvh': 'unmeasured:gpu_copy'}), f), 'UNDETERMINED')
    f = files()
    check('G4b (RC3) buffer ggpu=1 (even with equal hashes) -> UNDETERMINED',
          run_fx(fx_log(f, buf_over={'ggpu': 1}), f), 'UNDETERMINED')
    f = files()
    check('G4c (RC3(v)) SRT ring gvh=unmeasured:gpu_copy -> UNDETERMINED (was silently equal)',
          run_fx(fx_log(f, srt_over={'gvh': 'unmeasured:gpu_copy'}), f), 'UNDETERMINED')
    f = files()
    check('G4d (RC3(b)) the old copy_in_flight value -> UNDETERMINED',
          run_fx(fx_log(f, buf_over={'gvh': 'copy_in_flight'}), f), 'UNDETERMINED')
    # RC5 - blend constant and dual-source
    for code, name in ((13, 'ConstantColor'), (14, 'OneMinusConstantColor'), (19, 'ConstantAlpha'),
                       (20, 'OneMinusConstantAlpha'), (15, 'Src1Color'), (16, 'OneMinusSrc1Color'),
                       (17, 'Src1Alpha'), (18, 'OneMinusSrc1Alpha')):
        bc = (1 << 30) | (1 << 29) | code | (0 << 5) | (5 << 8) | (0 << 16) | (0 << 21) | (5 << 24)
        f = files()
        check('G5 (RC5) source factor code %d (%s) equal in vk -> UNDETERMINED' % (code, name),
              run_fx(fx_log(f, reg_over={'CB_BLEND0_CONTROL': bc},
                            vk_over={'t0': 'fmt=R16G16B16A16Sfloat,mask=f,be=1,cs=%s,cd=OneMinusSrcAlpha,co=Add,as=Zero,'
                                           'ad=OneMinusSrcAlpha,ao=Add,g=%d/0/5/0/0/5/1' % (name, code)}), f),
              'UNDETERMINED')
    # RC5 - the members of (6)(3) printed at every outcome (DEFECT with a dead stand: the second reading)
    f = files()
    got = run_fx(fx_log(f, img_over={'sh': 'deadbeefdeadbeef'}), f, stand=False)
    check_true('G6 (RC5) DEFECT prints the members of (6)(3) and the dead control',
               got[0].startswith('DEFECT') and any(l.startswith('members (6)(3):') and 'stand DEAD' in l for l in got[1])
               and any(l.startswith('ne with a dead control member: stand dead') for l in got[1]), got[0])
    # F1 (item 742(g)(1)) - P1 narrowed
    f = files()
    lines = fx_log(f, white_ud='same_data', black_ud=lambda q: '00000001,%08x' % q)
    # white differs from black only in the user data, which changes inside the black series -> P1 dead (narrowed),
    # the full signature (reference) would call it alive
    got = run_fx(lines, f)
    check_true('G7 (F1) white differs only by a value changing inside the black series -> P1 narrowed DEAD, '
               'full ALIVE -> DEAD_END',
               got[0].startswith('DEAD_END') and any('P1 narrowed DEAD' in l and 'P1 full signature (reference) ALIVE' in l
                                                      for l in got[1]), got[0])
    f = files()
    lines = fx_log(f, black_ud=lambda q: '00000001,%08x' % q)
    got = run_fx(lines, f)
    check_true('G7b (F1) white differs by a value constant in the black series ((i) of the image) -> P1 narrowed ALIVE',
               got[0].startswith('NOT_A_DEFECT') and any('P1 narrowed ALIVE' in l for l in got[1]), got[0])
    # F2 (item 742(g)(2)) - INVALID is a stop, not an outcome
    f = files()
    lines = fx_log(f)
    lines[2] = lines[2].replace('q=757 ', 'q=758 ', 1)
    got = run_fx(lines, f)
    check_true('G8 (F2) INVALID prints the stop line', got[0] == 'INVALID' and any(
        l.startswith('stop: not an outcome of rule (6)') for l in got[1]), got[0])
    # F3 (item 742(g)(3)) - ne with cpu=1 / maybe=1 is und; with cpu=0 maybe=0 it is the defect (F1a above)
    f = files()
    check('G9 (F3) (i) != (ii) with cpu=1 -> UNDETERMINED (m8: read as defect)',
          run_fx(fx_log(f, img_over={'sh': 'deadbeefdeadbeef', 'cpu': 1}), f), 'UNDETERMINED')
    f = files()
    check('G9b (F3) (i) != (ii) with maybe=1 -> UNDETERMINED',
          run_fx(fx_log(f, img_over={'sh': 'deadbeefdeadbeef', 'maybe': 1}), f), 'UNDETERMINED')

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
    # m-shift: q of one line shifted -> integrity; q of a whole draw shifted out of the block -> outcome changes
    f = files()
    lines = fx_log(f)
    lines[2] = lines[2].replace('q=757 ', 'q=758 ', 1)
    check('M3a q of one line shifted', run_fx(lines, f), 'INVALID')
    f = files()
    lines = [l.replace('q=772 ', 'q=773 ') for l in fx_log(f)]
    check('M3b q of a whole draw shifted out of a block show', run_fx(lines, f), 'UNDETERMINED')
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
    if len(sys.argv) >= 3 and sys.argv[1] == 'flips':
        sys.exit(main_flips(sys.argv[2:]))
    print(__doc__)
    sys.exit(2)
