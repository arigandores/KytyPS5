// Track F, link F10a (HPP-445), ROADMAP s122 item 366(d): offline test of the built-in SPIR-V check.
//
// ValidateShaderSpirv lives in an anonymous namespace of
// src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp (internal linkage), so no other
// translation unit can call it. sval_body.inc is its definition extracted byte for byte from the
// git blob by extract_body.py (sha256 printed there); it is compiled here unchanged. The only
// substitutions are the names it calls outside SPIRV-Tools and fmt:
//   Config::ShaderValidationEnabled() -> true (the launcher default shader_validation_enabled = true);
//   LOGF_COLOR / LOGF                 -> capture the printf-formatted text instead of writing the log.
// SPIRV-Tools is the static library of the emulator build tree (3rdparty/SPIRV-Tools 7f2d9ee).
//
// Usage: sval_f10a.exe <list.tsv>   (lines "<id>\t<path to .spv>")
// Output (stdout, one line per shader):
//   <id>\t<words>\t<builtin ACCEPT|REJECT>\t<builtin message>\t<layout ACCEPT|REJECT>\t<layout message>
// "builtin" = ValidateShaderSpirv as compiled from the extracted body; "layout" = control k3: the same
// environment SPV_ENV_VULKAN_1_3 with ValidatorOptions::SetUniformBufferStandardLayout(true).
#include <cinttypes>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

#include <fmt/format.h>

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
#include "sval_body.inc"
} // namespace

static bool ValidateWithLayout(const std::vector<uint32_t>& spirv, std::string* messages) {
	spvtools::SpirvTools tools(SPV_ENV_VULKAN_1_3);
	tools.SetMessageConsumer([messages](spv_message_level_t, const char*,
	                                    const spv_position_t& position, const char* message) {
		*messages += fmt::format("{}: {} ({}) {}\n", static_cast<int>(position.line),
		                         static_cast<int>(position.column), static_cast<int>(position.index),
		                         message);
	});
	spvtools::ValidatorOptions options;
	options.SetUniformBufferStandardLayout(true);
	return tools.Validate(spirv.data(), spirv.size(), options);
}

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
	if (argc != 2) {
		std::fprintf(stderr, "usage: sval_f10a.exe <list.tsv>\n");
		return 2;
	}
	std::printf("#spirv-tools\t%s\n", spvSoftwareVersionDetailsString());
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
		const bool builtin = ValidateShaderSpirv("f10a", 0, spirv);
		std::string layout_messages;
		const bool  layout = ValidateWithLayout(spirv, &layout_messages);
		std::printf("%s\t%zu\t%s\t%s\t%s\t%s\n", id.c_str(), spirv.size(), builtin ? "ACCEPT" : "REJECT",
		            OneLine(g_log_color).c_str(), layout ? "ACCEPT" : "REJECT",
		            OneLine(layout_messages).c_str());
		count++;
	}
	std::printf("#count\t%d\n", count);
	return 0;
}
