"""F23f (HPP-592, ROADMAP s122 item 498(v) RC1, (g)(1), (g)(3)): SPIR-V rewriters of the form-A sites
    %r = OpSelect %uint %c %new %old
into the two references of RC1 F23d (no OpSelect / OpPhi at the site) and the RC4 diagnostic module.

Common part at the site (the lane's own bit of the condition as an integer, from the ballot of %c over the invocations
that execute the site; the own bit of an executing invocation = %c by definition of the ballot):
    %l    = OpLoad %uint %SubgroupLocalInvocationId
    %bal  = OpGroupNonUniformBallot %v4uint %Subgroup %c
    %wi   = OpShiftRightLogical %uint %l %5
    %w    = OpVectorExtractDynamic %uint %bal %wi
    %sh   = OpBitwiseAnd %uint %l %31
    %t    = OpShiftRightLogical %uint %w %sh
    %bit  = OpBitwiseAnd %uint %t %1
(a) 'mask' - mix with the mask of the whole bit, no boolean:
    %mask = OpISub %uint %0 %bit ; %x = OpBitwiseXor %new %old ; %y = OpBitwiseAnd %x %mask ; %r = OpBitwiseXor %old %y
(b) 'mem'  - through memory: a Function variable uint[2] of the site's function (first block), Volatile stores of %old to
    [0] and %new to [1], %r = Volatile load of [%bit].
(diag) 'diag' - the default module (the OpSelect stays) plus, before the site, two atomic adds to a uint slot pair of a
    storage buffer chosen by the caller (variable id, constant index prefix before the word, e.g. (0,) for struct{uint[]} or
    (elem, 0) for an array of them): slot 2k += %bit, slot 2k+1 += (1 - %bit), k = site index - lanes executing the site;
    slot 2n (n = number of sites) += 1 at the start of the entry point - the positive control of the counters (invocations)
    with the condition true / false (n_t / n_f of RC4).
Types / constants / the built-in variable are reused when present, otherwise declared (non-aggregate types are never
duplicated). Only u32 selects with a scalar bool condition are rewritten (asserted)."""
import struct

OP_SELECT, OP_LABEL, OP_FUNCTION, OP_FUNCTIONEND, OP_VARIABLE = 169, 248, 54, 56, 59
OP_TYPEINT, OP_TYPEBOOL, OP_TYPEVECTOR, OP_TYPEARRAY, OP_TYPEPOINTER, OP_CONSTANT = 21, 20, 23, 28, 32, 43
OP_DECORATE, OP_ENTRYPOINT, OP_LOAD, OP_STORE, OP_ACCESSCHAIN = 71, 15, 61, 62, 65
BUILTIN, SUBGROUP_LOCAL_ID = 11, 41
SC_INPUT, SC_FUNCTION, SC_STORAGEBUFFER = 1, 7, 12
MA_VOLATILE = 1


def words_of(data):
    return list(struct.unpack('<%dI' % (len(data) // 4), data))


def instrs(words):
    out = []
    i = 5
    while i < len(words):
        n = words[i] >> 16
        out.append(list(words[i:i + n]))
        i += n
    return out


def enc(op, *operands):
    return [((len(operands) + 1) << 16) | op] + [int(x) for x in operands]


class Module:
    def __init__(self, data):
        w = words_of(data)
        self.header = w[:5]
        self.ins = instrs(w)
        self.bound = self.header[3]
        self.new_globals = []

    def new_id(self):
        r = self.bound
        self.bound += 1
        return r

    def first_function(self):
        return next(i for i, x in enumerate(self.ins) if x[0] & 0xffff == OP_FUNCTION)

    def find_type(self, op, operands):
        for x in self.ins + self.new_globals:
            if x[0] & 0xffff == op and x[2:] == list(operands):
                return x[1]
        return None

    def type_(self, op, *operands, aggregate=False):
        t = None if aggregate else self.find_type(op, operands)
        if t is None:
            t = self.new_id()
            self.new_globals.append(enc(op, t, *operands))
        return t

    def uint(self):
        return self.type_(OP_TYPEINT, 32, 0)

    def const(self, value):
        u = self.uint()
        for x in self.ins + self.new_globals:
            if x[0] & 0xffff == OP_CONSTANT and x[1] == u and x[3] == value and len(x) == 4:
                return x[2]
        c = self.new_id()
        self.new_globals.append(enc(OP_CONSTANT, u, c, value))
        return c

    def lane_var(self):
        """the Input variable with BuiltIn SubgroupLocalInvocationId; declared (variable, decoration, entry-point interface) when
        the module has none (3a8772dbc6934b1c). Called once before the rewrite loop: it may insert into self.ins."""
        if getattr(self, '_lane', None) is not None:
            return self._lane
        dec = set(x[1] for x in self.ins if x[0] & 0xffff == OP_DECORATE and len(x) >= 4 and x[2] == BUILTIN and x[3] == SUBGROUP_LOCAL_ID)
        vars_ = [x[2] for x in self.ins if x[0] & 0xffff == OP_VARIABLE and x[2] in dec]
        assert len(vars_) <= 1, ('SubgroupLocalInvocationId variable', vars_)
        if vars_:
            self._lane = vars_[0]
            return self._lane
        v = self.new_id()
        pin = self.type_(OP_TYPEPOINTER, SC_INPUT, self.uint())
        self.new_globals.append(enc(OP_VARIABLE, pin, v, SC_INPUT))
        last_dec = max(i for i, x in enumerate(self.ins) if x[0] & 0xffff in (OP_DECORATE, 72))
        self.ins.insert(last_dec + 1, enc(OP_DECORATE, v, BUILTIN, SUBGROUP_LOCAL_ID))
        eps = [i for i, x in enumerate(self.ins) if x[0] & 0xffff == OP_ENTRYPOINT]
        assert len(eps) == 1, eps
        x = self.ins[eps[0]]
        self.ins[eps[0]] = [((len(x)) + 1 << 16) | OP_ENTRYPOINT] + x[1:] + [v]
        self.added_lane = v
        self._lane = v
        return v

    def result_types(self):
        rt = {}
        no_result_type = {OP_TYPEINT, OP_TYPEBOOL, OP_TYPEVECTOR, OP_TYPEARRAY, OP_TYPEPOINTER, 19, 22, 24, 25, 26, 27, 29, 30, 31,
                          33, OP_LABEL, OP_DECORATE, 72, OP_ENTRYPOINT, 16, 17, 14, 11, 3, 5, 6, 7, 10, 12, 330, 331, 332,
                          OP_STORE, 247, 246, 249, 250, 251, 252, 253, 254, 255, OP_FUNCTIONEND, 4416}
        for x in self.ins:
            op = x[0] & 0xffff
            if len(x) >= 3 and op not in no_result_type:
                rt[x[2]] = x[1]
        return rt

    def assemble(self):
        fi = self.first_function()
        ins = self.ins[:fi] + self.new_globals + self.ins[fi:]
        self.header[3] = self.bound
        flat = list(self.header)
        for x in ins:
            flat += x
        return struct.pack('<%dI' % len(flat), *flat)


def own_bit(m, c, out):
    """appends the instructions of the common part, returns the id of %bit"""
    u = m.uint()
    v4 = m.type_(OP_TYPEVECTOR, u, 4)
    lane = m.lane_var()
    ids = [m.new_id() for _ in range(7)]
    l, bal, wi, w, sh, t, bit = ids
    out += enc(OP_LOAD, u, l, lane)
    out += enc(339, v4, bal, m.const(3), c)          # OpGroupNonUniformBallot, scope Subgroup
    out += enc(194, u, wi, l, m.const(5))            # OpShiftRightLogical
    out += enc(77, u, w, bal, wi)                    # OpVectorExtractDynamic
    out += enc(199, u, sh, l, m.const(31))           # OpBitwiseAnd
    out += enc(194, u, t, w, sh)
    out += enc(199, u, bit, t, m.const(1))
    return bit


def rewrite(data, sites, kind, diag_var=None, diag_base=0, diag_prefix=(0,)):
    """sites: list of (sid, cid, nid, oid); kind: 'mask' | 'mem' | 'diag'. Returns (bytes, number rewritten)."""
    m = Module(data)
    m.lane_var()
    rt = m.result_types()
    u = m.uint()
    want = {s[0]: s for s in sites}
    # pass 1: the function of each site (for 'mem': the Function variable goes to the first block of that function)
    func_of = {}
    cur_f = None
    for x in m.ins:
        op = x[0] & 0xffff
        if op == OP_FUNCTION:
            cur_f = x[2]
        elif op == OP_SELECT and x[2] in want:
            func_of[x[2]] = cur_f
    assert sorted(func_of) == sorted(want), ('sites not found', sorted(set(want) - set(func_of)))
    tmp_of = {}
    if kind == 'mem':
        arr = m.type_(OP_TYPEARRAY, u, m.const(2), aggregate=True)
        parr = m.type_(OP_TYPEPOINTER, SC_FUNCTION, arr, aggregate=True)
        pu = m.type_(OP_TYPEPOINTER, SC_FUNCTION, u, aggregate=True)
        for f in set(func_of.values()):
            tmp_of[f] = m.new_id()
    if kind == 'diag':
        assert diag_var is not None
        psb = m.type_(OP_TYPEPOINTER, SC_STORAGEBUFFER, u, aggregate=True)
    out = []
    cur_f = None
    after_label = False
    entry_f = [x for x in m.ins if x[0] & 0xffff == OP_ENTRYPOINT][0][2]
    pending_entry = False
    n = 0
    for x in m.ins:
        op = x[0] & 0xffff
        if pending_entry and op != OP_VARIABLE:
            # diag positive control: slot base + 2 * len(sites) += 1 per invocation entering the entry point
            pe, re_ = m.new_id(), m.new_id()
            pre = [m.const(i) for i in diag_prefix]
            out.append(enc(OP_ACCESSCHAIN, psb, pe, diag_var, *(pre + [m.const(diag_base + 2 * len(sites))])))
            out.append(enc(234, u, re_, pe, m.const(1), m.const(0), m.const(1)))
            pending_entry = False
        if op == OP_FUNCTION:
            cur_f = x[2]
            after_label = True
            out.append(x)
            continue
        if op == OP_LABEL and after_label:
            out.append(x)
            after_label = False
            if cur_f in tmp_of:
                out.append(enc(OP_VARIABLE, parr, tmp_of[cur_f], SC_FUNCTION))
            if kind == 'diag' and cur_f == entry_f:
                pending_entry = True
            continue
        if op == OP_SELECT and x[2] in want:
            sid, cid, nid, oid = want[x[2]]
            assert (x[3], x[4], x[5]) == (cid, nid, oid), ('operands', x, want[x[2]])
            assert x[1] == u, ('select type is not u32', x)
            seq = []
            bit = own_bit(m, cid, seq)
            if kind == 'mask':
                mask, xx, yy = m.new_id(), m.new_id(), m.new_id()
                seq += enc(130, u, mask, m.const(0), bit)    # OpISub
                seq += enc(198, u, xx, nid, oid)             # OpBitwiseXor
                seq += enc(199, u, yy, xx, mask)             # OpBitwiseAnd
                seq += enc(198, u, sid, oid, yy)             # OpBitwiseXor -> the select's own id
            elif kind == 'mem':
                tmp = tmp_of[cur_f]
                a0, a1, ab = m.new_id(), m.new_id(), m.new_id()
                seq += enc(OP_ACCESSCHAIN, pu, a0, tmp, m.const(0))
                seq += enc(OP_STORE, a0, oid, MA_VOLATILE)
                seq += enc(OP_ACCESSCHAIN, pu, a1, tmp, m.const(1))
                seq += enc(OP_STORE, a1, nid, MA_VOLATILE)
                seq += enc(OP_ACCESSCHAIN, pu, ab, tmp, bit)
                seq += enc(OP_LOAD, u, sid, ab, MA_VOLATILE)
            elif kind == 'diag':
                k = sites.index(want[x[2]])
                inv, pt, pf, r1, r2 = m.new_id(), m.new_id(), m.new_id(), m.new_id(), m.new_id()
                seq += enc(130, u, inv, m.const(1), bit)     # 1 - bit
                pre = [m.const(i) for i in diag_prefix]
                seq += enc(OP_ACCESSCHAIN, psb, pt, diag_var, *(pre + [m.const(diag_base + 2 * k)]))
                seq += enc(OP_ACCESSCHAIN, psb, pf, diag_var, *(pre + [m.const(diag_base + 2 * k + 1)]))
                seq += enc(234, u, r1, pt, m.const(1), m.const(0), bit)   # OpAtomicIAdd scope Device, semantics 0
                seq += enc(234, u, r2, pf, m.const(1), m.const(0), inv)
                seq += x                                      # the select itself stays
            out.append(seq)
            n += 1
            continue
        out.append(x)
    m.ins = out
    return m.assemble(), n


def selects_at(data, sids):
    """for a check: which of sids are still OpSelect results in the module"""
    return sorted(x[2] for x in instrs(words_of(data)) if x[0] & 0xffff == OP_SELECT and x[2] in set(sids))

def named_var(data, name):
    """id of the global OpVariable named `name` (OpName), or None"""
    ins = instrs(words_of(data))
    ids = [x[1] for x in ins if x[0] & 0xffff == 5 and bytes(b for w in x[2:] for b in w.to_bytes(4, 'little')).split(b'\0')[0] == name.encode()]
    vars_ = set(x[2] for x in ins if x[0] & 0xffff == OP_VARIABLE)
    ids = [i for i in ids if i in vars_]
    return ids[0] if len(ids) == 1 else None
