# F35b (HPP-756): check of the code lines cited in docs/track-f/f35b-review.md section 4-5 on ee9632be (and the mirror on
# 399d3271): the anchor (part of the line, >= 12 chars) must be on the cited line; the control line +1 is printed.
# Prints ALL OK or NOT OK. Reads files from git (C:/kyty/KytyPS5).
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RM = 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp'
EM = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp'
DS = 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
TS = 'tests/shaderCfgTests.cpp'
REFS = [
    ('ee9632be', DS, 4489, 'auto& binding = ResolveTextureWith('),
    ('ee9632be', DS, 2824, 'resource.written'),
    ('ee9632be', DS, 2835, 'if (descriptor.IsNull() ||'),
    ('ee9632be', DS, 1325, 'k32Float'),
    ('ee9632be', DS, 1335, 'desc.info.pixel_format    = VulkanFormat(desc.info.guest_format);'),
    ('ee9632be', DS, 1337, 'resource.depth_compare && !resource.manual_depth_compare;'),
    ('ee9632be', DS, 3033, 'Format()'),
    ('ee9632be', DS, 3072, 'auto pixel_format = surface_format.vk_format;'),
    ('ee9632be', RM, 44, 'bool FixF19ManualDepthCompare('),
    ('ee9632be', RM, 45, 'return !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;'),
    ('ee9632be', RM, 492, 'for (uint32_t candidate = 1; candidate < table.descriptors.size(); candidate++) {'),
    ('ee9632be', RM, 729, 'if (FixF19Enabled()) {'),
    ('ee9632be', RM, 733, 'FixF19MergeIndirectTables(next_specialization.images);'),
    ('ee9632be', RM, 1158, 'images.push_back(program.info.images[source.indirect_root]);'),
    ('ee9632be', RM, 1206, 'samplers[pair.sampler].depth_compare |= images[pair.image].depth_compare;'),
    ('ee9632be', RM, 1222, 'if (!samplers[pair.sampler].depth_compare && images[pair.image].depth_compare &&'),
    ('ee9632be', EM, 683, 'const bool  manual_dref    = dref && image.manual_depth_compare;'),
    ('ee9632be', EM, 766, 'opcode = native_dref ? spv::OpImageSampleDrefExplicitLod : spv::OpImageSampleExplicitLod;'),
    ('399d3271', TS, 5896, 'F22View F22MemberView('),
]
ok = True
cache = {}
for commit, path, line, anchor in REFS:
    key = (commit, path)
    if key not in cache:
        r = subprocess.run([G, '-C', REPO, 'show', commit + ':' + path], capture_output=True)
        cache[key] = r.stdout.decode('utf-8', 'replace').split('\n')
    lines = cache[key]
    got = lines[line - 1] if line - 1 < len(lines) else ''
    hit = anchor in got
    ok &= hit
    print('%s %s:%s:%d | %s | +1 | %s' % ('OK ' if hit else 'BAD', commit, path.split('/')[-1], line, got.strip()[:100],
                                          lines[line].strip()[:60] if line < len(lines) else ''))
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
