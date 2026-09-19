# Session 97 — route E, measurement M3 (continued) — FACTS

**This file is the only source of truth for session 97.** Anything not in it is not a result of
this session. A run that failed admission appears only as a replaced or failed run, and none of
its contrasts is quoted.

## 0. The three numbers route E opens with (`ROADMAP.md:1210-1212`)

* budget **≤ ~3.0 µs a draw** on a median frame, **≤ ~2.3 µs** on a p99 frame (7 284 draws);
* today **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms** (pinned p50 12.83 / p90 13.94 /
  p99 15.77);
* of M1–M5 still undone: **M3, M4, M5**.

**60 FPS is not promised** (~15 %, 8–25 %); nothing in this session moves it.

**The user's decision on the order** (asked first, `next-session-97.md` §0.1): **M3 → M4 → M5
stays as it is**, although M4's sealed rule closes only P, which M1 already closed.

## 0.1 What this session settled and what it did not

* **Settled — the synchronisation term at SUBMISSION granularity** (`bd96b`, admitted):
  **+103.5 ± 112.0 µs a flip, t = +1.85** — below the rule's 0.5 ms (P8 HIT). With `bd96a`'s
  label granularity (+2 893.6) both numbers now exist; **which one M3 uses is the user's choice.**
  The two were measured in DIFFERENT BDA regimes (`bd96a` NEW, `bd96b` OLD).
* **Settled — why `bindfloor` killed `bf96b`, and the fix works for that cause.** The gate was
  torn inside one draw (§2). With the per-op latch: **0 tears and 0 silent deaths in 486
  survived falling edges** (session 96: 2 deaths in 3 falling edges).
* **Settled — the floor's texture and buffer storms are gone** (R6 1 051 → 14–27 images, R7
  1 056 → 3 buffers over the two base flips after an edge).
* **NOT settled — reversibility.** A rarer failure remains: **3 GPU execution hangs in 489
  falling edges**, every one in the first base flip after a falling edge, at the same place in
  that flip (§5). No sealed proof passed on a counted attempt, so by the sealed stopping rule
  **nothing further was run on the floor**, **`F_st` does not exist, M3 is not closed, and G and
  R1 are neither closed nor licensed.**

## 1. Session 96's record of `bf96b` was wrong in three places

| FACTS s96 §4 says | the logs say |
|---|---|
| the run **froze** | both processes **died**: warmup + attempt took **157 s** against a **300 s** hold each; logs cut mid-line on a 4 KiB boundary; both stdouts lost their buffered tail |
| not reversible, deterministically | the **warmup survived** its first falling edge (1890) and died at its second (2010); the attempt died at its first. **2 deaths in 3 falling edges** |
| `bf_dlskip` **0** | **1** at flip 1841 (50 MiB, linear 10240×320) — and the warmup, with none, died anyway |

"No WER event" was never evidence: WER is disabled for the user (HKCU `Disabled=1`) and the
Application log holds zero kyty events since 2026-08-22. The VEH's 16-line budget for non-AV
exceptions is spent at startup in every run.

## 2. The mechanism of `bf96b`'s death — a gate torn inside one draw

Workflow `wf_a61503ed-82f`: five read-only investigators, a synthesis, three adversarial
skeptics per candidate; **candidate 1 survived 3 of 3, the other three were refuted 3 of 3.**
Inferred, not observed (no exit code was recorded then).

1. The schedule is applied on the **presentation thread** (`videoOut.cpp:1166` Present →
   `:1179` `Gates::Poll` → `gates.cpp` `ApplyText`, a relaxed `exchange`), unsynchronised with
   GuestGpu.
2. One draw read the gate **three** times: `ProgramCache::Get` (`pipelineCache.cpp:3119`),
   `ExecutePreparedDraw` (`renderDraw.cpp:2130`), `CommitBindings` (`descriptors.cpp:2854`); a
   dispatch likewise. Session 96's "read ONCE per draw" was true only inside each function.
3. Between the 2nd and 3rd read sat the burn (~17.5 of ~33 ms a flip). A falling edge there sent
   floor-prepared stages (`images`/`buffers`/`samplers` EMPTY) down the real branch →
   `descriptors.buffers.at()` → `std::out_of_range` → no catch on the `noexcept` `jthread` entry →
   `std::terminate` → `abort`, nothing flushed. A torn rising edge is harmless by construction.

## 3. The repairs — four patches, all behind the measurement gate except the crash reports

| patch | binary | what | why |
|---|---|---|---|
| `patch_s97.py` | `cb00d6fc…` (not run) | per-op latch; `PreparedBindings::floor` + `EXIT_IF`s; texture-GC keep-alive; sticky download skip; `bf_gc_hold`, `bf_edge`; `std::terminate` report | §2 |
| `patch_s97b.py` | **`be12a5e6…`** | terminate report per thread + global `SIGABRT` report, literal-first; LRU clock frozen; latch at the GC and compute-prefetch entries; comment fix | adversarial review `wf_731f12db-c67` of patch 1 found 3 defects of MY OWN edits before any run: the UCRT keeps `set_terminate` PER THREAD, the LRU clock kept ageing, the latch went stale outside ops |
| `patch_s97c.py` | **`c6fe36da…`** | buffer-GC keep-alive (`bf_bgc_hold`) | `rv97a`: ~1 056 buffers re-created after every falling edge |
| `patch_s97d.py` | `e80b1603…` (**built, NOT run**) | with `nullDescriptor`, the floor binds TRUE null descriptors (`bf_ndesc`); `Vulkan nullDescriptor:` log line | §5 candidate: floor stores polluted the SHARED 16-byte NULL buffer |

Commits: **`f26cb52`** (patches 1+B, before the floor runs), **`ee78f76`** (patch C, before
`rv97b`), and the closing commit of this session (patch D + records).

The first attempt at patch B put the `assert.h` declaration inside the NON-clang `#else` branch;
the clang-cl build failed on it and it was moved by hand (recorded in the script).

## 4. The harness

* **Port** `C:/kyty/s96/s97_port.py` — independent verification **PASS** on every requirement
  (`gates_base.txt` byte-identical, 1 092 B, 99 names, `00c116dc…0594d8`; five sealed `pred`
  into `prev96/pred/` with sizes and sha256 asserted; `pred/` empty). Remarks: the
  must-be-absent list carries a stale `pmlap` and lacks `bdabitscheck`; `stg92.py`, `bda93.py`,
  `shift91.py` point PRED into the empty `pred/`.
* **`s97_harness.py`**: the four carried scorers point at `prev96/pred/` (sha untouched);
  `guards.py` check 1 knows `--- Error ---` / `--- Fatal Error ---` / `--- std::terminate ---`
  (**`bf96a` died by EXIT and check 1 had PASSED it** — now FAIL) and FAILs a death inside the
  hold; `enter_scene.py` records `hold_exit`/`hold_s`.
* **`s97_bf96_repair.py`, `s97_bf96_repair2.py`**: `bf96.py` prints sealed C3/C6/C8/C10 for ever
  and decides by C3′, C6′, C8′, C10′, C10″; adds `E_net` and `W` to the readout.
* **`rv97.py`** (R1–R7), **`m3_97.py`** (the both-instruments verdict), **`accept97.sh`**.
* Dry runs on the session-96 fixtures found the C6/C8 defects before any number (§6).

## 5. Runs

| tag | binary | what | result |
|---|---|---|---|
| `bd96b` | `be12a5e6…` | `bdaevery=0\|1`, submission granularity | **ADMITTED**: criterion 3 VALID (split −0.001 %, 125/125), controls 6/6 (repaired set), P4/P5/P8 HIT |
| `rv97a` | `be12a5e6…` | proof, 10-flip ABBA, video | counted **4 of 6**, warmup 3 of 6: GPU hang after 116 / 98 falling edges |
| `hg97a` | `be12a5e6…` | diagnostic, `KYTY_GPU_CHECKPOINTS=1`, 4-flip ABBA | warmup hung **on ENTRY** (no schedule yet); attempt hung at a **rising** edge after 5 cycles; the breadcrumb holds only CPU-recorded EOP writes — useless |
| `rv97b` | `c6fe36da…` | proof again after patch C | counted **4 of 7** (hang after 76 falling edges); **warmup 7 of 7** (300 s, 196 falling edges) |

### 5.1 `bd96b` — the synchronisation term at submission granularity

`be_n` **8.00** a flip (P5 HIT), `be_ns` 1 088.5 µs a flip = 136.1 µs a call including the
render-mutex wait; endpoint **+103.5 ± 112.0 µs a flip, t = +1.85 on 125 pairs** (P4 HIT, **P8
HIT: below 500 µs**). BDA regime **OLD** in both arms (`buf_new` 1.456 / 1.454, unarmed
`bda_scan` 1 069 / 1 068 / 1 069 across windows); `prot_gpu_us` +11.5, `fbp_n` +4.1. Sealed C5
FAIL recorded (the known defect), C5′ PASS. `bd96a` (label granularity, +2 893.6 ± 93.2) ran in
the NEW regime — **the two numbers are from different regimes**, which the user's choice has to
weigh.

### 5.2 `rv97a` and `rv97b` — the proofs

|  | rv97a | rv97a warmup | rv97b | rv97b warmup |
|---|---|---|---|---|
| R1 survival | FAIL (276 s) | FAIL (249 s) | FAIL (214 s) | **PASS (300 s)** |
| R2 falling edges | 116 | 98 | 76 | **196** |
| R3 latch | 465 boundaries, 0 wrong (*) | 393, 0 wrong (*) | 305, 0 wrong (*) | **782, 0 wrong** |
| R4 dark base | PASS | PASS | PASS | PASS |
| R5 no readback | PASS | PASS | PASS | PASS |
| R6 images after an edge | 24 | 31 | 14 | 27 |
| R7 buffers after an edge | — (1 056 pre-patch C) | — | **3** | **3** |

(*) R3 failed only on the last flip of each dying log — the fatal edge's partner flip was never
written.

**The remaining failure.** All three deaths are a GPU **execution** hang in the **first base flip
after a falling edge**: `GpuWaitSlow`/`GpuHangAbort` `role=4 requested=known+1`, the CPU 87 ticks
ahead, zero backlogs, the hung submission waits on nothing, the GPU at **100 % / ~174 W** from
the edge until the abort, an **`nvlddmkm` event 153** in the System log at the same second
(TdrDelay is 60 s here, so no TDR fires), EXIT 321. The hung tick is ~20 submissions into the
flip, **~88–90 KB of log after the `GateArm` line in all three** — the same place in the frame.
Rate: **3 in 489 falling edges (~0.6 %)**; 0 in the rising edges of these runs; 0 in `bd96b`,
`pl96a`, `bd96a` (no floor). **Its signature equals the historical ENTRY hang's** (`role=4`,
`requested=known+1`, CPU 91–93 ticks ahead, zero backlogs; HANDOFF), and `hg97a`'s warmup hung
on entry in the same way.

Candidates (workflow `wf_724e89d5-00b`, four read-only lenses; ranked, none proven): a game
shader running away on data a transition frame left inconsistent — the same bug as the entry
hang, a floor edge being one more trigger (0.45–0.55). The loops lens names the only unbounded
memory-driven loops of the scene: the BVH traversal of four indirect async-compute ray-tracing
kernels (`0x503d7f066a496c3c`, `0x1f16e50eea0c89e3`, `0xff8ee744ffa4dcdc`, `0xf88d0f630ac5b35d`) —
exit only on sentinels read from memory, no step cap, the game's invalid-TLAS `S_TRAP` translated as
a no-op; the state lens adds per-pixel OIT lists (0.35). **The abort path could never name the
op: `masterSemaphore.cpp:113` calls `ReportGpuCheckpointHistory` (CPU ring), not
`ReportGpuCheckpoints` (GPU breadcrumb).** Further candidates: floor stores polluting the shared NULL
buffer the real path reads for degenerate V#s (0.12–0.20) — **patch D removes this one and is
built, not run**; floor draws rasterising garbage into real targets and history (0.12); buffer-GC
churn (0.12 before patch C — **patch C removed the churn and the hang stayed**).

### 5.3 The video pass (`rv97a`, 6 480 frames, the debt `bindfloor` owed since session 96)

Inside floor blocks the presented image is **frozen** (consecutive-frame difference 1.88 against
7.16 in base blocks): the final composite writes the display buffer through a storage binding
the floor replaced by a null image. **One frame per cycle — the second base flip after each
falling edge — shows what the floor drew into the intermediate targets** (materials black, sky
intact): the 140 one-frame glitches. The picture is allowed to break; this is the record of what
broke.

## 6. Sealed pre-registrations of this session — not to be edited

| file | bytes | sha256 |
|---|---:|---|
| `pred/01_floor_reversible.md` | 15 422 | `7df5beb55cd964f58cd79a6b0caa697089cd3b20ea546e80ab2b10644f7d43af` |
| `pred/02_floor_walk.md` | 12 151 | `9a88ab87a60789a2702bea4fb55939c6e578f25b4230482537361ee717f85519` |

`pred/01` added R1–R6 and C11–C16 and repaired three sealed controls of session 96's `pred/02`
that no run of the floor can pass: **C6** (the floor zeroes `bda_scan`), **C8** (at `bfmode=3`
the burn equalises `cpu_gpu_us`), **C10** (the gate flips before the flip's counters are read, so
every rising edge books burn into the last unarmed flip — 5 of 5 in session 96's logs). `pred/02`
added `bf97c` (the floor without the draw-ahead walk's M1 half), C3′, C10″, `E_net`, `W`, the
proof `rv97b` with R7, and the **both-instruments verdict** (§7). Its stopping rule fired:
`rv97b`'s counted attempt failed R1 ⇒ nothing further was run on the floor this session.

**Disclosures written into the sealed texts:** a dry run of `bf96.py` on the REPLACED `bf96b`
warmup printed a floor-arm net of 15 707 µs a flip; the review computed 14 149–14 530 µs for the
non-evicting blocks and ~2 ms of draw-ahead walk inside them. None is a measurement.

## 7. What the floor still carries — found before any `F_st` exists

The floor keeps the PM4 draw-ahead walk (~2 ms a flip on GuestGpu) and its four M1 workers
(~26 ms a flip of worker time), whose only consumer, `AheadTake`, it removed. That part of
`F_st` is **pessimistic**, while session 96's `pred/02` §1 rests CLOSE on `F_st` being only
optimistic. Sealed answer (`pred/02_floor_walk.md` §3): a second run `bf97c` with
`drawahead=0` in the floor arm, and **CLOSE only if `min(F_a, F_c) + 2.65 ≥ 15.5`, PROCEED only
if `max(F_a, F_c) + 2.65 ≤ 11.0`** — both branches strictly harder than before, neither easier.

## 8. Defects of this session's own work

1. Patch 1's terminate handler covered one thread (UCRT `set_terminate` is per thread); its GC
   keep-alive let the LRU clock age; its latch went stale outside ops — all three found by review
   before a run (patch B).
2. Patch B's `assert.h` anchor sat in the non-clang branch — the build caught it.
3. `pred/01`'s Q4 basis ("the repair does not touch the floor's work") and its 15 707 µs
   disclosure were wrong (the keep-alive removes eviction work); corrected in `pred/02` §1(c).
4. `pred/01` wrote "~450 falling edges" for a 10-flip ABBA; ABBA gives one falling edge per four
   blocks (~180). Fixed before sealing.
5. The `rv97b` command in `pred/02` carried no `--rec`, so `accept97.sh`'s `--video` step FAILs on
   it for a missing file — the video pass was taken on `rv97a`.

## 9. Not closed

* **`F_st`, and therefore M3, G, R1.** The floor survives hundreds of edges but not reliably:
  **a GPU execution hang at ~0.6 % of falling edges**, first base flip, same place in the frame,
  same signature as the historical entry hang.
* **Patch D** (true null descriptors) — built (`e80b1603…`), not run; it removes one candidate.
* The **decisive diagnostic** is still missing: the op that runs away. The checkpoint breadcrumb
  does not name it (CPU-recorded only) and the checkpoint mode itself hangs on entry.
* The **granularity choice** of the synchronisation term (label +2 893.6, NEW regime; submission
  +103.5, OLD regime) — the user's.
* The general hazard: **any gate read more than once inside one op can tear**, because gates flip
  on the presentation thread. `bindfloor` is fixed; no other gate was audited.
* Carried: M4, M5; `PrefetchComputePipelines` 245 µs a call; the 1 921.6 µs residue outside the
  mutex; the BDA regime; the written `bc_ok` slots; `C_bda` in NEW; the GPU side of `bdaall`; the
  single-chunk notify; the `ObtainBuffer` ring timer; `pfhint`/`pfcap`/`dapin` with the pin;
  route B.
