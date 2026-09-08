#include "graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h"

#include "common/file.h"
#include "common/logging/log.h"
#include "common/stringUtils.h"
#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"
#include "graphics/shader/recompiler/ir/Value.h"
#include "kytyGitVersion.h"

#include <cstdlib>
#include <cstring>
#include <string_view>
#include <unordered_map>
#include <xxhash.h>

namespace Libs::Graphics {

namespace IR = ShaderRecompiler::IR;

namespace {

constexpr uint32_t FORMAT_VERSION = 2;

// Little binary writer / reader. Every enum is stored as u32, every count as u32; the reader
// fails (returns false) on truncation and the caller drops the file.
class Writer final {
public:
	void Bytes(const void* data, size_t size) {
		const auto* p = static_cast<const uint8_t*>(data);
		m_data.insert(m_data.end(), p, p + size);
	}
	void U8(uint8_t v) { Bytes(&v, sizeof(v)); }
	void U32(uint32_t v) { Bytes(&v, sizeof(v)); }
	void U64(uint64_t v) { Bytes(&v, sizeof(v)); }
	void I32(int32_t v) { Bytes(&v, sizeof(v)); }
	void Bool(bool v) { U8(v ? 1 : 0); }
	template <typename E>
	void Enum(E v) {
		U32(static_cast<uint32_t>(v));
	}
	template <typename T>
	void Pod(const T& v) {
		static_assert(std::is_trivially_copyable_v<T>);
		Bytes(&v, sizeof(v));
	}
	void Str(const std::string& s) {
		U32(static_cast<uint32_t>(s.size()));
		Bytes(s.data(), s.size());
	}
	template <typename T>
	void PodVec(const std::vector<T>& v) {
		static_assert(std::is_trivially_copyable_v<T>);
		U32(static_cast<uint32_t>(v.size()));
		if (!v.empty()) {
			Bytes(v.data(), v.size() * sizeof(T));
		}
	}
	template <typename T, typename F>
	void Vec(const std::vector<T>& v, F&& f) {
		U32(static_cast<uint32_t>(v.size()));
		for (const auto& e: v) {
			f(e);
		}
	}
	[[nodiscard]] const std::vector<uint8_t>& Data() const { return m_data; }

private:
	std::vector<uint8_t> m_data;
};

class Reader final {
public:
	Reader(const uint8_t* data, size_t size): m_data(data), m_size(size) {}

	bool Bytes(void* out, size_t size) {
		if (m_failed || size > m_size - m_pos) {
			m_failed = true;
			return false;
		}
		std::memcpy(out, m_data + m_pos, size);
		m_pos += size;
		return true;
	}
	uint8_t U8() {
		uint8_t v = 0;
		Bytes(&v, sizeof(v));
		return v;
	}
	uint32_t U32() {
		uint32_t v = 0;
		Bytes(&v, sizeof(v));
		return v;
	}
	uint64_t U64() {
		uint64_t v = 0;
		Bytes(&v, sizeof(v));
		return v;
	}
	int32_t I32() {
		int32_t v = 0;
		Bytes(&v, sizeof(v));
		return v;
	}
	bool Bool() { return U8() != 0; }
	template <typename E>
	E Enum() {
		return static_cast<E>(U32());
	}
	template <typename T>
	T Pod() {
		static_assert(std::is_trivially_copyable_v<T>);
		T v {};
		Bytes(&v, sizeof(v));
		return v;
	}
	std::string Str() {
		const auto  n = U32();
		std::string s;
		if (m_failed || n > m_size - m_pos) {
			m_failed = true;
			return s;
		}
		s.assign(reinterpret_cast<const char*>(m_data + m_pos), n);
		m_pos += n;
		return s;
	}
	template <typename T>
	std::vector<T> PodVec() {
		static_assert(std::is_trivially_copyable_v<T>);
		const auto     n = U32();
		std::vector<T> v;
		if (m_failed || n > (m_size - m_pos) / sizeof(T)) {
			m_failed = true;
			return v;
		}
		v.resize(n);
		if (n != 0) {
			Bytes(v.data(), n * sizeof(T));
		}
		return v;
	}
	// Count prefix with a sanity bound (an element takes at least one byte).
	uint32_t Count() {
		const auto n = U32();
		if (m_failed || n > m_size - m_pos) {
			m_failed = true;
			return 0;
		}
		return n;
	}
	[[nodiscard]] bool Failed() const { return m_failed; }
	[[nodiscard]] bool AtEnd() const { return m_pos == m_size; }

private:
	const uint8_t* m_data   = nullptr;
	size_t         m_size   = 0;
	size_t         m_pos    = 0;
	bool           m_failed = false;
};

// --- values -------------------------------------------------------------------------------

// A Value is (type, bits); an instruction reference is stored as its index in value_storage.
void WriteValue(Writer& w, const IR::Value& value,
                const std::unordered_map<const IR::Inst*, uint32_t>& index_of) {
	// GetType() of an instruction reference is the instruction's result type: store the
	// reference under Type::Opaque explicitly.
	if (!value.IsImmediate()) {
		w.Enum(IR::Type::Opaque);
		const auto* inst = value.TryInstruction();
		if (inst == nullptr) {
			w.U64(UINT64_MAX);
			return;
		}
		const auto found = index_of.find(inst);
		// Every reachable instruction was cloned into value_storage by ExtractResourcePlan.
		w.U64(found != index_of.end() ? found->second : UINT64_MAX);
		return;
	}
	w.Enum(value.GetType());
	w.U64(value.Bits());
}

IR::Value ReadValue(Reader& r, const std::vector<IR::Inst*>& insts, bool& ok) {
	const auto type = r.Enum<IR::Type>();
	const auto bits = r.U64();
	if (type == IR::Type::Opaque) {
		if (bits == UINT64_MAX) {
			return IR::Value(static_cast<IR::Inst*>(nullptr));
		}
		if (bits >= insts.size()) {
			ok = false;
			return {};
		}
		return IR::Value(insts[bits]);
	}
	return IR::Value::FromBits(type, bits);
}

// --- shader info ----------------------------------------------------------------------------

void WriteImage(Writer& w, const IR::ImageResource& i) {
	w.U32(i.source);
	w.U32(i.first_use_pc);
	w.Enum(i.resource_class);
	w.Enum(i.numeric_class);
	w.Enum(i.dimension);
	w.Enum(i.mip_mode);
	w.U32(i.mip_count);
	w.Enum(i.conversion_format);
	w.U32(i.shader_swizzle);
	w.Bool(i.read);
	w.Bool(i.written);
	w.Bool(i.atomic);
	w.Bool(i.depth_compare);
	w.Bool(i.cube);
	w.Bool(i.r128);
	w.Bool(i.manual_depth_compare);
	w.U32(i.depth_compare_op);
	w.U32(i.indirect_root);
	w.U32(i.indirect_mapping_offset);
	w.U32(i.indirect_search_iterations);
	w.PodVec(i.indirect_resources);
}

IR::ImageResource ReadImage(Reader& r) {
	IR::ImageResource i;
	i.source                     = r.U32();
	i.first_use_pc               = r.U32();
	i.resource_class             = r.Enum<IR::ImageResourceClass>();
	i.numeric_class              = r.Enum<Prospero::TextureNumericClass>();
	i.dimension                  = r.Enum<ShaderRecompiler::Decoder::ImageDimension>();
	i.mip_mode                   = r.Enum<IR::ImageMipMode>();
	i.mip_count                  = r.U32();
	i.conversion_format          = r.Enum<Prospero::BufferFormat>();
	i.shader_swizzle             = r.U32();
	i.read                       = r.Bool();
	i.written                    = r.Bool();
	i.atomic                     = r.Bool();
	i.depth_compare              = r.Bool();
	i.cube                       = r.Bool();
	i.r128                       = r.Bool();
	i.manual_depth_compare       = r.Bool();
	i.depth_compare_op           = r.U32();
	i.indirect_root              = r.U32();
	i.indirect_mapping_offset    = r.U32();
	i.indirect_search_iterations = r.U32();
	i.indirect_resources         = r.PodVec<uint32_t>();
	return i;
}

void WriteShaderInfo(Writer& w, const IR::ShaderInfo& info) {
	w.PodVec(info.buffers);
	w.Vec(info.images, [&](const IR::ImageResource& i) { WriteImage(w, i); });
	w.PodVec(info.samplers);
	w.PodVec(info.sampled_pairs);
	w.Vec(info.inputs, [&](const IR::StageInput& i) {
		w.Enum(i.kind);
		w.U32(i.location);
		w.U32(i.component_count);
		w.Str(i.debug_name);
		w.Bool(i.per_vertex);
	});
	w.Vec(info.outputs, [&](const IR::StageOutput& o) {
		w.Enum(o.kind);
		w.U32(o.index);
		w.U32(o.location);
		w.Str(o.debug_name);
	});
	w.Pod(info.vertex_fetch_components);
	w.I32(info.vertex_offset_sgpr);
	w.I32(info.instance_offset_sgpr);
	w.Bool(info.has_bitwise_xor);
	w.Bool(info.uses_dma);
}

bool ReadShaderInfo(Reader& r, IR::ShaderInfo& info) {
	info.buffers = r.PodVec<IR::BufferResource>();
	const auto n_images = r.Count();
	info.images.clear();
	info.images.reserve(n_images);
	for (uint32_t i = 0; i < n_images && !r.Failed(); i++) {
		info.images.push_back(ReadImage(r));
	}
	info.samplers      = r.PodVec<IR::SamplerResource>();
	info.sampled_pairs = r.PodVec<IR::SampledResourcePair>();
	const auto n_inputs = r.Count();
	info.inputs.clear();
	for (uint32_t i = 0; i < n_inputs && !r.Failed(); i++) {
		IR::StageInput in;
		in.kind            = r.Enum<IR::StageInputKind>();
		in.location        = r.U32();
		in.component_count = r.U32();
		in.debug_name      = r.Str();
		in.per_vertex      = r.Bool();
		info.inputs.push_back(std::move(in));
	}
	const auto n_outputs = r.Count();
	info.outputs.clear();
	for (uint32_t i = 0; i < n_outputs && !r.Failed(); i++) {
		IR::StageOutput out;
		out.kind       = r.Enum<IR::StageOutputKind>();
		out.index      = r.U32();
		out.location   = r.U32();
		out.debug_name = r.Str();
		info.outputs.push_back(std::move(out));
	}
	info.vertex_fetch_components = r.Pod<std::array<uint8_t, 32>>();
	info.vertex_offset_sgpr      = r.I32();
	info.instance_offset_sgpr    = r.I32();
	info.has_bitwise_xor         = r.Bool();
	info.uses_dma                = r.Bool();
	return !r.Failed();
}

void WriteBindingLayout(Writer& w, const IR::BindingLayout& b) {
	w.U32(b.push_data_start_dword);
	w.U32(b.memory_offset_dword);
	w.U32(b.memory_offset_count);
	w.PodVec(b.user_data_registers);
	w.Vec(b.descriptors, [&](const IR::DescriptorBinding& d) {
		w.Enum(d.kind);
		w.PodVec(d.resources);
	});
}

bool ReadBindingLayout(Reader& r, IR::BindingLayout& b) {
	b.push_data_start_dword = r.U32();
	b.memory_offset_dword   = r.U32();
	b.memory_offset_count   = r.U32();
	b.user_data_registers   = r.PodVec<uint32_t>();
	const auto n            = r.Count();
	b.descriptors.clear();
	for (uint32_t i = 0; i < n && !r.Failed(); i++) {
		IR::DescriptorBinding d;
		d.kind      = r.Enum<IR::DescriptorBindingKind>();
		d.resources = r.PodVec<uint32_t>();
		b.descriptors.push_back(std::move(d));
	}
	return !r.Failed();
}

void WriteCompiledInfo(Writer& w, const IR::CompiledShaderInfo& c) {
	w.Enum(c.stage);
	w.U64(c.shader_hash);
	w.U32(c.wave_size);
	w.U32(c.user_data_base);
	w.U32(c.user_data_count);
	w.U32(c.scratch_dwords);
	w.U32(c.param_export_mask);
	WriteShaderInfo(w, c.info);
	WriteBindingLayout(w, c.bindings);
}

bool ReadCompiledInfo(Reader& r, IR::CompiledShaderInfo& c) {
	c.stage             = r.Enum<ShaderType>();
	c.shader_hash       = r.U64();
	c.wave_size         = r.U32();
	c.user_data_base    = r.U32();
	c.user_data_count   = r.U32();
	c.scratch_dwords    = r.U32();
	c.param_export_mask = r.U32();
	return ReadShaderInfo(r, c.info) && ReadBindingLayout(r, c.bindings);
}

void WriteSpecialization(Writer& w, const IR::ResourceSpecialization& s) {
	w.PodVec(s.buffers);
	w.PodVec(s.images);
}

bool ReadSpecialization(Reader& r, IR::ResourceSpecialization& s) {
	s.buffers = r.PodVec<IR::ResourceSpecialization::Buffer>();
	s.images  = r.PodVec<IR::ResourceSpecialization::Image>();
	return !r.Failed();
}

// --- resource plan --------------------------------------------------------------------------

void WritePlan(Writer& w, const IR::ResourcePlan& plan) {
	w.Enum(plan.stage);
	w.U64(plan.shader_hash);
	w.U32(plan.user_data_base);
	w.U32(plan.user_data_count);

	std::unordered_map<const IR::Inst*, uint32_t> index_of;
	index_of.reserve(plan.value_storage.size());
	for (const auto& inst: plan.value_storage) {
		index_of.emplace(&inst, static_cast<uint32_t>(index_of.size()));
	}
	w.U32(static_cast<uint32_t>(plan.value_storage.size()));
	for (const auto& inst: plan.value_storage) {
		w.Enum(inst.GetOpcode());
		w.U64(inst.Flags<uint64_t>());
		w.U32(static_cast<uint32_t>(inst.NumArgs()));
		for (size_t i = 0; i < inst.NumArgs(); i++) {
			WriteValue(w, inst.Arg(i), index_of);
		}
	}
	w.PodVec(plan.memory_info);
	w.Vec(plan.descriptor_sources, [&](const IR::DescriptorSource& s) {
		w.U32(s.dword_count);
		for (uint32_t i = 0; i < 8; i++) {
			WriteValue(w, s.dwords[i], index_of);
		}
		w.Bool(s.indirect_image.has_value());
		if (s.indirect_image.has_value()) {
			w.Pod(*s.indirect_image);
		}
	});
	w.PodVec(plan.materialization_sources);
	w.Vec(plan.srt_reads, [&](const IR::SrtRead& s) {
		WriteValue(w, s.value, index_of);
		w.U32(s.flat_offset);
		w.Bool(s.variant);
	});
	w.PodVec(plan.clean_flat_slots);
	w.Bool(plan.requires_specialization_memory);
	w.Bool(plan.srt_plan_complete);
	w.Bool(plan.resource_tracking_complete);
	WriteShaderInfo(w, plan.info);
}

bool ReadPlan(Reader& r, IR::ResourcePlan& plan) {
	plan.stage           = r.Enum<ShaderType>();
	plan.shader_hash     = r.U64();
	plan.user_data_base  = r.U32();
	plan.user_data_count = r.U32();

	const auto n_insts = r.Count();
	std::vector<IR::Inst*> insts;
	insts.reserve(n_insts);
	// Two passes: instructions first (phis may reference later ones), then the operands.
	struct Raw {
		IR::ValueOpcode opcode;
		uint64_t        flags;
		uint32_t        num_args;
	};
	std::vector<Raw> raws;
	// Operands are read in the first pass into a flat list of (type, bits) and resolved after.
	struct RawValue {
		IR::Type type;
		uint64_t bits;
	};
	std::vector<std::vector<RawValue>> raw_args;
	raws.reserve(n_insts);
	raw_args.reserve(n_insts);
	for (uint32_t i = 0; i < n_insts && !r.Failed(); i++) {
		Raw raw {};
		raw.opcode   = r.Enum<IR::ValueOpcode>();
		raw.flags    = r.U64();
		raw.num_args = r.U32();
		if (r.Failed() || raw.num_args > 4096) {
			return false;
		}
		std::vector<RawValue> values(raw.num_args);
		for (auto& v: values) {
			v.type = r.Enum<IR::Type>();
			v.bits = r.U64();
		}
		raws.push_back(raw);
		raw_args.push_back(std::move(values));
	}
	if (r.Failed()) {
		return false;
	}
	for (const auto& raw: raws) {
		auto& inst = plan.value_storage.emplace_back(raw.opcode, raw.flags);
		insts.push_back(&inst);
	}
	const auto resolve = [&](const RawValue& v, bool& ok) -> IR::Value {
		if (v.type == IR::Type::Opaque) {
			if (v.bits == UINT64_MAX) {
				return IR::Value(static_cast<IR::Inst*>(nullptr));
			}
			if (v.bits >= insts.size()) {
				ok = false;
				return {};
			}
			return IR::Value(insts[v.bits]);
		}
		return IR::Value::FromBits(v.type, v.bits);
	};
	bool ok = true;
	for (size_t i = 0; i < insts.size(); i++) {
		auto* inst = insts[i];
		if (raws[i].opcode == IR::ValueOpcode::Phi) {
			for (const auto& v: raw_args[i]) {
				inst->AddPhiOperand(nullptr, resolve(v, ok));
			}
		} else {
			for (size_t a = 0; a < raw_args[i].size(); a++) {
				inst->SetArg(a, resolve(raw_args[i][a], ok));
			}
		}
	}
	if (!ok) {
		return false;
	}
	plan.memory_info = r.PodVec<IR::MemoryInfo>();
	const auto n_sources = r.Count();
	plan.descriptor_sources.clear();
	for (uint32_t i = 0; i < n_sources && !r.Failed(); i++) {
		IR::DescriptorSource s;
		s.dword_count = r.U32();
		for (uint32_t d = 0; d < 8; d++) {
			s.dwords[d] = ReadValue(r, insts, ok);
		}
		if (r.Bool()) {
			s.indirect_image = r.Pod<IR::DescriptorSource::IndirectImage>();
		}
		plan.descriptor_sources.push_back(std::move(s));
	}
	plan.materialization_sources = r.PodVec<uint32_t>();
	const auto n_reads           = r.Count();
	plan.srt_reads.clear();
	for (uint32_t i = 0; i < n_reads && !r.Failed(); i++) {
		IR::SrtRead s;
		s.value       = ReadValue(r, insts, ok);
		s.flat_offset = r.U32();
		s.variant     = r.Bool();
		plan.srt_reads.push_back(s);
	}
	plan.clean_flat_slots               = r.PodVec<uint8_t>();
	plan.requires_specialization_memory = r.Bool();
	plan.srt_plan_complete              = r.Bool();
	plan.resource_tracking_complete     = r.Bool();
	return ok && !r.Failed() && ReadShaderInfo(r, plan.info);
}

} // namespace

ShaderTranslationCache::ShaderTranslationCache(const std::string& title_id) {
	const char* env = std::getenv("KYTY_SHADER_CACHE");
	if (env != nullptr && env[0] == '0') {
		LOGF("Shader translation cache: disabled (KYTY_SHADER_CACHE=0)\n");
		return;
	}
	const std::string_view translator_hash = KYTY_SHADER_SOURCE_HASH;
	if (title_id.empty() || translator_hash == "unknown") {
		LOGF("Shader translation cache: disabled (unknown title or translator hash)\n");
		return;
	}
	m_directory = std::filesystem::path("_ShaderCache") / title_id;
	// Keyed by the translator sources, not the git revision: unrelated commits keep the cache.
	m_signature = std::string("KytySC") + std::to_string(FORMAT_VERSION) + ":" +
	              std::string(translator_hash) +
	              (ShaderRecompiler::Spirv::Emitter::RobustBufferLoads() ? ":robust" : "") +
	              (ShaderRecompiler::Spirv::Emitter::DenormFlushToZero() ? ":ftz" : "") +
	              (ShaderRecompiler::Spirv::Emitter::DenormFlushToZeroDeclared() ? ":ftzd" : "") + "\n";
	m_enabled = true;
	LOGF("Shader translation cache: %s\n", Common::PathToString(m_directory).c_str());
}

std::filesystem::path ShaderTranslationCache::PathOf(const Key& key) const {
	// The static state (vertex attributes, pixel inputs, wave size...) selects the variant.
	XXH3_state_t* state = XXH3_createState();
	XXH3_64bits_reset(state);
	XXH3_64bits_update(state, &key.user_data_count, sizeof(key.user_data_count));
	XXH3_64bits_update(state, &key.code_size, sizeof(key.code_size));
	if (!key.static_state.empty()) {
		XXH3_64bits_update(state, key.static_state.data(),
		                   key.static_state.size_bytes());
	}
	const auto state_hash = XXH3_64bits_digest(state);
	XXH3_freeState(state);
	char name[80];
	std::snprintf(name, sizeof(name), "%s_%016llx_%016llx.bin",
	              key.stage == static_cast<uint32_t>(ShaderType::Vertex)  ? "vs"
	              : key.stage == static_cast<uint32_t>(ShaderType::Pixel) ? "ps"
	                                                                       : "cs",
	              static_cast<unsigned long long>(key.hash),
	              static_cast<unsigned long long>(state_hash));
	return m_directory / name;
}

bool ShaderTranslationCache::Load(const Key& key, Entry& entry) {
	if (!m_enabled) {
		return false;
	}
	const auto path = PathOf(key);
	if (!Common::File::IsFileExisting(path)) {
		return false;
	}
	Common::File file(path, Common::File::Mode::Read);
	if (file.IsInvalid()) {
		return false;
	}
	const auto size = file.Size();
	if (size < m_signature.size() + sizeof(uint64_t) || size > (64u << 20)) {
		return false;
	}
	std::vector<uint8_t> data(static_cast<size_t>(size));
	uint32_t             read = 0;
	file.Read(data.data(), static_cast<uint32_t>(data.size()), &read);
	file.Close();
	if (read != data.size()) {
		return false;
	}
	if (std::memcmp(data.data(), m_signature.data(), m_signature.size()) != 0) {
		return false;
	}
	uint64_t stored_hash = 0;
	std::memcpy(&stored_hash, data.data() + m_signature.size(), sizeof(stored_hash));
	const auto* payload      = data.data() + m_signature.size() + sizeof(stored_hash);
	const auto  payload_size = data.size() - m_signature.size() - sizeof(stored_hash);
	if (XXH3_64bits(payload, payload_size) != stored_hash) {
		LOGF("Shader translation cache: corrupt %s\n", Common::PathToString(path).c_str());
		return false;
	}
	Reader r(payload, payload_size);
	// Key echo.
	if (r.U32() != key.stage || r.U64() != key.hash || r.U32() != key.user_data_count ||
	    r.U32() != key.code_size) {
		return false;
	}
	const auto state = r.PodVec<uint32_t>();
	if (r.Failed() || state.size() != key.static_state.size() ||
	    !std::equal(state.begin(), state.end(), key.static_state.begin())) {
		return false;
	}
	if (!ReadPlan(r, entry.plan)) {
		LOGF("Shader translation cache: unreadable plan in %s\n",
		     Common::PathToString(path).c_str());
		return false;
	}
	const auto n = r.Count();
	entry.permutations.clear();
	for (uint32_t i = 0; i < n && !r.Failed(); i++) {
		Permutation p;
		if (!ReadSpecialization(r, p.specialization) || !ReadCompiledInfo(r, p.program)) {
			return false;
		}
		p.spirv = r.PodVec<uint32_t>();
		if (r.Failed() || p.spirv.empty()) {
			return false;
		}
		entry.permutations.push_back(std::move(p));
	}
	if (r.Failed() || !r.AtEnd()) {
		return false;
	}
	m_loaded++;
	return true;
}

bool ShaderTranslationCache::ReadFileUnchecked(const std::filesystem::path& path, StoredKey& key,
                                               Entry& entry) {
	if (!Common::File::IsFileExisting(path)) {
		return false;
	}
	Common::File file(path, Common::File::Mode::Read);
	if (file.IsInvalid()) {
		return false;
	}
	const auto           size = file.Size();
	std::vector<uint8_t> data(static_cast<size_t>(size));
	uint32_t             read = 0;
	file.Read(data.data(), static_cast<uint32_t>(data.size()), &read);
	file.Close();
	if (read != data.size() || data.size() < 8u) {
		return false;
	}
	// signature = "KytySC<version>:<translator hash>[:robust]\n"
	const auto newline = std::find(data.begin(), data.end(), static_cast<uint8_t>(10));
	if (newline == data.end() || std::memcmp(data.data(), "KytySC", 6) != 0) {
		return false;
	}
	const auto signature_size = static_cast<size_t>(newline - data.begin()) + 1u;
	if (data.size() < signature_size + sizeof(uint64_t)) {
		return false;
	}
	uint64_t stored_hash = 0;
	std::memcpy(&stored_hash, data.data() + signature_size, sizeof(stored_hash));
	const auto* payload      = data.data() + signature_size + sizeof(stored_hash);
	const auto  payload_size = data.size() - signature_size - sizeof(stored_hash);
	if (XXH3_64bits(payload, payload_size) != stored_hash) {
		return false;
	}
	Reader r(payload, payload_size);
	key.stage           = r.U32();
	key.hash            = r.U64();
	key.user_data_count = r.U32();
	key.code_size       = r.U32();
	key.static_state    = r.PodVec<uint32_t>();
	if (r.Failed() || !ReadPlan(r, entry.plan)) {
		return false;
	}
	const auto n = r.Count();
	entry.permutations.clear();
	for (uint32_t i = 0; i < n && !r.Failed(); i++) {
		Permutation p;
		if (!ReadSpecialization(r, p.specialization) || !ReadCompiledInfo(r, p.program)) {
			return false;
		}
		p.spirv = r.PodVec<uint32_t>();
		if (r.Failed() || p.spirv.empty()) {
			return false;
		}
		entry.permutations.push_back(std::move(p));
	}
	return !r.Failed() && r.AtEnd();
}

bool ShaderTranslationCache::Save(const Key& key, const IR::ResourcePlan& plan,
                                  std::span<const Permutation> permutations) {
	if (!m_enabled) {
		return false;
	}
	Writer w;
	w.U32(key.stage);
	w.U64(key.hash);
	w.U32(key.user_data_count);
	w.U32(key.code_size);
	w.U32(static_cast<uint32_t>(key.static_state.size()));
	if (!key.static_state.empty()) {
		w.Bytes(key.static_state.data(), key.static_state.size_bytes());
	}
	WritePlan(w, plan);
	w.U32(static_cast<uint32_t>(permutations.size()));
	for (const auto& p: permutations) {
		WriteSpecialization(w, p.specialization);
		WriteCompiledInfo(w, p.program);
		w.PodVec(p.spirv);
	}
	const auto& payload      = w.Data();
	const auto  payload_hash = XXH3_64bits(payload.data(), payload.size());

	if (!Common::File::CreateDirectories(m_directory)) {
		return false;
	}
	const auto path = PathOf(key);
	auto       temp = path;
	temp += ".tmp";
	Common::File file;
	if (!file.Create(temp)) {
		return false;
	}
	uint32_t w1 = 0;
	uint32_t w2 = 0;
	uint32_t w3 = 0;
	file.Write(m_signature.data(), static_cast<uint32_t>(m_signature.size()), &w1);
	file.Write(&payload_hash, sizeof(payload_hash), &w2);
	file.Write(payload.data(), static_cast<uint32_t>(payload.size()), &w3);
	const bool flushed = file.Flush();
	file.Close();
	if (w1 != m_signature.size() || w2 != sizeof(payload_hash) || w3 != payload.size() ||
	    !flushed) {
		Common::File::DeleteFile(temp);
		return false;
	}
	if (Common::File::IsFileExisting(path)) {
		Common::File::DeleteFile(path);
	}
	if (!Common::File::RenameFile(temp, path)) {
		return false;
	}
	m_saved++;
	return true;
}

} // namespace Libs::Graphics
