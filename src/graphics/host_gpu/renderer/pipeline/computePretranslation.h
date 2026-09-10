#pragma once

#include "graphics/shader/recompiler/ShaderRecompiler.h"
#include "graphics/shader/recompiler/TranslationBudget.h"
#include "graphics/shader/shaderCompiler.h"
#include <algorithm>
#include <array>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <list>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <thread>

namespace Libs::Graphics {

// One-shot CPU IR cache. It never touches Vulkan, live descriptors, the ordinary ProgramCache,
// or the guest clock. Unsupported/no-longer-needed jobs are discarded, not waited on by Get.
class ComputePretranslation {
public:
	struct Limits {
		size_t entries = 1024;
		size_t code_bytes = 8 * 1024 * 1024;
		size_t ready_bytes = 192 * 1024 * 1024;
	};
	struct Stats { size_t queued = 0, ready = 0, failed = 0, hits = 0, missed = 0, evicted = 0; };
	ComputePretranslation() = default;
	explicit ComputePretranslation(Limits limits): limits(limits) {}
	~ComputePretranslation() { Stop(); }
	ComputePretranslation(const ComputePretranslation&) = delete;
	ComputePretranslation& operator=(const ComputePretranslation&) = delete;
	static bool Enabled() {
#if defined(__cpp_exceptions)
		static const bool enabled = [] {
			const char* value = std::getenv("KYTY_CS_PRETRANSLATE");
			return value == nullptr || value[0] != '0';
		}();
		return enabled;
#else
		// Unwinding must be enabled throughout the translator before speculating on new code.
		return false;
#endif
	}

	bool Enqueue(std::span<const uint32_t> code, uint64_t hash,
	             const ShaderComputeInputInfo& info, uint32_t user_data_count, bool dump_ir = false) {
#if defined(__cpp_exceptions)
		if (code.empty() || code.size_bytes() > 128 * 1024 || user_data_count > 32) { return false; }
		try {
			auto key = KeyFor(hash, code.size(), user_data_count, info);
			std::list<std::shared_ptr<Job>> retired;
			std::lock_guard lock(mutex);
			if (stopping) { return false; }
			for (const auto& job: entries) {
				if (job->key == key) { return false; }
			}
			// Retire completed entries so this is a bounded cache, not a lifetime quota.
			// Their potentially large IR is destroyed after releasing the queue mutex.
			for (auto it = entries.begin(); it != entries.end() &&
			     (entries.size() >= limits.entries || code_bytes + code.size_bytes() > limits.code_bytes);) {
				auto current = it++;
				auto& old = **current;
				if (!old.finished) { continue; }
				ready_bytes -= old.cost;
				code_bytes -= old.code.size() * sizeof(uint32_t);
				retired.splice(retired.end(), entries, current);
				++stats.evicted;
			}
			if (entries.size() >= limits.entries || code_bytes + code.size_bytes() > limits.code_bytes) {
				return false;
			}
			auto job = std::make_shared<Job>();
			job->key = std::move(key);
			job->code.assign(code.begin(), code.end());
			job->info = info;
			job->info.stage = {};
			job->dump_ir = dump_ir;
			if (!worker.joinable()) { worker = std::thread([this] { Work(); }); }
			entries.push_back(job);
			try { queue.push_back(job); } catch (...) { entries.pop_back(); throw; }
			code_bytes += job->code.size() * sizeof(uint32_t);
			++stats.queued;
			cv.notify_one();
			return true;
		} catch (const std::exception& error) {
			LOGF("CsPretranslate: enqueue skipped hash=%016" PRIx64 " reason=%s\n", hash, error.what());
		}
#endif
		return false;
	}

	std::optional<ShaderRecompiler::TranslateResult> Take(
	    std::span<const uint32_t> code, uint64_t hash, const ShaderComputeInputInfo& info,
	    uint32_t user_data_count) {
		const auto key = KeyFor(hash, code.size(), user_data_count, info);
		std::optional<ShaderRecompiler::TranslateResult> retired;
		std::lock_guard lock(mutex);
		const char* reason = "absent";
		for (const auto& job: entries) {
			if (!(job->key == key)) {
				if (job->key.hash == hash) { reason = "static-key"; }
				continue;
			}
			reason = job->result ? "code-changed" : "not-ready";
			// The declared hash is not enough: verify the owned bytes before reusing IR.
			if (job->result && std::ranges::equal(job->code, code)) {
				auto result = std::move(job->result);
				job->result.reset();
				ready_bytes -= job->cost;
				job->cost = 0;
				job->discard = true;
				ReleaseCode(*job);
				++stats.hits;
				LOGF("CsPretranslate: hit hash=%016" PRIx64 " saved_us=%" PRIu64 " hits=%zu\n",
				     hash, job->translate_us, stats.hits);
				return result;
			}
			// The normal path is already translating it. A running job owns its code until
			// completion; its late result must not occupy cache space afterward.
			job->discard = true;
			if (job->result) {
				ready_bytes -= job->cost; job->cost = 0;
				retired = std::move(job->result); job->result.reset(); ReleaseCode(*job);
			}
			break;
		}
		++stats.missed;
		LOGF("CsPretranslate: miss hash=%016" PRIx64 " reason=%s\n", hash, reason);
		return std::nullopt;
	}
	Stats GetStats() { std::lock_guard lock(mutex); return stats; }
	// Test/teardown only. The guest path never calls this.
	void WaitIdle() {
		std::unique_lock lock(mutex);
		cv.wait(lock, [this] { return queue.empty() && !running; });
	}
	void Stop() {
		{
			std::lock_guard lock(mutex);
			if (stopping) { return; }
			stopping = true; queue.clear();
		}
		cv.notify_all();
		if (worker.joinable()) { worker.join(); }
		LOGF("CsPretranslate: summary queued=%zu ready=%zu failed=%zu hits=%zu missed=%zu evicted=%zu\n",
		     stats.queued, stats.ready, stats.failed, stats.hits, stats.missed, stats.evicted);
	}

private:
	struct Key {
		uint64_t hash;
		size_t words;
		uint32_t user_data_count;
		std::vector<uint32_t> state;
		bool operator==(const Key&) const = default;
	};
	static Key KeyFor(uint64_t hash, size_t words, uint32_t ud, const ShaderComputeInputInfo& info) {
		Key key {hash, words, ud, {}};
		BuildStageStaticKey(info, key.state);
		return key;
	}
	struct Job {
		Key key {};
		std::vector<uint32_t> code;
		ShaderComputeInputInfo info;
		std::optional<ShaderRecompiler::TranslateResult> result;
		size_t cost = 0;
		uint64_t translate_us = 0;
		bool discard = false;
		bool dump_ir = false;
		bool finished = false;
	};
	void ReleaseCode(Job& job) {
		code_bytes -= job.code.size() * sizeof(uint32_t);
		std::vector<uint32_t>().swap(job.code);
	}
	static size_t RetainedBytes(const ShaderRecompiler::TranslateResult& translated) {
		const auto& p = translated.program;
		const auto bytes = [](const auto& v) { return v.capacity() * sizeof(typename std::decay_t<decltype(v)>::value_type); };
		size_t total = sizeof(translated) + translated.decoded_dump.capacity() + translated.cfg_dump.capacity();
		total += bytes(p.block_storage) + bytes(p.blocks) + bytes(p.block_info) + bytes(p.export_info) +
		         bytes(p.dynamic_reads) + bytes(p.memory_info) + bytes(p.descriptor_sources) + bytes(p.control_flow) +
		         bytes(p.materialization_sources) + bytes(p.srt_reads) + bytes(p.clean_flat_slots);
		for (const auto& block: p.block_storage) { total += block->AllocatedBytes(); }
		for (const auto& inst: p.value_storage) { total += inst.AllocatedBytes() + 32; }
		for (const auto& block: p.control_flow) { total += bytes(block.sources) + bytes(block.successors); }
		total += bytes(p.info.buffers) + bytes(p.info.images) + bytes(p.info.samplers) + bytes(p.info.sampled_pairs) +
		         bytes(p.info.inputs) + bytes(p.info.outputs) + bytes(p.bindings.user_data_registers) + bytes(p.bindings.descriptors);
		for (const auto& image: p.info.images) { total += bytes(image.indirect_resources); }
		for (const auto& binding: p.bindings.descriptors) { total += bytes(binding.resources); }
		// Allocator overhead and small auxiliary containers: reserve twice the measured payload.
		return total * 2;
	}
	void Work() {
#if defined(__cpp_exceptions)
		for (;;) {
			std::shared_ptr<Job> job;
			{
				std::unique_lock lock(mutex);
				cv.wait(lock, [this] { return stopping || !queue.empty(); });
				if (stopping) { return; }
				job = queue.front(); queue.pop_front();
				if (job->discard) { ReleaseCode(*job); job->finished = true; cv.notify_all(); continue; }
				running = true;
			}
			std::optional<ShaderRecompiler::TranslateResult> result;
			size_t cost = 0;
			const auto begin = std::chrono::steady_clock::now();
			try {
				Common::ScopedFatalInterceptor recover([](const char* file, int line, std::string_view text) {
					throw std::runtime_error(fmt::format("{}:{} {}", file, line, text));
				});
				ShaderRecompiler::TranslationBudget budget;
				struct Scope {
					Scope(ShaderRecompiler::TranslationBudget& b) { ShaderRecompiler::TranslationBudget::current = &b; }
					~Scope() { ShaderRecompiler::TranslationBudget::current = nullptr; }
				} scope(budget);
				std::array<uint32_t, 32> user_data {};
				ShaderRecompiler::CompileOptions options;
				options.stage = ShaderType::Compute;
				options.shader_hash = job->key.hash;
				options.wave_size = job->info.wave_size;
				options.scratch_dwords = job->info.scratch_size_dwords;
				options.input_info.compute = &job->info;
				options.user_data = std::span(user_data).first(job->key.user_data_count);
				options.dump_ir = job->dump_ir;
				options.dump_label = "CsPretranslate";
				result.emplace(ShaderRecompiler::TranslateProgram(job->code, options));
				cost = RetainedBytes(*result);
			} catch (const std::exception& error) {
				LOGF("CsPretranslate: skipped hash=%016" PRIx64 " reason=%s\n", job->key.hash, error.what());
			} catch (...) {
				LOGF("CsPretranslate: skipped hash=%016" PRIx64 " unknown exception\n", job->key.hash);
			}
			const auto us = static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::microseconds>(
			    std::chrono::steady_clock::now() - begin).count());
			std::list<std::shared_ptr<Job>> retired;
			{
				std::lock_guard lock(mutex);
				if (!result) { ++stats.failed; }
				if (result && !stopping && !job->discard && cost <= limits.ready_bytes) {
					for (auto it = entries.begin(); it != entries.end();) {
						if (ready_bytes + cost <= limits.ready_bytes) { break; }
						auto current = it++;
						const auto& old = *current;
						if (old->result) {
							ready_bytes -= old->cost;
							code_bytes -= old->code.size() * sizeof(uint32_t);
							retired.splice(retired.end(), entries, current); ++stats.evicted;
						}
					}
					job->result = std::move(result); job->cost = cost; job->translate_us = us;
					ready_bytes += cost; ++stats.ready;
					LOGF("CsPretranslate: ready hash=%016" PRIx64 " us=%" PRIu64 " kb=%zu ready_kb=%zu\n",
					     job->key.hash, us, cost / 1024, ready_bytes / 1024);
				} else { ReleaseCode(*job); }
				job->finished = true;
				running = false;
			}
			cv.notify_all();
		}
#endif
	}
	Limits limits;
	Stats stats;
	std::mutex mutex;
	std::condition_variable cv;
	std::thread worker;
	std::list<std::shared_ptr<Job>> entries;
	std::deque<std::shared_ptr<Job>> queue;
	size_t code_bytes = 0, ready_bytes = 0;
	bool stopping = false, running = false;
};
} // namespace Libs::Graphics
