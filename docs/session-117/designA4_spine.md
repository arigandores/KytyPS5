# Route A, stage 4, part 1 — the shadow spine: can a second pass over PM4 reproduce the register state, and what does it cost?

Session 117. Written from reading the code (HEAD `a430787`, sources = the installed build `d3a981a2` plus docs only)
before any line of it is written. Tags: **[I]** read from source, **[M]** measured in a named run, **[U]** unknown.

## 0. What part 1 answers, and what it leaves to part 2

Route A (`docs/DESIGN_82_parallel.md`, re-reviewed for "maximum FPS" in `docs/session-104/designA_review.md` §3) splits
the command stream into slices executed by N recording contexts. Each slice needs the **full register state at its
start**, which only a sequential pass over the stream can give: the *spine*. Stage 4 of the review measures the spine in
shadow before any context exists. Part 1 (this session) measures the two things the rest of the route cannot survive
without:

- **K5 (feasibility):** the spine reproduces, at every draw and dispatch, exactly the register state the real command
  processor sees there — `spine_bad = 0` over a whole scene run;
- **K1 (price):** `spine_us`, the decode cost per frame, against the sealed 1 200 µs.

Part 2 (next session, only if part 1 passes): the pass histogram (K3) and the image overlap of adjacent segments (K4),
which need hooks in the render path, not in the command processor.

## 1. Why a second `CommandProcessor` is enough [I]

Every register handler in `pm4Handlers.cpp` is a free function over `CommandProcessor&` and touches only that object's
state: across the file the handlers call `cp.GetCtx()` 182 times, `cp.GetShCtx()` 38, `cp.GetUcfg()` 16,
`cp.Set/GetUserDataMarker()` 18, `cp.SetIndex*`/`SetNumInstances`/`Set*IndirectArgsBaseAddress` and
`cp.ApplyContextStateOperation()`. `HwCtxTrySetFakeRegister` keeps no state. So a **second `CommandProcessor` object** (same
`RenderContext&`, never asked to draw) run through the **same opcode handlers** for the register packets reproduces the
register state by construction — the spine does not re-implement a single register.

What must NOT be called on the shadow, because it reaches outside the object:
`CpOpIndirectBuffer`/`CpOpBranch` (they call `cp.ProcessIndirectBuffer`, which pushes onto `g_current_execution` — the
REAL execution), every draw/dispatch handler, `WRITE_DATA`/`COPY_DATA`/`DMA_DATA`, EOP/EOS/event packets, waits, CE/DE
counters, const RAM, flips and the other `R_*` markers except `R_CONTEXT_STATE`. The spine follows indirect buffers and
evaluates `COND_EXEC` and the 14-dword branch itself, reading the same memory the handlers read.

## 2. The instrument (measurement only)

**Knob `spine`** (`KYTY_SPINE`, 0..2, default 0, the LAST line of `KNOB_DEFINITIONS`; nothing under
`src/graphics/shader/**`). Read once per submission, when the submission starts (the place where
`CommandProcessor::Process` pushes the first cursor and calls `PrefetchComputePipelines`), and latched into
`Pm4Execution`, so a schedule flip cannot give one submission two modes.

- **0** — nothing (one knob read per submission).
- **1 — plan:** before the first packet of the submission is executed, on the GuestGpu thread, the spine processor is
  seeded from the real one (`m_ctx`, `m_saved_ctx`, `m_context_state_pushed`, `m_ucfg`, `m_sh_ctx`, the user-data marker,
  the index/indirect-base registers, `m_num_instances`, `m_predicate_skip`) and walks the whole submission:
  - packets `0x80000000` skipped; a packet with header bit 0 is skipped while the SPINE's predicate says skip (the same
    test as `ProcessPm4Range`);
  - **applied through the real handler on the shadow:** `SET_CONTEXT_REG`, `SET_SH_REG`, `SET_UCONFIG_REG(_INDEX)`, the
    three `*_REG_INDIRECT`, `CLEAR_STATE`, `SET_BASE`, `INDEX_TYPE`, `INDEX_BASE`, `INDEX_BUFFER_SIZE`,
    `NUM_INSTANCES`, `SET_PREDICATION`, and `IT_NOP` with `R_CONTEXT_STATE`;
  - **followed by the spine:** `INDIRECT_BUFFER` (4 dwords: push; 14 dwords: evaluate the branch like `CpOpBranch`,
    push the taken buffer — `spine_cf_br`), `COND_EXEC` (read the word like `CpOpCondExec`, skip `exec_count` —
    `spine_cf_cond`);
  - **elements:** `DRAW_INDEX_2`, `DRAW_INDEX_OFFSET_2`, `DRAW_INDEX_AUTO`, `DRAW_INDIRECT`, `DRAW_INDEX_INDIRECT`,
    `DRAW_INDIRECT_MULTI`, `DRAW_INDEX_INDIRECT_MULTI`, `DISPATCH_DRAW_PREAMBLE`, `DISPATCH_DIRECT`, `DISPATCH_INDIRECT`
    — counted in order (`spine_el`); indirect ones also `spine_cf_ind` (their arguments are read at execution);
  - everything else advanced by its length; an opcode with no handler in `g_cp_op_func` ends the plan
    (`spine_abort`).
  Counters: `spine_n` (plans), `spine_ns` (wall of the plan pass minus digest time, raw ns), `spine_pk` (packets),
  `spine_el`, `spine_ib`, `spine_cf_br`, `spine_cf_cond`, `spine_cf_pred` (`SET_PREDICATION` packets), `spine_cf_ind`,
  `spine_abort`.
- **2 — plan and verify:** as 1, plus a 64-bit digest of the shadow's register state before every element, stored in
  the execution; the real `ProcessPm4Range` computes the same digest of the REAL state before the handler of each
  element packet and compares in order: `spine_cmp`, **`spine_bad`**, `spine_dig_ns` (digest time on both sides, raw
  ns); a submission whose real element count differs from the plan at completion is `spine_misal`. The first 40
  mismatches print `SpineMismatch: sub= el= op= part=ctx|ucfg|sh|cp off=` (the first differing byte).

**Digest.** XXH3-64 over copies of `HW::Context`, `HW::UserConfig`, `HW::Shader` and the CP registers above except
`m_num_instances` (indirect draws rewrite it from GPU-written arguments — counted, not compared). The structures hold
127 `bool`s, so raw bytes carry padding: the copies are hashed after `__builtin_clear_padding` if the compiler has it
(clang 19.1.5 — checked by compiling before the patch); otherwise padding is a known false-mismatch source and part 1
reports mismatches by offset, and a mismatch confined to padding bytes of one struct type is not a state mismatch.

**Price.** Mode 2 hashes ~7 KB twice per element, ~5 400 elements a frame — milliseconds a frame; it is a verify run,
not a speed run. `spine_ns` excludes digest time by construction (separate lap).

## 3. The sealed run (to be sealed before it runs)

One Sky Garden entry on the new build, 300 s, pinned, no video; schedule ABBA `spine=1 | spine=2` (both arms plan, so
the knob's own flip is the only difference); scorer derived from `obs116` (whole-line anchors). Verdicts:
- **K5:** `spine_bad = 0` and `spine_misal = 0` over all arm-2 blocks, with `spine_cmp` ≥ 0,9 × elements (the compare
  armed) ⇒ PASS; any mismatch ⇒ FAIL, and the mismatch lines name what the spine cannot reproduce;
- **K1:** mean `spine_ns` per frame in arm-1 blocks ≤ 1 200 µs ⇒ PASS; above ⇒ FAIL **on the GuestGpu thread** — and
  then the report says whether it would fit on the `dawalk` walker thread (walker's own `da_walk_us` + `spine_ns` < frame
  time), because in route A the spine may run there (the walker already decodes every submission at enqueue);
- admission as `obs116` (build, pin, env, idle, markers, rows, arming: `spine_n` ≈ submissions, `spine_el` ≈ draws +
  dispatches ± the skipped predicated ones).
**Consequences (fixed now):** K5 FAIL ⇒ route A stops at stage 4 until the named hazard has a design, recorded before
any code; K5 PASS and K1 PASS ⇒ part 2; K5 PASS and K1 FAIL on both threads ⇒ route A closed for maximum FPS (the spine
does not fit anywhere). Nothing ships from this stage.

## 4. What this cannot see

The spine is seeded from the real state at every submission start, so it proves reproduction WITHIN a submission, not
the carry of state across submissions a walker-side spine would need (the walker carries per-queue state, which part 2
can compare at submission starts). Memory the GPU rewrites between plan and execution (indirect register tables,
`COND_EXEC` words, predicates) shows up as mismatches only when it changes state that later elements see.
