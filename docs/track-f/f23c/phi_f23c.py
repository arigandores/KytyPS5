"""F23c (HPP-587, ROADMAP s122 item 493(g)(2)): reference-method candidate 'branch + OpPhi' - rewrites chosen OpSelect of a
SPIR-V module into structured control flow:

    %r = OpSelect %T %c %new %old            OpSelectionMerge %m None
                                     ==>      OpBranchConditional %c %t %m
                                         %t = OpLabel
                                              OpBranch %m
                                         %m = OpLabel
                                         %r = OpPhi %T %new %t %old %prev

(%prev = the label of the block the select was in, or of the previous split of that block). The rest of the block - its
merge instruction and terminator included - moves to the last %m, so OpPhi of successor blocks that named the original block
as parent are renamed to the last %m. Only scalar-bool conditions. Values of active lanes are those of OpSelect by SPIR-V
semantics; the point is that the driver sees a branch and a phi instead of a select (weakness: it may if-convert the
branch back into a select)."""
import struct

OP_LABEL, OP_BRANCH, OP_BRANCHCOND, OP_SELMERGE, OP_PHI, OP_SELECT = 248, 249, 250, 247, 245, 169
TERMINATORS = {249, 250, 251, 252, 253, 254, 255, 4416}
OP_TYPEBOOL = 20


def instrs(words):
    i = 5
    out = []
    while i < len(words):
        n = words[i] >> 16
        out.append(list(words[i:i + n]))
        i += n
    return out


def enc(op, operands):
    return [((len(operands) + 1) << 16) | op] + list(operands)


def rewrite(data, select_ids=None, cond_id=None):
    """select_ids: set of result ids to rewrite; or cond_id: rewrite every OpSelect with this condition"""
    words = list(struct.unpack('<%dI' % (len(data) // 4), data))
    header = words[:5]
    bound = header[3]
    ins = instrs(words)
    types = {}
    result_type = {}
    for x in ins:
        op = x[0] & 0xffff
        if op == OP_TYPEBOOL:
            types[x[1]] = 'bool'
    # result types of value instructions (<type, result> layout); only the condition's type is used
    no_result = {62, 63, 64, 71, 72, 73, 74, 75, 224, 225, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 332, 4416, 5632, 5633}
    for x in ins:
        op = x[0] & 0xffff
        if len(x) >= 3 and op >= 59 and op not in no_result:
            result_type[x[2]] = x[1]
    out = []
    cur_label = None
    renames = {}  # original block label -> label of its last split
    done = []
    for x in ins:
        op = x[0] & 0xffff
        if op == OP_LABEL:
            cur_label = x[1]
            orig_label = x[1]
            out.append(x)
            continue
        if op == OP_SELECT and cur_label is not None and ((select_ids is not None and x[2] in select_ids) or
                                                           (cond_id is not None and x[3] == cond_id)):
            T, r, c, a, b = x[1], x[2], x[3], x[4], x[5]
            assert types.get(result_type.get(c)) == 'bool', ('condition is not a scalar bool', r)
            t, m = bound, bound + 1
            bound += 2
            out.append(enc(OP_SELMERGE, [m, 0]))
            out.append(enc(OP_BRANCHCOND, [c, t, m]))
            out.append(enc(OP_LABEL, [t]))
            out.append(enc(OP_BRANCH, [m]))
            out.append(enc(OP_LABEL, [m]))
            out.append(enc(OP_PHI, [T, r, a, t, b, cur_label]))
            cur_label = m
            renames[orig_label] = m
            done.append(r)
            continue
        out.append(x)
    # OpPhi elsewhere naming a split block as parent -> its last split label (the phis created here keep their parents)
    created = set(done)
    for x in out:
        if (x[0] & 0xffff) == OP_PHI and x[2] not in created:
            for k in range(4, len(x), 2):
                if x[k] in renames:
                    x[k] = renames[x[k]]
    header[3] = bound
    flat = header + [w for x in out for w in x]
    return struct.pack('<%dI' % len(flat), *flat), done


OP_CONSTANT, OP_XOR, OP_AND, OP_TYPEINT = 43, 198, 199, 21


def blend(data, select_ids=None, cond_id=None):
    """reference-method candidate 'bit blend': %r = OpSelect %uint %c %new %old  ==>
    %m = OpSelect %uint %c %all_ones %zero; %x = OpBitwiseXor %new %old; %y = OpBitwiseAnd %x %m; %r = OpBitwiseXor %old %y
    (32-bit integer result types only). The value of %r is the select's on every lane; the select left is one of two
    constants. Weakness: an optimizer may recognise the pattern and turn it back into a select of %new and %old."""
    words = list(struct.unpack('<%dI' % (len(data) // 4), data))
    header = words[:5]
    bound = header[3]
    ins = instrs(words)
    int32 = {x[1] for x in ins if (x[0] & 0xffff) == OP_TYPEINT and x[2] == 32}
    zero = {}
    ones_id = {}
    out = []
    done = []
    for x in ins:
        if (x[0] & 0xffff) == OP_CONSTANT and x[1] in int32 and len(x) == 4 and x[3] == 0:
            zero.setdefault(x[1], x[2])
    for x in ins:
        op = x[0] & 0xffff
        out.append(x)
        if op == OP_CONSTANT and x[1] in int32 and x[1] not in ones_id:
            ones_id[x[1]] = bound
            out.append(enc(OP_CONSTANT, [x[1], bound, 0xffffffff]))
            bound += 1
    out2 = []
    for x in out:
        op = x[0] & 0xffff
        if op == OP_SELECT and ((select_ids is not None and x[2] in select_ids) or (cond_id is not None and x[3] == cond_id)):
            T, r, c, a, b = x[1], x[2], x[3], x[4], x[5]
            assert T in int32 and T in zero and T in ones_id, ('not a 32-bit integer select', r)
            m, xx, yy = bound, bound + 1, bound + 2
            bound += 3
            out2.append(enc(OP_SELECT, [T, m, c, ones_id[T], zero[T]]))
            out2.append(enc(OP_XOR, [T, xx, a, b]))
            out2.append(enc(OP_AND, [T, yy, xx, m]))
            out2.append(enc(OP_XOR, [T, r, b, yy]))
            done.append(r)
            continue
        out2.append(x)
    header[3] = bound
    flat = header + [w for x in out2 for w in x]
    return struct.pack('<%dI' % len(flat), *flat), done
