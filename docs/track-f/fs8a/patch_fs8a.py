# FS8a (HPP-571, ROADMAP s122 items 471(g)(1), 522(d)): KYTY_FIX_F19 default 0 -> 1 in the form of FS4a 17adaf80
# (unset or "" = ON; otherwise Common::EnvValueOn), one read (static const bool) kept; comments "default 0/OFF" by the item.
# Anchors are whole lines; CRLF-safe (strips \r before the search, restores it); writes bytes.
# Usage: patch_fs8a.py <source root>
import sys, os

root = sys.argv[1]

def patch(rel, pairs):
    path = os.path.join(root, rel)
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    lines = text.split('\n')
    for old, new in pairs:
        old_l = old.split('\n')
        hits = [i for i in range(len(lines) - len(old_l) + 1) if lines[i:i + len(old_l)] == old_l]
        if len(hits) != 1:
            print('ANCHOR FAIL', rel, len(hits), repr(old_l[0]))
            sys.exit(2)
        i = hits[0]
        lines[i:i + len(old_l)] = new.split('\n')
        print('patched', rel, 'line', i + 1)
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    open(path, 'wb').write(out.encode('utf-8'))

patch('src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', [(
    '// Track F, F14e (ROADMAP s122 items 409(v), 415(b)-(v)): see ResourceMaterialization.h.\n'
    'bool FixF19Enabled() {\n'
    '\tstatic const bool enabled = Common::EnvFlagOn("KYTY_FIX_F19");\n'
    '\treturn enabled;\n'
    '}',
    '// Track F, F14e (ROADMAP s122 items 409(v), 415(b)-(v)): see ResourceMaterialization.h.\n'
    'bool FixF19Enabled() {\n'
    '\t// Track F, FS8a (HPP-571, ROADMAP s122 item 471(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any\n'
    '\t// other value as EnvValueOn (the form of FS4a 17adaf80).\n'
    '\tstatic const bool enabled = [] {\n'
    '\t\tconst char* value = std::getenv("KYTY_FIX_F19");\n'
    '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);\n'
    '\t}();\n'
    '\treturn enabled;\n'
    '}')])

patch('src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.h', [(
    '// Track F, F14e (HPP-505, ROADMAP s122 items 409(v), 415(b)-(v)): KYTY_FIX_F19, default OFF (unset, empty, 0, false,\n'
    '// off, no = off; any other value as Common::EnvValueOn), read once per process. On: MaterializeResources puts a',
    '// Track F, F14e (HPP-505, ROADMAP s122 items 409(v), 415(b)-(v)): KYTY_FIX_F19, default ON since FS8a (HPP-571, item\n'
    '// 471(g)(1): unset or "" = ON; 0, false, off, no = off; any other value as Common::EnvValueOn; F14e had default OFF),\n'
    '// read once per process. On: MaterializeResources puts a')])

patch('src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', [(
    '\t// Track F, F14e (ROADMAP s122 item 409(v)): KYTY_FIX_F19=1 (default 0) adds ":fixf19" after ":fixf10", last.',
    '\t// Track F, F14e (ROADMAP s122 item 409(v)): KYTY_FIX_F19=1 (the default since FS8a, p.471(g)(1)) adds ":fixf19" after\n'
    '\t// ":fixf10", last.')])
print('PATCH OK')
