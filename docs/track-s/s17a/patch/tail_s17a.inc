// ---------------------------------------------------------------------------------------------
// Track S, S17a (HPP-611, ROADMAP "SESSION 122" item 524(e)-(z); shaderReplay.h): S-replay under KYTY_S_REPLAY.

// Constructor, before StartPrecache and before any Get. KYTY_S_REPLAY=0: returns at once - no file is read or written,
// no "ShaderReplay:" line, no writer thread (member K1(1)).
void PipelineCache::ReplayInit() {
	const int mode = ShaderReplay::Mode();
	if (mode == 0) {
		return;
	}
	const auto title = PipelineCacheTitleId();
	auto&      cache = m_program_cache->translation_cache;
	if (title.empty() || !cache.Enabled()) {
		LOGF("ShaderReplay: mode=%d disabled (no title or no translation cache)\n", mode);
		return;
	}
	std::string app_version;
	Loader::SystemContentParamSfoGetString("APP_VER", &app_version);
	// Compatibility without the translator signature and without the GPU model (S16a section 5.1): the game, its
	// version, the record format and its input versions, and the layout of the pipeline POD of R-PIPE.
	const auto compat = fmt::format("KytyReplay{}:{}:{}:key{}:canon{}:input{}:pod{}.{}.{}", ShaderReplay::FormatVersion,
	                                title, app_version, ShaderReplay::StaticKeyVersion, ShaderReplay::CanonVersion,
	                                ShaderReplay::ReplayInputVersion, sizeof(PipelineRenderingState),
	                                sizeof(PipelineVertexInputState), sizeof(PipelineStaticParameters));
	// _ShaderCache/<title>/replay: next to the variant folders, never inside one - it outlives a signature change.
	const auto directory = std::filesystem::path("_ShaderCache") / title / "replay";
	m_replay_store       = std::make_unique<ShaderReplay::Store>(directory, compat);
	auto     catalogue   = std::make_unique<ShaderReplay::Catalogue>();
	uint64_t generation  = 0;
	uint64_t corrupt     = 0;
	m_replay_store->Load(*catalogue, m_replay_state, generation, corrupt);
	LOGF("ShaderReplay: mode=%d dir=%s compat=%s generation=%" PRIu64 " corrupt=%" PRIu64
	     " sources=%zu specs=%zu pipes=%zu test=%s\n",
	     mode, Common::PathToString(directory).c_str(), m_replay_state.c_str(), generation, corrupt,
	     catalogue->sources.size(), catalogue->specs.size(), catalogue->pipes.size(),
	     ShaderReplay::StandName(ShaderReplay::TestStand()));
	if (ShaderReplay::CaptureOn()) {
		ShaderReplay::Catalogue initial;
		if (m_replay_state == "ok") {
			initial = *catalogue;
		}
		m_replay_capture = std::make_unique<ShaderReplay::Capture>(*m_replay_store, std::move(initial),
		                                                           std::max(generation, corrupt));
		m_program_cache->replay_capture = m_replay_capture.get();
	}
	m_replay_catalogue                = std::move(catalogue);
	m_program_cache->replay_rebuilt   = &m_replay_rebuilt;
	m_program_cache->replay_active    = true;
}

// Save(): the writer drains the ring, saves the last generation and exits; it reads the plans of the program cache,
// so it is joined before anything is destroyed. Idempotent; nothing at KYTY_S_REPLAY=0.
void PipelineCache::ReplayStop() {
	if (m_replay_capture != nullptr) {
		m_replay_capture->Stop();
	}
}

// R-PIPE of one pipeline (holder of m_mutex): the spec ids of its stages and its POD; queued to the writer, which keeps
// it until every R-SPEC it names is in the catalogue.
void PipelineCache::ReplayCapturePipe(uint32_t kind, uint64_t first_id, uint64_t second_id,
                                      const GraphicsPipelineKey* key) {
	auto item     = std::make_unique<ShaderReplay::PipeItem>();
	item->kind    = kind;
	item->spec[0] = m_program_cache->ReplaySpecIdOf(first_id);
	item->spec[1] = second_id != 0 ? m_program_cache->ReplaySpecIdOf(second_id) : 0;
	if (item->spec[0] == 0 || (second_id != 0 && item->spec[1] == 0)) {
		return;
	}
	if (key != nullptr) {
		const auto append = [&item](const auto& pod) {
			const auto* bytes = reinterpret_cast<const uint8_t*>(&pod);
			item->pod.insert(item->pod.end(), bytes, bytes + sizeof(pod));
		};
		append(key->rendering);
		append(key->vertex_input);
		append(key->static_params);
	}
	std::vector<uint8_t> id_bytes(sizeof(uint32_t) + 2 * sizeof(uint64_t));
	std::memcpy(id_bytes.data(), &item->kind, sizeof(uint32_t));
	std::memcpy(id_bytes.data() + sizeof(uint32_t), item->spec, 2 * sizeof(uint64_t));
	id_bytes.insert(id_bytes.end(), item->pod.begin(), item->pod.end());
	item->pipe_id = XXH3_64bits(id_bytes.data(), id_bytes.size()) | 1u;
	m_replay_capture->Push(std::move(item));
}

namespace {

// KYTY_S_REPLAY_TEST=spec: a copy of the specialization with one field changed (the SPIR-V emitted from it must differ
// from the true one, or the stand moves on to the next permutation).
bool ReplayFlipSpecialization(ShaderRecompiler::IR::ResourceSpecialization& specialization) {
	const auto swap_xy = [](uint32_t v) { return (v & ~0x3Fu) | ((v & 7u) << 3u) | ((v >> 3u) & 7u); };
	for (auto& image: specialization.images) {
		if (swap_xy(image.shader_swizzle) != image.shader_swizzle) {
			image.shader_swizzle = swap_xy(image.shader_swizzle);
			return true;
		}
	}
	for (auto& buffer: specialization.buffers) {
		if (buffer.descriptor_format != Prospero::BufferFormat::kInvalid &&
		    swap_xy(buffer.descriptor_swizzle) != buffer.descriptor_swizzle) {
			buffer.descriptor_swizzle = swap_xy(buffer.descriptor_swizzle);
			return true;
		}
	}
	return false;
}

// The file name ShaderTranslationCache::PathOf gives a key (rebuild manifest only).
std::string ReplayCacheFileName(const ShaderTranslationCache::StoredKey& key) {
	XXH3_state_t* state = XXH3_createState();
	XXH3_64bits_reset(state);
	XXH3_64bits_update(state, &key.user_data_count, sizeof(key.user_data_count));
	XXH3_64bits_update(state, &key.code_size, sizeof(key.code_size));
	if (!key.static_state.empty()) {
		XXH3_64bits_update(state, key.static_state.data(), key.static_state.size() * sizeof(uint32_t));
	}
	const auto state_hash = XXH3_64bits_digest(state);
	XXH3_freeState(state);
	return fmt::format("{}_{:016x}_{:016x}.bin",
	                   key.stage == static_cast<uint32_t>(ShaderType::Vertex)  ? "vs"
	                   : key.stage == static_cast<uint32_t>(ShaderType::Pixel) ? "ps"
	                                                                           : "cs",
	                   key.hash, state_hash);
}

} // namespace

// The rebuild (S16a section 3; member K4): on the precache thread, before PrecachePipelines and before the guest. Per
// R-PIPE (the unit of the count, RC6): every stage - its source translated by THIS translator with the stage input
// rebuilt from the static key (form K), its R-SPEC specialized by MaterializeResources over the canonical read path
// (the rules of this translator, e.g. F19, apply by themselves), the permutation found or emitted at the push-data
// start of this translator's cursor (PS first, then VS, from 6 for a mesh stage, as GetGraphicsPrograms) - then the
// recipe with the pipeline POD of R-PIPE. Translation cache files are saved every 128 recipes and at the end (each by
// its own temporary file and rename); pipelines.bin only after the loop ran to the end - never when m_precache_stop
// stopped it (window closed), so the next start rebuilds the rest.
void PipelineCache::ReplayRebuild() {
#if defined(_WIN32)
	SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_BELOW_NORMAL);
#endif
	namespace SR = ShaderReplay;
	using ShaderRecompiler::IR::PushData;
	const auto  wall_begin = HostMicros();
	const auto& catalogue  = *m_replay_catalogue;
	auto&       cache      = m_program_cache->translation_cache;

	enum Reason : uint8_t { RSrc, RFused, RKey, RVersion, RShape, RTranslate, REmit, RVal, RWrite, RRef, RCount };
	static constexpr std::array<const char*, RCount> ReasonNames = {"src",       "fused", "key", "version", "shape",
	                                                               "translate", "emit",  "val", "write",   "ref"};
	struct Source {
		const SR::Catalogue::Source*                     record = nullptr;
		uint64_t                                         src_id = 0;
		int                                              reason = -1; // -1: prepared
		ShaderType                                       stage  = ShaderType::Unknown;
		ShaderTranslationCache::StoredKey                key;
		ShaderTranslationCache::Entry                    entry;
		bool                                             from_file = false;
		bool                                             dirty     = false;
		bool                                             saved_ok  = true;
		std::vector<uint32_t>                            user_data;
		std::unique_ptr<ShaderVertexInputInfo>           vertex;
		std::unique_ptr<ShaderPixelInputInfo>            pixel;
		std::unique_ptr<ShaderComputeInputInfo>          compute;
		ShaderRecompiler::CompileOptions                 options;
		std::optional<ShaderRecompiler::TranslateResult> first; // the translation the plan was extracted from
		std::vector<uint32_t>                            used;  // permutation indices of prepared recipes
	};
	std::unordered_map<uint64_t, std::unique_ptr<Source>> sources;
	struct SpecState {
		int                                          reason = -1;
		ShaderRecompiler::IR::ResourceSpecialization specialization;
		bool                                         counted = false;
	};
	std::unordered_map<uint64_t, SpecState> specs;

	std::array<uint32_t, RCount> rejected {};
	uint32_t prepared        = 0;
	uint64_t translate_us    = 0;
	uint32_t perms_new       = 0;
	uint32_t perms_cached    = 0;
	uint32_t rb_push_moved   = 0;
	uint32_t rb_spec_changed = 0;
	uint32_t groups_same_pc  = 0;
	uint32_t group_sources   = 0;
	bool     spec_stand_done = false;
	bool     stop_stand_done = false;

	const auto prepare = [&](const SR::Catalogue::Source& record) -> Source& {
		auto& slot = sources[record.header.src_id];
		if (slot != nullptr) {
			return *slot;
		}
		slot           = std::make_unique<Source>();
		auto& s        = *slot;
		s.record       = &record;
		s.src_id       = record.header.src_id;
		s.stage        = static_cast<ShaderType>(record.header.stage);
		s.key          = {.stage           = record.header.stage,
		                  .hash            = record.header.hash,
		                  .user_data_count = record.header.user_data_count,
		                  .code_size       = record.header.code_size,
		                  .static_state    = record.static_state};
		if (record.code.empty() || record.code.size() != record.header.code_size) {
			s.reason = RSrc;
			return s;
		}
		{
			Loader::GamePatchFile::Sha256 sha;
			sha.Update(reinterpret_cast<const uint8_t*>(record.code.data()), record.code.size() * sizeof(uint32_t));
			const auto hex = sha.FinalHex();
			for (size_t i = 0; i < 32; i++) {
				if (static_cast<uint8_t>(std::stoul(hex.substr(2 * i, 2), nullptr, 16)) != record.header.sha256[i]) {
					s.reason = RSrc;
					return s;
				}
			}
		}
		// Form K: the stage input from the static key, accepted only when it gives the same key back.
		std::string           why;
		std::vector<uint32_t> again;
		bool                  key_ok = false;
		if (s.stage == ShaderType::Vertex || s.stage == ShaderType::Mesh) {
			s.vertex = std::make_unique<ShaderVertexInputInfo>();
			key_ok   = SR::VertexFromKey(record.static_state, s.stage, *s.vertex, why);
			if (key_ok) {
				BuildStageStaticKey(*s.vertex, again);
			}
		} else if (s.stage == ShaderType::Pixel) {
			s.pixel = std::make_unique<ShaderPixelInputInfo>();
			key_ok  = SR::PixelFromKey(record.static_state, *s.pixel, why);
			if (key_ok) {
				BuildStageStaticKey(*s.pixel, again);
			}
		} else if (s.stage == ShaderType::Compute) {
			s.compute = std::make_unique<ShaderComputeInputInfo>();
			key_ok    = SR::ComputeFromKey(record.static_state, *s.compute, why);
			if (key_ok) {
				BuildStageStaticKey(*s.compute, again);
			}
		}
		if (!key_ok || again != record.static_state) {
			s.reason = RKey;
			return s;
		}
		// The options of ProgramCache::Compile for this stage.
		s.user_data.assign(record.header.user_data_count, 0u);
		auto& options       = s.options;
		options.stage       = s.stage;
		options.shader_hash = record.header.hash;
		options.user_data   = s.user_data;
		options.back_code   = record.back;
		options.dump_ir     = Config::GetShaderLogDirection() != Config::LogDirection::Silent;
		options.early_dump  = options.dump_ir;
		ShaderStageInputInfo stage_input {};
		if (s.vertex != nullptr) {
			stage_input.vertex     = s.vertex.get();
			options.dump_label     = s.stage == ShaderType::Mesh ? "ShaderRecompiler MS" : "ShaderRecompiler VS";
			options.user_data_base = 8;
			if (s.stage == ShaderType::Mesh) {
				options.user_data_base = 0;
				options.wave_size      = s.vertex->mesh.wave_size;
			} else {
				options.detect_wave_size = true;
			}
		} else if (s.pixel != nullptr) {
			stage_input.pixel        = s.pixel.get();
			options.dump_label       = "ShaderRecompiler PS";
			options.wave_size        = s.pixel->wave_size;
			options.detect_wave_size = true;
		} else {
			stage_input.compute = s.compute.get();
			options.dump_label  = "ShaderRecompiler CS";
			options.wave_size   = s.compute->wave_size;
		}
		options.input_info = stage_input;
		// The entry of this key under the current signature, when a previous start (or a run) wrote it; otherwise
		// translate now and take the plan from that translation.
		if (m_program_cache->LoadEntry(s.key, s.entry)) {
			s.from_file = true;
		} else {
			const auto begin = HostMicros();
			s.first.emplace(ShaderRecompiler::TranslateProgram(record.code, options));
			translate_us += HostMicros() - begin;
			s.entry.plan = ShaderRecompiler::IR::ExtractResourcePlan(s.first->program);
		}
		groups_same_pc += SR::SamePcGroups(s.entry.plan.info);
		group_sources++;
		return s;
	};

	// The permutation of (specialization, cursor): an existing one at the start this cursor gives, or a new one.
	const auto permutation_for = [&](Source& s, const ShaderRecompiler::IR::ResourceSpecialization& specialization,
	                                 uint32_t cursor, int& reason) -> int {
		for (uint32_t i = 0; i < s.entry.permutations.size(); i++) {
			const auto& p      = s.entry.permutations[i];
			const auto& layout = p.program.bindings;
			if (p.specialization == specialization &&
			    layout.push_data_start_dword == PushData::StartFor(cursor, layout.ShaderDataDwords())) {
				perms_cached++;
				return static_cast<int>(i);
			}
		}
		const auto begin      = HostMicros();
		auto       translated = s.first.has_value() ? std::move(*s.first)
		                                            : ShaderRecompiler::TranslateProgram(s.record->code, s.options);
		s.first.reset();
		auto result = ShaderRecompiler::CompileProgram(std::move(translated), s.options, specialization, cursor);
		if (SR::TestStand() == SR::Stand::Spec && !spec_stand_done) {
			// KYTY_S_REPLAY_TEST=spec (member K4): this one permutation is emitted from a changed specialization and stored
			// under the true one - the comparison with the live translation must see it (rb_live_mismatch > 0).
			auto changed = specialization;
			if (ReplayFlipSpecialization(changed)) {
				auto alt = ShaderRecompiler::CompileProgram(
				    ShaderRecompiler::TranslateProgram(s.record->code, s.options), s.options, changed, cursor);
				if (alt.spirv != result.spirv &&
				    ValidateShaderSpirv(s.options.dump_label, s.record->header.hash, alt.spirv)) {
					result.spirv    = std::move(alt.spirv);
					spec_stand_done = true;
					LOGF("ShaderReplay: stand spec applied file=%s permutation=%zu\n",
					     ReplayCacheFileName(s.key).c_str(), s.entry.permutations.size());
				}
			}
		}
		translate_us += HostMicros() - begin;
		if (!ValidateShaderSpirv(s.options.dump_label, s.record->header.hash, result.spirv)) {
			reason = RVal;
			return -1;
		}
		s.entry.permutations.push_back({.specialization = specialization,
		                                .program        = std::move(result.program).TakeCompiledInfo(),
		                                .spirv          = std::move(result.spirv)});
		s.dirty = true;
		perms_new++;
		return static_cast<int>(s.entry.permutations.size() - 1);
	};

	const auto save_dirty = [&]() {
		for (auto& [id, s]: sources) {
			(void)id;
			if (s->dirty && !s->entry.permutations.empty()) {
				const ShaderTranslationCache::Key key {.stage           = s->key.stage,
				                                       .hash            = s->key.hash,
				                                       .user_data_count = s->key.user_data_count,
				                                       .code_size       = s->key.code_size,
				                                       .static_state    = s->key.static_state};
				if (!cache.Save(key, s->entry.plan, s->entry.permutations)) {
					s->saved_ok = false;
				}
				s->dirty = false;
			}
		}
	};

	struct Prepared {
		std::vector<uint8_t>           bytes;
		std::array<Source*, 2>         stages {};
		std::array<uint32_t, 2>        indices {};
	};
	std::vector<Prepared> recipes;
	const auto            records = static_cast<uint32_t>(catalogue.pipes.size());
	constexpr size_t      PodSize = sizeof(PipelineRenderingState) + sizeof(PipelineVertexInputState) +
	                           sizeof(PipelineStaticParameters);
	uint32_t processed = 0;
	for (const auto& pipe: catalogue.pipes) {
		if (m_precache_stop.load()) {
			break;
		}
		if (SR::TestStand() == SR::Stand::Stop && !stop_stand_done && processed >= records / 2u) {
			stop_stand_done = true;
			LOGF("ShaderReplay: stand stop applied processed=%u records=%u\n", processed, records);
			SR::StandRequestClose();
		}
		if (processed != 0 && processed % 128u == 0) {
			save_dirty();
		}
		processed++;
		int      reason = -1;
		Prepared out;
		// Stage order of the push-data cursor: graphics PS (spec[1]) then VS (spec[0]); compute spec[0].
		const bool graphics = pipe.header.kind == 1;
		if ((!graphics && pipe.header.kind != 2) || (graphics && pipe.pod.size() != PodSize) ||
		    (!graphics && !pipe.pod.empty())) {
			reason = RVersion;
		}
		std::array<std::pair<uint64_t, int>, 2> order {};
		uint32_t                                stage_count = 0;
		if (graphics && pipe.header.spec[1] != 0) {
			order[stage_count++] = {pipe.header.spec[1], 1};
		}
		order[stage_count++] = {pipe.header.spec[0], 0};
		uint32_t cursor      = 0;
		if (graphics && reason < 0) {
			// The cursor starts after the mesh draw words when the vertex stage is a mesh stage.
			const auto* vs_spec = catalogue.FindSpec(pipe.header.spec[0]);
			const auto* vs_src  = vs_spec != nullptr ? catalogue.FindSource(vs_spec->header.src_id) : nullptr;
			if (vs_src != nullptr && vs_src->header.stage == static_cast<uint32_t>(ShaderType::Mesh)) {
				cursor = PushData::MeshDrawDwordCount;
			}
		}
		for (uint32_t k = 0; k < stage_count && reason < 0; k++) {
			const auto [spec_id, slot] = order[k];
			const auto* spec_record    = catalogue.FindSpec(spec_id);
			const auto* src_record     = spec_record != nullptr ? catalogue.FindSource(spec_record->header.src_id) : nullptr;
			if (spec_record == nullptr) {
				reason = RRef;
				break;
			}
			if (src_record == nullptr) {
				reason = RSrc;
				break;
			}
			auto& s = prepare(*src_record);
			if (s.reason >= 0) {
				reason = s.reason;
				break;
			}
			// Stage kinds: graphics slot 0 vertex or mesh, slot 1 pixel; compute slot 0 compute.
			const bool kind_ok = graphics ? (slot == 1 ? s.pixel != nullptr : s.vertex != nullptr) : s.compute != nullptr;
			if (!kind_ok) {
				reason = RKey;
				break;
			}
			auto& state = specs[spec_id];
			if (!state.counted) {
				state.counted = true;
				if (!SR::Specialize(s.entry.plan, *spec_record, state.specialization)) {
					state.reason = RShape;
				} else if (SR::SpecializationHash(state.specialization) != spec_record->header.live_spec_hash) {
					rb_spec_changed++;
				}
			}
			if (state.reason >= 0) {
				reason = state.reason;
				break;
			}
			const int index = permutation_for(s, state.specialization, cursor, reason);
			if (index < 0) {
				break;
			}
			const auto& bindings = s.entry.permutations[static_cast<size_t>(index)].program.bindings;
			if (bindings.push_data_start_dword != spec_record->header.stored_start) {
				rb_push_moved++;
			}
			bindings.AdvancePushData(cursor);
			out.stages[slot]  = &s;
			out.indices[slot] = static_cast<uint32_t>(index);
		}
		if (reason >= 0) {
			rejected[static_cast<size_t>(reason)]++;
			continue;
		}
		RecipeWriter w;
		if (graphics) {
			const bool ps_active = out.stages[1] != nullptr;
			w.U8(1);
			w.Key(out.stages[0]->key);
			w.U32(out.indices[0]);
			w.U8(ps_active ? 1 : 0);
			if (ps_active) {
				w.Key(out.stages[1]->key);
				w.U32(out.indices[1]);
			}
			w.Bytes(pipe.pod.data(), pipe.pod.size()); // PipelineRenderingState, PipelineVertexInputState, static params
			w.Info(*out.stages[0]->vertex);            // stage inputs rebuilt from the keys (K1(6): vertex input = POD)
			if (ps_active) {
				w.Info(*out.stages[1]->pixel);
			}
		} else {
			w.U8(2);
			w.Key(out.stages[0]->key);
			w.U32(out.indices[0]);
			w.Info(*out.stages[0]->compute);
		}
		out.bytes = std::move(w.Data());
		recipes.push_back(std::move(out));
		prepared++;
	}
	const bool stopped = m_precache_stop.load();
	save_dirty();
	// A recipe that names a source whose file could not be saved is rejected (write), one reason per recipe.
	std::vector<uint8_t> body;
	uint32_t             count = 0;
	for (auto& r: recipes) {
		const bool saved = (r.stages[0] == nullptr || r.stages[0]->saved_ok) &&
		                   (r.stages[1] == nullptr || r.stages[1]->saved_ok);
		if (!saved) {
			prepared--;
			rejected[RWrite]++;
			continue;
		}
		body.insert(body.end(), r.bytes.begin(), r.bytes.end());
		count++;
		for (uint32_t k = 0; k < 2; k++) {
			if (r.stages[k] != nullptr) {
				auto& used = r.stages[k]->used;
				if (std::ranges::find(used, r.indices[k]) == used.end()) {
					used.push_back(r.indices[k]);
				}
			}
		}
	}
	for (const auto& [id, s]: sources) {
		if (!s->used.empty()) {
			m_replay_rebuilt[id] = s->used;
		}
	}
	const char* recipes_state = "written";
	if (stopped) {
		recipes_state = "stopped";
	} else if (count == 0) {
		recipes_state = "empty";
	} else {
		RecipeWriter w;
		w.Bytes(RECIPES_MAGIC, sizeof(RECIPES_MAGIC) - 1);
		const auto signature = cache.Signature() + RecipeLayoutSignature();
		w.U32(static_cast<uint32_t>(signature.size()));
		w.Bytes(signature.data(), signature.size());
		w.U32(count);
		w.Bytes(body.data(), body.size());
		const auto& payload = w.Data();
		auto        temp    = m_recipes_path;
		temp += ".tmp";
		Common::File file;
		uint32_t     written = 0;
		if (Common::File::CreateDirectories(m_recipes_path.parent_path()) && file.Create(temp)) {
			file.Write(payload.data(), static_cast<uint32_t>(payload.size()), &written);
		}
		const bool flushed = !file.IsInvalid() && file.Flush();
		file.Close();
		if (written != payload.size() || !flushed || !Common::File::RenameFile(temp, m_recipes_path)) {
			recipes_state = "failed";
		}
	}
	// Manifest for the comparison with a live translation (member K4): file, permutation index, specialization hash,
	// push-data start, XXH3 of the SPIR-V - every permutation a prepared recipe uses.
	if (!stopped && count != 0) {
		std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}", cache.Signature());
		for (const auto& [id, s]: sources) {
			(void)id;
			for (const auto index: s->used) {
				const auto& p = s->entry.permutations[index];
				manifest += fmt::format("{}\t{}\t{:016x}\t{}\t{:016x}\n", ReplayCacheFileName(s->key), index,
				                        ShaderReplay::SpecializationHash(p.specialization),
				                        p.program.bindings.push_data_start_dword,
				                        XXH3_64bits(p.spirv.data(), p.spirv.size() * sizeof(uint32_t)));
			}
		}
		std::ofstream file(m_replay_store->Directory() / "rebuild_manifest.tsv", std::ios::binary | std::ios::trunc);
		file << manifest;
	}
	uint32_t rejected_total = 0;
	for (const auto n: rejected) {
		rejected_total += n;
	}
	const uint32_t pending = records - prepared - rejected_total;
	LOGF("ShaderReplay: rebuild records=%u prepared=%u rejected=%u pending=%u rej_src=%u rej_fused=%u rej_key=%u "
	     "rej_version=%u rej_shape=%u rej_translate=%u rej_emit=%u rej_val=%u rej_write=%u rej_ref=%u translate_ms=%" PRIu64
	     " wall_ms=%" PRIu64 " perms_new=%u perms_cached=%u rb_push_moved=%u rb_spec_changed=%u groups_same_pc=%u "
	     "group_sources=%u pipelines_bin=%s\n",
	     records, prepared, rejected_total, pending, rejected[RSrc], rejected[RFused], rejected[RKey], rejected[RVersion],
	     rejected[RShape], rejected[RTranslate], rejected[REmit], rejected[RVal], rejected[RWrite], rejected[RRef],
	     translate_us / 1000u, (HostMicros() - wall_begin) / 1000u, perms_new, perms_cached, rb_push_moved,
	     rb_spec_changed, groups_same_pc, group_sources, recipes_state);
	// The other two kinds, by their own records (RC6): sources and specializations the recipes reached.
	uint32_t src_ok  = 0;
	uint32_t src_bad = 0;
	std::array<uint32_t, RCount> src_reason {};
	for (const auto& [id, s]: sources) {
		(void)id;
		if (s->reason >= 0) {
			src_bad++;
			src_reason[static_cast<size_t>(s->reason)]++;
		} else if (!s->saved_ok) {
			src_bad++;
			src_reason[RWrite]++;
		} else {
			src_ok++;
		}
	}
	uint32_t spec_ok  = 0;
	uint32_t spec_bad = 0;
	for (const auto& [id, state]: specs) {
		(void)id;
		(state.reason >= 0 ? spec_bad : spec_ok)++;
	}
	LOGF("ShaderReplay: rebuild-src records=%zu prepared=%u rejected=%u rej_src=%u rej_key=%u rej_write=%u\n",
	     sources.size(), src_ok, src_bad, src_reason[RSrc], src_reason[RKey], src_reason[RWrite]);
	LOGF("ShaderReplay: rebuild-spec records=%zu prepared=%u rejected=%u rej_shape=%u\n", specs.size(), spec_ok,
	     spec_bad, spec_bad);
	(void)ReasonNames;
}
