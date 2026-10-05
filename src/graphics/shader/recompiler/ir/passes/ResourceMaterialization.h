#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_RESOURCEMATERIALIZATION_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_RESOURCEMATERIALIZATION_H_

#include "graphics/shader/recompiler/ir/passes/SrtWalker.h"

namespace Libs::Graphics::ShaderRecompiler::IR {

// KYTY_VEC_CONST=1: the V# base alignment class is part of the specialization (static uvec4
// constant loads); default: decided at run time by the emitter.
bool VectorConstStaticAlignmentClass();
// KYTY_CBANK_COPY (default 1): const-bank V#s specialized as 16-byte aligned (host copies).
bool ConstBankAlignedCopy();

// Canonical module-affecting resource state. Runtime addresses and descriptor payloads remain in
// ResourceSnapshot and therefore do not create shader permutations.
struct ResourceSpecialization {
	struct Buffer {
		uint32_t               packed_stride                   = 0;
		Prospero::BufferFormat descriptor_format               = Prospero::BufferFormat::kInvalid;
		uint32_t               descriptor_swizzle              = DstSel(4, 5, 6, 7);
		bool                   operator==(const Buffer&) const = default;
	};

	struct Image {
		Prospero::TextureNumericClass numeric_class = Prospero::TextureNumericClass::Unsupported;
		Decoder::ImageDimension       dimension     = Decoder::ImageDimension::Unknown;
		uint32_t                      mip_count     = 1;
		Prospero::BufferFormat        conversion_format          = Prospero::BufferFormat::kInvalid;
		uint32_t                      shader_swizzle             = ShaderImageIdentitySwizzle;
		uint32_t                      indirect_root              = ImageResource::NoIndirectImage;
		uint32_t                      indirect_mapping_offset    = 0;
		uint32_t                      indirect_search_iterations = 0;
		bool                          cube                       = false;
		bool                          manual_depth_compare       = false;
		uint32_t                      depth_compare_op           = 0;
		bool                          fmask                      = false;
		bool                          operator==(const Image&) const = default;
	};

	std::vector<Buffer> buffers;
	std::vector<Image>  images;

	bool operator==(const ResourceSpecialization&) const = default;
};

// Track F, F14e (HPP-505, ROADMAP s122 items 409(v), 415(b)-(v)): KYTY_FIX_F19, default ON since FS8a (HPP-571, item
// 471(g)(1): unset or "" = ON; 0, false, off, no = off; any other value as Common::EnvValueOn; F14e had default OFF),
// read once per process. On: MaterializeResources puts a
// comparison image on the shader (manual) comparison path only by FixF19ManualDepthCompare, and an indirect image
// table is manual as a whole when that rule makes any of its members manual (FixF19MergeIndirectTables). Off: the
// rule before the fix, verbatim. The translation cache keys the value in its signature and directory
// (shaderTranslationCache.cpp).
bool FixF19Enabled();
// The =1 rule: a comparison image is compared in the shader unless its T# is null or the renderer gives its guest
// format a depth view - the formats of DEPTH_FORMAT_POLICIES (imageInfo.h), the table descriptors.cpp resolves the
// host view of a comparison texture by (k16UNorm -> D16_UNORM, k32Float -> D32_SFLOAT).
bool FixF19ManualDepthCompare(Prospero::BufferFormat format, bool null_descriptor);
// The =1 indirect-table branch (variant O1 of item 415(b)): one opcode samples every member of an indirect image
// table (the root decides it), so for every table (root and candidates, indirect_root) the manual_depth_compare
// flag of all members becomes the "or" of their flags.
void FixF19MergeIndirectTables(std::vector<ResourceSpecialization::Image>& images);

// Extracts the descriptor/SRT value graph before resource specialization. The returned plan owns
// its values and is independent of the translated shader CFG.
ResourcePlan ExtractResourcePlan(const Program& program);

// Resolves and specializes the immutable resource plan in one transaction. On failure both
// destinations are unchanged.
bool MaterializeResources(const ResourcePlan& program, const SrtRuntime& runtime,
                          ResourceSnapshot& snapshot, ResourceSpecialization& specialization);

// Applies an already-derived specialization to native IR before layout and emission.
void ApplyResourceSpecialization(Program& program, const ResourceSpecialization& specialization);

} // namespace Libs::Graphics::ShaderRecompiler::IR

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_RESOURCEMATERIALIZATION_H_ */
