#pragma once

#include "graphics/shader/recompiler/ir/Type.h"

#include <cstddef>
#include <cstdint>
#include <string_view>
#include <type_traits>

namespace Libs::Graphics::ShaderRecompiler::IR {

enum class ValueOpcode {
#define VALUE_OPCODE(name, ...) name,
#include "graphics/shader/recompiler/ir/opcodes/ValueOpcodes.inc"
#undef VALUE_OPCODE
	Count,
};

enum class BufferAccess { None, Read, Write, Atomic };
enum class SharedAccess { None, Read, Write, Atomic, Append, Consume };
enum class AddressAccess { None, Read, Write };
enum class ImageAccess { None, Read, Write, Atomic };
enum class ImageResourceClass { None, Sampled, Storage };

struct AddressOpcodeInfo {
	AddressAccess access    = AddressAccess::None;
	uint32_t      data_bits = 0;
};

struct ImageOpcodeInfo {
	ImageAccess        access         = ImageAccess::None;
	ImageResourceClass resource_class = ImageResourceClass::None;
	bool               needs_sampler  = false;
};

struct DppMoveFlags {
	uint16_t control        = 0;
	uint8_t  row_mask       = 0xf;
	uint8_t  bank_mask      = 0xf;
	bool     fetch_inactive = false;
	bool     bound_control  = false;
};
static_assert(sizeof(DppMoveFlags) <= sizeof(uint64_t));
static_assert(std::is_trivially_copyable_v<DppMoveFlags>);

struct PermlaneFlags {
	bool x16            = false;
	bool fetch_inactive = false;
	bool bound_control  = false;
};
static_assert(sizeof(PermlaneFlags) <= sizeof(uint64_t));
static_assert(std::is_trivially_copyable_v<PermlaneFlags>);

struct MemoryFlags {
	uint32_t index = 0;
	uint32_t pc    = 0;
};
static_assert(sizeof(MemoryFlags) == sizeof(uint64_t));
static_assert(std::is_trivially_copyable_v<MemoryFlags>);

struct ExportFlags {
	uint32_t index = 0;
	uint32_t pc    = 0;
};
static_assert(sizeof(ExportFlags) == sizeof(uint64_t));
static_assert(std::is_trivially_copyable_v<ExportFlags>);

// Track M, M7a (T306, KYTY_M_T306; ROADMAP s122 items 762(b), 767(g)): the flags of the SelectU32(exec of the sample,
// offset dword, 0) that Translator::IMAGE_SAMPLE hands over for the texel offset of IMAGE_SAMPLE_*_O. The emitter
// (MResolveSampleOffset) takes a select as that wrapper only with these flags: under a constant lane mask (the entry
// EXEC of a non-pixel stage, s_mov_b64 exec, -1) constant propagation folds the wrapper away, and the write of the
// offset under another mask, SelectU32(mask, immediate, old), then stood in its place and was read as the wrapper.
inline constexpr uint64_t MSampleOffsetWrapperFlags = 0x0000003630335447ull; // "GT306"

[[nodiscard]] Type              TypeOf(ValueOpcode opcode);
[[nodiscard]] Type              ArgTypeOf(ValueOpcode opcode, size_t index);
[[nodiscard]] size_t            NumArgsOf(ValueOpcode opcode);
[[nodiscard]] bool              HasSideEffects(ValueOpcode opcode);
[[nodiscard]] BufferAccess      BufferAccessOf(ValueOpcode opcode);
[[nodiscard]] uint32_t          BufferComponentCount(ValueOpcode opcode);
[[nodiscard]] SharedAccess      SharedAccessOf(ValueOpcode opcode);
[[nodiscard]] uint32_t          SharedComponentCount(ValueOpcode opcode);
[[nodiscard]] AddressOpcodeInfo AddressOpcodeInfoOf(ValueOpcode opcode);
[[nodiscard]] ImageOpcodeInfo   ImageOpcodeInfoOf(ValueOpcode opcode);
[[nodiscard]] std::string_view  ValueOpcodeName(ValueOpcode opcode);

} // namespace Libs::Graphics::ShaderRecompiler::IR
