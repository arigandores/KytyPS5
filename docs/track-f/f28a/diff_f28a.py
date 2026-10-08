"""F28a (HPP-698, ROADMAP s122 item 638(v)(1)): line diff of the SPIR-V of 380bb9d636390bae at the
KYTY_BVH_LOOP_CAP default (def) against KYTY_BVH_LOOP_CAP=0 (c0), outputs of spv_f28a.py.

Method (removal proof): every fragment the loop cap adds to def is recognised by its exact shape and
removed; what is left must be equal to c0 line for line under ONE consistent renaming of ids (a
bijection), with one allowed substitution: a phi/branch operand that names the guard's fall-through
label in def names the guarded header's own label in c0 (the edge out of the header now leaves from
the fall-through block). Shapes (spirvEmitterProgram.cpp EmitLoopGuard, spirvEmitterMemory.cpp
EmitLoopCapTrip / EmitLoopCapNear, EmitReturnTail):
  DECL   OpName bvh_loop_budget; OpTypePointer Function uint; OpVariable bvh_loop_budget (init 0);
         OpConstant 65536, 4096, 2097152..2097160 (only when absent from c0)
  PRE    load budget; IAdd 1; Store budget; UGreaterThan budget 65536          (before OpLoopMerge)
  GUARD  OpBranch G; G: SelectionMerge A; BranchConditional over AB A; AB: trip atomics x3 on the
         fault-buffer tail; return tail (fault flush, OpReturn); A: OpLabel    (after OpLoopMerge)
  NEAR   load budget; UGreaterThan 4096; SelectionMerge N; BranchConditional; label; 2 atomics on the
         tail; OpBranch N; N: OpLabel                                          (before each return tail)
Checks printed per permutation: counts of each shape, stores/atomics/barriers inside removed code (only
the budget variable and tail words 2097152..2097160, plus the fault-bitmap word of the copied return
tail in the abort block), remainder length equality, renaming conflicts (must be 0), substitutions.
Usage: python diff_f28a.py <spv dir of spv_f28a.py>. Exit 0 and ALL OK when every check holds.
"""
import collections
import re
import subprocess
import sys

DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
TAIL_WORDS = {'%%uint_%d' % (2097152 + k) for k in range(16)}
ID = re.compile(r'%[\w]+')


def dis(path):
    out = subprocess.run([DIS, '--raw-id', '--no-color', '--no-header', path], capture_output=True, check=True).stdout
    return [l.strip() for l in out.decode('utf-8').splitlines() if l.strip()]


def const_names(lines):
    """raw-id disassembly: map constant id -> 'uint_<v>' for OpConstant of the uint type."""
    uint_t = None
    for l in lines:
        m = re.match(r'(%\d+) = OpTypeInt 32 0$', l)
        if m:
            uint_t = m.group(1)
    names = {}
    for l in lines:
        m = re.match(r'(%\d+) = OpConstant (%\d+) (\d+)$', l)
        if m and m.group(2) == uint_t:
            names[m.group(1)] = '%%uint_%s' % m.group(3)
    return names, uint_t


def strip_cap(lines):
    names, uint_t = const_names(lines)
    nm = lambda t: names.get(t, t)
    budget = None
    for l in lines:
        m = re.match(r'OpName (%\d+) "bvh_loop_budget"$', l)
        if m:
            budget = m.group(1)
    assert budget, 'no bvh_loop_budget'
    fault = [re.match(r'OpName (%\d+) "fault_buffer"$', l).group(1) for l in lines if re.match(r'OpName (%\d+) "fault_buffer"$', l)][0]
    out = []
    removed_defs = set()
    subst = {}             # def after-label -> def header label
    counts = collections.Counter()
    effects = collections.Counter()
    cur_label = None
    i = 0
    n = len(lines)

    def scan_effects(seg, kind):
        for l in seg:
            op = re.search(r'\bOp\w+', l).group(0)
            if op in ('OpControlBarrier', 'OpMemoryBarrier'):
                effects['BARRIER in ' + kind] += 1
            if op.startswith('OpAtomic'):
                toks = l.split()
                ptr = toks[4]
                # find the access chain of ptr in seg
                ac = [x for x in seg if x.startswith(ptr + ' = OpAccessChain')]
                word = nm(ac[0].split()[-1]) if ac else '?'
                sem = nm(toks[6])
                scope = nm(toks[5])
                key = '%s %s word=%s scope=%s sem=%s' % (kind, op, 'TAIL' if word in TAIL_WORDS else word, scope, sem)
                effects[key] += 1
            if op == 'OpStore':
                tgt = l.split()[1]
                if tgt == budget:
                    effects[kind + ' OpStore budget'] += 1
                else:
                    ac = [x for x in seg if x.startswith(tgt + ' = OpAccessChain')]
                    acb = ac[0].split() if ac else []
                    if acb and acb[4] == fault and acb[-1] not in names:
                        effects[kind + ' OpStore fault_bitmap(word=page>>5)'] += 1
                    else:
                        effects['FORBIDDEN store in %s: %s' % (kind, ac[0] if ac else tgt)] += 1
            if op in ('OpImageWrite', 'OpFunctionCall', 'OpKill', 'OpTerminateInvocation', 'OpEmitVertex'):
                effects['FORBIDDEN %s in %s' % (op, kind)] += 1

    while i < n:
        l = lines[i]
        m = re.match(r'(%\d+) = OpLabel$', l)
        if m:
            cur_label = m.group(1)
        # DECL
        if re.match(r'OpName %s "bvh_loop_budget"$' % budget, l) or l.startswith(budget + ' = OpVariable'):
            counts['DECL'] += 1
            removed_defs.add(budget)
            i += 1
            continue
        # PRE + GUARD
        if re.match(r'(%\d+) = OpLoad ' + uint_t + ' ' + budget + '$', l) and i + 3 < n and 'OpIAdd' in lines[i + 1]:
            pre = lines[i:i + 4]
            ld = pre[0].split()[0]
            nx = pre[1].split()[0]
            ok = (re.match(nx + ' = OpIAdd ' + uint_t + ' ' + ld + r' %\d+$', pre[1]) and nm(pre[1].split()[-1]) == '%uint_1'
                  and pre[2] == 'OpStore %s %s' % (budget, nx)
                  and re.match(r'%\d+ = OpUGreaterThan %\d+ ' + nx + r' %\d+$', pre[3])
                  and nm(pre[3].split()[-1]) == '%uint_65536')
            over = pre[3].split()[0]
            lm = lines[i + 4]
            assert ok and lm.startswith('OpLoopMerge'), ('PRE shape', i, pre, lm)
            br = lines[i + 5]
            g = br.split()[1]
            assert br == 'OpBranch ' + g and lines[i + 6] == g + ' = OpLabel', ('GUARD head', i)
            sm = lines[i + 7].split()
            a = sm[1]
            bc = lines[i + 8].split()
            assert sm[0] == 'OpSelectionMerge' and bc[0] == 'OpBranchConditional' and bc[1] == over and bc[3] == a, ('GUARD sel', i)
            ab = bc[2]
            assert lines[i + 9] == ab + ' = OpLabel'
            j = i + 10
            while lines[j] != a + ' = OpLabel':
                j += 1
            body = lines[i + 10:j]
            assert body[-1] == 'OpReturn', ('abort body must end in OpReturn', i)
            scan_effects(pre + body, 'GUARD')
            for x in pre + lines[i + 5:j + 1]:
                t = x.split()
                if len(t) > 1 and t[1] == '=':
                    removed_defs.add(t[0])
            removed_defs.update({g, a, ab})
            subst[a] = cur_label
            counts['PRE+GUARD'] += 1
            counts['abort_body_lines_%d' % len(body)] += 1
            out.append(lm)
            i = j + 1
            continue
        # NEAR
        if re.match(r'(%\d+) = OpLoad ' + uint_t + ' ' + budget + '$', l) and 'OpUGreaterThan' in lines[i + 1]:
            seg = lines[i:i + 11]
            sp = seg[0].split()[0]
            assert nm(seg[1].split()[-1]) == '%uint_4096' and seg[1].split()[4] == sp, ('NEAR cmp', i)
            nn = seg[2].split()[1]
            assert seg[2].startswith('OpSelectionMerge') and seg[3].startswith('OpBranchConditional') and seg[9] == 'OpBranch ' + nn \
                and seg[10] == nn + ' = OpLabel', ('NEAR shape', i, seg)
            scan_effects(seg, 'NEAR')
            for x in seg:
                t = x.split()
                if len(t) > 1 and t[1] == '=':
                    removed_defs.add(t[0])
            removed_defs.add(nn)
            # the code after N continues the block that held the NEAR prologue: in c0 it follows cur_label
            subst[nn] = cur_label
            counts['NEAR'] += 1
            i += 11
            continue
        out.append(l)
        i += 1
    return out, removed_defs, subst, counts, effects, names


def compare(d_lines, c_lines):
    dn, _ = const_names(d_lines)
    cn, _ = const_names(c_lines)
    rest, removed, subst, counts, effects, names = strip_cap(d_lines)
    # DECL constants: drop def OpConstant lines whose value is absent from c0
    c_vals = set(cn.values())
    rest2 = []
    for l in rest:
        m = re.match(r'(%\d+) = OpConstant (%\d+) (\d+)$', l)
        if m and dn.get(m.group(1)) and dn[m.group(1)] not in c_vals:
            counts['DECL_CONST ' + dn[m.group(1)]] += 1
            removed.add(m.group(1))
            continue
        m = re.match(r'(%\d+) = OpTypePointer Function (%\d+)$', l)
        if m and not any(re.match(r'%\d+ = OpTypePointer Function ', x) for x in c_lines if 'Function' in x):
            counts['DECL_PTR_FUNCTION'] += 1
            removed.add(m.group(1))
            continue
        rest2.append(l)
    print('  shapes', dict(counts))
    print('  effects of removed code', dict(effects))
    print('  remainder lines def', len(rest2), ' c0', len(c_lines))
    if len(rest2) != len(c_lines):
        return False, 'length'
    fwd, bwd = {}, {}
    conflicts = []
    subs_used = collections.Counter()
    leaks = []
    pending = []
    for k, (a, b) in enumerate(zip(rest2, c_lines)):
        ta, tb = ID.split(a), ID.split(b)
        ia, ib = ID.findall(a), ID.findall(b)
        if ta != tb or len(ia) != len(ib):
            conflicts.append((k, a, b, 'text'))
            continue
        for x, y in zip(ia, ib):
            if x in removed and x not in subst:
                leaks.append((k, a))
            xx = x
            if x in subst:
                # allowed: operand naming a guard fall-through / near merge label maps to the header / block label
                if fwd.get(subst[x], y) == y and bwd.get(y, subst[x]) == subst[x]:
                    subs_used[x] += 1
                    pending.append((k, subst[x], y))
                    continue
                xx = subst[x]
            if fwd.setdefault(xx, y) != y or bwd.setdefault(y, xx) != xx:
                conflicts.append((k, a, b, 'map %s->%s vs %s' % (xx, fwd.get(xx), y)))
    for k, h, y in pending:
        if fwd.get(h) != y:
            conflicts.append((k, h, y, 'substitution not confirmed by the header label'))
    print('  renaming size', len(fwd), ' conflicts', len(conflicts), ' leaks of removed ids', len(leaks),
          ' substitutions used', sum(subs_used.values()), 'on', len(subs_used), 'labels')
    for c in conflicts[:10]:
        print('   CONFLICT', c)
    for c in leaks[:10]:
        print('   LEAK', c)
    bad_eff = [k for k in effects if 'FORBIDDEN' in k or 'BARRIER' in k or ('Atomic' in k and 'word=TAIL' not in k)
               or ('NEAR' in k and 'OpStore' in k)]
    print('  effects outside the tail/budget/bitmap flush:', bad_eff)
    return not conflicts and not leaks and not bad_eff, counts


def main():
    root = sys.argv[1]
    ok = True
    for perm in (0, 1, 2):
        d = dis('%s/p%d_def/out.spv' % (root, perm))
        c = dis('%s/p%d_c0/out.spv' % (root, perm))
        print('perm', perm, 'def lines', len(d), 'c0 lines', len(c))
        r, counts = compare(d, c)
        print('  perm', perm, 'EQUIVALENT-MODULO-CAP' if r else 'NOT PROVEN')
        ok &= r
    # negative controls: the checker must refuse (a) def of perm 0 against c0 of perm 1 (a different
    # specialization), (b) def of perm 0 against c0 of perm 0 with one operand of one instruction changed
    d0 = dis('%s/p0_def/out.spv' % root)
    c1 = dis('%s/p1_c0/out.spv' % root)
    print('NEG-A def p0 vs c0 p1')
    try:
        ra, _ = compare(d0, c1)
    except AssertionError as e:
        ra = False
    c0 = dis('%s/p0_c0/out.spv' % root)
    k = next(i for i, l in enumerate(c0) if ' = OpIAdd ' in l and len(c0) // 2 < i)
    t = c0[k].split()
    t[-1], t[-2] = t[-2], t[-1]
    c0m = c0[:k] + [' '.join(t)] + c0[k + 1:]
    print('NEG-B def p0 vs c0 p0 with operands of line %d swapped: %s -> %s' % (k, c0[k], c0m[k]))
    rb, _ = compare(d0, c0m)
    print('NEG-A refused', not ra, ' NEG-B refused', not rb)
    ok &= (not ra) and (not rb)
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
