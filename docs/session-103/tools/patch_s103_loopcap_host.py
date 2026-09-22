"""Session 103: KYTY_BVH_LOOP_CAP, the host half - fault-buffer tail, per-GC readback, counters."""
import sys

DRY = len(sys.argv) > 1 and sys.argv[1] == '--dry'
SRC = 'C:/kyty/KytyPS5/src/'
NL = chr(92) + 'n'
files = {}


def load(rel):
    if rel not in files:
        b = open(SRC + rel, 'rb').read().decode('utf-8')
        assert '\r\n' not in b, rel
        files[rel] = b
    return files[rel]


def rep(rel, old, new, cnt=1):
    b = load(rel)
    n = b.count(old)
    assert n == cnt, (rel, old[:90], n)
    files[rel] = b.replace(old, new)


FMH = 'graphics/host_gpu/renderer/cache/faultManager.h'
FMC = 'graphics/host_gpu/renderer/cache/faultManager.cpp'
BCC = 'graphics/host_gpu/renderer/cache/bufferCache.cpp'
FSH = 'common/frameStats.h'
VOC = 'graphics/presentation/videoOut.cpp'

# --- faultManager.h
rep(FMH, '''	[[nodiscard]] Buffer* GetFaultBuffer() noexcept { return &m_fault_buffer; }
	void                  ProcessFaultBuffer();
''', '''	[[nodiscard]] Buffer* GetFaultBuffer() noexcept { return &m_fault_buffer; }
	void                  ProcessFaultBuffer();
	// KYTY_BVH_LOOP_CAP: zero the counter tail after the fault bitmap (needs a command buffer,
	// so the buffer cache calls it at its first registration, like the null page).
	void ClearLoopTripTail();
''')
rep(FMH, '''	std::array<uint64_t, MaxPendingFaults>      m_fault_areas {};
''', '''	std::array<uint64_t, MaxPendingFaults>      m_fault_areas {};
	Buffer                                     m_trip_download;
	std::array<uint32_t, 16>                   m_trip_last {};
	uint32_t                                   m_trip_lines = 0;
''')

# --- faultManager.cpp
rep(FMC, '''#include "graphics/host_gpu/vulkanCommon.h"
''', '''#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"
''')
rep(FMC, '''constexpr size_t MaxPageFaults    = 1024;
constexpr size_t PageFaultAreaSize = MaxPageFaults * sizeof(uint64_t);
''', '''constexpr size_t MaxPageFaults    = 1024;
constexpr size_t PageFaultAreaSize = MaxPageFaults * sizeof(uint64_t);

namespace LoopCap = ShaderRecompiler::Spirv::Emitter;

// KYTY_BVH_LOOP_CAP counters: LoopTripWords u32 right after the bitmap of CACHING_NUMPAGES bits.
constexpr uint64_t LoopTripOffset = BufferCache::CACHING_NUMPAGES / 8;
constexpr uint64_t LoopTripBytes  = LoopCap::LoopTripWords * sizeof(uint32_t);
static_assert(LoopTripOffset == uint64_t {LoopCap::LoopTripWordBase} * sizeof(uint32_t));
''')
rep(FMC, '''      m_fault_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 0, AllFlags,
                     BufferCache::CACHING_NUMPAGES / 8),
      m_download_buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
                        MaxPendingFaults * PageFaultAreaSize) {
	SetVulkanObjectNameF(m_graphics.device, m_fault_buffer.Handle(), "Fault Buffer");
''', '''      m_fault_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 0, AllFlags,
                     LoopTripOffset + LoopTripBytes),
      m_download_buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
                        MaxPendingFaults * PageFaultAreaSize),
      m_trip_download(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
                      MaxPendingFaults * LoopTripBytes) {
	SetVulkanObjectNameF(m_graphics.device, m_fault_buffer.Handle(), "Fault Buffer");
	LOGF("BvhLoopCap: cap=%u token='%s' default_slot0=%d@NL@", LoopCap::BvhLoopCap(),
	     LoopCap::BvhLoopCapSignatureToken().c_str(), LoopCap::BvhLoopCapSlot(0x380bb9d636390baeull));
'''.replace('@NL@', NL))
rep(FMC, '''void FaultManager::ProcessFaultBuffer() {''', '''void FaultManager::ClearLoopTripTail() {
	m_fault_buffer.Fill(LoopTripOffset, LoopTripBytes, 0);
}

void FaultManager::ProcessFaultBuffer() {''')
rep(FMC, '''	dependency.pBufferMemoryBarriers = &post_barrier;
	command.pipelineBarrier2(dependency);

	const auto area = m_current_area;
	m_scheduler.DeferOperation([this, mapped, offset, area] {''', '''	dependency.pBufferMemoryBarriers = &post_barrier;
	command.pipelineBarrier2(dependency);

	// KYTY_BVH_LOOP_CAP: copy the counter tail next to the fault list; the counters only grow,
	// so each readback is diffed against the largest values already seen.
	const bool trips       = LoopCap::BvhLoopCap() != 0;
	const auto trip_offset = m_current_area * LoopTripBytes;
	if (trips) {
		vk::BufferMemoryBarrier2 tail_barrier {};
		tail_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eAllCommands;
		tail_barrier.srcAccessMask = vk::AccessFlagBits2::eShaderWrite;
		tail_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eCopy;
		tail_barrier.dstAccessMask = vk::AccessFlagBits2::eTransferRead;
		tail_barrier.buffer        = m_fault_buffer.Handle();
		tail_barrier.offset        = LoopTripOffset;
		tail_barrier.size          = LoopTripBytes;
		vk::BufferMemoryBarrier2 host_barrier {};
		host_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eCopy;
		host_barrier.srcAccessMask = vk::AccessFlagBits2::eTransferWrite;
		host_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eHost;
		host_barrier.dstAccessMask = vk::AccessFlagBits2::eHostRead;
		host_barrier.buffer        = m_trip_download.Handle();
		host_barrier.offset        = trip_offset;
		host_barrier.size          = LoopTripBytes;
		vk::DependencyInfo tail_dependency {};
		tail_dependency.bufferMemoryBarrierCount = 1;
		tail_dependency.pBufferMemoryBarriers    = &tail_barrier;
		command.pipelineBarrier2(tail_dependency);
		const vk::BufferCopy region {LoopTripOffset, trip_offset, LoopTripBytes};
		command.copyBuffer(m_fault_buffer.Handle(), m_trip_download.Handle(), 1, &region);
		tail_dependency.pBufferMemoryBarriers = &host_barrier;
		command.pipelineBarrier2(tail_dependency);
	}

	const auto area = m_current_area;
	m_scheduler.DeferOperation([this, mapped, offset, area, trips, trip_offset] {
		if (trips) {
			m_trip_download.Invalidate(trip_offset, LoopTripBytes);
			std::array<uint32_t, LoopCap::LoopTripWords> words {};
			std::memcpy(words.data(), m_trip_download.Mapped().data() + trip_offset,
			            LoopTripBytes);
			const auto grown = [&](uint32_t index) {
				const uint32_t delta =
				    words[index] > m_trip_last[index] ? words[index] - m_trip_last[index] : 0;
				m_trip_last[index] = std::max(m_trip_last[index], words[index]);
				return delta;
			};
			const auto trip_delta = grown(0);
			const auto near_delta = grown(1);
			(void)grown(2);
			for (uint32_t slot = 0; slot < LoopCap::LoopTripSlots; slot++) {
				(void)grown(8 + slot);
			}
			Common::FrameStats::Add(Common::FrameStats::Counter::LoopCapTrips, trip_delta);
			Common::FrameStats::Add(Common::FrameStats::Counter::LoopCapNear, near_delta);
			if ((trip_delta != 0 || near_delta != 0) && m_trip_lines < 64) {
				m_trip_lines++;
				LOGF("BvhLoopCapTrip: trips=+%u total=%u near=+%u near_total=%u max_spent=%u "
				     "cap=%u slot0=%u slot1=%u@NL@",
				     trip_delta, m_trip_last[0], near_delta, m_trip_last[1], m_trip_last[2],
				     LoopCap::BvhLoopCap(), m_trip_last[8], m_trip_last[9]);
			}
		}'''.replace('@NL@', NL))
rep(FMC, '''#include <bit>
#include <cinttypes>''', '''#include <algorithm>
#include <bit>
#include <cinttypes>''')

# --- bufferCache.cpp: zero the tail at the first registration, with the null page.
rep(BCC, '''			m_bda_null_page_ready = true;
			m_bda_null_page.Fill(0, CACHING_PAGESIZE, 0);
''', '''			m_bda_null_page_ready = true;
			m_bda_null_page.Fill(0, CACHING_PAGESIZE, 0);
			m_fault_manager.ClearLoopTripTail();
''')

# --- counters
rep(FSH, '''	DrawAheadQueueCalls,     // da_qcall
	Count
};''', '''	DrawAheadQueueCalls,     // da_qcall
	// Session 103, KYTY_BVH_LOOP_CAP: invocations of a capped BVH program that exhausted their
	// step budget (bl_trip) and that returned normally after spending more than 1/16 of it
	// (bl_near), read back from the fault-buffer tail by ProcessFaultBuffer. Raw counts; they
	// land 1-3 flips after the dispatch.
	LoopCapTrips,            // bl_trip
	LoopCapNear,             // bl_near
	Count
};''')
rep(VOC, '''				    {"da_qcall", FS::Counter::DrawAheadQueueCalls, false},
''', '''				    {"da_qcall", FS::Counter::DrawAheadQueueCalls, false},
				    // Session 103, KYTY_BVH_LOOP_CAP: capped BVH invocations that tripped / came
				    // near the cap (1/16).  Raw counts.
				    {"bl_trip", FS::Counter::LoopCapTrips, false},
				    {"bl_near", FS::Counter::LoopCapNear, false},
''')

if DRY:
    print('DRY ok', sorted(files))
else:
    for rel, b in files.items():
        open(SRC + rel, 'wb').write(b.encode('utf-8'))
    print('written', sorted(files))
