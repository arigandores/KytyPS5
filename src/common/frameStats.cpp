#include "common/frameStats.h"

#include "common/common.h"
#include "common/envFlag.h"
#include "common/gates.h"
#include "common/logging/log.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdlib>
#include <map>
#include <mutex>
#include <vector>
#include <unordered_map>
#include <thread>
#include <string>
#include <cstring>
#include <chrono>
#include <fstream>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#include <intrin.h>
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h> // IWYU pragma: keep
#endif

namespace Common::FrameStats {

namespace {

// Counters are sharded per thread: a shared atomic array cost one contended RMW per Add (about
// 50 per draw on the GuestGpu thread while a dozen guest threads count page faults). Each thread
// owns a shard (plain relaxed loads/stores, no RMW); Read() sums the live shards and the totals
// of exited threads. The registry is leaked on purpose: thread-local destructors may run after
// static destruction.
using Shard = Detail::Shard;

struct ShardRegistry {
	std::mutex                                                          mutex;
	std::vector<Shard*>                                                 live;
	std::array<std::atomic<uint64_t>, static_cast<size_t>(Counter::Count)> retired {};
};

ShardRegistry& Registry() {
	static auto* registry = new ShardRegistry;
	return *registry;
}

// Counts of a thread that already retired its shard (thread-local destructors of other objects
// can still count) go here and are never read.
Shard& SinkShard() {
	static auto* sink = new Shard;
	return *sink;
}

struct ShardOwner {
	Shard* shard = nullptr;
	~ShardOwner() {
		if (shard == nullptr) {
			return;
		}
		{
			auto&           registry = Registry();
			std::lock_guard lock(registry.mutex);
			for (size_t i = 0; i < shard->counters.size(); i++) {
				registry.retired[i].fetch_add(shard->counters[i].load(std::memory_order_relaxed),
				                              std::memory_order_relaxed);
			}
			registry.live.erase(std::find(registry.live.begin(), registry.live.end(), shard));
		}
		Detail::t_shard = &SinkShard();
		delete shard;
		shard = nullptr;
	}
};

thread_local ShardOwner t_owner;

bool TimingsFromEnvironment() {
	const auto* value = std::getenv("KYTY_FRAME_TRACE");
	return value == nullptr || std::strcmp(value, "lite") != 0;
}

thread_local ThreadRole  t_role = ThreadRole::Count;
thread_local const char* t_site = nullptr;

constexpr size_t MaxSites = 160;

struct SiteTable {
	std::mutex                                 mutex;
	std::array<const char*, MaxSites>          names {};
	std::array<std::atomic<uint64_t>, MaxSites> ns {};
	std::array<std::atomic<uint64_t>, MaxSites> count {};
	std::atomic<size_t>                        size {0};
};

std::array<SiteTable, static_cast<size_t>(Table::Count)> g_sites {};

size_t SiteIndex(SiteTable& table, const char* site) {
	const auto size = table.size.load(std::memory_order_acquire);
	for (size_t i = 0; i < size; i++) {
		if (table.names[i] == site) {
			return i;
		}
	}
	std::lock_guard lock(table.mutex);
	const auto      current = table.size.load(std::memory_order_acquire);
	for (size_t i = size; i < current; i++) {
		if (table.names[i] == site) {
			return i;
		}
	}
	if (current >= MaxSites) {
		return MaxSites - 1;
	}
	table.names[current] = site;
	table.size.store(current + 1, std::memory_order_release);
	return current;
}

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
std::array<std::atomic<HANDLE>, static_cast<size_t>(ThreadRole::Count)> g_threads {};

uint64_t QpcFrequency() {
	static const uint64_t frequency = [] {
		LARGE_INTEGER f {};
		QueryPerformanceFrequency(&f);
		return static_cast<uint64_t>(f.QuadPart);
	}();
	return frequency;
}

uint64_t Qpc() {
	LARGE_INTEGER c {};
	QueryPerformanceCounter(&c);
	return static_cast<uint64_t>(c.QuadPart);
}

// QueryThreadCycleTime() counts invariant TSC cycles; calibrate the TSC against QPC once (20 ms).
double TscCyclesPerNs() {
	static const double cycles_per_ns = [] {
		const auto f  = QpcFrequency();
		const auto q0 = Qpc();
		const auto t0 = __rdtsc();
		while (Qpc() - q0 < f / 50) {
		}
		const auto q1 = Qpc();
		const auto t1 = __rdtsc();
		const double ns = static_cast<double>(q1 - q0) * 1e9 / static_cast<double>(f);
		return ns > 0.0 ? static_cast<double>(t1 - t0) / ns : 0.0;
	}();
	return cycles_per_ns;
}
#endif

} // namespace

bool Enabled() {
	static const bool enabled = Common::EnvFlagOn("KYTY_FRAME_TRACE") ||
	                            Common::EnvFlagOn("KYTY_AV_TRACE");
	return enabled;
}

namespace {

// The inline Add and TimingsEnabled read these; before this runs they count and time nothing.
const bool g_published = [] {
	Detail::g_timings = TimingsFromEnvironment() && Enabled();
	Detail::g_count_limit.store(Enabled() ? static_cast<uint32_t>(Counter::Count) : 0u,
	                            std::memory_order_relaxed);
	return true;
}();

} // namespace

Detail::Shard* Detail::AttachShard() {
	auto& owner = t_owner;
	if (owner.shard == nullptr) {
		owner.shard              = new Shard;
		auto&           registry = Registry();
		std::lock_guard lock(registry.mutex);
		registry.live.push_back(owner.shard);
	}
	t_shard = owner.shard;
	return owner.shard;
}

void SetLean(bool lean) {
	(void)g_published;
	const auto limit = !Enabled() ? 0u
	                   : lean     ? static_cast<uint32_t>(Counter::LogNs)
	                              : static_cast<uint32_t>(Counter::Count);
	Detail::g_count_limit.store(limit, std::memory_order_relaxed);
}

uint64_t NowNs() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	// Invariant TSC (calibrated once against QPC): QueryPerformanceCounter cost 8% of the GuestGpu
	// thread under KYTY_FRAME_TRACE (about 26k timestamps per frame).
	static const double cycles_per_ns = TscCyclesPerNs();
	if (cycles_per_ns > 0.0) {
		return static_cast<uint64_t>(static_cast<double>(__rdtsc()) / cycles_per_ns);
	}
	const auto f = QpcFrequency();
	const auto c = Qpc();
	return f != 0 ? (c / f) * 1000000000ull + ((c % f) * 1000000000ull) / f : 0;
#else
	return 0;
#endif
}

uint64_t Read(Counter counter) {
	auto&           registry = Registry();
	std::lock_guard lock(registry.mutex);
	const auto      i     = static_cast<size_t>(counter);
	uint64_t        total = registry.retired[i].load(std::memory_order_relaxed);
	for (const auto* shard: registry.live) {
		total += shard->counters[i].load(std::memory_order_relaxed);
	}
	return total;
}

uint32_t TakeMax(Gauge gauge) {
	return Detail::g_gauges[static_cast<size_t>(gauge)].exchange(0, std::memory_order_relaxed);
}

void RegisterCurrentThread(ThreadRole role) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	t_role = role;
	StartSampler(role);
	if (!Enabled()) {
		return;
	}
	HANDLE handle = OpenThread(THREAD_QUERY_LIMITED_INFORMATION, FALSE, GetCurrentThreadId());
	if (handle != nullptr) {
		const auto old = g_threads[static_cast<size_t>(role)].exchange(handle);
		if (old != nullptr) {
			CloseHandle(old);
		}
	}
	(void)TscCyclesPerNs();
#else
	t_role = role;
#endif
}

ThreadRole CurrentRole() {
	return t_role;
}

void AddSite(Table table, const char* site, uint64_t ns) {
	auto&      t = g_sites[static_cast<size_t>(table)];
	const auto i = SiteIndex(t, site != nullptr ? site : "other");
	t.ns[i].fetch_add(ns, std::memory_order_relaxed);
	t.count[i].fetch_add(1, std::memory_order_relaxed);
}

size_t ReadSites(Table table, SiteRow* out, size_t max) {
	auto&      t    = g_sites[static_cast<size_t>(table)];
	const auto size = (std::min)(t.size.load(std::memory_order_acquire), max);
	for (size_t i = 0; i < size; i++) {
		out[i].name  = t.names[i];
		out[i].ns    = t.ns[i].load(std::memory_order_relaxed);
		out[i].count = t.count[i].load(std::memory_order_relaxed);
	}
	return size;
}

const char* CurrentSite() {
	return t_site;
}

// ---------------------------------------------------------------------------------------------
// Sampling profiler (KYTY_SAMPLE_GPU=1). A helper thread suspends the target thread about once a
// millisecond, reads RIP, unwinds the stack with RtlVirtualUnwind until the first frame inside
// this executable and counts (leaf module, leaf rip, kyty frame). Every 10 s the counts are
// logged and reset:
//   SampleTrace: t=<s> total=<n> thread=<role>
//   SampleTrace: leaf=<module> rip=<+rva|abs> at=+0x<kyty rva> n=<count>
// The kyty RVAs map to functions through the linker map (scripts/s12_samples.py).
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
namespace {

std::atomic<uint64_t> g_sample_frame {0};

struct SampleKey {
	uint64_t leaf_module = 0; // module base of the leaf frame (0 = unknown)
	uint64_t leaf_rip    = 0; // leaf rip relative to its module (or absolute if unknown)
	uint64_t kyty_rva    = 0; // first frame inside the executable (0 = none found)
	uint64_t chain[6] {};     // the next six frames inside the executable (callers)
	bool     operator==(const SampleKey& o) const noexcept {
		return leaf_module == o.leaf_module && leaf_rip == o.leaf_rip && kyty_rva == o.kyty_rva &&
		       chain[0] == o.chain[0] && chain[1] == o.chain[1] && chain[2] == o.chain[2] &&
		       chain[3] == o.chain[3] && chain[4] == o.chain[4] && chain[5] == o.chain[5];
	}
};

struct SampleKeyHash {
	size_t operator()(const SampleKey& k) const noexcept {
		uint64_t h = k.leaf_module * 0x9E3779B97F4A7C15ull;
		h ^= k.leaf_rip + 0x7F4A7C15ull + (h << 6u) + (h >> 2u);
		h ^= k.kyty_rva * 0xC2B2AE3D27D4EB4Full;
		h ^= k.chain[0] * 0x9E3779B97F4A7C15ull + (h << 5u);
		h ^= k.chain[1] * 0xC2B2AE3D27D4EB4Full + (h >> 3u);
		h ^= k.chain[2] * 0x165667B19E3779F9ull + (h << 7u);
		h ^= k.chain[3] * 0x9E3779B97F4A7C15ull + (h >> 5u);
		h ^= k.chain[4] * 0xC2B2AE3D27D4EB4Full + (h << 3u);
		h ^= k.chain[5] * 0x165667B19E3779F9ull + (h >> 7u);
		return static_cast<size_t>(h ^ (h >> 29u));
	}
};

std::string ModuleBaseName(uint64_t base) {
	if (base == 0) {
		return "?";
	}
	wchar_t path[MAX_PATH] = {};
	const auto n = GetModuleFileNameW(reinterpret_cast<HMODULE>(base), path, MAX_PATH);
	if (n == 0) {
		return "?";
	}
	std::wstring w(path, n);
	const auto   slash = w.find_last_of(L"\\/");
	if (slash != std::wstring::npos) {
		w = w.substr(slash + 1);
	}
	std::string s;
	for (const auto c: w) {
		s.push_back(c < 128 ? static_cast<char>(c) : '?');
	}
	return s;
}

uint64_t ModuleBaseOf(uint64_t address) {
	HMODULE module = nullptr;
	if (GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
	                           GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
	                       reinterpret_cast<LPCWSTR>(address), &module) == 0) {
		return 0;
	}
	return reinterpret_cast<uint64_t>(module);
}

void SamplerThread(HANDLE target, ThreadRole role) {
	const auto self_base = reinterpret_cast<uint64_t>(GetModuleHandleW(nullptr));
	std::unordered_map<SampleKey, uint32_t, SampleKeyHash> counts;
	std::unordered_map<uint64_t, std::string>              module_names;
	const auto  t_start = std::chrono::steady_clock::now();
	auto        t_dump  = t_start;
	uint64_t    total   = 0;
	// KYTY_SAMPLE_FRAME_MS=<ms>: samples of every frame that lasted at least this long are logged
	// separately (SampleFrame: rows), so the composition of a scene-cut frame is visible.
	static const uint64_t frame_min_ms = [] {
		const char* value = std::getenv("KYTY_SAMPLE_FRAME_MS");
		return value != nullptr ? std::strtoull(value, nullptr, 10) : uint64_t {0};
	}();
	std::unordered_map<SampleKey, uint32_t, SampleKeyHash> frame_counts;
	uint64_t    frame_total = 0;
	uint64_t    frame_seq   = g_sample_frame.load();
	auto        t_frame     = t_start;
	const auto  name_of = [&](uint64_t base) -> const std::string& {
		auto it = module_names.find(base);
		if (it == module_names.end()) {
			it = module_names.emplace(base, ModuleBaseName(base)).first;
		}
		return it->second;
	};
	// KYTY_SAMPLE_US=<us>: sampling interval. The default sleeps ~700 us (in practice the Windows
	// timer rounds this up to ~1.5 ms); a value below 1000 spins on the clock instead, so a scene-cut
	// frame of 80 ms gets several hundred samples instead of fifty.
	static const int64_t interval_us = [] {
		const char* value = std::getenv("KYTY_SAMPLE_US");
		return value != nullptr ? std::strtoll(value, nullptr, 10) : int64_t {0};
	}();
	auto t_next = std::chrono::steady_clock::now();
	// Optional gate lets one run supply an ordinary FPS window followed by CPU samples.
	// Only the helper polls this file; with the gate off it never suspends the game thread.
	const auto* gate_path = std::getenv("KYTY_SAMPLE_GATE");
	bool sampling = gate_path == nullptr;
	auto gate_next = t_next;
	for (;;) {
		if (gate_path != nullptr) {
			const auto now = std::chrono::steady_clock::now();
			if (now >= gate_next) {
				gate_next = now + std::chrono::milliseconds(100);
				char value = '0';
				std::ifstream(gate_path).get(value);
				const bool requested = value == '1';
				if (requested != sampling) {
					sampling = requested;
					counts.clear();
					frame_counts.clear();
					total = frame_total = 0;
					t_dump = t_frame = t_next = now;
					LOGF("SampleGate: enabled=%d\n", sampling ? 1 : 0);
				}
			}
			if (!sampling) {
				std::this_thread::sleep_for(std::chrono::milliseconds(50));
				continue;
			}
		}
		if (interval_us <= 0) {
			std::this_thread::sleep_for(std::chrono::microseconds(700));
		} else {
			t_next += std::chrono::microseconds(interval_us);
			while (std::chrono::steady_clock::now() < t_next) {
				YieldProcessor();
			}
		}
		if (SuspendThread(target) == static_cast<DWORD>(-1)) {
			break;
		}
		CONTEXT context {};
		context.ContextFlags = CONTEXT_CONTROL | CONTEXT_INTEGER;
		const bool ok        = GetThreadContext(target, &context) != 0;
		SampleKey  key;
		if (ok) {
			const auto rip   = context.Rip;
			const auto base  = ModuleBaseOf(rip);
			key.leaf_module  = base;
			key.leaf_rip     = base != 0 ? rip - base : rip;
			// Unwind until the first frame inside this executable (at most 40 frames), then
			// six more frames inside it (the callers).
			uint64_t pc    = rip;
			int      found = 0;
			for (int depth = 0; depth < 40; depth++) {
				if (ModuleBaseOf(pc) == self_base) {
					if (found == 0) {
						key.kyty_rva = pc - self_base;
					} else {
						key.chain[found - 1] = pc - self_base;
					}
					if (++found > 6) {
						break;
					}
				}
				DWORD64 image_base = 0;
				auto*   entry      = RtlLookupFunctionEntry(pc, &image_base, nullptr);
				if (entry == nullptr) {
					// Leaf function without unwind info: the return address is at [rsp].
					uint64_t ret = 0;
					if (context.Rsp == 0 ||
					    IsBadReadPtr(reinterpret_cast<const void*>(context.Rsp), 8) != 0) {
						break;
					}
					std::memcpy(&ret, reinterpret_cast<const void*>(context.Rsp), 8);
					context.Rsp += 8;
					context.Rip = ret;
				} else {
					void*   handler_data = nullptr;
					DWORD64 establisher  = 0;
					RtlVirtualUnwind(UNW_FLAG_NHANDLER, image_base, pc, entry, &context,
					                 &handler_data, &establisher, nullptr);
				}
				pc = context.Rip;
				if (pc == 0) {
					break;
				}
			}
		}
		ResumeThread(target);
		if (ok) {
			counts[key]++;
			total++;
		}
		const auto now = std::chrono::steady_clock::now();
		if (frame_min_ms != 0) {
			const auto seq = g_sample_frame.load();
			if (seq != frame_seq) {
				const auto ms = std::chrono::duration<double, std::milli>(now - t_frame).count();
				if (ms >= static_cast<double>(frame_min_ms) && frame_total != 0) {
					std::vector<std::pair<SampleKey, uint32_t>> rows(frame_counts.begin(),
					                                                 frame_counts.end());
					std::sort(rows.begin(), rows.end(),
					          [](const auto& a, const auto& b) { return a.second > b.second; });
					LOGF("SampleFrame: n=%llu dt_ms=%.1f total=%llu thread=%d\n",
					     static_cast<unsigned long long>(frame_seq), ms,
					     static_cast<unsigned long long>(frame_total), static_cast<int>(role));
					size_t shown = 0;
					for (const auto& [k, n]: rows) {
						if (shown++ >= 200) {
							break;
						}
						LOGF("SampleFrame: leaf=%s rip=%s0x%llx at=+0x%llx n=%u chain=+0x%llx,+0x%llx,+0x%llx,+0x%llx,+0x%llx,+0x%llx\n",
						     name_of(k.leaf_module).c_str(), k.leaf_module != 0 ? "+" : "",
						     static_cast<unsigned long long>(k.leaf_rip),
						     static_cast<unsigned long long>(k.kyty_rva), n,
						     static_cast<unsigned long long>(k.chain[0]),
						     static_cast<unsigned long long>(k.chain[1]),
						     static_cast<unsigned long long>(k.chain[2]),
						     static_cast<unsigned long long>(k.chain[3]),
						     static_cast<unsigned long long>(k.chain[4]),
						     static_cast<unsigned long long>(k.chain[5]));
					}
				}
				frame_counts.clear();
				frame_total = 0;
				frame_seq   = seq;
				t_frame     = now;
			}
			if (ok) {
				frame_counts[key]++;
				frame_total++;
			}
		}
		if (now - t_dump >= std::chrono::seconds(10)) {
			t_dump = now;
			std::vector<std::pair<SampleKey, uint32_t>> rows(counts.begin(), counts.end());
			std::sort(rows.begin(), rows.end(),
			          [](const auto& a, const auto& b) { return a.second > b.second; });
			const auto t_s =
			    std::chrono::duration<double>(now - t_start).count();
			LOGF("SampleTrace: t=%.1f total=%llu thread=%d\n", t_s,
			     static_cast<unsigned long long>(total), static_cast<int>(role));
			size_t shown = 0;
			for (const auto& [k, n]: rows) {
				// Every row: with call chains in the key the top 400 rows held only about half the
				// samples, and the shares printed by the scripts were of that half.
				if (shown++ >= 20000) {
					break;
				}
				LOGF("SampleTrace: leaf=%s rip=%s0x%llx at=+0x%llx n=%u chain=+0x%llx,+0x%llx,+0x%llx,+0x%llx,+0x%llx,+0x%llx\n",
				     name_of(k.leaf_module).c_str(), k.leaf_module != 0 ? "+" : "",
				     static_cast<unsigned long long>(k.leaf_rip),
				     static_cast<unsigned long long>(k.kyty_rva), n,
				     static_cast<unsigned long long>(k.chain[0]),
				     static_cast<unsigned long long>(k.chain[1]),
				     static_cast<unsigned long long>(k.chain[2]),
				     static_cast<unsigned long long>(k.chain[3]),
				     static_cast<unsigned long long>(k.chain[4]),
				     static_cast<unsigned long long>(k.chain[5]));
			}
			counts.clear();
			total = 0;
		}
	}
	CloseHandle(target);
}

} // namespace

void NoteFrame(uint64_t frame) {
	g_sample_frame.store(frame);
}

void StartSampler(ThreadRole role) {
	static std::atomic<bool> started {false};
	const char*              value = std::getenv("KYTY_SAMPLE_GPU");
	if (value == nullptr) {
		return;
	}
	const bool want_gpu  = std::strcmp(value, "1") == 0 || std::strcmp(value, "gpu") == 0;
	const bool want_main = std::strcmp(value, "main") == 0;
	if (!((want_gpu && role == ThreadRole::Gpu) || (want_main && role == ThreadRole::Main)) ||
	    started.exchange(true)) {
		return;
	}
	HANDLE target = OpenThread(THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT |
	                               THREAD_QUERY_INFORMATION,
	                           FALSE, GetCurrentThreadId());
	if (target == nullptr) {
		return;
	}
	std::thread(SamplerThread, target, role).detach();
}
#else
void StartSampler(ThreadRole) {}
void NoteFrame(uint64_t) {}
#endif

uint64_t ModuleOffset(const void* address) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	const auto base = reinterpret_cast<uint64_t>(GetModuleHandleW(nullptr));
	return reinterpret_cast<uint64_t>(address) - base;
#else
	return reinterpret_cast<uint64_t>(address);
#endif
}

const char* SiteName(const void* address) {
	static std::mutex                         mutex;
	static std::map<const void*, std::string> names;
	std::lock_guard                           lock(mutex);
	auto [it, inserted] = names.try_emplace(address);
	if (inserted) {
		char text[32];
		std::snprintf(text, sizeof(text), "+0x%llx",
		              static_cast<unsigned long long>(ModuleOffset(address)));
		it->second = text;
	}
	return it->second.c_str();
}

SiteScope::SiteScope(const char* site): m_previous(t_site) {
	t_site = site;
}

SiteScope::~SiteScope() {
	t_site = m_previous;
}

bool GpuWallOn() {
	static const bool on = [] {
		const bool value = Common::EnvFlagOn("KYTY_GPU_WALL");
		if (value) {
			LOGF("GpuWall: mode 1" "\n");
		}
		return value;
	}();
	return on;
}

uint64_t ThreadCpuNs(ThreadRole role) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	const auto handle = g_threads[static_cast<size_t>(role)].load();
	if (handle == nullptr) {
		return 0;
	}
	ULONG64 cycles = 0;
	if (QueryThreadCycleTime(handle, &cycles) == 0) {
		return 0;
	}
	const auto per_ns = TscCyclesPerNs();
	return per_ns > 0.0 ? static_cast<uint64_t>(static_cast<double>(cycles) / per_ns) : 0;
#else
	(void)role;
	return 0;
#endif
}

uint64_t ProcessCpuNs() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	FILETIME creation {};
	FILETIME exit {};
	FILETIME kernel {};
	FILETIME user {};
	if (GetProcessTimes(GetCurrentProcess(), &creation, &exit, &kernel, &user) == 0) {
		return 0;
	}
	const auto to_u64 = [](const FILETIME& t) {
		return (static_cast<uint64_t>(t.dwHighDateTime) << 32u) | t.dwLowDateTime;
	};
	return (to_u64(kernel) + to_u64(user)) * 100u;
#else
	return 0;
#endif
}

// ---------------------------------------------------------------------------------------------------------------------
// Session 122, knob "burn" (MEASUREMENT ONLY): the cold paths of the hooks in frameStats.h.  They run once per frame and
// site on each hooked thread (a seen counter, one knob read) and, only while armed, the spin and its bookkeeping.  The
// counted time (burn_*_ns) is the wall of the armed path: from right after the decode (and the one-off self-test and arm
// log) to right before the counter Adds, so a spread step's per-call overhead is inside the dose; a block converts TSC ->
// ns once, a spread step converts per step and carries the sub-ns remainder to the next step (t_burn_frac), so the
// frame's spread total is not truncated per step.  RC3: the thread CPU (QueryThreadCycleTime on this thread) is read
// around every block spin and around one spread step in 64, and published beside the wall of the same spins
// (burn_*_cpu_ns / burn_*_cpu_w): the admission check
// "cpu >= 0.9 * wall" verifies the burn itself, not the frame.  A spread sample's CPU interval holds most of the two
// QueryThreadCycleTime calls and its wall does not (unit test: cpu/wall 1.32-1.37 at a ~227 ns step, no preemption),
// so the spread ratio is read against that baseline, not 1.0 (ROADMAP s. 122 item 3 (e)); blocks read 1.000.
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
namespace {

struct BurnCounters {
	Counter ns;     // wall of the armed path
	Counter n;      // burnt (block) or armed (spread) frames
	Counter q;      // spread spin calls; Counter::Count = a block-only group
	Counter cpu_ns; // thread CPU across the sampled spins
	Counter cpu_w;  // wall of the same sampled spins
};
constexpr BurnCounters kBurnGpu {Counter::BurnGNs, Counter::BurnGN, Counter::Count, Counter::BurnGCpuNs,
                                 Counter::BurnGCpuW};
constexpr BurnCounters kBurnRecord {Counter::BurnRNs, Counter::BurnRN, Counter::BurnRQ, Counter::BurnRCpuNs,
                                    Counter::BurnRCpuW};
constexpr BurnCounters kBurnM1 {Counter::BurnMNs, Counter::BurnMN, Counter::BurnMQ, Counter::BurnMCpuNs,
                                Counter::BurnMCpuW};
constexpr BurnCounters kBurnMain {Counter::BurnTNs, Counter::BurnTN, Counter::Count, Counter::BurnTCpuNs,
                                  Counter::BurnTCpuW};
constexpr BurnCounters kBurnPlacebo {Counter::BurnPNs, Counter::BurnPN, Counter::Count, Counter::BurnPCpuNs,
                                     Counter::BurnPCpuW};

constexpr uint32_t BurnCodeBase    = 100000;
constexpr uint32_t BurnMaxDoseUs   = 20000;
constexpr uint64_t BurnLateSlackNs = 50000;

std::array<std::atomic<uint32_t>, 9> g_burn_last_armed {}; // per code: the last armed value that was logged
std::atomic<uint32_t>                g_burn_log_arm {0};
std::atomic<uint32_t>                g_burn_log_reject {0};
std::atomic<uint32_t>                g_burn_log_late {0};
std::atomic<bool>                    g_burn_notsc {false};
std::atomic<bool>                    g_burn_selftest {false};
std::atomic<bool>                    g_burn_placebo {false};

thread_local uint64_t            t_burn_q          = 0;       // spread quantum, TSC cycles
thread_local uint32_t            t_burn_prev_calls = 0;       // calls of this thread's previous ARMED spread frame
thread_local uint32_t            t_burn_sample     = 0;       // spread steps, for the 1-in-64 CPU sample
thread_local const BurnCounters* t_burn_ctr        = nullptr; // counters of the armed spread frame
thread_local uint64_t            t_burn_carry      = 0;       // previous step's bookkeeping tail, TSC cycles
thread_local uint64_t            t_burn_gap        = 0;       // per-step rdtsc gap, TSC cycles (BurnRdtscGap)
thread_local double              t_burn_frac       = 0.0;     // sub-ns remainder of the spread conversions, cycles

// The mean cost of a back-to-back rdtsc pair (4 096 pairs; a pair over 1 000 cycles is an interrupt and dropped),
// measured once per process: the sliver between a spread step's last timestamp and the next step's first that
// neither counts (the unit test measured it at ~7 ns a step, 2.8 % of a 2 000 us spread dose).
uint64_t BurnRdtscGap() {
	static const uint64_t gap = [] {
		uint64_t sum = 0;
		uint64_t n   = 0;
		for (int i = 0; i < 4096; i++) {
			const uint64_t a = __rdtsc();
			const uint64_t b = __rdtsc();
			if (b - a < 1000) {
				sum += b - a;
				n++;
			}
		}
		return n != 0 ? (sum + n / 2) / n : 0;
	}();
	return gap;
}

uint64_t BurnNs(uint64_t cycles, double cycles_per_ns) {
	return static_cast<uint64_t>(static_cast<double>(cycles) / cycles_per_ns);
}

bool BurnThreadCycles(uint64_t* cycles) {
	ULONG64 c = 0;
	if (QueryThreadCycleTime(GetCurrentThread(), &c) == 0) {
		return false;
	}
	*cycles = c;
	return true;
}

// The one knob read of a new frame.  False: off, rejected (logged, <= 8 lines) or no calibrated TSC (logged once).
bool BurnDecode(uint32_t* code, uint32_t* dose_us, double* cycles_per_ns) {
	const auto value = Common::Gates::Value(Common::Gates::Knob::Burn);
	if (value == 0) {
		return false;
	}
	*code    = value / BurnCodeBase;
	*dose_us = value % BurnCodeBase;
	if (*code < 1 || *code > 8 || *dose_us == 0 || *dose_us > BurnMaxDoseUs) {
		if (g_burn_log_reject.fetch_add(1, std::memory_order_relaxed) < 8) {
			LOGF("Burn: value=%u rejected\n", value);
		}
		return false;
	}
	*cycles_per_ns = TscCyclesPerNs();
	if (!(*cycles_per_ns > 0.0)) {
		if (!g_burn_notsc.exchange(true, std::memory_order_relaxed)) {
			LOGF("Burn: no calibrated TSC, disabled\n");
		}
		return false;
	}
	return true;
}

// Once per process, on the first arming of any code (RC13: on that thread at block position 0 of the first armed block,
// outside the estimator window 10-88): 1 000 us of the same spin, timed by NowNs and by QPC.
void BurnSelfTest(double cycles_per_ns) {
	if (g_burn_selftest.exchange(true, std::memory_order_relaxed)) {
		return;
	}
	const auto frequency = QpcFrequency();
	const auto q0        = Qpc();
	const auto n0        = NowNs();
	const auto cycles    = BurnSpinUntil(__rdtsc(), static_cast<uint64_t>(1000000.0 * cycles_per_ns));
	const auto n1        = NowNs();
	const auto q1        = Qpc();
	const double qpc_us  = frequency != 0 ? static_cast<double>(q1 - q0) * 1e6 / static_cast<double>(frequency) : 0.0;
	LOGF("Burn: selftest target_us=1000 tsc_us=%.1f qpc_us=%.1f spin_us=%.1f cycles_per_ns=%.6f rdtsc_gap_ns=%.1f\n",
	     static_cast<double>(n1 - n0) / 1000.0, qpc_us, static_cast<double>(cycles) / cycles_per_ns / 1000.0,
	     cycles_per_ns, static_cast<double>(BurnRdtscGap()) / cycles_per_ns);
}

// On each change of the armed value per code (the first arming of a code, or a new dose); <= 32 lines.
void BurnLogArm(uint32_t code, uint32_t dose_us, const char* thread, uint64_t q_ns) {
	const uint32_t value = code * BurnCodeBase + dose_us;
	if (g_burn_last_armed[code].exchange(value, std::memory_order_relaxed) == value) {
		return;
	}
	if (g_burn_log_arm.fetch_add(1, std::memory_order_relaxed) < 32) {
		LOGF("Burn: arm code=%u thread=%s dose_us=%u q_ns=%llu\n", code, thread, dose_us,
		     static_cast<unsigned long long>(q_ns));
	}
}

// One block of `dose_us` on this thread, CPU read around it (RC3; burn_*_cpu_w = the wall between the readings).
void BurnBlock(uint32_t code, uint32_t dose_us, double cycles_per_ns, const BurnCounters& c, const char* thread) {
	BurnSelfTest(cycles_per_ns);
	BurnLogArm(code, dose_us, thread, 0);
	const uint64_t dose_ns = static_cast<uint64_t>(dose_us) * 1000u;
	const uint64_t target  = static_cast<uint64_t>(static_cast<double>(dose_ns) * cycles_per_ns);
	const uint64_t t_in    = __rdtsc();
	uint64_t       c0      = 0;
	uint64_t       c1      = 0;
	const bool     ok0     = BurnThreadCycles(&c0);
	const uint64_t s0      = __rdtsc();
	(void)BurnSpinUntil(t_in, target);
	const uint64_t s1    = __rdtsc();
	const bool     ok1   = BurnThreadCycles(&c1);
	const uint64_t t_out = __rdtsc();
	const uint64_t ns    = BurnNs(t_out - t_in, cycles_per_ns);
	Add(c.ns, ns);
	Add(c.n, 1);
	if (ok0 && ok1 && c1 > c0) {
		Add(c.cpu_ns, BurnNs(c1 - c0, cycles_per_ns));
		Add(c.cpu_w, BurnNs(s1 - s0, cycles_per_ns)); // the wall between the two readings
	} else {
		Add(Counter::BurnCpuBad, 1);
	}
	if (ns > dose_ns + BurnLateSlackNs) {
		Add(Counter::BurnLate, 1);
		if (g_burn_log_late.fetch_add(1, std::memory_order_relaxed) < 64) {
			LOGF("BurnLate: code=%u us=%.1f target_us=%u\n", code, static_cast<double>(ns) / 1000.0, dose_us);
		}
	}
}

// Arms a spread frame on this thread: budget B = dose / divisor, quantum q = 1.25 * B / (calls of the previous armed
// frame), 250 ns in the first armed frame; the dose is front-loaded into the first ~80 % of the frame and never
// exceeds B (leftover budget is discarded at the next key).  The arming call is the frame's first step.
void BurnArmSpread(uint32_t code, uint32_t dose_us, uint32_t divisor, double cycles_per_ns, const BurnCounters& c,
                   const char* thread) {
	BurnSelfTest(cycles_per_ns);
	const uint64_t budget =
	    static_cast<uint64_t>(static_cast<double>(dose_us) * 1000.0 * cycles_per_ns / static_cast<double>(divisor));
	uint64_t q = t_burn_prev_calls == 0
	                 ? static_cast<uint64_t>(250.0 * cycles_per_ns)
	                 : static_cast<uint64_t>(1.25 * static_cast<double>(budget) / static_cast<double>(t_burn_prev_calls));
	q = std::max<uint64_t>(q, 1);
	BurnLogArm(code, dose_us, thread, BurnNs(q, cycles_per_ns));
	t_burn_q             = q;
	t_burn_ctr           = &c;
	t_burn_carry         = 0;
	t_burn_frac          = 0.0;
	t_burn_gap           = BurnRdtscGap();
	Detail::t_burn_left  = budget;
	Detail::t_burn_calls = 1;
	Detail::t_burn_spread = true;
	Add(c.n, 1);
	if (budget != 0) {
		BurnSpreadStep();
	}
}

void BurnPlaceboLoop(void (*pin)(bool)) {
	uint32_t last = Detail::g_burn_frame.v.load(std::memory_order_acquire);
	for (;;) {
		Sleep(1);
		const uint32_t key = Detail::g_burn_frame.v.load(std::memory_order_acquire);
		if (key == last) {
			continue;
		}
		last = key;
		Add(Counter::BurnPSeen, 1);
		uint32_t code          = 0;
		uint32_t dose_us       = 0;
		double   cycles_per_ns = 0.0;
		if (!BurnDecode(&code, &dose_us, &cycles_per_ns) || code != 8) {
			continue;
		}
		if (pin != nullptr) {
			pin(false); // knob "dapin", as an M1 worker applies it (RC9)
		}
		BurnBlock(code, dose_us, cycles_per_ns, kBurnPlacebo, "Placebo");
	}
}

// RC9: detached (a joinable std::thread destroyed at exit would call std::terminate), started once.
void BurnStartPlacebo(void (*pin)(bool)) {
	if (g_burn_placebo.exchange(true, std::memory_order_relaxed)) {
		return;
	}
	std::thread(BurnPlaceboLoop, pin).detach();
	LOGF("Burn: placebo thread started\n");
}

} // namespace

// The counted wall of a step runs from its entry to the end of its spin, plus the bookkeeping tail of the previous
// step (t_burn_carry) and the rdtsc gap between steps (t_burn_gap), so the per-call overhead is inside the dose (the
// unit test measured ~8 ns a step outside it before the carry, ~7 ns after it); the tail of a frame's last step is
// lost.  t_burn_gap is a per-process ESTIMATE (the mean back-to-back rdtsc pair, ~7 ns), not a measured wall (ROADMAP
// s. 122 item 3 (d)).  The TSC -> ns conversion carries the sub-ns remainder to the next step (t_burn_frac); truncating
// every step lost ~0.5 ns a step, ~0.2 % of a 2 000 us spread dose.
void BurnSpreadStep() {
	const uint64_t t_in          = __rdtsc();
	const double   cycles_per_ns = TscCyclesPerNs();
	const auto&    c             = *t_burn_ctr;
	const uint64_t chunk         = std::min(t_burn_q, Detail::t_burn_left);
	const bool     sample        = (t_burn_sample++ & 63u) == 0;
	uint64_t       c0            = 0;
	uint64_t       c1            = 0;
	const bool     ok0           = sample && BurnThreadCycles(&c0);
	const uint64_t s0            = sample ? __rdtsc() : t_in;
	(void)BurnSpinUntil(s0, chunk);
	const uint64_t s1      = sample ? __rdtsc() : 0;
	const bool     ok1     = sample && BurnThreadCycles(&c1);
	const uint64_t t_mid   = __rdtsc();
	const uint64_t elapsed = t_mid - t_in + t_burn_carry + t_burn_gap;
	Detail::t_burn_left    = elapsed >= Detail::t_burn_left ? 0 : Detail::t_burn_left - elapsed;
	const double   counted = static_cast<double>(elapsed) + t_burn_frac;
	const uint64_t ns      = static_cast<uint64_t>(counted / cycles_per_ns);
	t_burn_frac            = counted - static_cast<double>(ns) * cycles_per_ns;
	Add(c.ns, ns);
	Add(c.q, 1);
	if (sample) {
		if (ok0 && ok1 && c1 > c0) {
			Add(c.cpu_ns, BurnNs(c1 - c0, cycles_per_ns));
			Add(c.cpu_w, BurnNs(s1 - s0, cycles_per_ns)); // the wall between the two readings
		} else {
			Add(Counter::BurnCpuBad, 1);
		}
	}
	t_burn_carry = __rdtsc() - t_mid;
}

void BurnNewFrame(BurnSite site, uint32_t key, void (*pin)(bool)) {
	Detail::t_burn_key[static_cast<size_t>(site)] = key;
	if (site == BurnSite::Record || site == BurnSite::M1Job) {
		if (Detail::t_burn_spread) {
			t_burn_prev_calls = Detail::t_burn_calls;
		}
		Detail::t_burn_spread = false;
		Detail::t_burn_left   = 0;
		Detail::t_burn_calls  = 0;
	}
	switch (site) {
		case BurnSite::Gpu: Add(Counter::BurnGSeen, 1); break;
		case BurnSite::Record: Add(Counter::BurnRSeen, 1); break;
		case BurnSite::M1Job: Add(Counter::BurnMSeen, 1); break;
		case BurnSite::M1Top: Add(Counter::BurnM0Seen, 1); break;
		case BurnSite::Main:
			if (CurrentRole() != ThreadRole::Main) {
				return;
			}
			Add(Counter::BurnTSeen, 1);
			break;
		default: return;
	}
	uint32_t code          = 0;
	uint32_t dose_us       = 0;
	double   cycles_per_ns = 0.0;
	if (!BurnDecode(&code, &dose_us, &cycles_per_ns)) {
		return;
	}
	switch (site) {
		case BurnSite::Gpu:
			if (code == 1) {
				BurnBlock(code, dose_us, cycles_per_ns, kBurnGpu, "GuestGpu");
			} else if (code == 8) {
				BurnStartPlacebo(pin);
			}
			break;
		case BurnSite::Record:
			if (code == 5) {
				BurnBlock(code, dose_us, cycles_per_ns, kBurnRecord, "Record");
			} else if (code == 2) {
				BurnArmSpread(code, dose_us, 1, cycles_per_ns, kBurnRecord, "Record");
			}
			break;
		case BurnSite::M1Job:
			if (code == 3) {
				const auto threads = Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads);
				BurnArmSpread(code, dose_us, std::max<uint32_t>(threads, 1), cycles_per_ns, kBurnM1, "M1");
			}
			break;
		case BurnSite::M1Top:
			if (code == 6) {
				BurnBlock(code, dose_us, cycles_per_ns, kBurnM1, "M1worker0");
			}
			break;
		case BurnSite::Main:
			if (code == 4) {
				BurnBlock(code, dose_us, cycles_per_ns, kBurnMain, "Main");
			}
			break;
		default: break;
	}
}

void BurnSubmitFrame(uint32_t key) {
	uint32_t taken = Detail::g_burn_submit_key.v.load(std::memory_order_relaxed);
	do {
		// A submitter that loaded an older key must not move the frame back.
		if (static_cast<int32_t>(key - taken) <= 0) {
			return;
		}
	} while (!Detail::g_burn_submit_key.v.compare_exchange_weak(taken, key, std::memory_order_relaxed));
	Add(Counter::BurnSSeen, 1);
	if (CurrentRole() == ThreadRole::Main) {
		Add(Counter::BurnSMain, 1);
	}
	uint32_t code          = 0;
	uint32_t dose_us       = 0;
	double   cycles_per_ns = 0.0;
	if (!BurnDecode(&code, &dose_us, &cycles_per_ns) || code != 7) {
		return;
	}
	BurnBlock(code, dose_us, cycles_per_ns, kBurnMain, "Submit");
}
#else
void BurnSpreadStep() {
	Detail::t_burn_left = 0;
}
void BurnNewFrame(BurnSite site, uint32_t key, void (*pin)(bool)) {
	(void)pin;
	Detail::t_burn_key[static_cast<size_t>(site)] = key;
}
void BurnSubmitFrame(uint32_t key) {
	Detail::g_burn_submit_key.v.store(key, std::memory_order_relaxed);
}
#endif

} // namespace Common::FrameStats
