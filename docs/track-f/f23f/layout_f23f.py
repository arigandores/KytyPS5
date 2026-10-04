"""F23f (HPP-592, ROADMAP s122 item 498(g)(2)(b)): interface layout of the S12 module = that of the captured module.
For each of the 17 programs: the captured module (bytes from a cache file whose module sha = the capture's, map_f23f.json) and the
S12 module (s12spv/) are reduced to an interface signature - every global OpVariable of a non-Function / non-Private storage
class with its DescriptorSet / Binding / BuiltIn / Location / Flat / Aliased decorations and its fully expanded pointee type
(struct members with Offset, arrays with ArrayStride and length, ints / floats / vectors / images / samplers), the entry point
execution model and execution modes (LocalSize etc.), the capability list. Equal signatures = equal pipeline layout of the
module (the descriptor set layout and push constant range are what these decorations and types describe).
Output: layout_f23f.out.txt (per program EQUAL / DIFF with the first differing lines), layout_f23f.json."""
import hashlib
import json
import os
import re
import struct
import sys

sys.path.insert(0, 'C:/kyty/f287/f23f')
import map_f23f as M  # noqa: E402

D = 'C:/kyty/f287/f23f/'
NL = chr(10)
GLOBAL_SKIP_SC = {7, 6}  # Function, Private


def words(b):
    return list(struct.unpack('<%dI' % (len(b) // 4), b))


def ins_of(w):
    i = 5
    while i < len(w):
        n = w[i] >> 16
        yield w[i:i + n]
        i += n


def string(ops):
    return bytes(b for x in ops for b in x.to_bytes(4, 'little')).split(b'\0')[0].decode('latin1')


def signature(data):
    w = words(data)
    types, consts, decos, mdecos, names = {}, {}, {}, {}, {}
    vars_, caps, modes, entry = [], [], [], []
    for x in ins_of(w):
        op = x[0] & 0xffff
        if op == 17:
            caps.append(x[1])
        elif op == 15:
            entry.append((x[1], string(x[3:])))
        elif op == 16:
            modes.append(tuple(x[2:]))
        elif op == 5:
            names[x[1]] = string(x[2:])
        elif op == 71:
            decos.setdefault(x[1], []).append(tuple(x[2:]))
        elif op == 72:
            mdecos.setdefault((x[1], x[2]), []).append(tuple(x[3:]))
        elif op in (19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32):
            types[x[1]] = (op, tuple(x[2:]))
        elif op == 43:
            consts[x[2]] = tuple(x[3:])
        elif op == 59 and x[3] not in GLOBAL_SKIP_SC:
            vars_.append((x[2], x[1], x[3]))

    def ty(t, depth=0):
        if depth > 20 or t not in types:
            return '?%d' % t
        op, a = types[t]
        if op == 21:
            return 'i%d%s' % (a[0], 's' if a[1] else 'u')
        if op == 22:
            return 'f%d' % a[0]
        if op == 20:
            return 'bool'
        if op == 19:
            return 'void'
        if op == 23:
            return 'v%d<%s>' % (a[1], ty(a[0], depth + 1))
        if op == 24:
            return 'm%d<%s>' % (a[1], ty(a[0], depth + 1))
        if op == 25:
            return 'image<%s,%s>' % (ty(a[0], depth + 1), ','.join(str(v) for v in a[1:]))
        if op in (26, 27):
            return 'sampler' if op == 26 else 'sampledimage<%s>' % ty(a[0], depth + 1)
        if op == 28:
            return 'arr[%s]<%s>%s' % (consts.get(a[1], '?'), ty(a[0], depth + 1), decos.get(t, ''))
        if op == 29:
            return 'rarr<%s>%s' % (ty(a[0], depth + 1), decos.get(t, ''))
        if op == 30:
            mem = []
            for k, m in enumerate(a):
                mem.append('%s%s' % (ty(m, depth + 1), sorted(mdecos.get((t, k), []))))
            return 'struct{%s}%s' % (';'.join(mem), sorted(decos.get(t, [])))
        if op == 32:
            return 'ptr%d<%s>' % (a[0], ty(a[1], depth + 1))
        return 'op%d' % op
    out = ['caps %s' % sorted(caps), 'entry %s' % entry, 'modes %s' % sorted(modes)]
    for v, t, sc in vars_:
        out.append('var %s sc%d deco %s type %s' % (names.get(v, '?'), sc, sorted(d for d in decos.get(v, []) if d[0] in (33, 34, 11, 30, 14, 20, 24, 25, 19, 21, 23, 31, 32)),
                                                    ty(t)))
    return out


def captured_bytes(stage, h, state, perm, want_sha):
    for path, m in M.walk(M.TREES, {h}):
        if m.group(1) != stage or m.group(3) != state:
            continue
        r = M.read_cache(path)
        if r is None:
            continue
        mods = r[2]
        if perm < len(mods) and hashlib.sha256(mods[perm]).hexdigest() == want_sha:
            return mods[perm], path
    return None, None


def main():
    mp = json.load(open(D + 'map_f23f.json'))
    out, res = [], {}
    ok_all = True
    for h in sorted(mp, key=lambda x: (mp[x]['stage'], x)):
        v = mp[h]
        s12k = list(v['s12'].keys())[0]
        s12 = open(D + 's12spv/' + v['s12'][s12k]['file'], 'rb').read()
        caps = [e for l in v['captures'].values() for e in l]
        e = caps[0]
        if e['equal_s12']:
            out.append('%s %s captured module = S12 module (sha %s) - layout EQUAL by identity' % (v['stage'], h, e['sha'][:16]))
            res[h] = 'EQUAL_IDENTICAL'
            continue
        cb, path = captured_bytes(v['stage'], h, e['state'], e['perm'], e['sha'])
        if cb is None:
            out.append('%s %s captured module bytes NOT FOUND' % (v['stage'], h))
            res[h] = 'NOT_FOUND'
            ok_all = False
            continue
        a, b = signature(cb), signature(s12)
        eq = a == b
        res[h] = 'EQUAL' if eq else 'DIFF'
        out.append('%s %s captured %s (%s) vs S12 %s: interface lines %d / %d -> %s' % (
            v['stage'], h, e['sha'][:16], path, v['s12'][s12k]['sha'][:16], len(a), len(b), res[h]))
        if not eq:
            ok_all = False
            for x, y in zip(a + [''] * (len(b) - len(a)), b + [''] * (len(a) - len(b))):
                if x != y:
                    out.append('   capture: %s' % x[:400])
                    out.append('   S12    : %s' % y[:400])
    out.append('ALL EQUAL' if ok_all else 'NOT ALL EQUAL')
    open(D + 'layout_f23f.out.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(out) + NL)
    json.dump(res, open(D + 'layout_f23f.json', 'w'), indent=1, sort_keys=True)
    print(NL.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
