#ifndef KYTY_COMMON_LOGGING_LOG_H_
#define KYTY_COMMON_LOGGING_LOG_H_

#include "common/common.h"

#include <fmt/color.h>
#include <fmt/printf.h>
#include <string_view>

namespace Log {

void Initialize();
void Shutdown();

struct Lifecycle {
	static constexpr const char* name               = "Log";
	static constexpr auto        initialize         = Log::Initialize;
	static constexpr auto        shutdown           = Log::Shutdown;
	static constexpr auto        emergency_shutdown = Log::Shutdown;
};

enum class Direction { Silent, Console, File };

Direction GetDirection();
bool      IsSilent();
// Per-packet chatter (end-of-pipe signals, event-queue polls, AGC argument dumps: ~1800 lines per
// frame in ASTRO BOT) goes through LOGV and is written only with KYTY_LOG_VERBOSE=1 or when the
// graphics debug dump is enabled.
bool      IsVerbose();
void      Write(std::string_view text);
void      Write(fmt::text_style style, std::string_view text);
void      WriteToConsoleAndLog(std::string_view text);
void      WriteFatal(std::string_view text);
void      WriteFatal(fmt::text_style style, std::string_view text);
void      Flush();
// Track F, F25k (KYTY_FIX_B36, ROADMAP s122 item 613(v)(4)): the queue of the async log writer reaches the file before a
// process end that skips Log::Shutdown (the std::_Exit sites); the writer stops. No-op at KYTY_FIX_B36=0.
void      DrainForExit() noexcept;
// The same without stopping the writer: the unresolved branch of the host exception filter (the process may live on).
void      DrainForFault() noexcept;
// KYTY_FIX_B36=1 in effect (the File direction): the "log_async" field of the "LongFrame:" line.
bool      AsyncEnabled();
// Track F, F25k2 (KYTY_LONGFRAME=1; RC2 of F25l, ROADMAP s122 item 616(b)(2)): one record of a flip >= 100 ms - stored in a
// static array without log I/O on the calling thread; a printer thread off the frame path writes the "LongFrame:" line.
// One producer at a time (FlipQueue::Flip under FlipQueue::m_mutex); at most 4 096 records. No-op without KYTY_LONGFRAME.
void      LongFrameRecord(uint64_t n, uint64_t dt_us, uint64_t t_ms);
namespace Testing {
// log_async_tests only: the 256 MiB limit of the queue replaced.
void SetAsyncLimit(uint64_t bytes);
// log_async_tests only (F25k2, RC4): the next sink write by a thread that holds the sink lock outside the writer faults.
void FaultInNextOwnerWrite();
// log_async_tests only (F25k2, RC2): the printer thread of KYTY_LONGFRAME was created.
bool LongFramePrinterStarted();
} // namespace Testing

namespace Color {

inline constexpr auto Default       = fmt::text_style {};
inline constexpr auto Red           = fmt::fg(fmt::terminal_color::red);
inline constexpr auto Green         = fmt::fg(fmt::terminal_color::green);
inline constexpr auto Yellow        = fmt::fg(fmt::terminal_color::yellow);
inline constexpr auto Magenta       = fmt::fg(fmt::terminal_color::magenta);
inline constexpr auto Cyan          = fmt::fg(fmt::terminal_color::cyan);
inline constexpr auto White         = fmt::fg(fmt::terminal_color::white);
inline constexpr auto BrightRed     = fmt::fg(fmt::terminal_color::bright_red);
inline constexpr auto BrightGreen   = fmt::fg(fmt::terminal_color::bright_green);
inline constexpr auto BrightYellow  = fmt::fg(fmt::terminal_color::bright_yellow);
inline constexpr auto BrightMagenta = fmt::fg(fmt::terminal_color::bright_magenta);
inline constexpr auto BrightWhite   = fmt::fg(fmt::terminal_color::bright_white);

} // namespace Color

} // namespace Log

// NOLINTNEXTLINE(cppcoreguidelines-macro-usage)
#define LOGF(...)                                                                                  \
	do {                                                                                           \
		if (!::Log::IsSilent()) {                                                                  \
			::Log::Write(::fmt::sprintf(__VA_ARGS__));                                             \
		}                                                                                          \
	} while (false)
// NOLINTNEXTLINE(cppcoreguidelines-macro-usage)
#define LOGF_COLOR(style, ...)                                                                     \
	do {                                                                                           \
		if (!::Log::IsSilent()) {                                                                  \
			::Log::Write((style), ::fmt::sprintf(__VA_ARGS__));                                    \
		}                                                                                          \
	} while (false)
// NOLINTNEXTLINE(cppcoreguidelines-macro-usage)
#define LOGV(...)                                                                                  \
	do {                                                                                           \
		if (::Log::IsVerbose()) {                                                                  \
			::Log::Write(::fmt::sprintf(__VA_ARGS__));                                             \
		}                                                                                          \
	} while (false)
// NOLINTNEXTLINE(cppcoreguidelines-macro-usage)
#define LOGV_COLOR(style, ...)                                                                     \
	do {                                                                                           \
		if (::Log::IsVerbose()) {                                                                  \
			::Log::Write((style), ::fmt::sprintf(__VA_ARGS__));                                    \
		}                                                                                          \
	} while (false)

#endif /* KYTY_COMMON_LOGGING_LOG_H_ */
