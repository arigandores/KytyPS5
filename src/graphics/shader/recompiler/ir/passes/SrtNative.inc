// Included in SrtWalker's private namespace after the portable node evaluator.
// This is a host-only execution plan. Memory callbacks still run in node order,
// with exactly the portable evaluator's status propagation and fallback nodes.
struct NativeSrtFrame {
	const CompiledSrt* compiled;
	const ResourcePlan* plan;
	const SrtRuntime* runtime;
	uint64_t* values;
	uint8_t* status;
	const uint32_t* user_data;
	size_t user_data_size;
	uint32_t user_data_base;
};

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
bool EvaluateNativeSrtRange(NativeSrtFrame* frame, uint32_t first, uint32_t last) {
	EvaluateCompiledNodes(*frame->compiled, *frame->plan, *frame->runtime, frame->values,
	                      frame->status, first, last);
	if (std::any_of(frame->status + first, frame->status + last,
	                [](uint8_t status) { return status != CompiledSrt::StOk; })) {
		EvaluateCompiledNodes(*frame->compiled, *frame->plan, *frame->runtime, frame->values,
		                      frame->status, last);
		return false;
	}
	return true;
}

class NativeSrtCode final: public Xbyak::CodeGenerator {
public:
	NativeSrtCode(const CompiledSrt& compiled)
	    : Xbyak::CodeGenerator(4096, Xbyak::AutoGrow) {
		// Windows x64: retain frame/data pointers and immutable runtime callbacks in
		// nonvolatile registers. Every call has shadow space and 16-byte alignment.
		push(r12); const auto save12 = getSize();
		push(r13); const auto save13 = getSize();
		push(r14); const auto save14 = getSize();
		push(r15); const auto save15 = getSize();
		push(rbx); const auto save3 = getSize();
		push(rsi); const auto save6 = getSize();
		push(rdi); const auto save7 = getSize();
		sub(rsp, 32);
		const auto prologue = getSize();
		mov(r12, rcx);
		mov(r13, ptr[r12 + offsetof(NativeSrtFrame, values)]);
		mov(r14, ptr[r12 + offsetof(NativeSrtFrame, status)]);
		mov(r15, ptr[r12 + offsetof(NativeSrtFrame, runtime)]);
		mov(rbx, ptr[r15 + offsetof(SrtRuntime, userdata)]);
		mov(rsi, ptr[r15 + offsetof(SrtRuntime, read_specialization_memory)]);
		mov(rdi, ptr[r15 + offsetof(SrtRuntime, read_memory)]);
		Xbyak::Label epilogue;
		for (uint32_t index = 0; index < compiled.nodes.size();) {
			if (!Supported(compiled.nodes[index].op)) {
				const auto first = index++;
				while (index < compiled.nodes.size() && !Supported(compiled.nodes[index].op)) ++index;
				mov(rcx, r12); mov(edx, first); mov(r8d, index);
				mov(rax, reinterpret_cast<uintptr_t>(&EvaluateNativeSrtRange)); call(rax);
				test(al, al); jz(epilogue, T_NEAR);
				continue;
			}
			Emit(compiled.nodes[index], index);
			++index;
		}
		jmp(epilogue, T_NEAR);
		for (auto& failure: m_failures) {
			L(failure.label);
			mov(byte[r14 + failure.index], al);
			mov(qword[r13 + size_t(failure.index) * 8], 0);
			mov(rcx, r12); mov(edx, failure.index + 1);
			mov(r8d, static_cast<uint32_t>(compiled.nodes.size()));
			mov(rax, reinterpret_cast<uintptr_t>(&EvaluateNativeSrtRange)); call(rax);
			jmp(epilogue, T_NEAR);
		}
		L(epilogue);
		add(rsp, 32);
		pop(rdi); pop(rsi); pop(rbx);
		pop(r15); pop(r14); pop(r13); pop(r12);
		ret();
		const auto code_size = getSize();
		align(4);
		const auto unwind_offset = getSize();
		// Windows must be able to unwind a callback exception or a profiler stack
		// through this non-leaf function. Codes describe the prologue in reverse order.
		db(1); db(static_cast<uint8_t>(prologue)); db(8); db(0);
		db(static_cast<uint8_t>(prologue)); db(0x32); // UWOP_ALLOC_SMALL, 32 bytes
		db(static_cast<uint8_t>(save7)); db(0x70);
		db(static_cast<uint8_t>(save6)); db(0x60);
		db(static_cast<uint8_t>(save3)); db(0x30);
		db(static_cast<uint8_t>(save15)); db(0xf0); // UWOP_PUSH_NONVOL r15
		db(static_cast<uint8_t>(save14)); db(0xe0);
		db(static_cast<uint8_t>(save13)); db(0xd0);
		db(static_cast<uint8_t>(save12)); db(0xc0);
		ready();
		m_unwind = {0, static_cast<DWORD>(code_size), static_cast<DWORD>(unwind_offset)};
		m_registered = RtlAddFunctionTable(&m_unwind, 1, reinterpret_cast<DWORD64>(getCode())) != 0;
		if (!m_registered) throw std::runtime_error("SRT native unwind registration failed");
	}
	~NativeSrtCode() {
		if (m_registered) RtlDeleteFunctionTable(&m_unwind);
	}

private:
	RUNTIME_FUNCTION m_unwind {};
	bool m_registered = false;
	struct FailureSite { Xbyak::Label label; uint32_t index; };
	std::deque<FailureSite> m_failures;
	using Op = CompiledSrt::Op;
	static bool Supported(Op op) {
		switch (op) {
			case Op::Const: case Op::UserData: case Op::ShaderBase: case Op::Fail:
			case Op::Address48: case Op::MemReadScalar:
			case Op::Add32: case Op::Add64: case Op::Sub32: case Op::Sub64:
			case Op::Mul32: case Op::Mul64: case Op::And32: case Op::And64:
			case Op::Or32: case Op::Xor32: case Op::Not32:
			case Op::Shl32: case Op::Shl64: case Op::Shr32: case Op::Shr64:
			case Op::Sar32: case Op::Sar64: case Op::Construct64: case Op::Extract64:
			case Op::IEq32: case Op::INe32: case Op::ULt32: case Op::UGt32:
			case Op::Select: case Op::UMin32: return true;
			default: return false;
		}
	}

	Xbyak::Address ValueAt(uint32_t index) { return ptr[r13 + size_t(index) * 8]; }
	void Emit(const CompiledSrt::Node& n, uint32_t index) {
		Xbyak::Label done;
		Xbyak::Label unused_failure;
		auto* failure = &unused_failure;
		if (n.op == Op::UserData || n.op == Op::Fail || n.op == Op::MemReadScalar) {
			auto& site = m_failures.emplace_back();
			site.index = index;
			failure = &site.label;
		}
		auto& failed = *failure;
		if (n.a != CompiledSrt::None) mov(rax, ValueAt(n.a));
		if (n.b != CompiledSrt::None) mov(rdx, ValueAt(n.b));
		switch (n.op) {
			case Op::Const: mov(rax, n.imm); break;
			case Op::Fail: mov(eax, CompiledSrt::StHardFail); jmp(failed, T_NEAR); break;
			case Op::UserData: {
				Xbyak::Label valid, invalid;
				mov(rax, n.imm);
				mov(ecx, dword[r12 + offsetof(NativeSrtFrame, user_data_base)]);
				cmp(rax, rcx); jb(invalid, T_NEAR);
				sub(rax, rcx);
				cmp(rax, qword[r12 + offsetof(NativeSrtFrame, user_data_size)]);
				jb(valid, T_NEAR);
				L(invalid);
				mov(eax, CompiledSrt::StHardFail); jmp(failed, T_NEAR);
				L(valid);
				mov(rdx, ptr[r12 + offsetof(NativeSrtFrame, user_data)]);
				mov(eax, dword[rdx + rax * 4]);
				break;
			}
			case Op::ShaderBase: mov(rax, ptr[r15 + offsetof(SrtRuntime, shader_base)]); break;
			case Op::Address48:
				and_(eax, ~3u); and_(edx, 0xffff); shl(rdx, 32); or_(rax, rdx); break;
			case Op::MemReadScalar: {
				Xbyak::Label valid, raw;
				mov(rdx, rax); mov(rax, n.imm); add(rdx, rax);
				mov(rax, AddressMask); cmp(rdx, rax); jbe(valid, T_NEAR);
				mov(eax, CompiledSrt::StHardFail); jmp(failed, T_NEAR);
				L(valid);
				const bool clean = (n.comp & 2u) != 0;
				mov(rax, clean ? rsi : rdi);
				test(rax, rax); jz(raw, T_NEAR);
				mov(qword[r13 + size_t(index) * 8], 0);
				mov(rcx, rbx);
				lea(r8, ValueAt(index)); call(rax);
				test(al, al); jnz(done, T_NEAR);
				mov(eax, clean ? CompiledSrt::StCleanMemFail : CompiledSrt::StMemFail);
				jmp(failed, T_NEAR);
				L(raw); mov(eax, dword[rdx]);
				break;
			}
			case Op::Add32: add(eax, edx); break;
			case Op::Add64: add(rax, rdx); break;
			case Op::Sub32: sub(eax, edx); break;
			case Op::Sub64: sub(rax, rdx); break;
			case Op::Mul32: imul(eax, edx); break;
			case Op::Mul64: imul(rax, rdx); break;
			case Op::And32: and_(eax, edx); break;
			case Op::And64: and_(rax, rdx); break;
			case Op::Or32: or_(eax, edx); break;
			case Op::Xor32: xor_(eax, edx); break;
			case Op::Not32: not_(eax); break;
			case Op::Shl32: mov(ecx, edx); shl(eax, cl); break;
			case Op::Shl64: mov(ecx, edx); shl(rax, cl); break;
			case Op::Shr32: mov(ecx, edx); shr(eax, cl); break;
			case Op::Shr64: mov(ecx, edx); shr(rax, cl); break;
			case Op::Sar32: mov(ecx, edx); sar(eax, cl); break;
			case Op::Sar64: mov(ecx, edx); sar(rax, cl); break;
			case Op::Construct64: mov(eax, eax); shl(rdx, 32); or_(rax, rdx); break;
			case Op::Extract64: shr(rax, n.comp * 32); mov(eax, eax); break;
			case Op::Select:
				test(rax, rax); mov(rax, ValueAt(n.c)); cmovnz(rax, rdx); break;
			case Op::UMin32: cmp(eax, edx); cmova(eax, edx); mov(eax, eax); break;
			case Op::IEq32: cmp(eax, edx); sete(al); movzx(eax, al); break;
			case Op::INe32: cmp(eax, edx); setne(al); movzx(eax, al); break;
			case Op::ULt32: cmp(eax, edx); setb(al); movzx(eax, al); break;
			case Op::UGt32: cmp(eax, edx); seta(al); movzx(eax, al); break;
			default: break;
		}
		mov(ValueAt(index), rax);
		L(done);
	}
};

struct NativeSrtAuditTape {
	struct Read { uint64_t address; uint32_t word; bool clean, ok; };
	const SrtRuntime& original;
	std::vector<Read> reads;
	size_t cursor = 0;
	bool mismatch = false;

	template <bool clean>
	static bool Record(void* opaque, uint64_t address, uint32_t* word) {
		auto& tape = *static_cast<NativeSrtAuditTape*>(opaque);
		const auto reader = clean ? tape.original.read_specialization_memory : tape.original.read_memory;
		bool ok = true;
		if (reader != nullptr) ok = reader(tape.original.userdata, address, word);
		else std::memcpy(word, reinterpret_cast<const void*>(address), sizeof(*word));
		tape.reads.push_back({address, *word, clean, ok});
		return ok;
	}
	template <bool clean>
	static bool Replay(void* opaque, uint64_t address, uint32_t* word) {
		auto& tape = *static_cast<NativeSrtAuditTape*>(opaque);
		if (tape.cursor >= tape.reads.size()) {
			tape.mismatch = true;
			return false;
		}
		const auto& read = tape.reads[tape.cursor++];
		if (read.address != address || read.clean != clean) {
			tape.mismatch = true;
			return false;
		}
		*word = read.word;
		return read.ok;
	}
};

void AuditNativeSrt(const CompiledSrt& compiled, const ResourcePlan& plan,
                    const SrtRuntime& runtime, uint64_t* values, uint8_t* status) {
	// Use portable results for the actual draw. The native evaluator only sees a replay
	// of those reads, so a bad native address cannot reach guest memory or the GPU.
	NativeSrtAuditTape tape {runtime};
	tape.reads.reserve(compiled.nodes.size() / 3);
	auto recorded = runtime;
	recorded.userdata = &tape;
	recorded.read_memory = NativeSrtAuditTape::Record<false>;
	recorded.read_specialization_memory = NativeSrtAuditTape::Record<true>;
	EvaluateCompiledNodes(compiled, plan, recorded, values, status);
	std::vector<uint64_t> native_values(compiled.nodes.size());
	std::vector<uint8_t> native_status(compiled.nodes.size(), CompiledSrt::StOk);
	auto replayed = recorded;
	replayed.read_memory = NativeSrtAuditTape::Replay<false>;
	replayed.read_specialization_memory = NativeSrtAuditTape::Replay<true>;
	NativeSrtFrame frame {&compiled, &plan, &replayed, native_values.data(), native_status.data(),
	                      runtime.user_data.data(), runtime.user_data.size(), plan.user_data_base};
	compiled.native_eval(&frame);
	static std::atomic<uint64_t> checked {0};
	const auto count = checked.fetch_add(1, std::memory_order_relaxed) + 1;
	if ((count & 65535u) == 0 && std::getenv("KYTY_SRT_NATIVE_STATS") != nullptr) {
		std::fprintf(stderr, "SrtNativeAuditProgress: checked=%llu\n", static_cast<unsigned long long>(count));
	}
	size_t bad = 0;
	while (bad < compiled.nodes.size() && native_values[bad] == values[bad] &&
	       native_status[bad] == status[bad]) ++bad;
	if (bad != compiled.nodes.size() || tape.mismatch || tape.cursor != tape.reads.size()) {
		static std::atomic<uint32_t> logged {0};
		if (logged.fetch_add(1) < 64) {
			std::fprintf(stderr, "SrtNativeAudit: hash=%016llx node=%zu/%zu trace=%d reads=%zu/%zu expected=%016llx actual=%016llx status=%u/%u\n",
			    static_cast<unsigned long long>(plan.shader_hash), bad, compiled.nodes.size(),
			    tape.mismatch ? 1 : 0, tape.cursor, tape.reads.size(),
			    static_cast<unsigned long long>(bad < compiled.nodes.size() ? values[bad] : 0),
			    static_cast<unsigned long long>(bad < compiled.nodes.size() ? native_values[bad] : 0),
			    bad < compiled.nodes.size() ? status[bad] : 0,
			    bad < compiled.nodes.size() ? native_status[bad] : 0);
		}
	}
}
#endif

bool EvaluateNativeSrt(const CompiledSrt& compiled, const ResourcePlan& plan,
                       const SrtRuntime& runtime, uint64_t* values, uint8_t* status) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_SRT_NATIVE");
		return value != nullptr && value[0] == '1';
	}();
	if (!enabled) return false;
	bool created = false;
	std::call_once(compiled.native_once, [&] {
		if (compiled.nodes.size() > 8192) return;
		try {
			auto code = std::make_shared<NativeSrtCode>(compiled);
			if (std::getenv("KYTY_SRT_NATIVE_STATS") != nullptr) {
				std::fprintf(stderr, "SrtNative: hash=%016llx nodes=%zu bytes=%zu\n",
				             static_cast<unsigned long long>(plan.shader_hash),
				             compiled.nodes.size(), code->getSize());
			}
			compiled.native_eval = code->getCode<void (*)(void*)>();
			compiled.native_owner = std::move(code);
			created = true;
		} catch (const std::exception& error) {
			std::fprintf(stderr, "SrtNative: portable fallback: %s\n", error.what());
		}
	});
	if (compiled.native_eval == nullptr) return false;
	static const bool audit = std::getenv("KYTY_SRT_NATIVE_AUDIT") != nullptr;
	if (audit) {
		static const uint64_t every = [] {
			const auto* value = std::getenv("KYTY_SRT_NATIVE_AUDIT_EVERY");
			return value == nullptr ? uint64_t {1}
			    : std::max(uint64_t {1}, static_cast<uint64_t>(std::strtoull(value, nullptr, 10)));
		}();
		static thread_local uint64_t calls = 0;
		if (created || (++calls % every) == 0) {
			AuditNativeSrt(compiled, plan, runtime, values, status);
		} else {
			EvaluateCompiledNodes(compiled, plan, runtime, values, status);
		}
		return true;
	}
	// A native instruction is reached only while all prior statuses are OK. The first
	// failure transfers the remaining suffix to the portable evaluator, without replay.
	std::fill_n(status, compiled.nodes.size(), CompiledSrt::StOk);
	NativeSrtFrame frame {&compiled, &plan, &runtime, values, status,
	                      runtime.user_data.data(), runtime.user_data.size(), plan.user_data_base};
	compiled.native_eval(&frame);
	return true;
#else
	return false;
#endif
}
