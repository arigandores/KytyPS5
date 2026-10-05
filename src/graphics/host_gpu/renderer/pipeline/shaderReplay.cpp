#include "graphics/host_gpu/renderer/pipeline/shaderReplay.h"

#include "common/file.h"
#include "common/logging/log.h"
#include "loader/gamePatchFile.h"

#include <algorithm>
#include <atomic>
#include <bit>
#include <chrono>
#include <cinttypes>
#include <condition_variable>
#include <cstdlib>
#include <cstring>
#include <fmt/format.h>
#include <fstream>
#include <map>
#include <mutex>
#include <string_view>
#include <thread>
#include <unordered_set>
#include <xxhash.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#endif

#include "SDL.h"
#include "SDL_events.h"

namespace Libs::Graphics::ShaderReplay {

namespace IR = ShaderRecompiler::IR;

int Mode() {
	// Read once per process. Only the exact values "1", "2", "3" turn it on; unset, "", "0" or anything else is 0.
	static const int mode = [] {
		const char* value = std::getenv("KYTY_S_REPLAY");
		if (value == nullptr || value[0] < '1' || value[0] > '3' || value[1] != '\0') {
			return 0;
		}
		return value[0] - '0';
	}();
	return mode;
}

bool CaptureOn() {
	return Mode() == 1 || Mode() == 2;
}

bool RebuildOn() {
	return Mode() == 1 || Mode() == 3;
}

Stand TestStand() {
	static const Stand stand = [] {
		const char* value = std::getenv("KYTY_S_REPLAY_TEST");
		if (value == nullptr) {
			return Stand::None;
		}
		const std::string_view text(value);
		if (text == "canon") {
			return Stand::Canon;
		}
		if (text == "spec") {
			return Stand::Spec;
		}
		if (text == "addr") {
			return Stand::Addr;
		}
		if (text == "stop") {
			return Stand::Stop;
		}
		if (text == "corrupt") {
			return Stand::Corrupt;
		}
		return Stand::None;
	}();
	return stand;
}

const char* StandName(Stand stand) {
	switch (stand) {
		case Stand::Canon: return "canon";
		case Stand::Spec: return "spec";
		case Stand::Addr: return "addr";
		case Stand::Stop: return "stop";
		case Stand::Corrupt: return "corrupt";
		default: return "none";
	}
}

void StandRequestClose() {
	// KYTY_S_REPLAY_TEST=stop: the same event a click on the close button of the window produces; the preparation loop
	// (window.cpp, WindowPrepareShaders) returns and the shutdown path stores m_precache_stop.
	SDL_Event event {};
	event.type = SDL_QUIT;
	SDL_PushEvent(&event);
}

std::string LayoutLine() {
	return fmt::format(
	    "ShaderReplayLayout: word={} word.value={} word.role={} word.flags={} file={} file.magic={} file.format={} "
	    "file.compat_size={} body={} body.generation={} body.body_checksum={} body.sources={} body.specs={} "
	    "body.pipes={} src={} src.src_id={} src.hash={} src.stage={} src.user_data_count={} src.code_size={} "
	    "src.static_words={} src.code_words={} src.back_words={} src.sha256={} spec={} spec.spec_id={} spec.src_id={} "
	    "spec.live_spec_hash={} spec.stored_start={} spec.user_words={} spec.reads={} spec.words={} pipe={} "
	    "pipe.pipe_id={} pipe.spec={} pipe.kind={} pipe.pod_size={} versions={}:{}:{}:{}",
	    sizeof(Word), offsetof(Word, value), offsetof(Word, role), offsetof(Word, flags), sizeof(FileHeader),
	    offsetof(FileHeader, magic), offsetof(FileHeader, format), offsetof(FileHeader, compat_size), sizeof(BodyHeader),
	    offsetof(BodyHeader, generation), offsetof(BodyHeader, body_checksum), offsetof(BodyHeader, sources),
	    offsetof(BodyHeader, specs), offsetof(BodyHeader, pipes), sizeof(SourceHeader), offsetof(SourceHeader, src_id),
	    offsetof(SourceHeader, hash), offsetof(SourceHeader, stage), offsetof(SourceHeader, user_data_count),
	    offsetof(SourceHeader, code_size), offsetof(SourceHeader, static_words), offsetof(SourceHeader, code_words),
	    offsetof(SourceHeader, back_words), offsetof(SourceHeader, sha256), sizeof(SpecHeader),
	    offsetof(SpecHeader, spec_id), offsetof(SpecHeader, src_id), offsetof(SpecHeader, live_spec_hash),
	    offsetof(SpecHeader, stored_start), offsetof(SpecHeader, user_words), offsetof(SpecHeader, reads),
	    offsetof(SpecHeader, words), sizeof(PipeHeader), offsetof(PipeHeader, pipe_id), offsetof(PipeHeader, spec),
	    offsetof(PipeHeader, kind), offsetof(PipeHeader, pod_size), FormatVersion, StaticKeyVersion, CanonVersion,
	    ReplayInputVersion);
}

namespace {

bool Lo4(uint32_t value) {
	return (value & ~0xFu) == 0x100u;
}

} // namespace

bool WordCanonical(const Word& word) {
	const uint32_t v = word.value;
	switch (word.role) {
		case ROLE_KEEP: return true;
		case ROLE_INERT:
		case ROLE_V_LO: return v == 0 || Lo4(v);
		case ROLE_PTR_LO: return Lo4(v);
		case ROLE_PTR_HI:
		case ROLE_V_HI: return (v & 0xFFFFu) == 0;
		case ROLE_T_LO: return v == 0 || v == 1;
		case ROLE_T_HI: return (v & 0xFFu) == 0;
		case ROLE_T_META6: return (v & 0xFF000000u) == 0;
		case ROLE_T_META7: return v == 0;
		default: return false;
	}
}

uint64_t SourceId(uint32_t stage, uint64_t hash, uint32_t user_data_count, uint32_t code_size,
                  std::span<const uint32_t> static_state) {
	std::vector<uint32_t> words;
	words.reserve(6 + static_state.size());
	words.push_back(stage);
	words.push_back(static_cast<uint32_t>(hash));
	words.push_back(static_cast<uint32_t>(hash >> 32u));
	words.push_back(user_data_count);
	words.push_back(code_size);
	words.push_back(static_cast<uint32_t>(static_state.size()));
	words.insert(words.end(), static_state.begin(), static_state.end());
	return XXH3_64bits_withSeed(words.data(), words.size() * sizeof(uint32_t), StaticKeyVersion);
}

namespace {

void SpecWords(const IR::ResourceSpecialization& specialization, std::vector<uint32_t>& words) {
	words.push_back(static_cast<uint32_t>(specialization.buffers.size()));
	for (const auto& b: specialization.buffers) {
		words.push_back(b.packed_stride);
		words.push_back(static_cast<uint32_t>(b.descriptor_format));
		words.push_back(b.descriptor_swizzle);
	}
	words.push_back(static_cast<uint32_t>(specialization.images.size()));
	for (const auto& i: specialization.images) {
		words.push_back(static_cast<uint32_t>(i.numeric_class));
		words.push_back(static_cast<uint32_t>(i.dimension));
		words.push_back(i.mip_count);
		words.push_back(static_cast<uint32_t>(i.conversion_format));
		words.push_back(i.shader_swizzle);
		words.push_back(i.indirect_root);
		words.push_back(i.indirect_mapping_offset);
		words.push_back(i.indirect_search_iterations);
		words.push_back(i.cube ? 1u : 0u);
		words.push_back(i.manual_depth_compare ? 1u : 0u);
		words.push_back(i.depth_compare_op);
		words.push_back(i.fmask ? 1u : 0u);
	}
}

} // namespace

uint64_t SpecializationHash(const IR::ResourceSpecialization& specialization) {
	std::vector<uint32_t> words;
	SpecWords(specialization, words);
	return XXH3_64bits(words.data(), words.size() * sizeof(uint32_t));
}

uint64_t SpecId(uint64_t src_id, const IR::ResourceSpecialization& specialization, uint32_t push_start) {
	std::vector<uint32_t> words;
	words.push_back(static_cast<uint32_t>(src_id));
	words.push_back(static_cast<uint32_t>(src_id >> 32u));
	words.push_back(push_start);
	SpecWords(specialization, words);
	return XXH3_64bits_withSeed(words.data(), words.size() * sizeof(uint32_t), CanonVersion);
}

// --- Form K: the stage input from the static key (port of tests/S16dProbe.inc, 1d8d9aa6) -----------------------------

bool VertexFromKey(std::span<const uint32_t> s, ShaderType stage, ShaderVertexInputInfo& info, std::string& why) {
	if (s.size() < 9) {
		why = "short";
		return false;
	}
	size_t i                 = 0;
	info.fetch_embedded      = s[i++] != 0;
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

bool PixelFromKey(std::span<const uint32_t> s, ShaderPixelInputInfo& pixel, std::string& why) {
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

bool ComputeFromKey(std::span<const uint32_t> s, ShaderComputeInputInfo& compute, std::string& why) {
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

// --- Recording and replaying a read path ------------------------------------------------------------------------------

namespace {

bool RecordRead(Recorder* recorder, IR::SrtMemoryReader reader, uint64_t address, uint32_t* value, bool clean) {
	const bool ok    = reader != nullptr && value != nullptr && reader(recorder->inner->userdata, address, value);
	auto&      trace = *recorder->trace;
	if (trace.reads.size() >= MaxPathWords) {
		trace.overflow = true;
	} else {
		trace.reads.push_back({address, ok ? *value : 0u, static_cast<uint8_t>(clean ? 1 : 0),
		                       static_cast<uint8_t>(ok ? 1 : 0)});
	}
	return ok;
}

bool RecordLive(void* userdata, uint64_t address, uint32_t* value) {
	auto* recorder = static_cast<Recorder*>(userdata);
	return RecordRead(recorder, recorder->inner->read_memory, address, value, false);
}

bool RecordClean(void* userdata, uint64_t address, uint32_t* value) {
	auto* recorder = static_cast<Recorder*>(userdata);
	return RecordRead(recorder, recorder->inner->read_specialization_memory, address, value, true);
}

bool Answer(Replayer* replayer, uint64_t address, uint32_t* value, bool clean) {
	if (replayer->requested != nullptr) {
		replayer->requested->push_back(address);
	}
	if (value == nullptr || replayer->next >= replayer->reads.size()) {
		replayer->diverged = true;
		return false;
	}
	const auto& word = replayer->reads[replayer->next++];
	if (((word.flags & WORD_CLEAN) != 0) != clean) {
		replayer->diverged = true;
		return false;
	}
	*value = word.value;
	return (word.flags & WORD_OK) != 0;
}

bool ReplayLive(void* userdata, uint64_t address, uint32_t* value) {
	return Answer(static_cast<Replayer*>(userdata), address, value, false);
}

bool ReplayClean(void* userdata, uint64_t address, uint32_t* value) {
	return Answer(static_cast<Replayer*>(userdata), address, value, true);
}

} // namespace

IR::SrtRuntime Recorder::Runtime() {
	trace->shader_base = inner->shader_base;
	trace->user_data.assign(inner->user_data.begin(), inner->user_data.end());
	return {
	    .user_data                  = inner->user_data,
	    .shader_base                = inner->shader_base,
	    .read_memory                = RecordLive,
	    .userdata                   = this,
	    .read_specialization_memory = RecordClean,
	};
}

Replayer::Replayer(std::span<const Word> words, size_t user_words) {
	if (words.size() >= 2) {
		shader_base = words[0].value | (static_cast<uint64_t>(words[1].value) << 32u);
	}
	const size_t user_begin = std::min<size_t>(2, words.size());
	const size_t user_end   = std::min(words.size(), user_begin + user_words);
	for (size_t i = user_begin; i < user_end; i++) {
		user_data.push_back(words[i].value);
	}
	reads.assign(words.begin() + static_cast<std::ptrdiff_t>(user_end), words.end());
}

IR::SrtRuntime Replayer::Runtime() {
	return {
	    .user_data                  = user_data,
	    .shader_base                = shader_base,
	    .read_memory                = ReplayLive,
	    .userdata                   = this,
	    .read_specialization_memory = ReplayClean,
	};
}

// --- Canonicalization ------------------------------------------------------------------------------------------------

namespace {

struct RunResult {
	bool                       ok       = false;
	bool                       complete = false;
	IR::ResourceSnapshot       snapshot;
	IR::ResourceSpecialization specialization;
	std::vector<uint64_t>      requested;
};

RunResult Run(const IR::ResourcePlan& plan, std::span<const Word> words, size_t user_words, bool want_requested) {
	RunResult result;
	Replayer  replayer(words, user_words);
	if (want_requested) {
		replayer.requested = &result.requested;
	}
	result.ok       = IR::MaterializeResources(plan, replayer.Runtime(), result.snapshot, result.specialization);
	result.complete = replayer.Complete();
	return result;
}

// Kinds of the descriptor arrays of a snapshot.
constexpr int KindBuffer  = 0;
constexpr int KindImage   = 1;
constexpr int KindSampler = 2;

Role DescriptorRole(int kind, uint32_t dword) {
	if (kind == KindBuffer) {
		return dword == 0 ? ROLE_V_LO : dword == 1 ? ROLE_V_HI : ROLE_KEEP;
	}
	if (kind == KindImage) {
		switch (dword) {
			case 0: return ROLE_T_LO;
			case 1: return ROLE_T_HI;
			case 6: return ROLE_T_META6;
			case 7: return ROLE_T_META7;
			default: return ROLE_KEEP;
		}
	}
	return ROLE_KEEP;
}

struct Flow {
	int      kind  = -1;
	uint32_t index = 0;
	uint32_t dword = 0;
};

// A word that changed one descriptor dword by exactly the perturbation flows into it (a copy); any other descriptor
// change (another value, a zero-filled descriptor, a size change) marks the word as one the result depends on.
void CompareDescriptors(const std::vector<IR::DescriptorValue>& base, const std::vector<IR::DescriptorValue>& now,
                        int kind, uint32_t delta, Flow& flow, bool& other) {
	if (base.size() != now.size()) {
		other = true;
		return;
	}
	for (uint32_t i = 0; i < base.size(); i++) {
		if (base[i].dword_count != now[i].dword_count) {
			other = true;
			continue;
		}
		for (uint32_t d = 0; d < base[i].dwords.size(); d++) {
			const uint32_t x = base[i].dwords[d] ^ now[i].dwords[d];
			if (x == 0) {
				continue;
			}
			if (x == delta && kind != KindSampler) {
				const Role role = DescriptorRole(kind, d);
				if (flow.kind < 0 || (role != ROLE_KEEP && DescriptorRole(flow.kind, flow.dword) == ROLE_KEEP)) {
					flow = {kind, i, d};
				}
			} else {
				other = true;
			}
		}
	}
}

uint32_t Canonical(Role role, uint32_t value, const IR::DescriptorValue* descriptor) {
	switch (role) {
		case ROLE_INERT: return value == 0 ? 0u : (0x100u | (value & 0xFu));
		case ROLE_PTR_LO: return 0x100u | (value & 0xFu);
		case ROLE_PTR_HI:
		case ROLE_V_HI: return value & 0xFFFF0000u;
		case ROLE_V_LO: {
			const uint64_t base = descriptor != nullptr
			                          ? (descriptor->dwords[0] | (static_cast<uint64_t>(descriptor->dwords[1] & 0xFFFFu) << 32u))
			                          : value;
			return base == 0 ? 0u : (0x100u | (value & 0xFu));
		}
		case ROLE_T_LO: {
			const bool null = descriptor != nullptr
			                      ? descriptor->dwords[0] == 0 && (descriptor->dwords[1] & 0xFFu) == 0
			                      : value == 0;
			return null ? 0u : 1u;
		}
		case ROLE_T_HI: return value & 0xFFFFFF00u;
		case ROLE_T_META6: return value & 0x00FFFFFFu;
		case ROLE_T_META7: return 0u;
		default: return value;
	}
}

const IR::DescriptorValue* DescriptorOf(const IR::ResourceSnapshot& snapshot, const Flow& flow) {
	const auto& array = flow.kind == KindBuffer ? snapshot.buffers : flow.kind == KindImage ? snapshot.images
	                                                                                        : snapshot.samplers;
	return flow.index < array.size() ? &array[flow.index] : nullptr;
}

std::atomic<bool> g_canon_stand_done {false};

} // namespace

bool Canonicalize(const IR::ResourcePlan& plan, const Trace& trace, const IR::ResourceSpecialization& live,
                  std::vector<Word>& words, size_t& user_words, std::string& why, bool canon_stand) {
	user_words = trace.user_data.size();
	if (trace.overflow || 2 + trace.user_data.size() + trace.reads.size() > MaxPathWords) {
		why = "big";
		return false;
	}
	std::vector<Word> raw;
	raw.reserve(2 + trace.user_data.size() + trace.reads.size());
	raw.push_back({static_cast<uint32_t>(trace.shader_base), ROLE_KEEP, WORD_BASE | WORD_OK});
	raw.push_back({static_cast<uint32_t>(trace.shader_base >> 32u), ROLE_KEEP, WORD_BASE | WORD_OK});
	for (const auto value: trace.user_data) {
		raw.push_back({value, ROLE_KEEP, WORD_USER | WORD_OK});
	}
	for (const auto& read: trace.reads) {
		raw.push_back({read.value, ROLE_KEEP,
		               static_cast<uint8_t>((read.clean != 0 ? WORD_CLEAN : 0) | (read.ok != 0 ? WORD_OK : 0))});
	}
	// The raw path must give the live specialization: the walk is a function of the plan and the words it read.
	const auto base = Run(plan, raw, user_words, true);
	if (!base.ok || !base.complete || !(base.specialization == live)) {
		why = "base";
		return false;
	}
	// Role of every word: two perturbations (bit 8, bit 0), each replayed in full.
	std::vector<Word> canonical = raw;
	for (size_t i = 0; i < raw.size(); i++) {
		if ((raw[i].flags & WORD_OK) == 0) {
			continue; // a failed read answers 0 and fails again; nothing to keep
		}
		bool sensitive = false;
		bool ptr_lo    = false;
		bool ptr_hi    = false;
		Flow flow;
		for (const uint32_t delta: {0x100u, 0x1u}) {
			auto perturbed = raw;
			perturbed[i].value ^= delta;
			const auto now = Run(plan, perturbed, user_words, true);
			if (!now.ok || !now.complete) {
				sensitive = true;
				continue;
			}
			if (!(now.specialization == live)) {
				sensitive = true;
			}
			if (now.requested.size() != base.requested.size()) {
				sensitive = true;
			} else {
				for (size_t j = 0; j < base.requested.size(); j++) {
					if (now.requested[j] == base.requested[j]) {
						continue;
					}
					const uint64_t up   = now.requested[j] - base.requested[j];
					const uint64_t down = base.requested[j] - now.requested[j];
					const uint64_t step = std::min(up, down);
					if (step == delta) {
						ptr_lo = true;
					} else if (step == (static_cast<uint64_t>(delta) << 32u)) {
						ptr_hi = true;
					} else {
						sensitive = true;
					}
				}
			}
			bool other = false;
			CompareDescriptors(base.snapshot.buffers, now.snapshot.buffers, KindBuffer, delta, flow, other);
			CompareDescriptors(base.snapshot.images, now.snapshot.images, KindImage, delta, flow, other);
			CompareDescriptors(base.snapshot.samplers, now.snapshot.samplers, KindSampler, delta, flow, other);
			if (other) {
				sensitive = true;
			}
		}
		Role role = ROLE_KEEP;
		const IR::DescriptorValue* descriptor = nullptr;
		if (flow.kind >= 0) {
			role       = DescriptorRole(flow.kind, flow.dword);
			descriptor = DescriptorOf(base.snapshot, flow);
		} else if (ptr_lo != ptr_hi) {
			role = ptr_lo ? ROLE_PTR_LO : ROLE_PTR_HI;
		} else if (!sensitive && !ptr_lo) {
			role = ROLE_INERT;
		}
		canonical[i].role  = role;
		canonical[i].value = Canonical(role, raw[i].value, descriptor);
	}
	// KYTY_S_REPLAY_TEST=canon: one canonical T# base field spoiled (a non-null T# made null) in one record - the
	// self-check below must reject it (canon_mismatch > 0, member K3).
	if (canon_stand && !g_canon_stand_done.load()) {
		for (auto& word: canonical) {
			if (word.role == ROLE_T_LO && word.value == 1u) {
				word.value = 0u;
				g_canon_stand_done.store(true);
				LOGF("ShaderReplay: stand canon applied hash=0x%016" PRIx64 "\n", plan.shader_hash);
				break;
			}
		}
	}
	// Self-check (S16a section 2.2, member K3): the canonical path gives the live specialization.
	const auto check = Run(plan, canonical, user_words, false);
	if (!check.ok || !check.complete || !(check.specialization == live)) {
		// Diagnosis for the log (only on a failure): the words whose raw value alone makes the check pass.
		why = fmt::format("self ok={} complete={}", check.ok ? 1 : 0, check.complete ? 1 : 0);
		uint32_t named = 0;
		for (size_t i = 0; i < canonical.size() && named < 4; i++) {
			if (canonical[i].value == raw[i].value) {
				continue;
			}
			auto partial     = canonical;
			partial[i].value = raw[i].value;
			const auto again = Run(plan, partial, user_words, false);
			if (again.ok && again.complete && again.specialization == live) {
				why += fmt::format(" culprit={}:role{}:{:08x}->{:08x}", i, canonical[i].role, raw[i].value,
				                   canonical[i].value);
				named++;
			}
		}
		return false;
	}
	// No word kept as read may carry a guest address the walk used (lower 32 bits of a read address or of a non-null
	// descriptor base); small values are not compared.
	std::unordered_set<uint32_t> addresses;
	for (const auto address: base.requested) {
		addresses.insert(static_cast<uint32_t>(address));
	}
	for (const auto& d: base.snapshot.buffers) {
		if (d.dwords[0] != 0) {
			addresses.insert(d.dwords[0]);
		}
	}
	for (const auto& d: base.snapshot.images) {
		if (d.dwords[0] != 0) {
			addresses.insert(d.dwords[0]);
		}
		if (d.dword_count == 8u && d.dwords[7] != 0) {
			addresses.insert(d.dwords[7]);
		}
	}
	for (const auto& word: canonical) {
		if (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value)) {
			why = "residual";
			return false;
		}
	}
	words = std::move(canonical);
	return true;
}

bool Specialize(const IR::ResourcePlan& plan, const Catalogue::Spec& spec, IR::ResourceSpecialization& specialization) {
	Replayer             replayer(spec.words, spec.header.user_words);
	IR::ResourceSnapshot snapshot;
	const bool           ok = IR::MaterializeResources(plan, replayer.Runtime(), snapshot, specialization);
	return ok && replayer.Complete();
}

uint32_t SamePcGroups(const IR::ShaderInfo& info) {
	std::map<std::pair<uint32_t, uint32_t>, uint32_t> groups;
	for (const auto& b: info.buffers) {
		groups[{0u, b.first_use_pc}]++;
	}
	for (const auto& image: info.images) {
		groups[{1u, image.first_use_pc}]++;
	}
	return static_cast<uint32_t>(std::ranges::count_if(groups, [](const auto& g) { return g.second >= 2u; }));
}

// --- Catalogue and its files -----------------------------------------------------------------------------------------

const Catalogue::Source* Catalogue::FindSource(uint64_t id) const {
	const auto it = source_index.find(id);
	return it == source_index.end() ? nullptr : &sources[it->second];
}

const Catalogue::Spec* Catalogue::FindSpec(uint64_t id) const {
	const auto it = spec_index.find(id);
	return it == spec_index.end() ? nullptr : &specs[it->second];
}

void Catalogue::Index() {
	source_index.clear();
	spec_index.clear();
	pipe_index.clear();
	for (uint32_t i = 0; i < sources.size(); i++) {
		source_index[sources[i].header.src_id] = i;
	}
	for (uint32_t i = 0; i < specs.size(); i++) {
		spec_index[specs[i].header.spec_id] = i;
	}
	for (uint32_t i = 0; i < pipes.size(); i++) {
		pipe_index[pipes[i].header.pipe_id] = i;
	}
}

Store::Store(std::filesystem::path directory, std::string compat)
    : m_directory(std::move(directory)), m_compat(std::move(compat)) {}

namespace {

template <typename T>
void Append(std::vector<uint8_t>& out, const T& value) {
	static_assert(std::is_trivially_copyable_v<T>);
	const auto* bytes = reinterpret_cast<const uint8_t*>(&value);
	out.insert(out.end(), bytes, bytes + sizeof(T));
}

void AppendBytes(std::vector<uint8_t>& out, const void* data, size_t size) {
	const auto* bytes = static_cast<const uint8_t*>(data);
	out.insert(out.end(), bytes, bytes + size);
}

class Reader {
public:
	Reader(const uint8_t* data, size_t size): m_data(data), m_size(size) {}
	template <typename T>
	bool Get(T& value) {
		return Bytes(&value, sizeof(T));
	}
	bool Bytes(void* out, size_t size) {
		if (size > m_size - m_pos) {
			return false;
		}
		std::memcpy(out, m_data + m_pos, size);
		m_pos += size;
		return true;
	}
	template <typename T>
	bool Vector(std::vector<T>& out, size_t count, size_t max) {
		if (count > max || count * sizeof(T) > m_size - m_pos) {
			return false;
		}
		out.resize(count);
		return Bytes(out.data(), count * sizeof(T));
	}
	[[nodiscard]] size_t Pos() const { return m_pos; }
	[[nodiscard]] bool   AtEnd() const { return m_pos == m_size; }

private:
	const uint8_t* m_data;
	size_t         m_size;
	size_t         m_pos = 0;
};

bool ReadFileBytes(const std::filesystem::path& path, std::vector<uint8_t>& data) {
	std::ifstream file(path, std::ios::binary | std::ios::ate);
	if (!file) {
		return false;
	}
	const auto size = file.tellg();
	if (size < 0 || size > (std::streamoff {1} << 30)) {
		return false;
	}
	data.resize(static_cast<size_t>(size));
	file.seekg(0);
	file.read(reinterpret_cast<char*>(data.data()), size);
	return static_cast<bool>(file);
}

bool WriteFileAtomic(const std::filesystem::path& path, const std::vector<uint8_t>& data) {
	auto temp = path;
	temp += ".tmp";
	Common::File file;
	uint32_t     written = 0;
	if (file.Create(temp)) {
		file.Write(data.data(), static_cast<uint32_t>(data.size()), &written);
	}
	const bool flushed = !file.IsInvalid() && file.Flush();
	file.Close();
	return written == data.size() && flushed && Common::File::RenameFile(temp, path);
}

std::filesystem::path GenerationPath(const std::filesystem::path& directory, uint64_t generation) {
	return directory / fmt::format("replay.{}.bin", generation);
}

} // namespace

std::vector<uint8_t> Store::Serialize(const Catalogue& catalogue, const std::string& compat, uint64_t generation) {
	std::vector<uint8_t> body;
	for (const auto& s: catalogue.sources) {
		Append(body, s.header);
		AppendBytes(body, s.static_state.data(), s.static_state.size() * sizeof(uint32_t));
		AppendBytes(body, s.code.data(), s.code.size() * sizeof(uint32_t));
		AppendBytes(body, s.back.data(), s.back.size() * sizeof(uint32_t));
	}
	for (const auto& s: catalogue.specs) {
		Append(body, s.header);
		AppendBytes(body, s.words.data(), s.words.size() * sizeof(Word));
	}
	for (const auto& p: catalogue.pipes) {
		Append(body, p.header);
		AppendBytes(body, p.pod.data(), p.pod.size());
	}
	FileHeader file_header;
	file_header.compat_size = static_cast<uint32_t>(compat.size());
	BodyHeader body_header;
	body_header.generation    = generation;
	body_header.body_checksum = XXH3_64bits(body.data(), body.size());
	body_header.sources       = static_cast<uint32_t>(catalogue.sources.size());
	body_header.specs         = static_cast<uint32_t>(catalogue.specs.size());
	body_header.pipes         = static_cast<uint32_t>(catalogue.pipes.size());
	std::vector<uint8_t> out;
	out.reserve(sizeof(FileHeader) + compat.size() + sizeof(BodyHeader) + body.size());
	Append(out, file_header);
	AppendBytes(out, compat.data(), compat.size());
	Append(out, body_header);
	out.insert(out.end(), body.begin(), body.end());
	return out;
}

bool Store::Parse(const std::vector<uint8_t>& data, const std::string& compat, Catalogue& catalogue,
                  uint64_t& generation, std::string& state) {
	Reader     r(data.data(), data.size());
	FileHeader file_header;
	if (!r.Get(file_header) || std::memcmp(file_header.magic, FileHeader {}.magic, sizeof(file_header.magic)) != 0 ||
	    file_header.format != FormatVersion || file_header.compat_size > 4096u) {
		state = "mismatch";
		return false;
	}
	std::string stored(file_header.compat_size, '\0');
	BodyHeader  body_header;
	if (!r.Bytes(stored.data(), stored.size()) || !r.Get(body_header)) {
		state = "corrupt";
		return false;
	}
	const size_t body_begin = r.Pos();
	if (XXH3_64bits(data.data() + body_begin, data.size() - body_begin) != body_header.body_checksum) {
		state = "corrupt";
		return false;
	}
	Catalogue next;
	for (uint32_t i = 0; i < body_header.sources; i++) {
		Catalogue::Source s;
		if (!r.Get(s.header) || !r.Vector(s.static_state, s.header.static_words, 4096u) ||
		    !r.Vector(s.code, s.header.code_words, size_t {1} << 22u) ||
		    !r.Vector(s.back, s.header.back_words, size_t {1} << 22u)) {
			state = "corrupt";
			return false;
		}
		next.sources.push_back(std::move(s));
	}
	for (uint32_t i = 0; i < body_header.specs; i++) {
		Catalogue::Spec s;
		if (!r.Get(s.header) || s.header.words != 2u + s.header.user_words + s.header.reads ||
		    !r.Vector(s.words, s.header.words, MaxPathWords)) {
			state = "corrupt";
			return false;
		}
		next.specs.push_back(std::move(s));
	}
	for (uint32_t i = 0; i < body_header.pipes; i++) {
		Catalogue::Pipe p;
		if (!r.Get(p.header) || !r.Vector(p.pod, p.header.pod_size, 4096u)) {
			state = "corrupt";
			return false;
		}
		next.pipes.push_back(std::move(p));
	}
	if (!r.AtEnd()) {
		state = "corrupt";
		return false;
	}
	next.Index();
	catalogue  = std::move(next);
	generation = body_header.generation;
	state      = stored == compat ? "ok" : "mismatch";
	return true;
}

bool Store::Load(Catalogue& catalogue, std::string& state, uint64_t& generation, uint64_t& corrupt_generation) {
	corrupt_generation = 0;
	generation         = 0;
	std::ifstream pointer(m_directory / "replay.cur");
	uint64_t      current = 0;
	if (!(pointer >> current) || current == 0) {
		state = "absent";
		return false;
	}
	for (uint64_t g = current; g + 1 >= current && g >= 1; g--) {
		std::vector<uint8_t> data;
		if (!ReadFileBytes(GenerationPath(m_directory, g), data)) {
			state = "absent";
			if (g == current) {
				corrupt_generation = g;
				continue;
			}
			return false;
		}
		if (g == current && TestStand() == Stand::Corrupt && data.size() > sizeof(FileHeader) + sizeof(BodyHeader)) {
			// KYTY_S_REPLAY_TEST=corrupt (member K6): one byte of the current generation spoiled before the check.
			data[data.size() - 1] ^= 0xFFu;
			LOGF("ShaderReplay: stand corrupt applied generation=%" PRIu64 "\n", g);
		}
		if (Parse(data, m_compat, catalogue, generation, state)) {
			return state == "ok";
		}
		if (state != "corrupt") {
			return false;
		}
		corrupt_generation = g;
	}
	return false;
}

bool Store::Save(const Catalogue& catalogue, uint64_t generation, uint64_t& bytes) {
	if (!Common::File::CreateDirectories(m_directory)) {
		return false;
	}
	const auto data = Serialize(catalogue, m_compat, generation);
	if (!WriteFileAtomic(GenerationPath(m_directory, generation), data)) {
		return false;
	}
	const auto           text = fmt::format("{}\n", generation);
	std::vector<uint8_t> pointer(text.begin(), text.end());
	if (!WriteFileAtomic(m_directory / "replay.cur", pointer)) {
		return false;
	}
	if (generation >= 3) {
		const auto old = GenerationPath(m_directory, generation - 2);
		std::error_code ec;
		std::filesystem::remove(old, ec); // the generation before the previous one; a failure only leaves it
	}
	bytes = data.size();
	return true;
}

// --- The writer thread -------------------------------------------------------------------------------------------------

class Writer {
public:
	Writer(Store& store, Catalogue catalogue, uint64_t generation)
	    : m_store(store), m_catalogue(std::move(catalogue)), m_generation(generation) {
		m_catalogue.Index();
		m_last_save_ms = NowMs();
		m_thread       = std::thread([this] { Loop(); });
	}
	~Writer() { Stop(); }
	Writer(const Writer&)            = delete;
	Writer& operator=(const Writer&) = delete;

	struct Slot {
		std::unique_ptr<SourceItem> source;
		std::unique_ptr<SpecItem>   spec;
		std::unique_ptr<PipeItem>   pipe;
	};

	// Producer: the holder of PipelineCache::m_mutex (one at a time); never waits.
	void Push(Slot slot) {
		if (m_stop.load(std::memory_order_acquire)) {
			m_dropped.fetch_add(1, std::memory_order_relaxed);
			return;
		}
		const uint64_t head = m_head.load(std::memory_order_relaxed);
		const uint64_t tail = m_tail.load(std::memory_order_acquire);
		if (head - tail >= RingSize) {
			m_dropped.fetch_add(1, std::memory_order_relaxed);
			return;
		}
		m_ring[head % RingSize] = std::move(slot);
		m_head.store(head + 1, std::memory_order_release);
		m_wait_cv.notify_one();
	}

	void Stop() {
		if (!m_thread.joinable()) {
			return;
		}
		m_stop.store(true, std::memory_order_release);
		m_wait_cv.notify_one();
		m_thread.join();
	}

private:
	static constexpr size_t RingSize = 4096;

	static uint64_t NowMs() {
		return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
		                                 std::chrono::steady_clock::now().time_since_epoch())
		                                 .count());
	}

	void Loop() {
#if defined(_WIN32)
		SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_BELOW_NORMAL);
#endif
		while (true) {
			const bool stopping = m_stop.load(std::memory_order_acquire);
			Drain();
			ResolveWaiting();
			if (m_unsaved >= 256u || (m_unsaved != 0 && NowMs() - m_last_save_ms >= 30000u)) {
				SaveGeneration();
			}
			if (stopping) {
				Drain();
				ResolveWaiting();
				if (m_unsaved != 0) {
					SaveGeneration();
				}
				LogLine("stop");
				return;
			}
			std::unique_lock<std::mutex> lock(m_wait_mutex);
			m_wait_cv.wait_for(lock, std::chrono::milliseconds(100));
		}
	}

	void Drain() {
		uint64_t       tail = m_tail.load(std::memory_order_relaxed);
		const uint64_t head = m_head.load(std::memory_order_acquire);
		while (tail < head) {
			Slot slot = std::move(m_ring[tail % RingSize]);
			m_tail.store(++tail, std::memory_order_release);
			if (slot.source != nullptr) {
				HandleSource(*slot.source);
			}
			if (slot.spec != nullptr) {
				HandleSpec(*slot.spec);
			}
			if (slot.pipe != nullptr) {
				HandlePipe(std::move(slot.pipe));
			}
		}
	}

	void HandleSource(const SourceItem& item) {
		if (m_catalogue.FindSource(item.src_id) != nullptr) {
			return;
		}
		Catalogue::Source source;
		source.header.src_id          = item.src_id;
		source.header.hash            = item.hash;
		source.header.stage           = item.stage;
		source.header.user_data_count = item.user_data_count;
		source.header.code_size       = item.code_size;
		source.header.static_words    = static_cast<uint32_t>(item.static_state.size());
		source.header.code_words      = static_cast<uint32_t>(item.code.size());
		source.header.back_words      = static_cast<uint32_t>(item.back.size());
		Loader::GamePatchFile::Sha256 sha;
		sha.Update(reinterpret_cast<const uint8_t*>(item.code.data()), item.code.size() * sizeof(uint32_t));
		const auto hex = sha.FinalHex();
		for (size_t i = 0; i < 32 && 2 * i + 1 < hex.size(); i++) {
			source.header.sha256[i] = static_cast<uint8_t>(std::stoul(hex.substr(2 * i, 2), nullptr, 16));
		}
		source.static_state = item.static_state;
		source.code         = item.code;
		source.back         = item.back;
		m_catalogue.source_index[item.src_id] = static_cast<uint32_t>(m_catalogue.sources.size());
		m_catalogue.sources.push_back(std::move(source));
		m_stats.sources++;
		Count();
	}

	void HandleSpec(const SpecItem& item) {
		if (m_catalogue.FindSpec(item.spec_id) != nullptr) {
			return;
		}
		if (m_catalogue.FindSource(item.src_id) == nullptr || item.plan == nullptr) {
			m_orphans++; // its source was dropped by a full ring
			return;
		}
		std::vector<Word> words;
		size_t            user_words = 0;
		std::string       why;
		if (!Canonicalize(*item.plan, item.trace, item.live, words, user_words, why, TestStand() == Stand::Canon)) {
			if (why.starts_with("self")) {
				m_stats.canon_self++;
			} else if (why == "residual") {
				m_stats.canon_residual++;
			} else if (why == "base") {
				m_stats.canon_base++;
			} else {
				m_stats.canon_big++;
			}
			m_stats.canon_mismatch = m_stats.canon_self + m_stats.canon_residual;
			if (m_stats.canon_self + m_stats.canon_residual + m_stats.canon_base + m_stats.canon_big <= 20u) {
				LOGF("ShaderReplay: capture reject why=%s hash=0x%016" PRIx64 " words=%zu\n", why.c_str(),
				     item.plan->shader_hash, 2 + item.trace.user_data.size() + item.trace.reads.size());
			}
			return;
		}
		if (TestStand() == Stand::Addr && !m_addr_stand_done) {
			// KYTY_S_REPLAY_TEST=addr (member K3, RC7): this one record keeps the values as read - the offline scanner
			// R_ADDR must count its address words.
			m_addr_stand_done = true;
			words[0].value    = static_cast<uint32_t>(item.trace.shader_base);
			words[1].value    = static_cast<uint32_t>(item.trace.shader_base >> 32u);
			for (size_t i = 0; i < item.trace.user_data.size(); i++) {
				words[2 + i].value = item.trace.user_data[i];
			}
			for (size_t i = 0; i < item.trace.reads.size(); i++) {
				words[2 + user_words + i].value = item.trace.reads[i].value;
			}
			LOGF("ShaderReplay: stand addr applied spec=0x%016" PRIx64 "\n", item.spec_id);
		}
		Catalogue::Spec spec;
		spec.header.spec_id        = item.spec_id;
		spec.header.src_id         = item.src_id;
		spec.header.live_spec_hash = SpecializationHash(item.live);
		spec.header.stored_start   = item.stored_start;
		spec.header.user_words     = static_cast<uint32_t>(user_words);
		spec.header.reads          = static_cast<uint32_t>(words.size() - 2 - user_words);
		spec.header.words          = static_cast<uint32_t>(words.size());
		spec.words                 = std::move(words);
		m_catalogue.spec_index[item.spec_id] = static_cast<uint32_t>(m_catalogue.specs.size());
		m_catalogue.specs.push_back(std::move(spec));
		m_stats.specs++;
		Count();
	}

	bool Resolvable(const PipeItem& item) const {
		for (const auto id: item.spec) {
			if (id != 0 && m_catalogue.FindSpec(id) == nullptr) {
				return false;
			}
		}
		return item.spec[0] != 0;
	}

	void AddPipe(const PipeItem& item) {
		Catalogue::Pipe pipe;
		pipe.header.pipe_id  = item.pipe_id;
		pipe.header.spec[0]  = item.spec[0];
		pipe.header.spec[1]  = item.spec[1];
		pipe.header.kind     = item.kind;
		pipe.header.pod_size = static_cast<uint32_t>(item.pod.size());
		pipe.pod             = item.pod;
		m_catalogue.pipe_index[item.pipe_id] = static_cast<uint32_t>(m_catalogue.pipes.size());
		m_catalogue.pipes.push_back(std::move(pipe));
		m_stats.pipes++;
		Count();
	}

	void HandlePipe(std::unique_ptr<PipeItem> item) {
		if (m_catalogue.pipe_index.contains(item->pipe_id) || m_waiting_ids.contains(item->pipe_id)) {
			return;
		}
		if (Resolvable(*item)) {
			AddPipe(*item);
			return;
		}
		m_waiting_ids.insert(item->pipe_id);
		m_waiting.push_back(std::move(item));
	}

	void ResolveWaiting() {
		for (auto it = m_waiting.begin(); it != m_waiting.end();) {
			if (Resolvable(**it)) {
				AddPipe(**it);
				m_waiting_ids.erase((*it)->pipe_id);
				it = m_waiting.erase(it);
			} else {
				++it;
			}
		}
		m_stats.pipes_waiting = static_cast<uint32_t>(m_waiting.size());
	}

	void Count() {
		m_unsaved++;
		m_records++;
	}

	void SaveGeneration() {
		const uint64_t generation = m_generation + 1;
		uint64_t       bytes      = 0;
		m_last_save_ms            = NowMs();
		if (!m_store.Save(m_catalogue, generation, bytes)) {
			LOGF("ShaderReplay: capture save FAILED generation=%" PRIu64 " dir=%s\n", generation,
			     Common::PathToString(m_store.Directory()).c_str());
			return;
		}
		m_generation       = generation;
		m_stats.bytes      = bytes;
		m_stats.generation = generation;
		m_unsaved          = 0;
		LogLine("save");
	}

	void LogLine(const char* why) {
		m_stats.dropped_queue = m_dropped.load(std::memory_order_relaxed) + m_orphans;
		LOGF("ShaderReplay: capture sources=%u specs=%u pipes=%u canon_mismatch=%u dropped_queue=%u bytes=%" PRIu64
		     " gen=%" PRIu64 " canon_self=%u canon_residual=%u canon_base=%u canon_big=%u pipes_waiting=%u "
		     "catalogue_sources=%zu catalogue_specs=%zu catalogue_pipes=%zu at=%s\n",
		     m_stats.sources, m_stats.specs, m_stats.pipes, m_stats.canon_mismatch, m_stats.dropped_queue, m_stats.bytes,
		     m_stats.generation, m_stats.canon_self, m_stats.canon_residual, m_stats.canon_base, m_stats.canon_big,
		     m_stats.pipes_waiting, m_catalogue.sources.size(), m_catalogue.specs.size(), m_catalogue.pipes.size(), why);
	}

	Store&                         m_store;
	Catalogue                      m_catalogue;
	uint64_t                       m_generation = 0;
	CaptureStats                   m_stats;
	std::vector<Slot>              m_ring = std::vector<Slot>(RingSize);
	std::atomic<uint64_t>          m_head {0};
	std::atomic<uint64_t>          m_tail {0};
	std::atomic<uint32_t>          m_dropped {0};
	std::atomic<bool>              m_stop {false};
	std::mutex                     m_wait_mutex; // only the writer's wait; producers notify without it
	std::condition_variable        m_wait_cv;
	std::thread                    m_thread;
	std::vector<std::unique_ptr<PipeItem>> m_waiting;
	std::unordered_set<uint64_t>   m_waiting_ids;
	uint32_t                       m_orphans         = 0;
	uint32_t                       m_unsaved         = 0;
	uint64_t                       m_records         = 0;
	uint64_t                       m_last_save_ms    = 0;
	bool                           m_addr_stand_done = false;
};

Capture::Capture(Store& store, Catalogue initial, uint64_t generation)
    : m_writer(std::make_unique<Writer>(store, std::move(initial), generation)) {}

Capture::~Capture() {
	Stop();
}

void Capture::Push(std::unique_ptr<SourceItem> item) {
	m_writer->Push({.source = std::move(item)});
}

void Capture::Push(std::unique_ptr<SpecItem> item) {
	m_writer->Push({.spec = std::move(item)});
}

void Capture::Push(std::unique_ptr<PipeItem> item) {
	m_writer->Push({.pipe = std::move(item)});
}

void Capture::Stop() {
	m_writer->Stop();
}

} // namespace Libs::Graphics::ShaderReplay
