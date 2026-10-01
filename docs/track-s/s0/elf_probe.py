# elf_probe.py - S0 (HPP-294): can the GCN payload of the AGC header candidates of the flat ELF be located offline?
# Reads C:/kyty/eboot.elf and elf_inventory.json; prints COUNTS only (no game bytes leave the machine).
import json, struct, collections, hashlib
data = open('C:/kyty/eboot.elf', 'rb').read()
inv = json.load(open('C:/kyty/s288/s0/elf_inventory.json'))['elf']['headers']
ENDPGM = struct.pack('<I', 0xbf810000)
res = collections.Counter(); bytype = collections.Counter(); uniq = {}
fieldhits = collections.Counter()
for h in inv:
    off, cs, ty = h['file_offset'], h['code_size'], h['type']
    found = None
    for fld in (8, 16, 40, 48, 56):
        delta = struct.unpack_from('<q', data, off + fld)[0]
        tgt = off + fld + delta
        if delta == 0 or tgt < 0 or tgt + cs > len(data):
            continue
        code = data[tgt:tgt + cs]
        if ENDPGM in code and code.rfind(ENDPGM) % 4 == 0:
            fieldhits[fld] += 1
            if found is None:
                found = (fld, tgt)
    if found is None:
        res['no payload located'] += 1
        continue
    fld, tgt = found
    code = data[tgt:tgt + cs]
    tail = data[tgt + cs - 64:tgt + cs + 64]
    res['payload located'] += 1
    res['OrbShdr near end'] += (b'OrbShdr' in tail)
    bytype[ty] += 1
    uniq.setdefault((ty, hashlib.sha256(code).hexdigest()), 0)
    uniq[(ty, hashlib.sha256(code).hexdigest())] += 1
print('candidates', len(inv))
print('result', dict(res))
print('field offset hits (relative pointer at header+N whose target holds s_endpgm, dword aligned)', dict(fieldhits))
print('located by binary type', dict(sorted(bytype.items())))
print('unique payloads (type, sha256)', len(uniq), 'by type', dict(sorted(collections.Counter(k[0] for k in uniq).items())))
