# S14a: extract shader / pipeline / frame lines of one S10 log with line numbers (binary stream)
import sys, os, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
tag = sys.argv[1]
p = 'C:/kyty/s288/s10/log_%s.txt' % tag
PFX = (b'ShaderRegister:', b'ShaderFirstUse:', b'AvTrace: shader', b'AvTrace: pipeline ', b'AvTrace: pcw',
       b'AsyncPipelines', b'PipelinePrecache', b'Vulkan pipeline cache', b'Shader translation cache',
       b'GuestOut: Level has started', b'ShaderSeed', b'S-pcw', b'FrameTrace: n=', b'PipelineTrace',
       b'CsPretranslate: ', b'ShaderPreparation', b'Shaders: ', b'DualSrcBlend', b'GamePatch', b'AvTrace: flip',
       b'AvTrace: present', b'AvTrace: hold', b'AvTrace: draw')
h = hashlib.sha256()
n = 0
with open(p, 'rb') as f, open('C:/kyty/s288/s14a/x_%s.txt' % tag, 'wb') as o:
    for n, l in enumerate(f, 1):
        h.update(l)
        if l.startswith(PFX):
            o.write(b'%d\t' % n + l.rstrip(b'\r\n')[:6000] + b'\n')
print(tag, 'lines', n, 'sha256', h.hexdigest(), 'out', os.path.getsize('C:/kyty/s288/s14a/x_%s.txt' % tag))
