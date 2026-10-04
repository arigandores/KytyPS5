"""F23a (HPP-578, item 483(e)(1)): the full list of RDNA2 VALU opcodes that the decoder of main dd7c6b33 sends to
SetUnsupported (opcode level), per family. Encodings of "implemented" - the decoder tables [c code, read by
gcn_f23a.load_tables]; the RDNA2 opcode space and names - ISA [I] (gcn_f23a name tables; codes without a known RDNA2
name are listed as 'not an RDNA2 opcode [I]' and counted apart). VOP3-encoded VOPC / VOP2 / VOP1 follow LookupVop3Opcode."""
import sys

sys.path.insert(0, 'C:/kyty/f287/f23a')
import gcn_f23a as G  # noqa: E402

t = G.load_tables('dd7c6b33')
v2, v1, v31, vc, v3, v3p = (t['VOP2_OPCODE_LIST'], t['VOP1_OPCODE_LIST'], t['VOP3_ENCODED_VOP1_OPCODE_LIST'],
                            t['VOPC_OPCODE_LIST'], t['VOP3_OPCODE_LIST'], t['VOP3P_OPCODE_LIST'])
alias = t['VOP3_VOP2_ALIAS_UNSUPPORTED']
print('decoder tables (dd7c6b33, VectorAluOps.cpp sha256 %s): VOP2 %d, VOP1 %d, VOP3-VOP1 %d, VOPC %d, VOP3 native %d, '
      'VOP3P %d; VOP3-VOP2 aliases rejected %s' % (t['_sha'][:16], len(v2), len(v1), len(v31), len(vc), len(v3), len(v3p),
                                                  sorted(hex(x) for x in alias)))


def vopc_valid(op):
    # groups 0x00-0x3f (F32/F64), 0x80-0xff; 0xaf and 0xbf are not RDNA2 opcodes [I]
    return (op >> 5) in (0, 1, 4, 5, 6, 7) and op not in (0xaf, 0xbf)


out = {}
out['VOP2 (e32)'] = [(op, G.VOP2_NAMES[op]) for op in range(0x40) if op in G.VOP2_NAMES and op not in v2]
out['VOP1 (e32)'] = [(op, G.VOP1_NAMES[op]) for op in range(0x100) if op in G.VOP1_NAMES and op not in v1]
out['VOPC (e32)'] = [(op, G.vopc_name(op)) for op in range(0x100) if vopc_valid(op) and op not in vc]
out['VOP3: VOPC e64 (0x000-0x0ff)'] = [(op, G.vopc_name(op) + '_e64') for op in range(0x100)
                                        if vopc_valid(op) and op not in v3 and op not in vc]
out['VOP3: VOP2 e64 (0x100-0x13f)'] = [(0x100 + op, G.VOP2_NAMES[op] + '_e64') for op in range(0x40)
                                        if op in G.VOP2_NAMES and (0x100 + op) not in v3 and (op in alias or op not in v2)]
out['VOP3: VOP1 e64 (0x180-0x1ff)'] = [(0x180 + op, G.VOP1_NAMES[op] + '_e64') for op in range(0x80)
                                        if op in G.VOP1_NAMES and (0x180 + op) not in v3 and op not in v31]
out['VOP3 native (0x140-0x37f)'] = [(op, G.VOP3_NAMES[op]) for op in sorted(G.VOP3_NAMES) if op not in v3]
out['VOP3P (extra)'] = [(op, G.VOP3P_NAMES[op]) for op in sorted(G.VOP3P_NAMES) if op not in v3p]
odd = {'VOP2 table codes without an RDNA2 VOP2 name [I]': [hex(op) for op in sorted(v2) if op not in G.VOP2_NAMES],
       'VOP1 table codes without an RDNA2 VOP1 name [I]': [hex(op) for op in sorted(v1) if op not in G.VOP1_NAMES],
       'VOP3 table codes without an RDNA2 name [I]': [hex(op) for op in sorted(v3) if op >= 0x140 and op not in G.VOP3_NAMES]}
total = 0
for k, lst in out.items():
    total += len(lst)
    print('%s: %d' % (k, len(lst)))
    print('   ' + ', '.join('0x%x %s' % (op, nm) for op, nm in lst))
print('total opcode-level unsupported RDNA2 VALU encodings (names [I]):', total)
for k, v in odd.items():
    print(k + ':', v)
mul_legacy = [k for k, lst in out.items() for op, nm in lst if 'legacy' in nm]
print('families listing a *_legacy_* opcode:', mul_legacy)
