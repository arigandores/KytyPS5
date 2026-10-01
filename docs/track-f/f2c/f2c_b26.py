"""F2c (HPP-310), track F: B26b profile reader of one emulator log - ROADMAP p.237(g)(4),(5)(a),(v),(g) and F2b RC3.

Reads only what p.237(g) adds to the sealed s142 reading (sc142.py is not changed and not copied):
  - opcode profile by the pair (family, opcode) of 'opcode is not implemented' lines (RC3(1); VOPC 0xf3 is its own row);
  - per B26b hash (5): the CsPretranslate 'ready' / 'skipped' lines - exactly one per hash, else 'not counted' (RC3(2));
    a skip prints its mechanism and pc (RC3(3));
  - positive control of the knob: the 'Shader translation cache:' line - variant_fixb26 at =1, the root PPSA21564 at =0 (RC3(4));
  - 'lowered its phi to a host-evaluated select' lines - expected, not a marker (RC3(5));
  - B26a reopen check p.237(v)(2): 'CsPretranslate: miss|hit' with a hash of the 96, 'shader CFG build failed' outside
    'CsPretranslate:', death of the process from the translator (RC3(6)).
Output: ASCII only.
"""
import hashlib
import json
import re
import sys

TSV = 'C:/kyty/f287/f1a/b26_shaders.tsv'
CHUNK = 1 << 26
BASE0 = {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4}
FIXED_OPS = (('SOP1', '0x0c'), ('VOPC', '0xe3'))
M_OPC = b'opcode is not implemented'
M_CSP = b'CsPretranslate: '
M_CFG = b'shader CFG build failed'
M_CACHE = b'Shader translation cache: '
M_PHI = b'lowered its phi to a host-evaluated select'
M_DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost', b'DbgExit')
TRANSLATOR = (b'\\recompiler\\', b'/recompiler/', b'ShaderCFG', b'ShaderRecompiler', b'Translate')
RX_OP = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
RX_CSP = re.compile(rb'CsPretranslate: (ready|skipped|miss|hit|enqueue skipped) hash=([0-9a-fA-F]{16})(.*)')
RX_PC_CFG = re.compile(rb'in CFG at pc 0x([0-9a-fA-F]+)')
RX_PC_ANY = re.compile(rb'pc[= ]0x([0-9a-fA-F]+)')
RX_SRC = re.compile(rb'([A-Za-z_]+\.cpp):(\d+)')


def load_hashes(path=TSV):
    h96, h5 = set(), {}
    with open(path, 'rb') as f:
        rows = f.read().decode('ascii').splitlines()
    for line in rows[1:]:
        p = line.split('\t')
        if len(p) < 4:
            continue
        if p[1] == 'SOP1' and p[2] == '0x21':
            h96.add(p[0])
        elif (p[1], p[2]) in FIXED_OPS:
            h5[p[0]] = (p[1], p[2], int(p[3], 16))
    return h96, h5


def _line(whole, i):
    s = whole.rfind(b'\n', 0, i) + 1
    e = whole.find(b'\n', i)
    if e < 0:
        e = len(whole)
    return s, e


def parse_skip(rest):
    """Mechanism of a 'skipped' reason: ('opcode', family, opcode, pc) | ('other', source, None, pc|None)."""
    m = RX_OP.search(rest)
    if m:
        pc = RX_PC_CFG.search(rest)
        return ('opcode', m.group(1).decode(), m.group(2).decode().lower(), int(pc.group(1), 16) if pc else None)
    src = RX_SRC.search(rest)
    pc = RX_PC_ANY.search(rest)
    name = '%s:%s' % (src.group(1).decode(), src.group(2).decode()) if src else 'unknown'
    return ('other', name, None, int(pc.group(1), 16) if pc else None)


def scan(path, h96, h5):
    res = dict(path=path, profile={}, per5={h: [] for h in h5}, reopen_mh=[], cfg_outside=0, deaths=[], translator_deaths=0,
               cache_lines=[], phi=0, csp_kinds={})
    sha = hashlib.sha256()
    off = 0
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            sha.update(b)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf
                    continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if not whole:
                break
            base = off
            off += len(whole)
            # opcode profile by (family, opcode)
            i = whole.find(M_OPC)
            while i >= 0:
                s, e = _line(whole, i)
                m = RX_OP.search(whole[s:e])
                k = (m.group(1).decode(), m.group(2).decode().lower()) if m else ('?', '?')
                res['profile'][k] = res['profile'].get(k, 0) + 1
                i = whole.find(M_OPC, e)
            # CsPretranslate lines
            i = whole.find(M_CSP)
            while i >= 0:
                s, e = _line(whole, i)
                m = RX_CSP.search(whole[s:e])
                if m:
                    kind = m.group(1).decode()
                    h = m.group(2).decode().lower()
                    res['csp_kinds'][kind] = res['csp_kinds'].get(kind, 0) + 1
                    if h in res['per5'] and kind in ('ready', 'skipped'):
                        res['per5'][h].append((kind, parse_skip(m.group(3)) if kind == 'skipped' else None, base + s))
                    if h in h96 and kind in ('miss', 'hit'):
                        res['reopen_mh'].append((kind, h, base + s))
                i = whole.find(M_CSP, e)
            # 'shader CFG build failed' outside CsPretranslate:
            i = whole.find(M_CFG)
            while i >= 0:
                s, e = _line(whole, i)
                if M_CSP not in whole[s:e]:
                    res['cfg_outside'] += 1
                i = whole.find(M_CFG, e)
            # knob control and expected phi lines
            i = whole.find(M_CACHE)
            while i >= 0:
                s, e = _line(whole, i)
                res['cache_lines'].append(whole[s:e][whole[s:e].find(M_CACHE) + len(M_CACHE):].strip().decode('latin1'))
                i = whole.find(M_CACHE, e)
            res['phi'] += whole.count(M_PHI)
            # deaths; 'from the translator' = the line or the 4 KB before it names the translator
            for mk in M_DEATH:
                i = whole.find(mk)
                while i >= 0:
                    s, e = _line(whole, i)
                    ctx = whole[max(0, s - 4096):e]
                    tr = any(t in ctx for t in TRANSLATOR)
                    res['deaths'].append((mk.decode(), base + s, tr))
                    res['translator_deaths'] += 1 if tr else 0
                    i = whole.find(mk, e)
            if not b:
                break
    res['sha256'] = sha.hexdigest()
    res['bytes'] = off
    return res


def knob_of(cache_lines):
    """'1' when the only cache line ends with variant_fixb26, '0' when it ends with the title root, else None."""
    if len(cache_lines) != 1:
        return None
    p = cache_lines[0].replace('\\', '/').rstrip('/')
    last = p.split('/')[-1]
    if last.startswith('variant') and 'fixb26' in last:
        return '1'
    if last == 'PPSA21564':
        return '0'
    return None


def judge(res, fix, h5):
    """Reading of one log run with KYTY_FIX_B26=<fix> ('1' or '0'). Letter of p.237(g)(4) and the F2b RC1 reviewer variant
    side by side; the RC1 rule itself is the lead's."""
    out = dict(fix=fix, knob=knob_of(res['cache_lines']))
    out['knob_ok'] = out['knob'] == fix
    prof = res['profile']
    out['n21'] = prof.get(('SOP1', '0x21'), 0)
    out['n0c'] = prof.get(('SOP1', '0x0c'), 0)
    out['ne3'] = prof.get(('VOPC', '0xe3'), 0)
    out['nf3'] = prof.get(('VOPC', '0xf3'), 0)
    out['other_ops'] = sorted((k, v) for k, v in prof.items() if k not in BASE0 and k != ('VOPC', '0xf3'))
    per = {}
    letter = variant = 0
    for h in sorted(h5):
        fam, op, fpc = h5[h]
        ls = res['per5'].get(h, [])
        if len(ls) != 1:
            st = dict(state='NOT COUNTED', why='%d lines' % len(ls), letter=False, variant=False)
        else:
            kind, sk, _ = ls[0]
            if kind == 'ready':
                st = dict(state='ready', letter=True, variant=True)
            else:
                mech, a, b, pc = sk
                if mech == 'opcode':
                    other = (a, b) not in FIXED_OPS
                    st = dict(state='skipped opcode %s %s pc 0x%x' % (a, b, pc if pc is not None else -1), letter=other,
                              variant=other and pc is not None and pc > fpc)
                else:
                    st = dict(state='skipped %s pc %s' % (a, '0x%x' % pc if pc is not None else 'none'), letter=False,
                              variant=pc is not None and pc > fpc)
        st['fix_place'] = '%s %s pc 0x%x' % (fam, op, fpc)
        per[h] = st
        letter += 1 if st['letter'] else 0
        variant += 1 if st['variant'] else 0
    out['per5'] = per
    out['letter5'] = letter
    out['variant5'] = variant
    out['reopen'] = dict(mh=len(res['reopen_mh']), cfg_outside=res['cfg_outside'], translator_deaths=res['translator_deaths'])
    out['reopen_any'] = any(out['reopen'].values())
    out['deaths'] = len(res['deaths'])
    out['phi'] = res['phi']
    if fix == '1':
        out['profile_ok'] = out['n0c'] == 0 and out['ne3'] == 0 and out['n21'] == 96
        out['verdict_letter'] = 'PASS' if out['knob_ok'] and out['profile_ok'] and letter == 5 else 'FAIL'
        out['verdict_variant'] = 'PASS' if out['knob_ok'] and out['profile_ok'] and variant == 5 else 'FAIL'
    else:
        out['profile_ok'] = out['n21'] == 96 and out['n0c'] == 1 and out['ne3'] == 4 and not out['other_ops'] and out['nf3'] == 0
        out['verdict_letter'] = out['verdict_variant'] = 'CONTROL RETURNS' if out['knob_ok'] and out['profile_ok'] else 'CONTROL FAILS'
    if not out['knob_ok']:
        out['verdict_letter'] = out['verdict_variant'] = 'INVALID RUN (knob control %s, want %s)' % (out['knob'], fix)
    return out


def report(res, out):
    L = ['log %s sha256 %s bytes %d' % (res['path'], res['sha256'], res['bytes']),
         'knob KYTY_FIX_B26=%s cache line(s) %s -> %s ok %s' % (out['fix'], res['cache_lines'], out['knob'], out['knob_ok']),
         'profile SOP1 0x21 %d / SOP1 0x0c %d / VOPC 0xe3 %d / VOPC 0xf3 %d / other %s' % (
             out['n21'], out['n0c'], out['ne3'], out['nf3'], out['other_ops']),
         'profile ok %s' % out['profile_ok'],
         'CsPretranslate kinds %s' % sorted(res['csp_kinds'].items())]
    for h, st in sorted(out['per5'].items()):
        L.append('hash %s fix place %s : %s letter %s variant %s' % (h, st['fix_place'], st['state'], st['letter'], st['variant']))
    L.append('positive count p.237(g)(4): letter %d of 5, F2b RC1 reviewer variant %d of 5' % (out['letter5'], out['variant5']))
    L.append('phi lines (expected at =1, not a marker): %d' % out['phi'])
    L.append('B26a reopen p.237(v)(2): miss|hit of the 96 %d, CFG failed outside CsPretranslate %d, translator deaths %d -> %s' % (
        out['reopen']['mh'], out['reopen']['cfg_outside'], out['reopen']['translator_deaths'],
        'REOPEN' if out['reopen_any'] else 'no reopen'))
    L.append('death lines (any) %d' % out['deaths'])
    L.append('verdict letter: %s' % out['verdict_letter'])
    L.append('verdict RC1 reviewer variant: %s' % out['verdict_variant'])
    return '\n'.join(L)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) < 2 or a[1] not in ('0', '1'):
        print('usage: f2c_b26.py <log> <0|1> [--json out.json]')
        return 2
    h96, h5 = load_hashes()
    res = scan(a[0], h96, h5)
    out = judge(res, a[1], h5)
    print(report(res, out))
    if '--json' in a:
        with open(a[a.index('--json') + 1], 'w', encoding='ascii') as f:
            json.dump(dict(res={k: v for k, v in res.items() if k not in ('per5', 'profile')},
                           profile=[[k[0], k[1], v] for k, v in res['profile'].items()], out=out), f, indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main())
