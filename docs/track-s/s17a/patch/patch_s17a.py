"""S17a (HPP-611): S-replay hooks in pipelineCache.cpp / pipelineCache.h (outside the translator signature set).
Anchors are whole lines; every anchor must occur exactly once (or the stated number of times). LF in, LF out."""
import sys

ROOT = 'C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/'


def load(path):
    data = open(path, 'rb').read().decode('utf-8')
    assert '\r' not in data, path
    return data


def save(path, text):
    open(path, 'wb').write(text.encode('utf-8'))


def insert_after(text, anchor, block, count=1):
    n = text.count(anchor)
    assert n == count, (anchor[:80], n)
    return text.replace(anchor, anchor + block)


def insert_before(text, anchor, block, count=1):
    n = text.count(anchor)
    assert n == count, (anchor[:80], n)
    return text.replace(anchor, block + anchor)


def replace_once(text, old, new):
    n = text.count(old)
    assert n == 1, (old[:80], n)
    return text.replace(old, new)


# ---------------------------------------------------------------------------------------------- pipelineCache.h
h = load(ROOT + 'pipelineCache.h')
h = insert_before(h, 'struct GraphicContext;\n', r'''namespace ShaderReplay {
class Store;
struct Catalogue;
class Capture;
} // namespace ShaderReplay

''')
h = insert_after(h, '\tvoid PrecachePipelines();\n', r'''
	// Track S, S17a (HPP-611, ROADMAP s122 item 524; shaderReplay.h): S-replay under KYTY_S_REPLAY. At 0 (the default)
	// ReplayInit returns at once: every member below stays empty, null or false.
	std::unique_ptr<ShaderReplay::Store>     m_replay_store;
	std::unique_ptr<ShaderReplay::Catalogue> m_replay_catalogue; // the loaded generation (input of the rebuild)
	std::unique_ptr<ShaderReplay::Capture>   m_replay_capture;
	std::string                              m_replay_state;     // "ok", "mismatch", "absent", "corrupt"
	bool                                     m_replay_rebuild     = false; // StartPrecache: the rebuild runs first
	bool                                     m_replay_hits_logged = false;
	// Source id -> permutation indices the rebuild wrote; filled on the precache thread before PrecachePipelines, read
	// under m_mutex afterwards (ProgramCache::ReplayAdopt).
	std::unordered_map<uint64_t, std::vector<uint32_t>> m_replay_rebuilt;
	void ReplayInit();
	void ReplayStop();
	void ReplayCapturePipe(uint32_t kind, uint64_t first_id, uint64_t second_id, const GraphicsPipelineKey* key);
	void ReplayRebuild();
''')
save(ROOT + 'pipelineCache.h', h)

# ---------------------------------------------------------------------------------------------- pipelineCache.cpp
c = load(ROOT + 'pipelineCache.cpp')

c = insert_after(c, '#include "graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h"\n',
                 '#include "graphics/host_gpu/renderer/pipeline/shaderReplay.h"\n'
                 '#include "loader/gamePatchFile.h"\n')
c = insert_after(c, '#include <limits>\n', '#include <optional>\n')

# Permutation: the replay flags.
c = insert_after(c, '\t\tuint8_t                                      dma_layout = 0;\n', r'''		// Track S, S17a (KYTY_S_REPLAY): ReplayCapturePending / ReplayRebuiltUnseen, set only by ReplayAdopt when the
		// knob is on; at 0 they stay 0, and the one byte test on the hit paths of Get is the whole cost there.
		// replay_spec_id: ShaderReplay::SpecId of this permutation, 0 until computed (holder of m_mutex).
		uint8_t                                      replay_flags   = 0;
		uint64_t                                     replay_spec_id = 0;
''')

# SourceEntry: R-SRC queued this run.
c = insert_after(c, '\t\tbool                               from_cache = false;\n', r'''		// Track S, S17a: 1 once the R-SRC of this source was queued in this run (holder of m_mutex).
		uint8_t                            replay_src = 0;
''')

# LoadFromTranslationCache and Resolve: flag the loaded permutations.
c = replace_once(c, '\t\tIndexPermutations(entry->first, entry->second);\n\t\treturn true;\n',
                 '\t\tIndexPermutations(entry->first, entry->second);\n'
                 '\t\tReplayAdoptAll(entry->first, entry->second); // track S, S17a\n'
                 '\t\treturn true;\n')
c = insert_after(c, '\t\t\tIndexPermutations(entry->first, entry->second);\n',
                 '\t\t\tReplayAdoptAll(entry->first, entry->second); // track S, S17a\n')

# Get, materialization memo hit.
c = insert_before(c, '\t\t\t\treturn memo_entry->handle;\n', r'''				if (memo_entry->permutation->replay_flags != 0) [[unlikely]] {
					ReplayOnHit(entry->first, entry->second, *memo_entry->permutation, params, runtime); // S17a
				}
''')

# Get, permutation found by specialization.
c = insert_before(c, '\t\t\t\tif (memo_enabled) {\n\t\t\t\t\tMemoStore(&entry->second, params.Base(), memo_log, resources, &*permutation,\n',
                  r'''				if (permutation->replay_flags != 0) [[unlikely]] {
					ReplayOnHit(entry->first, entry->second, *permutation, params, runtime); // S17a
				}
''')

# Compile: a new permutation.
c = insert_after(c, '\t\tSaveToTranslationCache(entry->first, entry->second);\n', r'''		if (replay_active) [[unlikely]] {
			// Track S, S17a: a new permutation is captured at once (and its source, the first time the run sees it).
			auto& created = entry->second.permutations.back();
			ReplayAdopt(ReplaySourceId(entry->first), created,
			            static_cast<uint32_t>(entry->second.permutations.size() - 1));
			if (created.replay_flags != 0) {
				ReplayOnHit(entry->first, entry->second, created, params, runtime);
			}
		}
''')

# ProgramCache: the replay members and methods, before the programs map.
c = insert_before(c, '\tstd::unordered_map<ProgramKey, SourceEntry, ProgramKeyHash> programs;\n', r'''	// --- Track S, S17a (HPP-611, KYTY_S_REPLAY, shaderReplay.h) ---------------------------------------------------
	static constexpr uint8_t ReplayCapturePending = 1u; // the R-SPEC of this permutation is not queued yet
	static constexpr uint8_t ReplayRebuiltUnseen  = 2u; // written by the rebuild, not hit yet in this run
	// Set by the PipelineCache constructor (ReplayInit) before any Get and never changed; false / null at mode 0.
	bool                   replay_active  = false;
	ShaderReplay::Capture* replay_capture = nullptr;
	// PipelineCache::m_replay_rebuilt: filled by the rebuild on the precache thread before PrecachePipelines (which
	// Resolves the rebuilt sources) and before the guest starts (FinishPreparation joins that thread); read under
	// PipelineCache::m_mutex.
	const std::unordered_map<uint64_t, std::vector<uint32_t>>* replay_rebuilt = nullptr;
	// Holder of PipelineCache::m_mutex: permutations of the rebuild loaded by this run, those of them a draw or a
	// dispatch hit (the hit counter of RC2 / RC11(b) of the S16b review), captures that were not taken.
	uint32_t replay_rb_marked = 0;
	uint32_t replay_rb_used   = 0;
	uint32_t replay_cap_skip  = 0;

	static uint64_t ReplaySourceId(const ProgramKey& key) {
		return ShaderReplay::SourceId(static_cast<uint32_t>(key.stage), key.hash, key.user_data_count, key.code_size,
		                              key.static_state);
	}

	// A permutation entering `permutations` (the three sites of AdoptDmaLayout); `index` is its position.
	void ReplayAdopt(uint64_t src_id, Permutation& permutation, uint32_t index) {
		if (replay_capture != nullptr) {
			permutation.replay_flags |= ReplayCapturePending;
		}
		if (replay_rebuilt != nullptr && !replay_rebuilt->empty()) {
			const auto it = replay_rebuilt->find(src_id);
			if (it != replay_rebuilt->end() && std::ranges::find(it->second, index) != it->second.end()) {
				permutation.replay_flags |= ReplayRebuiltUnseen;
				replay_rb_marked++;
			}
		}
	}

	void ReplayAdoptAll(const ProgramKey& key, SourceEntry& source) {
		if (!replay_active) {
			return;
		}
		const uint64_t src_id = ReplaySourceId(key);
		uint32_t       index  = 0;
		for (auto& permutation: source.permutations) {
			ReplayAdopt(src_id, permutation, index++);
		}
	}

	// Cold: reached only through replay_flags != 0, i.e. never at KYTY_S_REPLAY=0.
	[[gnu::noinline]] void ReplayOnHit(const ProgramKey& key, SourceEntry& source, Permutation& permutation,
	                                   const ShaderParams& params, const ShaderRecompiler::IR::SrtRuntime& runtime) {
		if ((permutation.replay_flags & ReplayRebuiltUnseen) != 0) {
			permutation.replay_flags = static_cast<uint8_t>(permutation.replay_flags & ~ReplayRebuiltUnseen);
			replay_rb_used++;
			if (replay_rb_used <= 4u || replay_rb_used % 64u == 0u) {
				LOGF("ShaderReplay: hits rb_used=%u rb_marked=%u\n", replay_rb_used, replay_rb_marked);
			}
		}
		if ((permutation.replay_flags & ReplayCapturePending) != 0) {
			permutation.replay_flags = static_cast<uint8_t>(permutation.replay_flags & ~ReplayCapturePending);
			ReplayCaptureSpec(key, source, permutation, params, runtime);
		}
	}

	uint64_t ReplaySpecId(uint64_t src_id, Permutation& permutation) {
		if (permutation.replay_spec_id == 0) {
			permutation.replay_spec_id = ShaderReplay::SpecId(src_id, permutation.specialization,
			                                                  permutation.program.bindings.push_data_start_dword);
		}
		return permutation.replay_spec_id;
	}

	// The R-SRC (first time) and the R-SPEC of one permutation: its read path recorded by one more materialization
	// through the live readers of this Get (the memo's read log, when one is being built, is detached meanwhile so the
	// witness stays what it would have been). The writer thread canonicalizes and self-checks it, off this thread.
	void ReplayCaptureSpec(const ProgramKey& key, SourceEntry& source, Permutation& permutation,
	                       const ShaderParams& params, const ShaderRecompiler::IR::SrtRuntime& runtime) {
		if (replay_capture == nullptr) {
			return;
		}
		const uint64_t src_id = ReplaySourceId(key);
		if (source.replay_src == 0) {
			source.replay_src    = 1;
			auto item            = std::make_unique<ShaderReplay::SourceItem>();
			item->src_id          = src_id;
			item->hash            = key.hash;
			item->stage           = static_cast<uint32_t>(key.stage);
			item->user_data_count = key.user_data_count;
			item->code_size       = key.code_size;
			item->static_state    = key.static_state;
			item->code.assign(params.code.begin(), params.code.end());
			item->back.assign(params.back_code.begin(), params.back_code.end());
			replay_capture->Push(std::move(item));
		}
		// Every SrtRuntime of Get carries its ShaderReadCache as userdata (Get builds it so; Compile receives it).
		auto*       read_cache = static_cast<ShaderReadCache*>(runtime.userdata);
		SrtReadLog* saved_log  = read_cache != nullptr ? read_cache->log : nullptr;
		if (read_cache != nullptr) {
			read_cache->log = nullptr;
		}
		auto                                   item = std::make_unique<ShaderReplay::SpecItem>();
		ShaderReplay::Recorder                 recorder {.inner = &runtime, .trace = &item->trace};
		ShaderRecompiler::IR::ResourceSnapshot snapshot;
		const bool ok = ShaderRecompiler::IR::MaterializeResources(source.resource_plan, recorder.Runtime(), snapshot,
		                                                           item->live);
		if (read_cache != nullptr) {
			read_cache->log = saved_log;
		}
		if (!ok || !(item->live == permutation.specialization)) {
			replay_cap_skip++;
			if (replay_cap_skip <= 8u) {
				LOGF("ShaderReplay: capture skip hash=0x%016" PRIx64 " materialized=%d skips=%u\n", key.hash,
				     ok ? 1 : 0, replay_cap_skip);
			}
			return;
		}
		item->src_id       = src_id;
		item->spec_id      = ReplaySpecId(src_id, permutation);
		item->stored_start = permutation.program.bindings.push_data_start_dword;
		item->plan         = &source.resource_plan;
		replay_capture->Push(std::move(item));
	}

	// R-PIPE: the spec id of a permutation handle; 0 when unknown.
	uint64_t ReplaySpecIdOf(uint64_t id) {
		const auto ref = by_id.find(id);
		if (ref == by_id.end()) {
			return 0;
		}
		const auto entry = programs.find(*ref->second.key);
		if (entry == programs.end() || ref->second.index >= entry->second.permutations.size()) {
			return 0;
		}
		return ReplaySpecId(ReplaySourceId(entry->first), entry->second.permutations[ref->second.index]);
	}

''')

# RecordGraphicsRecipe / RecordComputeRecipe: R-PIPE of a pipeline the run created.
c = replace_once(c, '\tif (ps_active) {\n\t\tw.Info(*ps_input_info);\n\t}\n\tAppendRecipe(w.Data().data(), w.Data().size());\n',
                 '\tif (ps_active) {\n\t\tw.Info(*ps_input_info);\n\t}\n'
                 '\tif (m_replay_capture != nullptr) [[unlikely]] {\n'
                 '\t\tReplayCapturePipe(1, key.vertex_shader_ids[0], ps_active ? key.ps_shader_id : 0, &key); // S17a\n'
                 '\t}\n'
                 '\tAppendRecipe(w.Data().data(), w.Data().size());\n')
c = replace_once(c, '\tw.U8(2);\n\tw.Key(key);\n\tw.U32(index);\n\tw.Info(input_info);\n\tAppendRecipe(w.Data().data(), w.Data().size());\n',
                 '\tw.U8(2);\n\tw.Key(key);\n\tw.U32(index);\n\tw.Info(input_info);\n'
                 '\tif (m_replay_capture != nullptr) [[unlikely]] {\n'
                 '\t\tReplayCapturePipe(2, program_id, 0, nullptr); // S17a\n'
                 '\t}\n'
                 '\tAppendRecipe(w.Data().data(), w.Data().size());\n')

# PrecachePipelines: R-PIPE of a pipeline replayed from the recipes (its R-SPEC comes when a draw hits it).
c = insert_after(c, '\t\t\t\tkey.ps_shader_id = ps_active ? ps_program.id : 0;\n', r'''				if (m_replay_capture != nullptr) [[unlikely]] {
					ReplayCapturePipe(1, vs_program.id, key.ps_shader_id, &key); // S17a
				}
''')
c = insert_after(c, '\t\t\t\tloaded_sources += cs_loaded ? 1 : 0;\n', r'''				if (m_replay_capture != nullptr) [[unlikely]] {
					ReplayCapturePipe(2, program.id, 0, nullptr); // S17a
				}
''')

# Constructor: ReplayInit before the driver cache and the precache.
c = replace_once(c, '\t     graphics.uniform_buffer_standard_layout_enabled ? 1 : 0);\n\tInitializeDriverCache();\n',
                 '\t     graphics.uniform_buffer_standard_layout_enabled ? 1 : 0);\n'
                 '\tReplayInit(); // track S, S17a: returns at once at KYTY_S_REPLAY=0\n'
                 '\tInitializeDriverCache();\n')

# Save: the writer is joined before anything else (it reads plans of the program cache).
c = replace_once(c, '\tPcwStop();\n\tCommon::LockGuard lock(m_mutex);\n\tif (m_recipes_unsaved != 0 && !PcwRecipesSaved()) {\n',
                 '\tReplayStop(); // track S, S17a: nothing at KYTY_S_REPLAY=0\n'
                 '\tPcwStop();\n\tCommon::LockGuard lock(m_mutex);\n'
                 '\tif (m_program_cache->replay_active && !m_replay_hits_logged) {\n'
                 '\t\tm_replay_hits_logged = true;\n'
                 '\t\tLOGF("ShaderReplay: hits rb_used=%u rb_marked=%u cap_skip=%u at=save\\n", m_program_cache->replay_rb_used,\n'
                 '\t\t     m_program_cache->replay_rb_marked, m_program_cache->replay_cap_skip);\n'
                 '\t}\n'
                 '\tif (m_recipes_unsaved != 0 && !PcwRecipesSaved()) {\n')

# StartPrecache: the rebuild first, when wanted.
old_start = r'''	InstallShaderSeed();
	m_recipes_path = m_program_cache->translation_cache.Directory() / "pipelines.bin";
	if (!Common::File::IsFileExisting(m_recipes_path)) {
		LOGF("PipelinePrecache: no %s yet\n", Common::PathToString(m_recipes_path).c_str());
		return;
	}
	m_precache_active.store(true, std::memory_order_release);
	m_precache_thread = std::thread([this] {
		PrecachePipelines();
		m_precache_active.store(false, std::memory_order_release);
	});
'''
new_start = r'''	InstallShaderSeed();
	m_recipes_path = m_program_cache->translation_cache.Directory() / "pipelines.bin";
	if (m_replay_catalogue != nullptr) [[unlikely]] {
		// Track S, S17a (S16a section 3 item 2): rebuild when the catalogue is compatible and the variant folder has no
		// recipes of the current signature (a compatible seed installed above is the fast path and wins).
		const auto expected = m_program_cache->translation_cache.Signature() + RecipeLayoutSignature();
		const char* skip     = nullptr;
		if (!ShaderReplay::RebuildOn()) {
			skip = "mode";
		} else if (m_replay_state == "mismatch") {
			const auto n = static_cast<uint32_t>(m_replay_catalogue->pipes.size());
			LOGF("ShaderReplay: rebuild records=%u prepared=0 rejected=%u pending=0 rej_src=0 rej_fused=0 rej_key=0 "
			     "rej_version=%u rej_shape=0 rej_translate=0 rej_emit=0 rej_val=0 rej_write=0 rej_ref=0 compat=mismatch\n",
			     n, n, n);
			skip = "compat_mismatch";
		} else if (m_replay_state != "ok" || m_replay_catalogue->pipes.empty()) {
			skip = "no_catalogue";
		} else if (RecipesFileCurrent(m_recipes_path, expected)) {
			skip = "recipes_current";
		}
		if (skip != nullptr) {
			LOGF("ShaderReplay: rebuild skipped reason=%s\n", skip);
		}
		m_replay_rebuild = skip == nullptr;
	}
	if (!m_replay_rebuild && !Common::File::IsFileExisting(m_recipes_path)) {
		LOGF("PipelinePrecache: no %s yet\n", Common::PathToString(m_recipes_path).c_str());
		return;
	}
	m_precache_active.store(true, std::memory_order_release);
	m_precache_thread = std::thread([this] {
		if (m_replay_rebuild) [[unlikely]] {
			ReplayRebuild();
		}
		if (!m_replay_rebuild || (!m_precache_stop.load() && Common::File::IsFileExisting(m_recipes_path))) {
			PrecachePipelines();
		}
		m_precache_active.store(false, std::memory_order_release);
	});
'''
c = replace_once(c, old_start, new_start)

# RecipesFileCurrent next to PipelinePrecacheEnabled (anonymous namespace of the recipe code).
c = insert_before(c, 'bool PipelinePrecacheEnabled() {\n', r'''// Track S, S17a: the recipe file exists and carries `expected` (the check of InstallShaderSeed's recipes_match).
bool RecipesFileCurrent(const std::filesystem::path& path, const std::string& expected) {
	std::ifstream file(path, std::ios::binary);
	char          magic[sizeof(RECIPES_MAGIC) - 1] {};
	uint32_t      size = 0;
	file.read(magic, sizeof(magic));
	file.read(reinterpret_cast<char*>(&size), sizeof(size));
	if (!file || std::memcmp(magic, RECIPES_MAGIC, sizeof(magic)) != 0 || size != expected.size()) {
		return false;
	}
	std::string actual(size, '\0');
	file.read(actual.data(), size);
	return static_cast<bool>(file) && actual == expected;
}

''')

# The replay functions at the end of the file.
tail = open(sys.argv[1], 'rb').read().decode('utf-8')
assert '\r' not in tail
end = '\n} // namespace Libs::Graphics\n'
assert c.endswith(end), repr(c[-60:])
c = c[:-len(end)] + '\n' + tail + end
save(ROOT + 'pipelineCache.cpp', c)
print('patched OK')
