// Track S, S16d (HPP-608, ROADMAP s122 item 516(v)(1)-(12)): probe P-S16, the offline gate K0 of S-replay.
// Test code only (shader_cfg_tests); no emulator code, no signature file is touched (the signature set is
// src/graphics/shader/** plus CMakeLists.txt and src/generate_version.cmake). Included by shaderCfgTests.cpp
// after its own namespaces; entered by KYTY_S16D_JOBS=<jobs file> KYTY_S16D_OUT=<result file> before any test.
//
// One job = one stage of one recipe of the S13b catalogue in one arm and one input form:
//   J <id> <arm A|B> <form A0|K|C> <cache file> <permutation> <gcn file> <input file|-> <start S|n> <f19 -|k16UNorm|k8UNorm>
//     <corrupt 0|stride|format|spirv>
// form A0 - the raw recipe bytes of Shader*InputInfo (no canonicalization; harness control, item 516(v)(3));
// form K  - the input rebuilt from the static key of the stage stored in the cache file (item 516(v)(2));
// form C  - the raw recipe bytes with the address fields canonicalized by the rules of S16a section 2.2
//           (V# base and ShaderVertexInputBuffer::addr := 0 when 0, else 0x100 | (value & 0xF)).
// start S - the push-data start of the stored permutation (arm A, RC1); n - the cursor the driver computed over
// the recipe PS -> VS (arm B). The result lines carry the SPIR-V identity against the stored permutation, the
// binding layout (start, shader data dwords) for the driver's cursor, the plan identity and the validation.
// Before each phase a line "P <id> <T|E|V>" is flushed, so a fatal exit inside the translator is attributed to
// the job and phase by the driver, which restarts the process after the failed job.

#include <map>

namespace Libs::Graphics::S16dProbe {

namespace SR = ShaderRecompiler;

struct ProbeJob {
	std::string id;
	std::string arm;
	std::string form;
	std::string cache;
	uint32_t    permutation = 0;
	std::string gcn;
	std::string input;
	bool        start_stored = true;
	uint32_t    start        = 0;
	std::string f19;
	std::string corrupt;
};

struct CachedFile {
	bool                                                ok = false;
	Libs::Graphics::ShaderTranslationCache::StoredKey key;
	Libs::Graphics::ShaderTranslationCache::Entry     entry;
};

FILE* g_out = nullptr;

void Out(const std::string& line) {
	std::fputs(line.c_str(), g_out);
	std::fputc(10, g_out);
	std::fflush(g_out);
}

bool ReadAll(const std::string& path, std::vector<uint8_t>& bytes) {
	FILE* file = std::fopen(path.c_str(), "rb");
	if (file == nullptr) {
		return false;
	}
	bytes.clear();
	uint8_t buffer[65536];
	size_t  n = 0;
	while ((n = std::fread(buffer, 1, sizeof(buffer), file)) > 0) {
		bytes.insert(bytes.end(), buffer, buffer + n);
	}
	std::fclose(file);
	return true;
}

// The recipe reader of pipelineCache.cpp (RecipeReader::Info): the bytes of the struct except its runtime part.
template <typename T>
bool LoadInfo(const std::vector<uint8_t>& bytes, T& info) {
	if (bytes.size() != sizeof(T)) {
		return false;
	}
	auto*        base  = reinterpret_cast<uint8_t*>(&info);
	const auto*  stage = reinterpret_cast<const uint8_t*>(&info.stage);
	const size_t off   = static_cast<size_t>(stage - base);
	const size_t tail  = off + sizeof(ShaderStageRuntime);
	std::memcpy(base, bytes.data(), off);
	std::memcpy(base + tail, bytes.data() + tail, sizeof(T) - tail);
	return true;
}

uint64_t CanonAddress(uint64_t value) {
	return value == 0 ? 0 : (0x100u | (value & 0xFu));
}

// S16a section 2.2: the address fields of the stage input (V# base 48 bits, the vertex buffer address).
void CanonVertex(ShaderVertexInputInfo& info) {
	for (auto& resource: info.resources) {
		const uint64_t base = resource.Base48();
		const uint64_t c    = CanonAddress(base);
		resource.fields[0]  = static_cast<uint32_t>(c & 0xffffffffu);
		resource.fields[1]  = (resource.fields[1] & 0xffff0000u) | static_cast<uint32_t>((c >> 32u) & 0xffffu);
	}
	for (auto& buffer: info.buffers) {
		buffer.addr = CanonAddress(buffer.addr);
	}
}

// Word index of the first resource record in the vertex static key (BuildStageStaticKey order, shader.cpp).
bool VertexResourceBase(const std::vector<uint32_t>& s, size_t& base) {
	size_t i = 7;
	if (s.size() < i) {
		return false;
	}
	if (s[6] != 0) {
		i += 6;
	}
	if (i >= s.size()) {
		return false;
	}
	const uint32_t mesh = s[i++];
	if (mesh != 0) {
		i += 10;
	}
	if (i >= s.size()) {
		return false;
	}
	const uint32_t tess = s[i++];
	if (tess != 0) {
		i += 6;
	}
	base = i;
	return i <= s.size();
}

// Inverse of BuildStageStaticKey(ShaderVertexInputInfo): every field the key holds; the rest keeps its default
// (addresses 0, record counts 0, no vertex buffers), logical_stage from the key stage.
bool VertexFromKey(const std::vector<uint32_t>& s, ShaderType stage, ShaderVertexInputInfo& info,
                   std::string& why) {
	if (s.size() < 9) {
		why = "short";
		return false;
	}
	size_t i            = 0;
	info.fetch_embedded = s[i++] != 0;
	info.fetch_attrib_reg    = static_cast<int>(s[i++]);
	info.fetch_buffer_reg    = static_cast<int>(s[i++]);
	info.resources_num       = static_cast<int>(s[i++]);
	info.scratch_size_dwords = s[i++];
	info.pa_cl_vs_out_cntl   = s[i++];
	info.clip_space.enabled  = s[i++] != 0;
	if (info.resources_num < 0 || info.resources_num > ShaderVertexInputInfo::RES_MAX) {
		why = "resources_num";
		return false;
	}
	if (info.clip_space.enabled) {
		if (i + 6 > s.size()) {
			why = "clip";
			return false;
		}
		for (float& value: info.clip_space.scale) {
			value = std::bit_cast<float>(s[i++]);
		}
		for (float& value: info.clip_space.offset) {
			value = std::bit_cast<float>(s[i++]);
		}
		for (float& value: info.clip_space.half_extent) {
			value = std::bit_cast<float>(s[i++]);
		}
	}
	if (i >= s.size()) {
		why = "mesh";
		return false;
	}
	info.mesh.threads_num[0] = s[i++];
	if (info.mesh.threads_num[0] != 0) {
		if (i + 10 > s.size()) {
			why = "mesh";
			return false;
		}
		auto& mesh                = info.mesh;
		mesh.wave_size            = s[i++];
		mesh.host_subgroup_size   = s[i++];
		mesh.lds_size_dwords      = s[i++];
		mesh.scratch_size_dwords  = s[i++];
		mesh.input_primitive      = s[i++];
		mesh.primitives_per_group = s[i++];
		mesh.vertices_per_group   = s[i++];
		mesh.max_vertices         = s[i++];
		mesh.max_primitives       = s[i++];
		mesh.provoking_vertex     = s[i++];
	}
	if (i >= s.size()) {
		why = "tess";
		return false;
	}
	info.tess.input_control_points = s[i++];
	if (info.tess.input_control_points != 0) {
		if (i + 6 > s.size()) {
			why = "tess";
			return false;
		}
		auto& tess                 = info.tess;
		tess.output_control_points = s[i++];
		tess.ls_stride             = s[i++];
		tess.hs_stride             = s[i++];
		tess.domain                = s[i++];
		tess.partitioning          = s[i++];
		tess.output_topology       = s[i++];
	}
	if (i + static_cast<size_t>(info.resources_num) * 13u != s.size()) {
		why = "resources";
		return false;
	}
	for (int r = 0; r < info.resources_num; r++) {
		auto& destination          = info.resources_dst[r];
		destination.register_start = static_cast<int>(s[i++]);
		destination.registers_num  = static_cast<int>(s[i++]);
		destination.fetch_index    = s[i++];
		destination.attr_id        = static_cast<int>(s[i++]);
		const uint32_t stride      = s[i++];
		const uint32_t swizzle     = s[i++];
		const uint32_t x           = s[i++];
		const uint32_t y           = s[i++];
		const uint32_t z           = s[i++];
		const uint32_t w           = s[i++];
		const uint32_t format      = s[i++];
		const uint32_t oob         = s[i++];
		const uint32_t add_tid     = s[i++];
		auto&          resource    = info.resources[r];
		resource.fields[0]         = 0;
		resource.fields[1]         = ((stride & 0x3FFFu) << 16u) | ((swizzle & 1u) << 31u);
		resource.fields[2]         = 0;
		resource.fields[3]         = (x & 7u) | ((y & 7u) << 3u) | ((z & 7u) << 6u) | ((w & 7u) << 9u) |
		                     ((format & 0x7Fu) << 12u) | ((add_tid & 1u) << 23u) | ((oob & 3u) << 28u);
	}
	info.logical_stage = stage == ShaderType::Mesh ? ShaderType::Mesh : ShaderType::Vertex;
	return true;
}

// Inverse of BuildStageStaticKey(ShaderPixelInputInfo) (the KYTY_RECOMPILE order of this file).
bool PixelFromKey(const std::vector<uint32_t>& s, ShaderPixelInputInfo& pixel, std::string& why) {
	if (s.size() < 30) {
		why = "short";
		return false;
	}
	size_t i                         = 0;
	pixel.scratch_size_dwords        = s[i++];
	pixel.input_num                  = s[i++];
	pixel.wave_size                  = s[i++];
	pixel.ps_system_input_base       = s[i++];
	pixel.vs_export_count            = s[i++];
	pixel.custom_interpolation_mask  = s[i++];
	pixel.ps_perspective_center_vgpr = s[i++];
	for (auto& v: pixel.ps_barycentric_vgpr) {
		v = s[i++];
	}
	pixel.ps_pos_x                     = s[i++] != 0;
	pixel.ps_pos_y                     = s[i++] != 0;
	pixel.ps_pos_z                     = s[i++] != 0;
	pixel.ps_pos_w                     = s[i++] != 0;
	pixel.ps_front_face                = s[i++] != 0;
	pixel.ps_ancillary                 = s[i++] != 0;
	pixel.ps_no_perspective            = s[i++] != 0;
	pixel.ps_pixel_kill_enable         = s[i++] != 0;
	pixel.ps_depth_export_enable       = s[i++] != 0;
	pixel.ps_sample_mask_export_enable = s[i++] != 0;
	pixel.ps_early_z                   = s[i++] != 0;
	if (i + 8 + 2 > s.size()) {
		why = "short";
		return false;
	}
	for (auto& m: pixel.target_output_mode) {
		m = static_cast<uint8_t>(s[i++]);
	}
	for (uint32_t base = 0; base < pixel.target_export_mapping.size(); base += 4u) {
		const uint32_t packed = s[i++];
		for (uint32_t k = 0; k < 4u; k++) {
			pixel.target_export_mapping[base + k].packed = static_cast<uint8_t>(packed >> (k * 8u));
		}
	}
	if (pixel.input_num > 32u || i + pixel.input_num != s.size()) {
		why = "inputs";
		return false;
	}
	for (uint32_t k = 0; k < pixel.input_num; k++) {
		pixel.interpolator_settings[k] = s[i++];
	}
	return true;
}

// Inverse of BuildStageStaticKey(ShaderComputeInputInfo).
bool ComputeFromKey(const std::vector<uint32_t>& s, ShaderComputeInputInfo& compute, std::string& why) {
	if (s.size() != 14) {
		why = "size";
		return false;
	}
	compute.workgroup_register         = static_cast<int>(s[0]);
	compute.wave_size                  = s[1];
	compute.host_subgroup_size         = s[2];
	compute.thread_ids_num             = static_cast<int>(s[3]);
	compute.lds_size_dwords            = s[4];
	compute.scratch_size_dwords        = s[5];
	compute.dispatch_thread_dimensions = s[6] != 0;
	for (int i = 0; i < 3; i++) {
		compute.threads_num[i] = s[7 + 2 * i];
		compute.group_id[i]    = s[8 + 2 * i] != 0;
	}
	compute.tg_size_en = s[13] != 0;
	return true;
}

// Identity of a plan resource for the matching of item 516(v)(8): kind, first_use_pc, ordinal among the
// resources of the same kind and first_use_pc (in plan order).
struct ResourceIdentity {
	uint32_t kind    = 0;
	uint32_t pc      = 0;
	uint32_t ordinal = 0;
	bool     operator==(const ResourceIdentity&) const = default;
};

std::vector<ResourceIdentity> Identities(const SR::IR::ShaderInfo& info) {
	std::vector<ResourceIdentity> out;
	std::map<std::pair<uint32_t, uint32_t>, uint32_t> seen;
	for (const auto& b: info.buffers) {
		out.push_back({0u, b.first_use_pc, seen[{0u, b.first_use_pc}]++});
	}
	for (const auto& image: info.images) {
		out.push_back({1u, image.first_use_pc, seen[{1u, image.first_use_pc}]++});
	}
	return out;
}

// Item 516(v)(8): the stored specialization carried to the resources of the new plan by identity, not by
// index. The images past the plan count (indirect table candidates) keep their order after the plan images.
bool MapSpecialization(const SR::IR::ShaderInfo& stored_plan, const SR::IR::ShaderInfo& new_plan,
                       const SR::IR::ResourceSpecialization& stored, SR::IR::ResourceSpecialization& out,
                       bool& identity_order, std::string& why) {
	identity_order = true;
	if (stored.buffers.size() != stored_plan.buffers.size() || stored.images.size() < stored_plan.images.size()) {
		why = "stored_counts";
		return false;
	}
	if (new_plan.buffers.size() != stored_plan.buffers.size() || new_plan.images.size() != stored_plan.images.size()) {
		why = "plan_counts";
		return false;
	}
	const auto old_ids = Identities(stored_plan);
	const auto new_ids = Identities(new_plan);
	out.buffers.assign(new_plan.buffers.size(), {});
	out.images.assign(stored.images.size(), {});
	std::vector<bool> used(old_ids.size(), false);
	for (size_t n = 0; n < new_ids.size(); n++) {
		size_t found = old_ids.size();
		for (size_t o = 0; o < old_ids.size(); o++) {
			if (!used[o] && old_ids[o] == new_ids[n]) {
				found = o;
				break;
			}
		}
		if (found == old_ids.size()) {
			why = "unmatched";
			return false;
		}
		used[found] = true;
		if (found != n) {
			identity_order = false;
		}
		const size_t nb = new_plan.buffers.size();
		if (n < nb) {
			out.buffers[n] = stored.buffers[found];
		} else {
			out.images[n - nb] = stored.images[found - nb];
		}
	}
	for (size_t k = stored_plan.images.size(); k < stored.images.size(); k++) {
		out.images[k] = stored.images[k];
	}
	return true;
}

// The check of ValidateShaderSpirv (pipelineCache.cpp, KYTY_FIX_SVAL=1) with the options of this machine's device:
// SPV_ENV_VULKAN_1_3 and uniformBufferStandardLayout (the const-bank token of the catalogue signature needs it).
bool Validate(const std::vector<uint32_t>& spirv, std::string& message) {
	spvtools::SpirvTools tools(SPV_ENV_VULKAN_1_3);
	tools.SetMessageConsumer([&message](spv_message_level_t, const char*, const spv_position_t&, const char* text) {
		if (message.empty()) {
			message = text;
		}
	});
	spvtools::ValidatorOptions options;
	options.SetUniformBufferStandardLayout(true);
	return tools.Validate(spirv.data(), spirv.size(), options);
}

std::string Hex64(uint64_t value) {
	char text[24];
	std::snprintf(text, sizeof(text), "%016llx", static_cast<unsigned long long>(value));
	return text;
}

std::string Clean(std::string text) {
	for (char& c: text) {
		if (c == ' ' || c == 10 || c == 13 || c == 9) {
			c = '_';
		}
	}
	if (text.size() > 120) {
		text.resize(120);
	}
	return text;
}

bool ParseJob(const std::string& line, ProbeJob& job) {
	std::istringstream in(line);
	std::string        tag;
	std::string        start;
	in >> tag >> job.id >> job.arm >> job.form >> job.cache >> job.permutation >> job.gcn >> job.input >> start >>
	    job.f19 >> job.corrupt;
	if (in.fail() || tag != "J") {
		return false;
	}
	job.start_stored = start == "S";
	job.start        = job.start_stored ? 0u : static_cast<uint32_t>(std::strtoul(start.c_str(), nullptr, 10));
	return true;
}

void RunJob(const ProbeJob& job, std::map<std::string, CachedFile>& files) {
	auto& file = files[job.cache];
	if (!file.ok) {
		file.ok = Libs::Graphics::ShaderTranslationCache::ReadFileUnchecked(job.cache, file.key, file.entry);
		if (!file.ok) {
			Out("R " + job.id + " st=ERR why=cache_read");
			return;
		}
	}
	const auto& key   = file.key;
	const auto& entry = file.entry;
	if (job.permutation >= entry.permutations.size()) {
		Out("R " + job.id + " st=ERR why=permutation");
		return;
	}
	const auto& stored = entry.permutations[job.permutation];
	std::vector<uint8_t> gcn_bytes;
	if (!ReadAll(job.gcn, gcn_bytes) || gcn_bytes.size() % 4u != 0) {
		Out("R " + job.id + " st=ERR why=gcn_read");
		return;
	}
	std::vector<uint32_t> code(gcn_bytes.size() / 4u);
	std::memcpy(code.data(), gcn_bytes.data(), gcn_bytes.size());
	if (code.size() != key.code_size) {
		Out("R " + job.id + " st=ERR why=code_size have=" + std::to_string(code.size()) + " key=" +
		    std::to_string(key.code_size));
		return;
	}
	const auto stage = static_cast<ShaderType>(key.stage);
	const bool vertex_like = stage == ShaderType::Vertex || stage == ShaderType::Mesh;
	const bool pixel       = stage == ShaderType::Pixel;
	const bool compute     = stage == ShaderType::Compute;
	if (!vertex_like && !pixel && !compute) {
		Out("R " + job.id + " st=ERR why=stage");
		return;
	}
	ShaderVertexInputInfo  vertex {};
	ShaderPixelInputInfo   pixel_info {};
	ShaderComputeInputInfo compute_info {};
	std::vector<uint32_t>  state = key.static_state;
	if (job.corrupt == "stride" || job.corrupt == "format") {
		size_t base = 0;
		if (!vertex_like || !VertexResourceBase(state, base) || base + 13u > state.size()) {
			Out("R " + job.id + " st=ERR why=corrupt_target");
			return;
		}
		if (job.corrupt == "stride") {
			state[base + 4u] = (state[base + 4u] + 4u) & 0x3FFFu;
		} else {
			state[base + 10u] = state[base + 10u] == 13u ? 14u : 13u;
		}
	}
	std::string why;
	bool        input_ok = true;
	if (job.form == "K") {
		input_ok = vertex_like ? VertexFromKey(state, stage, vertex, why)
		           : pixel     ? PixelFromKey(state, pixel_info, why)
		                       : ComputeFromKey(state, compute_info, why);
	} else if (job.form == "A0" || job.form == "C") {
		std::vector<uint8_t> bytes;
		if (!ReadAll(job.input, bytes)) {
			Out("R " + job.id + " st=ERR why=input_read");
			return;
		}
		input_ok = vertex_like ? LoadInfo(bytes, vertex)
		           : pixel     ? LoadInfo(bytes, pixel_info)
		                       : LoadInfo(bytes, compute_info);
		if (!input_ok) {
			why = "input_size";
		} else if (job.form == "C" && vertex_like) {
			CanonVertex(vertex);
		}
	} else {
		Out("R " + job.id + " st=ERR why=form");
		return;
	}
	if (!input_ok) {
		Out("R " + job.id + " st=NOINPUT why=" + why);
		return;
	}
	// The options of ProgramCache::Compile (pipelineCache.cpp) for this stage.
	std::vector<uint32_t>   user_data(key.user_data_count, 0u);
	ShaderStageInputInfo    stage_input {};
	SR::CompileOptions      options;
	options.stage       = stage;
	options.shader_hash = key.hash;
	options.user_data   = user_data;
	options.dump_ir     = false;
	options.early_dump  = false;
	if (vertex_like) {
		stage_input.vertex     = &vertex;
		options.dump_label     = stage == ShaderType::Mesh ? "ShaderRecompiler MS" : "ShaderRecompiler VS";
		options.user_data_base = 8;
		if (stage == ShaderType::Mesh) {
			options.user_data_base = 0;
			options.wave_size      = vertex.mesh.wave_size;
		} else {
			options.detect_wave_size = true;
		}
	} else if (pixel) {
		stage_input.pixel        = &pixel_info;
		options.dump_label       = "ShaderRecompiler PS";
		options.wave_size        = pixel_info.wave_size;
		options.detect_wave_size = true;
	} else {
		stage_input.compute = &compute_info;
		options.dump_label  = "ShaderRecompiler CS";
		options.wave_size   = compute_info.wave_size;
	}
	options.input_info = stage_input;
	Out("P " + job.id + " T");
	auto translated = SR::TranslateProgram(std::span<const uint32_t> {code}, options);
	const auto new_ids    = Identities(translated.program.info);
	const auto stored_ids = Identities(entry.plan.info);
	const bool plan_same  = new_ids == stored_ids;
	SR::IR::ResourceSpecialization specialization;
	std::string map_state = "stored";
	if (job.arm == "B") {
		bool identity_order = true;
		if (!MapSpecialization(entry.plan.info, translated.program.info, stored.specialization, specialization,
		                       identity_order, why)) {
			Out("R " + job.id + " st=SHAPE why=" + why);
			return;
		}
		map_state = identity_order ? "identity" : "reordered";
	} else {
		specialization = stored.specialization;
	}
	std::string f19_line = "-";
	if (job.f19 != "-") {
#ifdef KYTY_S16D_HAVE_F19
		// The stand of KYTY_RECOMPILE_F19_FORMAT (tests/shaderCfgTests.cpp, F14e): every stored manual comparison image
		// gets its flag again from the =1 rule for the GIVEN format, then the indirect-table merge of the =1 branch.
		if (!SR::IR::FixF19Enabled()) {
			Out("R " + job.id + " st=ERR why=f19_disabled");
			return;
		}
		Prospero::BufferFormat format = Prospero::BufferFormat::kInvalid;
		if (job.f19 == "k16UNorm") {
			format = Prospero::BufferFormat::k16UNorm;
		} else if (job.f19 == "k8UNorm") {
			format = Prospero::BufferFormat::k8UNorm;
		} else {
			Out("R " + job.id + " st=ERR why=f19_format");
			return;
		}
		uint32_t to_native   = 0;
		uint32_t kept_manual = 0;
		for (auto& image: specialization.images) {
			if (!image.manual_depth_compare) {
				continue;
			}
			image.manual_depth_compare = SR::IR::FixF19ManualDepthCompare(format, false);
			(image.manual_depth_compare ? kept_manual : to_native)++;
		}
		SR::IR::FixF19MergeIndirectTables(specialization.images);
		f19_line = "[f19]_stand_format=" + std::to_string(static_cast<uint32_t>(format)) +
		           "_manual_to_native=" + std::to_string(to_native) + "_kept_manual=" + std::to_string(kept_manual);
#else
		Out("R " + job.id + " st=ERR why=f19_unbuilt");
		return;
#endif
	}
	uint32_t indirect = 0;
	for (const auto& image: stored.specialization.images) {
		if (image.indirect_root != SR::IR::ImageResource::NoIndirectImage) {
			indirect++;
		}
	}
	const uint32_t start = job.start_stored ? stored.program.bindings.push_data_start_dword : job.start;
	Out("P " + job.id + " E");
	auto compiled = SR::CompileProgram(std::move(translated), options, specialization, start);
	auto spirv    = std::move(compiled.spirv);
	if (job.corrupt == "spirv" && spirv.size() > 8u) {
		spirv[spirv.size() / 2u] ^= 0x1u;
	}
	const bool equal = spirv == stored.spirv;
	Out("P " + job.id + " V");
	std::string message;
	const bool  valid = Validate(spirv, message);
	const auto& layout = compiled.program.bindings;
	const auto& stored_layout = stored.program.bindings;
	std::string line = "R " + job.id + " st=OK eq=" + (equal ? "1" : "0") + " spv=" +
	                   Hex64(XXH3_64bits(spirv.data(), spirv.size() * sizeof(uint32_t))) +
	                   " words=" + std::to_string(spirv.size()) + " stored_words=" + std::to_string(stored.spirv.size()) +
	                   " start_arg=" + std::to_string(start) + " start=" + std::to_string(layout.push_data_start_dword) +
	                   " dd=" + std::to_string(layout.ShaderDataDwords()) +
	                   " stored_start=" + std::to_string(stored_layout.push_data_start_dword) +
	                   " stored_dd=" + std::to_string(stored_layout.ShaderDataDwords()) +
	                   " plan=" + (plan_same ? "same" : "diff") + " map=" + map_state +
	                   " val=" + (valid ? "1" : "0") + " ind=" + std::to_string(indirect) + " f19=" + f19_line;
	if (!valid) {
		line += " val_msg=" + Clean(message);
	}
	Out(line);
}

int Main(const char* jobs_path, const char* out_path) {
	g_out = std::fopen(out_path, "ab");
	if (g_out == nullptr) {
		std::fprintf(stderr, "s16d: cannot open %s\n", out_path);
		return 1;
	}
	// The device state of this machine (the catalogue signature :robust:ftz:cbank): robustBufferAccess2, fp32
	// denormals neither controllable (flush assumed), uniformBufferStandardLayout + robustBufferAccess2 (const bank).
	SR::Spirv::Emitter::SetRobustBufferLoads(true);
	SR::Spirv::Emitter::SetDenormFlushToZero(false, false);
	SR::IR::SetConstBankSupported(true);
	{
		const Libs::Graphics::ShaderTranslationCache cache("PPSA21564");
		std::string signature = cache.Signature();
		while (!signature.empty() && (signature.back() == 10 || signature.back() == 13)) {
			signature.pop_back();
		}
		Out("S signature=" + signature + " enabled=" + (cache.Enabled() ? "1" : "0"));
	}
	Out("S layout=" + std::to_string(sizeof(ShaderVertexInputInfo)) + ":" + std::to_string(sizeof(ShaderPixelInputInfo)) +
	    ":" + std::to_string(sizeof(ShaderComputeInputInfo)));
	Out(std::string("S effective robust=") + (SR::Spirv::Emitter::RobustBufferLoads() ? "1" : "0") +
	    " ftz=" + (SR::Spirv::Emitter::DenormFlushToZero() ? "1" : "0") +
	    " ftzd=" + (SR::Spirv::Emitter::DenormFlushToZeroDeclared() ? "1" : "0") +
	    " cbank=" + (SR::IR::ConstBankEnabled() ? "1" : "0") +
	    " cbank_cs=" + (SR::IR::ConstBankForStage(ShaderType::Compute) ? "1" : "0") +
	    " vec_const_static_class=" + (SR::IR::VectorConstStaticAlignmentClass() ? "1" : "0") +
	    " cbank_aligned_copy=" + (SR::IR::ConstBankAlignedCopy() ? "1" : "0") +
	    " bvh_cap_token=" + SR::Spirv::Emitter::BvhLoopCapSignatureToken() +
	    " bda_lean=" + (SR::Spirv::Emitter::BdaLeanEnabled() ? "1" : "0")
#ifdef KYTY_S16D_HAVE_F19
	    + " fix_f19=" + (SR::IR::FixF19Enabled() ? "1" : "0")
#endif
	);
	// Item 516(v)(6), RC3(g): the value of every knob read once per process (names from the driver, taken from the
	// getenv calls of the signature set and of pipelineCache.cpp of the tree), as the environment holds it.
	if (const char* knobs = std::getenv("KYTY_S16D_KNOBS"); knobs != nullptr) {
		std::vector<uint8_t> bytes;
		if (ReadAll(knobs, bytes)) {
			std::istringstream in(std::string(bytes.begin(), bytes.end()));
			std::string        name;
			while (in >> name) {
				const char* value = std::getenv(name.c_str());
				Out("K " + name + "=" + (value == nullptr ? std::string("<unset>") : Clean(value)));
			}
		}
	}
	std::vector<uint8_t> jobs_bytes;
	if (!ReadAll(jobs_path, jobs_bytes)) {
		Out("S error=jobs_read");
		return 1;
	}
	std::istringstream jobs(std::string(jobs_bytes.begin(), jobs_bytes.end()));
	std::string        line;
	std::map<std::string, CachedFile> files;
	uint32_t           done = 0;
	while (std::getline(jobs, line)) {
		if (line.empty() || line[0] == '#') {
			continue;
		}
		ProbeJob job;
		if (!ParseJob(line, job)) {
			Out("S error=parse " + Clean(line));
			continue;
		}
		Out("B " + job.id);
		RunJob(job, files);
		done++;
	}
	Out("S done=" + std::to_string(done));
	std::fclose(g_out);
	return 0;
}

} // namespace Libs::Graphics::S16dProbe
