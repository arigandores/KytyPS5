#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"

#include "graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h"
#include "graphics/host_gpu/renderer/pipeline/computePretranslation.h"
#include "graphics/guest_gpu/command_processor/commandProcessor.h"
#include "graphics/guest_gpu/pm4.h"

#include "common/gates.h"
#include "common/frameStats.h"

#include "common/assert.h"
#include "common/drawStat.h"
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
#include <xmmintrin.h>
#include <bit>

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

	// A view over a direct-mapped table of validated pages. The per-call tables are small (they
	// are constructed on every lookup); the persistent one is large enough for the descriptor
	// pages of a whole frame.
	struct Pages {
		Page   last;
		Page*  entries = nullptr;
		size_t mask    = 0;

		void Bind(Page* storage, size_t count) {
			entries = storage;
			mask    = count - 1;
		}
		bool Find(uint64_t page) {
			if (last.address == page) return true;
			if (entries == nullptr || !Enabled()) return false;
			const auto& entry = entries[Slot(page) & mask];
			if (entry.address != page) return false;
			last = entry;
			return true;
		}
		void Store(uint64_t page, const void* backing) {
			last = {page, static_cast<const uint8_t*>(backing)};
			if (entries != nullptr && Enabled()) entries[Slot(page) & mask] = last;
		}
		static size_t Slot(uint64_t page) { return (page >> 12u) ^ (page >> 19u); }
		static bool Enabled() {
			static const bool enabled = [] {
				const auto* value = std::getenv("KYTY_SRT_PAGE_CACHE");
				return value == nullptr || value[0] != '0';
			}();
			return enabled;
		}
	};

	static constexpr size_t CALL_SLOTS       = 8;
	static constexpr size_t PERSISTENT_SLOTS = 4096;

	// The same descriptor pages are walked by every stage of every draw. A validated live
	// translation stays correct until the guest map table changes, so keep it per thread and drop
	// the whole table when the backing map epoch moves. The gate "srtpages" restores the
	// per-call table.
	struct Persistent {
		uint64_t                           epoch = 0;
		Pages                              pages;
		std::array<Page, PERSISTENT_SLOTS> storage {};
	};

	static Pages* PersistentLive() {
		thread_local Persistent cache;
		if (cache.pages.entries == nullptr) {
			cache.pages.Bind(cache.storage.data(), PERSISTENT_SLOTS);
		}
		const auto epoch = Libs::LibKernel::Memory::BackingMapEpoch();
		if (cache.epoch != epoch) {
			cache.epoch = epoch;
			// In place: `storage = {}` builds a 64 KiB array temporary, and inlining puts that
			// temporary in the caller's stack frame (it is what made ProgramCache::Get reserve
			// 66 KiB and overflow guest stacks).
			cache.storage.fill(Page {});
			cache.pages.last = {};
		}
		return &cache.pages;
	}

	// One add per lookup instead of one per guest word (about 440k words a frame).
	~ShaderReadCache() {
		if (live_reads != 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::ProgReads, live_reads);
		}
		if (clean_reads != 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::ProgCleanReads, clean_reads);
		}
	}
	ShaderReadCache(const ShaderReadCache&)            = delete;
	ShaderReadCache& operator=(const ShaderReadCache&) = delete;

	ShaderReadCache() {
		own_live.Bind(own_live_storage.data(), CALL_SLOTS);
		clean.Bind(clean_storage.data(), CALL_SLOTS);
		live = Common::Gates::Enabled(Common::Gates::Gate::SrtPagePersist) ? PersistentLive()
		                                                                  : &own_live;
	}

	// GPU-clean validations stay per lookup: they depend on the GPU dirty state, not on the map.
	std::array<Page, CALL_SLOTS> own_live_storage {};
	std::array<Page, CALL_SLOTS> clean_storage {};
	Pages                        own_live;
	Pages                        clean;
	Pages*                       live = nullptr;
	struct SrtReadLog*           log  = nullptr; // set while a materialization is being recorded
	uint32_t                     live_reads  = 0;
	uint32_t                     clean_reads = 0;
};

// The guest words one materialization read. Every read of the SRT walk goes through the two
// SrtRuntime callbacks, so this is the complete input of that walk besides the plan, the user data
// and the shader base: while all these addresses still hold these values, repeating the walk would
// produce the same snapshot (see the materialization memo below).
struct SrtReadLog {
	struct Entry {
		uint64_t address = 0;
		uint32_t value   = 0;
		uint8_t  clean   = 0; // read through the GPU-clean (specialization) reader
		uint8_t  ok      = 0;
		uint8_t  paged   = 0; // served from a validated page (may be checked as part of a run)
	};

	static constexpr size_t MaxEntries = 1024;

	std::vector<Entry> entries;
	bool               overflow = false;

	void Note(uint64_t address, uint32_t value, bool clean, bool ok, bool paged) {
		if (entries.size() >= MaxEntries) {
			overflow = true;
			return;
		}
		entries.push_back({address, value, static_cast<uint8_t>(clean ? 1 : 0),
		                   static_cast<uint8_t>(ok ? 1 : 0), static_cast<uint8_t>(paged ? 1 : 0)});
	}
};

constexpr uint64_t ShaderPageSize = 0x1000;

// Validated host pointer to a guest page, or nullptr. Shared by the readers below and by the memo
// validation, which compares whole runs of recorded words with one memcmp instead of re-reading
// them one at a time.
const uint8_t* LiveBackingPage(ShaderReadCache* cache, uint64_t page) {
	if (cache == nullptr) {
		return nullptr;
	}
	if (!cache->live->Find(page)) {
		if (Common::FrameStats::Enabled()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SrtPageMisses, 1);
		}
		const void* backing = nullptr;
		if (Libs::LibKernel::Memory::TryGetBackingPointer(page, ShaderPageSize, &backing)) {
			cache->live->Store(page, backing);
		} else {
			cache->live->last = {};
			return nullptr;
		}
	}
	return cache->live->last.address == page ? cache->live->last.backing : nullptr;
}

const uint8_t* CleanBackingPage(ShaderReadCache* cache, uint64_t page) {
	if (cache == nullptr) {
		return nullptr;
	}
	if (!cache->clean.Find(page)) {
		const void* backing = nullptr;
		if (Libs::LibKernel::Memory::TryGetGpuCleanBackingPointer(page, ShaderPageSize, &backing)) {
			cache->clean.Store(page, backing);
		}
	}
	return cache->clean.last.address == page ? cache->clean.last.backing : nullptr;
}

// Guest memory for specialization decisions: only words with no pending GPU writes may be read
// (upstream reads them one at a time with a dirty-range query per word; the SRT control-flow
// conditions add several per draw, so the whole page is validated once and reused).
bool ReadShaderGuestMemory(void* userdata, uint64_t address, uint32_t* value) {
	auto* cache = static_cast<ShaderReadCache*>(userdata);
	if (cache != nullptr) {
		cache->clean_reads++;
	} else {
		Common::FrameStats::Add(Common::FrameStats::Counter::ProgCleanReads, 1);
	}
	if (value == nullptr) {
		return false;
	}
	const auto page  = address & ~(ShaderPageSize - 1);
	if (cache != nullptr && (address & 3u) == 0) {
		if (const auto* backing = CleanBackingPage(cache, page); backing != nullptr) {
			std::memcpy(value, backing + (address - page), sizeof(*value));
			if (cache->log != nullptr) {
				cache->log->Note(address, *value, true, true, true);
			}
			return true;
		}
	}
	// The page is partly GPU-dirty or not one mapping: decide per word as before.
	const bool ok = Libs::LibKernel::Memory::TryReadGpuCleanBacking(address, value, sizeof(*value));
	if (cache != nullptr && cache->log != nullptr) {
		cache->log->Note(address, ok ? *value : 0u, true, ok, false);
	}
	return ok;
}

bool ReadShaderLiveMemory(void* userdata, uint64_t address, uint32_t* value) {
	auto* cache = static_cast<ShaderReadCache*>(userdata);
	if (cache != nullptr) {
		cache->live_reads++;
	} else {
		Common::FrameStats::Add(Common::FrameStats::Counter::ProgReads, 1);
	}
	if (value == nullptr) {
		return false;
	}
	const auto page  = address & ~(ShaderPageSize - 1);
	if (cache != nullptr && (address & 3u) == 0) {
		if (const auto* backing = LiveBackingPage(cache, page); backing != nullptr) {
			std::memcpy(value, backing + (address - page), sizeof(*value));
			if (cache->log != nullptr) {
				cache->log->Note(address, *value, false, true, true);
			}
			return true;
		}
	}
	const bool ok = Libs::LibKernel::Memory::TryReadBacking(address, value, sizeof(*value));
	if (cache != nullptr && cache->log != nullptr) {
		cache->log->Note(address, ok ? *value : 0u, false, ok, false);
	}
	return ok;
}

// The specialization reader of a draw-lookahead worker. Whether a word has pending GPU writes can
// only be asked on the GuestGpu thread, so the worker reads the word as it is and records the read
// as a clean one: the draw validates it through the clean reader, which fails exactly where a
// clean read would have failed, and the result is then materialized again.
bool ReadShaderAheadClean(void* userdata, uint64_t address, uint32_t* value) {
	if (value == nullptr) {
		return false;
	}
	auto*      cache = static_cast<ShaderReadCache*>(userdata);
	const auto page  = address & ~(ShaderPageSize - 1);
	if (cache != nullptr && (address & 3u) == 0) {
		if (const auto* backing = LiveBackingPage(cache, page); backing != nullptr) {
			std::memcpy(value, backing + (address - page), sizeof(*value));
			if (cache->log != nullptr) {
				cache->log->Note(address, *value, true, true, true);
			}
			return true;
		}
	}
	const bool ok = Libs::LibKernel::Memory::TryReadBacking(address, value, sizeof(*value));
	if (cache != nullptr && cache->log != nullptr) {
		cache->log->Note(address, ok ? *value : 0u, true, ok, false);
	}
	return ok;
}

// The recorded reads of one materialization in the form they are validated in: consecutive dwords
// inside one guest page read through the same reader form a run checked with one memcmp.
struct Witness {
	struct Run {
		uint64_t address = 0;
		uint32_t first   = 0; // index into that reader's value array
		uint32_t count   = 0;
	};
	struct Single { // a read the page path could not serve (unaligned, or unreadable)
		uint64_t address = 0;
		uint32_t value   = 0;
		bool     clean   = false;
		bool     ok      = false;
	};

	std::vector<Run>      live_runs;
	std::vector<uint32_t> live_values;
	std::vector<Run>      clean_runs;
	std::vector<uint32_t> clean_values;
	std::vector<Single>   singles;

	[[nodiscard]] size_t Words() const {
		return live_values.size() + clean_values.size() + singles.size();
	}

	// What validation actually costs: one page lookup and one comparison per run. A single
	// counts as one of its own - it is a separate guest read.
	[[nodiscard]] size_t Runs() const {
		return live_runs.size() + clean_runs.size() + singles.size();
	}

	void Build(const SrtReadLog& log) {
		live_runs.clear();
		live_values.clear();
		clean_runs.clear();
		clean_values.clear();
		singles.clear();
		for (const auto& read: log.entries) {
			if (read.ok == 0 || read.paged == 0) {
				singles.push_back({read.address, read.value, read.clean != 0, read.ok != 0});
				continue;
			}
			auto&      runs   = read.clean != 0 ? clean_runs : live_runs;
			auto&      values = read.clean != 0 ? clean_values : live_values;
			const bool joins  = !runs.empty() &&
			                   runs.back().address + runs.back().count * sizeof(uint32_t) == read.address &&
			                   ((runs.back().address ^ read.address) & ~(ShaderPageSize - 1)) == 0;
			if (joins) {
				runs.back().count++;
			} else {
				runs.push_back({read.address, static_cast<uint32_t>(values.size()), 1});
			}
			values.push_back(read.value);
		}
	}
};

// One recorded run against the guest words it was read from. The runs are short - a run is a
// V# or a T#, four or eight dwords - and a memcmp call each was 6.4 % of all GuestGpu samples in
// Sky Garden, so compare short runs here and leave memcmp the rare long one. The guest bytes are
// read through memcpy: the backing pointer carries no alignment or type guarantee.
[[nodiscard]] bool SameRecordedWords(const uint8_t* backing, const uint32_t* recorded,
                                     uint32_t count) noexcept {
	if (count > 8) {
		return std::memcmp(backing, recorded, count * sizeof(uint32_t)) == 0;
	}
	for (uint32_t i = 0; i < count; i++) {
		uint32_t word = 0;
		std::memcpy(&word, backing + i * sizeof(uint32_t), sizeof(word));
		if (word != recorded[i]) {
			return false;
		}
	}
	return true;
}

// True while every recorded word still reads back, through its reader, as recorded.
bool VerifyWitness(const Witness& witness, ShaderReadCache& cache) {
	for (const auto& run: witness.live_runs) {
		const auto* backing = LiveBackingPage(&cache, run.address & ~(ShaderPageSize - 1));
		if (backing == nullptr ||
		    !SameRecordedWords(backing + (run.address & (ShaderPageSize - 1)),
		                       &witness.live_values[run.first], run.count)) {
			return false;
		}
	}
	for (const auto& run: witness.clean_runs) {
		const auto* backing = CleanBackingPage(&cache, run.address & ~(ShaderPageSize - 1));
		if (backing != nullptr) {
			if (!SameRecordedWords(backing + (run.address & (ShaderPageSize - 1)),
			                       &witness.clean_values[run.first], run.count)) {
				return false;
			}
			continue;
		}
		// The page is not GPU-clean as a whole any more: the clean reader decides per word, and
		// so does the check.
		for (uint32_t i = 0; i < run.count; i++) {
			uint32_t value = 0;
			if (!ReadShaderGuestMemory(&cache, run.address + i * sizeof(uint32_t), &value) ||
			    value != witness.clean_values[run.first + i]) {
				return false;
			}
		}
	}
	for (const auto& single: witness.singles) {
		uint32_t   value = 0;
		const bool ok    = single.clean ? ReadShaderGuestMemory(&cache, single.address, &value)
		                                : ReadShaderLiveMemory(&cache, single.address, &value);
		if (ok != single.ok || (ok && value != single.value)) {
			return false;
		}
	}
	return true;
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

// Gate "daclass" (session 56): the canonical form of a resource plan.
// ShaderTranslationCache::PlanFingerprint hashes the plan exactly as the translation cache writes it,
// and those bytes are not canonical: IR::Value keeps immediates in a union whose ScalarReg/VectorReg/
// U1/U8/U16/U32 constructors set only the low bytes, while WriteValue stores Bits(), the whole 64-bit
// member (a plan loaded from the cache keeps the bytes of its file), and POD vectors are written with
// their struct padding. Static variants of one program - the vertex layout of the mesh, which the
// plan does not depend on - got different fingerprints for the same plan (session 56: 68 of 69
// multi-variant programs of the cache had one canonical plan), and the lookahead queued one task per
// variant. This writes the fields WritePlan writes, in the same order, with every immediate masked to
// the width its accessors read (Bits() has no reader outside serialization) and PODs field by field.
// Equal bytes therefore mean plans that differ at most in bits no accessor reads - the equivalence the
// translation cache itself relies on (a plan read back from its file materializes like the live one) -
// so MaterializeResources gives them the same snapshot and specialization for the same runtime. The
// stage interface (inputs, outputs, vertex fetch) is compared too although materialization does not
// read it: "equal" stays stricter than needed. Kept out of shaderTranslationCache.cpp and
// graphics/shader/**, whose contents key the translation cache.
struct CanonicalPlanWriter {
	std::vector<uint8_t> data;

	void Bytes(const void* bytes, size_t size) {
		const auto* p = static_cast<const uint8_t*>(bytes);
		data.insert(data.end(), p, p + size);
	}
	void U8(uint8_t value) { data.push_back(value); }
	void U32(uint32_t value) { Bytes(&value, sizeof(value)); }
	void U64(uint64_t value) { Bytes(&value, sizeof(value)); }
	void Bool(bool value) { U8(value ? 1u : 0u); }
	void Str(const std::string& value) {
		U32(static_cast<uint32_t>(value.size()));
		Bytes(value.data(), value.size());
	}
	void U32s(const std::vector<uint32_t>& values) {
		U32(static_cast<uint32_t>(values.size()));
		Bytes(values.data(), values.size() * sizeof(uint32_t));
	}
};

// A field added to one of these PODs must be added to CanonicalPlanBytes as well (the sizes are those
// of the translation cache files, parsed in session 56).
static_assert(sizeof(ShaderRecompiler::IR::MemoryInfo) == 72);
static_assert(sizeof(ShaderRecompiler::IR::BufferResource) == 36);
static_assert(sizeof(ShaderRecompiler::IR::SamplerResource) == 12);
static_assert(sizeof(ShaderRecompiler::IR::SampledResourcePair) == 12);
static_assert(sizeof(ShaderRecompiler::IR::DescriptorSource::IndirectImage) == 20);
static_assert(sizeof(ShaderRecompiler::IR::UniformFill) == 28);

uint64_t CanonicalImmediate(ShaderRecompiler::IR::Type type, uint64_t bits) {
	using Type = ShaderRecompiler::IR::Type;
	switch (type) {
		case Type::Void: return 0;
		case Type::U1:
		case Type::U8: return bits & 0xffu;
		case Type::ScalarReg:
		case Type::VectorReg:
		case Type::U16:
		case Type::F16: return bits & 0xffffu;
		case Type::U32:
		case Type::F32: return bits & 0xffffffffu;
		default: return bits; // wider or unusual immediates: all bits (only ever splits a class)
	}
}

void CanonicalValue(CanonicalPlanWriter& w, const ShaderRecompiler::IR::Value& value,
					const std::unordered_map<const ShaderRecompiler::IR::Inst*, uint32_t>& index_of) {
	if (!value.IsImmediate()) {
		w.U32(static_cast<uint32_t>(ShaderRecompiler::IR::Type::Opaque));
		const ShaderRecompiler::IR::Inst* inst = value.TryInstruction();
		const auto found = inst != nullptr ? index_of.find(inst) : index_of.end();
		w.U64(inst == nullptr ? UINT64_MAX : found != index_of.end() ? found->second : UINT64_MAX - 1u);
		return;
	}
	const auto type = value.GetType();
	w.U32(static_cast<uint32_t>(type));
	w.U64(CanonicalImmediate(type, value.Bits()));
}

[[gnu::noinline]] std::vector<uint8_t> CanonicalPlanBytes(const ShaderRecompiler::IR::ResourcePlan& plan) {
	namespace IR = ShaderRecompiler::IR;
	CanonicalPlanWriter w;
	w.data.reserve(4096);
	w.U32(static_cast<uint32_t>(plan.stage));
	w.U64(plan.shader_hash);
	w.U32(plan.user_data_base);
	w.U32(plan.user_data_count);
	std::unordered_map<const IR::Inst*, uint32_t> index_of;
	index_of.reserve(plan.value_storage.size());
	for (const auto& inst: plan.value_storage) {
		index_of.emplace(&inst, static_cast<uint32_t>(index_of.size()));
	}
	w.U32(static_cast<uint32_t>(plan.value_storage.size()));
	for (const auto& inst: plan.value_storage) {
		w.U32(static_cast<uint32_t>(inst.GetOpcode()));
		w.U64(inst.Flags<uint64_t>());
		w.U32(static_cast<uint32_t>(inst.NumArgs()));
		for (size_t i = 0; i < inst.NumArgs(); i++) {
			CanonicalValue(w, inst.Arg(i), index_of);
		}
	}
	w.U32(static_cast<uint32_t>(plan.memory_info.size()));
	for (const auto& m: plan.memory_info) {
		for (const uint32_t field: {static_cast<uint32_t>(m.kind), m.resource, m.sampler, m.offset,
									m.secondary_offset, m.dmask, m.data_dwords, m.data_bits,
									m.component_index, m.component_count, m.data_format,
									m.number_format, m.image_sample_flags,
									static_cast<uint32_t>(m.image_dimension),
									m.image_address_components}) {
			w.U32(field);
		}
		for (const bool flag: {m.address_is_full, m.data_signed, m.typed, m.formatted, m.image_has_mip,
							   m.image_r128, m.idxen, m.offen, m.planning_only}) {
			w.Bool(flag);
		}
	}
	w.U32(static_cast<uint32_t>(plan.descriptor_sources.size()));
	for (const auto& source: plan.descriptor_sources) {
		w.U32(source.dword_count);
		for (const auto& dword: source.dwords) {
			CanonicalValue(w, dword, index_of);
		}
		w.Bool(source.indirect_image.has_value());
		if (source.indirect_image.has_value()) {
			const auto& image = *source.indirect_image;
			for (const uint32_t field: {image.material_source, image.heap_source, image.selector_stride,
										image.selector_offset, image.key_arg}) {
				w.U32(field);
			}
		}
	}
	w.U32s(plan.materialization_sources);
	w.U32(static_cast<uint32_t>(plan.srt_reads.size()));
	for (const auto& read: plan.srt_reads) {
		CanonicalValue(w, read.value, index_of);
		w.U32(read.flat_offset);
		w.Bool(read.variant);
	}
	w.U32(static_cast<uint32_t>(plan.clean_flat_slots.size()));
	w.Bytes(plan.clean_flat_slots.data(), plan.clean_flat_slots.size());
	w.Bool(plan.requires_specialization_memory);
	w.Bool(plan.srt_plan_complete);
	w.Bool(plan.resource_tracking_complete);
	w.U32(static_cast<uint32_t>(plan.control_flow.size()));
	for (const auto& block: plan.control_flow) {
		CanonicalValue(w, block.condition, index_of);
		w.U32s(block.successors);
		w.U32s(block.sources);
	}
	const auto& fill = plan.uniform_fill.fill;
	for (const uint32_t field: {static_cast<uint32_t>(fill.kind), fill.resource, fill.group_stride[0],
								fill.group_stride[1], fill.group_stride[2], fill.words, fill.value}) {
		w.U32(field);
	}
	for (const auto& value: plan.uniform_fill.values) {
		CanonicalValue(w, value, index_of);
	}
	const auto& info = plan.info;
	w.U32(static_cast<uint32_t>(info.buffers.size()));
	for (const auto& b: info.buffers) {
		for (const uint32_t field: {b.source, b.first_use_pc, b.max_byte_extent, b.packed_stride,
									static_cast<uint32_t>(b.descriptor_format), b.descriptor_swizzle,
									b.image_alias}) {
			w.U32(field);
		}
		for (const bool flag: {b.read, b.written, b.atomic, b.formatted, b.scalar}) {
			w.Bool(flag);
		}
	}
	w.U32(static_cast<uint32_t>(info.images.size()));
	for (const auto& i: info.images) {
		for (const uint32_t field: {i.source, i.first_use_pc, static_cast<uint32_t>(i.resource_class),
									static_cast<uint32_t>(i.numeric_class),
									static_cast<uint32_t>(i.dimension), static_cast<uint32_t>(i.mip_mode),
									i.mip_count, static_cast<uint32_t>(i.conversion_format),
									i.shader_swizzle}) {
			w.U32(field);
		}
		for (const bool flag: {i.read, i.written, i.atomic, i.depth_compare, i.cube, i.r128,
							   i.manual_depth_compare}) {
			w.Bool(flag);
		}
		for (const uint32_t field: {i.depth_compare_op, i.indirect_root, i.indirect_mapping_offset,
									i.indirect_search_iterations}) {
			w.U32(field);
		}
		w.U32s(i.indirect_resources);
	}
	w.U32(static_cast<uint32_t>(info.samplers.size()));
	for (const auto& s: info.samplers) {
		w.U32(s.source);
		w.U32(s.first_use_pc);
		w.Bool(s.force_point_filtering);
		w.Bool(s.depth_compare);
	}
	w.U32(static_cast<uint32_t>(info.sampled_pairs.size()));
	for (const auto& p: info.sampled_pairs) {
		w.U32(p.image);
		w.U32(p.sampler);
		w.U32(p.first_use_pc);
	}
	w.U32(static_cast<uint32_t>(info.inputs.size()));
	for (const auto& in: info.inputs) {
		w.U32(static_cast<uint32_t>(in.kind));
		w.U32(in.location);
		w.U32(in.component_count);
		w.Str(in.debug_name);
		w.Bool(in.per_vertex);
	}
	w.U32(static_cast<uint32_t>(info.outputs.size()));
	for (const auto& out: info.outputs) {
		w.U32(static_cast<uint32_t>(out.kind));
		w.U32(out.index);
		w.U32(out.location);
		w.Str(out.debug_name);
	}
	w.Bytes(info.vertex_fetch_components.data(), info.vertex_fetch_components.size());
	w.U32(static_cast<uint32_t>(info.vertex_offset_sgpr));
	w.U32(static_cast<uint32_t>(info.instance_offset_sgpr));
	w.Bool(info.has_bitwise_xor);
	w.Bool(info.uses_dma);
	return std::move(w.data);
}

// Gate "daprefetch": the first lines of a vector's heap block.
template <typename T>
void PrefetchVectorData(const std::vector<T>& values) {
	if (values.empty()) {
		return;
	}
	const auto* bytes = reinterpret_cast<const char*>(values.data());
	const auto  size  = std::min<size_t>(values.size() * sizeof(T), 192u);
	for (size_t offset = 0; offset < size; offset += 64u) {
		_mm_prefetch(bytes + offset, _MM_HINT_T0);
	}
}

// Session 58 (B4 follow-up): what one snapshot copy carried, for the ceiling counters. Filled
// only while the counters run; the copy itself never looks at it.
struct SnapshotCopyStats {
	uint64_t bytes        = 0;
	uint64_t same_bytes   = 0;
	uint32_t vectors      = 0;
	uint32_t same_vectors = 0;
};

// One vector of a copy into the kept snapshot storage (gate "snapkeep"). Gate "snapdiff"
// (`diff`) leaves a destination that already holds the same elements alone: what a reader sees
// is the same either way, and not storing it keeps the line clean and exclusive to this thread.
// The comparison stops at the first element that differs, so a changed vector pays little before
// its copy, and an equal one only reads memory the copy would have read anyway.
template <typename T>
void CopySnapshotVector(std::vector<T>& to, const std::vector<T>& from, bool diff,
                        SnapshotCopyStats* stats) {
	if (stats == nullptr) [[likely]] {
		if (diff && to == from) {
			return;
		}
		to = from;
		return;
	}
	const auto bytes = from.size() * sizeof(T);
	const bool same  = to == from;
	// Both under the same condition: a vector that is empty on both sides is no copy at all and is
	// counted nowhere. Counting it as equal alone broke snap_cp_eq (the snapshots whose vectors all
	// compare equal), which is read as same_vectors == vectors.
	if (bytes != 0 || !to.empty()) {
		stats->bytes += bytes;
		stats->vectors++;
		if (same) {
			stats->same_bytes += bytes;
			stats->same_vectors++;
		}
	}
	if (same && diff) {
		return;
	}
	to = from;
}

// The five vectors of a snapshot. uniform_fill is a few words inside the struct: always stored.
void CopySnapshot(const ShaderRecompiler::IR::ResourceSnapshot& from,
                  ShaderRecompiler::IR::ResourceSnapshot& to, bool diff,
                  SnapshotCopyStats* stats) {
	CopySnapshotVector(to.buffers, from.buffers, diff, stats);
	CopySnapshotVector(to.images, from.images, diff, stats);
	CopySnapshotVector(to.samplers, from.samplers, diff, stats);
	CopySnapshotVector(to.flattened_srt, from.flattened_srt, diff, stats);
	CopySnapshotVector(to.user_data, from.user_data, diff, stats);
	to.uniform_fill = from.uniform_fill;
}

void CopySpecialization(const ShaderRecompiler::IR::ResourceSpecialization& from,
                        ShaderRecompiler::IR::ResourceSpecialization& to, bool diff,
                        SnapshotCopyStats* stats) {
	CopySnapshotVector(to.buffers, from.buffers, diff, stats);
	CopySnapshotVector(to.images, from.images, diff, stats);
}

// Knob "dapin" and counter da_ccd_x (session 56): the L3 caches of processor group 0. On the Ryzen 9
// 9955HX3D the two CCDs have separate L3 caches, so a result a DrawAhead worker built on one CCD is
// cold for a GuestGpu thread running on the other.
struct DrawAheadCacheTopology {
	std::vector<uint64_t>   l3_masks; // group-0 affinity mask of every L3 cache
	std::vector<uint64_t>   l3_sizes; // its size in bytes
	std::array<uint8_t, 64> l3_of {}; // logical processor -> index in l3_masks, 0xff unknown
	uint64_t                process_mask = 0;
};

const DrawAheadCacheTopology& DrawAheadTopology() {
	static const DrawAheadCacheTopology topology = [] {
		DrawAheadCacheTopology result;
		result.l3_of.fill(0xffu);
#if defined(_WIN32)
		DWORD length = 0;
		GetLogicalProcessorInformationEx(RelationCache, nullptr, &length);
		std::vector<uint8_t> buffer(length);
		if (length != 0 &&
			GetLogicalProcessorInformationEx(
				RelationCache, reinterpret_cast<PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX>(buffer.data()),
				&length) != FALSE) {
			for (DWORD offset = 0; offset < length;) {
				const auto* entry =
					reinterpret_cast<PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX>(buffer.data() + offset);
				if (entry->Size == 0) {
					break;
				}
				const auto& cache = entry->Cache;
				if (entry->Relationship == RelationCache && cache.Level == 3 &&
					(cache.Type == CacheUnified || cache.Type == CacheData) &&
					cache.GroupMask.Group == 0 && result.l3_masks.size() < 0xffu) {
					const auto mask = static_cast<uint64_t>(cache.GroupMask.Mask);
					for (uint32_t cpu = 0; cpu < 64u; cpu++) {
						if (((mask >> cpu) & 1u) != 0) {
							result.l3_of[cpu] = static_cast<uint8_t>(result.l3_masks.size());
						}
					}
					result.l3_masks.push_back(mask);
					result.l3_sizes.push_back(cache.CacheSize);
				}
				offset += entry->Size;
			}
		}
		DWORD_PTR process = 0;
		DWORD_PTR system  = 0;
		if (GetProcessAffinityMask(GetCurrentProcess(), &process, &system) != FALSE) {
			result.process_mask = static_cast<uint64_t>(process);
		}
#endif
		return result;
	}();
	return topology;
}

} // namespace

// Declared in pipelineCache.h: the record thread counts rec_ccd_x with it (session 57, A4).
uint8_t DrawAheadCurrentL3() {
#if defined(_WIN32)
	const auto cpu = GetCurrentProcessorNumber();
	return cpu < 64u ? DrawAheadTopology().l3_of[cpu] : static_cast<uint8_t>(0xffu);
#else
	return 0xffu;
#endif
}

namespace {

std::atomic<uint8_t>  g_draw_ahead_gpu_l3 {0xffu}; // L3 index the GuestGpu thread last queued from
std::atomic<uint64_t> g_draw_ahead_gpu_mask {0};   // dapin=2: the mask the GuestGpu thread chose
// Knob "procpin": bumped whenever the process mask changes. SetProcessAffinityMask resets the mask of
// every thread, so a thread that pinned itself through "dapin" pins itself again.
std::atomic<uint32_t> g_process_pin_epoch {0};

// The process mask procpin last set (0 = the mask the process started with, topology.process_mask).
std::atomic<uint64_t> g_process_pin_mask {0};

} // namespace

// Knob "dapin" (session 56), for the "workers on the GuestGpu thread's CCD" experiment:
// 0 = leave affinity alone (a thread this pinned goes back to the process mask),
// 1 = the L3 group with the largest cache (the 3D-cache CCD of an X3D processor),
// 2 = the L3 group of the processor the GuestGpu thread is on when it applies the knob; the workers
//     follow the mask it chose,
// other = raw affinity mask of processor group 0 (decimal in the gate file; 1 and 2 are taken).
// Each thread applies it to itself: the GuestGpu thread once per submission, a DrawAhead worker at
// every task it claims (a thread-local compare when nothing changed).
void DrawAheadApplyPin(bool gpu_thread) {
#if defined(_WIN32)
	thread_local uint32_t applied_mode = 0;
	thread_local uint64_t applied_mask = 0;
	thread_local uint32_t applied_epoch = 0;
	const auto& topology = DrawAheadTopology();
	if (gpu_thread) {
		// Knob "procpin", applied by the GuestGpu thread for the whole process.
		static uint32_t applied_process = 0;
		const auto      process_mode    = Common::Gates::Value(Common::Gates::Knob::ProcessPin);
		if (process_mode != applied_process) {
			uint64_t mask = process_mode;
			if (process_mode == 0) {
				mask = topology.process_mask;
			} else if (process_mode == 1) {
				mask = 0;
				size_t best = 0;
				for (size_t index = 0; index < topology.l3_masks.size(); index++) {
					if (mask == 0 || topology.l3_sizes[index] > topology.l3_sizes[best]) {
						best = index;
						mask = topology.l3_masks[index];
					}
				}
			}
			if (process_mode != 0 && topology.process_mask != 0) {
				mask &= topology.process_mask;
			}
			// Remembered whether or not it works: a refused mask is not retried every submission.
			applied_process = process_mode;
			if (process_mode != 0 && std::popcount(mask) < 4) {
				LOGF("ProcessPin: mode=%u mask=0x%016" PRIx64 " refused (fewer than 4 processors)\n",
				     process_mode, mask);
			} else if (mask != 0 &&
			           SetProcessAffinityMask(GetCurrentProcess(), static_cast<DWORD_PTR>(mask)) != FALSE) {
				g_process_pin_mask.store(process_mode == 0 ? 0 : mask, std::memory_order_relaxed);
				g_process_pin_epoch.fetch_add(1, std::memory_order_relaxed);
				LOGF("ProcessPin: mode=%u mask=0x%016" PRIx64 "\n", process_mode, mask);
			} else {
				LOGF("ProcessPin: mode=%u mask=0x%016" PRIx64 " failed\n", process_mode, mask);
			}
		}
	}
	if (const auto epoch = g_process_pin_epoch.load(std::memory_order_relaxed); epoch != applied_epoch) {
		// The process mask changed under this thread: whatever it had applied is gone.
		applied_epoch = epoch;
		applied_mode  = 0;
		applied_mask  = 0;
	}
	const auto  mode     = Common::Gates::Value(Common::Gates::Knob::DrawAheadPin);
	if (mode == 0) {
		if (applied_mode != 0) {
			const auto pinned       = g_process_pin_mask.load(std::memory_order_relaxed);
			if (const auto process_mask = pinned != 0 ? pinned : topology.process_mask; process_mask != 0) {
				SetThreadAffinityMask(GetCurrentThread(), static_cast<DWORD_PTR>(process_mask));
			}
			if (gpu_thread) {
				g_draw_ahead_gpu_mask.store(0, std::memory_order_relaxed);
			}
			LOGF("DrawAheadPin: %s released\n", gpu_thread ? "GuestGpu" : "DrawAhead");
			applied_mode = 0;
			applied_mask = 0;
		}
		return;
	}
	if (gpu_thread && mode == applied_mode) {
		return; // the GuestGpu thread keeps the group chosen when the knob changed
	}
	uint64_t mask = mode;
	if (mode == 1) {
		mask = 0;
		size_t best = 0;
		for (size_t index = 0; index < topology.l3_masks.size(); index++) {
			if (mask == 0 || topology.l3_sizes[index] > topology.l3_sizes[best]) {
				best = index;
				mask = topology.l3_masks[index];
			}
		}
	} else if (mode == 2) {
		if (gpu_thread) {
			const auto l3 = DrawAheadCurrentL3();
			mask          = l3 < topology.l3_masks.size() ? topology.l3_masks[l3] : 0;
			g_draw_ahead_gpu_mask.store(mask, std::memory_order_relaxed);
		} else {
			mask = g_draw_ahead_gpu_mask.load(std::memory_order_relaxed);
		}
	}
	const auto pinned = g_process_pin_mask.load(std::memory_order_relaxed);
	if (const auto process_mask = pinned != 0 ? pinned : topology.process_mask; process_mask != 0) {
		mask &= process_mask;
	}
	if (mask == 0 || (mode == applied_mode && mask == applied_mask)) {
		return; // unknown topology, the GuestGpu thread has not chosen yet, or nothing changed
	}
	// Remembered whether or not it works: a DrawAhead worker applies the knob on every task.
	applied_mode     = mode;
	applied_mask     = mask;
	const bool fixed = SetThreadAffinityMask(GetCurrentThread(), static_cast<DWORD_PTR>(mask)) != 0;
	LOGF("DrawAheadPin: %s mode=%u mask=0x%016" PRIx64 "%s\n", gpu_thread ? "GuestGpu" : "DrawAhead",
	     mode, mask, fixed ? "" : " failed");
#else
	(void)gpu_thread;
#endif
}

uint8_t DrawAheadGpuL3() {
	return g_draw_ahead_gpu_l3.load(std::memory_order_relaxed);
}

// Gate "recpin" (session 57, A4). The record thread of the GuestGpu scheduler reads the ring the
// GuestGpu thread writes and shares the head and tail lines with it, so it follows knob "dapin" the
// way a DrawAhead worker does: 1 = the L3 group with the largest cache, 2 = the mask the GuestGpu
// thread chose, other = a raw mask. Gate off, dapin=0 or no mask yet: back to the process mask (the
// one "procpin" set, else the start mask). Called by the record thread once per command buffer.
void DrawAheadApplyRecordPin(bool wanted) {
#if defined(_WIN32)
	thread_local uint64_t applied_mask  = 0; // 0: this thread runs on the process mask
	thread_local uint32_t applied_epoch = 0;
	const auto&           topology      = DrawAheadTopology();
	if (const auto epoch = g_process_pin_epoch.load(std::memory_order_relaxed); epoch != applied_epoch) {
		// SetProcessAffinityMask put every thread back on the new process mask.
		applied_epoch = epoch;
		applied_mask  = 0;
	}
	const auto mode = wanted ? Common::Gates::Value(Common::Gates::Knob::DrawAheadPin) : 0u;
	uint64_t   mask = 0;
	if (mode == 1) {
		size_t best = 0;
		for (size_t index = 0; index < topology.l3_masks.size(); index++) {
			if (mask == 0 || topology.l3_sizes[index] > topology.l3_sizes[best]) {
				best = index;
				mask = topology.l3_masks[index];
			}
		}
	} else if (mode == 2) {
		mask = g_draw_ahead_gpu_mask.load(std::memory_order_relaxed);
	} else if (mode != 0) {
		mask = mode;
	}
	const auto pinned       = g_process_pin_mask.load(std::memory_order_relaxed);
	const auto process_mask = pinned != 0 ? pinned : topology.process_mask;
	if (process_mask != 0) {
		mask &= process_mask;
	}
	if (mask == applied_mask) {
		return;
	}
	// Remembered whether or not it works, as DrawAheadApplyPin does.
	applied_mask = mask;
	if (mask == 0) {
		if (process_mask != 0) {
			SetThreadAffinityMask(GetCurrentThread(), static_cast<DWORD_PTR>(process_mask));
		}
		LOGF("DrawAheadPin: Record released\n");
		return;
	}
	const bool fixed = SetThreadAffinityMask(GetCurrentThread(), static_cast<DWORD_PTR>(mask)) != 0;
	LOGF("DrawAheadPin: Record mode=%u mask=0x%016" PRIx64 "%s\n", mode, mask, fixed ? "" : " failed");
#else
	(void)wanted;
#endif
}

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

	// Gate "daclass": static variants of programs whose plans are canonically equal
	// (CanonicalPlanBytes). Never freed: slots and source entries keep pointers to it.
	struct PlanClass {
		std::vector<uint8_t> bytes;
		uint64_t             hash = 0; // XXH3 of `bytes` | 1: the slot fingerprint in class mode
	};

	struct SourceEntry {
		explicit SourceEntry(ShaderRecompiler::IR::ResourcePlan plan)
		    : resource_plan(std::move(plan)) {}

		ShaderRecompiler::IR::ResourcePlan resource_plan;
		// ShaderTranslationCache::PlanFingerprint of the plan (| 1, 0 = not computed yet); only
		// the holder of PipelineCache::m_mutex computes and reads it.
		mutable uint64_t                   plan_fingerprint = 0;
		// Canonical class of the plan (ClassOf), same ownership as plan_fingerprint.
		mutable const PlanClass* plan_class = nullptr;
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
	[[gnu::noinline]] bool LoadFromTranslationCache(const ProgramKey& key,
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

	// Materialization memo (gate "srtmemo"). MaterializeResources is a pure function of the
	// resource plan, the user data registers, the shader base and the guest words it reads, and
	// all of those reads go through the two SrtRuntime callbacks. Recording them therefore gives a
	// witness: while every recorded address still holds its recorded value the walk would take the
	// same path and build the same snapshot, so the stored result may be handed out instead of
	// walking the plan again. Consecutive words of one page are checked with a single memcmp.
	struct MemoEntry {
		bool                  valid       = false;
		uint64_t              generation  = 0;
		const SourceEntry*    source      = nullptr;
		uint64_t              shader_base = 0;
		Witness               witness;
		// The snapshot carries the user data registers, which are the rest of the key.
		ShaderRecompiler::IR::ResourceSnapshot snapshot;
		Permutation*                           permutation        = nullptr;
		uint32_t                               push_data_start    = 0;
		uint32_t                               shader_data_dwords = 0;
		ShaderProgram                          handle {};
	};

	static constexpr size_t MemoSlots = 16384;

	std::vector<MemoEntry> memo = std::vector<MemoEntry>(MemoSlots);
	// Bumped when a source entry is dropped: the stored permutation pointers belong to one.
	uint64_t memo_generation = 1;

	static uint64_t MemoHash(const SourceEntry* source, uint64_t shader_base,
	                         std::span<const uint32_t> user_data) {
		const auto seed = (reinterpret_cast<uintptr_t>(source) * 0x9e3779b97f4a7c15ull) ^ shader_base;
		return XXH3_64bits_withSeed(user_data.data(), user_data.size_bytes(), seed);
	}

	[[gnu::noinline]] MemoEntry* MemoFind(const SourceEntry* source, uint64_t shader_base,
	                    std::span<const uint32_t> user_data) {
		auto& slot = memo[MemoHash(source, shader_base, user_data) % MemoSlots];
		if (!slot.valid || slot.generation != memo_generation || slot.source != source ||
		    slot.shader_base != shader_base ||
		    slot.snapshot.user_data.size() != user_data.size() ||
		    !std::equal(user_data.begin(), user_data.end(), slot.snapshot.user_data.begin())) {
			return nullptr;
		}
		return &slot;
	}

	[[gnu::noinline]] static bool MemoVerify(const MemoEntry& entry, ShaderReadCache& cache) {
		if (Common::FrameStats::Enabled()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SrtMemoReads, entry.witness.Words());
		}
		return VerifyWitness(entry.witness, cache);
	}

	static bool SameSnapshot(const ShaderRecompiler::IR::ResourceSnapshot& a,
	                         const ShaderRecompiler::IR::ResourceSnapshot& b) {
		return a.buffers == b.buffers && a.images == b.images && a.samplers == b.samplers &&
		       a.flattened_srt == b.flattened_srt && a.user_data == b.user_data &&
		       a.uniform_fill == b.uniform_fill;
	}

	// Gate "smemocheck": walk the plan anyway and report where the memo would have answered with
	// something else. Diagnostic only - the memo answer is still the one used, so what the run
	// shows is what the game would have been given.
	[[gnu::noinline]] void MemoCheck(const ProgramKey& key, const SourceEntry& entry,
	               const ShaderRecompiler::IR::SrtRuntime& runtime, const MemoEntry& memo_entry) {
		ShaderRecompiler::IR::ResourceSnapshot       fresh;
		ShaderRecompiler::IR::ResourceSpecialization fresh_specialization;
		const bool ok = ShaderRecompiler::IR::MaterializeResources(entry.resource_plan, runtime,
		                                                           fresh, fresh_specialization);
		const bool same = ok && SameSnapshot(fresh, memo_entry.snapshot) &&
		                  fresh_specialization == memo_entry.permutation->specialization;
		if (same) {
			memo_checks_ok++;
			return;
		}
		memo_checks_bad++;
		if (memo_checks_bad <= 40) {
			LOGF("SrtMemoVerify: MISMATCH hash=0x%016" PRIx64 " stage=%u materialized=%d "
			     "snapshot=%d specialization=%d (ok=%" PRIu64 " bad=%" PRIu64 ")\n",
			     key.hash, static_cast<uint32_t>(key.stage), ok ? 1 : 0,
			     ok && SameSnapshot(fresh, memo_entry.snapshot) ? 1 : 0,
			     ok && fresh_specialization == memo_entry.permutation->specialization ? 1 : 0,
			     memo_checks_ok, memo_checks_bad);
		}
	}

	uint64_t memo_checks_ok  = 0;
	uint64_t memo_checks_bad = 0;

	// Gate "snapkeep" (session 57, B4): per graphics stage (0 = vertex or mesh, 1 = pixel) the
	// snapshot and specialization storage Get works in. Only GetGraphicsPrograms passes an index,
	// and only the GuestGpu draw path calls it, so nothing else ever touches these.
	std::array<ShaderRecompiler::IR::ResourceSnapshot, 2>       kept_snapshots;
	std::array<ShaderRecompiler::IR::ResourceSpecialization, 2> kept_specializations;

	[[gnu::noinline]] void MemoStore(const SourceEntry* source, uint64_t shader_base, const SrtReadLog& log,
	               const ShaderRecompiler::IR::ResourceSnapshot& snapshot, Permutation* permutation,
	               ShaderProgram handle) {
		if (log.overflow || permutation == nullptr) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SrtMemoSkips, 1);
			return;
		}
		auto& slot = memo[MemoHash(source, shader_base, snapshot.user_data) % MemoSlots];
		slot.valid = false;
		slot.witness.Build(log);
		slot.snapshot           = snapshot;
		slot.source             = source;
		slot.shader_base        = shader_base;
		slot.permutation        = permutation;
		slot.handle             = handle;
		slot.push_data_start    = permutation->program.bindings.push_data_start_dword;
		slot.shader_data_dwords = permutation->program.bindings.ShaderDataDwords();
		slot.generation         = memo_generation;
		slot.valid              = true;
	}

	// Draw lookahead (gates "drawahead"/"dause", docs/parallel-draw-path.md M1). A slot holds one
	// materialization task and, once a worker has run it, its result and witness.
	// Ownership: the key fields are written only by the holder of PipelineCache::m_mutex while no
	// worker can touch the slot (state Empty, Ready or Failed). A worker claims a Queued slot with a
	// compare-exchange, writes only the result fields and publishes Ready or Failed; after that it
	// never touches the slot again, so the holder of m_mutex reads the result without a lock.
	enum AheadState : uint8_t { AheadEmpty, AheadQueued, AheadRunning, AheadReady, AheadFailed };

	struct AheadSlot {
		std::atomic<uint8_t> state {AheadEmpty};
		// Holder of m_mutex only (workers never read them): a draw took this result (da_unused counts
		// results that went without), and the stage it was queued for.
		uint8_t taken = 0;
		uint8_t pixel = 0;
		// Gate "daclass": the canonical class of the key (nullptr = keyed by plan fingerprint alone).
		const PlanClass* plan_class = nullptr;
		// key (holder of m_mutex); `source` is one entry with this plan, for the worker
		const SourceEntry*                                 source      = nullptr;
		uint64_t                                           fingerprint = 0;
		uint64_t                                           shader_base = 0;
		uint64_t                                           generation  = 0;
		uint64_t                                           walk        = 0;
		uint32_t                                           uses        = 0; // draws still to take it
		uint32_t                                           count       = 0;
		std::array<uint32_t, HW::UserSgprInfo::SGPRS_MAX> user_data {};
		// result (worker, published by the state)
		Witness                                      witness;
		ShaderRecompiler::IR::ResourceSnapshot       snapshot;
		ShaderRecompiler::IR::ResourceSpecialization specialization;

		[[nodiscard]] bool Matches(uint64_t key_fingerprint, const PlanClass* key_class, uint64_t base, uint64_t key_generation,
		                           std::span<const uint32_t> key_user_data) const {
			return fingerprint == key_fingerprint && plan_class == key_class && shader_base == base && generation == key_generation &&
			       count == key_user_data.size() &&
			       std::equal(key_user_data.begin(), key_user_data.end(), user_data.begin());
		}
	};

	// The source entry the draw path last used for a program: the static part of a program's key
	// (vertex fetch, pixel inputs, render target exports) depends on context state the PM4 walk
	// does not follow, so the walk asks which entry that program resolved to the last time. A wrong
	// guess costs a task whose result no draw matches.
	struct AheadHint {
		std::array<const SourceEntry*, 4> sources {}; // static variants seen, replaced in turn
		uint64_t                          base       = 0;
		uint64_t                          generation = 0;
		uint32_t                          count      = 0;
		uint32_t                          next       = 0; // variant slot replaced next
		ShaderType                        stage      = ShaderType::Unknown;
	};

	static constexpr size_t AheadSlotCount = 32768;
	static constexpr size_t AheadHintCount = 16384;
	static constexpr size_t AheadBatch     = 16;

	std::unique_ptr<AheadSlot[]>          ahead_slots; // allocated by the first queued walk
	std::array<AheadHint, AheadHintCount> ahead_hints {};
	uint64_t                              ahead_walk = 0;
	// The static variant a multi-variant program last ran with for given user data: which source
	// entry the walk should materialize a request for.
	struct AheadVariant {
		uint64_t           key    = 0;
		const SourceEntry* source = nullptr;
	};
	static constexpr size_t                     AheadVariantCount = 16384;
	std::array<AheadVariant, AheadVariantCount> ahead_variants {};

	// The user data is hashed once per request (the PM4 walk fills DrawAheadRequest::user_hash)
	// and once per draw stage; the two keys below mix that value with the plan fingerprint, the
	// shader base and the stage by integer math. Before this, a program with four static variants
	// ran XXH3 over the whole user-data block five times for one request - ~35k hashes a frame on
	// the critical thread in Sky Garden.
	static uint64_t UserDataHash(std::span<const uint32_t> user_data) {
		return XXH3_64bits_withSeed(user_data.data(), user_data.size_bytes(), 0);
	}

	static uint64_t SplitMix64(uint64_t value) {
		value += 0x9e3779b97f4a7c15ull;
		value = (value ^ (value >> 30u)) * 0xbf58476d1ce4e5b9ull;
		value = (value ^ (value >> 27u)) * 0x94d049bb133111ebull;
		return value ^ (value >> 31u);
	}

	static uint64_t AheadVariantKey(ShaderType stage, uint64_t base, uint64_t user_hash) {
		return SplitMix64(user_hash ^ (base * 0x9e3779b97f4a7c15ull) ^
		                  (static_cast<uint64_t>(stage) << 56u)) |
		       1u;
	}

	static uint64_t Fingerprint(const SourceEntry& source) {
		if (source.plan_fingerprint == 0) {
			source.plan_fingerprint = ShaderTranslationCache::PlanFingerprint(source.resource_plan) | 1u;
		}
		return source.plan_fingerprint;
	}

	static uint64_t AheadHash(uint64_t fingerprint, uint64_t shader_base, uint64_t user_hash) {
		return SplitMix64(user_hash ^ (fingerprint * 0x9e3779b97f4a7c15ull) ^ shader_base);
	}
	std::mutex                            ahead_mutex;
	std::condition_variable               ahead_cv;
	// Slot indices waiting for a worker. A fixed ring rather than std::deque: MSVC puts four
	// uint32_t in one heap block, so a Sky Garden frame's ~19k tasks cost ~4.7k allocations and
	// as many frees, taken and given back under this very lock - the samples of QueueAhead inside
	// ntdll. head and tail are free-running counters; tail - head is the fill, which can never
	// reach 2^32. A full ring drops the task exactly like a key whose slots are busy: the draw
	// materializes it itself.
	static constexpr uint32_t             AheadQueueSize   = 65536; // power of two
	std::unique_ptr<uint32_t[]>           ahead_queue;              // ahead_mutex
	uint32_t                              ahead_queue_head = 0;     // ahead_mutex, pop position
	uint32_t                              ahead_queue_tail = 0;     // ahead_mutex, push position
	bool                                  ahead_stop = false; // ahead_mutex
	std::vector<std::thread>              ahead_threads;

	static size_t AheadHintIndex(ShaderType stage, uint64_t base, uint32_t count) {
		return static_cast<size_t>((base >> 2u) ^ (base >> 17u) ^ (uint64_t {count} * 0x9e37u) ^
		                           (static_cast<uint64_t>(stage) << 11u)) &
		       (AheadHintCount - 1);
	}

	void AheadNote(ShaderType stage, uint64_t base, std::span<const uint32_t> user_data,
	               const SourceEntry* source) {
		const auto count = static_cast<uint32_t>(user_data.size());
		auto&      hint  = ahead_hints[AheadHintIndex(stage, base, count)];
		if (hint.sources[1] != nullptr && hint.base == base && hint.count == count &&
			!Common::Gates::Enabled(Common::Gates::Gate::DrawAheadClass) &&
		    hint.stage == stage && hint.generation == memo_generation) {
			const auto key = AheadVariantKey(stage, base, UserDataHash(user_data));
			ahead_variants[key % AheadVariantCount] = {key, source};
		}
		if (hint.base != base || hint.count != count || hint.stage != stage ||
		    hint.generation != memo_generation) {
			hint            = {};
			hint.sources[0] = source;
			hint.base       = base;
			hint.generation = memo_generation;
			hint.count      = count;
			hint.next       = 1;
			hint.stage      = stage;
			return;
		}
		if (std::find(hint.sources.begin(), hint.sources.end(), source) != hint.sources.end()) {
			return;
		}
		// Another static variant of the same program.
		Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadHintFlip, 1);
		hint.sources[hint.next % hint.sources.size()] = source;
		hint.next++;
	}

	// Canonical class of a source entry's plan (gate "daclass", counter da_fan_canon): built once per
	// entry by the holder of PipelineCache::m_mutex, by exact comparison of canonical bytes, so equal
	// pointers mean equal plans and a hash collision cannot merge two classes. Never freed.
	std::unordered_map<uint64_t, std::vector<std::unique_ptr<PlanClass>>> plan_classes;

	[[gnu::noinline]] const PlanClass* ClassOf(const SourceEntry& source) {
		if (source.plan_class != nullptr) {
			return source.plan_class;
		}
		namespace FS      = Common::FrameStats;
		const bool timed  = FS::Enabled();
		const auto t0     = timed ? FS::NowNs() : 0;
		auto       bytes  = CanonicalPlanBytes(source.resource_plan);
		const auto hash   = XXH3_64bits(bytes.data(), bytes.size()) | 1u;
		auto&      bucket = plan_classes[hash];
		const PlanClass* found = nullptr;
		for (const auto& candidate: bucket) {
			if (candidate->bytes == bytes) {
				found = candidate.get();
				break;
			}
		}
		if (found == nullptr) {
			auto created   = std::make_unique<PlanClass>();
			created->bytes = std::move(bytes);
			created->hash  = hash;
			found          = created.get();
			bucket.push_back(std::move(created));
			FS::Add(FS::Counter::DrawAheadClasses, 1);
		} else {
			FS::Add(FS::Counter::DrawAheadClassShared, 1);
		}
		source.plan_class = found;
		if (timed) {
			FS::Add(FS::Counter::DrawAheadClassNs, FS::NowNs() - t0);
		}
		return found;
	}

	void AheadStartThreads(uint32_t wanted) {
		if (ahead_threads.size() >= wanted) {
			return;
		}
		{
			std::lock_guard<std::mutex> lock(ahead_mutex);
			if (ahead_stop) {
				return; // shutting down: nobody would join a new thread
			}
		}
		while (ahead_threads.size() < wanted) {
			const auto index = static_cast<uint32_t>(ahead_threads.size());
			ahead_threads.emplace_back([this, index] {
				SetThreadDescription(GetCurrentThread(), L"DrawAhead");
				AheadWorker(index);
			});
		}
	}

	void AheadStopThreads() {
		{
			std::lock_guard<std::mutex> lock(ahead_mutex);
			ahead_stop = true;
		}
		ahead_cv.notify_all();
		for (auto& thread: ahead_threads) {
			thread.join();
		}
		ahead_threads.clear();
	}

	struct AheadQueueStats {
		uint64_t no_hint = 0;
		uint64_t no_plan = 0;
		uint64_t present = 0;
		uint64_t refresh = 0;
		uint64_t busy    = 0;
		uint64_t predicted = 0;
		uint64_t probes    = 0; // slots looked at, the cost of the table itself
		uint64_t requests     = 0; // requests with a hint
		uint64_t fan          = 0; // distinct fingerprints among their variants
		uint64_t fan_canon    = 0; // distinct canonical classes among them
		uint64_t unused       = 0; // results dropped without a take
		uint64_t unused_pixel = 0;
	};

	// Holder of m_mutex: queue one request for one source entry, or find it already queued.
	void QueueAheadSource(const SourceEntry* source, const PlanClass* plan_class,
						  const PipelineCache::DrawAheadRequest& request,
	                      AheadQueueStats& stats, std::vector<uint32_t>& batch) {
		if (source->resource_plan.srt_compiled == nullptr) {
			stats.no_plan++;
			return;
		}
		const auto fingerprint = plan_class != nullptr ? plan_class->hash : Fingerprint(*source);
		const std::span<const uint32_t> user_data(request.user_data.data(), request.count);
		const auto hash        = AheadHash(fingerprint, request.base, request.user_hash);
		AheadSlot* victim      = nullptr;
		uint32_t   victim_rank = UINT32_MAX;
		for (size_t probe = 0; probe < 2; probe++) {
			stats.probes++;
			auto&      slot  = ahead_slots[(hash + probe) & (AheadSlotCount - 1)];
			const auto state = slot.state.load(std::memory_order_acquire);
			if (state != AheadEmpty && slot.Matches(fingerprint, plan_class, request.base, memo_generation, user_data)) {
				if (slot.walk == ahead_walk) {
					slot.uses += request.uses;
					stats.present++;
				} else if (state == AheadReady || state == AheadFailed) {
					// Answered by an older walk from guest words that may have moved since:
					// answer it again for this walk.
					slot.walk = ahead_walk;
					slot.uses = request.uses;
					slot.state.store(AheadQueued, std::memory_order_release);
					if (slot.taken == 0) {
						stats.unused++;
						stats.unused_pixel += slot.pixel;
					}
					slot.taken = 0;
					slot.pixel = request.pixel ? 1u : 0u;
					batch.push_back(static_cast<uint32_t>(&slot - ahead_slots.get()));
					stats.refresh++;
				} else {
					slot.walk = ahead_walk; // still queued or running: fresh enough
					slot.uses = request.uses;
					stats.present++;
				}
				return;
			}
			// Free first, then work of an older walk; never work of this walk.
			uint32_t rank = UINT32_MAX;
			if (state == AheadEmpty || state == AheadFailed) {
				rank = 0;
			} else if (slot.walk != ahead_walk && state == AheadReady) {
				rank = 1;
			} else if (slot.walk != ahead_walk && state == AheadQueued) {
				rank = 2; // cancelled below if chosen
			}
			if (rank < victim_rank) {
				victim      = &slot;
				victim_rank = rank;
			}
		}
		if (victim != nullptr && victim_rank == 2) {
			auto expected = static_cast<uint8_t>(AheadQueued);
			if (!victim->state.compare_exchange_strong(expected, AheadEmpty, std::memory_order_acq_rel)) {
				victim = nullptr; // a worker claimed it meanwhile
			}
		}
		if (victim == nullptr) {
			stats.busy++;
			return;
		}
		victim->source      = source;
		victim->fingerprint = fingerprint;
		victim->shader_base = request.base;
		victim->generation  = memo_generation;
		victim->walk        = ahead_walk;
		victim->uses        = request.uses;
		victim->count       = request.count;
		std::copy(user_data.begin(), user_data.end(), victim->user_data.begin());
		{
			const auto previous = victim->state.load(std::memory_order_acquire);
			if ((previous == AheadReady || previous == AheadFailed) && victim->taken == 0) {
				stats.unused++;
				stats.unused_pixel += victim->pixel;
			}
		}
		victim->taken      = 0;
		victim->pixel      = request.pixel ? 1u : 0u;
		victim->plan_class = plan_class;
		victim->state.store(AheadQueued, std::memory_order_release);
		batch.push_back(static_cast<uint32_t>(victim - ahead_slots.get()));
	}

	// Holder of m_mutex.
	void QueueAhead(std::span<const PipelineCache::DrawAheadRequest> requests, bool first_batch) {
		namespace FS     = Common::FrameStats;
		const auto wanted = Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads);
		if (wanted == 0) {
			return;
		}
		if (ahead_slots == nullptr) {
			// Both before any worker exists: a worker reads the ring under ahead_mutex and would
			// otherwise have to check the pointer on every wake-up.
			ahead_slots = std::make_unique<AheadSlot[]>(AheadSlotCount);
			ahead_queue = std::make_unique<uint32_t[]>(AheadQueueSize);
		}
		AheadStartThreads(wanted);
		if (FS::Enabled()) {
			g_draw_ahead_gpu_l3.store(DrawAheadCurrentL3(), std::memory_order_relaxed);
		}
		if (first_batch) {
			ahead_walk++;
		}
		AheadQueueStats                    stats;
		thread_local std::vector<uint32_t> batch;
		const bool class_mode = Common::Gates::Enabled(Common::Gates::Gate::DrawAheadClass);
		const bool counting   = FS::Enabled();
		batch.clear();
		for (const auto& request: requests) {
			const auto  stage = request.pixel ? ShaderType::Pixel : ShaderType::Vertex;
			const auto& hint  = ahead_hints[AheadHintIndex(stage, request.base, request.count)];
			if (request.count > HW::UserSgprInfo::SGPRS_MAX || hint.sources[0] == nullptr ||
			    hint.stage != stage || hint.base != request.base || hint.count != request.count ||
			    hint.generation != memo_generation) {
				stats.no_hint++;
				continue;
			}
			// Session 56: the distinct plan identities among the static variants the hint holds - by
			// fingerprint (one task each without the gate) and by canonical class (gate "daclass").
			stats.requests++;
			std::array<const SourceEntry*, 4> print_sources {};
			std::array<const SourceEntry*, 4> class_sources {};
			std::array<const PlanClass*, 4>   classes {};
			size_t                            prints      = 0;
			size_t                            class_count = 0;
			for (const auto* source: hint.sources) {
				if (source == nullptr) {
					continue;
				}
				const auto print   = Fingerprint(*source);
				size_t     earlier = 0;
				while (earlier < prints && Fingerprint(*print_sources[earlier]) != print) {
					earlier++;
				}
				if (earlier == prints) {
					print_sources[prints++] = source;
				}
				if (class_mode || counting) {
					const auto* plan_class = ClassOf(*source);
					size_t      index      = 0;
					while (index < class_count && classes[index] != plan_class) {
						index++;
					}
					if (index == class_count) {
						classes[class_count]       = plan_class;
						class_sources[class_count] = source;
						class_count++;
					} else if (class_sources[index]->resource_plan.srt_compiled == nullptr) {
						// Any member computes the result; prefer one whose plan is compiled.
						class_sources[index] = source;
					}
				}
			}
			stats.fan += prints;
			stats.fan_canon += class_count;
			if (class_mode) {
				for (size_t index = 0; index < class_count; index++) {
					QueueAheadSource(class_sources[index], classes[index], request, stats, batch);
				}
				continue;
			}
			if (hint.sources[1] != nullptr) {
				const auto  key       = AheadVariantKey(stage, request.base, request.user_hash);
				const auto& predicted = ahead_variants[key % AheadVariantCount];
				if (predicted.key == key &&
				    std::find(hint.sources.begin(), hint.sources.end(), predicted.source) !=
				        hint.sources.end()) {
					QueueAheadSource(predicted.source, nullptr, request, stats, batch);
					stats.predicted++;
					continue;
				}
			}
			for (size_t variant = 0; variant < hint.sources.size(); variant++) {
				const auto* source = hint.sources[variant];
				if (source == nullptr) {
					continue;
				}
				// Variants with the same plan share one task.
				const auto fingerprint = Fingerprint(*source);
				bool       shared      = false;
				for (size_t earlier = 0; earlier < variant; earlier++) {
					shared |= hint.sources[earlier] != nullptr &&
					          Fingerprint(*hint.sources[earlier]) == fingerprint;
				}
				if (!shared) {
					QueueAheadSource(source, nullptr, request, stats, batch);
				}
			}
		}
		size_t dropped = 0;
		if (!batch.empty()) {
			{
				std::lock_guard<std::mutex> lock(ahead_mutex);
				for (const auto index: batch) {
					if (ahead_queue_tail - ahead_queue_head >= AheadQueueSize) {
						// The ring is full: hand the slot back, the draw will materialize it
						// itself. A worker that has already claimed it wins the exchange.
						auto expected = static_cast<uint8_t>(AheadQueued);
						ahead_slots[index].state.compare_exchange_strong(
						    expected, AheadEmpty, std::memory_order_acq_rel);
						dropped++;
						continue;
					}
					ahead_queue[ahead_queue_tail & (AheadQueueSize - 1)] = index;
					ahead_queue_tail++;
				}
			}
			// One waiter is enough: a worker that takes work hands the wake on while the ring is
			// not empty (AheadWorker). A worker the knob has made ineligible goes back to sleep
			// without handing it on, so wake everybody while such a thread exists.
			if (ahead_threads.size() > wanted) {
				ahead_cv.notify_all();
			} else {
				ahead_cv.notify_one();
			}
		}
		stats.busy += dropped;
		if (FS::Enabled()) {
			const auto queued = batch.size() - stats.refresh;
			FS::Add(FS::Counter::DrawAheadQueued, queued > dropped ? queued - dropped : 0);
			FS::Add(FS::Counter::DrawAheadProbes, stats.probes);
			FS::Add(FS::Counter::DrawAheadNoHint, stats.no_hint);
			FS::Add(FS::Counter::DrawAheadNoPlan, stats.no_plan);
			FS::Add(FS::Counter::DrawAheadRefresh, stats.refresh);
			FS::Add(FS::Counter::DrawAheadPresent, stats.present);
			FS::Add(FS::Counter::DrawAheadBusy, stats.busy);
			FS::Add(FS::Counter::DrawAheadPredicted, stats.predicted);
			FS::Add(FS::Counter::DrawAheadRequests, stats.requests);
			FS::Add(FS::Counter::DrawAheadFan, stats.fan);
			FS::Add(FS::Counter::DrawAheadFanCanon, stats.fan_canon);
			FS::Add(FS::Counter::DrawAheadUnused, stats.unused);
			FS::Add(FS::Counter::DrawAheadUnusedPixel, stats.unused_pixel);
		}
	}

	void AheadWorker(uint32_t index) {
		std::array<uint32_t, AheadBatch> taken {};
		for (;;) {
			size_t count    = 0;
			bool   more     = false;
			bool   wake_all = false;
			{
				std::unique_lock<std::mutex> lock(ahead_mutex);
				ahead_cv.wait(lock, [&] {
					return ahead_stop ||
					       (ahead_queue_tail != ahead_queue_head &&
					        index < Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads));
				});
				if (ahead_stop) {
					return;
				}
				while (count < taken.size() && ahead_queue_tail != ahead_queue_head) {
					taken[count++] = ahead_queue[ahead_queue_head & (AheadQueueSize - 1)];
					ahead_queue_head++;
				}
				more = ahead_queue_tail != ahead_queue_head;
				wake_all =
				    ahead_threads.size() > Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads);
			}
			if (more) {
				// The producer wakes one worker per batch: pass the wake on, outside the lock, so
				// the others do not sleep through a ring that still holds work. A worker the knob
				// has made ineligible would go back to sleep without handing it on, so while such
				// a thread exists everybody is woken, exactly as the producer does.
				if (wake_all) {
					ahead_cv.notify_all();
				} else {
					ahead_cv.notify_one();
				}
			}
			for (size_t i = 0; i < count; i++) {
				AheadRun(ahead_slots[taken[i]]);
			}
		}
	}

	[[gnu::noinline]] static void AheadRun(AheadSlot& slot) {
		DrawAheadApplyPin(false); // knob "dapin"
		namespace FS  = Common::FrameStats;
		auto expected = static_cast<uint8_t>(AheadQueued);
		if (!slot.state.compare_exchange_strong(expected, AheadRunning, std::memory_order_acq_rel)) {
			return; // cancelled, or claimed through an older queue entry
		}
		const bool              timed = FS::Enabled();
		const auto              t0    = timed ? FS::NowNs() : 0;
		thread_local SrtReadLog log;
		log.entries.clear();
		log.overflow = false;
		ShaderReadCache cache;
		cache.log = &log;
		const ShaderRecompiler::IR::SrtRuntime runtime {
		    .user_data                  = std::span<const uint32_t>(slot.user_data.data(), slot.count),
		    .shader_base                = slot.shader_base,
		    .read_memory                = ReadShaderLiveMemory,
		    .userdata                   = &cache,
		    .read_specialization_memory = ReadShaderAheadClean,
		};
		const bool ok = ShaderRecompiler::IR::MaterializeResources(
		                    slot.source->resource_plan, runtime, slot.snapshot, slot.specialization) &&
		                !log.overflow;
		if (ok) {
			slot.witness.Build(log);
		}
		if (timed) {
			FS::Add(ok ? FS::Counter::DrawAheadDone : FS::Counter::DrawAheadFailed, 1);
			FS::Add(FS::Counter::DrawAheadWorkerNs, FS::NowNs() - t0);
			const auto l3     = DrawAheadCurrentL3();
			const auto gpu_l3 = g_draw_ahead_gpu_l3.load(std::memory_order_relaxed);
			if (l3 != 0xffu && gpu_l3 != 0xffu && l3 != gpu_l3) {
				FS::Add(FS::Counter::DrawAheadCrossCcd, 1);
			}
		}
		slot.state.store(ok ? AheadReady : AheadFailed, std::memory_order_release);
	}

	// A lookahead result copied out of its slot. With `kept` (gate "snapkeep") the destination is
	// the kept storage of the draw's stage, whose capacity the vector copies reuse: no allocation
	// here, and the worker's blocks stay in the slot for the worker to free. Without it these are
	// the two assignments the callers made before.
	static void CopyAheadResult(const AheadSlot& slot, ShaderRecompiler::IR::ResourceSnapshot& resources,
	                            ShaderRecompiler::IR::ResourceSpecialization& specialization,
	                            bool kept, bool last_use) {
		// Gate "snapdiff" says something only with `kept`: there the destination still holds this
		// stage's snapshot of the previous draw, which half of a frame's descriptor sets repeat
		// (session 57, E9). A fresh local is empty and every comparison against it would fail.
		const bool diff = kept && Common::Gates::Enabled(Common::Gates::Gate::SnapshotDiff);
		if (kept && Common::FrameStats::Enabled()) {
			CopyAheadResultCounted(slot, resources, specialization, diff, last_use);
			return;
		}
		CopySnapshot(slot.snapshot, resources, diff, nullptr);
		CopySpecialization(slot.specialization, specialization, diff, nullptr);
	}

	// The same copy with the session 58 ceiling counters around it: how much it moves, how much of
	// that the destination already held (what "snapdiff" leaves out) and whether it was a slot's
	// last use (what "snapswap" turns into two swaps). Out of line - it runs under FRAME_TRACE only,
	// and the capacities have to be read before the copy changes them.
	[[gnu::noinline]] static void
	CopyAheadResultCounted(const AheadSlot& slot, ShaderRecompiler::IR::ResourceSnapshot& resources,
	                       ShaderRecompiler::IR::ResourceSpecialization& specialization, bool diff,
	                       bool last_use) {
		namespace FS     = Common::FrameStats;
		const auto& from = slot.snapshot;
		const bool  grow = resources.buffers.capacity() < from.buffers.size() ||
		                  resources.images.capacity() < from.images.size() ||
		                  resources.samplers.capacity() < from.samplers.size() ||
		                  resources.flattened_srt.capacity() < from.flattened_srt.size() ||
		                  resources.user_data.capacity() < from.user_data.size() ||
		                  specialization.buffers.capacity() < slot.specialization.buffers.size() ||
		                  specialization.images.capacity() < slot.specialization.images.size();
		const bool        same_fill = resources.uniform_fill == from.uniform_fill;
		SnapshotCopyStats stats;
		CopySnapshot(from, resources, diff, &stats);
		CopySpecialization(slot.specialization, specialization, diff, &stats);
		FS::Add(FS::Counter::SnapKeepCopies, 1);
		if (grow) {
			FS::Add(FS::Counter::SnapKeepGrows, 1);
		}
		FS::Add(FS::Counter::SnapCopyBytes, stats.bytes);
		FS::Add(FS::Counter::SnapCopySameBytes, stats.same_bytes);
		FS::Add(FS::Counter::SnapCopyVectors, stats.vectors);
		FS::Add(FS::Counter::SnapCopySameVectors, stats.same_vectors);
		if (same_fill && stats.same_vectors == stats.vectors) {
			FS::Add(FS::Counter::SnapCopyUnchanged, 1);
		}
		if (last_use) {
			FS::Add(FS::Counter::SnapLastUseCopies, 1);
			FS::Add(FS::Counter::SnapLastUseBytes, stats.bytes);
		}
	}

	// Holder of m_mutex, on a draw: the worker result for this program and user data, if its
	// witness still holds.
	[[gnu::noinline]] bool AheadTake(const SourceEntry& source, const ShaderParams& params,
	                                 ShaderReadCache&                              cache,
	                                 ShaderRecompiler::IR::ResourceSnapshot&       resources,
	                                 ShaderRecompiler::IR::ResourceSpecialization& specialization,
	                                 bool kept = false) {
		namespace FS = Common::FrameStats;
		if (params.user_data.size() > HW::UserSgprInfo::SGPRS_MAX || ahead_slots == nullptr) {
			return false;
		}
		const PlanClass* plan_class =
			Common::Gates::Enabled(Common::Gates::Gate::DrawAheadClass) ? ClassOf(source) : nullptr;
		const auto fingerprint = plan_class != nullptr ? plan_class->hash : Fingerprint(source);
		const auto hash = AheadHash(fingerprint, params.Base(), UserDataHash(params.user_data));
		// Handed to the counters once, on the way out: this function leaves from six places, and
		// an Add per probe (~16k a frame) would have cost more than it measures.
		size_t probes = 2;
		struct ProbeCounter {
			const size_t& probes;
			~ProbeCounter() {
				if (Common::FrameStats::Enabled()) {
					Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadProbes, probes);
				}
			}
		} probe_counter {probes};
		for (size_t probe = 0; probe < 2; probe++) {
			auto& slot = ahead_slots[(hash + probe) & (AheadSlotCount - 1)];
			if (!slot.Matches(fingerprint, plan_class, params.Base(), memo_generation, params.user_data)) {
				continue;
			}
			probes     = probe + 1;
			auto state = slot.state.load(std::memory_order_acquire);
			if (state == AheadQueued) {
				if (slot.uses > 1) {
					slot.uses--; // later draws of this walk still want it
				} else {
					// Nobody will need it after this draw: let the workers skip it.
					auto expected = static_cast<uint8_t>(AheadQueued);
					slot.state.compare_exchange_strong(expected, AheadEmpty, std::memory_order_acq_rel);
				}
				FS::Add(FS::Counter::DrawAheadLate, 1);
				return false;
			}
			if (state == AheadRunning) {
				slot.uses -= slot.uses != 0 ? 1u : 0u;
				FS::Add(FS::Counter::DrawAheadLate, 1);
				return false;
			}
			if (state != AheadReady) {
				break;
			}
			if (Common::Gates::Enabled(Common::Gates::Gate::DrawAheadPrefetch)) {
				// A worker built these, usually on another core: start loading the witness for
				// the comparison below and the snapshot for this draw's bindings (session 56:
				// their first touches in PrepareBindings, FindBuffers, ResolveTexture,
				// StreamBuffer::Copy and ~ResourceSnapshot were ~5 % of the thread).
				PrefetchVectorData(slot.witness.live_runs);
				PrefetchVectorData(slot.witness.live_values);
				PrefetchVectorData(slot.witness.clean_runs);
				PrefetchVectorData(slot.witness.clean_values);
				PrefetchVectorData(slot.snapshot.buffers);
				PrefetchVectorData(slot.snapshot.images);
				PrefetchVectorData(slot.snapshot.samplers);
				PrefetchVectorData(slot.snapshot.flattened_srt);
				PrefetchVectorData(slot.snapshot.user_data);
				PrefetchVectorData(slot.specialization.buffers);
				PrefetchVectorData(slot.specialization.images);
			}
			if (FS::Enabled()) {
				FS::Add(FS::Counter::DrawAheadWords, slot.witness.Words());
				FS::Add(FS::Counter::DrawAheadCleanWords, slot.witness.clean_values.size());
				FS::Add(FS::Counter::DrawAheadRuns, slot.witness.Runs());
			}
			if (!VerifyWitness(slot.witness, cache)) {
				FS::Add(slot.walk == ahead_walk ? FS::Counter::DrawAheadStale
				                                : FS::Counter::DrawAheadStaleOld,
				        1);
				Common::DrawStat::Mark(Common::DrawStat::M1);
				// Guest words moved since the worker read them: no later draw can use it either.
				slot.uses = 0;
				slot.state.store(AheadEmpty, std::memory_order_release);
				return false;
			}
			if (slot.uses > 1) {
				slot.uses--;
				CopyAheadResult(slot, resources, specialization, kept, false);
			} else {
				// The last draw of this walk that asked for it: take the vectors, and retire the
				// slot, which no longer holds a result.
				// Gate "snapkeep" copies too: its destination already has the capacity (da_clone
				// then counts these copies as well). Gate "snapswap" takes the swap even then: the
				// slot is retired here under m_mutex, and the worker that materializes into it next
				// move-assigns over its vectors, so the kept storage handed over is freed there
				// exactly like the worker's own blocks are today. What it trades away is a
				// destination that stayed hot across draws - the same trade "daclone" measures.
				const bool clone =
				    (kept && !Common::Gates::Enabled(Common::Gates::Gate::SnapshotSwap)) ||
				    Common::Gates::Enabled(Common::Gates::Gate::DrawAheadClone);
				if (clone) {
					// Gate "daclone": copy on this thread and leave the worker's vectors in the
					// slot, so they are freed by the worker that allocated them when it
					// materializes into this slot again, not by the draw path after the draw (a
					// cross-thread HeapFree of cold blocks). The slot keeps that memory until then.
					CopyAheadResult(slot, resources, specialization, kept, true);
					FS::Add(FS::Counter::DrawAheadClones, 1);
				} else {
					std::swap(resources, slot.snapshot);
					std::swap(specialization, slot.specialization);
				}
				slot.uses = 0;
				slot.state.store(AheadEmpty, std::memory_order_release);
				FS::Add(FS::Counter::DrawAheadMoves, 1);
			}
			slot.taken = 1;
			Common::DrawStat::Mark(Common::DrawStat::M1);
			FS::Add(FS::Counter::DrawAheadHits, 1);
			return true;
		}
		FS::Add(FS::Counter::DrawAheadMisses, 1);
		return false;
	}

	// Gate "smemocheck" with a lookahead hit: walk the plan anyway and report a different answer.
	[[gnu::noinline]] void AheadCheck(const ProgramKey& key, const SourceEntry& entry,
	                                  const ShaderRecompiler::IR::SrtRuntime&             runtime,
	                                  const ShaderRecompiler::IR::ResourceSnapshot&       resources,
	                                  const ShaderRecompiler::IR::ResourceSpecialization& specialization) {
		ShaderRecompiler::IR::ResourceSnapshot       fresh;
		ShaderRecompiler::IR::ResourceSpecialization fresh_specialization;
		const bool ok = ShaderRecompiler::IR::MaterializeResources(entry.resource_plan, runtime, fresh,
		                                                           fresh_specialization);
		const bool same_snapshot       = ok && SameSnapshot(fresh, resources);
		const bool same_specialization = ok && fresh_specialization == specialization;
		if (same_snapshot && same_specialization) {
			memo_checks_ok++;
			return;
		}
		memo_checks_bad++;
		if (memo_checks_bad <= 40) {
			LOGF("DrawAheadVerify: MISMATCH hash=0x%016" PRIx64 " stage=%u materialized=%d "
			     "snapshot=%d specialization=%d (ok=%" PRIu64 " bad=%" PRIu64 ")\n",
			     key.hash, static_cast<uint32_t>(key.stage), ok ? 1 : 0, same_snapshot ? 1 : 0,
			     same_specialization ? 1 : 0, memo_checks_ok, memo_checks_bad);
		}
	}

	// tolerant: the PM4 lookahead reads guest memory that may not be final yet; a resource plan
	// that does not materialize returns an empty program instead of stopping the emulator.
	template <typename InputInfo>
	ShaderProgram Get(const ShaderParams& params, InputInfo& input_info,
	                  uint32_t& push_data_cursor, bool tolerant = false, int kept = -1) {
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
		static const bool dump_gcn = [] {
			const auto* value = std::getenv("KYTY_DUMP_GCN");
			return value != nullptr && value[0] != '0';
		}();
		if (!tolerant && (register_trace || dump_gcn) &&
		    first_used.emplace(static_cast<uint32_t>(stage), params.hash).second) {
			if (register_trace) {
				LOGF("ShaderFirstUse: hash=%016" PRIx64 " stage=%u words=%zu ud=%zu host_us=%" PRIu64 "\n",
				     params.hash, static_cast<uint32_t>(stage), params.code.size(), params.user_data.size(), HostMicros());
			}
			DumpShaderGcn(stage, params.hash, params.code);
		}
		auto                                         entry = programs.find(lookup_key);
		if (entry == programs.end()) {
			Common::DrawStat::Mark(Common::DrawStat::ObjNew);
			LibKernel::KernelTimeFreezeScope load_freeze;
			const auto                       load_begin = HostMicros();
			if (LoadFromTranslationCache(lookup_key, entry) && AvTraceEnabled()) {
				LOGF("AvTrace: shader-cache load hash=0x%016" PRIx64 " permutations=%zu us=%" PRIu64
				     "\n",
				     params.hash, entry->second.permutations.size(), HostMicros() - load_begin);
			}
		}
		lap.Mark(Common::FrameStats::Counter::ProgKeyNs);
		// Gate "snapkeep" (kept >= 0): the stage's kept storage instead of fresh locals. Every path
		// below overwrites both before reading them (lookahead copy, MaterializeResources, the reset
		// on a dropped plan, or Compile's own materialization when no entry exists).
		ShaderRecompiler::IR::ResourceSnapshot       local_resources;
		ShaderRecompiler::IR::ResourceSpecialization local_specialization;
		auto& resources = kept >= 0 ? kept_snapshots[static_cast<size_t>(kept)] : local_resources;
		auto& specialization =
		    kept >= 0 ? kept_specializations[static_cast<size_t>(kept)] : local_specialization;
		ShaderReadCache                              read_cache;
		const ShaderRecompiler::IR::SrtRuntime       runtime {
		    .user_data                  = params.user_data,
		    .shader_base                = params.Base(),
		    .read_memory                = ReadShaderLiveMemory,
		    .userdata                   = &read_cache,
		    .read_specialization_memory = ReadShaderGuestMemory,
		};
		bool ahead_hit = false;
		if (entry != programs.end() && (stage == ShaderType::Vertex || stage == ShaderType::Pixel) &&
		    Common::Gates::Enabled(Common::Gates::Gate::DrawAhead)) {
			AheadNote(stage, params.Base(), params.user_data, &entry->second);
			if (Common::Gates::Enabled(Common::Gates::Gate::DrawAheadUse)) {
				// Two rdtsc per stage, ~19k a frame in Sky Garden: only pay them while the
				// counters are being collected.
				const bool timed      = Common::FrameStats::Enabled();
				const auto take_begin = timed ? Common::FrameStats::NowNs() : 0;
				ahead_hit = AheadTake(entry->second, params, read_cache, resources, specialization,
				                      kept >= 0);
				if (timed) {
					Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadTakeNs,
					                        Common::FrameStats::NowNs() - take_begin);
				}
				if (ahead_hit && Common::Gates::Enabled(Common::Gates::Gate::SrtMemoCheck)) {
					AheadCheck(lookup_key, entry->second, runtime, resources, specialization);
				}
			}
		}
		const bool memo_enabled =
		    !ahead_hit && Common::Gates::Enabled(Common::Gates::Gate::SrtMemo);
		SrtReadLog memo_log;
		if (memo_enabled && entry != programs.end()) {
			auto* memo_entry = MemoFind(&entry->second, params.Base(), params.user_data);
			if (memo_entry != nullptr && MemoVerify(*memo_entry, read_cache) &&
			    memo_entry->push_data_start ==
			        ShaderRecompiler::IR::PushData::StartFor(push_data_cursor,
			                                                 memo_entry->shader_data_dwords)) {
				if (Common::Gates::Enabled(Common::Gates::Gate::SrtMemoCheck)) {
					MemoCheck(lookup_key, entry->second, runtime, *memo_entry);
				}
				input_info.stage.program   = &memo_entry->permutation->program;
				if (kept >= 0) {
					// Through the kept storage, which then moves into the input info like below.
					// Gate "snapdiff" holds here for the same reason as on the lookahead path; the
					// ceiling counters cover that path only, where the default configuration copies.
					CopySnapshot(memo_entry->snapshot, resources,
					             Common::Gates::Enabled(Common::Gates::Gate::SnapshotDiff), nullptr);
					input_info.stage.resources = std::move(resources);
				} else {
					input_info.stage.resources = memo_entry->snapshot;
				}
				memo_entry->permutation->program.bindings.AdvancePushData(push_data_cursor);
				Common::FrameStats::Add(Common::FrameStats::Counter::SrtMemoHits, 1);
				lap.Mark(Common::FrameStats::Counter::ProgMaterializeNs);
				return memo_entry->handle;
			}
			// A key that is not stored at all, against one whose recorded words have changed
			// (or whose push data no longer lines up): the two say different things about why
			// the frame's materializations have to run.
			Common::FrameStats::Add(memo_entry == nullptr
			                            ? Common::FrameStats::Counter::SrtMemoMisses
			                            : Common::FrameStats::Counter::SrtMemoStale,
			                        1);
			read_cache.log = &memo_log;
		}
		if (entry != programs.end() && !ahead_hit &&
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
			// Not freed: a lookahead worker may still be materializing with its plan.
			retired_sources.push_back(programs.extract(entry));
			memo_generation++; // the memo holds permutation pointers of the dropped entry
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
				if (memo_enabled) {
					MemoStore(&entry->second, params.Base(), memo_log, resources, &*permutation,
					          permutation->handle);
				}
				input_info.stage = {.program   = &permutation->program,
				                    .resources = std::move(resources)};
				permutation->program.bindings.AdvancePushData(push_data_cursor);
				lap.Mark(Common::FrameStats::Counter::ProgPermNs);
				return permutation->handle;
			}
		}

		Common::DrawStat::Mark(Common::DrawStat::ObjNew);
		return Compile(params, input_info, push_data_cursor, tolerant, stage, entry, runtime,
		               resources, specialization);
	}

	// The cold half of Get: translate the shader, or add a permutation of an already translated
	// one. Kept out of line because its inlined callees (translation, SPIR-V emission, the
	// translation cache) reserve tens of kilobytes of stack, and Get itself runs on guest threads
	// whose stacks are small.
	template <typename InputInfo>
	[[gnu::noinline]] ShaderProgram
	Compile(const ShaderParams& params, InputInfo& input_info, uint32_t& push_data_cursor,
	        bool tolerant, ShaderType stage,
	        typename std::unordered_map<ProgramKey, SourceEntry, ProgramKeyHash>::iterator entry,
	        const ShaderRecompiler::IR::SrtRuntime&       runtime,
	        ShaderRecompiler::IR::ResourceSnapshot&       resources,
	        ShaderRecompiler::IR::ResourceSpecialization& specialization) {
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
		AheadStopThreads();
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
	std::vector<std::unordered_map<ProgramKey, SourceEntry, ProgramKeyHash>::node_type> retired_sources;
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
	// Gate "snapkeep" (session 57, B4; needs "drawstate", which makes these input infos the draw
	// state reused across draws): their snapshots still hold the storage of the previous draw.
	// Take it back before PrepareProgram resets them, so Get copies into warm capacity and the end
	// of the draw frees nothing. Outside m_mutex: only this (GuestGpu draw) path uses the storage.
	const bool keep_snapshots = Common::Gates::Enabled(Common::Gates::Gate::SnapshotKeep) &&
	                            Common::Gates::Enabled(Common::Gates::Gate::DrawStateReuse);
	if (keep_snapshots) {
		std::swap(m_program_cache->kept_snapshots[0], vertex_info.stage.resources);
	}
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
		if (keep_snapshots) {
			std::swap(m_program_cache->kept_snapshots[1], pixel_info.stage.resources);
		}
		pixel_params = PrepareProgram(pixel_regs, sh, target_export_mapping, pixel_info);
	}
	lap.Mark(Common::FrameStats::Counter::ProgPrepareNs);
	if (Common::FrameStats::Enabled()) {
		// Draw stages the lookahead cannot serve (session 56 ceiling counters).
		if (mesh_active) {
			Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadMeshStages, 1);
		}
		if (!pixel_active && pixel_regs.ps_regs.data_addr != 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadPixelOff, 1);
		}
	}
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
		result.pixel = m_program_cache->Get(pixel_params, pixel_info, push_data_cursor, false,
		                                    keep_snapshots ? 1 : -1);
	}
	result.vertex = m_program_cache->Get(vertex_params, vertex_info, push_data_cursor, false,
	                                     keep_snapshots ? 0 : -1);
	return result;
}

void PipelineCache::QueueDrawAhead(std::span<const DrawAheadRequest> requests, bool first_batch) {
	if (requests.empty()) {
		return;
	}
	const bool        timed       = Common::FrameStats::Enabled();
	const auto        queue_begin = timed ? Common::FrameStats::NowNs() : 0;
	Common::LockGuard lock(m_mutex);
	m_program_cache->QueueAhead(requests, first_batch);
	if (timed) {
		Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadQueueNs,
		                        Common::FrameStats::NowNs() - queue_begin);
	}
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

void PipelineCache::PipelineKeyHash::MixStaticParams(std::size_t& hash,
                                                    const PipelineStaticParameters& params) {
	static const bool fast = [] {
		const auto* value = std::getenv("KYTY_PIPELINE_FAST_HASH");
		return value == nullptr || value[0] != '0';
	}();
	if (fast) {
		// Transient map lookup only. Equality already compares these packed bytes, and
		// the persisted pipeline recipes serialize the parameters themselves, not this hash.
		hash = static_cast<std::size_t>(XXH3_64bits_withSeed(&params, sizeof(params), hash));
		return;
	}
	const auto* bytes = reinterpret_cast<const uint8_t*>(&params);
	for (std::size_t i = 0; i < sizeof(params); i++) {
		Mix(hash, bytes[i]);
	}
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
	static const bool alpha_trace = std::getenv("KYTY_ALPHA_TRACE") != nullptr;
	if (alpha_trace && ps_active && ps_input_info->stage.program &&
	    (ps_input_info->stage.program->shader_hash == 0x1a4e22aaa15d8ab3ull ||
	     ps_input_info->stage.program->shader_hash == 0xaef08e7e8c990db9ull)) {
		static uint32_t last_frame = UINT32_MAX;
		const auto frame = GpuTimeProfiler::Frame();
		if (last_frame != frame) {
			last_frame = frame;
			LOGF("AlphaTrace: frame=%u ps=%016" PRIx64 " reg=0x%08x disabled=%d samples=%u\n",
			     frame, ps_input_info->stage.program->shader_hash, ctx.GetAlphaToMask(),
			     ctx.GetShaderRegisters().db_shader_control.alpha_to_mask_disable,
			     attachment_samples);
		}
	}
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
		Common::DrawStat::Mark(Common::DrawStat::ObjNew);
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
	Common::DrawStat::Mark(Common::DrawStat::ObjNew);
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
