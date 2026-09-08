#pragma once

#include "graphics/shader/recompiler/ir/Block.h"

#include <cstdint>

namespace Libs::Graphics::ShaderRecompiler::IR {

struct PredicationStats {
	// "exec ? new : old" selects whose result only feeds values that are themselves discarded
	// for inactive lanes; replaced by the unpredicated value.
	uint32_t removed_selects = 0;
	// Select(p, b, Select(p, a, c)) chains folded to Select(p, b, c).
	uint32_t folded_chains = 0;
};

// Every VGPR write is translated as `Select(exec, new, old)` so that lanes disabled by EXEC keep
// their register contents. Most of those values are temporaries whose only consumers are other
// VALU operations that are predicated by the same EXEC value: for an inactive lane the consumer's
// result is discarded anyway, so the temporary may hold garbage and the select is dead weight
// (SEL/FSEL + MOV made up ~25 % of NVIDIA SASS in ASTRO BOT's lighting compute shader).
// Values that reach a phi, a memory or image operation, a subgroup operation (read lane etc.) or
// any select under a different predicate keep their selects.
// `preserve_liveness`: fold a select chain only when the value it keeps alive is live past the
// outer select anyway. Without it the block-entry value of every register rewritten in a block
// stays live up to the block's last write to it; on NVIDIA that pushed the lighting compute
// shader of ASTRO BOT from 128 to 181 registers (one workgroup per SM, +50 % time) while pixel
// shaders were unaffected, so KYTY_PRED_LIVE=1 (default) preserves liveness in compute shaders
// only; 0 = never (full folding everywhere), 2 = every stage.
[[nodiscard]] PredicationStats EliminatePredication(const BlockList& blocks, bool preserve_liveness);
[[nodiscard]] bool             PredicationPreserveLiveness(bool compute_stage);

// KYTY_PRED_ELIM=0 disables the pass (not part of the translation-cache key).
[[nodiscard]] bool PredicationEliminationEnabled();

} // namespace Libs::Graphics::ShaderRecompiler::IR
