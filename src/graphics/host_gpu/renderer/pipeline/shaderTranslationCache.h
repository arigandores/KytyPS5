#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINE_SHADERTRANSLATIONCACHE_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINE_SHADERTRANSLATIONCACHE_H_

#include "graphics/shader/recompiler/ir/ShaderIR.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"

#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <vector>

namespace Libs::Graphics {

// Disk cache of the GCN -> SPIR-V translation (the resource plan of a shader and the SPIR-V of
// each of its specializations). The Vulkan pipeline cache only covers the driver's part; the
// translation itself took 3-5 s per run of ASTRO BOT (30-60 shaders on every scene cut, each a
// 0.5-1.3 s freeze). Files: _ShaderCache/<title>/<stage>_<hash>_<state hash>.bin, invalidated
// by the translator source signature/options (the plan is an internal structure).
class ShaderTranslationCache {
public:
	struct Permutation {
		ShaderRecompiler::IR::ResourceSpecialization specialization;
		ShaderRecompiler::IR::CompiledShaderInfo     program;
		std::vector<uint32_t>                        spirv;
	};

	struct Entry {
		ShaderRecompiler::IR::ResourcePlan plan;
		std::vector<Permutation>           permutations;
	};

	struct Key {
		uint32_t                   stage           = 0;
		uint64_t                   hash            = 0;
		uint32_t                   user_data_count = 0;
		uint32_t                   code_size       = 0;
		std::span<const uint32_t>  static_state;
	};

	// Disabled when the title or translator signature is unknown, or KYTY_SHADER_CACHE=0.
	explicit ShaderTranslationCache(const std::string& title_id);

	[[nodiscard]] bool Enabled() const { return m_enabled; }

	// Reads the entry of a key; false when there is none or it does not match (stale version).
	bool Load(const Key& key, Entry& entry);
	// Writes (replaces) the entry of a key.
	bool Save(const Key& key, const ShaderRecompiler::IR::ResourcePlan& plan,
	          std::span<const Permutation> permutations);

	// Offline tools: the key stored in a file (owning copy of the static state).
	struct StoredKey {
		uint32_t              stage           = 0;
		uint64_t              hash            = 0;
		uint32_t              user_data_count = 0;
		uint32_t              code_size       = 0;
		std::vector<uint32_t> static_state;
	};
	// Reads any cache file regardless of the translator signature (only the payload hash is
	// checked): shader_cfg_tests KYTY_RECOMPILE re-emits a shader's SPIR-V from its GCN dump and
	// the specialization stored here.
	static bool ReadFileUnchecked(const std::filesystem::path& path, StoredKey& key, Entry& entry);

	[[nodiscard]] uint32_t Loaded() const { return m_loaded; }
	[[nodiscard]] const std::filesystem::path& Directory() const { return m_directory; }
	[[nodiscard]] const std::string&           Signature() const { return m_signature; }
	[[nodiscard]] uint32_t Saved() const { return m_saved; }

private:
	[[nodiscard]] std::filesystem::path PathOf(const Key& key) const;

	bool                  m_enabled = false;
	std::filesystem::path m_directory;
	std::string           m_signature;
	uint32_t              m_loaded = 0;
	uint32_t              m_saved  = 0;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINE_SHADERTRANSLATIONCACHE_H_
