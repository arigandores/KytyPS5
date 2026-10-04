"""F14e (HPP-505, ROADMAP s122 items 409(v), 415(b)-(v)): KYTY_FIX_F19 (default 0) in the translator.

Usage: python patch_f14e_src.py <repo root>. Whole-line anchors, each must occur exactly once; CR is stripped before the
search and restored if the file had it; files are written with write_bytes.
"""
import sys

ROOT = sys.argv[1].rstrip('/\\')
NL = chr(10)


def patch(rel, edits):
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r', '')
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit('anchor count %d in %s: %r' % (n, rel, old[:120]))
        text = text.replace(old, new)
    out = text.encode('utf-8')
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    open(path, 'wb').write(out)
    print('patched', rel, 'edits', len(edits), 'crlf', crlf)


def L(*lines):
    return NL.join(lines) + NL


# --- ResourceMaterialization.h: declarations after the specialization struct ---------------------------------------
H_OLD = L(
    '	bool operator==(const ResourceSpecialization&) const = default;',
    '};',
    '',
    '// Extracts the descriptor/SRT value graph before resource specialization. The returned plan owns',
)
H_NEW = L(
    '	bool operator==(const ResourceSpecialization&) const = default;',
    '};',
    '',
    '// Track F, F14e (HPP-505, ROADMAP s122 items 409(v), 415(b)-(v)): KYTY_FIX_F19, default OFF (unset, empty, 0, false,',
    '// off, no = off; any other value as Common::EnvValueOn), read once per process. On: MaterializeResources puts a',
    '// comparison image on the shader (manual) comparison path only by FixF19ManualDepthCompare, and an indirect image',
    '// table is manual as a whole when that rule makes any of its members manual (FixF19MergeIndirectTables). Off: the',
    '// rule before the fix, verbatim. The translation cache keys the value in its signature and directory',
    '// (shaderTranslationCache.cpp).',
    'bool FixF19Enabled();',
    '// The =1 rule: a comparison image is compared in the shader unless its T# is null or the renderer gives its guest',
    '// format a depth view - the formats of DEPTH_FORMAT_POLICIES (imageInfo.h), the table descriptors.cpp resolves the',
    '// host view of a comparison texture by (k16UNorm -> D16_UNORM, k32Float -> D32_SFLOAT).',
    'bool FixF19ManualDepthCompare(Prospero::BufferFormat format, bool null_descriptor);',
    '// The =1 indirect-table branch (variant O1 of item 415(b)): one opcode samples every member of an indirect image',
    '// table (the root decides it), so for every table (root and candidates, indirect_root) the manual_depth_compare',
    '// flag of all members becomes the "or" of their flags.',
    'void FixF19MergeIndirectTables(std::vector<ResourceSpecialization::Image>& images);',
    '',
    '// Extracts the descriptor/SRT value graph before resource specialization. The returned plan owns',
)

# --- ResourceMaterialization.cpp -------------------------------------------------------------------------------------
C_INC_OLD = L(
    '#include "common/assert.h"',
    '#include "graphics/guest_gpu/gpu_format.h"',
)
C_INC_NEW = L(
    '#include "common/assert.h"',
    '#include "common/envFlag.h"',
    '#include "graphics/guest_gpu/gpu_format.h"',
    '#include "graphics/host_gpu/renderer/image/imageInfo.h"',
)

C_FN_OLD = L(
    '// KYTY_CBANK_COPY (default 1): const-bank V#s are specialized as 16-byte aligned regardless of',
)
C_FN_NEW = L(
    '// Track F, F14e (ROADMAP s122 items 409(v), 415(b)-(v)): see ResourceMaterialization.h.',
    'bool FixF19Enabled() {',
    '	static const bool enabled = Common::EnvFlagOn("KYTY_FIX_F19");',
    '	return enabled;',
    '}',
    '',
    'bool FixF19ManualDepthCompare(Prospero::BufferFormat format, bool null_descriptor) {',
    '	return !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;',
    '}',
    '',
    'void FixF19MergeIndirectTables(std::vector<ResourceSpecialization::Image>& images) {',
    '	for (uint32_t root = 0; root < images.size(); root++) {',
    '		if (images[root].indirect_root != root) {',
    '			continue;',
    '		}',
    '		bool manual = false;',
    '		for (const auto& image: images) {',
    '			manual = manual || (image.indirect_root == root && image.manual_depth_compare);',
    '		}',
    '		for (auto& image: images) {',
    '			if (image.indirect_root == root) {',
    '				image.manual_depth_compare = manual;',
    '			}',
    '		}',
    '	}',
    '}',
    '',
    '// KYTY_CBANK_COPY (default 1): const-bank V#s are specialized as 16-byte aligned regardless of',
)

C_RULE_OLD = L(
    '			// The renderer resolves non-null R32F comparison textures as native D32.',
    '			// Other color formats require shader comparison, irrespective of byte size.',
    '			// Null native-comparison descriptors use a D32 placeholder at binding time.',
    '			image.manual_depth_compare = !NullImageDescriptor(descriptor) &&',
    '			                             format != Prospero::BufferFormat::k32Float;',
    '		}',
)
C_RULE_NEW = L(
    '			// The renderer resolves non-null R32F comparison textures as native D32.',
    '			// Other color formats require shader comparison, irrespective of byte size.',
    '			// Null native-comparison descriptors use a D32 placeholder at binding time.',
    '			if (FixF19Enabled()) {',
    '				// Track F, F14e (ROADMAP s122 item 409(v)): native for every format the renderer views as',
    '				// depth (k16UNorm joins k32Float), shader comparison for the rest.',
    '				image.manual_depth_compare =',
    '				    FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));',
    '			} else {',
    '				image.manual_depth_compare = !NullImageDescriptor(descriptor) &&',
    '				                             format != Prospero::BufferFormat::k32Float;',
    '			}',
    '		}',
)

C_MERGE_OLD = L(
    '	SamplerPlan sampler_plan;',
    '	if (!BuildSamplerPlan(program.info, next_specialization.images, sampler_plan)) {',
)
C_MERGE_NEW = L(
    '	if (FixF19Enabled()) {',
    '		// Track F, F14e (ROADMAP s122 item 415(b), variant O1): an indirect table with a shader-compared',
    '		// member is shader-compared as a whole; the shared-sampler pass of ApplyResourceSpecialization',
    '		// then runs as before.',
    '		FixF19MergeIndirectTables(next_specialization.images);',
    '	}',
    '	SamplerPlan sampler_plan;',
    '	if (!BuildSamplerPlan(program.info, next_specialization.images, sampler_plan)) {',
)

# --- shaderTranslationCache.cpp --------------------------------------------------------------------------------------
T_INC_OLD = L('#include "graphics/shader/recompiler/ir/Value.h"')
T_INC_NEW = L(
    '#include "graphics/shader/recompiler/ir/Value.h"',
    '#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"',
)
T_VAR_OLD = L(
    '	// Track F, F12d (ROADMAP p.391(v)): KYTY_FIX_F10=1 (the default since FS5a, p.410(g)(1)) adds ":fixf10" last, so',
    '	// =0 and =1 never share a signature or a directory.',
    '	const std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +',
    '	                            (ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? ":bdalean" : "") +',
    '	                            (ShaderRecompiler::Decoder::FixB26Enabled() ? ":fixb26" : "") +',
    '	                            (ShaderRecompiler::Decoder::FixB1BEnabled() ? ":fixb1b" : "") +',
    '	                            (ShaderRecompiler::Decoder::FixF10Enabled() ? ":fixf10" : "");',
)
T_VAR_NEW = L(
    '	// Track F, F12d (ROADMAP p.391(v)): KYTY_FIX_F10=1 (the default since FS5a, p.410(g)(1)) adds ":fixf10" last, so',
    '	// =0 and =1 never share a signature or a directory.',
    '	// Track F, F14e (ROADMAP s122 item 409(v)): KYTY_FIX_F19=1 (default 0) adds ":fixf19" after ":fixf10", last.',
    '	const std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +',
    '	                            (ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? ":bdalean" : "") +',
    '	                            (ShaderRecompiler::Decoder::FixB26Enabled() ? ":fixb26" : "") +',
    '	                            (ShaderRecompiler::Decoder::FixB1BEnabled() ? ":fixb1b" : "") +',
    '	                            (ShaderRecompiler::Decoder::FixF10Enabled() ? ":fixf10" : "") +',
    '	                            (ShaderRecompiler::IR::FixF19Enabled() ? ":fixf19" : "");',
)

patch('src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.h', [(H_OLD, H_NEW)])
patch('src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp',
      [(C_INC_OLD, C_INC_NEW), (C_FN_OLD, C_FN_NEW), (C_RULE_OLD, C_RULE_NEW), (C_MERGE_OLD, C_MERGE_NEW)])
patch('src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', [(T_INC_OLD, T_INC_NEW), (T_VAR_OLD, T_VAR_NEW)])
print('ALL OK')
