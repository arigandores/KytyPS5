#include "common/frameStats.h"

#include "common/common.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdlib>
#include <mutex>

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

constexpr size_t MaxSites = 48;

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
