# Track F, F5a (HPP-355): B37 - swapchain at a zero window extent under KYTY_FIX_MINIMIZE, stand KYTY_TEST_MINIMIZE.
# Anchors are whole lines; CRLF files keep CRLF; output is written with write_bytes.
import sys

ROOT = 'C:/kyty/KytyPS5/src/'


def load(path):
    raw = open(ROOT + path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    return text, crlf


def save(path, text, crlf):
    if crlf:
        text = text.replace('\n', '\r\n')
    open(ROOT + path, 'wb').write(text.encode('utf-8'))


def replace_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        print('ANCHOR FAIL', what, n)
        sys.exit(1)
    return text.replace(old, new)


# ---------------------------------------------------------------- swapchain.cpp
p = 'graphics/presentation/window/swapchain.cpp'
t, crlf = load(p)

t = replace_once(t, r'''class Swapchain final {
public:
''', r'''// Track F, F5 (ROADMAP s122 item 273(e)(1), B37): KYTY_FIX_MINIMIZE (default 0 until F5d; 0 - the old path byte for
// byte).  1: a swapchain recreate that finds currentExtent 0 on either axis (a minimized window) creates no swapchain;
// Presenter::Present drops its frames without blocking and retries on each later present until the extent is non-zero.
// Read once; "FixMinimize: on" is logged only when on.
static bool FixMinimizeEnabled() {
	static const bool enabled = [] {
		const bool on = Common::EnvFlagOn("KYTY_FIX_MINIMIZE");
		if (on) {
			LOGF("FixMinimize: on\n");
		}
		return on;
	}();
	return enabled;
}

class Swapchain final {
public:
''', 'class Swapchain')

t = replace_once(t, r'''	[[nodiscard]] vk::Format Format() const noexcept { return m_format; }
''', r'''	[[nodiscard]] vk::Format Format() const noexcept { return m_format; }
	// F5 (B37): no swapchain - only after a recreate at a zero extent under KYTY_FIX_MINIMIZE=1 (Create exits on failure).
	[[nodiscard]] bool Missing() const noexcept { return m_handle == nullptr; }
	// F5 (B37): the last refreshed surface capabilities have currentExtent 0 on either axis.
	[[nodiscard]] bool SurfaceExtentZero();
''', 'Format()')

t = replace_once(t, r'''		swapchain.Create();
		frames.Initialize(swapchain.ImageCount(), swapchain.Format());
	}
''', r'''		swapchain.Create();
		frames.Initialize(swapchain.ImageCount(), swapchain.Format());
		static_cast<void>(FixMinimizeEnabled());
	}
''', 'Impl ctor')

t = replace_once(t, r'''		swapchain.Recreate(status == Swapchain::Status::SurfaceLost);
		frames.SetFormat(swapchain.Format());
	}
''', r'''		swapchain.Recreate(status == Swapchain::Status::SurfaceLost);
		if (swapchain.Missing()) [[unlikely]] { // F5 (B37): KYTY_FIX_MINIMIZE=1 and a zero extent only
			BeginZeroExtent();
			return;
		}
		frames.SetFormat(swapchain.Format());
	}

	// F5 (B37): one zero-extent episode - it begins when a recreate leaves no swapchain and ends when a later present
	// finds a non-zero extent and creates the swapchain.  Present thread only (Present is single-threaded by design,
	// the PresentOverlap detector); the fields below are touched nowhere else.
	void BeginZeroExtent() {
		if (zero_extent_active) {
			return;
		}
		zero_extent_active  = true;
		zero_extent_dropped = 0;
		zero_extent_t0_ns   = Common::FrameStats::NowNs();
		LOGF("SwapchainZeroExtent: begin\n");
	}

	// False - the extent is still zero, the caller drops the frame.  True - the swapchain exists again.
	bool TryEndZeroExtent() {
		window.RefreshSurfaceCapabilities();
		if (swapchain.SurfaceExtentZero()) {
			return false;
		}
		swapchain.Create();
		frames.SetFormat(swapchain.Format());
		const auto ms = (Common::FrameStats::NowNs() - zero_extent_t0_ns) / 1000000ull;
		LOGF("SwapchainZeroExtent: end frames_dropped=%llu ms=%llu\n",
		     static_cast<unsigned long long>(zero_extent_dropped), static_cast<unsigned long long>(ms));
		zero_extent_active  = false;
		zero_extent_dropped = 0;
		return true;
	}
''', 'RecoverSwapchain')

t = replace_once(t, r'''	InputScript           input_script;
	std::atomic<uint64_t> presented_overlay_revision {0};
};
''', r'''	InputScript           input_script;
	std::atomic<uint64_t> presented_overlay_revision {0};
	// F5 (B37) episode state, present thread only (see BeginZeroExtent).
	bool                  zero_extent_active  = false;
	uint64_t              zero_extent_dropped = 0;
	uint64_t              zero_extent_t0_ns   = 0;
};
''', 'Impl fields')

t = replace_once(t, r'''	m_window.RefreshSurfaceCapabilities();
	Create();
}
''', r'''	m_window.RefreshSurfaceCapabilities();
	if (FixMinimizeEnabled() && SurfaceExtentZero()) {
		return; // F5 (B37): no swapchain at a zero extent; Presenter::Present retries on a later present
	}
	Create();
}

bool Swapchain::SurfaceExtentZero() {
	Common::LockGuard lock(m_window.mutex);
	const auto&       extent = m_window.surface_capabilities.capabilities.currentExtent;
	return extent.width == 0 || extent.height == 0;
}
''', 'Recreate')

t = replace_once(t, r'''	for (uint32_t attempt = 0; attempt < 2; attempt++) {
		const auto trace_start = PresentTraceEnabled() ? Common::FrameStats::NowNs() : 0;
''', r'''	for (uint32_t attempt = 0; attempt < 2; attempt++) {
		if (swapchain.Missing()) [[unlikely]] { // F5 (B37): KYTY_FIX_MINIMIZE=1 and a zero extent only
			if (!m_impl->TryEndZeroExtent()) {
				m_impl->zero_extent_dropped++;
				m_impl->frames.Release(&frame, reuse);
				return;
			}
		}
		const auto trace_start = PresentTraceEnabled() ? Common::FrameStats::NowNs() : 0;
''', 'Present loop')

save(p, t, crlf)

# ---------------------------------------------------------------- window.h
p = 'graphics/presentation/window.h'
t, crlf = load(p)
t = replace_once(t, r'''void                     WindowShutdown();
''', r'''void                     WindowShutdown();
// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): the stand KYTY_TEST_MINIMIZE - fed the game's log text.
void                     WindowTestMinimizeNoteGuestText(const char* text, size_t size);
''', 'window.h')
save(p, t, crlf)

# ---------------------------------------------------------------- window.cpp
p = 'graphics/presentation/window/window.cpp'
t, crlf = load(p)
t = replace_once(t, r'''#include <string>
#include <vector>
#include <vulkan/vk_platform.h>
''', r'''#include <string>
#include <string_view>
#include <vector>
#include <vulkan/vk_platform.h>
''', 'window.cpp includes')

t = replace_once(t, r'''void WindowShutdown() {
	if (g_window != nullptr) {
		Controller::EmergencyShutdown();
		g_window.reset();
	}
}
''', r'''void WindowShutdown() {
	if (g_window != nullptr) {
		Controller::EmergencyShutdown();
		g_window.reset();
	}
}

// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): KYTY_TEST_MINIMIZE=<s>:<dur> - <s> seconds after the
// game's first "Level has started:" line the emulator minimizes its own window (SDL_MinimizeWindow on the main thread)
// and restores it <dur> seconds later (SDL_RestoreWindow); lines "TestMinimize: minimize" / "TestMinimize: restore".
// Unset or empty - nothing (one getenv, then a static flag per guest log write).  The timer is a detached thread that
// sleeps; the SDL calls are posted to the main thread.  A process that ends inside the window never restores it.
void WindowTestMinimizeNoteGuestText(const char* text, size_t size) {
	struct TestMinimize {
		bool   on      = false;
		double delay_s = 0.0;
		double dur_s   = 0.0;
	};
	static const TestMinimize cfg = [] {
		TestMinimize c;
		const char*  value = std::getenv("KYTY_TEST_MINIMIZE");
		if (value == nullptr || value[0] == '\0') {
			return c;
		}
		char* end = nullptr;
		c.delay_s = std::strtod(value, &end);
		if (end != value && end != nullptr && *end == ':') {
			const char* dur = end + 1;
			c.dur_s         = std::strtod(dur, &end);
			c.on            = end != dur && *end == '\0' && c.delay_s >= 0.0 && c.dur_s >= 0.0;
		}
		LOGF("TestMinimize: config %s delay_s=%.3f dur_s=%.3f\n", c.on ? "on" : "invalid", c.delay_s, c.dur_s);
		return c;
	}();
	static std::atomic<bool> armed {false};
	if (!cfg.on || text == nullptr || armed.load(std::memory_order_relaxed)) {
		return;
	}
	if (std::string_view(text, size).find("Level has started: ") == std::string_view::npos ||
	    armed.exchange(true, std::memory_order_acq_rel)) {
		return;
	}
	LOGF("TestMinimize: armed delay_s=%.3f dur_s=%.3f\n", cfg.delay_s, cfg.dur_s);
	std::thread([] {
		const auto post = [](bool minimize) {
			auto* context = g_window.get();
			if (context == nullptr) {
				return;
			}
			context->PostToMainThread([context, minimize] {
				if (context->window == nullptr) {
					return;
				}
				if (minimize) {
					LOGF("TestMinimize: minimize\n");
					SDL_MinimizeWindow(context->window);
				} else {
					LOGF("TestMinimize: restore\n");
					SDL_RestoreWindow(context->window);
				}
			});
		};
		std::this_thread::sleep_for(std::chrono::duration<double>(cfg.delay_s));
		post(true);
		std::this_thread::sleep_for(std::chrono::duration<double>(cfg.dur_s));
		post(false);
	}).detach();
}
''', 'WindowShutdown')
save(p, t, crlf)

# ---------------------------------------------------------------- libC.cpp
p = 'libs/libC.cpp'
t, crlf = load(p)
t = replace_once(t, r'''#include "graphics/presentation/renderDoc.h"
''', r'''#include "graphics/presentation/renderDoc.h"
#include "graphics/presentation/window.h"
''', 'libC include')
t = replace_once(t, r'''		Libs::Graphics::RenderDocNoteGuestText(text.data(), text.size());
''', r'''		Libs::Graphics::RenderDocNoteGuestText(text.data(), text.size());
		Libs::Graphics::WindowTestMinimizeNoteGuestText(text.data(), text.size()); // F5, KYTY_TEST_MINIMIZE
''', 'libC call')
save(p, t, crlf)

print('PATCH OK')
