# Sealed addendum 03 — session 100: the CLOSE of `pred/02` is WITHDRAWN

**Immutable once written.** `pred/01_addend_census.md` and `pred/02_moved_mark.md` are NOT edited;
they stand exactly as sealed, and so do the runs scored under them. This file records that the
**rule** of both seals is defective, states what the defect is, and restates the session's
verdict. It is written after an adversarial audit and after the defects were verified against the
sources by hand.

---

## 0. What is withdrawn

**"G and R1 are closed" is withdrawn. M3 remains GAP.** The arithmetic published under
`pred/02` (ADDEND 2.918040 / 2.916948, VERDICT_INPUT 15.743040…17.192040) is not disputed as
arithmetic — an independent recount reproduced every digit, and a second independent parse by an
auditor reproduced them again. What is wrong is the **composition of the ADDEND**, i.e. the term
test of `pred/01` §2 that both seals use.

The commit `8a9de7b`, its message, the first version of `FACTS.md` and the first ROADMAP edit all
claimed CLOSE. **That claim is wrong and is retracted here and in every one of those documents.**

---

## 1. Defect A — the term test is ONE-DIRECTIONAL, and the missing direction is larger than the margin

`pred/01` §2 admits a term iff **(i)** the full floor removes it **and (ii)** `gpu-driven.md`
§3–§4 keeps it for V2. Every such term is **added** to the floor.

There is no slot for the symmetric case: **the floor KEEPS it and V2 DELETES it**, which must be
**subtracted**. The session's own cited authority names one, with a number, on the row next to the
one the rule is built on — `C:/kyty/s94/rewrite94/gpu-driven.md:63`:

> \| `mh_emit` \| 7 531 \| 30–45 %: **CommitBindings 2 035 (tr/wr/em 962/626/447 [M s94]) → 0.1–0.3** \| 4.2–5.3 \|

The floor keeps `CommitBindings`' write and emit halves: `BindFloorPrepareStage`
(`descriptors.cpp:669-676`) leaves the stubs to be supplied *inside* `CommitBindings`, and its own
comment says the emit half is unchanged — "the SHAPE of the descriptor writes, which the floor
does not change". So **626 + 447 = 1 073 µs a flip of per-draw descriptor-set work stays inside
`F_a`/`F_c`, while the design document puts V2's survivor of the same work at 0.1–0.3 ms.** The
excess is **0.773 … 1.935 ms**, to be **subtracted** from the verdict input.

That is **3.2× to 8.0× the 0.243 ms margin**, in the direction that destroys CLOSE. It is not
measured by this session and cannot be repaired by re-running anything: it is a hole in the rule,
not in the data.

**A one-directional census cannot decide M3 in the CLOSE direction. Any future rule must be
two-directional, and the subtractive half must be measured, not argued.**

---

## 2. Defect B — term T4 fails its own half (i), and its half (ii) points at work already inside F

`pred/01` §2 admits T4 (the `shader_data` / user-SGPR copy) on the ground that
"`BindFloorPrepareStage` **zeroes** `shader_data` instead of copying it (descriptors.cpp:669)".

Verified in the source, `descriptors.cpp:673`:

    prepared.shader_data.assign(runtime.program->bindings.ShaderDataDwords(), 0u);

The floor **writes every dword of the same vector**. The real path
(`descriptors.cpp:2296-2300`) is `reserve(N)` + K `push_back`s + `resize(N)`. The two differ by
"K gathered stores" against "N zero stores", not by the presence or absence of the work. **The
floor removes the gather, not the write**, and `bl_sd_us` measures the whole block. Half (i) as
written in the seal is false.

Half (ii) is worse. The work `gpu-driven.md` §3 credits to V2 — *"push user SGPRs plus texture
heap indices **as push data**"* — is `descriptors.cpp:3887-3891`:

    EXIT_IF(prepared->shader_data.size() != shader_data_dwords);
    if (program.bindings.UsesPushData()) {
        std::ranges::copy(prepared->shader_data, push_data.dwords.begin() + ...);

which is **inside `CommitBindings`, which the floor keeps** — therefore already inside `F`.
Citing it as a V2 survivor that the floor removed is a double count of the kept half.

T4 must be **struck**.

---

## 3. Defect C — the headline "two dropped measured items" is half wrong

`FACTS.md` §1 and §9 said the sealed constant "dropped two of that same line's own measured
items". The `mh_bind` basis line of `gpu-driven.md` §4 contains **three** items — written slots
490.5, images 47 885 × 34.66 ns, **and samplers 345 [M s86]** — and the constant dropped **one**
of them: samplers. `shader_data`/T4 appears nowhere on that line, has no measured value and no
`[M]` label anywhere in the document; it entered only through an uncosted prose sentence in §3.

**The sampler half of the finding stands.** `bl_smp_us` = 345.1 µs is measured (`drm86a`, session
86, same scene), the floor stubs samplers (`bf_smp`, verified: `prepared.samplers` is left empty
and `CommitBindings`' `floor_sources` supplies one cached handle per slot without calling
`NativeSampler`), and the design table lists it as a V2 survivor. Dropping it from the constant
was an assembly error. **That single repair does not reach CLOSE**, which is exactly what
`pred/01` §3.1 pre-declared before any data existed.

---

## 4. Defect D — the floor's own stub work is inside F and was never priced

The addend must be **(real work − the floor's stub over the same slots)**, because the stub is
inside `F`. Nobody has ever timed the stub: `floor_sources` does a null lookup plus an
`emplace_back` per image and per sampler slot, `BindFloorPrepareStage` fills `shader_data`, and
`pipelineCache.cpp:3219-3226` copies the whole frozen snapshot per stage. Only counts exist
(`bf_img`, `bf_smp`, `bf_reuse`), never a timer. The sealed s88 unit 34.66 ns/slot used for T1 is
a **gross** per-slot price of the real path, not a price net of the floor.

CLOSE would need the stub to cost under **4.1 ns per slot-touch** over 47 866.5 image and
11 165 sampler touches, before charging 9 107 per-stage fills and snapshot copies. That is not
established and is not plausible on its face.

---

## 5. Defect E — the constant was changed on the executor's authority, not the user's

`docs/next-session-100.md` §1: *"A change to that rule, to its branches or to its constant goes
into `ROADMAP.md` **first**, with the **user's** decision recorded, before it is acted on."* The
change was recorded in `ROADMAP.md` **after** all five runs and after the verdict, and it is
labelled — correctly and from the start — as **the executor's decision under the user's
delegation of 2026-09-20**, in explicit contrast with the two prior amendments of this same rule,
which are recorded as the user's. The delegation was real and explicit, so the work was
authorised; but a global M3 verdict taken on a constant the user never approved is **not
licensed**, and it is now doubly not licensed because the constant is also defective.

---

## 6. The restated verdict

Applying the seals' **own** pre-declared branches, with T4 struck (§2) and **before** any of the
subtractive correction of §1:

    cen100b        (bindlap, 34206e3f):  T1 1.664154 + T2 0.4905 + T3 0.337034 + T5 0.1035
                                         ADDEND 2.595188 -> VERDICT_INPUT 15.420188 … 16.869188
                                         => GAP by 0.079812 ms
    mov100b_entry1 (blmove, 6f7475b8):   T3 inferred from cen100b's bl_smp_us : bl_sd_us split
                                         of the measured T34 0.664996 -> 0.302122
                                         ADDEND 2.555166 -> VERDICT_INPUT 15.380166 … 16.829166
                                         => GAP by 0.119834 ms

`pred/01` §3.1 declared exactly this, before any session-100 data existed: *"Without T4 it is
2.5988 ⇒ 15.424 … 16.873 ⇒ GAP by 0.076 ms."* The session landed on its own pre-declared branch.

Adding the subtractive direction of §1 (≥ 0.773 ms) takes the minimum verdict input to
**≤ 14.97 ms** and widens the gap further. **M3 is GAP. G and R1 are alive, open and
unlicensed. The order M3 → M4 → M5 is untouched.**

---

## 7. What still stands, unaffected by this addendum

* Every **measurement**, and both independent recounts. The numbers are right; their assembly was
  not. Specifically: image slots a flip 48 013.674 (`cen100b`) / 47 866.5 (`mov100b_entry1`);
  `bl_smp_us` 0.337034; `bl_sd_us` 0.404808; moved-mark T34 0.664996 with phase balance 0.0031 %
  and 0.0076 % and bias bound 0.001092; instrument costs C 0.436552 (`bindlap`) and 0.140948
  (`blmove`).
* **The moved-mark instrument works as designed.** The auditor who attacked it hardest confirmed
  that neither span contains any mark cost at all, that the base arm is exactly dark, and that the
  two phases draw from the same stage population. `blmove` remains the right way to measure a
  quantity of the same order as its probe.
* **The sampler assembly error in the sealed constant is real** (§3) and is worth +0.337 ms; it
  narrows the session-98 gap from 0.422 ms to about 0.080 ms without closing it.
* **The session-98 L3 debt is paid**: `clr_taken_meta` + `clr_taken_img` = 9.00 a flip of 268.0
  dispatches (3.358 %) against the 198.01 shape census, tightening `|dF_L3|` from 1.578 ms to
  0.0717 ms — with the carried caveat that it is measured in an unfloored run on another binary.
* **`PrefetchComputePipelines` is decomposed**: 1 836.9 µs a flip over 5 walks, 769.1 µs (41.9 %)
  inside `QueueDrawAhead` under `PipelineCache::m_mutex`, 125 acquisitions a flip.
* **The source changes and their A/B** (gate `blmove`, +0.387 % ± 0.112 % cpu/draw, t = +6.91,
  symmetric arms on every strict control) satisfy ROADMAP §6 on their own terms.
* **`cen100b`'s GAP** was right for a reason that is still right.

## 8. What the next rule must do

1. Be **two-directional**: ADDEND = Σ(floor removes it ∧ V2 keeps it) − Σ(floor keeps it ∧ V2
   deletes it). The second sum starts with `CommitBindings`' write and emit halves (626 + 447 µs
   measured in s94, survivor 0.1–0.3 ms by the design table) and must be **measured**.
2. **Price the floor's own stub**, so that every added term is net of what the floor already pays
   over the same slots. A timer on `floor_sources` and on `BindFloorPrepareStage` is the minimum.
3. **Price terms in V2's units, not the current implementation's.** T1 already is (34.66 ns a
   slot); T3 is not — it is the current 30.3 ns memoised lookup. The two must not be mixed in one
   sum without saying so.
4. **Put the constant to the user before acting on it**, as `docs/next-session-100.md` §1
   requires, whatever the delegation says about the rest of the session.
