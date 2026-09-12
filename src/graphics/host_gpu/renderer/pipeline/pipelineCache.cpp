#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"

#include "graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h"
#include "graphics/host_gpu/renderer/pipeline/computePretranslation.h"
#include "graphics/guest_gpu/command_processor/commandProcessor.h"
#include "graphics/guest_gpu/pm4.h"

#include "common/frameStats.h"

#include "common/assert.h"
#include "common/emulatorConfig.h"
#include "common/file.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
#include "graphics/host_gpu/renderer/debug.h"
#include "graphics/host_gpu/renderer/depthRenderTarget.h"
#include "graphics/host_gpu/renderer/image/imageView.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/shader/recompiler/ShaderRecompiler.h"
#include "graphics/shader/shaderCompiler.h"
#include "common/timer.h"
#include "kernel/memory.h"
#include "kernel/pthread.h"
#include "kytyGitVersion.h"
#include "loader/systemContent.h"

#include <algorithm>
#include <cstdlib>
#include <unordered_set>
#include <mutex>
#include <array>
#include <atomic>
#include <cctype>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <deque>
#include <fstream>
#include <fmt/format.h>
#include <limits>
#include <span>
#include <set>
#include <spirv-tools/libspirv.hpp>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>
#include <xxhash.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#endif

namespace Libs::Graphics {

namespace {

// KYTY_ASYNC_PIPELINES: 0 = compile graphics pipelines synchronously on the GuestGpu thread
// (freezing the guest clock), 1 = compile them on a worker pool while the draws that need them
// are skipped (default). A scene cut brings 4-13 new vertex/pixel shaders at once and the
// driver takes 170-500 ms per new shader module: serial compilation froze the frame for 1-5 s.
int AsyncPipelinesMode() {
	static const int mode = [] {
		const char* value = std::getenv("KYTY_ASYNC_PIPELINES");
		return value == nullptr ? 1 : std::atoi(value);
	}();
	return mode;
}

// The draw that queues a pipeline waits this long for it: driver re-links of already compiled
// modules take ~0.2 ms and would otherwise skip a draw for one frame (visible flicker).
uint32_t AsyncPipelineWaitUs() {
	static const uint32_t wait_us = [] {
		const char* value = std::getenv("KYTY_ASYNC_PIPELINE_WAIT_US");
		return value == nullptr ? 4000u : static_cast<uint32_t>(std::atoi(value));
	}();
	return wait_us;
}

uint32_t AsyncPipelineThreads() {
	static const uint32_t threads = [] {
		if (const char* value = std::getenv("KYTY_ASYNC_PIPELINE_THREADS"); value != nullptr) {
			return std::max(1u, static_cast<uint32_t>(std::atoi(value)));
		}
		// Few, low-priority workers: the guest's loading threads must keep their CPU share (an
		// asset registry that lags behind the cutscene makes the game assert), and one driver
		// compile already runs its own helper threads.
		const auto hw = std::thread::hardware_concurrency();
		return std::clamp(hw / 4u, 2u, 4u);
	}();
	return threads;
}

uint64_t HostMicros() {
	const auto frequency = Common::Timer::QueryPerformanceFrequency();
	if (frequency == 0) {
		return 0;
	}
	const auto counter = Common::Timer::QueryPerformanceCounter();
	return (counter / frequency) * 1000000u + ((counter % frequency) * 1000000u) / frequency;
}

bool AvTraceEnabled() {
	static const bool enabled = std::getenv("KYTY_AV_TRACE") != nullptr;
	return enabled;
}

vk::PolygonMode ResolvePolygonMode(const HW::ModeControl& mode, bool cull_front, bool cull_back) {
	// CxPrimitiveSetup::PolygonMode disables both per-face modes when it is zero.
	if (mode.poly_mode == 0) {
		return vk::PolygonMode::eFill;
	}
	EXIT_NOT_IMPLEMENTED(mode.poly_mode != 1);
	if (cull_front && cull_back) {
		return vk::PolygonMode::eFill;
	}
	if (!cull_front && !cull_back && mode.polymode_front_ptype != mode.polymode_back_ptype) {
		EXIT("Pipeline: different polygon modes for two visible faces are unsupported\n");
	}
	// Vulkan has one polygon mode. A culled face does not constrain that mode.
	const auto polygon_mode = cull_front ? mode.polymode_back_ptype : mode.polymode_front_ptype;
	switch (polygon_mode) {
		case 0: return vk::PolygonMode::ePoint;
		case 1: return vk::PolygonMode::eLine;
		case 2: return vk::PolygonMode::eFill;
		default: EXIT("Pipeline: invalid polygon mode %u\n", polygon_mode);
	}
}

std::string DriverCacheSignature(const vk::PhysicalDeviceProperties& properties) {
	constexpr char hex[] = "0123456789abcdef";
	std::string    uuid(VK_UUID_SIZE * 2, '0');
	for (size_t i = 0; i < VK_UUID_SIZE; i++) {
		uuid[i * 2]     = hex[properties.pipelineCacheUUID[i] >> 4u];
		uuid[i * 2 + 1] = hex[properties.pipelineCacheUUID[i] & 0xfu];
	}
	// Vulkan validates the shader and pipeline keys inside this opaque cache. Its compatibility
	// is defined by the device/driver UUID, not by an unrelated emulator commit.
	return fmt::format("KytyPC2:{:08x}:{:08x}:{:08x}:{}\n",
	                   properties.vendorID, properties.deviceID, properties.driverVersion, uuid);
}

// Salt only the module passed to Vulkan, including modules loaded from translation/seed caches.
// The saved translation stays unchanged; a new salt gives a fresh driver compilation experiment.
vk::ShaderModule CreateCachedModule(vk::Device device, const std::vector<uint32_t>& source) {
	std::vector<uint32_t> salted;
	const auto* words = &source;
	if (const char* salt = std::getenv("KYTY_PIPELINE_SALT"); salt != nullptr && salt[0] != 0) {
		uint32_t void_id = 0;
		size_t names = source.size();
		for (size_t i = 5; i < source.size();) {
			const auto count = source[i] >> 16u;
			EXIT_IF(count == 0 || count > source.size() - i);
			const auto op = source[i] & 0xffffu;
			if (op == 5 && names == source.size()) names = i; // OpName
			if (op == 19 && count == 2) void_id = source[i + 1]; // OpTypeVoid
			i += count;
		}
		EXIT_IF(void_id == 0 || names == source.size());
		const auto name = fmt::format("kyty_pipeline_{:016x}", XXH3_64bits(salt, std::strlen(salt)));
		const auto string_words = (name.size() + 1 + 3) / 4;
		std::vector<uint32_t> instruction(2 + string_words, 0);
		instruction[0] = static_cast<uint32_t>(instruction.size() << 16u) | 5u;
		instruction[1] = void_id;
		std::memcpy(instruction.data() + 2, name.c_str(), name.size() + 1);
		salted = source;
		salted.insert(salted.begin() + names, instruction.begin(), instruction.end());
		words = &salted;
	}
	vk::ShaderModuleCreateInfo info {};
	info.codeSize = words->size() * sizeof(uint32_t);
	info.pCode = words->data();
	vk::ShaderModule module = nullptr;
	RequireVulkanSuccess(device.createShaderModule(&info, nullptr, &module), "create shader module");
	return module;
}

std::string PipelineCacheTitleId() {
	std::string title_id;
	if ((!Loader::SystemContentParamSfoGetString("TITLE_ID", &title_id) || title_id.empty()) &&
	    (!Loader::SystemContentParamSfoGetString("CONTENT_ID", &title_id) || title_id.empty())) {
		return {};
	}
	if (!std::ranges::all_of(title_id, [](unsigned char c) {
		    return std::isalnum(c) != 0 || c == '-' || c == '_';
	    })) {
		return {};
	}
	return title_id;
}

template <typename... Args>
void PipelineCacheLog(fmt::format_string<Args...> format, Args&&... args) {
	auto message = fmt::format(format, std::forward<Args>(args)...);
	message += '\n';
	if (Log::GetDirection() != Log::Direction::Console) {
		std::fwrite(message.data(), 1, message.size(), stdout);
		std::fflush(stdout);
	}
	Log::Write(message);
	Log::Flush();
}

// Live guest memory for SRT walking. The evaluator falls back to a raw host memcpy when no
// reader is installed, which turns an unmapped pointer in a descriptor chain into a host
// access violation instead of a reported evaluation failure. The walk reads tens of words per
// draw, mostly from the same descriptor pages: the caller passes a ShaderReadCache as userdata
// and each page is validated once per lookup (the validated map lock costs more than the read).
struct ShaderReadCache {
	struct Page {
		uint64_t address = UINT64_MAX;
		const uint8_t* backing = nullptr;
	};
	struct Pages {
		Page last;
		std::array<Page, 8> entries;

		bool Find(uint64_t page) {
			if (last.address == page) return true;
			if (!Enabled()) return false;
			const auto& entry = entries[Slot(page)];
			if (entry.address != page) return false;
			last = entry;
			return true;
		}
		void Store(uint64_t page, const void* backing) {
			last = {page, static_cast<const uint8_t*>(backing)};
			if (Enabled()) entries[Slot(page)] = last;
		}
		static size_t Slot(uint64_t page) { return ((page >> 12u) ^ (page >> 19u)) & 7u; }
		static bool Enabled() {
			static const bool enabled = [] {
				const auto* value = std::getenv("KYTY_SRT_PAGE_CACHE");
				return value == nullptr || value[0] != '0';
			}();
			return enabled;
		}
	};
	// Keep live and GPU-clean validations separate, and never keep them across lookups.
	Pages live;
	Pages clean;
};

// Guest memory for specialization decisions: only words with no pending GPU writes may be read
// (upstream reads them one at a time with a dirty-range query per word; the SRT control-flow
// conditions add several per draw, so the whole page is validated once and reused).
bool ReadShaderGuestMemory(void* userdata, uint64_t address, uint32_t* value) {
	if (Common::FrameStats::Enabled()) {
		Common::FrameStats::Add(Common::FrameStats::Counter::ProgCleanReads, 1);
	}
	if (value == nullptr) {
		return false;
	}
	auto* cache = static_cast<ShaderReadCache*>(userdata);
	constexpr uint64_t PageSize = 0x1000;
	const auto         page     = address & ~(PageSize - 1);
	if (cache != nullptr && (address & 3u) == 0) {
		if (!cache->clean.Find(page)) {
			const void* backing = nullptr;
			if (Libs::LibKernel::Memory::TryGetGpuCleanBackingPointer(page, PageSize, &backing)) {
				cache->clean.Store(page, backing);
			}
		}
		if (cache->clean.last.address == page) {
			std::memcpy(value, cache->clean.last.backing + (address - page), sizeof(*value));
			return true;
		}
	}
	// The page is partly GPU-dirty or not one mapping: decide per word as before.
	return Libs::LibKernel::Memory::TryReadGpuCleanBacking(address, value, sizeof(*value));
}

bool ReadShaderLiveMemory(void* userdata, uint64_t address, uint32_t* value) {
	if (Common::FrameStats::Enabled()) {
		Common::FrameStats::Add(Common::FrameStats::Counter::ProgReads, 1);
	}
	if (value == nullptr) {
		return false;
	}
	auto* cache = static_cast<ShaderReadCache*>(userdata);
	constexpr uint64_t PageSize = 0x1000;
	const auto         page     = address & ~(PageSize - 1);
	if (cache != nullptr && (address & 3u) == 0) {
		if (!cache->live.Find(page)) {
			const void* backing = nullptr;
			if (Libs::LibKernel::Memory::TryGetBackingPointer(page, PageSize, &backing)) {
				cache->live.Store(page, backing);
			} else {
				cache->live.last = {};
			}
		}
		if (cache->live.last.address == page) {
			std::memcpy(value, cache->live.last.backing + (address - page), sizeof(*value));
			return true;
		}
	}
	return Libs::LibKernel::Memory::TryReadBacking(address, value, sizeof(*value));
}

void DumpShaderSpirv(const char* stage_name, uint64_t shader_hash,
                     const std::vector<uint32_t>& spirv) {
	if (!Config::GraphicsDebugDumpEnabled()) {
		return;
	}
	static std::atomic_int id = 0;
	const auto path = Config::GetShaderLogFolder() / fmt::format("{:04d}_new_shader_{}_{:016x}.spv",
	                                                             id++, stage_name, shader_hash);
	Common::File::CreateDirectories(path.parent_path());
	Common::File file(path);
	if (file.IsInvalid()) {
		const auto path_text = Common::PathToString(path);
		LOGF_COLOR(Log::Color::BrightRed, "Can't create file: %s\n", path_text.c_str());
		return;
	}
	file.Write(spirv.data(), spirv.size() * sizeof(uint32_t));
}

void DumpShaderOriginal(const char* stage_name, uint64_t shader_hash,
                        std::span<const uint32_t> code, const std::string& decoded_dump) {
	if (!Config::GraphicsDebugDumpEnabled()) {
		return;
	}
	EXIT_IF(code.empty());
	static std::atomic_int id = 0;
	const auto base = Config::GetShaderLogFolder() / "original" /
	                  fmt::format("{:04d}_new_shader_{}_{:016x}", id++, stage_name, shader_hash);
	Common::File::CreateDirectories(base.parent_path());
	for (const auto& [suffix, data, size]: {
	         std::tuple {".bin", static_cast<const void*>(code.data()), code.size_bytes()},
	         std::tuple {".rdna2", static_cast<const void*>(decoded_dump.data()),
	                     decoded_dump.size()},
	     }) {
		if (size == 0) {
			continue;
		}
		auto path = base;
		path += suffix;
		Common::File file(path);
		if (file.IsInvalid()) {
			const auto path_text = Common::PathToString(path);
			LOGF_COLOR(Log::Color::BrightRed, "Can't create file: %s\n", path_text.c_str());
		} else {
			file.Write(data, size);
		}
	}
}

// KYTY_DUMP_GCN=1 writes the raw GCN code of every shader to <shader log folder>/gcn/ before it
// is translated (unlike --graphics-debug-dump, which dumps only after a successful translation
// and slows the game with IR/SPIR-V text). Failed translations can then be replayed offline.
void DumpShaderGcn(ShaderType stage, uint64_t shader_hash, std::span<const uint32_t> code) {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_DUMP_GCN");
		return value != nullptr && value[0] != '0';
	}();
	if (!enabled || code.empty()) {
		return;
	}
	static std::mutex                   mutex;
	static std::unordered_set<uint64_t> written;
	{
		std::lock_guard lock(mutex);
		if (!written.insert(shader_hash ^ (static_cast<uint64_t>(stage) << 56u)).second) {
			return;
		}
	}
	const char* stage_name = "xx";
	switch (stage) {
		case ShaderType::Vertex: stage_name = "vs"; break;
		case ShaderType::Mesh: stage_name = "ms"; break;
		case ShaderType::Pixel: stage_name = "ps"; break;
		case ShaderType::Compute: stage_name = "cs"; break;
		default: break;
	}
	const auto path = Config::GetShaderLogFolder() / "gcn" /
	                  fmt::format("{}_{:016x}.bin", stage_name, shader_hash);
	Common::File::CreateDirectories(path.parent_path());
	Common::File file(path);
	if (file.IsInvalid()) {
		const auto path_text = Common::PathToString(path);
		LOGF_COLOR(Log::Color::BrightRed, "Can't create file: %s\n", path_text.c_str());
		return;
	}
	file.Write(code.data(), code.size_bytes());
}

bool ValidateShaderSpirv(const char* label, uint64_t shader_hash,
                         const std::vector<uint32_t>& spirv) {
	if (!Config::ShaderValidationEnabled()) {
		return true;
	}
	spvtools::SpirvTools tools(SPV_ENV_VULKAN_1_3);
	std::string          messages;
	tools.SetMessageConsumer([&messages](spv_message_level_t, const char*,
	                                     const spv_position_t& position, const char* message) {
		messages += fmt::format("{}: {} ({}) {}\n", static_cast<int>(position.line),
		                        static_cast<int>(position.column), static_cast<int>(position.index),
		                        message);
	});
	if (tools.Validate(spirv)) {
		return true;
	}
	spvtools::SpirvTools disassembler(SPV_ENV_VULKAN_1_2);
	std::string          text;
	disassembler.Disassemble(spirv, &text,
	                         static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_NO_HEADER) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_FRIENDLY_NAMES) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_COMMENT) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_INDENT) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_COLOR));
	LOGF_COLOR(Log::Color::BrightRed, "%s SPIR-V validation failed hash=0x%016" PRIx64 ":\n%s",
	           label, shader_hash, messages.c_str());
	LOGF("%s\n", text.c_str());
	return false;
}

} // namespace

struct PipelineCache::ProgramCache {
	ComputePretranslation pretranslation;
	struct ProgramKey {
		ShaderType            stage           = ShaderType::Unknown;
		uint64_t              hash            = 0;
		uint32_t              user_data_count = 0;
		uint32_t              code_size       = 0;
		std::vector<uint32_t> static_state;

		bool operator==(const ProgramKey&) const = default;
	};

	struct Permutation {
		ShaderRecompiler::IR::ResourceSpecialization specialization;
		ShaderRecompiler::IR::CompiledShaderInfo     program;
		ShaderProgram                                handle;
		std::vector<uint32_t>                        spirv; // kept for the translation cache file
	};

	struct SourceEntry {
		explicit SourceEntry(ShaderRecompiler::IR::ResourcePlan plan)
		    : resource_plan(std::move(plan)) {}

		ShaderRecompiler::IR::ResourcePlan resource_plan;
		// deque: draws and asynchronous pipeline jobs keep pointers to a permutation's program
		// while later permutations of the same source are appended.
		std::deque<Permutation>            permutations;
		bool                               from_cache = false;
	};

	struct ProgramKeyHash {
		std::size_t operator()(const ProgramKey& key) const {
			std::size_t hash = static_cast<std::size_t>(key.stage);
			PipelineKeyHash::Mix(hash, static_cast<std::size_t>(key.hash));
			if constexpr (sizeof(std::size_t) < sizeof(uint64_t)) {
				PipelineKeyHash::Mix(hash, static_cast<std::size_t>(key.hash >> 32u));
			}
			PipelineKeyHash::Mix(hash, key.user_data_count);
			PipelineKeyHash::Mix(hash, key.code_size);
			PipelineKeyHash::Mix(hash, key.static_state.size());
			// Bucket same-shape static variants by source. ProgramKey equality performs the one
			// exact state comparison needed on a stable hit without hashing up to 429 words first.
			return hash;
		}
	};

	static constexpr std::size_t MaxStaticKeyWords = 13 + ShaderVertexInputInfo::RES_MAX * 13;

	Permutation CompilePermutation(const ShaderParams&                          params,
	                               const ShaderRecompiler::CompileOptions&      options,
	                               ShaderRecompiler::TranslateResult            translated,
	                               ShaderRecompiler::IR::ResourceSpecialization specialization,
	                               uint32_t push_data_start_dword) {
		const char* stage_name = nullptr;
		switch (options.stage) {
			case ShaderType::Vertex: stage_name = "vs"; break;
			case ShaderType::Mesh: stage_name = "ms"; break;
			case ShaderType::Pixel: stage_name = "ps"; break;
			case ShaderType::Compute: stage_name = "cs"; break;
			default: EXIT("invalid pipeline shader stage\n");
		}
		const auto emit_begin = HostMicros();
		auto result = ShaderRecompiler::CompileProgram(std::move(translated), options,
		                                               specialization, push_data_start_dword);
		const auto emit_end = HostMicros();
		DumpShaderOriginal(stage_name, options.shader_hash, params.code, result.decoded_dump);
		if (!ValidateShaderSpirv(options.dump_label, options.shader_hash, result.spirv)) {
			DumpShaderSpirv(stage_name, options.shader_hash, result.spirv);
			EXIT("%s failed hash=0x%016" PRIx64 ": SPIR-V validation failed\n", options.dump_label,
			     options.shader_hash);
		}
		DumpShaderSpirv(stage_name, options.shader_hash, result.spirv);
		// KYTY_PIPELINE_STATS_SPV=<hex hash>=<file.spv>[;...]: substitute a SPIR-V module (variant
		// measurement with KYTY_PIPELINE_STATS; needs KYTY_SHADER_CACHE=0).
		if (const char* subst = std::getenv("KYTY_PIPELINE_STATS_SPV"); subst != nullptr) {
			char hash_text[24];
			snprintf(hash_text, sizeof(hash_text), "%016" PRIx64 "=", options.shader_hash);
			if (const char* at = std::strstr(subst, hash_text); at != nullptr) {
				std::string path(at + std::strlen(hash_text));
				if (const auto semi = path.find(';'); semi != std::string::npos) {
					path.resize(semi);
				}
				if (FILE* file = fopen(path.c_str(), "rb"); file != nullptr) {
					std::vector<uint32_t> words;
					uint32_t              word = 0;
					while (fread(&word, sizeof(word), 1, file) == 1) {
						words.push_back(word);
					}
					fclose(file);
					LOGF("PipelineStats: substituting SPIR-V of %016" PRIx64 " with %s (%zu words)\n",
					     options.shader_hash, path.c_str(), words.size());
					result.spirv = std::move(words);
				}
			}
		}

		const auto module_begin = HostMicros();
		const auto module = CreateCachedModule(device, result.spirv);
		EXIT_IF(module == nullptr);
		if (AvTraceEnabled()) {
			LOGF("AvTrace: shader-emit %s hash=0x%016" PRIx64 " emit_us=%" PRIu64 " validate_us=%" PRIu64
			     " module_us=%" PRIu64 " words=%" PRIu64 "\n",
			     stage_name, options.shader_hash, emit_end - emit_begin, module_begin - emit_end,
			     HostMicros() - module_begin, static_cast<uint64_t>(result.spirv.size()));
		}
		if (options.dump_ir) {
			LOGF("%s SPIR-V words=%" PRIu64 " wave_size=%u\n", options.dump_label,
			     static_cast<uint64_t>(result.spirv.size()), options.wave_size);
		}
		return {
		    .specialization = std::move(specialization),
		    .program        = std::move(result.program).TakeCompiledInfo(),
		    .handle         = {.id = ++next_shader_id, .module = module},
		    .spirv          = translation_cache.Enabled() ? std::move(result.spirv)
		                                                  : std::vector<uint32_t> {},
		};
	}

	ShaderTranslationCache::Key CacheKey(const ProgramKey& key) const {
		return {.stage           = static_cast<uint32_t>(key.stage),
		        .hash            = key.hash,
		        .user_data_count = key.user_data_count,
		        .code_size       = key.code_size,
		        .static_state    = key.static_state};
	}

	// Disk cache miss path: a translated program (plan + SPIR-V permutations) written earlier.
	bool LoadFromTranslationCache(const ProgramKey& key,
	                              std::unordered_map<ProgramKey, SourceEntry, ProgramKeyHash>::iterator& entry) {
		if (!translation_cache.Enabled()) {
			return false;
		}
		ShaderTranslationCache::Entry cached;
		if (!translation_cache.Load(CacheKey(key), cached)) {
			return false;
		}
		SourceEntry source(std::move(cached.plan));
		for (auto& p: cached.permutations) {
			const auto module = CreateCachedModule(device, p.spirv);
			EXIT_IF(module == nullptr);
			source.permutations.push_back({
			    .specialization = std::move(p.specialization),
			    .program        = std::move(p.program),
			    .handle         = {.id = ++next_shader_id, .module = module},
			    .spirv          = std::move(p.spirv),
			});
		}
		source.from_cache = true;
		entry             = programs.try_emplace(key, std::move(source)).first;
		IndexPermutations(entry->first, entry->second);
		return true;
	}

	// KYTY_SHADER_CACHE_VERIFY=1: read the file back and check that the deserialized plan
	// materializes to the same snapshot and specialization as the live one.
	void VerifyTranslationCache(const ProgramKey& key, const ShaderRecompiler::IR::SrtRuntime& runtime,
	                            const ShaderRecompiler::IR::ResourceSnapshot&       resources,
	                            const ShaderRecompiler::IR::ResourceSpecialization& specialization) {
		static const bool verify = std::getenv("KYTY_SHADER_CACHE_VERIFY") != nullptr;
		if (!verify || !translation_cache.Enabled()) {
			return;
		}
		ShaderTranslationCache::Entry cached;
		if (!translation_cache.Load(CacheKey(key), cached)) {
			LOGF("ShaderCacheVerify: hash=0x%016" PRIx64 " reload failed\n", key.hash);
			return;
		}
		ShaderRecompiler::IR::ResourceSnapshot       resources2;
		ShaderRecompiler::IR::ResourceSpecialization specialization2;
		if (!ShaderRecompiler::IR::MaterializeResources(cached.plan, runtime, resources2,
		                                                specialization2)) {
			LOGF("ShaderCacheVerify: hash=0x%016" PRIx64 " materialization FAILED\n", key.hash);
			return;
		}
		const bool same = specialization2 == specialization && resources2.buffers == resources.buffers &&
		                  resources2.images == resources.images &&
		                  resources2.samplers == resources.samplers &&
		                  resources2.flattened_srt == resources.flattened_srt &&
		                  resources2.user_data == resources.user_data;
		LOGF("ShaderCacheVerify: hash=0x%016" PRIx64 " %s (values=%zu perms=%zu)\n", key.hash,
		     same ? "ok" : "MISMATCH", cached.plan.value_storage.size(), cached.permutations.size());
	}

	void SaveToTranslationCache(const ProgramKey& key, const SourceEntry& source) {
		if (!translation_cache.Enabled()) {
			return;
		}
		std::vector<ShaderTranslationCache::Permutation> permutations;
		permutations.reserve(source.permutations.size());
		for (const auto& p: source.permutations) {
			if (p.spirv.empty()) {
				continue;
			}
			permutations.push_back({.specialization = p.specialization,
			                        .program        = p.program,
			                        .spirv          = p.spirv});
		}
		if (permutations.empty()) {
			return;
		}
		const auto t0 = HostMicros();
		const bool ok = translation_cache.Save(CacheKey(key), source.resource_plan, permutations);
		if (AvTraceEnabled() || !ok) {
			LOGF("AvTrace: shader-cache save hash=0x%016" PRIx64 " permutations=%zu ok=%d us=%" PRIu64
			     "\n",
			     key.hash, permutations.size(), ok ? 1 : 0, HostMicros() - t0);
		}
	}

	// tolerant: the PM4 lookahead reads guest memory that may not be final yet; a resource plan
	// that does not materialize returns an empty program instead of stopping the emulator.
	template <typename InputInfo>
	ShaderProgram Get(const ShaderParams& params, InputInfo& input_info,
	                  uint32_t& push_data_cursor, bool tolerant = false) {
		ShaderType stage;
		if constexpr (std::is_same_v<InputInfo, ShaderVertexInputInfo>) {
			stage = input_info.mesh.threads_num[0] != 0 ? ShaderType::Mesh : ShaderType::Vertex;
		} else if constexpr (std::is_same_v<InputInfo, ShaderPixelInputInfo>) {
			stage = ShaderType::Pixel;
		} else {
			static_assert(std::is_same_v<InputInfo, ShaderComputeInputInfo>);
			stage = ShaderType::Compute;
		}

		Common::FrameStats::Lap lap;
		lookup_key.stage           = stage;
		lookup_key.hash            = params.hash;
		lookup_key.user_data_count = static_cast<uint32_t>(params.user_data.size());
		lookup_key.code_size       = static_cast<uint32_t>(params.code.size());
		BuildStageStaticKey(input_info, lookup_key.static_state);
		static const bool register_trace = std::getenv("KYTY_SHADER_REGISTER_TRACE") != nullptr;
		if (register_trace && first_used.emplace(static_cast<uint32_t>(stage), params.hash).second) {
			LOGF("ShaderFirstUse: hash=%016" PRIx64 " stage=%u words=%zu ud=%zu host_us=%" PRIu64 "\n",
			     params.hash, static_cast<uint32_t>(stage), params.code.size(), params.user_data.size(), HostMicros());
		}
		auto                                         entry = programs.find(lookup_key);
		if (entry == programs.end()) {
			LibKernel::KernelTimeFreezeScope load_freeze;
			const auto                       load_begin = HostMicros();
			if (LoadFromTranslationCache(lookup_key, entry) && AvTraceEnabled()) {
				LOGF("AvTrace: shader-cache load hash=0x%016" PRIx64 " permutations=%zu us=%" PRIu64
				     "\n",
				     params.hash, entry->second.permutations.size(), HostMicros() - load_begin);
			}
		}
		lap.Mark(Common::FrameStats::Counter::ProgKeyNs);
		ShaderRecompiler::IR::ResourceSnapshot       resources;
		ShaderRecompiler::IR::ResourceSpecialization specialization;
		ShaderReadCache                              read_cache;
		const ShaderRecompiler::IR::SrtRuntime       runtime {
		    .user_data                  = params.user_data,
		    .shader_base                = params.Base(),
		    .read_memory                = ReadShaderLiveMemory,
		    .userdata                   = &read_cache,
		    .read_specialization_memory = ReadShaderGuestMemory,
		};
		if (entry != programs.end() &&
		    !ShaderRecompiler::IR::MaterializeResources(entry->second.resource_plan, runtime,
		                                                resources, specialization)) {
			if (!entry->second.from_cache) {
				if (tolerant) {
					return {};
				}
				EXIT("shader resource materialization failed hash=0x%016" PRIx64 "\n", params.hash);
			}
			// A cached plan that does not materialize: drop it and translate the shader again.
			LOGF("Shader translation cache: dropping hash=0x%016" PRIx64 " (materialization failed)\n",
			     params.hash);
			// The modules are leaked on purpose: a precached pipeline job on a worker may still
			// be compiling with them (a few KB each, rare path).
			for (const auto& permutation: entry->second.permutations) {
				by_id.erase(permutation.handle.id);
			}
			programs.erase(entry);
			entry = programs.end();
			resources = {};
			specialization = {};
		}
		if (entry != programs.end()) {
			lap.Mark(Common::FrameStats::Counter::ProgMaterializeNs);
			if (const auto permutation = std::ranges::find_if(
			        entry->second.permutations, [&](const Permutation& candidate) {
				        const auto& layout = candidate.program.bindings;
				        return layout.push_data_start_dword ==
				                   ShaderRecompiler::IR::PushData::StartFor(
				                       push_data_cursor, layout.ShaderDataDwords()) &&
				               candidate.specialization == specialization;
			        });
			    permutation != entry->second.permutations.end()) {
				input_info.stage = {.program   = &permutation->program,
				                    .resources = std::move(resources)};
				permutation->program.bindings.AdvancePushData(push_data_cursor);
				lap.Mark(Common::FrameStats::Counter::ProgPermNs);
				return permutation->handle;
			}
		}

		// Recompiling a shader stalls the guest GPU for tens of milliseconds; keep guest time still.
		LibKernel::KernelTimeFreezeScope freeze_scope;
		ShaderStageInputInfo             stage_input {};
		if constexpr (std::is_same_v<InputInfo, ShaderVertexInputInfo>) {
			stage_input.vertex = &input_info;
		} else if constexpr (std::is_same_v<InputInfo, ShaderPixelInputInfo>) {
			stage_input.pixel = &input_info;
		} else {
			stage_input.compute = &input_info;
		}
		const char* label = nullptr;
		switch (stage) {
			case ShaderType::Vertex: label = "ShaderRecompiler VS"; break;
			case ShaderType::Mesh: label = "ShaderRecompiler MS"; break;
			case ShaderType::Pixel: label = "ShaderRecompiler PS"; break;
			case ShaderType::Compute: label = "ShaderRecompiler CS"; break;
			default: EXIT("invalid pipeline shader stage\n");
		}
		ShaderRecompiler::CompileOptions options;
		options.stage       = stage;
		options.shader_hash = params.hash;
		options.user_data   = params.user_data;
		options.back_code      = params.back_code;
		options.dump_ir     = Config::GetShaderLogDirection() != Config::LogDirection::Silent;
		options.early_dump  = options.dump_ir;
		options.dump_label  = label;
		options.input_info  = stage_input;

		if constexpr (std::is_same_v<InputInfo, ShaderVertexInputInfo>) {
			options.user_data_base = 8;
			if (stage == ShaderType::Mesh) {
				options.user_data_base = 0;
				options.wave_size      = input_info.mesh.wave_size;
			} else {
				options.detect_wave_size = true;
			}
		} else if constexpr (std::is_same_v<InputInfo, ShaderPixelInputInfo>) {
			options.detect_wave_size = true;
		} else if constexpr (std::is_same_v<InputInfo, ShaderComputeInputInfo>) {
			options.wave_size = input_info.wave_size;
		}
		DumpShaderGcn(options.stage, options.shader_hash, params.code);
		const auto translate_begin = HostMicros();
		std::optional<ShaderRecompiler::TranslateResult> prepared;
		if constexpr (std::is_same_v<InputInfo, ShaderComputeInputInfo>) {
			if (ComputePretranslation::Enabled() && !Config::GraphicsDebugDumpEnabled()) {
				prepared = pretranslation.Take(params.code, params.hash, input_info,
				                              static_cast<uint32_t>(params.user_data.size()));
			}
		}
		auto translated = prepared ? std::move(*prepared) :
		                             ShaderRecompiler::TranslateProgram(params.code, options);
		const auto translate_end   = HostMicros();
		if (entry == programs.end()) {
			auto resource_plan = ShaderRecompiler::IR::ExtractResourcePlan(translated.program);
			if (!ShaderRecompiler::IR::MaterializeResources(resource_plan, runtime, resources,
			                                                specialization)) {
				if (tolerant) {
					return {};
				}
				EXIT("shader resource materialization failed hash=0x%016" PRIx64 "\n", params.hash);
			}
			entry = programs.try_emplace(lookup_key, std::move(resource_plan)).first;
		}
		entry->second.permutations.push_back(CompilePermutation(
		    params, options, std::move(translated), std::move(specialization), push_data_cursor));
		by_id[entry->second.permutations.back().handle.id] = {
		    &entry->first, static_cast<uint32_t>(entry->second.permutations.size() - 1)};
		SaveToTranslationCache(entry->first, entry->second);
		const auto& permutation = entry->second.permutations.back();
		if (AvTraceEnabled()) {
			std::string spec;
			for (const auto& b: permutation.specialization.buffers) {
				spec += fmt::format(" b:{:x}/{}/{:x}", b.packed_stride, static_cast<int>(b.descriptor_format),
				                    b.descriptor_swizzle);
			}
			for (const auto& i: permutation.specialization.images) {
				spec += fmt::format(" i:{}/{}/{}/{}/{:x}/{}", static_cast<int>(i.numeric_class),
				                    static_cast<int>(i.dimension), i.mip_count,
				                    static_cast<int>(i.conversion_format), i.shader_swizzle,
				                    i.indirect_root);
			}
			LOGF("AvTrace: shader-spec %s hash=0x%016" PRIx64 " perm=%zu%s\n", label, params.hash,
			     entry->second.permutations.size(), spec.c_str());
		}
		VerifyTranslationCache(entry->first, runtime, resources, permutation.specialization);
		input_info.stage = {.program = &permutation.program, .resources = std::move(resources)};
		permutation.program.bindings.AdvancePushData(push_data_cursor);

		if (AvTraceEnabled()) {
			LOGF("AvTrace: shader %s hash=0x%016" PRIx64 " translate_us=%" PRIu64 " compile_us=%" PRIu64
			     " permutations=%" PRIu64 "\n",
			     label, params.hash, translate_end - translate_begin, HostMicros() - translate_end,
			     static_cast<uint64_t>(entry->second.permutations.size()));
		}

		std::array<size_t, static_cast<size_t>(ShaderType::Mesh) + 1> counts {};
		for (const auto& [key, source]: programs) {
			counts[static_cast<size_t>(key.stage)] += source.permutations.size();
		}
		// Guest geometry shaders are compiled through the host mesh stage.
		std::printf("Shaders: VS %zu | PS %zu | CS %zu | GS %zu\n",
		            counts[static_cast<size_t>(ShaderType::Vertex)],
		            counts[static_cast<size_t>(ShaderType::Pixel)],
		            counts[static_cast<size_t>(ShaderType::Compute)],
		            counts[static_cast<size_t>(ShaderType::Mesh)]);
		return permutation.handle;
	}

	explicit ProgramCache(vk::Device device)
	    : device(device), translation_cache(PipelineCacheTitleId()) {
		lookup_key.static_state.reserve(MaxStaticKeyWords);
	}
	~ProgramCache() {
		pretranslation.Stop();
		for (const auto& [key, entry]: programs) {
			(void)key;
			for (const auto& permutation: entry.permutations) {
				device.destroyShaderModule(permutation.handle.module, nullptr);
			}
		}
	}

	// Pipeline precache: a permutation handle id -> (source key, index in the permutation list;
	// the list order is the translation-cache file order, so the index is stable across runs).
	struct PermutationRef {
		const ProgramKey* key   = nullptr;
		uint32_t          index = 0;
	};
	std::unordered_map<uint64_t, PermutationRef> by_id;

	void IndexPermutations(const ProgramKey& key, const SourceEntry& source) {
		uint32_t index = 0;
		for (const auto& permutation: source.permutations) {
			by_id[permutation.handle.id] = {&key, index++};
		}
	}

	bool Lookup(uint64_t id, ShaderTranslationCache::StoredKey& key, uint32_t& index) const {
		const auto it = by_id.find(id);
		if (it == by_id.end()) {
			return false;
		}
		key.stage           = static_cast<uint32_t>(it->second.key->stage);
		key.hash            = it->second.key->hash;
		key.user_data_count = it->second.key->user_data_count;
		key.code_size       = it->second.key->code_size;
		key.static_state    = it->second.key->static_state;
		index               = it->second.index;
		return true;
	}

	static ProgramKey ProgramKeyOf(const ShaderTranslationCache::StoredKey& key) {
		return {.stage           = static_cast<ShaderType>(key.stage),
		        .hash            = key.hash,
		        .user_data_count = key.user_data_count,
		        .code_size       = key.code_size,
		        .static_state    = key.static_state};
	}

	// Precache, outside the cache lock: reads the translation-cache file of a stored key.
	bool LoadEntry(const ShaderTranslationCache::StoredKey& key,
	               ShaderTranslationCache::Entry&           entry) {
		if (!translation_cache.Enabled()) {
			return false;
		}
		const ShaderTranslationCache::Key lookup {.stage           = key.stage,
		                                          .hash            = key.hash,
		                                          .user_data_count = key.user_data_count,
		                                          .code_size       = key.code_size,
		                                          .static_state    = key.static_state};
		return translation_cache.Load(lookup, entry);
	}

	// Precache, under the cache lock: the permutation of a stored key (the source is inserted
	// from `loaded` when the run has not touched it yet; `loaded` may be empty when the source
	// is already present).
	bool Resolve(const ShaderTranslationCache::StoredKey& key, uint32_t index,
	             ShaderTranslationCache::Entry* loaded, ShaderProgram& handle,
	             const ShaderRecompiler::IR::CompiledShaderInfo*& program) {
		auto entry = programs.find(ProgramKeyOf(key));
		if (entry == programs.end()) {
			if (loaded == nullptr || loaded->permutations.empty()) {
				return false;
			}
			SourceEntry source(std::move(loaded->plan));
			for (auto& p: loaded->permutations) {
				const auto module = CreateCachedModule(device, p.spirv);
				EXIT_IF(module == nullptr);
				source.permutations.push_back({
				    .specialization = std::move(p.specialization),
				    .program        = std::move(p.program),
				    .handle         = {.id = ++next_shader_id, .module = module},
				    .spirv          = std::move(p.spirv),
				});
			}
			source.from_cache = true;
			entry             = programs.try_emplace(ProgramKeyOf(key), std::move(source)).first;
			IndexPermutations(entry->first, entry->second);
		}
		if (index >= entry->second.permutations.size()) {
			return false;
		}
		const auto& permutation = entry->second.permutations[index];
		handle                  = permutation.handle;
		program                 = &permutation.program;
		return true;
	}

	std::unordered_map<ProgramKey, SourceEntry, ProgramKeyHash> programs;
	std::set<std::pair<uint32_t, uint64_t>>                     first_used;
	ProgramKey                                                  lookup_key;
	vk::Device                                                  device;
	ShaderTranslationCache                                      translation_cache;
	uint64_t                                                    next_shader_id = 0;
};

PipelineCache::PipelineCache(GraphicContext& graphics)
    : m_graphics(graphics), m_program_cache(std::make_unique<ProgramCache>(graphics.device)) {
	EXIT_NOT_IMPLEMENTED(!Common::Thread::IsMainThread());
	InitializeDriverCache();
	if (AsyncPipelinesMode() != 0) {
		StartWorkers();
		StartPrecache();
	}
}

PipelineCache::~PipelineCache() {
	m_precache_stop.store(true);
	if (m_precache_thread.joinable()) {
		m_precache_thread.join();
	}
	StopWorkers();
	Save();
	auto destroy = [this](const auto& pipelines) {
		for (const auto& [key, pipeline]: pipelines) {
			(void)key;
			m_graphics.device.destroyPipeline(pipeline->pipeline, nullptr);
			m_graphics.device.destroyPipelineLayout(pipeline->pipeline_layout, nullptr);
			m_graphics.device.destroyDescriptorSetLayout(pipeline->descriptor_set_layout, nullptr);
		}
	};
	destroy(m_graphics_pipelines);
	destroy(m_compute_pipelines);
	if (m_driver_cache != nullptr) {
		m_graphics.device.destroyPipelineCache(m_driver_cache, nullptr);
	}
}

void PipelineCache::InitializeDriverCache() {
	const auto title_id = PipelineCacheTitleId();
	if (title_id.empty()) {
		return;
	}
	if (const char* env = std::getenv("KYTY_PIPELINE_CACHE"); env != nullptr && std::atoi(env) == 0) {
		PipelineCacheLog("Vulkan pipeline cache: disabled (KYTY_PIPELINE_CACHE=0)");
		return;
	}

	m_driver_cache_path     = std::filesystem::path("_PipelineCache") / (title_id + ".bin");
	if (const char* salt = std::getenv("KYTY_PIPELINE_SALT"); salt != nullptr && salt[0] != 0) {
		m_driver_cache_path = std::filesystem::path("_PipelineCache") /
		    fmt::format("{}.{:016x}.bin", title_id, XXH3_64bits(salt, std::strlen(salt)));
		PipelineCacheLog("Pipeline cold-test namespace: {}", salt);
	}

	const auto path         = Common::PathToString(m_driver_cache_path);
	const bool cache_exists = Common::File::IsFileExisting(m_driver_cache_path);
	if (cache_exists) {
		PipelineCacheLog("Vulkan pipeline cache: loading {}", path);
	} else {
		PipelineCacheLog("Vulkan pipeline cache: initializing {}", path);
	}
	std::vector<uint8_t> initial_data;
	if (cache_exists) {
		Common::File file(m_driver_cache_path, Common::File::Mode::Read);
		const auto   file_size = file.IsInvalid() ? 0 : file.Size();
		const auto   signature = DriverCacheSignature(m_graphics.GetPhysicalDeviceProperties());
		if (file_size >= signature.size() + sizeof(uint64_t) &&
		    file_size <= std::numeric_limits<uint32_t>::max()) {
			std::string cached_signature(signature.size(), '\0');
			uint64_t    payload_hash = 0;
			initial_data.resize(file_size - signature.size() - sizeof(payload_hash));
			uint32_t signature_read = 0;
			uint32_t hash_read      = 0;
			uint32_t payload_read   = 0;
			file.Read(cached_signature.data(), static_cast<uint32_t>(cached_signature.size()),
			          &signature_read);
			file.Read(&payload_hash, sizeof(payload_hash), &hash_read);
			file.Read(initial_data.data(), static_cast<uint32_t>(initial_data.size()),
			          &payload_read);
			file.Close();
			if (signature_read != cached_signature.size() || hash_read != sizeof(payload_hash) ||
			    payload_read != initial_data.size() || cached_signature != signature ||
			    XXH3_64bits(initial_data.data(), initial_data.size()) != payload_hash) {
				initial_data.clear();
				PipelineCacheLog(
				    "Vulkan pipeline cache: invalidating {} (driver, emulator, or data mismatch)",
				    path);
			}
		} else {
			file.Close();
			PipelineCacheLog("Vulkan pipeline cache: invalidating {} (invalid file size)", path);
		}
	}

	vk::PipelineCacheCreateInfo create {};
	create.initialDataSize = initial_data.size();
	create.pInitialData    = initial_data.empty() ? nullptr : initial_data.data();
	auto result = m_graphics.device.createPipelineCache(&create, nullptr, &m_driver_cache);
	if (result != vk::Result::eSuccess && !initial_data.empty()) {
		PipelineCacheLog("Vulkan pipeline cache: driver rejected {} ({}); starting empty", path,
		                 vk::to_string(result));
		initial_data.clear();
		create.initialDataSize = 0;
		create.pInitialData    = nullptr;
		result = m_graphics.device.createPipelineCache(&create, nullptr, &m_driver_cache);
	}
	if (result != vk::Result::eSuccess) {
		PipelineCacheLog("Vulkan pipeline cache: disabled ({})", vk::to_string(result));
		m_driver_cache = nullptr;
		return;
	}
	if (!initial_data.empty()) {
		PipelineCacheLog("Vulkan pipeline cache: loaded {} bytes from {}", initial_data.size(),
		                 path);
	} else {
		PipelineCacheLog("Vulkan pipeline cache: initialized empty");
	}
	m_driver_cache_saved_us = HostMicros();
}

// Called with m_mutex held right after a new pipeline was created. The process is often ended
// without running destructors (the window is closed by the OS, a debugger, a timeout), so the
// blob is written every 20 s while it keeps growing instead of only from ~PipelineCache().
void PipelineCache::MaybeWriteDriverCache() {
	MaybeWriteRecipes();
	if (m_driver_cache == nullptr) {
		return;
	}
	m_driver_cache_unsaved++;
	const auto now = HostMicros();
	if (now - m_driver_cache_saved_us < 20000000u) {
		return;
	}
	if (WriteDriverCache()) {
		m_driver_cache_unsaved = 0;
	}
	m_driver_cache_saved_us = now;
}

void PipelineCache::StartWorkers() {
	const auto count = AsyncPipelineThreads();
	m_workers.reserve(count);
	for (uint32_t i = 0; i < count; i++) {
		m_workers.emplace_back([this] { WorkerLoop(); });
	}
	LOGF("AsyncPipelines: mode=%d workers=%u\n", AsyncPipelinesMode(), count);
}

void PipelineCache::StopWorkers() {
	{
		std::lock_guard<std::mutex> lock(m_job_mutex);
		m_stop_workers = true;
	}
	m_job_cv.notify_all();
	for (auto& worker: m_workers) {
		if (worker.joinable()) {
			worker.join();
		}
	}
	m_workers.clear();
}

// Workers drain the queue before they exit, so every queued pipeline is created even when the
// cache is destroyed right after a scene cut.
void PipelineCache::WorkerLoop() {
#if defined(_WIN32)
	SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_BELOW_NORMAL);
#endif
	for (;;) {
		std::function<void()> job;
		{
			std::unique_lock<std::mutex> lock(m_job_mutex);
			m_job_cv.wait(lock, [this] { return m_stop_workers || !m_jobs.empty(); });
			if (m_jobs.empty()) {
				return;
			}
			job = std::move(m_jobs.front());
			m_jobs.pop_front();
			m_jobs_active++;
		}
		job();
		{
			std::lock_guard<std::mutex> lock(m_job_mutex);
			m_jobs_active--;
			if (m_jobs.empty() && m_jobs_active == 0) {
				m_idle_cv.notify_all();
			}
		}
	}
}

void PipelineCache::EnqueueJob(std::function<void()> job) {
	{
		std::lock_guard<std::mutex> lock(m_job_mutex);
		m_jobs.push_back(std::move(job));
	}
	m_job_cv.notify_one();
}

void PipelineCache::WaitForPendingPipelines() {
	std::unique_lock<std::mutex> lock(m_job_mutex);
	m_idle_cv.wait(lock, [this] { return m_jobs.empty() && m_jobs_active == 0; });
}

void PipelineCache::Save() {
	Common::LockGuard lock(m_mutex);
	if (m_recipes_unsaved != 0) {
		WriteRecipes();
	}
	if (m_driver_cache == nullptr) {
		return;
	}
	if (m_driver_cache_unsaved != 0 || m_driver_cache_saved_us == 0) {
		WriteDriverCache();
	}
	m_graphics.device.destroyPipelineCache(m_driver_cache, nullptr);
	m_driver_cache = nullptr;
}

bool PipelineCache::WriteDriverCache() {
	if (m_driver_cache == nullptr) {
		return false;
	}
	const auto           write_begin = HostMicros();
	size_t               size = 0;
	vk::Result           result;
	std::vector<uint8_t> payload;
	for (uint32_t attempt = 0; attempt < 3; attempt++) {
		size   = 0;
		result = m_graphics.device.getPipelineCacheData(m_driver_cache, &size, nullptr);
		if (result != vk::Result::eSuccess || size == 0 ||
		    size > std::numeric_limits<uint32_t>::max()) {
			break;
		}
		payload.resize(size);
		result = m_graphics.device.getPipelineCacheData(m_driver_cache, &size, payload.data());
		if (result != vk::Result::eIncomplete) {
			break;
		}
	}
	if (result != vk::Result::eSuccess || size == 0 ||
	    size > std::numeric_limits<uint32_t>::max()) {
		PipelineCacheLog("Vulkan pipeline cache: save failed ({}, {} bytes)",
		                 vk::to_string(result), size);
		return false;
	}
	payload.resize(size);
	auto       prefix       = DriverCacheSignature(m_graphics.GetPhysicalDeviceProperties());
	const auto payload_hash = XXH3_64bits(payload.data(), payload.size());
	prefix.append(reinterpret_cast<const char*>(&payload_hash), sizeof(payload_hash));
	if (!Common::File::CreateDirectories(m_driver_cache_path.parent_path())) {
		PipelineCacheLog("Vulkan pipeline cache: failed to create cache directory");
		return false;
	}
	auto temp_path = m_driver_cache_path;
	temp_path += ".tmp";
	Common::File file;
	uint32_t     prefix_written  = 0;
	uint32_t     payload_written = 0;
	if (file.Create(temp_path)) {
		file.Write(prefix.data(), static_cast<uint32_t>(prefix.size()), &prefix_written);
		file.Write(payload.data(), static_cast<uint32_t>(payload.size()), &payload_written);
	}
	const bool flushed = !file.IsInvalid() && file.Flush();
	file.Close();
	if (prefix_written != prefix.size() || payload_written != payload.size() || !flushed ||
	    !Common::File::RenameFile(temp_path, m_driver_cache_path)) {
		PipelineCacheLog("Vulkan pipeline cache: failed to write {}",
		                 Common::PathToString(m_driver_cache_path));
		return false;
	}
	PipelineCacheLog("Vulkan pipeline cache: saved {} bytes to {} ({} us)", payload.size(),
	                 Common::PathToString(m_driver_cache_path), HostMicros() - write_begin);
	return true;
}

PipelineCache::GraphicsPrograms PipelineCache::GetGraphicsPrograms(
    const HW::VertexShaderInfo& vertex_regs, const HW::PixelShaderInfo& pixel_regs,
    const HW::ShaderRegisters& sh, const HW::Context& context, const HW::UserConfig& user_config,
    std::span<const Prospero::ColorComponentMapping, 8> target_export_mapping, bool pixel_active,
    ShaderVertexInputInfo& vertex_info, ShaderPixelInputInfo& pixel_info) {
	Common::FrameStats::Lap lap;
	const auto vertex_params = PrepareProgram(vertex_regs, context, user_config, vertex_info);
	const bool mesh_active   = vertex_info.mesh.threads_num[0] != 0;
	if (mesh_active) {
		EXIT_NOT_IMPLEMENTED(!m_graphics.mesh_shader_enabled);
		auto& mesh              = vertex_info.mesh;
		mesh.host_subgroup_size = m_graphics.subgroup_size;
		const auto& limits      = m_graphics.mesh_shader_properties;
		const auto  logical_threads =
		    mesh.threads_num[0] * mesh.threads_num[1] * mesh.threads_num[2];
		const auto host_threads = ((logical_threads + mesh.wave_size - 1u) / mesh.wave_size) *
		                          std::min(mesh.host_subgroup_size, mesh.wave_size);
		if (host_threads > limits.maxMeshWorkGroupInvocations ||
		    host_threads > limits.maxMeshWorkGroupSize[0] ||
		    mesh.max_vertices > limits.maxMeshOutputVertices ||
		    mesh.max_primitives > limits.maxMeshOutputPrimitives ||
		    mesh.lds_size_dwords * sizeof(uint32_t) > limits.maxMeshSharedMemorySize) {
			EXIT("mesh shader exceeds host limits: threads=%u vertices=%u primitives=%u LDS=%u\n",
			     host_threads, mesh.max_vertices, mesh.max_primitives, mesh.lds_size_dwords);
		}
	}
	ShaderParams pixel_params;
	if (pixel_active) {
		pixel_params = PrepareProgram(pixel_regs, sh, target_export_mapping, pixel_info);
	}
	lap.Mark(Common::FrameStats::Counter::ProgPrepareNs);
	if (context.GetClipControl().clip_disable) {
		const auto& viewport = context.GetScreenViewport().viewports[0];
		const auto& limits   = m_graphics.GetPhysicalDeviceProperties().limits;
		auto&       clip     = vertex_info.clip_space;
		clip.scale[0]        = viewport.xscale;
		clip.scale[1]        = viewport.yscale;
		clip.offset[0]       = viewport.xoffset;
		clip.offset[1]       = viewport.yoffset;
		clip.half_extent[0] =
		    static_cast<float>(std::min(limits.maxViewportDimensions[0], 16384u)) * 0.5f;
		clip.half_extent[1] =
		    static_cast<float>(std::min(limits.maxViewportDimensions[1], 16384u)) * 0.5f;
		clip.enabled = true;
	}
	Common::LockGuard lock(m_mutex);
	uint32_t          push_data_cursor =
	    mesh_active ? ShaderRecompiler::IR::PushData::MeshDrawDwordCount : 0;
	GraphicsPrograms  result;
	if (pixel_active) {
		result.pixel = m_program_cache->Get(pixel_params, pixel_info, push_data_cursor);
	}
	result.vertex = m_program_cache->Get(vertex_params, vertex_info, push_data_cursor);
	return result;
}

ShaderProgram PipelineCache::GetComputeProgram(const HW::ComputeShaderInfo& regs,
                                               const HW::ShaderRegisters&   sh,
                                               ShaderComputeInputInfo&      input_info) {
	input_info.host_subgroup_size = m_graphics.SupportsComputeWave64() ? 64u : 32u;
	Common::FrameStats::Lap lap;
	const auto        params      = PrepareProgram(regs, sh, input_info);
	lap.Mark(Common::FrameStats::Counter::ProgPrepareNs);
	Common::LockGuard lock(m_mutex);
	uint32_t          push_data_cursor = 0;
	return m_program_cache->Get(params, input_info, push_data_cursor);
}

bool PipelineStaticParameters::operator==(const PipelineStaticParameters& other) const noexcept {
	return std::memcmp(this, &other, sizeof(*this)) == 0;
}

PipelineCache::Pipeline* PipelineCache::GetGraphicsPipeline(
    std::span<const RenderColorInfo> colors, const RenderDepthInfo& depth,
    const ShaderVertexInputInfo& vs_input_info, CommandBuffer& command,
    const ShaderPixelInputInfo* ps_input_info, vk::PrimitiveTopology topology,
    bool primitive_restart_enable, const ShaderProgram& vertex_program,
    const ShaderProgram& pixel_program, bool allow_wait) {
	bool                   queued = false;
	GraphicsPipelineEntry* entry  = nullptr;
	{
		Common::LockGuard lock(m_mutex);
		entry = CreateGraphicsPipelineLocked(colors, depth, vs_input_info, command, ps_input_info,
		                                     topology, primitive_restart_enable, vertex_program,
		                                     pixel_program, queued);
	}
	if (entry->ready.load(std::memory_order_acquire)) {
		return entry;
	}
	(void)queued; // precached entries are waited for too (bounded: one wait per frame after a skip)
	if (allow_wait && AsyncPipelineWaitUs() != 0) {
		std::unique_lock<std::mutex> lock(m_job_mutex);
		m_ready_cv.wait_for(lock, std::chrono::microseconds(AsyncPipelineWaitUs()),
		                    [entry] { return entry->ready.load(std::memory_order_acquire); });
	}
	return entry->ready.load(std::memory_order_acquire) ? entry : nullptr;
}

PipelineCache::GraphicsPipelineEntry* PipelineCache::CreateGraphicsPipelineLocked(
    std::span<const RenderColorInfo> colors, const RenderDepthInfo& depth,
    const ShaderVertexInputInfo& vs_input_info, CommandBuffer& command,
    const ShaderPixelInputInfo* ps_input_info, vk::PrimitiveTopology topology,
    bool primitive_restart_enable, const ShaderProgram& vertex_program,
    const ShaderProgram& pixel_program, bool& queued) {
	KYTY_PROFILER_BLOCK("PipelineCache::CreatePipeline(Gfx)", profiler::colors::DeepOrangeA200);
	queued = false;

	EXIT_IF(colors.size() > RENDER_COLOR_ATTACHMENTS_MAX);
	EXIT_IF(!vertex_program);
	const bool ps_active = ps_input_info != nullptr;
	EXIT_IF(ps_active && !pixel_program);
	const auto color_count = static_cast<uint32_t>(colors.size());

	auto& ctx = command.GetRegisters();

	const HW::ModeControl& mc = ctx.GetModeControl();

	const auto vs_id = vertex_program.id;
	const auto ps_id = ps_active ? pixel_program.id : 0;

	GraphicsPipelineKey key {};
	key.vs_shader_id            = vs_id;
	key.ps_shader_id            = ps_id;
	auto& static_params         = key.static_params;
	auto& rendering             = key.rendering;
	uint32_t attachment_samples = 0;
	for (uint32_t i = 0; i < color_count; i++) {
		EXIT_IF(!colors[i].image_id || colors[i].desc.view_info.format == vk::Format::eUndefined);
		const auto slot = colors[i].target_slot;
		EXIT_IF(slot >= RENDER_COLOR_ATTACHMENTS_MAX);
		rendering.color_count = std::max(rendering.color_count, slot + 1);
		static_params.color_mask[slot] = colors[i].export_mapping.ApplyMask(
		    render_target_mask_slot(ctx.GetRenderTargetMask(), slot));
		rendering.color_formats[slot] = colors[i].desc.view_info.format;
		if (attachment_samples == 0) {
			attachment_samples = colors[i].desc.info.samples;
		} else if (attachment_samples != colors[i].desc.info.samples) {
			EXIT("mixed color attachment sample counts are unsupported: %u and %u\n",
			     attachment_samples, colors[i].desc.info.samples);
		}
		// Blend state is indexed by the target slot, not by the dense loop index: a draw with
		// sparse MRT slots (sand decals) otherwise gets another slot's blend factors.
		const auto& rt                           = ctx.GetRenderTarget(slot);
		const auto& bc                           = ctx.GetBlendControl(slot);
		static_params.color_srcblend[slot]       = bc.color_srcblend;
		static_params.color_comb_fcn[slot]       = bc.color_comb_fcn;
		static_params.color_destblend[slot]      = bc.color_destblend;
		static_params.alpha_srcblend[slot]       = bc.alpha_srcblend;
		static_params.alpha_comb_fcn[slot]       = bc.alpha_comb_fcn;
		static_params.alpha_destblend[slot]      = bc.alpha_destblend;
		static_params.separate_alpha_blend[slot] = bc.separate_alpha_blend;
		static_params.blend_enable[slot]         = bc.enable && !rt.info.blend_bypass;
	}
	const bool with_depth =
	    depth.desc.view_info.format != vk::Format::eUndefined && static_cast<bool>(depth.image_id);
	if (with_depth) {
		const auto aspects       = ImageViewOps::DepthAspectMask(depth.desc.view_info.format);
		rendering.depth_format   = aspects & vk::ImageAspectFlagBits::eDepth
		                               ? depth.desc.view_info.format
		                               : vk::Format::eUndefined;
		rendering.stencil_format = aspects & vk::ImageAspectFlagBits::eStencil
		                               ? depth.desc.view_info.format
		                               : vk::Format::eUndefined;
		if (attachment_samples == 0) {
			attachment_samples = depth.desc.info.samples;
		} else if (attachment_samples != depth.desc.info.samples) {
			EXIT("mixed color/depth sample counts are unsupported: %u and %u\n", attachment_samples,
			     depth.desc.info.samples);
		}
	}
	if (color_count == 0 && !with_depth) {
		attachment_samples = render_sample_count(ctx.GetAaConfig().msaa_num_samples);
		EXIT_IF(!static_cast<bool>(
		    m_graphics.GetPhysicalDeviceProperties().limits.framebufferNoAttachmentsSampleCounts &
		    vulkan_sample_count(attachment_samples)));
	}
	EXIT_IF(attachment_samples == 0 ||
	        vulkan_sample_count(attachment_samples) == vk::SampleCountFlagBits {});

	if (ps_active && depth.depth_test_enable && ps_input_info->ps_execute_on_noop) {
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 16) {
			LOGF("Pipeline: temporary: accepting EXEC_ON_NOOP with depth test enabled\n");
		}
	}

	const auto& clip_control               = ctx.GetClipControl();
	static_params.negative_one_to_one      = !clip_control.dx_clip_space;
	static_params.depth_clip_enable        = clip_control.IsZClipEnabled();
	static_params.topology                 = topology;
	static_params.primitive_restart_enable = primitive_restart_enable;
	static_params.samples                  = attachment_samples;
	static_params.sample_shading_enable =
	    ps_active && attachment_samples > 1 && ps_input_info->ps_sample_shading;
	if (static_params.sample_shading_enable && !m_graphics.sample_rate_shading_enabled) {
		EXIT("Pipeline: sample-rate shading is required but unsupported by the host\n");
	}
	static_params.depth_bounds_test_enable = depth.depth_bounds_test_enable;
	static_params.depth_min_bounds         = depth.depth_min_bounds;
	static_params.depth_max_bounds         = depth.depth_max_bounds;
	static_params.stencil_test_enable      = depth.stencil_test_enable;
	static_params.stencil_front            = depth.stencil_static_front;
	static_params.stencil_back             = depth.stencil_static_back;
	const bool rect_list     = topology == vk::PrimitiveTopology::ePatchList;
	static_params.cull_back  = !rect_list && mc.cull_back;
	static_params.cull_front = !rect_list && mc.cull_front;
	static_params.face       = mc.face;
	static_params.provoking_vtx_last = mc.provoking_vtx_last;
	static_params.polygon_mode =
	    ResolvePolygonMode(mc, static_params.cull_front, static_params.cull_back);

	if (vs_input_info.stage.program->stage != ShaderType::Mesh) {
		EXIT_IF(vs_input_info.buffers_num < 0 ||
		        vs_input_info.buffers_num > ShaderVertexInputInfo::RES_MAX ||
		        vs_input_info.resources_num < 0 ||
		        vs_input_info.resources_num > ShaderVertexInputInfo::RES_MAX);
		key.vertex_input.binding_count   = static_cast<uint8_t>(vs_input_info.buffers_num);
		key.vertex_input.attribute_count = static_cast<uint8_t>(vs_input_info.resources_num);
		uint32_t attributes_num          = 0;
		for (int binding = 0; binding < vs_input_info.buffers_num; binding++) {
			const auto& buffer = vs_input_info.buffers[binding];
			EXIT_IF(buffer.attr_num < 0 || buffer.attr_num > ShaderVertexInputBuffer::ATTR_MAX);
			attributes_num += static_cast<uint32_t>(buffer.attr_num);
			EXIT_IF(attributes_num > static_cast<uint32_t>(vs_input_info.resources_num));
			key.vertex_input.bindings[binding] = {.stride   = buffer.stride,
			                                      .instance = buffer.fetch_index != 0};
			for (int attribute = 0; attribute < buffer.attr_num; attribute++) {
				const auto index = buffer.attr_indices[attribute];
				EXIT_IF(index < 0 || index >= vs_input_info.resources_num);
				key.vertex_input.attributes[index] = {
				    .offset  = buffer.attr_offsets[attribute],
				    .binding = static_cast<uint8_t>(binding),
				};
			}
		}
		EXIT_IF(attributes_num != static_cast<uint32_t>(vs_input_info.resources_num));
	}

	if (auto iter = m_graphics_pipelines.find(key); iter != m_graphics_pipelines.end()) {
		return iter->second.get(); // may still be compiling on a worker
	}
	RecordGraphicsRecipe(key, vs_input_info, ps_input_info);

	const auto pair_key = ShaderPairKey(vs_id, ps_id);
	if (AsyncPipelinesMode() != 0 && !m_ready_shader_pairs.contains(pair_key)) {
		// Everything CreatePipelineInternal reads is copied into the job: the register context and
		// the input infos belong to the current draw, only the shader modules and the compiled
		// program infos (owned by the program cache for the process lifetime) are shared.
		struct Job {
			PipelineRenderingState   rendering;
			PipelineVertexInputState vertex_input;
			ShaderVertexInputInfo    vs_input_info;
			ShaderProgram            vertex_program;
			bool                     ps_active = false;
			ShaderPixelInputInfo     ps_input_info;
			ShaderProgram            pixel_program;
			PipelineStaticParameters static_params;
		};
		auto job            = std::make_shared<Job>();
		job->rendering      = rendering;
		job->vertex_input   = key.vertex_input;
		job->vs_input_info  = vs_input_info;
		job->vertex_program = vertex_program;
		job->ps_active      = ps_active;
		if (ps_active) {
			job->ps_input_info = *ps_input_info;
		}
		job->pixel_program = pixel_program;
		job->static_params = static_params;

		auto  entry  = std::make_unique<GraphicsPipelineEntry>();
		auto* target = entry.get();
		auto [iter, inserted] = m_graphics_pipelines.emplace(std::move(key), std::move(entry));
		EXIT_IF(!inserted);
		m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);
		const auto queued_at = HostMicros();
		EnqueueJob([this, job, target, vs_id, ps_id, pair_key, queued_at] {
			const auto create_begin = HostMicros();
			CreatePipelineInternal(m_graphics, *target, job->rendering, job->vertex_input,
			                       job->vs_input_info, job->vertex_program,
			                       job->ps_active ? &job->ps_input_info : nullptr,
			                       job->pixel_program, job->static_params, m_driver_cache);
			EXIT_NOT_IMPLEMENTED(target->pipeline == nullptr);
			EXIT_NOT_IMPLEMENTED(target->pipeline_layout == nullptr);
			const auto create_end = HostMicros();
			{
				Common::LockGuard lock(m_mutex);
				if (AvTraceEnabled()) {
					LOGF("AvTrace: pipeline gfx vs=%" PRIu64 " ps=%" PRIu64 " us=%" PRIu64
					     " total=%" PRIu64 " async wait_us=%" PRIu64 " pending=%u\n",
					     vs_id, ps_id, create_end - create_begin,
					     static_cast<uint64_t>(m_graphics_pipelines.size()), create_begin - queued_at,
					     m_pending_pipelines.load(std::memory_order_relaxed) - 1u);
				}
				MaybeWriteDriverCache();
				m_ready_shader_pairs.insert(pair_key);
			}
			{
				std::lock_guard<std::mutex> lock(m_job_mutex);
				target->ready.store(true, std::memory_order_release);
			}
			m_ready_cv.notify_all();
			m_pending_pipelines.fetch_sub(1, std::memory_order_relaxed);
		});
		queued = true;
		return target;
	}

	LibKernel::KernelTimeFreezeScope freeze_scope;

	if (graphics_debug_dump_enabled()) {
		ShaderDbgDumpInputInfo(vs_input_info);
		if (ps_active) {
			ShaderDbgDumpInputInfo(*ps_input_info);
		}
		LOGF("PipelineTrace: shader modules VS=%" PRIu64 " module=%p PS=%" PRIu64 " module=%p\n",
		     vs_id, static_cast<void*>(vertex_program.module), ps_id,
		     static_cast<void*>(pixel_program.module));
	}

	auto cached = std::make_unique<GraphicsPipelineEntry>();
	LogPipelineTrace("CreatePipelineInternal begin", vs_id, ps_id);
	const auto create_begin = HostMicros();
	CreatePipelineInternal(m_graphics, *cached, rendering, key.vertex_input, vs_input_info,
	                       vertex_program, ps_input_info, pixel_program, static_params,
	                       m_driver_cache);
	if (AvTraceEnabled()) {
		LOGF("AvTrace: pipeline gfx vs=%" PRIu64 " ps=%" PRIu64 " us=%" PRIu64 " total=%" PRIu64 "\n",
		     vs_id, ps_id, HostMicros() - create_begin,
		     static_cast<uint64_t>(m_graphics_pipelines.size() + 1));
	}
	LogPipelineTrace("CreatePipelineInternal done", vs_id, ps_id);
	MaybeWriteDriverCache();

	EXIT_NOT_IMPLEMENTED(cached->pipeline == nullptr);
	EXIT_NOT_IMPLEMENTED(cached->pipeline_layout == nullptr);
	cached->ready.store(true, std::memory_order_release);
	m_ready_shader_pairs.insert(pair_key);

	auto [iter, inserted] = m_graphics_pipelines.emplace(std::move(key), std::move(cached));
	EXIT_IF(!inserted);

	return iter->second.get();
}

void PipelineCache::PrefetchComputePipeline(const HW::ComputeShaderInfo& regs,
                                            const HW::ShaderRegisters&   sh,
                                            ShaderComputeInputInfo       input_info) {
	if (m_workers.empty()) {
		return;
	}
	input_info.host_subgroup_size = m_graphics.SupportsComputeWave64() ? 64u : 32u;
	const auto params             = PrepareProgram(regs, sh, input_info);
	Common::LockGuard lock(m_mutex);
	uint32_t          push_data_cursor = 0;
	const auto        program = m_program_cache->Get(params, input_info, push_data_cursor, true);
	static std::atomic<uint32_t> log_count {0};
	const bool                   log = log_count.fetch_add(1, std::memory_order_relaxed) < 2048;
	if (!program) {
		if (log) {
			LOGF("AsyncCompute: prefetch hash=0x%016" PRIx64 " failed to materialize\n", params.hash);
		}
		return;
	}
	if (m_compute_pipelines.contains(program.id)) {
		return;
	}
	if (log) {
		LOGF("AsyncCompute: prefetch hash=0x%016" PRIx64 " id=%" PRIu64 " queued\n", params.hash, program.id);
	}
	RecordComputeRecipe(input_info, program.id);
	auto  entry  = std::make_unique<ComputePipelineEntry>();
	auto* target = entry.get();
	m_compute_pipelines.emplace(program.id, std::move(entry));
	m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);
	// The job owns a copy of the input info (stage.program points into the program cache, which
	// lives for the process; the resource snapshot is per dispatch and only copied along).
	auto       job       = std::make_shared<ShaderComputeInputInfo>(input_info);
	const auto module    = program.module;
	const auto id        = program.id;
	const auto hash      = input_info.stage.program->shader_hash;
	const auto queued_at = HostMicros();
	EnqueueJob([this, job, target, module, id, hash, queued_at] {
		const auto create_begin = HostMicros();
		CreatePipelineInternal(m_graphics, *target, *job, module, m_driver_cache);
		EXIT_NOT_IMPLEMENTED(target->pipeline == nullptr);
		EXIT_NOT_IMPLEMENTED(target->pipeline_layout == nullptr);
		const auto create_end = HostMicros();
		{
			Common::LockGuard lock(m_mutex);
			if (AvTraceEnabled()) {
				LOGF("AvTrace: pipeline cs cs=%" PRIu64 " us=%" PRIu64 " total=%" PRIu64
				     " async wait_us=%" PRIu64 " hash=0x%016" PRIx64 "\n",
				     id, create_end - create_begin, static_cast<uint64_t>(m_compute_pipelines.size()),
				     create_begin - queued_at, hash);
			}
			MaybeWriteDriverCache();
		}
		{
			std::lock_guard<std::mutex> lock(m_job_mutex);
			target->ready.store(true, std::memory_order_release);
		}
		m_ready_cv.notify_all();
		m_pending_pipelines.fetch_sub(1, std::memory_order_relaxed);
	});
}

PipelineCache::Pipeline&
PipelineCache::GetComputePipeline(const ShaderComputeInputInfo& input_info,
                                  const ShaderProgram&          compute_program) {
	KYTY_PROFILER_BLOCK("PipelineCache::CreatePipeline(Compute)", profiler::colors::RedA100);

	EXIT_IF(!compute_program);

	ComputePipelineEntry* pending = nullptr;
	{
		Common::LockGuard lock(m_mutex);

		if (auto iter = m_compute_pipelines.find(compute_program.id);
		    iter != m_compute_pipelines.end()) {
			if (iter->second->ready.load(std::memory_order_acquire)) {
				return *iter->second;
			}
			pending = iter->second.get(); // queued by the lookahead, still compiling
		} else {
			LibKernel::KernelTimeFreezeScope freeze_scope;

			if (graphics_debug_dump_enabled()) {
				ShaderDbgDumpInputInfo(input_info);
			}

			RecordComputeRecipe(input_info, compute_program.id);
			auto       cached       = std::make_unique<ComputePipelineEntry>();
			const auto create_begin = HostMicros();
			CreatePipelineInternal(m_graphics, *cached, input_info, compute_program.module,
			                       m_driver_cache);
			if (AvTraceEnabled()) {
				LOGF("AvTrace: pipeline cs cs=%" PRIu64 " us=%" PRIu64 " total=%" PRIu64
				     " sync hash=0x%016" PRIx64 "\n",
				     compute_program.id, HostMicros() - create_begin,
				     static_cast<uint64_t>(m_compute_pipelines.size() + 1),
				     input_info.stage.program->shader_hash);
			}
			MaybeWriteDriverCache();

			EXIT_NOT_IMPLEMENTED(cached->pipeline == nullptr);
			EXIT_NOT_IMPLEMENTED(cached->pipeline_layout == nullptr);
			cached->ready.store(true, std::memory_order_release);

			auto [place, inserted] =
			    m_compute_pipelines.emplace(compute_program.id, std::move(cached));
			EXIT_IF(!inserted);
			return *place->second;
		}
	}
	// A dispatch cannot be skipped: wait for the worker with the guest clock frozen.
	LibKernel::KernelTimeFreezeScope freeze_scope;
	const auto                       wait_begin = HostMicros();
	{
		std::unique_lock<std::mutex> lock(m_job_mutex);
		m_ready_cv.wait(lock, [pending] { return pending->ready.load(std::memory_order_acquire); });
	}
	if (AvTraceEnabled()) {
		LOGF("AvTrace: pipeline cs cs=%" PRIu64 " waited_us=%" PRIu64 " hash=0x%016" PRIx64 "\n",
		     compute_program.id, HostMicros() - wait_begin, input_info.stage.program->shader_hash);
	}
	return *pending;
}
// ---------------------------------------------------------------------------------------------
// Pipeline precache (session 25). Warm runs still created 190+ graphics pipelines and ~140
// compute pipelines in the process (0.2-10 ms each even from the driver cache), 20-33 of them
// on every scene cut, where the compiling workers also hold the driver lock that
// vkQueueSubmit / vkBindImageMemory / vkAllocateMemory on the GuestGpu thread need. A recipe
// is what CreatePipelineInternal reads: the translation-cache key and permutation index of each
// stage (the SPIR-V and the compiled info come from the translation cache), the POD pipeline
// state and the stage input infos without their runtime part.
namespace {

constexpr char RECIPES_MAGIC[] = "KytyPR1\n";

class RecipeWriter {
public:
	void U8(uint8_t v) { m_data.push_back(v); }
	void U32(uint32_t v) { Bytes(&v, sizeof(v)); }
	void U64(uint64_t v) { Bytes(&v, sizeof(v)); }
	void Bytes(const void* p, size_t n) {
		const auto* b = static_cast<const uint8_t*>(p);
		m_data.insert(m_data.end(), b, b + n);
	}
	template <typename T>
	void Pod(const T& v) {
		static_assert(std::is_trivially_copyable_v<T>);
		Bytes(&v, sizeof(T));
	}
	void Key(const ShaderTranslationCache::StoredKey& key) {
		U32(key.stage);
		U64(key.hash);
		U32(key.user_data_count);
		U32(key.code_size);
		U32(static_cast<uint32_t>(key.static_state.size()));
		Bytes(key.static_state.data(), key.static_state.size() * sizeof(uint32_t));
	}
	// A stage input info without its runtime part (program pointer + resource snapshot).
	template <typename T>
	void Info(const T& info) {
		const auto*  base  = reinterpret_cast<const uint8_t*>(&info);
		const auto*  stage = reinterpret_cast<const uint8_t*>(&info.stage);
		const size_t off   = static_cast<size_t>(stage - base);
		const size_t tail  = off + sizeof(ShaderStageRuntime);
		std::array<uint8_t, sizeof(T)> bytes {};
		std::memcpy(bytes.data(), base, off);
		std::memcpy(bytes.data() + tail, base + tail, sizeof(T) - tail);
		Bytes(bytes.data(), bytes.size());
	}
	[[nodiscard]] const std::vector<uint8_t>& Data() const { return m_data; }
	std::vector<uint8_t>&                     Data() { return m_data; }

private:
	std::vector<uint8_t> m_data;
};

class RecipeReader {
public:
	RecipeReader(const uint8_t* data, size_t size): m_data(data), m_size(size) {}
	[[nodiscard]] bool   Failed() const { return m_failed; }
	[[nodiscard]] size_t Pos() const { return m_pos; }
	[[nodiscard]] bool AtEnd() const { return m_pos == m_size; }
	uint8_t            U8() {
		uint8_t v = 0;
		Bytes(&v, 1);
		return v;
	}
	uint32_t U32() {
		uint32_t v = 0;
		Bytes(&v, sizeof(v));
		return v;
	}
	uint64_t U64() {
		uint64_t v = 0;
		Bytes(&v, sizeof(v));
		return v;
	}
	void Bytes(void* out, size_t n) {
		if (m_failed || n > m_size - m_pos) {
			m_failed = true;
			std::memset(out, 0, n);
			return;
		}
		std::memcpy(out, m_data + m_pos, n);
		m_pos += n;
	}
	template <typename T>
	void Pod(T& v) {
		static_assert(std::is_trivially_copyable_v<T>);
		Bytes(&v, sizeof(T));
	}
	void Key(ShaderTranslationCache::StoredKey& key) {
		key.stage           = U32();
		key.hash            = U64();
		key.user_data_count = U32();
		key.code_size       = U32();
		const auto n        = U32();
		if (m_failed || n > 4096u) {
			m_failed = true;
			return;
		}
		key.static_state.resize(n);
		Bytes(key.static_state.data(), n * sizeof(uint32_t));
	}
	template <typename T>
	void Info(T& info) {
		std::array<uint8_t, sizeof(T)> bytes {};
		Bytes(bytes.data(), bytes.size());
		if (m_failed) {
			return;
		}
		auto*        base  = reinterpret_cast<uint8_t*>(&info);
		const auto*  stage = reinterpret_cast<const uint8_t*>(&info.stage);
		const size_t off   = static_cast<size_t>(stage - base);
		const size_t tail  = off + sizeof(ShaderStageRuntime);
		std::memcpy(base, bytes.data(), off);
		std::memcpy(base + tail, bytes.data() + tail, sizeof(T) - tail);
	}

private:
	const uint8_t* m_data;
	size_t         m_size;
	size_t         m_pos    = 0;
	bool           m_failed = false;
};

// Layout guard: the records embed these structs byte for byte.
std::string RecipeLayoutSignature() {
	return fmt::format("{}:{}:{}:{}:{}:{}", sizeof(ShaderVertexInputInfo), sizeof(ShaderPixelInputInfo),
	                   sizeof(ShaderComputeInputInfo), sizeof(PipelineRenderingState),
	                   sizeof(PipelineVertexInputState), sizeof(PipelineStaticParameters));
}

bool PipelinePrecacheEnabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_PIPELINE_PRECACHE");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

} // namespace

void PipelineCache::RecordGraphicsRecipe(const GraphicsPipelineKey&   key,
                                         const ShaderVertexInputInfo& vs_input_info,
                                         const ShaderPixelInputInfo*  ps_input_info) {
	if (!PipelinePrecacheEnabled() || !m_program_cache->translation_cache.Enabled()) {
		return;
	}
	ShaderTranslationCache::StoredKey vs_key;
	ShaderTranslationCache::StoredKey ps_key;
	uint32_t                          vs_index = 0;
	uint32_t                          ps_index = 0;
	if (!m_program_cache->Lookup(key.vs_shader_id, vs_key, vs_index)) {
		return;
	}
	const bool ps_active = ps_input_info != nullptr;
	if (ps_active && !m_program_cache->Lookup(key.ps_shader_id, ps_key, ps_index)) {
		return;
	}
	RecipeWriter w;
	w.U8(1);
	w.Key(vs_key);
	w.U32(vs_index);
	w.U8(ps_active ? 1 : 0);
	if (ps_active) {
		w.Key(ps_key);
		w.U32(ps_index);
	}
	w.Pod(key.rendering);
	w.Pod(key.vertex_input);
	w.Pod(key.static_params);
	w.Info(vs_input_info);
	if (ps_active) {
		w.Info(*ps_input_info);
	}
	AppendRecipe(w.Data().data(), w.Data().size());
}

// Appends one serialized record unless an identical one is already known.
void PipelineCache::AppendRecipe(const uint8_t* record, size_t size) {
	if (!m_recipe_hashes.insert(XXH3_64bits(record, size)).second) {
		return;
	}
	m_recipes.insert(m_recipes.end(), record, record + size);
	m_recipe_sizes.push_back(static_cast<uint32_t>(size));
	m_recipe_count++;
	m_recipes_unsaved++;
}

void PipelineCache::RecordComputeRecipe(const ShaderComputeInputInfo& input_info,
                                        uint64_t                      program_id) {
	if (!PipelinePrecacheEnabled() || !m_program_cache->translation_cache.Enabled()) {
		return;
	}
	ShaderTranslationCache::StoredKey key;
	uint32_t                          index = 0;
	if (!m_program_cache->Lookup(program_id, key, index)) {
		return;
	}
	RecipeWriter w;
	w.U8(2);
	w.Key(key);
	w.U32(index);
	w.Info(input_info);
	AppendRecipe(w.Data().data(), w.Data().size());
}

void PipelineCache::MaybeWriteRecipes() {
	if (m_recipes_unsaved == 0 || m_recipes_path.empty()) {
		return;
	}
	const auto now = HostMicros();
	static uint64_t last_us = 0;
	if (now - last_us < 20000000u) {
		return;
	}
	last_us = now;
	WriteRecipes();
}

// Called with m_mutex held.
bool PipelineCache::WriteRecipes() {
	if (m_recipes_path.empty() || m_recipe_count == 0) {
		return false;
	}
	RecipeWriter w;
	w.Bytes(RECIPES_MAGIC, sizeof(RECIPES_MAGIC) - 1);
	const auto signature = m_program_cache->translation_cache.Signature() + RecipeLayoutSignature();
	w.U32(static_cast<uint32_t>(signature.size()));
	w.Bytes(signature.data(), signature.size());
	w.U32(m_recipe_count);
	w.Bytes(m_recipes.data(), m_recipes.size());
	const auto& payload = w.Data();
	if (!Common::File::CreateDirectories(m_recipes_path.parent_path())) {
		return false;
	}
	auto temp_path = m_recipes_path;
	temp_path += ".tmp";
	Common::File file;
	uint32_t     written = 0;
	if (file.Create(temp_path)) {
		file.Write(payload.data(), static_cast<uint32_t>(payload.size()), &written);
	}
	const bool flushed = !file.IsInvalid() && file.Flush();
	file.Close();
	if (written != payload.size() || !flushed ||
	    !Common::File::RenameFile(temp_path, m_recipes_path)) {
		LOGF("PipelinePrecache: failed to write %s\n", Common::PathToString(m_recipes_path).c_str());
		return false;
	}
	LOGF("PipelinePrecache: saved %u recipes (%zu bytes)\n", m_recipe_count, payload.size());
	m_recipes_unsaved = 0;
	return true;
}

void PipelineCache::TraceShaderRegistration(const Shader& header, const ShaderMappedData& mapped) {
	if (ComputePretranslation::Enabled() && mapped.type == Prospero::ShaderBinaryType::kCs &&
	    header.specials != nullptr && header.special_sizes_bytes >= sizeof(ShaderSpecialRegs) &&
	    header.sh_registers != nullptr && header.code != nullptr &&
	    mapped.code_size_bytes != 0 && mapped.code_size_bytes % 4 == 0 &&
	    mapped.code_size_bytes <= 128 * 1024 &&
	    !Config::GraphicsDebugDumpEnabled()) {
		HW::ComputeShaderInfo regs;
		uint32_t present = 0;
		for (uint32_t i = 0; i < header.num_sh_registers; ++i) {
			const auto& reg = header.sh_registers[i];
			// Decode only known static registers. Do not call ignore/log handlers on unknown
			// AGC entries, and never dereference user-data resource pointers here.
			switch (reg.offset) {
				case Pm4::COMPUTE_NUM_THREAD_X: present |= 1; break;
				case Pm4::COMPUTE_NUM_THREAD_Y: present |= 2; break;
				case Pm4::COMPUTE_NUM_THREAD_Z: present |= 4; break;
				case Pm4::COMPUTE_PGM_RSRC2: present |= 8; break;
				default: continue;
			}
			ApplyCsShRegister(regs.cs_regs, reg.offset, reg.value);
		}
		if (present == 15 && regs.cs_regs.user_sgpr <= 32 && regs.cs_regs.num_thread_x != 0 &&
		    regs.cs_regs.num_thread_y != 0 && regs.cs_regs.num_thread_z != 0) {
			const auto modifier = header.specials->dispatch_modifier;
			regs.cs_regs.wave_size = Pm4::ComputeWaveSize(modifier);
			ShaderComputeInputInfo info;
			info.host_subgroup_size = m_graphics.SupportsComputeWave64() ? 64u : 32u;
			info.dispatch_thread_dimensions = (modifier & (1u << 5u)) != 0;
			ShaderGetStaticInputInfoCS(regs, {}, mapped, info);
			ProgramCache::ProgramKey key;
			key.stage = ShaderType::Compute;
			key.hash = mapped.hash;
			key.code_size = mapped.code_size_bytes / 4;
			key.user_data_count = regs.cs_regs.user_sgpr;
			BuildStageStaticKey(info, key.static_state);
			bool known = false;
			// Startup precache already prepared these sources. Never wait for a runtime
			// translation holding m_mutex merely to avoid redundant speculative work.
			if (m_mutex.TryLock()) {
				known = m_program_cache->programs.contains(key);
				m_mutex.Unlock();
			}
			const auto* code = static_cast<const uint32_t*>(const_cast<const void*>(header.code));
			if (!known) { m_program_cache->pretranslation.Enqueue({code, mapped.code_size_bytes / 4}, mapped.hash,
			                                        info, regs.cs_regs.user_sgpr,
			    Config::GetShaderLogDirection() != Config::LogDirection::Silent); }
		}
	}
	static const bool trace = std::getenv("KYTY_SHADER_REGISTER_TRACE") != nullptr;
	if (!trace) {
		return;
	}
	std::string registers;
	for (uint32_t i = 0; i < header.num_sh_registers; ++i) {
		registers += fmt::format(" {:x}={:08x}", header.sh_registers[i].offset, header.sh_registers[i].value);
	}
	for (uint32_t i = 0; i < header.num_cx_registers; ++i) {
		registers += fmt::format(" cx{:x}={:08x}", header.cx_registers[i].offset, header.cx_registers[i].value);
	}
	LOGF("ShaderRegister: hash=%016" PRIx64 " type=%u size=%u scratch=%u code=%016" PRIx64
	     " header=%016" PRIx64 " host_us=%" PRIu64 "%s\n", mapped.hash, header.type,
	     mapped.code_size_bytes, mapped.scratch_size_dwords, reinterpret_cast<uint64_t>(header.code),
	     reinterpret_cast<uint64_t>(&header), HostMicros(), registers.c_str());
}

PipelineCache::PreparationStatus PipelineCache::GetPreparationStatus() const {
	const bool active = m_precache_active.load(std::memory_order_acquire);
	return {active, m_precache_total.load(), m_precache_completed.load(), m_precache_skipped.load()};
}

void PipelineCache::FinishPreparation() {
	if (m_precache_thread.joinable()) {
		m_precache_thread.join();
	}
	// Do not use Save(): it destroys the VkPipelineCache used by later guest draws.
	Common::LockGuard lock(m_mutex);
	if (m_precache_completed.load() > m_precache_skipped.load() && WriteDriverCache()) {
		m_driver_cache_unsaved = 0;
		m_driver_cache_saved_us = HostMicros();
	}
	const auto status = GetPreparationStatus();
	PipelineCacheLog("ShaderPreparation: ready completed={} total={} skipped={}",
	                 status.completed, status.total, status.skipped);
}

void PipelineCache::InstallShaderSeed() {
	const auto& cache = m_program_cache->translation_cache;
	const auto& properties = m_graphics.GetPhysicalDeviceProperties();
	std::string app_version;
	Loader::SystemContentParamSfoGetString("APP_VER", &app_version);
	// Seed SPIR-V is device-specialized. Until cross-device profiles are validated, only accept
	// the exact GPU model, translator options, game version and recipe ABI used to build it.
	auto signature = cache.Signature();
	std::replace(signature.begin(), signature.end(), '\n', ':');
	const auto compatibility = fmt::format("KytySeed1:{}:{}:{}:{}:{:08x}:{:08x}",
	    PipelineCacheTitleId(), app_version, signature, RecipeLayoutSignature(),
	    properties.vendorID, properties.deviceID);
	PipelineCacheLog("ShaderSeed: compatibility={}", compatibility);
	if (const char* value = std::getenv("KYTY_SHADER_SEED"); value != nullptr && value[0] == '0') {
		return;
	}
	const char* root = std::getenv("KYTY_SHADER_SEED_PATH");
	const auto seed = std::filesystem::path(root != nullptr ? root : "_ShaderSeeds") / PipelineCacheTitleId();
	std::ifstream manifest(seed / "compatibility.txt");
	std::string stored;
	if (!std::getline(manifest, stored)) return;
	if (!stored.empty() && stored.back() == '\r') stored.pop_back();
	if (stored != compatibility) {
		PipelineCacheLog("ShaderSeed: incompatible game, GPU or translator; ignored");
		return;
	}
	const auto recipes_match = [&](const std::filesystem::path& path) {
		std::ifstream file(path, std::ios::binary);
		char magic[sizeof(RECIPES_MAGIC) - 1] {};
		uint32_t size = 0;
		file.read(magic, sizeof(magic));
		file.read(reinterpret_cast<char*>(&size), sizeof(size));
		const auto expected = cache.Signature() + RecipeLayoutSignature();
		if (!file || std::memcmp(magic, RECIPES_MAGIC, sizeof(magic)) != 0 || size != expected.size()) return false;
		std::string actual(size, '\0');
		file.read(actual.data(), size);
		return bool(file) && actual == expected;
	};
	if (recipes_match(cache.Directory() / "pipelines.bin")) return;
	if (!recipes_match(seed / "pipelines.bin")) {
		PipelineCacheLog("ShaderSeed: invalid recipes; ignored");
		return;
	}
	// Verify every shader before installing any. Publish recipes last, so an interrupted copy
	// is retried next time. Files and recipes are a single set (permutation indices must match).
	std::error_code ec;
	std::vector<std::filesystem::path> shaders;
	for (std::filesystem::directory_iterator it(seed, ec), end; !ec && it != end; it.increment(ec)) {
		const auto path = it->path();
		if (path.extension() != ".bin" || path.filename() == "pipelines.bin") continue;
		std::ifstream file(path, std::ios::binary | std::ios::ate);
		const auto size = file.tellg();
		if (!file || size < static_cast<std::streamoff>(cache.Signature().size() + 8) || size > (64u << 20)) {
			PipelineCacheLog("ShaderSeed: invalid shader size; ignored");
			return;
		}
		std::vector<char> bytes(static_cast<size_t>(size));
		file.seekg(0);
		file.read(bytes.data(), size);
		uint64_t checksum = 0;
		std::memcpy(&checksum, bytes.data() + cache.Signature().size(), 8);
		const auto offset = cache.Signature().size() + 8;
		if (!file || std::memcmp(bytes.data(), cache.Signature().data(), cache.Signature().size()) != 0 ||
		    checksum != XXH3_64bits(bytes.data() + offset, bytes.size() - offset)) {
			PipelineCacheLog("ShaderSeed: stale or corrupt shader; ignored");
			return;
		}
		shaders.push_back(path);
	}
	if (ec || shaders.empty()) return;
	std::filesystem::create_directories(cache.Directory(), ec);
	for (const auto& path: shaders) {
		if (ec) break;
		std::filesystem::copy_file(path, cache.Directory() / path.filename(),
		                          std::filesystem::copy_options::overwrite_existing, ec);
	}
	if (!ec) {
		const auto temporary = cache.Directory() / "pipelines.seed.tmp";
		std::filesystem::copy_file(seed / "pipelines.bin", temporary,
		                          std::filesystem::copy_options::overwrite_existing, ec);
		if (!ec && !Common::File::RenameFile(temporary, cache.Directory() / "pipelines.bin")) {
			ec = std::make_error_code(std::errc::io_error);
		}
	}
	PipelineCacheLog("ShaderSeed: {} ({} shaders)", ec ? ec.message() : "installed", shaders.size());
}

void PipelineCache::StartPrecache() {
	if (!PipelinePrecacheEnabled() || !m_program_cache->translation_cache.Enabled()) {
		return;
	}
	InstallShaderSeed();
	m_recipes_path = m_program_cache->translation_cache.Directory() / "pipelines.bin";
	if (!Common::File::IsFileExisting(m_recipes_path)) {
		LOGF("PipelinePrecache: no %s yet\n", Common::PathToString(m_recipes_path).c_str());
		return;
	}
	m_precache_active.store(true, std::memory_order_release);
	m_precache_thread = std::thread([this] {
		PrecachePipelines();
		m_precache_active.store(false, std::memory_order_release);
	});
}

// Background thread: reads the recipes, loads the translation-cache entries they need (file
// reads outside the cache lock), inserts the programs and queues one job per pipeline. The
// recipes are kept in memory so the file is rewritten complete when new pipelines are added.
void PipelineCache::PrecachePipelines() {
#if defined(_WIN32)
	SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_BELOW_NORMAL);
#endif
	const auto           t0 = HostMicros();
	std::vector<uint8_t> data;
	{
		Common::File file(m_recipes_path, Common::File::Mode::Read);
		if (file.IsInvalid()) {
			return;
		}
		const auto size = file.Size();
		if (size < sizeof(RECIPES_MAGIC) || size > (256u << 20)) {
			return;
		}
		data.resize(static_cast<size_t>(size));
		uint32_t read = 0;
		file.Read(data.data(), static_cast<uint32_t>(data.size()), &read);
		if (read != data.size()) {
			return;
		}
	}
	RecipeReader r(data.data(), data.size());
	char         magic[sizeof(RECIPES_MAGIC) - 1] = {};
	r.Bytes(magic, sizeof(magic));
	if (r.Failed() || std::memcmp(magic, RECIPES_MAGIC, sizeof(magic)) != 0) {
		LOGF("PipelinePrecache: bad magic\n");
		return;
	}
	const auto  signature_size = r.U32();
	const auto expected = m_program_cache->translation_cache.Signature() + RecipeLayoutSignature();
	if (r.Failed() || signature_size != expected.size()) {
		LOGF("PipelinePrecache: stale recipes (signature size mismatch), ignored\n");
		return;
	}
	std::string signature(signature_size, '\0');
	r.Bytes(signature.data(), signature_size);
	if (r.Failed() || signature != expected) {
		LOGF("PipelinePrecache: stale recipes (signature mismatch), ignored\n");
		return;
	}
	const auto count = r.U32();
	m_precache_total.store(count);
	uint32_t graphics = 0;
	uint32_t compute  = 0;
	uint32_t skipped  = 0;
	uint32_t loaded_sources = 0;
	uint32_t max_scratch    = 0; // dwords per thread, over all stages
	uint32_t with_scratch   = 0;
	std::vector<std::pair<size_t, size_t>> record_spans;
	for (uint32_t i = 0; i < count && !r.Failed() && !m_precache_stop.load(); i++) {
		const size_t record_begin = r.Pos();
		const auto   kind         = r.U8();
		// KYTY_PIPELINE_PRECACHE=gfx|cs: only one kind (bisection of memory use).
		static const char* only = std::getenv("KYTY_PIPELINE_PRECACHE");
		const bool skip_kind = only != nullptr && ((kind == 1 && std::strcmp(only, "cs") == 0) ||
		                                           (kind == 2 && std::strcmp(only, "gfx") == 0));
		if (kind == 1) {
			ShaderTranslationCache::StoredKey vs_key;
			ShaderTranslationCache::StoredKey ps_key;
			r.Key(vs_key);
			const auto vs_index  = r.U32();
			const bool ps_active = r.U8() != 0;
			uint32_t   ps_index  = 0;
			if (ps_active) {
				r.Key(ps_key);
				ps_index = r.U32();
			}
			GraphicsPipelineKey key {};
			r.Pod(key.rendering);
			r.Pod(key.vertex_input);
			r.Pod(key.static_params);
			auto vs_info = std::make_shared<ShaderVertexInputInfo>();
			auto ps_info = std::make_shared<ShaderPixelInputInfo>();
			r.Info(*vs_info);
			if (ps_active) {
				r.Info(*ps_info);
			}
			if (r.Failed()) {
				break;
			}
			record_spans.emplace_back(record_begin, r.Pos());
			if (skip_kind) {
				skipped++;
				m_precache_skipped.fetch_add(1);
				m_precache_completed.fetch_add(1);
				continue;
			}
			// File reads outside the lock; the entries are only used when the run has not loaded
			// the source yet.
			ShaderTranslationCache::Entry vs_entry;
			ShaderTranslationCache::Entry ps_entry;
			const bool vs_loaded = m_program_cache->LoadEntry(vs_key, vs_entry);
			const bool ps_loaded = ps_active && m_program_cache->LoadEntry(ps_key, ps_entry);
			ShaderProgram                                   vs_program;
			ShaderProgram                                   ps_program;
			const ShaderRecompiler::IR::CompiledShaderInfo* vs_compiled = nullptr;
			const ShaderRecompiler::IR::CompiledShaderInfo* ps_compiled = nullptr;
			GraphicsPipelineEntry*                          target      = nullptr;
			{
				Common::LockGuard lock(m_mutex);
				if (!m_program_cache->Resolve(vs_key, vs_index, vs_loaded ? &vs_entry : nullptr,
				                              vs_program, vs_compiled) ||
				    (ps_active && !m_program_cache->Resolve(ps_key, ps_index,
				                                            ps_loaded ? &ps_entry : nullptr,
				                                            ps_program, ps_compiled))) {
					skipped++;
					m_precache_skipped.fetch_add(1);
					m_precache_completed.fetch_add(1);
					continue;
				}
				loaded_sources += (vs_loaded ? 1 : 0) + (ps_loaded ? 1 : 0);
				key.vs_shader_id = vs_program.id;
				key.ps_shader_id = ps_active ? ps_program.id : 0;
				if (m_graphics_pipelines.contains(key)) {
					skipped++;
					m_precache_skipped.fetch_add(1);
					m_precache_completed.fetch_add(1);
					continue;
				}
				auto entry = std::make_unique<GraphicsPipelineEntry>();
				target     = entry.get();
				m_graphics_pipelines.emplace(key, std::move(entry));
				m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);
			}
			vs_info->stage = {.program = vs_compiled};
			ps_info->stage = {.program = ps_compiled};
			{
				const auto scratch = std::max(vs_info->scratch_size_dwords,
				                              ps_active ? ps_info->scratch_size_dwords : 0u);
				max_scratch        = std::max(max_scratch, scratch);
				with_scratch += scratch != 0 ? 1u : 0u;
			}
			const auto pair_key = ShaderPairKey(key.vs_shader_id, key.ps_shader_id);
			graphics++;
			EnqueueJob([this, key, vs_info, ps_info, ps_active, vs_program, ps_program, target,
			            pair_key] {
				const auto create_begin = HostMicros();
				CreatePipelineInternal(m_graphics, *target, key.rendering, key.vertex_input, *vs_info,
				                       vs_program, ps_active ? ps_info.get() : nullptr, ps_program,
				                       key.static_params, m_driver_cache);
				EXIT_NOT_IMPLEMENTED(target->pipeline == nullptr);
				EXIT_NOT_IMPLEMENTED(target->pipeline_layout == nullptr);
				{
					Common::LockGuard lock(m_mutex);
					if (AvTraceEnabled()) {
						LOGF("AvTrace: pipeline gfx vs=%" PRIu64 " ps=%" PRIu64 " us=%" PRIu64
						     " total=%" PRIu64 " precache\n",
						     key.vs_shader_id, key.ps_shader_id, HostMicros() - create_begin,
						     static_cast<uint64_t>(m_graphics_pipelines.size()));
					}
					m_ready_shader_pairs.insert(pair_key);
				}
				{
					std::lock_guard<std::mutex> lock(m_job_mutex);
					target->ready.store(true, std::memory_order_release);
				}
				m_ready_cv.notify_all();
				m_pending_pipelines.fetch_sub(1, std::memory_order_relaxed);
			m_precache_completed.fetch_add(1);
			});
		} else if (kind == 2) {
			ShaderTranslationCache::StoredKey cs_key;
			r.Key(cs_key);
			const auto index = r.U32();
			auto       info  = std::make_shared<ShaderComputeInputInfo>();
			r.Info(*info);
			if (r.Failed()) {
				break;
			}
			record_spans.emplace_back(record_begin, r.Pos());
			if (skip_kind) {
				skipped++;
				m_precache_skipped.fetch_add(1);
				m_precache_completed.fetch_add(1);
				continue;
			}
			ShaderTranslationCache::Entry cs_entry;
			const bool cs_loaded = m_program_cache->LoadEntry(cs_key, cs_entry);
			ShaderProgram                                   program;
			const ShaderRecompiler::IR::CompiledShaderInfo* compiled = nullptr;
			ComputePipelineEntry*                           target   = nullptr;
			{
				Common::LockGuard lock(m_mutex);
				if (!m_program_cache->Resolve(cs_key, index, cs_loaded ? &cs_entry : nullptr, program,
				                              compiled)) {
					skipped++;
					m_precache_skipped.fetch_add(1);
					m_precache_completed.fetch_add(1);
					continue;
				}
				loaded_sources += cs_loaded ? 1 : 0;
				if (m_compute_pipelines.contains(program.id)) {
					skipped++;
					m_precache_skipped.fetch_add(1);
					m_precache_completed.fetch_add(1);
					continue;
				}
				auto entry = std::make_unique<ComputePipelineEntry>();
				target     = entry.get();
				m_compute_pipelines.emplace(program.id, std::move(entry));
				m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);
			}
			info->stage = {.program = compiled};
			max_scratch = std::max(max_scratch, info->scratch_size_dwords);
			with_scratch += info->scratch_size_dwords != 0 ? 1u : 0u;
			compute++;
			const auto module = program.module;
			const auto id     = program.id;
			EnqueueJob([this, info, module, id, target] {
				const auto create_begin = HostMicros();
				CreatePipelineInternal(m_graphics, *target, *info, module, m_driver_cache);
				EXIT_NOT_IMPLEMENTED(target->pipeline == nullptr);
				EXIT_NOT_IMPLEMENTED(target->pipeline_layout == nullptr);
				{
					Common::LockGuard lock(m_mutex);
					if (AvTraceEnabled()) {
						LOGF("AvTrace: pipeline cs cs=%" PRIu64 " us=%" PRIu64 " total=%" PRIu64
						     " precache\n",
						     id, HostMicros() - create_begin,
						     static_cast<uint64_t>(m_compute_pipelines.size()));
					}
				}
				{
					std::lock_guard<std::mutex> lock(m_job_mutex);
					target->ready.store(true, std::memory_order_release);
				}
				m_ready_cv.notify_all();
				m_pending_pipelines.fetch_sub(1, std::memory_order_relaxed);
			m_precache_completed.fetch_add(1);
			});
		} else {
			break;
		}
	}
	const bool complete = !r.Failed() && r.AtEnd();
	{
		// Keep the file's recipes (complete file only) so the rewrite carries them forward, then
		// the records this run added meanwhile; both deduplicated by hash.
		Common::LockGuard lock(m_mutex);
		if (complete) {
			std::vector<uint8_t>  current;
			std::vector<uint32_t> current_sizes;
			current.swap(m_recipes);
			current_sizes.swap(m_recipe_sizes);
			m_recipe_hashes.clear();
			m_recipe_count = 0;
			for (const auto& [begin, end]: record_spans) {
				AppendRecipe(data.data() + begin, end - begin);
			}
			size_t offset = 0;
			for (const auto size: current_sizes) {
				AppendRecipe(current.data() + offset, size);
				offset += size;
			}
			m_recipes_unsaved = m_recipe_count > count ? m_recipe_count - count : 0;
		}
	}
	LOGF("PipelinePrecache: %u recipes -> %u graphics + %u compute pipelines queued, %u skipped, "
	     "%u sources loaded, %s, %" PRIu64 " ms (scratch: %u pipelines, max %u dwords/thread)\n",
	     count, graphics, compute, skipped, loaded_sources, complete ? "complete" : "TRUNCATED",
	     (HostMicros() - t0) / 1000u, with_scratch, max_scratch);
	VulkanLogMemoryStats();
	WaitForPendingPipelines();
	LOGF("PipelinePrecache: all pipelines created, %" PRIu64 " ms\n", (HostMicros() - t0) / 1000u);
	VulkanLogMemoryStats();
}

} // namespace Libs::Graphics
