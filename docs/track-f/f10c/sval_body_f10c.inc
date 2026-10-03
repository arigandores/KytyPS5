bool FixSvalEnabled() {
	static const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_SVAL"));
	return enabled;
}

std::atomic<bool> g_fix_sval_ubo_std_layout {false};

bool ValidateShaderSpirv(const char* label, uint64_t shader_hash,
                         const std::vector<uint32_t>& spirv) {
	if (!Config::ShaderValidationEnabled()) {
		return true;
	}
	spvtools::SpirvTools tools(SPV_ENV_VULKAN_1_3);
	std::string          messages;
	tools.SetMessageConsumer([&messages](spv_message_level_t, const char*,
	                                     const spv_position_t& position, const char* message) {
		messages += fmt::format("{}: {} ({}) {}\n", static_cast<int>(position.line),
		                        static_cast<int>(position.column), static_cast<int>(position.index),
		                        message);
	});
	// Track F, F10c (KYTY_FIX_SVAL, see FixSvalEnabled): ON - the options of the device; OFF - the old call.
	bool valid = false;
	if (FixSvalEnabled()) {
		spvtools::ValidatorOptions options;
		if (g_fix_sval_ubo_std_layout.load(std::memory_order_acquire)) {
			options.SetUniformBufferStandardLayout(true);
		}
		valid = tools.Validate(spirv.data(), spirv.size(), options);
		static std::atomic<uint64_t> validated {0};
		static std::atomic<uint64_t> rejected {0};
		if (!valid) {
			rejected.fetch_add(1, std::memory_order_relaxed);
		}
		const uint64_t checks = validated.fetch_add(1, std::memory_order_relaxed) + 1;
		if (checks % 256u == 0) {
			LOGF("FixSvalStat: validated=%" PRIu64 " rejected=%" PRIu64 "\n", checks,
			     rejected.load(std::memory_order_relaxed));
		}
	} else {
		valid = tools.Validate(spirv);
	}
	if (valid) {
		return true;
	}
	spvtools::SpirvTools disassembler(SPV_ENV_VULKAN_1_2);
	std::string          text;
	disassembler.Disassemble(spirv, &text,
	                         static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_NO_HEADER) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_FRIENDLY_NAMES) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_COMMENT) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_INDENT) |
	                             static_cast<uint32_t>(SPV_BINARY_TO_TEXT_OPTION_COLOR));
	LOGF_COLOR(Log::Color::BrightRed, "%s SPIR-V validation failed hash=0x%016" PRIx64 ":\n%s",
	           label, shader_hash, messages.c_str());
	LOGF("%s\n", text.c_str());
	return false;
}
