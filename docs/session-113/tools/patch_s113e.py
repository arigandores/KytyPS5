"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 18 (recorded first): the priority-operation stall instrument, no behaviour
change.  A priority operation remembers where it was queued (return address of DeferPriorityOperation).  The priority
thread counts waits that start on the recording (unsubmitted) tick (prio_unsub) and waits longer than 50 ms (prio_stall,
first 64 logged as PriorityStall:).  GuestGpu, before it waits for work (idle) or sleeps with every queue blocked, counts
the times a priority operation sits on the unsubmitted tick (gw_idle_prio, first 32 logged as GpuIdlePrio:).

    python C:/kyty/s106_stage/patch_s113e.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/common/frameStats.h'] = [
    ("""	BdaNarrowRace,           // bda_nrace
	Count
""",
     """	BdaNarrowRace,           // bda_nrace
	// Session 113 (item 18): the priority-operation stall instrument (raw counts).  prio_unsub: priority waits that
	// started on the recording (unsubmitted) tick; prio_stall: priority waits longer than 50 ms (PriorityStall: lines);
	// gw_idle_prio: GuestGpu went idle or slept with every queue blocked while a priority operation sat on the
	// unsubmitted tick (GpuIdlePrio: lines).
	PrioUnsub,               // prio_unsub
	PrioStall,               // prio_stall
	GpuIdlePrio,             // gw_idle_prio
	Count
"""),
]

EDITS['src/graphics/presentation/videoOut.cpp'] = [
    ("""				    {"bda_nrace", FS::Counter::BdaNarrowRace, false},
""",
     """				    {"bda_nrace", FS::Counter::BdaNarrowRace, false},
				    {"prio_unsub", FS::Counter::PrioUnsub, false},
				    {"prio_stall", FS::Counter::PrioStall, false},
				    {"gw_idle_prio", FS::Counter::GpuIdlePrio, false},
"""),
]

EDITS['src/graphics/host_gpu/renderer/commandScheduler.h'] = [
    ("""	void                      DeferPriorityOperation(Common::UniqueFunction<void>&& operation);
""",
     """	void                      DeferPriorityOperation(Common::UniqueFunction<void>&& operation);
	// Session 113 (ROADMAP item 18): a queued or waited priority operation on the recording (unsubmitted) tick - its tick
	// and the place that queued it.  Try-lock: false when the operation lock is busy.
	[[nodiscard]] bool        UnsubmittedPriorityOperation(uint64_t* tick, const void** site);
"""),
    ("""	uint64_t                     m_priority_active_tick = 0;
""",
     """	uint64_t                     m_priority_active_tick = 0;
	const void*                  m_priority_active_site = nullptr; // Session 113 (item 18)
"""),
]

CS = 'src/graphics/host_gpu/renderer/commandScheduler.cpp'
EDITS[CS] = [
    ("""#include <algorithm>
#include <array>
""",
     """#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
"""),
    ("""		m_priority_operations.push({std::move(operation), CurrentTick()});
""",
     """		m_priority_operations.push({std::move(operation), CurrentTick(), __builtin_return_address(0)});
"""),
    ("""			m_priority_active      = true;
			m_priority_active_tick = operation.tick;
		}
		m_master.Wait(operation.tick);
""",
     """			m_priority_active      = true;
			m_priority_active_tick = operation.tick;
			m_priority_active_site = operation.site;
		}
		// Session 113 (ROADMAP item 18): a wait that starts on the recording tick ends only when somebody submits it.
		const bool unsubmitted = operation.tick >= CurrentTick();
		const auto wait_t0     = std::chrono::steady_clock::now();
		m_master.Wait(operation.tick);
		const auto wait_us = std::chrono::duration_cast<std::chrono::microseconds>(
		                         std::chrono::steady_clock::now() - wait_t0)
		                         .count();
		if (unsubmitted) {
			Common::FrameStats::Add(Common::FrameStats::Counter::PrioUnsub, 1);
		}
		if (wait_us >= 50000) {
			Common::FrameStats::Add(Common::FrameStats::Counter::PrioStall, 1);
			static std::atomic<uint32_t> stall_logged {0};
			if (stall_logged.fetch_add(1, std::memory_order_relaxed) < 64) {
				LOGF("PriorityStall: tick=%llu unsub=%d us=%lld site=%s\\n",
				     static_cast<unsigned long long>(operation.tick), unsubmitted ? 1 : 0,
				     static_cast<long long>(wait_us), DeferredSiteName(operation.site));
			}
		}
"""),
    ("""			m_priority_active      = false;
			m_priority_active_tick = 0;
""",
     """			m_priority_active      = false;
			m_priority_active_tick = 0;
			m_priority_active_site = nullptr;
"""),
    ("""void CommandScheduler::PriorityOperationsThread(std::stop_token stop) {
""",
     """bool CommandScheduler::UnsubmittedPriorityOperation(uint64_t* tick, const void** site) {
	std::unique_lock lock(m_operation_mutex, std::try_to_lock);
	if (!lock.owns_lock()) {
		return false;
	}
	const auto current = CurrentTick();
	if (m_priority_active && m_priority_active_tick >= current) {
		*tick = m_priority_active_tick;
		*site = m_priority_active_site;
		return true;
	}
	if (!m_priority_operations.empty() && m_priority_operations.front().tick >= current) {
		*tick = m_priority_operations.front().tick;
		*site = m_priority_operations.front().site;
		return true;
	}
	return false;
}

void CommandScheduler::PriorityOperationsThread(std::stop_token stop) {
"""),
]

GR = 'src/graphics/guest_gpu/graphicsRun.cpp'
EDITS[GR] = [
    ("""CommandProcessor& GuestGpu::GetProcessor(uint32_t queue_id) {
""",
     """// Session 113 (ROADMAP item 18): GuestGpu is about to wait for work (or sleep with every queue blocked) while a priority
// operation sits on the recording tick - nothing submits that tick until more work arrives.  Instrument only.
static void NoteIdlePriority(RenderContext& renderer, const char* where) {
	uint64_t    tick = 0;
	const void* site = nullptr;
	if (!renderer.GetCommandScheduler().UnsubmittedPriorityOperation(&tick, &site)) {
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::GpuIdlePrio, 1);
	static std::atomic<uint32_t> logged {0};
	if (logged.fetch_add(1, std::memory_order_relaxed) < 32) {
		LOGF("GpuIdlePrio: where=%s tick=%llu site=+0x%llx\\n", where, static_cast<unsigned long long>(tick),
		     static_cast<unsigned long long>(Common::FrameStats::ModuleOffset(site)));
	}
}

CommandProcessor& GuestGpu::GetProcessor(uint32_t queue_id) {
"""),
    ("""				gpu->m_processing = false;
				gpu->m_idle.Signal();
				{
""",
     """				gpu->m_processing = false;
				gpu->m_idle.Signal();
				NoteIdlePriority(gpu->m_renderer, "idle");
				{
"""),
    ("""					gpu->m_processing = false;
					const auto t0 = std::chrono::steady_clock::now();
""",
     """					gpu->m_processing = false;
					NoteIdlePriority(gpu->m_renderer, "blocked");
					const auto t0 = std::chrono::steady_clock::now();
"""),
]


def main():
    for rel, pairs in EDITS.items():
        path = ROOT / rel
        raw = path.read_bytes().decode('utf-8')
        crlf = '\r\n' in raw
        text = raw.replace('\r\n', '\n')
        for old, new in pairs:
            assert old.endswith('\n') and (text.startswith(old) or ('\n' + old) in text), (rel, 'anchor not whole lines')
            n = text.count(old)
            assert n == 1, (rel, n, old[:90])
            text = text.replace(old, new)
        if crlf:
            text = text.replace('\n', '\r\n')
        if not DRY:
            path.write_bytes(text.encode('utf-8'))
        print(('checked ' if DRY else 'patched ') + rel)


if __name__ == '__main__':
    main()
