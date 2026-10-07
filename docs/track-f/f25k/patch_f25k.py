# F25k (HPP-678, ROADMAP s122 item 613(v)(1)-(7), (g)(1)): KYTY_FIX_B36 (async log writer), KYTY_TEST_LOGSTALL,
# KYTY_LONGFRAME, the tests log_async_tests. Usage: python patch_f25k.py <repo root> [--ref]
#   --ref: only the test target (without KYTY_LOG_ASYNC_TESTS) and tests/LogAsyncTests.cpp - the reference build of the
#          code before F25k (the "=0 byte for byte with the old code" case).
# Anchors are whole lines; each must occur exactly once; files are LF (asserted); written with write_bytes.
import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
root = Path(sys.argv[1])
ref = '--ref' in sys.argv[2:]

OLD_LOG_CPP = '455c7fde3ca7c834e2af09448a0fa1c0ca8fc7ac3eb790d7a70dfc35bcc2b6a5'
OLD_LOG_H = '518231b09835406b842f1bc984939154a69d4ab05ee7e90e411b9fa48bde14f7'


def rd(rel):
    b = (root / rel).read_bytes()
    assert b'\r' not in b, rel + ': CR'
    return b.decode('utf-8')


def wr(rel, text):
    (root / rel).write_bytes(text.encode('utf-8'))
    print('patched', rel)


def once(text, anchor, rel):
    n = text.count(anchor)
    assert n == 1, '%s: anchor count %d: %r' % (rel, n, anchor[:80])


def insert_after(rel, anchor, add):
    t = rd(rel)
    once(t, anchor, rel)
    wr(rel, t.replace(anchor, anchor + add))


def insert_before(rel, anchor, add):
    t = rd(rel)
    once(t, anchor, rel)
    wr(rel, t.replace(anchor, add + anchor))


# ------------------------------------------------------------------------------------------------ CMake + the tests
CMAKE_ANCHOR = '''add_executable(image_page_table_tests EXCLUDE_FROM_ALL
	"${KYTY_TESTS_DIR}/ImagePageTableTests.cpp"
)
target_link_libraries(image_page_table_tests common fmt::fmt)
target_include_directories(image_page_table_tests PRIVATE ${inc_headers})
'''
CMAKE_ADD = '''
# Track F, F25k (HPP-678, ROADMAP s122 item 613(g)(1)): KYTY_FIX_B36 (the async log writer) without the game - the order
# of the lines, the wait on overflow, the drain on every death path (child processes), =0 byte for byte; run by
# docs/track-f/f25k/run_tests_f25k.py, not by ctest.
add_executable(log_async_tests EXCLUDE_FROM_ALL
	"${KYTY_TESTS_DIR}/LogAsyncTests.cpp"
)
target_link_libraries(log_async_tests common fmt::fmt)
target_include_directories(log_async_tests PRIVATE ${inc_headers})
target_compile_definitions(log_async_tests PRIVATE KYTY_LOG_ASYNC_TESTS=1)
'''
if ref:
    CMAKE_ADD = CMAKE_ADD.replace('target_compile_definitions(log_async_tests PRIVATE KYTY_LOG_ASYNC_TESTS=1)\n', '')
insert_after('CMakeLists.txt', CMAKE_ANCHOR, CMAKE_ADD)
(root / 'tests/LogAsyncTests.cpp').write_bytes((HERE / 'LogAsyncTests.cpp').read_bytes().replace(b'\r', b''))
print('written tests/LogAsyncTests.cpp')
if ref:
    print('REF OK')
    sys.exit(0)

# ------------------------------------------------------------------------------------------------ log.cpp, log.h
assert hashlib.sha256((root / 'src/common/logging/log.cpp').read_bytes()).hexdigest() == OLD_LOG_CPP, 'log.cpp is not the base'
assert hashlib.sha256((root / 'src/common/logging/log.h').read_bytes()).hexdigest() == OLD_LOG_H, 'log.h is not the base'
(root / 'src/common/logging/log.cpp').write_bytes((HERE / 'log.cpp').read_bytes().replace(b'\r', b''))
print('written src/common/logging/log.cpp')

insert_after('src/common/logging/log.h', 'void      Flush();\n', '''// Track F, F25k (KYTY_FIX_B36, ROADMAP s122 item 613(v)(4)): the queue of the async log writer reaches the file before a
// process end that skips Log::Shutdown (the std::_Exit sites); the writer stops. No-op at KYTY_FIX_B36=0.
void      DrainForExit() noexcept;
// The same without stopping the writer: the unresolved branch of the host exception filter (the process may live on).
void      DrainForFault() noexcept;
// KYTY_FIX_B36=1 in effect (the File direction): the "log_async" field of the "LongFrame:" line.
bool      AsyncEnabled();
namespace Testing {
// log_async_tests only: the 256 MiB limit of the queue replaced.
void SetAsyncLimit(uint64_t bytes);
} // namespace Testing
''')

# ------------------------------------------------------------------------------------------------ the death sites
insert_after('src/common/hostException.cpp', '''		        static_cast<unsigned long long>(info.rsp));
		fflush(stderr);
''', '''		// Track F, F25k (KYTY_FIX_B36, ROADMAP s122 item 613(v)(4)): the queue of the async log writer reaches the file
		// (the process may end here); no-op at KYTY_FIX_B36=0.
		Log::DrainForFault();
''')

insert_before('src/graphics/host_gpu/pageManager.cpp', '''#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	TerminateProcess(GetCurrentProcess(), static_cast<UINT>(EXCEPTION_NONCONTINUABLE_EXCEPTION));
#endif
	std::_Exit(322);
''', '''	Log::DrainForExit(); // Track F, F25k (KYTY_FIX_B36): the async log queue to the file; no-op at =0
''')
insert_before('src/graphics/host_gpu/pageManager.cpp', '''	std::fputc('\\n', stderr);
	std::fflush(stderr);
	std::_Exit(322);
}
''', '''	Log::DrainForExit(); // Track F, F25k (KYTY_FIX_B36): the async log queue to the file; no-op at =0
''')

insert_after('src/common/parallelCopy.cpp', '#include "common/gates.h"\n', '#include "common/logging/log.h" // Track F, F25k (Log::DrainForExit)\n')
insert_before('src/common/parallelCopy.cpp', '''			std::fflush(stderr);
			std::_Exit(322);
''', '''			Log::DrainForExit(); // Track F, F25k (KYTY_FIX_B36): the async log queue to the file; no-op at =0
''')

# ------------------------------------------------------------------------------------------------ LongFrame
insert_before('src/graphics/presentation/videoOut.cpp', '''	if (Common::FrameStats::Enabled()) {
		namespace FS = Common::FrameStats;
		struct Snapshot {
''', '''	// Track F, F25k (KYTY_LONGFRAME=1, ROADMAP s122 item 613(v)(7); measurement only, default 0): a flip >= 100 ms after the
	// previous one - a "LongFrame:" line (at most 4 096), without KYTY_FRAME_TRACE. The clock and the point are those of
	// dt_us of the "FrameTrace:" line below: Common::FrameStats::NowNs on this Present thread after flip_status.count++,
	// under m_mutex. t_ms - the same clock, for the t0_ms / t1_ms of the stand's "TestLogStall:" line.
	{
		static const bool long_frame = Common::EnvFlagOn("KYTY_LONGFRAME");
		if (long_frame) [[unlikely]] {
			static uint64_t long_frame_prev_ns = 0;
			static uint32_t long_frame_lines   = 0;
			const uint64_t  now_ns             = Common::FrameStats::NowNs();
			if (long_frame_prev_ns != 0 && now_ns - long_frame_prev_ns >= 100000000u && long_frame_lines < 4096) {
				long_frame_lines++;
				LOGF("LongFrame: n=%" PRIu64 " dt_us=%llu log_async=%d t_ms=%llu\\n", r.cfg->flip_status.count,
				     static_cast<unsigned long long>((now_ns - long_frame_prev_ns) / 1000u), Log::AsyncEnabled() ? 1 : 0,
				     static_cast<unsigned long long>(now_ns / 1000000u));
			}
			long_frame_prev_ns = now_ns;
		}
	}
''')
print('ALL PATCHED')
