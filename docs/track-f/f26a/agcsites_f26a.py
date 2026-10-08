# F26a (HPP-688): call sites in eboot.elf of every libSceAgc / libSceAgcDriver import (PLT stub of plt.tsv), with the name of
# the emulator HLE.  These are the places where the emulator, not the game, writes PM4 dwords into the guest CommandBuffer.
# usage: agcsites_f26a.py <eboot.elf> <plt.tsv>
import sys, struct, re, collections
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
elf = Elf(sys.argv[1]); e = elf.data
stubs = {}
for l in open(sys.argv[2], encoding='utf-8'):
    a, idx, lib, nid, nm, impl = l.rstrip('\n').split('\t')
    if lib.startswith('libSceAgc'):
        stubs[int(a, 16)] = (lib, nid, impl)
calls = collections.defaultdict(list)
for v, o, fs in elf.code_segments():
    seg = e[o:o + fs]
    for m in re.finditer(rb'[\xe8\xe9]', seg):
        i = m.start()
        if i + 5 > fs: continue
        t = v + i + 5 + struct.unpack('<i', seg[i + 1:i + 5])[0]
        if t in stubs: calls[t].append(v + i)
print('libSceAgc* imports %d, called %d' % (len(stubs), len(calls)))
for t, (lib, nid, impl) in sorted(stubs.items(), key=lambda x: -len(calls.get(x[0], []))):
    c = calls.get(t, [])
    print('%-16s %-12s %-45s sites %4d  %s' % (lib, nid, impl, len(c), ' '.join('0x%x' % x for x in c[:6])))
