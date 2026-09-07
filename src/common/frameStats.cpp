#include "common/frameStats.h"

#include "common/common.h"
#include "common/logging/log.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdlib>
#include <mutex>
#include <vector>
#include <unordered_map>
#include <thread>
#include <string>
#include <cstring>
#include <chrono>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#include <intrin.h>
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h> // IWYU pragma: keep
#endif

namespace Common::FrameStats {

namespace {

std::array<std::atomic<uint64_t>, static_cast<size_t>(Counter::Count)> g_counters {};

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
	static const bool enabled = std::getenv("KYTY_FRAME_TRACE") != nullptr ||
	                            std::getenv("KYTY_AV_TRACE") != nullptr;
	return enabled;
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

void Add(Counter counter, uint64_t value) {
	g_counters[static_cast<size_t>(counter)].fetch_add(value, std::memory_order_relaxed);
}

uint64_t Read(Counter counter) {
	return g_counters[static_cast<size_t>(counter)].load(std::memory_order_relaxed);
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

struct SampleKey {
	uint64_t leaf_module = 0; // module base of the leaf frame (0 = unknown)
	uint64_t leaf_rip    = 0; // leaf rip relative to its module (or absolute if unknown)
	uint64_t kyty_rva    = 0; // first frame inside the executable (0 = none found)
	uint64_t chain[3] {};     // the next three frames inside the executable (callers)
	bool     operator==(const SampleKey& o) const noexcept {
		return leaf_module == o.leaf_module && leaf_rip == o.leaf_rip && kyty_rva == o.kyty_rva &&
		       chain[0] == o.chain[0] && chain[1] == o.chain[1] && chain[2] == o.chain[2];
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
	const auto  name_of = [&](uint64_t base) -> const std::string& {
		auto it = module_names.find(base);
		if (it == module_names.end()) {
			it = module_names.emplace(base, ModuleBaseName(base)).first;
		}
		return it->second;
	};
	for (;;) {
		std::this_thread::sleep_for(std::chrono::microseconds(700));
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
			// Unwind until the first frame inside this executable (at most 24 frames), then
			// three more frames inside it (the callers).
			uint64_t pc    = rip;
			int      found = 0;
			for (int depth = 0; depth < 40; depth++) {
				if (ModuleBaseOf(pc) == self_base) {
					if (found == 0) {
						key.kyty_rva = pc - self_base;
					} else {
						key.chain[found - 1] = pc - self_base;
					}
					if (++found > 3) {
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
				if (shown++ >= 400) {
					break;
				}
				LOGF("SampleTrace: leaf=%s rip=%s0x%llx at=+0x%llx n=%u chain=+0x%llx,+0x%llx,+0x%llx\n",
				     name_of(k.leaf_module).c_str(), k.leaf_module != 0 ? "+" : "",
				     static_cast<unsigned long long>(k.leaf_rip),
				     static_cast<unsigned long long>(k.kyty_rva), n,
				     static_cast<unsigned long long>(k.chain[0]),
				     static_cast<unsigned long long>(k.chain[1]),
				     static_cast<unsigned long long>(k.chain[2]));
			}
			counts.clear();
			total = 0;
		}
	}
	CloseHandle(target);
}

} // namespace

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
#endif

uint64_t ModuleOffset(const void* address) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	const auto base = reinterpret_cast<uint64_t>(GetModuleHandleW(nullptr));
	return reinterpret_cast<uint64_t>(address) - base;
#else
	return reinterpret_cast<uint64_t>(address);
#endif
}

SiteScope::SiteScope(const char* site): m_previous(t_site) {
	t_site = site;
}

SiteScope::~SiteScope() {
	t_site = m_previous;
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

} // namespace Common::FrameStats
