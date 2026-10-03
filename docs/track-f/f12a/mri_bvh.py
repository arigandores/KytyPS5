# F12a: extract the IMAGE_BVH_INTERSECT_RAY description and any ray-tracing text from the
# AMD machine-readable ISA (amdgpu_isa_rdna2.xml, rdna3.xml) with line numbers.
import re
import sys
import zipfile

zp = 'C:/kyty/f287/f12a/src_ext/mri.zip'
z = zipfile.ZipFile(zp)
for name in sys.argv[1:] or ['amdgpu_isa_rdna2.xml']:
    data = z.read(name).decode('utf-8', 'replace')
    lines = data.split(chr(10))
    print('=== %s lines=%d' % (name, len(lines)))
    pat = re.compile(r'BVH|triangle|Triangle|node_pointer|node pointer|ray_extent', re.I)
    shown = set()
    for i, line in enumerate(lines):
        if pat.search(line):
            for k in range(max(0, i - 2), min(len(lines), i + 3)):
                if k not in shown:
                    shown.add(k)
                    print('%s:%d: %s' % (name, k + 1, lines[k][:400]))
            print('--')
