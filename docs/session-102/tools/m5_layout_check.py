"""m5_layout_check.py -- session 102, M5: for every A/V2 pair built by m5_recompile.py, check that V2
declares exactly A's descriptor bindings plus BdaPagetable and FaultBuffer (NativeBinding = 46/47 +
51*group, group 0 for CS, 1 for PS), that the set of user-data registers the program reads
(GetUserData sN in the KYTY_RECOMPILE_DUMP IR) is unchanged (so user_data_registers, the memory-offset
dword and the push-data layout are unchanged), and that V2 reads the same flattened-SRT slots.

For every A/V2s pair (KYTY_RECOMPILE_BDA=2, the descriptor-path control) the check is EQUALITY with A:
the same (name, set, binding) of every descriptor variable (aliases included), the same canonical
interface - every Uniform / UniformConstant / StorageBuffer / PushConstant variable with its
decorations and its type resolved structurally (struct member offsets, array strides, element types),
which fixes the push-data block layout and so its start dword - the same user-data registers and the
same flattened-SRT slots. The strict interface comparison is also reported for V2 (informational: V2
adds the two DMA bindings by design).
Writes C:/kyty/s102/m5/layout_check.json (one row per pair, key 'arm' = V2 | V2s)."""
import json
import re
import subprocess

M5 = 'C:/kyty/s102/m5'
DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
INTERFACE_CLASSES = ('Uniform', 'UniformConstant', 'StorageBuffer', 'PushConstant')


def disassemble(spv):
    return subprocess.run([DIS, '--raw-id', spv], capture_output=True, text=True, errors='replace').stdout


def bindings(spv, text=None):
    text = text if text is not None else disassemble(spv)
    names = dict(re.findall(r'OpName (%\d+) "([^"]*)"', text))
    found = {}
    for var, b in re.findall(r'OpDecorate (%\d+) Binding (\d+)', text):
        found[int(b)] = names.get(var, var)
    push = len(re.findall(r'OpVariable %\d+ PushConstant', text))
    return found, push


def interface(text):
    """Canonical description of every interface variable: sorted list of
    (name, storage class, decorations, canonical type)."""
    names = dict(re.findall(r'OpName (%\d+) "([^"]*)"', text))
    member_names = {}
    for sid, idx, nm in re.findall(r'OpMemberName (%\d+) (\d+) "([^"]*)"', text):
        member_names[(sid, int(idx))] = nm
    decos = {}
    for line in text.splitlines():
        m = re.match(r'\s*OpDecorate (%\d+) (.*)$', line)
        if m:
            decos.setdefault(m.group(1), []).append(m.group(2).strip())
    member_decos = {}
    for line in text.splitlines():
        m = re.match(r'\s*OpMemberDecorate (%\d+) (\d+) (.*)$', line)
        if m:
            member_decos.setdefault((m.group(1), int(m.group(2))), []).append(m.group(3).strip())
    consts = {}
    for cid, typ, val in re.findall(r'(%\d+) = OpConstant (%\d+) (\S+)', text):
        consts[cid] = val
    types = {}
    for line in text.splitlines():
        m = re.match(r'\s*(%\d+) = (OpType\w+)(.*)$', line)
        if m:
            types[m.group(1)] = (m.group(2), m.group(3).split())

    def canon(tid, depth=0):
        if depth > 32 or tid not in types:
            return f'?{tid}'
        op, args = types[tid]
        own = sorted(d for d in decos.get(tid, []) if not d.startswith('Binding') and not d.startswith('DescriptorSet'))
        suffix = f'[{",".join(own)}]' if own else ''
        if op == 'OpTypeInt':
            return f'int{args[0]}{"s" if args[1] == "1" else "u"}' + suffix
        if op == 'OpTypeFloat':
            return f'float{args[0]}' + suffix
        if op == 'OpTypeBool':
            return 'bool' + suffix
        if op == 'OpTypeVector':
            return f'vec{args[1]}<{canon(args[0], depth + 1)}>' + suffix
        if op == 'OpTypeArray':
            return f'array<{canon(args[0], depth + 1)},{consts.get(args[1], args[1])}>' + suffix
        if op == 'OpTypeRuntimeArray':
            return f'rarray<{canon(args[0], depth + 1)}>' + suffix
        if op == 'OpTypeStruct':
            members = []
            for i, mt in enumerate(args):
                md = sorted(member_decos.get((tid, i), []))
                members.append(f'{canon(mt, depth + 1)}{{{",".join(md)}}}')
            return f'struct{{{";".join(members)}}}' + suffix
        if op == 'OpTypePointer':
            return f'ptr<{args[0]},{canon(args[1], depth + 1)}>' + suffix
        if op in ('OpTypeImage', 'OpTypeSampledImage'):
            rest = [canon(a, depth + 1) if a in types else a for a in args]
            return f'{op[6:]}<{",".join(rest)}>' + suffix
        return op[6:] + (f'<{",".join(args)}>' if args else '') + suffix

    out = []
    for vid, ptype, cls in re.findall(r'(%\d+) = OpVariable (%\d+) (\w+)', text):
        if cls not in INTERFACE_CLASSES:
            continue
        out.append((names.get(vid, vid), cls, tuple(sorted(decos.get(vid, []))), canon(ptype)))
    return sorted(out)


def ir_sets(ir):
    text = open(ir, encoding='utf-8', errors='replace').read().split('\nIR:\n', 1)[-1]
    user = sorted({int(r) for r in re.findall(r'GetUserData s(\d+)', text)})
    slots = sorted({int(s, 16) for s in re.findall(r'ReadConst %\d+, 0x([0-9a-f]+)', text)})
    return user, slots


def main():
    rec = json.load(open(f'{M5}/recompile.json', encoding='utf-8'))
    rows = []
    for item in rec['items']:
        for cache in item['caches']:
            mods = {m['name']: m for m in cache['modules']}
            for name, m in mods.items():
                if m['arm'] not in ('V2', 'V2s'):
                    continue
                arm = m['arm']
                a = mods[name[:-len(arm)] + 'A']
                group = 1 if m['stage'] == 'ps' else 0
                expected_new = {46 + 51 * group, 47 + 51 * group}
                ta, tv = disassemble(a['spv']), disassemble(m['spv'])
                ba, pa = bindings(a['spv'], ta)
                bv, pv = bindings(m['spv'], tv)
                ia, iv = interface(ta), interface(tv)
                ua, sa = ir_sets(a['dump']['ir'])
                uv, sv = ir_sets(m['dump']['ir'])
                added = sorted(set(bv) - set(ba))
                removed = sorted(set(ba) - set(bv))
                strict = {'interface_equal': ia == iv, 'interface_vars_A': len(ia),
                          'interface_vars_arm': len(iv),
                          'interface_only_A': [list(x[:3]) for x in ia if x not in iv],
                          'interface_only_arm': [list(x[:3]) for x in iv if x not in ia]}
                if arm == 'V2':
                    row = {'module': name, 'arm': arm, 'bindings_A': {str(k): v for k, v in sorted(ba.items())},
                           'added': {str(k): bv[k] for k in added}, 'removed': removed,
                           # A shader that already used DMA (uses_dma in A) declares both in A too.
                           'added_is_pagetable_and_fault': not removed and (
                               set(added) == expected_new or (not added and expected_new <= set(ba))),
                           'pagetable_and_fault_in_A': expected_new <= set(ba),
                           'push_constant_blocks': [pa, pv], 'user_data_A': ua, 'user_data_V2': uv,
                           'user_data_equal': ua == uv, 'srt_slots_equal': sa == sv,
                           'srt_slots_A': len(sa), 'srt_slots_V2': len(sv)}
                    row.update(strict)
                    row['ok'] = row['added_is_pagetable_and_fault'] and row['user_data_equal'] and row['srt_slots_equal']
                    print(f"{name}: added={row['added']} removed={removed} ok={row['added_is_pagetable_and_fault']} "
                          f"user_data_equal={row['user_data_equal']} ({len(ua)} regs) srt_equal={row['srt_slots_equal']} "
                          f"interface_equal={strict['interface_equal']}")
                else:
                    triples = lambda t: sorted(re.findall(r'OpDecorate (%\d+) Binding (\d+)', t))  # noqa: E731
                    row = {'module': name, 'arm': arm,
                           'bindings_A': {str(k): v for k, v in sorted(ba.items())},
                           'bindings_V2s': {str(k): v for k, v in sorted(bv.items())},
                           'bindings_equal': ba == bv, 'added': {str(k): bv[k] for k in added},
                           'removed': removed,
                           'binding_decorations': [len(triples(ta)), len(triples(tv))],
                           'push_constant_blocks': [pa, pv], 'push_constant_equal': pa == pv,
                           'user_data_A': ua, 'user_data_V2s': uv, 'user_data_equal': ua == uv,
                           'srt_slots_equal': sa == sv, 'srt_slots_A': len(sa), 'srt_slots_V2s': len(sv),
                           'uses_dma': [m.get('bda_rewrite_detail', {}).get('uses_dma_before'),
                                        m.get('bda_rewrite_detail', {}).get('uses_dma_after')]}
                    row.update(strict)
                    row['ok'] = (row['bindings_equal'] and not added and not removed and row['push_constant_equal']
                                 and row['user_data_equal'] and row['srt_slots_equal'] and strict['interface_equal']
                                 and row['binding_decorations'][0] == row['binding_decorations'][1])
                    print(f"{name}: bindings_equal={row['bindings_equal']} interface_equal={strict['interface_equal']} "
                          f"({len(ia)} vars) push={pa}/{pv} user_data_equal={row['user_data_equal']} ({len(ua)} regs) "
                          f"srt_equal={row['srt_slots_equal']} ok={row['ok']}")
                rows.append(row)
    json.dump(rows, open(f'{M5}/layout_check.json', 'w', encoding='utf-8'), indent=1)
    for arm in ('V2', 'V2s'):
        sel = [r for r in rows if r['arm'] == arm]
        print(arm, 'pairs', len(sel), 'bad', [r['module'] for r in sel if not r['ok']])


if __name__ == '__main__':
    main()
