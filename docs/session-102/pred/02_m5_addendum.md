# Sealed addendum 02 to pred/01 — session 102, M5: four corrections found by building the bench, sealed BEFORE any timing

**Immutable once written.** `pred/01_m5_bench.md` (14 288 B, `cf3c353f…`) is NOT edited. This file
is written after the offline build of every module (registers and SASS were read — pred/01 §6 makes
them "reported, never deciding") and **before** the capture exists, so before any EventGPUDuration
of any module of §2 has been measured. Nothing here moves the threshold (+6 %) or the branch.

---

## 1. V-f used the wrong validator command (my error in pred/01)

pred/01 §6 V-f: `spirv-val --target-env vulkan1.3`. Every PS item fails it on the const-bank
`cbuffers[]` block ("array with stride 4"), including arm A, which is **byte-identical to the module
the game runs** (`recompile-identity … identical=1` on all 16 permutations). The emulator enables
`uniformBufferStandardLayout` (`vulkanWindow.cpp:686`, logged at start), and the stand recipe of
sessions 18–20 always validated with `--uniform-buffer-standard-layout`
(`C:/kyty/scripts/s18_recompile.sh:20`, `s19_…`, `s20_…`). **V-f is therefore
`spirv-val --target-env vulkan1.3 --uniform-buffer-standard-layout`.** All 48 modules of A/V1/V2 pass
it; V2s (§3) must pass it too.

## 2. V-e: some draws are not bit-repeatable on replay even with nothing replaced

The mechanics run on an old capture (session 49, labelled MECHANICS ONLY) found a PS whose output
differs by 17–31 KB of an 8 MB target between two replays of the **untouched** capture
(subgroup/ballot-dependent output), under both replay optimisation levels. Under pred/01's "bit-equal
or the item fails", such an item would fail whatever the variant does. **Amended V-e:**

* For each item, arm A is replayed **three** times (A₁, A₂, A₃) with only that item replaced.
* If A₁ = A₂ = A₃ bit for bit, the item is *repeatable* and the variant must be **bit-equal** to A₁
  (pred/01 unchanged).
* Otherwise the item is *replay-nondeterministic*: let `E` = the largest number of differing bytes
  between any two of A₁, A₂, A₃; the variant passes iff its differing-byte count against A₁ is
  **≤ 2·E**. Such items are named in the report as passing "within replay noise", never as equal.
* Everything else in V-e (the 40 % rule, removal from that variant's sums) is unchanged.

## 3. D3: V2 loads 32 bits at a time — a new control arm V2s, and the verdict needs BOTH ratios

Building V2 showed that the translator's BDA machinery has **no vector load**: every wide constant
or buffer load becomes 32-bit BDA loads (one page lookup per group, a fits-in-page branch with a
per-dword slow path) and V2 adds a per-dword bounds select. The descriptor path it replaces loads
`uvec2`/`uvec4`. So V2 carries a **granularity artefact** that a G implementation could remove, and
**pred/01 §1's statement that V2 is a lower bound is withdrawn**: V2 is the price *with today's
emitter's BDA machinery*, biased upward by scalarisation and downward by the omissions §1 lists.

**New arm V2s** (`KYTY_RECOMPILE_BDA=2`): identical eligibility, run-time stride and limit, per-dword
bounds select, per-dword assembly and keep-alives — but every dword is loaded through the **original
descriptor** (const-bank loads stay UBO loads, SSBO loads stay SSBO loads), no BDA, `uses_dma`
untouched, layout identical to A's. `V2 / V2s` is then the BDA-plus-LDG price **at equal load
granularity**.

**Only V1 is a strict lower bound** of G's shader price (G must turn every const-bank load into a
global load; V1 does exactly that and nothing else). Hence the verdict, replacing pred/01 §5's:

* `X = median_r S[V2,r]/S[A,r]`, `Y = median_r S[V2,r]/S[V2s,r]`, `L = median_r S[V1,r]/S[A,r]`, each
  with the 90 % percentile bootstrap over rounds (20 000 resamples, seed 102; the same resample
  indices for all three).
* **CLOSE** if `CI_lo(L − 1) > 0.06` (the strict lower bound alone crosses), **or** if
  `CI_lo(X − 1) > 0.06` **and** `CI_lo(Y − 1) > 0.06` (the price crosses both with today's machinery
  and at equal granularity).
* **NOT CLOSED** if `CI_hi(X − 1) ≤ 0.06` **or** `CI_hi(Y − 1) ≤ 0.06`, and `CI_hi(L − 1) ≤ 0.06`.
* Otherwise **INCONCLUSIVE** ⇒ one extension (§4), then the points decide with the same logic
  (`L − 1 > 0.06`, or `X − 1 > 0.06` and `Y − 1 > 0.06` ⇒ CLOSE; else NOT CLOSED), published as
  *decided at the point after extension*.

The asymmetry is deliberate: a CLOSE ends the rewrite programme, so it must survive the artefact
(`Y`) as well as appear with today's machinery (`X`), unless the strict lower bound (`L`) already
carries it. `X`, `Y`, `L`, `V2s/A` and every per-item ratio are published whatever the verdict.

**What V2s does NOT control, known before any timing (read from the built modules, reported by the
harness author):** (i) V2-only BDA machinery — a 64-bit base, a page-table `LDG.E.64` per group, the
fits-in-page branch and its duplicated per-dword slow path, null-page fault tracking and the
fault-buffer store at exit; (ii) **every V2 data load in a PS item compiles to `LDG.E.STRONG.SM`**
(S4 480, S8 451, S2 143), while V2s/A loads are weak `LDG`/`LDC` — a memory-model property of
today's emitter's pointer loads, not of BDA as such; compute V2 has none; (iii) in PS items V2s keeps
the constants on the constant cache (`LDC.cx`/`LDCU.cx`, uniform datapath) while V2 moves them to
`LDG` in vector registers — this part IS G's price (it is what `L` isolates); (iv) V2s pays bounds
twice (its explicit select plus the robustBufferAccess2 predicate) — this biases `Y` DOWN;
(v) register allocation of V2s also differs from A (S8 p0 96 → 128 registers with its spill gone).
Static counts, A / V1 / V2 / V2s, full SASS instructions: S1 16137/16137/20994/16388,
S4 5495/5766/11177/6654, S8 p0 4549/4798/9945/5495 — V2s lands much nearer A than V2 does.

**Therefore a CLOSE is published in one of two tiers, both of which are "G closed" under the rule:**
* **CLOSE — strict** (`L` crosses): on a component every G implementation pays.
* **CLOSE — with today's BDA machinery** (`X` and `Y` cross, `L` does not): G closed *as the current
  emitter would implement it*; the report must name items (i) and (ii) as the machinery a G
  prototype would first have to replace, and reopening G on that ground is a decision for the user,
  recorded in `ROADMAP.md` first.

## 4. Five arms: the design and R

Arms `B A V1 V2 V2s`. Order per round: the ten sequences formed by the five cyclic rotations of
`B A V1 V2 V2s` and their reverses, used in that order; **R = 20** rounds (two full cycles; pred/01's
12 was for four arms), the never-below-8 floor unchanged (a cycle = 10), extension **+20** rounds.
The mechanics run measured 0.53–0.86 s a fetch and ≈ 1 s a replacement set, so R = 20 is minutes.

## 5. "Present", made explicit

An item is **present** when at least one captured module of it is found: either its SPIR-V md5
equals arm A's md5 for some permutation, or its bytes equal the SPIR-V stored in the item's
translation-cache file written by the capture run (arm A is byte-identical to that file for every
permutation built, so the two coincide on every permutation the harness compiled). V-b counts
present items; V-c keeps, per module, only those whose md5 equals an A module (unchanged).

## 6. Unchanged

Threshold, branch, shader set, capture protocol (pred/01 §4), V-a, V-b limits, V-c, V-d, V-g, the
40 % rules, P1–P4 (P2 and P3 now read against X), and every "must not be claimed" of pred/01 §8.

---

## Provenance at sealing time

* Emulator binary built this session, NOT yet installed or run: `346ba4f6448c35cba8677101a1599c6ddd0b907d3ea76015ada692cd3b3dc776` (source HEAD `0d35faa` + uncommitted session-102 changes; translator hash `2db9065aef8b54a24a7d29b3584df9647f61dd95` unchanged).
* `shader_cfg_tests.exe` `cfe15c6cf5ce14ed2988d4da4d7e6590c65f2b319b751d1937ccd71b825a73a5`.
* Sealed at 2026-09-22T22:12:14.
