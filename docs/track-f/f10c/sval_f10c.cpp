// Track F, link F10c (HPP-451), ROADMAP s122 item 369(v)(1): offline test of KYTY_FIX_SVAL in the built-in SPIR-V check.
//
// Copy of the F10a tool sval_f10a.cpp on the F10c code. sval_body_f10c.inc is the region of
// src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp from 'bool FixSvalEnabled() {' through the end of
// ValidateShaderSpirv, extracted byte for byte from the F10c commit by extract_body_f10c.py and compiled here unchanged:
// FixSvalEnabled (reads KYTY_FIX_SVAL once through the real common/envFlag.h of the worktree), the device value
// g_fix_sval_ubo_std_layout and ValidateShaderSpirv. The only substitutions are the names the region calls outside
// SPIRV-Tools, fmt and envFlag.h (as in F10a):
//   Config::ShaderValidationEnabled() -> true (the launcher default shader_validation_enabled = true);
//   LOGF_COLOR / LOGF                 -> capture the printf-formatted text instead of writing the log.
// The switch: KYTY_FIX_SVAL in the environment of the process (read by the extracted FixSvalEnabled, as in the
// emulator); the device value: the second argument, stored into g_fix_sval_ubo_std_layout as the PipelineCache
// constructor does.
//
// Usage: sval_f10c.exe --mode            prints "mode\t<FixSvalEnabled()>"
//        sval_f10c.exe --mode-once       FixSvalEnabled(), then _putenv KYTY_FIX_SVAL to the opposite, FixSvalEnabled()
//                                         again: prints "mode-once\t<first>\t<second>" (read once: equal)
//        sval_f10c.exe <list.tsv> <0|1>  list lines "<id>\t<path to .spv>"; one output line per shader:
//                                         <id>\t<words>\t<ACCEPT|REJECT>\t<message>; "#stat\t<n>\t<line>" for each
//                                         FixSvalStat line logged by the n-th check
#include <atomic>
#include <cinttypes>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#include <fmt/format.h>

#include "common/envFlag.h"
#include "spirv-tools/libspirv.hpp"

namespace Config {
bool ShaderValidationEnabled() {
	return true;
}
} // namespace Config

namespace Log::Color {
inline constexpr int BrightRed = 1;
} // namespace Log::Color

static std::string g_log_color;
static std::string g_log_plain;

static std::string PrintfText(const char* format, ...) {
	va_list args;
	va_start(args, format);
	va_list copy;
	va_copy(copy, args);
	const int size = std::vsnprintf(nullptr, 0, format, copy);
	va_end(copy);
	std::string text(size > 0 ? static_cast<size_t>(size) : 0u, '\0');
	if (size > 0) {
		std::vsnprintf(text.data(), text.size() + 1, format, args);
	}
	va_end(args);
	return text;
}

#define LOGF_COLOR(style, ...) (static_cast<void>(style), g_log_color += PrintfText(__VA_ARGS__))
#define LOGF(...) (g_log_plain += PrintfText(__VA_ARGS__))

namespace {
#include "sval_body_f10c.inc"
} // namespace

static std::string OneLine(const std::string& text) {
	std::string out;
	for (const char c: text) {
		if (c == '\n') {
			out += " | ";
		} else if (c == '\r' || c == '\t') {
			out += ' ';
		} else {
			out += c;
		}
	}
	while (out.size() >= 3 && out.compare(out.size() - 3, 3, " | ") == 0) {
		out.resize(out.size() - 3);
	}
	return out;
}

int main(int argc, char** argv) {
	if (argc == 2 && std::strcmp(argv[1], "--mode") == 0) {
		std::printf("mode\t%d\n", FixSvalEnabled() ? 1 : 0);
		return 0;
	}
	if (argc == 2 && std::strcmp(argv[1], "--mode-once") == 0) {
		const bool first = FixSvalEnabled();
		_putenv(first ? "KYTY_FIX_SVAL=0" : "KYTY_FIX_SVAL=1");
		const bool second = FixSvalEnabled();
		std::printf("mode-once\t%d\t%d\n", first ? 1 : 0, second ? 1 : 0);
		return 0;
	}
	if (argc != 3 || (std::strcmp(argv[2], "0") != 0 && std::strcmp(argv[2], "1") != 0)) {
		std::fprintf(stderr, "usage: sval_f10c.exe <list.tsv> <0|1> | --mode | --mode-once\n");
		return 2;
	}
	// As the PipelineCache constructor: the device value before the first check.
	g_fix_sval_ubo_std_layout.store(argv[2][0] == '1', std::memory_order_release);
	std::printf("#spirv-tools\t%s\n", spvSoftwareVersionDetailsString());
	std::printf("#mode\t%d\n", FixSvalEnabled() ? 1 : 0);
	std::printf("#ubo\t%d\n", g_fix_sval_ubo_std_layout.load() ? 1 : 0);
	std::ifstream list(argv[1]);
	if (!list) {
		std::fprintf(stderr, "cannot open %s\n", argv[1]);
		return 2;
	}
	std::string line;
	int         count = 0;
	while (std::getline(list, line)) {
		if (!line.empty() && line.back() == '\r') {
			line.pop_back();
		}
		const auto tab = line.find('\t');
		if (line.empty() || tab == std::string::npos) {
			continue;
		}
		const std::string id   = line.substr(0, tab);
		const std::string path = line.substr(tab + 1);
		std::vector<uint32_t> spirv;
		{
			FILE* file = std::fopen(path.c_str(), "rb");
			if (file == nullptr) {
				std::fprintf(stderr, "cannot open %s\n", path.c_str());
				return 2;
			}
			uint32_t word = 0;
			while (std::fread(&word, sizeof(word), 1, file) == 1) {
				spirv.push_back(word);
			}
			std::fclose(file);
		}
		g_log_color.clear();
		g_log_plain.clear();
		const bool valid = ValidateShaderSpirv("f10c", 0, spirv);
		count++;
		std::printf("%s\t%zu\t%s\t%s\n", id.c_str(), spirv.size(), valid ? "ACCEPT" : "REJECT",
		            OneLine(g_log_color).c_str());
		size_t pos = 0;
		while ((pos = g_log_plain.find("FixSvalStat:", pos)) != std::string::npos) {
			const auto end = g_log_plain.find('\n', pos);
			std::printf("#stat\t%d\t%s\n", count, g_log_plain.substr(pos, end - pos).c_str());
			pos = end;
		}
	}
	std::printf("#count\t%d\n", count);
	return 0;
}
