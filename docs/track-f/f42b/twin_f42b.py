"""F42b (HPP-780, Red Team; ROADMAP s122 item 694(g)(3)-(5)): an independent Python twin of the rewrite of item 694(v)(1)
(written from the item text and the SPIR-V spec, not from fixF20.h) and an independent scanner.

Rewrite rule (item 694(v)(1)): every three consecutive instructions
    %v = OpLoad %u32 %p ; %o = OpBitwiseOr %u32 (%v %b | %b %v) ; OpStore %p %o
where %p is an OpAccessChain / OpInBoundsAccessChain whose base is a variable with OpName "fault_buffer", and %v, %o
have no other use, become  %v = OpAtomicOr %u32 %p %one %zero %b  with %one / %zero the first OpConstant of value 1 / 0
of a 32-bit unsigned OpTypeInt. Nothing else changes (header and id bound included).

scan(words) -> named, bound_dec (fault_buffer var has a Binding decoration), triples, loads_fb (OpLoad through a chain on
fault_buffer), atomics_or, atomics_xor, atomic_scopes (set of Scope constant VALUES used by OpAtomicOr on fault_buffer).

Usage as a script:
  python twin_f42b.py diff <base.spv> <new.spv>     -> 'only triples' check of new against base
  python twin_f42b.py twin <base.spv> <cpp.spv>     -> twin(base) == cpp bytes
"""
import struct
import sys

OP_NAME, OP_DECORATE, OP_TYPEINT, OP_CONSTANT = 5, 71, 21, 43
OP_LOAD, OP_STORE, OP_AC, OP_IBAC, OP_OR = 61, 62, 65, 66, 197
OP_ATOMIC_OR, OP_ATOMIC_XOR, OP_FUNCTION = 241, 242, 54
DEC_BINDING = 33


def read_spv(path):
    b = open(path, 'rb').read()
    return list(struct.unpack('<%dI' % (len(b) // 4), b))


def insns(w):
    out = []
    i = 5
    while i < len(w):
        n = w[i] >> 16
        if n == 0 or i + n > len(w):
            raise ValueError('malformed at %d' % i)
        out.append((i, w[i] & 0xffff, n))
        i += n
    return out


def name_of(w, at, n):
    raw = struct.pack('<%dI' % (n - 2), *w[at + 2:at + n])
    return raw.split(b'\0', 1)[0].decode('latin-1')


def facts(w):
    ins = insns(w)
    fvars, u32, consts, chains, bind = set(), set(), {}, set(), set()
    for at, op, n in ins:
        if op == OP_NAME and name_of(w, at, n) == 'fault_buffer':
            fvars.add(w[at + 1])
        elif op == OP_TYPEINT and w[at + 2] == 32 and w[at + 3] == 0:
            u32.add(w[at + 1])
    for at, op, n in ins:
        if op == OP_CONSTANT and n == 4 and w[at + 1] in u32:
            consts.setdefault(w[at + 3], w[at + 2])
        if op in (OP_AC, OP_IBAC) and w[at + 3] in fvars:
            chains.add(w[at + 2])
        if op == OP_DECORATE and w[at + 2] == DEC_BINDING and w[at + 1] in fvars:
            bind.add(w[at + 1])
    return ins, fvars, u32, consts, chains, bind


def triples_of(w, ins, u32, chains):
    res = []
    for k in range(len(ins) - 2):
        (a1, o1, n1), (a2, o2, n2), (a3, o3, n3) = ins[k], ins[k + 1], ins[k + 2]
        if o1 == OP_LOAD and n1 == 4 and w[a1 + 3] in chains and w[a1 + 1] in u32 and o2 == OP_OR and n2 == 5 \
                and o3 == OP_STORE and n3 == 3:
            v, p, o = w[a1 + 2], w[a1 + 3], w[a2 + 2]
            ops = (w[a2 + 3], w[a2 + 4])
            if (ops[0] == v) != (ops[1] == v) and w[a3 + 1] == p and w[a3 + 2] == o and w[a2 + 1] == w[a1 + 1]:
                bit = ops[1] if ops[0] == v else ops[0]
                res.append((k, w[a1 + 1], v, p, o, bit))
    return res


def use_count(w, ins, ids):
    cnt = dict.fromkeys(ids, 0)
    first = next((k for k, (_, op, _) in enumerate(ins) if op == OP_FUNCTION), len(ins))
    for at, op, n in ins[first:]:
        last = 2 if op == 251 else n  # OpSwitch: selector only
        for x in w[at + 1:at + last]:
            if x in cnt:
                cnt[x] += 1
    return cnt


def scan(w):
    ins, fvars, u32, consts, chains, bind = facts(w)
    tr = triples_of(w, ins, u32, chains)
    loads = sum(1 for at, op, n in ins if op == OP_LOAD and n >= 4 and w[at + 3] in chains)
    aor = [(at, n) for at, op, n in ins if op == OP_ATOMIC_OR and w[at + 3] in chains]
    axor = sum(1 for at, op, n in ins if op == OP_ATOMIC_XOR and w[at + 3] in chains)
    inv = {v: k for k, v in consts.items()}
    scopes = set(inv.get(w[at + 4], 'nonconst') for at, n in aor)
    sems = set(inv.get(w[at + 5], 'nonconst') for at, n in aor)
    return {'named': len(fvars), 'bound_dec': len(bind), 'triples': len(tr), 'loads_fb': loads,
            'atomics_or': len(aor), 'atomics_xor': axor, 'atomic_scopes': scopes, 'atomic_sems': sems}


def twin(w, bound=True):
    """Returns (new words or None, sites, rewritten)."""
    ins, fvars, u32, consts, chains, bind = facts(w)
    if not bound or not fvars:
        return None, 0, 0
    tr = triples_of(w, ins, u32, chains)
    cnt = use_count(w, ins, [t[2] for t in tr] + [t[4] for t in tr])
    one, zero = consts.get(1), consts.get(0)
    keep = {t[0]: t for t in tr if one and zero and cnt[t[2]] == 2 and cnt[t[4]] == 2}
    if not keep:
        return None, len(tr), 0
    out = w[:5]
    k = 0
    while k < len(ins):
        at, op, n = ins[k]
        if k in keep:
            _, ty, v, p, o, bit = keep[k]
            out += [(7 << 16) | OP_ATOMIC_OR, ty, v, p, one, zero, bit]
            k += 3
            continue
        out += w[at:at + n]
        k += 1
    return out, len(tr), len(keep)


def only_triples(base, new):
    """new differs from base only by triples -> OpAtomicOr of the twin form. Returns (ok, replaced)."""
    t, s, r = twin(base)
    if t is None:
        return base == new, 0
    return t == new, r


if __name__ == '__main__':
    cmd, a, b = sys.argv[1], read_spv(sys.argv[2]), read_spv(sys.argv[3])
    if cmd == 'diff':
        print('only_triples', only_triples(a, b))
    else:
        t, s, r = twin(a)
        print('twin sites', s, 'rewritten', r, 'equal', (t if t is not None else a) == b)
