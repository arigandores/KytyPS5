# F41a (HPP-774): census of the fault-bitmap writes in the SPIR-V of program 380bb9d6 (=0 module of the F12g replay,
# disassembly C:/kyty/f287/f12g/spv0_dis.txt, local file - not in git). Prints: sha256 of the input, the id named
# "fault_buffer", every OpLoad -> OpBitwiseOr -> OpStore triple through an OpAccessChain on it (the RecordBdaFault form),
# every atomic and its target, Workgroup-storage variables, subgroup ops, returns. Last line ALL OK when the input parses.
# Usage: python spv_f41a.py <spv0_dis.txt>
import collections, hashlib, os, re, sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
path = sys.argv[1]
raw = open(path, 'rb').read()
print('input', path, 'sha256', hashlib.sha256(raw).hexdigest())
lines = [l.strip() for l in raw.decode('utf-8', 'replace').split(chr(10))]
fault = None
for l in lines:
    m = re.match(r'OpName (%\S+) "fault_buffer"', l)
    if m:
        fault = m.group(1)
print('fault_buffer id', fault)
chains = {}
for i, l in enumerate(lines):
    m = re.match(r'(%\S+) = OpAccessChain \S+ (%\S+) (.*)', l)
    if m and m.group(2) == fault:
        chains[m.group(1)] = i + 1
print('access chains on fault_buffer', len(chains))
rmw = 0
for i, l in enumerate(lines):
    m = re.match(r'(%\S+) = OpLoad %\S+ (%\S+)$', l)
    if m and m.group(2) in chains and i + 2 < len(lines):
        a, b = lines[i + 1], lines[i + 2]
        if re.match(r'%\S+ = OpBitwiseOr %\S+ ' + re.escape(m.group(1)) + ' ', a) and b.startswith('OpStore ' + m.group(2) + ' '):
            rmw += 1
            print('rmw line', i + 1, '|', l, '|', a, '|', b)
atom = collections.Counter()
atom_other = 0
for i, l in enumerate(lines):
    m = re.search(r'= (OpAtomic\w+) %\S+ (%\S+)', l)
    if m:
        atom[m.group(1)] += 1
        if m.group(2) not in chains:
            atom_other += 1
            print('atomic not on fault_buffer', i + 1, l)
ops = collections.Counter()
for l in lines:
    m = re.search(r'\b(Op[A-Za-z0-9]+)', l)
    if m:
        ops[m.group(1)] += 1
wg_vars = sum(1 for l in lines if re.search(r'OpVariable %\S+ Workgroup', l) or re.search(r'OpTypePointer Workgroup', l))
print('rmw triples', rmw)
print('atomics', dict(atom), 'not on fault_buffer', atom_other)
print('workgroup storage pointers/variables', wg_vars)
print('subgroup ops', {k: v for k, v in ops.items() if k.startswith('OpGroupNonUniform')})
print('barriers', {k: v for k, v in ops.items() if 'Barrier' in k})
print('returns', ops['OpReturn'], 'kill/terminate/demote', ops['OpKill'] + ops['OpTerminateInvocation'] + ops['OpDemoteToHelperInvocation'])
print('ALL OK' if fault and rmw > 0 else 'FAIL')
