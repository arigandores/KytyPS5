"""Session 115, ROADMAP 0.1 "СЕССИЯ 115" item 1 (recorded first): the presentation record ring has one producer by
construction - the main thread no longer presents during WindowPrepareShaders (the VideoOut present thread already
presents the preparation overlay while it is active); before the SDL main loop runs, UpdateTitle always posts (nothing
needs the present thread parked any more); the preparation progress counters are atomic; KYTY_PREPARE_MAIN_PRESENT=1
(measurement only) restores the old main-thread present as the positive control of the ring owner check; the wait line
reports the preparation presents by thread.  Whole-line anchors, asserted.

    python C:/kyty/s106_stage/patch_s115a.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/graphics/presentation/systemOverlay.h'] = [
    ("""// Startup-only screen, set and rendered on the main thread before guest execution.
void SetShaderPreparationOverlay(bool active, uint32_t completed = 0, uint32_t total = 0);
bool ShaderPreparationOverlayActive() noexcept;
""",
     """// Startup-only screen, set by the main thread before guest execution and rendered by the VideoOut present thread
// (session 115: the main thread no longer presents it, unless KYTY_PREPARE_MAIN_PRESENT=1).
void SetShaderPreparationOverlay(bool active, uint32_t completed = 0, uint32_t total = 0);
bool ShaderPreparationOverlayActive() noexcept;
// Session 115: presents made while the preparation overlay is active, by the main thread and by any other thread.
void NoteShaderPreparationPresent(bool main_thread) noexcept;
void ShaderPreparationPresents(uint64_t& main_thread, uint64_t& other) noexcept;
"""),
]

EDITS['src/graphics/presentation/systemOverlay.cpp'] = [
    ("""std::atomic<bool> g_shader_preparation {false};
uint32_t g_shader_completed = 0;
uint32_t g_shader_total = 0;
""",
     """std::atomic<bool> g_shader_preparation {false};
// Session 115 (audit C-10): written by the main thread, read by the present thread that renders the overlay.
std::atomic<uint32_t> g_shader_completed {0};
std::atomic<uint32_t> g_shader_total {0};
std::atomic<uint64_t> g_prep_presents_main {0};
std::atomic<uint64_t> g_prep_presents_other {0};
"""),
    ("""void SetShaderPreparationOverlay(bool active, uint32_t completed, uint32_t total) {
	g_shader_completed = completed;
	g_shader_total = total;
	g_shader_preparation.store(active);
}
""",
     """void SetShaderPreparationOverlay(bool active, uint32_t completed, uint32_t total) {
	g_shader_completed.store(completed, std::memory_order_relaxed);
	g_shader_total.store(total, std::memory_order_relaxed);
	g_shader_preparation.store(active);
}

void NoteShaderPreparationPresent(bool main_thread) noexcept {
	(main_thread ? g_prep_presents_main : g_prep_presents_other).fetch_add(1, std::memory_order_relaxed);
}

void ShaderPreparationPresents(uint64_t& main_thread, uint64_t& other) noexcept {
	main_thread = g_prep_presents_main.load(std::memory_order_relaxed);
	other       = g_prep_presents_other.load(std::memory_order_relaxed);
}
"""),
    ("""			if (g_shader_total != 0) {
				const auto completed = std::min(g_shader_completed, g_shader_total);
""",
     """			const uint32_t shader_total = g_shader_total.load(std::memory_order_relaxed);
			if (shader_total != 0) {
				const auto completed = std::min(g_shader_completed.load(std::memory_order_relaxed), shader_total);
"""),
    ("""				snprintf(label, sizeof(label), "%u / %u", completed, g_shader_total);
				ImGui::ProgressBar(static_cast<float>(completed) / g_shader_total, {-1, 26.0f * scale}, label);
""",
     """				snprintf(label, sizeof(label), "%u / %u", completed, shader_total);
				ImGui::ProgressBar(static_cast<float>(completed) / static_cast<float>(shader_total), {-1, 26.0f * scale},
				                   label);
"""),
]

EDITS['src/graphics/presentation/window/swapchain.cpp'] = [
    ("""		present_inside_guard.Leave();
		if (!preparing) m_impl->window.UpdateTitle();
""",
     """		present_inside_guard.Leave();
		if (preparing) {
			NoteShaderPreparationPresent(Common::Thread::IsMainThread());
		}
		if (!preparing) m_impl->window.UpdateTitle();
"""),
]

EDITS['src/graphics/presentation/window/window.cpp'] = [
    ("""	// Session 114 (ROADMAP item 4, review C1): the async path only once the SDL main loop runs - before WindowRun the
	// waiting path parks the present thread, which keeps it out of Present while WindowPrepareShaders presents.
	const bool loop_running = main_loop_running.load(std::memory_order_acquire);
	const bool title_async  = loop_running && Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;
""",
     """	// Session 115 (ROADMAP item 1): before the SDL main loop runs the title is always posted - the main thread no longer
	// presents during WindowPrepareShaders, so nothing needs the present thread parked, and a parked present thread
	// could not present the preparation overlay.  Once the loop runs, the knob decides (session 114).
	const bool loop_running = main_loop_running.load(std::memory_order_acquire);
	const bool title_async  = !loop_running || Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;
"""),
    ("""	if (hold_ms != 0) {
		LOGF("PrepareHold: ms=%llu\\n", static_cast<unsigned long long>(hold_ms));
	}
""",
     """	if (hold_ms != 0) {
		LOGF("PrepareHold: ms=%llu\\n", static_cast<unsigned long long>(hold_ms));
	}
	// Session 115 (ROADMAP item 1): the VideoOut present thread presents the preparation overlay (the overlay makes
	// NeedsSystemOverlayRefresh true), so the presentation record ring keeps one producer.  KYTY_PREPARE_MAIN_PRESENT=1
	// (MEASUREMENT ONLY, read once) restores the old main-thread present - the positive control of the ring owner check.
	static const bool main_present = [] {
		const char* value = std::getenv("KYTY_PREPARE_MAIN_PRESENT");
		return value != nullptr && value[0] == '1' && value[1] == '\\0';
	}();
	if (main_present) {
		LOGF("PrepareMainPresent: mode 1\\n");
	}
"""),
    ("""		SetShaderPreparationOverlay(true, status.completed, status.total);
		auto& frame = g_window->presenter->PrepareBlankFrame(
		    g_window->graphic_ctx.screen_width, g_window->graphic_ctx.screen_height, true);
		g_window->presenter->Present(frame);
""",
     """		SetShaderPreparationOverlay(true, status.completed, status.total);
		if (main_present) {
			auto& frame = g_window->presenter->PrepareBlankFrame(
			    g_window->graphic_ctx.screen_width, g_window->graphic_ctx.screen_height, true);
			g_window->presenter->Present(frame);
		}
"""),
    ("""	LOGF("ShaderPreparation: startup wait finished in %" PRIu64 " ms\\n", SDL_GetTicks64() - started);
""",
     """	uint64_t presents_main  = 0;
	uint64_t presents_other = 0;
	ShaderPreparationPresents(presents_main, presents_other);
	LOGF("ShaderPreparation: startup wait finished in %" PRIu64 " ms presents_other=%" PRIu64 " presents_main=%" PRIu64
	     "\\n",
	     SDL_GetTicks64() - started, presents_other, presents_main);
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
            print('note: %s was CRLF in the working tree; written as LF (the repository form)' % rel)
        if not DRY:
            path.write_bytes(text.encode('utf-8'))
        print(('checked ' if DRY else 'patched ') + rel)


if __name__ == '__main__':
    main()
