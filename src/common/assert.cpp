#include "common/assert.h"

#include "common/logging/log.h"
#include "common/subsystems.h"
#include "kytyGitVersion.h"

#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <exception>
#include <fmt/format.h>
#include <string>

namespace Common {

static std::string BuildFatalReport(const char* title, std::string_view text, const char* file,
                                    int line) {
	return fmt::format("--- Build ---\n{}\n{}\n{} in {}:{}\n", KYTY_BUILD_LABEL, title, text, file,
	                   line);
}

static int DbgReport(const char* title, std::string_view text, const char* file, int line) {
	if (fatal_interceptor) { fatal_interceptor(file, line, text); }
	Log::WriteFatal(BuildFatalReport(title, text, file, line));
	Subsystems::EmergencyShutdownActive();
	return 1;
}

int DbgExitIfHandler(const char* expr, const char* file, int line) {
	return DbgReport("--- Fatal Error ---", fmt::format("Error: condition ({}) is true", expr),
	                 file, line);
}

int DbgNotImplementedHandler(const char* expr, const char* file, int line) {
	return DbgReport("--- Fatal Error ---", fmt::format("Not implemented ({})", expr), file, line);
}

int DbgExitHandler(const char* file, int line, std::string_view text) {
	if (fatal_interceptor) { fatal_interceptor(file, line, text); }
	Log::WriteFatal(BuildFatalReport("--- Error ---", text, file, line));
	return 1;
}

int DbgExitHandler(const char* file, int line, fmt::text_style style, std::string_view text) {
	if (fatal_interceptor) { fatal_interceptor(file, line, text); }
	Log::WriteFatal(style, BuildFatalReport("--- Error ---", text, file, line));
	return 1;
}

// Session 97: std::terminate and abort() used to end the process with NOTHING on record - no
// text, no WER event (HKCU WER Disabled=1), the log and stdout tails lost with their
// unflushed CRT buffers.  bf96b died exactly that way (an exception escaping the noexcept
// thread entry of GuestGpu).  Two reports, both writing a FIXED literal and flushing BEFORE
// anything allocates (a bad_alloc-driven terminate must still leave text):
//  * TerminateReport - std::set_terminate is PER THREAD in the UCRT (ucrt/misc/terminate.cpp
//    reads __acrt_getptd()->_terminate; a new thread starts with none), so it is installed
//    at static init for the main thread and by InstallThreadTerminateReport at the entry of
//    GuestGpu::ThreadRun.  current_exception() is often empty (the exception is still in
//    flight when a noexcept boundary calls terminate) and the report says so;
//  * AbortReport - the SIGABRT action IS process-global in the UCRT and abort() raises it
//    before it ends the process, so every thread without a terminate report, and every
//    explicit abort(), still leaves "--- abort() ---".  raise() restores SIG_DFL before it
//    calls the handler, and returning lets abort() finish exactly as before.
// Not covered, and said so: a run with the Tracy profiler enabled (its top-level exception
// filter swallows uncaught C++ exceptions before terminate is reached), stack overflow and
// __fastfail.
static void WriteLiteral(const char* text, size_t size) {
	std::fflush(nullptr);
	std::fwrite(text, 1, size, stderr);
	std::fwrite(text, 1, size, stdout);
	std::fflush(nullptr);
}

extern "C" void AbortReport(int /*signal*/) {
	static const char text[] = "\n--- abort() ---\nabort() was called: std::terminate on a "
	                           "thread without a report, or an explicit abort\n";
	WriteLiteral(text, sizeof(text) - 1);
	try {
		Log::WriteFatal(BuildFatalReport("--- abort() ---", "SIGABRT", "abort", 0));
	} catch (...) {
	}
	std::fflush(nullptr);
}

[[noreturn]] static void TerminateReport() {
	static const char text[] = "\n--- std::terminate ---\n";
	WriteLiteral(text, sizeof(text) - 1);
	try {
		std::string what = "no exception is being handled (e.g. one escaped a noexcept function)";
		if (const auto current = std::current_exception()) {
			try {
				std::rethrow_exception(current);
			} catch (const std::exception& error) {
				what = fmt::format("std::exception: {}", error.what());
			} catch (...) {
				what = "a non-std exception";
			}
		}
		Log::WriteFatal(BuildFatalReport("--- std::terminate ---", what, "std::terminate", 0));
	} catch (...) {
	}
	std::fflush(nullptr);
	std::abort();
}

void InstallThreadTerminateReport() {
	std::set_terminate(TerminateReport);
}

[[maybe_unused]] static const bool g_terminate_report_installed = [] {
	std::set_terminate(TerminateReport);
	std::signal(SIGABRT, AbortReport);
	return true;
}();

void DbgExit(int status) {
	if (fatal_interceptor) { fatal_interceptor("DbgExit", status, "explicit fatal exit"); }
	Subsystems::EmergencyShutdownActive();
	std::fflush(nullptr);
	std::_Exit(status);
}

} // namespace Common
