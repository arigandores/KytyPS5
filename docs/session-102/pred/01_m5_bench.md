# Sealed pre-registration 01 — session 102, route E, M5: the GPU price of BDA/LDG on the top shaders

**Immutable once written.** A correction goes into a new sealed addendum, never into this file.
Written **before** the capture this bench needs, before any variant module is compiled by the
driver, and before any timing, register count or SASS listing of any shader named in §2 is read.
The operationalisation below was recorded in `docs/ROADMAP.md` §2 E (under M5) **first**.

---

## 0. The rule, and what this file does and does not change

`ROADMAP.md` §2 E, M5, verbatim: *«M5 — цена BDA/LDG на GPU (стенд, без прогона игры).
`KYTY_RECOMPILE` + `rd_cs_time.py` на топовых шейдерах. **Правило: > +6 % на топ-позициях GPU ⇒ G
закрыт.**»* The design source (`C:/kyty/s94/rewrite94/judge.md` §4, M5): *"recompile the top
shaders with read-only V# through BDA (`KYTY_RECOMPILE` + `rd_cs_time.py`). Rule: > +6 % on the top
GPU items ⇒ G closed. Answers U6."*

**The threshold (+6 %) and the branch (G closed) are not touched.** This file fixes only what the
rule leaves open and `docs/next-session-102.md` §1 delegates to the executor: the shader set, the
variant set, the estimator, the number of repetitions and what counts as a valid bench run.

Three facts found by reading, each of which shapes the protocol:

1. **Every stand capture is gone** (`kyty_1788790344792548`, `…1788813383972010`,
   `…1788888064175999`, `…1788894857451170`), and the nine captures on disk (sessions 31–49) were
   taken by a translator 13 commits older than the current one (signatures `1693ffd`/`8347ce22` →
   `2db9065a` today). A recompile of today's translator would number SRT slots and bindings
   differently from those captures, and the stand then returns **wrong times without an error**
   (`HANDOFF.md` §2.24, :5989-5998). **So M5 needs one fresh capture.** Taking it is a game run; it
   is a capture, not a measurement, and by the user's instruction of session 102 it happens at the
   end of the session together with every other game run.
2. **A BDA shader needs two bindings the base layout of a non-DMA stage does not have** — the page
   table (`NativeBinding(stage, BdaPagetable)` = 46 + 51·group) and the fault buffer (47 + 51·group),
   added only when `uses_dma` (`BindingLayout.cpp:132-135`). RenderDoc replacement keeps the
   captured pipeline layout, so a BDA variant of a graphics shader cannot run on an ordinary
   capture. **The capture is therefore taken with a new HOST-ONLY environment key
   `KYTY_DMA_LAYOUT=1`** (read once per process, default off, measurement only): every stage of every
   pipeline layout carries those two bindings and the host writes their descriptors, while the
   translator — and so the translation cache and every base shader module — is unchanged.
3. **The stand replaces a pixel or a compute shader only**, and `KYTY_RECOMPILE` rejects vertex-fetch
   VS and mesh shaders (`shaderCfgTests.cpp:13724-13748`). **M5 therefore prices PS and CS.**

---

## 1. What is measured, and why it is a LOWER bound

G's shader side (`C:/kyty/s94/rewrite94/gpu-driven.md` §3, V2) reads buffers through the BDA page
table instead of descriptors, fetches V#s at run time with emulated bounds/stride/swizzle/format,
chases SRT pointers through BDA, and reads constants through BDA instead of the const bank.

The variant measured here (**V2**, §3) keeps, of that list: page-table BDA for every read-only
buffer load and every constant load, the V# taken **at run time** from the value the base shader
already holds (push data or the flattened-SRT slot), run-time bounds against `num_records`, and a
run-time stride for indexed loads. It omits: SRT pointer chasing through BDA (the V# comes from the
host-flattened slot, one SSBO load, instead of a dependent BDA chain), run-time format decode
(formatted loads stay on descriptors), and every VS/mesh stage.

**Every omission removes cost.** So V2 is a **lower bound** on G's shader-side price, and the two
branches of the rule read differently:

* **> +6 % ⇒ G CLOSED** holds a fortiori — the true price is at least this.
* **≤ +6 % ⇒ "M5 does not close G at its lower bound."** G then survives **unlicensed**, with the
  omitted terms named as [U]; it is not evidence that the true price is ≤ 6 %.

M5 prices term U6 only. It says nothing about the other GPU terms of `gpu-driven.md` §5 (barriers at
guest sync events, mid-frame uploads, eager DCC/HTILE) or about any CPU term.

---

## 2. The shader set — fixed here, by hash, from the recorded population

Source: `C:/kyty/s72/log_gpt72a.txt`, Sky Garden, `KYTY_GPU_TIME=1`, 2 745 joined frames from 2100,
scored by `python C:/kyty/s72/gputime.py <log> --first-frame 2100 --top 40`; the output is saved at
`C:/kyty/s102/m5/top_gpt72a.txt` (5 698 B). Rows of the same PS under different VS are summed. Only
programs the stand can replace are eligible (PS, CS). The ten largest, in order:

| item | stage | hash | µs/frame (gpt72a) | share of non-idle 15 396.7 |
|---|---|---|---:|---:|
| S1 | CS | `56a15431999c5a2d` | 1 009.1 | 6.55 % |
| S2 | PS | `746c68bba46b2b49` | 493.0 (275.3 + 217.7) | 3.20 % |
| S3 | PS | `3d705c1b57adec00` | 473.2 | 3.07 % |
| S4 | PS | `2e2ae33a4d374e8f` | 428.9 | 2.79 % |
| S5 | PS | `b96c2898f05637df` | 373.9 | 2.43 % |
| S6 | CS | `173677e49330bd65` | 373.5 | 2.43 % |
| S7 | CS | `3276e23cce1be33c` | 361.4 | 2.35 % |
| S8 | PS | `7a46be05e11e081b` | 359.1 | 2.33 % |
| S9 | PS | `ca11de665702d6d9` | 349.9 | 2.27 % |
| S10 | PS | `c924afb0821b68c8` | 286.0 | 1.86 % |

Sum 4 508.0 µs/frame = **29.3 % of non-idle GPU and 41.3 % of draw + dispatch time** of that run.
Not eligible and excluded by construction: the depth-only VS `70c651c06dbbf1ce` (237.8, no PS), the
mesh halves of S2/S8, every VS half of every draw (the draw's EventGPUDuration still includes its
VS; only the PS is replaced). Every item has a GCN dump in `_Shaders/gcn/` and a translation-cache
file with the current signature `KytySC3:2db9065a…`.

**No substitution.** An item absent from the capture is reported absent; the next-ranked program is
**not** promoted into its place.

---

## 3. The arms

Each arm is a set of replacements applied to **all present items at once** (every captured module
that belongs to an item, §5 V-c) for one counter fetch.

* **B** — no replacement: the capture's own modules.
* **A** — the base recompiled: `KYTY_RECOMPILE` of the item's GCN with its cache file and the
  permutation whose SPIR-V md5 equals the captured module's, **no switch**. The reference arm of
  every ratio. (If the md5 matches, A and B are the same bytes and A measures only the replacement
  mechanism.)
* **V1** — `KYTY_RECOMPILE_CBANK=0`: const-bank loads (LDC) become SSBO loads (LDG). Graphics only;
  for CS it is byte-identical to A (compute already reads constants through SSBO). **Secondary:**
  the cheapest term of G, with no page table.
* **V2** — the decisive arm, `KYTY_RECOMPILE` with the new harness switch that rewrites, in the IR
  between translation and compilation (`tests/shaderCfgTests.cpp`, no `src/graphics/shader` change,
  so the translator hash does not move): every `ReadConstBuffer` and every `LoadBuffer*` whose buffer
  is not written, not atomic and not a formatted load, into a load of `base(V#) + byte offset`
  through the BDA page table (`get_bda_pointer`, null-page variant as shipped), where `base` is
  (d0, d1 & 0xffff) of the V# **at run time**, the byte offset is the one the base computes, the
  stride of an indexed access is read from the V# at run time, and an access whose byte range lies
  outside `num_records` (d2) reads 0. The V# dwords are kept alive (`ReferenceU32`) so the push-data
  layout is unchanged. `uses_dma` is set, which declares exactly the two bindings `KYTY_DMA_LAYOUT`
  put into the captured layout.

If the implementation of V2 cannot meet a clause above (for example the run-time stride), the
deviation is sealed in an addendum **before** any V2 module of an item in §2 is timed, and it is
named as a further omission in §1's list.

---

## 4. Capture protocol

* The binary installed at capture time is the session-102 build; its sha256 goes into the run's
  `<tag>.json`. `shader_cfg_tests.exe` is built from the **same** commit, and the kytyGitVersion
  shader-source hash of both builds is `2db9065a…` (the translator is not edited in this session).
* Scene: `python C:/kyty/s102/enter_scene.py m5cap102 --hold <≥150> --attempts 1 --no-install
  --gates-file C:/kyty/s102/gates_base.txt` with the RenderDoc flag passed through to the emulator,
  and positionally `KYTY_DMA_LAYOUT=1 KYTY_GPU_CLOCK_PIN=1 KYTY_RD_TIME=<s> KYTY_RD_FLIPS=2` plus the
  gate `bdaall=1` (freshness of the BDA mirrors for every buffer slot a V2 load may read). No
  `KYTY_GPU_CHECKPOINTS`, no `KYTY_GPU_TIME`, no `KYTY_REC`.
* Acceptance of the capture: the log carries `DmaLayout: mode 1` and `GpuClockPin: mode 1`; the
  `.rdc` opens; `rd_find`-style module listing contains at least one module of at least seven items.
  One further capture attempt is allowed only for a **technical** failure (crash, empty capture,
  capture file does not open); never because of anything measured.

---

## 5. Bench protocol and estimator — fixed here

* Driver/GPU state: nothing else on the GPU (`nvidia-smi --query-compute-apps` shows no other
  process with dedicated memory); clocks and temperature logged every 5 s for the whole bench.
* One `qrenderdoc --python` process. Build every module of every arm first. **Two warm-up fetches**
  with arm B, discarded. Then **R = 12 rounds**; each round measures every arm once, in the order of
  a Williams design for four arms (sequences `B A V1 V2`, `A V2 B V1`, `V1 B V2 A`, `V2 V1 A B`,
  cycled), so first-order carry-over and drift are balanced. A measurement = apply the arm's
  replacements, one `FetchCounters([EventGPUDuration])`, remove the replacements. If one fetch takes
  longer than 10 min, R drops to the largest value that fits a 4-hour bench, **never below 8**.
* Per round r, arm X, item i: `T[X,i,r]` = the sum of EventGPUDuration over the item's events in the
  capture. `S[X,r]` = Σ over valid items (§6) of `T[X,i,r]`.
* **Primary statistic:** `ρ = median_r ( S[V2,r] / S[A,r] )`, `Δ = ρ − 1`, with a 90 % two-sided
  percentile bootstrap over rounds (20 000 resamples, seed 102). Reported beside it, never deciding:
  the same for V1, per-item `median_r(T[X,i,r] / T[A,i,r])`, and `median_r(S[A,r]/S[B,r])`.
* **Verdict:**
  * **CLOSE** — the 90 % interval of Δ lies wholly above +0.06 ⇒ **G closed.**
  * **NOT CLOSED** — the interval lies wholly at or below +0.06 ⇒ M5 does not close G (at its lower
    bound, §1); G survives, unlicensed.
  * **INCONCLUSIVE** — the interval straddles +0.06 ⇒ **one** extension of 12 more rounds in the
    same design, same process if possible; then the point Δ over all rounds decides (> 0.06 ⇒ CLOSE,
    else NOT CLOSED), published as *decided at the point after extension*.

---

## 6. Validity — every limit fixed here

* **V-a Capture.** §4 acceptance holds; the bench opens exactly that `.rdc` (sha256 recorded).
* **V-b Coverage.** At least **7 of the 10** items present in the capture, carrying at least **60 %**
  of the §2 weight. Otherwise **INVALID**.
* **V-c Identity.** A captured module belongs to an item when its SPIR-V md5 equals the md5 of arm A
  for one permutation of that item's cache file. A module of an item's hash that no permutation
  reproduces is **excluded** (its events are not summed) and reported. If exclusion removes more than
  **40 %** of the present items' A-arm time → **INVALID** (the stand does not reproduce the capture).
* **V-d Mechanism noise.** `median_r(S[A,r] / S[B,r])` within **[0.97, 1.03]**. Otherwise INVALID.
* **V-e Output equality — the control that makes a timing mean anything.** For each valid item and
  each of V1 and V2, with **only that item** replaced, the item's outputs at its **last** event in
  the capture are compared with arm A's: every colour and depth target bound at that event for a PS
  item; every read-write image and buffer bound at that event for a CS item. **Bit-equal** or the
  item fails for that variant. A failing item is removed from **that variant's** sums (both numerator
  and denominator) and reported. If the failing items carry more than **40 %** of the valid A-arm
  time for V2 → **V2 INVALID ⇒ M5 NOT DECIDED this session**.
* **V-f** `spirv-val --target-env vulkan1.3` passes for every module of every arm.
* **V-g Technical completion.** Every fetch returns a value for every event of every valid item.
  A bench that crashes may be restarted from scratch once; a completed bench is never re-run.

**Reported for every module, never deciding** (the brief's register trap): driver Register Count,
Local Memory Size and Binary Size from `pipestat`, SASS instruction count, LDG/LDC/LDS/LDL/STL counts
from `s16_sass.py --stats`, for A, V1 and V2. An occupancy step is reported as part of the price, not
excused.

---

## 7. Predictions — fixed here, carrying no decision weight

* **P1.** V1 aggregate Δ in **[−0.01, +0.05]** — session 18 measured +1…+7 % per graphics shader on
  another translator, and V1 is identical to A on the three CS items (≈ 39 % of the set's weight).
* **P2.** V2 aggregate Δ in **[+0.02, +0.20]**.
* **P3.** V2 raises at least one PS item's register count above its A count.
* **P4.** V-e: at least 8 of the present items pass for V2.

A MISS is published beside the HITs and never repaired; none of P1–P4 is re-registered later.

---

## 8. What no outcome of this file may be used to claim

That the rule was changed · that M5 was run without a game run (a capture run was taken, §0.1) ·
that VS, mesh, SRT chasing, run-time format decode, barriers or uploads were priced · that a
NOT-CLOSED result licenses G or shows its price is ≤ 6 % · that a CLOSE says anything about CPU,
about 60 FPS being unreachable, or about F, P or R1 · that `KYTY_DMA_LAYOUT` or `bdaall` is a shipped
path (both are measurement-only, default off) · **any speedup or frame-rate gain.**
