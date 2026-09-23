"""Session 107: (a) plkstat holder/spin instrument, (b) knob cspmemo (compute-prefetch memo on the walker).
ROADMAP "СЕССИЯ 107 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 1 (commit a74ef62).  Anchored, CRLF-safe.
    python C:/kyty/s106_stage/patch_s107.py [--dry]
"""
import re
import sys

ROOT = 'C:/kyty/KytyPS5/src/'
DRY = '--dry' in sys.argv
NL = chr(10)


def patch(rel, edits, regex_edits=()):
    path = ROOT + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', NL)
    for old, new in edits:
        if text.count(old) != 1:
            raise SystemExit('%s: anchor found %d times: %r' % (rel, text.count(old), old[:90]))
        text = text.replace(old, new)
    for pattern, repl, want in regex_edits:
        text, n = re.subn(pattern, repl, text)
        if n != want:
            raise SystemExit('%s: regex %r matched %d, want %d' % (rel, pattern, n, want))
    if crlf:
        text = text.replace(NL, '\r\n')
    if not DRY:
        open(path, 'wb').write(text.encode('utf-8'))
    print('ok', rel)


# ---------------------------------------------------------------- gates
patch('common/gates.h', [
    ('''	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CtxTick,          // KYTY_CTX_TICK,           file name "ctxtick" (0 old, 1 buffer, 2 + check, 3 + exit)
	Count,''', '''	CtxTick,          // KYTY_CTX_TICK,           file name "ctxtick" (0 old, 1 buffer, 2 + check, 3 + exit)
	// Session 107: the compute-prefetch memo of PipelineCache::PrefetchComputePipeline (the
	// dawalk walker's second hold of PipelineCache::m_mutex).  0 = off; 1 = SHADOW (the key is
	// built and looked up, nothing is skipped: cspm_look / cspm_would); 2 = SKIP (a hit returns
	// before the lock and before ProgramCache::Get); 3 = skip-and-verify (a hit still runs the
	// locked path and compares the program id: cspm_bad, "CspMemoVerify:").  The memo is only a
	// hint - the dispatch always runs its own Get / GetComputePipeline - so a stale entry costs a
	// missed prefetch, never a wrong result.  Read once per prefetch call.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CsPrefetchMemo,   // KYTY_CS_PREFETCH_MEMO,   file name "cspmemo" (0 off, 1 shadow, 2 skip, 3 skip + verify)
	Count,'''),
])
patch('common/gates.cpp', [
    ('''    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_CTX_TICK", "ctxtick", 1, 3},
}};''', '''    {"KYTY_CTX_TICK", "ctxtick", 1, 3},
    // Session 107: compute-prefetch memo on the walker; 0 = off (today).  Read once per prefetch
    // call, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_CS_PREFETCH_MEMO", "cspmemo", 0, 3},
}};'''),
])

# ---------------------------------------------------------------- counters
patch('common/frameStats.h', [
    ('''	GpuWallCmdN,             // gw_cmd_n
	Count
};''', '''	GpuWallCmdN,             // gw_cmd_n
	// Session 107, gate "plkstat" (measurement only): GuestGpu's CONTENDED acquisitions of
	// PipelineCache::m_mutex at its three plkstat sites (a TryLock failed first): the count, the
	// wall and the thread CPU (ThreadCpuNs(Gpu)) around the blocking Lock - cpu / wall is the spin
	// share - and the same split by the holder tag read at the failed try (0 untagged, 1 walker
	// QueueDrawAhead, 2 walker PrefetchComputePipeline, 3 compute-pipeline compile completion).
	// Plus the walker's own holds, timed after its LockGuard.  Raw ns / counts.
	PipeLockContN,           // pl_cont_n
	PipeLockContWallNs,      // pl_cont_wall_ns
	PipeLockContCpuNs,       // pl_cont_cpu_ns
	PipeLockContH0N,         // pl_cont_h0_n
	PipeLockContH0Ns,        // pl_cont_h0_ns
	PipeLockContH1N,         // pl_cont_h1_n
	PipeLockContH1Ns,        // pl_cont_h1_ns
	PipeLockContH2N,         // pl_cont_h2_n
	PipeLockContH2Ns,        // pl_cont_h2_ns
	PipeLockContH3N,         // pl_cont_h3_n
	PipeLockContH3Ns,        // pl_cont_h3_ns
	PipeLockWalkQueueHoldNs, // pl_wq_hold_ns
	PipeLockWalkQueueHoldN,  // pl_wq_hold_n
	PipeLockWalkPrefHoldNs,  // pl_wp_hold_ns
	PipeLockWalkPrefHoldN,   // pl_wp_hold_n
	// Session 107, knob "cspmemo": the compute-prefetch memo.  Raw counts.
	CspMemoLook,             // cspm_look: prefetch calls that built a key (knob != 0)
	CspMemoWould,            // cspm_would: ... that found it (a skip at knob 2/3)
	CspMemoSkip,             // cspm_skip: calls returned early (knob 2)
	CspMemoBad,              // cspm_bad: knob 3 - the locked path disagreed with the memo
	CspMemoStore,            // cspm_store: entries written
	CspMemoClear,            // cspm_clear: memo cleared (stamp moved or full)
	CspPrefHave,             // cspf_have: locked prefetches whose program already had a pipeline
	CspPrefNew,              // cspf_new: ... that queued a new pipeline
	Count
};'''),
])

patch('graphics/presentation/videoOut.cpp', [
    ('''				    {"gw_cmd_n", FS::Counter::GpuWallCmdN, false},
				};''', '''				    {"gw_cmd_n", FS::Counter::GpuWallCmdN, false},
				    // Session 107, gate "plkstat": contended m_mutex acquisitions of GuestGpu and the
				    // walker's holds; knob "cspmemo": the compute-prefetch memo.  Raw ns / counts.
				    {"pl_cont_n", FS::Counter::PipeLockContN, false},
				    {"pl_cont_wall_ns", FS::Counter::PipeLockContWallNs, false},
				    {"pl_cont_cpu_ns", FS::Counter::PipeLockContCpuNs, false},
				    {"pl_cont_h0_n", FS::Counter::PipeLockContH0N, false},
				    {"pl_cont_h0_ns", FS::Counter::PipeLockContH0Ns, false},
				    {"pl_cont_h1_n", FS::Counter::PipeLockContH1N, false},
				    {"pl_cont_h1_ns", FS::Counter::PipeLockContH1Ns, false},
				    {"pl_cont_h2_n", FS::Counter::PipeLockContH2N, false},
				    {"pl_cont_h2_ns", FS::Counter::PipeLockContH2Ns, false},
				    {"pl_cont_h3_n", FS::Counter::PipeLockContH3N, false},
				    {"pl_cont_h3_ns", FS::Counter::PipeLockContH3Ns, false},
				    {"pl_wq_hold_ns", FS::Counter::PipeLockWalkQueueHoldNs, false},
				    {"pl_wq_hold_n", FS::Counter::PipeLockWalkQueueHoldN, false},
				    {"pl_wp_hold_ns", FS::Counter::PipeLockWalkPrefHoldNs, false},
				    {"pl_wp_hold_n", FS::Counter::PipeLockWalkPrefHoldN, false},
				    {"cspm_look", FS::Counter::CspMemoLook, false},
				    {"cspm_would", FS::Counter::CspMemoWould, false},
				    {"cspm_skip", FS::Counter::CspMemoSkip, false},
				    {"cspm_bad", FS::Counter::CspMemoBad, false},
				    {"cspm_store", FS::Counter::CspMemoStore, false},
				    {"cspm_clear", FS::Counter::CspMemoClear, false},
				    {"cspf_have", FS::Counter::CspPrefHave, false},
				    {"cspf_new", FS::Counter::CspPrefNew, false},
				};'''),
])

# ---------------------------------------------------------------- pipeline cache
patch('graphics/host_gpu/renderer/pipeline/pipelineCache.h', [
    ('''	std::unordered_map<uint64_t, std::unique_ptr<ComputePipelineEntry>> m_compute_pipelines;
	Common::Mutex m_mutex;''', '''	std::unordered_map<uint64_t, std::unique_ptr<ComputePipelineEntry>> m_compute_pipelines;
	Common::Mutex m_mutex;
	// Session 107, gate "plkstat": who holds m_mutex, written by the tagged holders while they
	// hold it (1 walker QueueDrawAhead, 2 walker PrefetchComputePipeline, 3 compute-pipeline
	// compile completion; 0 = untagged), read by GuestGpu when its TryLock fails.
	std::atomic<uint8_t> m_lock_holder {0};'''),
])

HELPERS = '''namespace Libs::Graphics {

namespace {

// Session 107: bumped next to every ProgramCache::programs_epoch++ (an entry inserted into or
// extracted from `programs`), readable outside PipelineCache::m_mutex - the stamp of the
// knob "cspmemo" memo.
std::atomic<uint64_t> g_programs_epoch_mirror {0};

// Session 107, gate "plkstat": GuestGpu's acquisition of PipelineCache::m_mutex at a plkstat
// site.  Measured only on the GuestGpu thread with the gate armed: a TryLock first; only when it
// fails, the holder tag, the wall and the thread CPU around the blocking Lock (CPU / wall = the
// spin share of the CRITICAL_SECTION).  Otherwise exactly Common::LockGuard.
class PipeLockMeasured {
public:
	PipeLockMeasured(Common::Mutex& mutex, bool measure, const std::atomic<uint8_t>& holder)
	    : m_mutex(mutex) {
		namespace FS = Common::FrameStats;
		if (!measure || FS::CurrentRole() != FS::ThreadRole::Gpu) {
			m_mutex.Lock();
			return;
		}
		if (m_mutex.TryLock()) {
			return;
		}
		const auto tag  = holder.load(std::memory_order_relaxed);
		const auto t0   = FS::NowNs();
		const auto cpu0 = FS::ThreadCpuNs(FS::ThreadRole::Gpu);
		m_mutex.Lock();
		const auto cpu1 = FS::ThreadCpuNs(FS::ThreadRole::Gpu);
		const auto wall = FS::NowNs() - t0;
		FS::Add(FS::Counter::PipeLockContN, 1);
		FS::Add(FS::Counter::PipeLockContWallNs, wall);
		FS::Add(FS::Counter::PipeLockContCpuNs, cpu1 > cpu0 && cpu0 != 0 ? cpu1 - cpu0 : 0);
		static constexpr std::array<FS::Counter, 4> tag_n {
		    FS::Counter::PipeLockContH0N, FS::Counter::PipeLockContH1N, FS::Counter::PipeLockContH2N,
		    FS::Counter::PipeLockContH3N};
		static constexpr std::array<FS::Counter, 4> tag_ns {
		    FS::Counter::PipeLockContH0Ns, FS::Counter::PipeLockContH1Ns,
		    FS::Counter::PipeLockContH2Ns, FS::Counter::PipeLockContH3Ns};
		const auto slot = tag < 4 ? tag : 0u;
		FS::Add(tag_n[slot], 1);
		FS::Add(tag_ns[slot], wall);
	}
	~PipeLockMeasured() {
		m_mutex.Unlock();
	}
	PipeLockMeasured(const PipeLockMeasured&)            = delete;
	PipeLockMeasured& operator=(const PipeLockMeasured&) = delete;

private:
	Common::Mutex& m_mutex;
};

// Session 107, gate "plkstat": a tagged holder of PipelineCache::m_mutex.  Constructed right
// after the LockGuard (so destroyed before the unlock): publishes the tag for the whole hold and,
// when `hold_ns` is given, times the hold itself (not the wait for the lock).
class PipeLockHolder {
public:
	PipeLockHolder(std::atomic<uint8_t>& holder, uint8_t tag,
	               Common::FrameStats::Counter hold_ns = Common::FrameStats::Counter::Count,
	               Common::FrameStats::Counter hold_n  = Common::FrameStats::Counter::Count)
	    : m_holder(holder),
	      m_on(Common::Gates::Enabled(Common::Gates::Gate::PipeLockStat) &&
	           Common::FrameStats::Enabled()),
	      m_hold_ns(hold_ns),
	      m_hold_n(hold_n) {
		if (m_on) {
			m_holder.store(tag, std::memory_order_relaxed);
			m_t0 = hold_ns != Common::FrameStats::Counter::Count ? Common::FrameStats::NowNs() : 0;
		}
	}
	~PipeLockHolder() {
		if (m_on) {
			if (m_t0 != 0) {
				Common::FrameStats::Add(m_hold_ns, Common::FrameStats::NowNs() - m_t0);
				Common::FrameStats::Add(m_hold_n, 1);
			}
			m_holder.store(0, std::memory_order_relaxed);
		}
	}
	PipeLockHolder(const PipeLockHolder&)            = delete;
	PipeLockHolder& operator=(const PipeLockHolder&) = delete;

private:
	std::atomic<uint8_t>&       m_holder;
	bool                        m_on;
	Common::FrameStats::Counter m_hold_ns;
	Common::FrameStats::Counter m_hold_n;
	uint64_t                    m_t0 = 0;
};

// Session 107, knob "cspmemo": per-thread memo of compute prefetches whose program already had
// a pipeline.  Key: the translated code (hash and base), the user SGPRs and the stage's static
// key; value: the program id.  Stamp: g_programs_epoch_mirror and ShaderRegistrations(); a moved
// stamp or a full table clears it.  Only ever a hint (see Knob::CsPrefetchMemo).
struct CsPrefetchMemo {
	static constexpr size_t Capacity = 4096;
	std::unordered_map<uint64_t, uint64_t> ids;
	uint64_t                               epoch = UINT64_MAX;
	uint64_t                               registrations = UINT64_MAX;
	std::vector<uint32_t>                  key_words;

	void Restamp(uint64_t now_epoch, uint64_t now_registrations) {
		if (now_epoch != epoch || now_registrations != registrations || ids.size() >= Capacity) {
			if (!ids.empty()) {
				Common::FrameStats::Add(Common::FrameStats::Counter::CspMemoClear, 1);
			}
			ids.clear();
			epoch         = now_epoch;
			registrations = now_registrations;
		}
	}
};

CsPrefetchMemo& ThreadCsPrefetchMemo() {
	thread_local CsPrefetchMemo memo;
	return memo;
}

'''

patch('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    ('''namespace Libs::Graphics {

namespace {

''', HELPERS),
    # GuestGpu sites: measured acquisition under plkstat
    ('''	Common::LockGuard lock(m_mutex);
	Common::FrameStats::LockSplit prog_lock_split(''', '''	PipeLockMeasured lock(m_mutex, prog_lock_t0 != 0, m_lock_holder);
	Common::FrameStats::LockSplit prog_lock_split('''),
    ('''	Common::LockGuard lock(m_mutex);
	Common::FrameStats::LockSplit cs_lock_split(''', '''	PipeLockMeasured lock(m_mutex, cs_lock_t0 != 0, m_lock_holder);
	Common::FrameStats::LockSplit cs_lock_split('''),
    ('''		Common::LockGuard lock(m_mutex);
		Common::FrameStats::LockSplit pipe_lock_split(''', '''		PipeLockMeasured lock(m_mutex, pipe_lock_t0 != 0, m_lock_holder);
		Common::FrameStats::LockSplit pipe_lock_split('''),
    # walker QueueDrawAhead hold
    ('''	Common::LockGuard lock(m_mutex);
	m_program_cache->QueueAhead(requests, walk);''', '''	Common::LockGuard lock(m_mutex);
	PipeLockHolder    holder(m_lock_holder, 1, Common::FrameStats::Counter::PipeLockWalkQueueHoldNs,
	                         Common::FrameStats::Counter::PipeLockWalkQueueHoldN);
	m_program_cache->QueueAhead(requests, walk);'''),
    # PrefetchComputePipeline: memo + tagged hold + outcome counters
    ('''	input_info.host_subgroup_size = m_graphics.SupportsComputeWave64() ? 64u : 32u;
	const auto params             = PrepareProgram(regs, sh, input_info);
	Common::LockGuard lock(m_mutex);
	uint32_t          push_data_cursor = 0;
	const auto        program = m_program_cache->Get(params, input_info, push_data_cursor, true);''',
     '''	input_info.host_subgroup_size = m_graphics.SupportsComputeWave64() ? 64u : 32u;
	const auto params             = PrepareProgram(regs, sh, input_info);
	// Session 107, knob "cspmemo": look the prefetch up before taking the lock.
	const auto memo_mode = Common::Gates::Value(Common::Gates::Knob::CsPrefetchMemo);
	uint64_t   memo_key  = 0;
	uint64_t   memo_id   = 0;
	bool       memo_hit  = false;
	if (memo_mode != 0) {
		auto& memo = ThreadCsPrefetchMemo();
		memo.Restamp(g_programs_epoch_mirror.load(std::memory_order_acquire), ShaderRegistrations());
		memo.key_words.clear();
		BuildStageStaticKey(input_info, memo.key_words);
		uint64_t seed = XXH3_64bits_withSeed(memo.key_words.data(), memo.key_words.size() * sizeof(uint32_t),
		                                     params.hash ^ 0x6373706d656d6fULL);
		seed          = XXH3_64bits_withSeed(params.user_data.words.data(),
		                                     size_t {params.user_data.count} * sizeof(uint32_t), seed ^ params.Base());
		memo_key      = seed;
		Common::FrameStats::Add(Common::FrameStats::Counter::CspMemoLook, 1);
		if (const auto it = memo.ids.find(memo_key); it != memo.ids.end()) {
			memo_hit = true;
			memo_id  = it->second;
			Common::FrameStats::Add(Common::FrameStats::Counter::CspMemoWould, 1);
			if (memo_mode == 2) {
				Common::FrameStats::Add(Common::FrameStats::Counter::CspMemoSkip, 1);
				return;
			}
		}
	}
	Common::LockGuard lock(m_mutex);
	PipeLockHolder    holder(m_lock_holder, 2, Common::FrameStats::Counter::PipeLockWalkPrefHoldNs,
	                         Common::FrameStats::Counter::PipeLockWalkPrefHoldN);
	uint32_t          push_data_cursor = 0;
	const auto        program = m_program_cache->Get(params, input_info, push_data_cursor, true);
	const auto memo_store = [&](uint64_t id) {
		if (memo_mode == 0) {
			return;
		}
		if (memo_mode == 3 && memo_hit && memo_id != id) {
			Common::FrameStats::Add(Common::FrameStats::Counter::CspMemoBad, 1);
			static std::atomic<uint32_t> bad_log {0};
			if (bad_log.fetch_add(1, std::memory_order_relaxed) < 40) {
				LOGF("CspMemoVerify: MISMATCH hash=0x%016" PRIx64 " memo_id=%" PRIu64 " id=%" PRIu64 "\\n",
				     params.hash, memo_id, id);
			}
		}
		ThreadCsPrefetchMemo().ids[memo_key] = id;
		Common::FrameStats::Add(Common::FrameStats::Counter::CspMemoStore, 1);
	};'''),
    ('''	if (m_compute_pipelines.contains(program.id)) {
		return;
	}
	if (log) {
		LOGF("AsyncCompute: prefetch hash=0x%016" PRIx64 " id=%" PRIu64 " queued\\n", params.hash, program.id);
	}''', '''	if (m_compute_pipelines.contains(program.id)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefHave, 1);
		memo_store(program.id);
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefNew, 1);
	if (log) {
		LOGF("AsyncCompute: prefetch hash=0x%016" PRIx64 " id=%" PRIu64 " queued\\n", params.hash, program.id);
	}'''),
    ('''	m_compute_pipelines.emplace(program.id, std::move(entry));
	m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);''', '''	m_compute_pipelines.emplace(program.id, std::move(entry));
	memo_store(program.id);
	m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);'''),
    # compile completion: tag 3
    ('''		{
			Common::LockGuard lock(m_mutex);
			if (AvTraceEnabled()) {
				LOGF("AvTrace: pipeline cs cs=%" PRIu64''', '''		{
			Common::LockGuard lock(m_mutex);
			PipeLockHolder    holder(m_lock_holder, 3);
			if (AvTraceEnabled()) {
				LOGF("AvTrace: pipeline cs cs=%" PRIu64'''),
], regex_edits=[
    (r'(\n(\t+))programs_epoch\+\+;', r'\1programs_epoch++;\1g_programs_epoch_mirror.fetch_add(1, std::memory_order_release);', 4),
])
