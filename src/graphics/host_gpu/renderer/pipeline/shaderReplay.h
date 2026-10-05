#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINE_SHADERREPLAY_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINE_SHADERREPLAY_H_

// Track S, S17a (HPP-611, ROADMAP "SESSION 122" item 524(e)-(z); design docs/track-s/s16a-design.md sections 2-3, 7):
// S-replay - a catalogue of the shader translation inputs that survives a change of the translator signature.
// Knob KYTY_S_REPLAY (read once per process): 0 (default; unset, "" or 0) - off: no file, no "ShaderReplay:" line, no
// writer thread; 1 - capture and rebuild; 2 - capture only; 3 - rebuild only. Stands KYTY_S_REPLAY_TEST=canon|spec|addr|
// stop|corrupt (positive controls of members K3, K4, K6).
//
// Not in the translator signature set (src/graphics/shader/** and SHADER_CACHE_EXTRA_FILES of CMakeLists.txt): the
// specialization is re-derived by MaterializeResources with a synthetic SrtRuntime that answers the canonical words of
// the recorded read path (member K1(7), RC10(b) of the S16b review), so BuildResourceSpecialization is not exported.
//
// Records (catalogue format KytyReplay1, one generation file _ShaderCache/<title>/replay/replay.<g>.bin):
//   R-SRC  - stage, hash, user data count, code size, the static key of the stage, sha256 and a copy of the GCN
//            (and of the back half of a fused stage); no address, no user data value.
//   R-SPEC - a reference to its R-SRC and the canonical read path of one materialization: the shader base, the user
//            data words and every word the SRT walk read, in order, each with its role; address words are canonical
//            (ROLE_* below). The live specialization is kept only as a hash (self-check reference).
//   R-PIPE - references to the R-SPEC of each stage and the POD of the pipeline (rendering state, vertex input state,
//            static parameters), no Shader*InputInfo bytes: the stage input is rebuilt from the static key (form K).

#include "graphics/shader/shader.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>
#include <string>
#include <unordered_map>
#include <vector>

namespace Libs::Graphics::ShaderReplay {

// Versions of the record inputs (item 524(e)): a translator change that reads a stage input field outside the static
// key raises StaticKeyVersion or ReplayInputVersion; a change of the canonical rules raises CanonVersion. All are part
// of the compatibility string; the translator signature and the GPU model are not.
constexpr uint32_t FormatVersion      = 1;
constexpr uint32_t StaticKeyVersion   = 1;
constexpr uint32_t CanonVersion       = 1;
constexpr uint32_t ReplayInputVersion = 1;

// 0, 1, 2, 3 (see above); any other value of the variable reads as 0.
int  Mode();
bool CaptureOn();
bool RebuildOn();

enum class Stand : uint8_t { None, Canon, Spec, Addr, Stop, Corrupt };
Stand TestStand();
const char* StandName(Stand stand);
// KYTY_S_REPLAY_TEST=stop: posts the event of a click on the close button of the window (member K6).
void StandRequestClose();

// Role of a word of the read path (Word::role). Canonical forms, checked by the offline scanner R_ADDR:
//   PTR_LO, V_LO        0 or 0x100 | (v & 0xF) (V# base 0 stays 0)
//   PTR_HI, V_HI        v & 0xFFFF0000 (bits 0..15 of the high dword - base[47:32] - cleared)
//   T_LO                0 or 1 (T# base[39:8]: null stays 0, else the address 0x100)
//   T_HI                v & 0xFFFFFF00 (base[47:40] cleared)
//   T_META6             v & 0x00FFFFFF (metadata address [15:8] cleared)
//   T_META7             0 (metadata address [47:16])
//   INERT               0 or 0x100 | (v & 0xF) (a word that changed neither the walk nor the specialization)
//   KEEP                as read (a scalar the specialization or the walk depends on)
enum Role : uint8_t {
	ROLE_KEEP    = 0,
	ROLE_INERT   = 1,
	ROLE_PTR_LO  = 2,
	ROLE_PTR_HI  = 3,
	ROLE_V_LO    = 4,
	ROLE_V_HI    = 5,
	ROLE_T_LO    = 6,
	ROLE_T_HI    = 7,
	ROLE_T_META6 = 8,
	ROLE_T_META7 = 9,
	ROLE_COUNT   = 10,
};

// Word::flags
constexpr uint8_t WORD_CLEAN = 1u; // read through the specialization (GPU-clean) reader
constexpr uint8_t WORD_OK    = 2u; // the read succeeded
constexpr uint8_t WORD_USER  = 4u; // a user data word (not a read)
constexpr uint8_t WORD_BASE  = 8u; // a half of the shader base (word 0 low, word 1 high)

#pragma pack(push, 1)
struct Word {
	uint32_t value = 0;
	uint8_t  role  = ROLE_KEEP;
	uint8_t  flags = 0;
};

// File: FileHeader, the compatibility string (compat_size bytes), BodyHeader, then the body: `sources` records
// (SourceHeader, static_words + code_words + back_words u32), `specs` records (SpecHeader, words Word), `pipes` records
// (PipeHeader, pod_size bytes). body_checksum = XXH3-64 of the body (everything after BodyHeader).
struct FileHeader {
	char     magic[8]    = {'K', 'y', 't', 'y', 'R', 'p', 'l', '1'};
	uint32_t format      = FormatVersion;
	uint32_t compat_size = 0;
};

struct BodyHeader {
	uint64_t generation    = 0;
	uint64_t body_checksum = 0;
	uint32_t sources       = 0;
	uint32_t specs         = 0;
	uint32_t pipes         = 0;
	uint32_t reserved      = 0;
};

struct SourceHeader {
	uint64_t src_id          = 0;
	uint64_t hash            = 0;
	uint32_t stage           = 0;
	uint32_t user_data_count = 0;
	uint32_t code_size       = 0;
	uint32_t static_words    = 0;
	uint32_t code_words      = 0;
	uint32_t back_words      = 0;
	uint8_t  sha256[32]      = {};
};

struct SpecHeader {
	uint64_t spec_id        = 0;
	uint64_t src_id         = 0;
	uint64_t live_spec_hash = 0; // XXH3 of the specialization the run made (self-check reference)
	uint32_t stored_start   = 0; // push-data start of the live permutation (reference: rb_push_moved)
	uint32_t user_words     = 0;
	uint32_t reads          = 0;
	uint32_t words          = 0; // 2 (shader base) + user_words + reads
};

struct PipeHeader {
	uint64_t pipe_id  = 0;
	uint64_t spec[2]  = {}; // kind 1: vertex (or mesh), pixel (0 without one); kind 2: compute, 0
	uint32_t kind     = 0;  // 1 graphics, 2 compute
	uint32_t pod_size = 0;  // kind 1: PipelineRenderingState, PipelineVertexInputState, PipelineStaticParameters
};
#pragma pack(pop)

static_assert(sizeof(Word) == 6);
static_assert(sizeof(FileHeader) == 16);
static_assert(sizeof(BodyHeader) == 32);
static_assert(sizeof(SourceHeader) == 72);
static_assert(sizeof(SpecHeader) == 40);
static_assert(sizeof(PipeHeader) == 32);

// The fixture of the offline scanner (RC7 of the S16b review): one "ShaderReplayLayout: ..." line with every size and
// offset the scanner reads, printed by shader_cfg_tests.
std::string LayoutLine();
// Canonical form check of one word by its role (the rule the scanner implements); KEEP is always true.
bool WordCanonical(const Word& word);

// Ids (XXH3-64).
uint64_t SourceId(uint32_t stage, uint64_t hash, uint32_t user_data_count, uint32_t code_size,
                  std::span<const uint32_t> static_state);
uint64_t SpecializationHash(const ShaderRecompiler::IR::ResourceSpecialization& specialization);
uint64_t SpecId(uint64_t src_id, const ShaderRecompiler::IR::ResourceSpecialization& specialization,
                uint32_t push_start);

// Form K (item 524(e)): the stage input rebuilt from the static key - the port of VertexFromKey / PixelFromKey /
// ComputeFromKey of tests/S16dProbe.inc (1d8d9aa6). Every field the key holds; the rest keeps its default (no address,
// no record count, no vertex buffer); the vertex input of the pipeline comes from the POD of R-PIPE (K1(6)).
bool VertexFromKey(std::span<const uint32_t> s, ShaderType stage, ShaderVertexInputInfo& info, std::string& why);
bool PixelFromKey(std::span<const uint32_t> s, ShaderPixelInputInfo& pixel, std::string& why);
bool ComputeFromKey(std::span<const uint32_t> s, ShaderComputeInputInfo& compute, std::string& why);

// The recorded read path of one materialization (capture, under PipelineCache::m_mutex).
struct TraceRead {
	uint64_t address = 0;
	uint32_t value   = 0;
	uint8_t  clean   = 0;
	uint8_t  ok      = 0;
};
struct Trace {
	uint64_t               shader_base = 0;
	std::vector<uint32_t>  user_data;
	std::vector<TraceRead> reads;
	bool                   overflow = false;
};

// The recording runtime: forwards both readers to `inner` and appends every read to `trace`.
struct Recorder {
	const ShaderRecompiler::IR::SrtRuntime* inner = nullptr;
	Trace*                                  trace = nullptr;
	[[nodiscard]] ShaderRecompiler::IR::SrtRuntime Runtime();
};

// The synthetic runtime of the rebuild and of the self-check: the shader base and user data of the words, and both
// readers answer the next word of the path in order (the address is not looked at; a read past the path or through
// the other reader than recorded is a divergence and fails).
struct Replayer {
	explicit Replayer(std::span<const Word> words, size_t user_words);
	[[nodiscard]] ShaderRecompiler::IR::SrtRuntime Runtime();
	// After a materialization: every read consumed, none diverged.
	[[nodiscard]] bool Complete() const { return !diverged && next == reads.size(); }

	uint64_t                  shader_base = 0;
	std::vector<uint32_t>     user_data;
	std::vector<Word>         reads;
	size_t                    next      = 0;
	bool                      diverged  = false;
	std::vector<uint64_t>*    requested = nullptr; // optional: the addresses asked for (classification)
};

// Pending work of the writer thread.
struct SourceItem {
	uint64_t              src_id          = 0;
	uint64_t              hash            = 0;
	uint32_t              stage           = 0;
	uint32_t              user_data_count = 0;
	uint32_t              code_size       = 0;
	std::vector<uint32_t> static_state;
	std::vector<uint32_t> code;
	std::vector<uint32_t> back;
};
struct SpecItem {
	uint64_t                                     spec_id      = 0;
	uint64_t                                     src_id       = 0;
	uint32_t                                     stored_start = 0;
	// Immutable while the process lives: source entries of the program cache are never freed, and the writer is
	// joined before the program cache is destroyed; its compiled SRT was published by the capture's materialization
	// (under PipelineCache::m_mutex), which happens before the queue push (release) and the pop (acquire).
	const ShaderRecompiler::IR::ResourcePlan*    plan = nullptr;
	ShaderRecompiler::IR::ResourceSpecialization live;
	Trace                                        trace;
};
struct PipeItem {
	uint64_t             pipe_id = 0;
	uint32_t             kind    = 0;
	uint64_t             spec[2] = {};
	std::vector<uint8_t> pod;
};

// One catalogue in memory (writer thread, or the precache thread of the rebuild).
struct Catalogue {
	struct Source {
		SourceHeader          header;
		std::vector<uint32_t> static_state;
		std::vector<uint32_t> code;
		std::vector<uint32_t> back;
	};
	struct Spec {
		SpecHeader        header;
		std::vector<Word> words;
	};
	struct Pipe {
		PipeHeader           header;
		std::vector<uint8_t> pod;
	};
	std::vector<Source> sources;
	std::vector<Spec>   specs;
	std::vector<Pipe>   pipes;

	[[nodiscard]] const Source* FindSource(uint64_t id) const;
	[[nodiscard]] const Spec*   FindSpec(uint64_t id) const;
	void                        Index();

	std::unordered_map<uint64_t, uint32_t> source_index;
	std::unordered_map<uint64_t, uint32_t> spec_index;
	std::unordered_map<uint64_t, uint32_t> pipe_index;
};

// Counters of the capture line (S16a section 7) - written by the writer thread, read for the log line.
struct CaptureStats {
	uint32_t sources        = 0;
	uint32_t specs          = 0;
	uint32_t pipes          = 0;
	uint32_t canon_mismatch = 0; // self-check failed (canon_self) or an address word left as is (canon_residual)
	uint32_t canon_self     = 0;
	uint32_t canon_residual = 0;
	uint32_t canon_base     = 0; // the replay of the raw path did not give the live specialization (no record)
	uint32_t canon_big      = 0; // path longer than MaxPathWords (no record)
	uint32_t dropped_queue  = 0;
	uint32_t pipes_waiting  = 0; // R-PIPE whose R-SPEC is not in the catalogue yet (not written)
	uint64_t bytes          = 0;
	uint64_t generation     = 0;
};

class Writer;

// The catalogue folder and its generations (_ShaderCache/<title>/replay/).
class Store {
public:
	Store(std::filesystem::path directory, std::string compat);

	[[nodiscard]] const std::filesystem::path& Directory() const { return m_directory; }
	[[nodiscard]] const std::string&           Compat() const { return m_compat; }

	// Loads the current generation (or the previous one when the current is corrupt); state: "ok", "mismatch",
	// "absent" or "corrupt".
	bool Load(Catalogue& catalogue, std::string& state, uint64_t& generation, uint64_t& corrupt_generation);
	// Writes generation `generation` (temporary file and rename), then the pointer replay.cur the same way; keeps the
	// previous generation file and removes the older ones.
	bool Save(const Catalogue& catalogue, uint64_t generation, uint64_t& bytes);

	static bool Parse(const std::vector<uint8_t>& data, const std::string& compat, Catalogue& catalogue,
	                  uint64_t& generation, std::string& state);
	static std::vector<uint8_t> Serialize(const Catalogue& catalogue, const std::string& compat, uint64_t generation);

private:
	std::filesystem::path m_directory;
	std::string           m_compat;
};

// The capture side (KYTY_S_REPLAY 1 or 2): a lock-free single-producer ring (every producer holds
// PipelineCache::m_mutex, which serializes them), drained by one writer thread that canonicalizes, self-checks and
// publishes generations. Nothing on the producer side blocks, allocates a lock, reads or writes a file.
class Capture {
public:
	Capture(Store& store, Catalogue initial, uint64_t generation);
	~Capture();
	Capture(const Capture&)            = delete;
	Capture& operator=(const Capture&) = delete;

	// Producer side (holder of PipelineCache::m_mutex).
	void Push(std::unique_ptr<SourceItem> item);
	void Push(std::unique_ptr<SpecItem> item);
	void Push(std::unique_ptr<PipeItem> item);

	// Joins the writer after it drained the ring and saved the last generation.
	void Stop();

private:
	std::unique_ptr<Writer> m_writer;
};

// Canonicalization of one read path (writer thread; also used by the tests). Returns false when the path cannot be
// recorded; `why` = "base", "big", "self" or "residual". On success `words` holds the canonical path.
constexpr size_t MaxPathWords = 4096;
bool Canonicalize(const ShaderRecompiler::IR::ResourcePlan& plan, const Trace& trace,
                  const ShaderRecompiler::IR::ResourceSpecialization& live, std::vector<Word>& words,
                  size_t& user_words, std::string& why, bool canon_stand);

// The specialization of a plan for one canonical path (rebuild): MaterializeResources with the synthetic runtime;
// false when it fails or the path diverges (rej_shape).
bool Specialize(const ShaderRecompiler::IR::ResourcePlan& plan, const Catalogue::Spec& spec,
                ShaderRecompiler::IR::ResourceSpecialization& specialization);

// Number of groups of two or more plan resources with one (kind, first_use_pc) (S16e section 5; K4 print).
uint32_t SamePcGroups(const ShaderRecompiler::IR::ShaderInfo& info);

} // namespace Libs::Graphics::ShaderReplay

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINE_SHADERREPLAY_H_
