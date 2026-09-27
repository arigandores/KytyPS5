#ifndef EMULATOR_SRC_COMMON_RK3CENSUS_H_
#define EMULATOR_SRC_COMMON_RK3CENSUS_H_

#include <cstdint>

// Session 126, knob "rk3cen" (MEASUREMENT ONLY, docs/session-126/design126.md rev 2, ROADMAP s122 items 63, 64, 67): the
// hot half of the K3 census - the per-draw latch and the hooks of the HW::Context setters whose registers the target
// resolution reads (design s.3.1, groups per [RC1]).  The generations live OUTSIDE HW::Context, in a table of the GuestGpu
// thread (renderDraw.cpp): no member of HW::Context is added, removed or moved ([RC8]).  At rk3cen = 0 a hook is one
// thread-local test.
namespace Common::Rk3 {

// Register groups (ROADMAP s122 item 64(b)).
inline constexpr uint32_t GroupMask  = 0;  // CB_TARGET_MASK
inline constexpr uint32_t GroupSlot0 = 1;  // CB_COLORn_*: GroupSlot0 + n, n = 0..7
inline constexpr uint32_t GroupDact  = 9;  // DB_DEPTH_CONTROL, DB_RENDER_CONTROL, DB_STENCIL_INFO
inline constexpr uint32_t GroupDepth = 10; // the other D_census registers of DB (DB_SHADING_RATE_ENCODING included, [RC6])
inline constexpr uint32_t GroupCount = 11;
inline constexpr uint32_t DSetters   = 29; // hooked setters: 12 colour + 1 mask + 3 G_dact + 13 G_depth

// The value latched for the draw in flight (0 = off).  Written only by the draw-entry latch, which arms only on the
// GuestGpu thread, so on every other thread it stays 0 and a hook there does nothing.
inline constinit thread_local uint32_t t_rk3 = 0;

void NoteWriteCold(const void* ctx, uint32_t group) noexcept; // renderDraw.cpp
void NoteObjectCold(const void* ctx) noexcept;                 // renderDraw.cpp

// C1: a setter of group `group` wrote the context `ctx`.
inline void NoteWrite(const void* ctx, uint32_t group) noexcept {
	if (t_rk3 != 0) [[unlikely]] {
		NoteWriteCold(ctx, group);
	}
}
// C1: a CB_COLORn_* setter of slot `slot` (group G_slot[slot]).
inline void NoteSlot(const void* ctx, uint32_t slot) noexcept {
	if (t_rk3 != 0) [[unlikely]] {
		NoteWriteCold(ctx, GroupSlot0 + slot);
	}
}
// C2: the whole object was written (Reset, R_CONTEXT_STATE Pop): every group moves.
inline void NoteObject(const void* ctx) noexcept {
	if (t_rk3 != 0) [[unlikely]] {
		NoteObjectCold(ctx);
	}
}

} // namespace Common::Rk3

#endif // EMULATOR_SRC_COMMON_RK3CENSUS_H_
