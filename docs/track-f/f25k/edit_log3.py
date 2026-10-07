# F25k: the "TestLogStall:" line names the thread that slept - tid (OS thread id) and role (the FrameStats role:
# Main / Gpu / Present / Record, "other" when the thread is not registered) - so the reading of b36_s0 sees whether the
# sleep held the flip. Usage: edit_log3.py <log.cpp>...
import sys
edits = [
    ('''static void StandPoint(const std::shared_ptr<spdlog::logger>& logger) {
''', '''static const char* RoleName() {
	switch (Common::FrameStats::CurrentRole()) {
		case Common::FrameStats::ThreadRole::Main: return "Main";
		case Common::FrameStats::ThreadRole::Gpu: return "Gpu";
		case Common::FrameStats::ThreadRole::Present: return "Present";
		case Common::FrameStats::ThreadRole::Record: return "Record";
		default: return "other";
	}
}

static uint32_t OsTid() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	return static_cast<uint32_t>(GetCurrentThreadId());
#else
	return 0;
#endif
}

static void StandPoint(const std::shared_ptr<spdlog::logger>& logger) {
'''),
    ('''		const auto line = fmt::format("TestLogStall: i={} sleep_ms={} slept_us={} t0_ms={} t1_ms={} on={}\\n", i + 1,
		                              g_stand.sleep_ms, (t1 - t0) / 1000u, t0 / 1000000u, t1 / 1000000u,
		                              t_writer ? "writer" : "caller");
''', '''		const auto line = fmt::format("TestLogStall: i={} sleep_ms={} slept_us={} t0_ms={} t1_ms={} on={} tid={} role={}\\n",
		                              i + 1, g_stand.sleep_ms, (t1 - t0) / 1000u, t0 / 1000000u, t1 / 1000000u,
		                              t_writer ? "writer" : "caller", OsTid(), RoleName());
'''),
]
for p in sys.argv[1:]:
    t = open(p, 'rb').read().decode()
    assert '\r' not in t
    for old, new in edits:
        assert t.count(old) == 1, (p, old[:50])
        t = t.replace(old, new)
    open(p, 'wb').write(t.encode())
    print('ok', p)
