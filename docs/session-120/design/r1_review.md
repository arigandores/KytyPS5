# Session 120 — adversarial review of `r1.md` (R1 texture-memo census)

Read-only review. Tree `C:/kyty/KytyPS5` at `996d565`. No build, no game run, no source edited. Every file:line claim of
`r1.md` was re-read against the source; the population table was re-parsed from `C:/kyty/s118/log_spk118.txt`.

**Verdict: SOUND_WITH_CHANGES.** The instrument changes nothing at `r1cen=0`, and nothing but timing and one 1.6 MiB
heap block at 1/2. Its would-hit test is exactly the real hit's test. Its bad check catches what it claims, in the pre
half. However the ceiling formula is **not** the honest upper bound the design says it is: one term is biased low
(losses), one is inflated by an unrelated population (re-records), one plus term is missing, and the verdict uses a
threshold and a gross ceiling that ROADMAP s120 item 2 has already replaced (0.5 ms, net of the check a real memo pays).
Under the new threshold the prediction sits on the border (≈ 0.45–0.65 ms net [I]), so each of these terms can decide
the verdict. The required changes are listed in §6. Every one is small and adds no new population.

## 1. File:line claims — verified

| claim in r1.md | source | result |
|---|---|---|
| memo direct-mapped 4 096, `memo_hash % 4096` | `renderMemo.h:114`, `descriptors.cpp:1469-1471` | OK |
| null returns before the memo | `descriptors.cpp:1425/1433/1438` | OK (`bindpack` on: `tnull_miss` = 0) |
| key test / collide-empty Add / hit branch | `:1473-1480`, `:1481` | OK |
| five-field liveness | `:1482-1485` | OK |
| `bindwit` marks | `:1496-1498`, `:1525-1527`; `g_bind_wit_arm` reset after the loop `:2270` | OK |
| stale path | `:1531-1535` | OK |
| miss path, `FindImage`, store, emit | `:1538-1711`, `:1666`, `:1695-1709`, `:1710-1711` | OK |
| `desc.info.data`/`extent` built from (T#, resource) | `:1635`, `:1639` | OK. Every input (`written`, `r128`, `mip_mode`, `depth_compare`…) sits in the hashed `ImageResource` prefix (`ShaderIR.h:161-182`, before `indirect_resources`) |
| `FindImage` never writes data/extent | `textureCache.cpp:2029-2113`: `ConstrainSampledSource` `:1189-1217` (source_* only, a pure function of desc + constants), overlap `view_info.base_level/base_layer` `:2102-2107` | OK |
| only two writers of memo key/valid | `grep (->\|\.)textures\b`: `:1472`, `:2559`, `:2773` (read-only); `m_memo` created once `:1723-1728`, never reset | OK |
| `RebindImages` writes only `fast_view`/`fast_stamp` | `:2600`, `:2615-2616` | OK |
| texfast eligibility ⇒ `memo_index < 4096` | `:2558-2566` | OK |
| re-record branch, `usage.texture`, `continue` | `:2605-2620`, `:2621`, `:2622` | OK |
| texfast Adds | `:2647-2653` | OK |
| `m_slot_images` private, friend | `textureCache.h:293`, `:324` | OK |
| `try_get` const, generation-checked | `slotVector.h:54-60`; generation moves on `erase` (`:80-87`) | OK |
| callers of the template | `:2223-2228`, `:2516`, `renderCompute.cpp:195` | OK (Grep: no others) |
| `shadowresolve` never calls the template | `:2737-2813` (copies jobs), `textureCache.cpp:2162-2200` (`ShadowProbe`, under `m_lock`) | OK |
| one executor per context | `renderContext.h:49` is the accessor `GetRenderExecutor()` | OK (line is the accessor, not the member) |
| Counter enum end / print table end | `frameStats.h:1941-1943`, `videoOut.cpp:2581-2583` | OK; printing is `std::string` + `fmt::sprintf`, no length limit (lines are 13.3 KB today) |
| `Scope` reads 0 in lite; `g_count_limit` | `frameStats.h:2079-2098`, `:2004-2007` | OK |
| `Knob::Spine` LAST / `KNOB_DEFINITIONS` LAST | `gates.h:607-608`, `gates.cpp:411-412` | OK |
| `Value` relaxed | `gates.h:642-647` | OK |
| `g_block` written before the arm is applied | `gates.cpp:638-639` then `ApplyText` `:649` | OK. A stale `g_block` read at an M→P edge only causes a second reset, and at P→P no reset at all, so the relaxed ordering is harmless |
| `FindAssignment` token-bounded | `gates.cpp:458-470` | OK, `r1cen` collides with no name |
| population table | re-parse of `log_spk118.txt`, arm 1, frames 10–88, `draws > 3000` | **exact**: 2 994 frames, `b_texn` 50 370.3, `tex_hits` 47 108.8, collide 1 771.9, empty 0.2, stale 7.4, `tnull_hit` 1 481.8, `texfast_ok/no/rec` 45 394.3 / 4 864.8 / 1 530.8. Identity closes to 0.2 |

Note for the scorer: `b_texn` and `tex_hits` are printed on **`FrameTrace-draw:`** (`videoOut.cpp:1305-1312`), not on
`FrameTrace-x:`. The F2 join by `n=` must read both lines.

## 2. Behaviour at 0, 1, 2

* **At 0.** Each call adds one relaxed knob load (`memo2 ? 0 : Value`) and short-circuited branches, and each
  `RebindImages` call adds one load (only when `fast`). There is no TLS access, no `Enabled()`, no `NowNs`, no
  allocation. Every existing Add keeps its order. No layout change: `RenderExecutorMemo`, `Texture`, `TextureBinding`
  are untouched. **PASS.**
* **At 1 and 2.** The census reads image fields through `try_get` without the lock, exactly as the real hit path reads
  them (`:1482-1485`). It never calls `TouchImage`, `FindImage` or `ConfigureImageSource`, so the texture cache's LRU,
  `tick_accessed_last` and GC order are untouched. It writes only its own memory and new counters, and never keeps a
  `const Image*` across the miss path. This matters: `SlotVector::insert` can reallocate `m_values` (`slotVector.h:66-68`),
  and `Cand` stores copies (`data`, `extent`), not pointers. The build session must keep it that way. Other scorers'
  counters (`tex_hits`, `texmemo_*`, `b_texn`, `texfast_*`) are unchanged. `bl_res_us`, `bl_img_us`, `mh_bind`,
  `a_hold_us` and `dt` of P carry the census. That is expected and is priced by the ABBA; see R2's constraint in §5 F-I.
  The heap block of 1.6 MiB feeds no emulation decision. **PASS.**

## 3. Is "would hit" as strict as a real memo?

Yes, for the returned answer. The pre-mode decision is the real hit's own conjunction, with each term checked:
valid/gen, 64-bit `resource_key`, 32-byte T# `memcmp`, `try_get` (generation), `registered`, `!needs_rebind`,
`!depth_id`, and data/extent equal. Data and extent are pure functions of the key, so comparing them with the fresh desc
is the same comparison as with the stored one. The tag is only a filter.

**Witnesses a real bigger memo would need beyond the answer.** None is missing for correctness of `(id, desc)`. The
side effects of the would-hit path are the hit tail, and by reading they equal the miss path's: `ConfigureImageSource`
against `ConfigureImageSourceUnlocked` on the same desc; `tick_accessed_last` against the same clock (`AgeTick` =
`m_command_scheduler.CurrentTick`); `TouchImage` on both paths; DCC adoption, conditional on the hit path and
unconditional in the miss path's non-depth branch. The validations skipped on a hit (`ValidateSampledDepthBinding`,
`SelectSampledColorView`) only `EXIT`; the existing memo skips them too. Two things are not a witness of the answer and
are rightly declared "not modelled": the texfast `memo_index`/`version` semantics, which affect only `R_T`, and the
cost of the N-way probe. The longer residency of a bigger table raises its exposure to "an overlap view superseded by a
later exact image" (`:1457-1459`), and the pre-half bad check is exactly what catches that. Good.

## 4. Can the bad counter catch what it claims?

In the pre half, yes: every would-hit is compared with the fresh resolution computed at the same moment (`store`, id,
and a digest of every `ImageDesc` field). The digest's field list was checked against `imageInfo.h:24-183` and
`textureCache.h:37-43` and is complete (`mip_layout` is hashed up to `levels`, which is what consumers read).

Limits, which the design should state:
* Bad covers the **answer**, not the side effects (argued equal in §3).
* In the post half, a bad whose miss path freed the candidate is invisible. The design states this.
* Bad also fires where the existing memo has the same semantics. It is conservative: FAIL, then record.
* There is **no failing control** for the census plumbing of the N-way tables (fill, drop, victim, tag probe). Bad
  checks answers only. F4 cannot see a bug that both halves share. `r1_incl` covers only d16 and the stale id
  invariant. So a wrong W₄/W₈ or `lose` would go unseen. See F-G.

## 5. Findings (most severe first)

**F-A (MAJOR, verdict rule out of date).** ROADMAP s120 item 2 (written before code) replaced the 1 ms threshold with
**0.5 ms** for the s120 designs (item 2(г)). It also defines the ceiling as **net of the price of the check that a real
memo also pays** (item 2(a)), and puts R1 and R2 into one image-resolve package when their populations do not overlap
(item 2(б)). `r1.md` §10 and F10 still use 1 000 µs and a gross ceiling, and §11 still predicts "CLOSED or BORDER".
Under 0.5 ms the [I] prediction of 0.7–0.85 gross is ≈ 0.45–0.65 net, which is the border.

**F-B (MAJOR, the net ceiling needs the probe).** `A_T` already subtracts `t_hit` (the hit proof and tail a real memo
pays on a would-hit). But the w4/w8 tables pay an extra tag probe on **every** lookup (≈ 48.8 k a frame), which §5.5
only lists as an omitted minus. Under item 2(a) it must be subtracted, and it is measurable for free: the census already
runs exactly that probe (`R1FindTag` on a compact tag set, as the s119 design requires of a real table). At 2–5 ns
[I] the probe is 0.1–0.25 ms a frame, which is decisive at a 0.5 ms threshold.

**F-C (MAJOR, the loss term biases C low, so C is not an upper bound).** `L_T = lose × (t_miss − t_hit)` prices a loss
at the mean of **all** post-mode key misses. A loss is a real hit, so its image exists and is live, and T's miss path
for it is the kind of miss that finds an existing image. That is the population priced by `t_T`. `t_miss` also contains
first-time keys whose `FindImage` goes through `InsertImage` (host image creation, `textureCache.cpp:2083-2090`), so
`t_miss ≥ t_T` is expected. Using it over-subtracts L, which pushes C down, against the stated direction of the bound.

**F-D (MAJOR, the re-record term is priced on an unrelated population).** `R_T` multiplies the would-hit re-record
count by the mean of **every** eligible null-view re-record (`r1_rb_ns / r1_rb_n`). That population includes slots
whose view could never be recorded (dirty or pending images re-run `FindTexture` on every bind) and first-time view
creations. Both are expensive and neither belongs to would-hit fills, so `R_T` is inflated by an amount unrelated to R1.
The marked re-records can be timed on their own at no extra stamp cost, because they are already inside the `r1_null`
interval.

**F-E (MEDIUM, the post-mode price is not clean).** The design calls post-mode misses "unwarmed", but `R1Begin` still
runs `R1FindExact` on up to three census proof lines before `t0`. These are random lines of a 1.5 MiB array: L2/L3
misses, and `rdtsc` does not serialise, so part of their latency bleeds into `[t0, t1]`. They also evict lines the miss
path needs. The census tables cannot change between `R1Begin` and `R1Miss` (no re-entrancy: `FindImage` never calls
back into the executor), so in post mode the whole lookup can move after `t1` at no loss. This inflates `t_T` (upward),
but with a border verdict a measured price must not carry the instrument.

**F-F (MEDIUM, missing plus term in §5.5).** A would-hit also avoids the miss path's after-effect on the lookups that
follow it. The miss path touches the region/page-hint tables, the `m_lock` line, a 650-byte memo slot write and the
stack desc, and can evict lines the next hits need. None of this lies inside `[t0, t1]`. §5.5 lists only minus
omissions, so the claim "UPPER bound" is unproved until this term is bounded. It is probably small (≤ ~0.05–0.1 ms
[I]), but it is measurable with two counters.

**F-G (MEDIUM, no failing control for the w4/w8 plumbing).** See §4. A 1-way shadow of 4 096 sets, run through the
**same** template helpers, is the real memo itself. Its would-hits and losses are exactly 0 by construction, so it is a
null control that can fail. It exercises `R1FindTag`, `R1FindExact`, `R1Fill`, `R1Drop` and the watched/observed logic,
but not the multi-way victim choice. For the victim choice, add a unit test of `R1Victim`/`R1Fill` against a
brute-force LRU on a synthetic key stream (recommended, build session).

**F-H (MINOR, correctness counters windowed).** §7 and §10 fail only on `*_bad` "in a window row", and F7 only on
`r1_incl` in one. A would-hit disagreeing with a fresh resolution is a correctness fact at any frame. Block edges
produce no false bad or incl (reset semantics checked in §1). Evaluate them over **all** P rows and over the process-wide
`R1CenMismatch:` lines.

**F-I (MINOR, self-cost bracket incomplete, and R2 depends on it).** `r1_self_*` brackets `R1Begin` + `R1Hit`/`R1Miss`
only. It omits `R1Arm` (the out-of-line `GetFrameNum`, `g_block`, the TLS access), the `Enabled()` call, the RNG draws
and the `cand` reset, so §6 item 2 understates R1's share. `r2.md` §11 item 2 asks R1 for its own in-loop cost, **split
hit / miss**, because the census is not uniform over the two (~10 ns on a hit against ~200 ns on a miss) and R2's level
factor `f` removes only uniform inflation.

**F-J (MINOR, guards).** `texfastcheck=1` would put a `FindTexture` inside the fast-sample interval, and nothing
detects it. Guard it in code (`r1_fs` only when `!fast_check`, which makes `r1_rbf_n` read 0 so F3 fails). The scorer
should also assert from the arm and base texts that `texmemo2=0`, `texfastcheck=0`, `m4baton=0`, `fslean=0` and
`bindwit` is absent or 0. Also recommended: a deterministic owner-thread check in `R1Arm` (a global atomic holding the
owning thread's `&t_r1`; any other thread counts `r1_xthr` and returns `nullptr`), instead of relying on the sampled
`r1_incl`.

**F-K (text / nits).**
* §4 calls level 1 a "fallback P arm", but level 1 produces no `W_T`, so it cannot give a verdict; it is a smoke
  level only.
* `Proof` is described as "one cache line" but is not `alignas(64)`, so proofs straddle two lines. Add `alignas(64)`.
* `R1Begin` does useless work on key-match lookups: the `cand` reset (3 × ~64 B) before every hit's `t0`. Draw `self`
  inline and skip it.
* Add to `R1CenMismatch` both ids (index/generation) and which desc group differs (info / view / source).
* Recommended, not required: `r1_nost` / `r1_nost_ns`, key misses with `store == false`. That population (≈ 240 a frame
  [I] from collide − `texfast_rec`) is uncatchable by any table shape and is a different candidate.

### Hot path and thread safety

Cost at 0 is ≤ ~20 µs a frame [I] and lands in both arms. At 2 it is 0.9–1.6 ms [I] per the design, plus ≈ 0.1 ms for
the controls below. This is outside every interval, and it is timing only. The census is single-thread by construction
(`thread_local`, GuestGpu under the render mutex). It takes no lock. Its unlocked reads of image fields are the same as
the real hit path's. Its logging is a `static std::atomic` limit of 40. No deadlock or ordering hazard.

## 6. Required changes (pseudo-diffs against `r1.md`)

**RC1 (F-A): verdict rule.** In §10 and F10 replace 1 000 by **500 µs**, apply them to the **net** ceiling `C_T` of
RC2–RC5, and add: "C_R1 enters the image-resolve package with R2's `C_pt` (ROADMAP s120 item 2(б)). The populations
are disjoint: R1 = key-miss lookups + the first re-record of their fills; R2 = memo-hit slots of clean repeating
blocks; `RebindImages` is not in R2." Rewrite the prediction in §11 for 0.5 ms.

**RC2 (F-B): measured N-way probe, subtracted.** In `R1Hit`, on the self sample only:
```cpp
+	if (c->self) {
+		const uint64_t a0 = FS::NowNs(), a1 = FS::NowNs();                         // null pair
+		const uint64_t b0 = FS::NowNs(); const int x4 = R1FindTag(s4, tag); const uint64_t b1 = FS::NowNs();
+		const uint64_t d0 = FS::NowNs(); const int x8 = R1FindTag(s8, tag); const uint64_t d1 = FS::NowNs();
+		FS::Add(FS::Counter::R1Pb0Ns, a1 - a0); FS::Add(FS::Counter::R1W4PbNs, b1 - b0);
+		FS::Add(FS::Counter::R1W8PbNs, d1 - d0); FS::Add(FS::Counter::R1PbN, 1);
+		(void)x4; (void)x8;   // results unused: the real lookups below decide
+	}
```
Scorer:
`t_pb_T = max(0, (Σ r1_T_pb_ns − Σ r1_pb0_ns) / Σ r1_pb_n)` (clamped at 0, because a lower bound of P keeps C net an
upper bound). Then `P_T = Σ (r1_hn + r1_mn + r1_sn) · t_pb_T` and `P_d16 = 0`. The d16 footprint (4 × 650 B entries,
10.6 MB) stays a stated [U] minus.

**RC3 (F-C): loss price.** Replace
`L_T = Σ r1_T_lose · (t_miss − t_hit)`
with
`L_T = Σ r1_T_lose · max(0, min(t_T, t_miss) − t_hit)`.
Keep `t_miss` as a reported number only.

**RC4 (F-D): re-record price on its own population.** In the `RebindImages` hunk, inside `if (r1_null)`:
```cpp
-						for (int t = 0; t < 3; t++) r1_rbm[t] += (m >> t) & 1u;
+						for (int t = 0; t < 3; t++) if ((m >> t) & 1u) { r1_rbm[t]++; r1_rbmns[t] += r1_dt; }
```
Add counters `r1_w4_rbns`, `r1_w8_rbns` and `r1_d16_rbns` (and `r1_w1_rbns` with RC7). Scorer:
`R_T = Σ r1_T_rbns − Σ r1_T_rb · t_fast`, where `t_fast = Σ r1_rbf_ns / Σ r1_rbf_n`.
Optional tightening: count and price a marked re-record only when that re-record recorded a view (`fast_record`
condition true). A re-record that could not record would also happen in T.

**RC5 (F-E): no census memory traffic before `t0` in post mode.** In `R1Begin`, for `!key_match`, draw `post`. If
`post`, return right after the draw (no `R1FindExact`, no `d16` read). In `R1Miss`, when `c->post`, run the three
exact lookups and then `R1Live` after `t1`. The pre half is unchanged. The candidates' meaning is unchanged, because
the tables cannot move between the two calls. §5.3 keeps its text, now true.

**RC6 (F-F): after-effect term.** State it in §5.5 as a **plus** omission. Measure its first order:
* A thread-local flag `t_r1_after_miss` is set in `R1Miss` (key miss with `store`) and read and cleared at the next
  `R1Begin`.
* On every hit after a miss, add `r1_am_n`. On a timed one, add `r1_ham_ns` and `r1_ham_t`.

Scorer: `E_T = max(0, t_ham − t_hit) · Σ r1_am_n · W_T / Σ r1_mn`, where `t_ham = Σ r1_ham_ns / Σ r1_ham_t`.

**Net formula** (replaces §5.4):
`C_T = (A_T − L_T + R_T + E_T − P_T) / N_f / 1000`.
Report A, L, R, E and P per table.

**RC7 (F-G): w1 null control.** Add a 1-way table `Set1 {tag, use}` × 4 096 with proofs, index `h & 4095`, filled and
dropped by the same helpers, candidate `cand[3]`, and a mark bit 3. It needs counters `r1_w1_q`, `r1_w1_p`, `r1_w1_lose`
and `r1_w1_rb`, and **all must read 0 over all rows, else NOT_EVALUABLE**. Cost ≈ 288 KiB and one more tag line a hit
(≈ 0.05–0.1 ms [I]). Recommended in addition: an offline LRU unit test of the helpers.

**RC8 (F-H): correctness counters over all rows.** FAIL if Σ `r1_{w4,w8,d16}_bad` > 0 over **all** P rows of the run
or any `R1CenMismatch:` line exists. NOT_EVALUABLE if Σ `r1_incl` > 0 over all rows, or if the RC7 control is nonzero.
Windowing stays for the estimator only. Add F7b/F6b fixtures with the offending row at block position 3 and at 95.

**RC9 (F-I): self bracket.** Take `self` and `s0` at the top of the `if (r1_on)` block, before `R1Arm`. That bracket
then covers `R1Arm`, `R1Begin` and `R1Hit`/`R1Miss`. Split the counters by kind: `r1_self_h_ns/_n` (hits),
`r1_self_m_ns/_n` (key misses), `r1_self_s_ns/_n` (stale). §6 item 2 and R2's `T*` correction use the split. The
remaining unbracketed cost is the `t0`/`t1` stamp pair (s101 constant) and `Enabled()` (≈ 1–2 ns [I]).

**RC10 (F-J): guards.**
* Code: `r1_fs = r1_time && !fast_check && !r1_null && eligible && (R1Next() & 15u) == 0`.
* Scorer: assert `texmemo2=0`, `texfastcheck=0`, `m4baton=0`, `fslean=0` and `bindwit` absent or 0 in both arm texts and
  in `gates_base.txt`; otherwise NOT_ADMITTED.
* Fix the F2 join to read `b_texn` and `tex_hits` from `FrameTrace-draw:`.

**RC11 (fixtures, follow from RC2–RC7).**
* **F8 (d16):** add `r1_d16_rbns = 84000`, so `R = 84000 − 1400·20 = 56000`, `P_d16 = 0` and `E = 0`
  (`r1_am_n = 0`). C_d16 stays **776.0 µs**.
* **F9 (w4):** `L_w4 = 300 · (min(475, 480) − 25) = 135000`. `r1_w4_rbns = 84000` gives `R = 56000`. Probe:
  `r1_pb_n = 800`, `r1_pb0_ns = 6680`, `r1_w4_pb_ns = 8680`, so `t_pb = 2.5`. With `r1_hn = 47000`, `r1_sn = 8`, the
  lookups are 48808, so `P = 122020`. Then **C_w4 = (720000 − 135000 + 56000 − 122020)/1000 = 519.0 µs**, and C_R1 = max
  = 776.0 (d16).
* **New fixtures:**
  * a negative `t_pb` clamps to 0;
  * `min(t_T, t_miss)` with `t_T > t_miss` uses `t_miss`;
  * `E` with `t_ham < t_hit` clamps to 0;
  * the w1 control nonzero gives NOT_EVALUABLE;
  * bad and incl at block positions 3 and 95 (see RC8);
  * F10 at 500: 500.0 / 2SE 20 gives OPEN; 479.9 gives CLOSED; 490 gives BORDER.
* **New mutants:**
  * `L` priced at `t_miss`;
  * `R` priced at `r1_rb_ns / r1_rb_n`;
  * `P_T` dropped;
  * `E_T` added unclamped;
  * threshold 1000;
  * bad windowed.

**Non-blocking (recommended):**
* `alignas(64)` on `Proof`.
* No `R1Begin` work on key-match lookups.
* Richer `R1CenMismatch` text.
* `r1_nost` / `r1_nost_ns`.
* The owner-thread check `r1_xthr`.
* Report `t_hit` and `r1_mp_ns/r1_mp` from the unsealed level-1 smoke next to the level-2 values, as a check on census
  cache pollution. §5.5 says its sign is ambiguous. By arithmetic it is ≤ ~5 µs a frame [I]: 2 tag lines a hit hit L2,
  not memory.
