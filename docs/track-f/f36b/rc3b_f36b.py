# F36b (HPP-759): RC3(b) own check - SPIR-V modules (magic 0x07230203) inside the cache files of be4c35a2031fd3f4 of every variant
# catalog: sha256 of each module vs the def arm (FS11) and the captured module (S12). Read only. ASCII only.
import hashlib, struct, glob, sys
D = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/'
REF = {'def_fs11': open('C:/kyty/f287/f36a/arms/ps_be4c35a2031fd3f4_def.spv', 'rb').read(),
       'captured_s12': open('C:/kyty/f287/f36a/spv/s12_p0.spv', 'rb').read()}
REFH = {hashlib.sha256(v).hexdigest(): k for k, v in REF.items()}
for f in sorted(glob.glob(D + '*/ps_be4c35a2031fd3f4_*.bin')):
    b = open(f, 'rb').read()
    print(f.replace(D, ''), 'bytes', len(b), 'sha', hashlib.sha256(b).hexdigest()[:16])
    i = 0
    while True:
        i = b.find(struct.pack('<I', 0x07230203), i)
        if i < 0:
            break
        for k, v in REF.items():
            if b[i:i + len(v)] == v:
                print('   module at', i, '=', k, hashlib.sha256(v).hexdigest()[:16], 'words', len(v) // 4)
        i += 4
