"""F42a (HPP-779, ROADMAP s122 item 694(g)(0), (g)(4)): independent SPIR-V counter of the F20 sites (form of the F41a
spv_f41a.py count, own code; it does not share code with the C++ rewrite function).

For one SPIR-V module (list of uint32 words):
  named      - an OpName "fault_buffer" exists (id of the variable);
  bound_dec  - that id carries OpDecorate Binding (the descriptor of the FaultBuffer binding);
  triples    - OpLoad %u32 %v %p; OpBitwiseOr %u32 %o %v %b (or %b %v); OpStore %p %o - three instructions in a row,
               %p the result of an OpAccessChain / OpInBoundsAccessChain whose base is the fault_buffer variable;
  loads_fb   - every OpLoad whose pointer is such an access chain (triples + loads outside a triple);
  atomics_or - OpAtomicOr whose pointer is such an access chain;
  returns    - OpReturn + OpReturnValue;
  local_size - the literal x of OpExecutionMode LocalSize (0 when absent);
  other_half - not countable from SPIR-V; the stand form check reads it from the emitter (see f42a.md).
Module extraction from a translation cache file: every 4-byte aligned SPIR-V magic preceded by a uint32 word count n
such that the instruction walk of n words ends exactly at n (the Writer of shaderTranslationCache.cpp stores the
spirv vector as U32(size) + words).
"""
import struct
import sys

MAGIC = 0x07230203
OP_NAME, OP_DECORATE, OP_LOAD, OP_STORE = 5, 71, 61, 62
OP_ACCESS_CHAIN, OP_IN_BOUNDS_ACCESS_CHAIN = 65, 66
OP_BITWISE_OR, OP_ATOMIC_OR, OP_RETURN, OP_RETURN_VALUE = 197, 242, 253, 254
OP_EXECUTION_MODE, EM_LOCAL_SIZE, DEC_BINDING = 16, 17, 33


def walk(words):
    """Yields (index, opcode, count); raises ValueError on a malformed stream."""
    i = 5
    n = len(words)
    while i < n:
        count = words[i] >> 16
        op = words[i] & 0xffff
        if count == 0 or i + count > n:
            raise ValueError('bad instruction at %d' % i)
        yield i, op, count
        i += count


def name_of(words, i, count):
    raw = struct.pack('<%dI' % (count - 2), *words[i + 2:i + count])
    return raw.split(b'\0', 1)[0].decode('ascii', 'replace')


def scan(words):
    r = {'named': 0, 'bound_dec': 0, 'triples': 0, 'loads_fb': 0, 'atomics_or': 0, 'returns': 0, 'local_size': 0,
         'words': len(words)}
    if len(words) < 5 or words[0] != MAGIC:
        raise ValueError('not SPIR-V')
    ins = list(walk(words))
    fb = set()
    for i, op, c in ins:
        if op == OP_NAME and c >= 3 and name_of(words, i, c) == 'fault_buffer':
            fb.add(words[i + 1])
    r['named'] = len(fb)
    for i, op, c in ins:
        if op == OP_DECORATE and c >= 4 and words[i + 1] in fb and words[i + 2] == DEC_BINDING:
            r['bound_dec'] += 1
        if op == OP_EXECUTION_MODE and c >= 4 and words[i + 2] == EM_LOCAL_SIZE:
            r['local_size'] = words[i + 3]
    chains = set()
    for i, op, c in ins:
        if op in (OP_ACCESS_CHAIN, OP_IN_BOUNDS_ACCESS_CHAIN) and c >= 4 and words[i + 3] in fb:
            chains.add(words[i + 2])
    for k, (i, op, c) in enumerate(ins):
        if op in (OP_RETURN, OP_RETURN_VALUE):
            r['returns'] += 1
        if op == OP_ATOMIC_OR and words[i + 3] in chains:
            r['atomics_or'] += 1
        if op != OP_LOAD or c < 4 or words[i + 3] not in chains:
            continue
        r['loads_fb'] += 1
        if k + 2 >= len(ins):
            continue
        (j, op2, c2), (s, op3, c3) = ins[k + 1][:3], ins[k + 2][:3]
        v, p = words[i + 2], words[i + 3]
        if op2 == OP_BITWISE_OR and c2 == 5 and v in (words[j + 3], words[j + 4]) and op3 == OP_STORE and c3 >= 3 \
                and words[s + 1] == p and words[s + 2] == words[j + 2]:
            r['triples'] += 1
    return r


def modules_in_cache_file(data):
    """SPIR-V modules stored in a translation cache file, in file order."""
    out = []
    magic = struct.pack('<I', MAGIC)
    pos = data.find(magic)
    while pos >= 4:
        if pos % 4 == 0 or True:
            (n,) = struct.unpack_from('<I', data, pos - 4)
            end = pos + 4 * n
            if 5 <= n and end <= len(data):
                words = list(struct.unpack_from('<%dI' % n, data, pos))
                try:
                    for _ in walk(words):
                        pass
                    out.append(words)
                    pos = data.find(magic, end)
                    continue
                except ValueError:
                    pass
        pos = data.find(magic, pos + 1)
    return out


def read_spv(path):
    data = open(path, 'rb').read()
    return list(struct.unpack('<%dI' % (len(data) // 4), data))


if __name__ == '__main__':
    for path in sys.argv[1:]:
        print(path, scan(read_spv(path)))
