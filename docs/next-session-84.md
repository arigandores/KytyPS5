# Session 84 — the brief

Session 83's commit is on `merge-upstream`. **Source changed and the binary was rebuilt**; the
installed `kyty_emulator.exe` is `4588d793c8919e515e6b…`, 23 578 624 bytes. Harness —
**`C:/kyty/s83`**, port it to `C:/kyty/s84`.

**The programme's goal changed in session 83 and you must read that before anything else.**

## 0. Read first

0. **`docs/ROADMAP.md` §0.** The sequential floor was measured at **20.8 ms** against a 60-FPS frame
   budget of **16.7 ms**. The serial part of the frame alone does not fit in a 60-FPS frame.
   **Route A — parallel command recording — is CLOSED by kill criterion K2, by a measurement, not by
   an argument.** Do not build any step of `docs/DESIGN_82_parallel.md`. It is now a closed design.
1. `C:/kyty/s83/FACTS.md` — the single source of truth. **§2 (the floor and its three caveats),
   §2.6 (the one thing that could reopen route A), §3 (where `bda_us` does NOT go), §4.5 (a package
   that missed its own threshold by 10 µs), §5 (seven corrections to the record).**
2. `C:/kyty/s83/README.md` — the standing traps.
3. `docs/PLAN_82_bind.md` — route B, thirteen ranked items. Item 5's premise is now bounded out.

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s83` → `C:/kyty/s84`. `gates_base.txt` is **unchanged** — 1092 bytes,
99 names, sha256 `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `mutwide`,
`bindpack` and `bindpackcheck` are deliberately absent from it. The s83 port already fixed
`area_series.py`'s stale root and three broken `--roots` chains; verify they survived.

## 1. What session 83 settled

* **The floor.** `flr83b`, VALID on all six criteria (pair match 119/119, split +0.002 %, work
  +0.054 %, gap +0.002 pp): `a_mut_us` **13 437 → 20 973** when `mutwide=15` adds `MutScope` to
  `PrepareDrawRenderState`, `RefreshShaders`, the dispatch critical section and `PrepareBda`. The
  instrument costs **+135.3 ± 87.7 µs**, so **`S_hi` = 20 838 µs**. Arming is `mw_n`: 0 → 10 542,
  matching `2·mh_n + mh_disp_n + bda_n` to −0.25 %.
* **`flr83a` was VOID** (pair match 65.8 %) and its contrast is quoted nowhere. Its floor readouts
  agree with the valid run to 0.3 %.
* **`bda_us` is not the `m_buffers` map.** The census: `bda_hit` 158 of `bda_n` 179 — **87.8 % of
  `PrepareBda` calls never scan at all**; `bda_rng` 288, of which `bda_rng_e` 216 (75 %) return on
  two lookups finding no registered buffer; `bda_drng` 1 178. That is ~1 754 red-black descents a
  frame, 0.18–0.35 ms at any plausible unit price, not 2.2 ms. **And `bda_us` reads 0 under `lite`,
  so nothing in session 83 timed the BDA path at all** — the 2 181 µs of `bind78a` was a
  full-tracing figure that includes its own nested instrumentation.
* **The binding-path package is correct and measured and did not ship.** `bindpack` =
  `PLAN_82_bind.md` items 1, 4 and 9. `bpk83a` is VALID (125/125 pairs, split +0.000 %, work
  +0.109 %) and reads `cpu/draw` **−0.548 % ± 0.146 %, t = −7.49**; the pre-registered endpoint
  `cpu_net_us` reads **−139.8 ± 81.2 µs** against a **−150 µs** ship threshold. It missed by 10.2 µs
  and **the threshold was not moved**. Gate stays 0.
* **The video debt is discharged.** `bpc83a`, `bindpack=1`, 5 732 recorded presents, **0 one-frame
  glitches**, `bp_bad` 0.

## 2. What is settled — do not reopen

* **Route A in every form.** `S` = 20.8 ms > 16.7 ms. No `W`, no granularity, no lock decomposition.
* The BDA epoch CAS of `DESIGN` step 1a: **the mechanism is already shipped** (`KYTY_BDA_EPOCH_CACHE`
  carries 87.8 % of calls).
* The `std::map` of `SynchronizeBuffersInRange` as the carrier of `bda_us` (§1).
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

The rule is unchanged and not negotiable: **the session ends with a source change that was A/B'd on
this machine, or it failed.**

### 3.1 First, the cheapest real win on the shelf (one run, no code)

**Pre-register a two-run pool for `bindpack` and take the second run.** One valid run reads
−139.8 ± 81.2 µs; a second halves the interval. Write the pooling rule and the threshold **before**
the run — pooling after seeing run 1 is optional stopping, which is why session 83 did not do it.
If the pool crosses −150 µs, ship `bindpack` default 0 → 1; the video pass is already done.

### 3.2 Then route C, which is now the only route with an unmeasured ceiling

`ROADMAP.md` §2 C: ~5 060 draws and ~95 000 descriptor slots a frame, of which **~5–7 ms is the
price of CHECKING memos that hit**. That price can only be removed by binding fewer slots. **No
counter in the tree measures how many of the ~95 000 slots a draw binds are identical to the slot
the same stage bound in the previous draw** — `bk82a` tried and was invalid in its entirety, and its
one-slot comparison answered the wrong question anyway. That counter is the first move, and
`PLAN_82_bind.md` item 0 specifies it (split key, N-way, XXH3, six counters).

### 3.3 The one thing that could reopen route A

`FACTS` s83 §2.6: `mh_prog_us` (5 850 µs) is inside `S` because it is wrapped **whole**, yet 74.8 %
of draws take the program memo, which is a **read**. `DESIGN` §5.3 says `ProgramCache`'s maps must
stay exclusive while the memo holds **iterators**, and names `SourceEntry*` + a validating key as
the precondition for splitting them. If that is possible, `S` falls towards ~15 ms. **This is a
source-reading question, not a run.** It is worth one careful read before route C, because the
answer decides whether a closed direction is really closed.

### 3.4 The debts

* **`dapin`'s GPU cost** +1.238 %, replicated four times, unexplained for a fifth session. One
  `KYTY_GPU_TIME` pair on a `dapin` ABBA.
* **What `PrepareBda` actually costs** — a `Lap` inside it, because `bda_us` is a `Scope` and reads
  0 in every measurement run.

## 4. Do NOT

**New, from session 83:**

* **Do not read `spin_gpu_us`, `bda_n`, `bda_scan` or `bda_skip` off the main `FrameTrace` line.**
  Under `KYTY_FRAME_TRACE=lite` that line is SHORT and they live on `FrameTrace-draw`. A tool that
  reads them from the main line finds nothing and a derived endpoint degenerates **silently**.
* **Do not use `memcmp` to compare two `ImageDesc`** — or any aggregate with padding. The copy
  assignment is member-wise and carries no padding; aggregate initialisation leaves it
  indeterminate. `bindpackcheck`'s first cut reported 177 false disagreements a frame this way.
* **Do not quote a threshold in one statistic and read it in another.** `summary4` reports
  `cpu_net_us` as a percentage (−0.548 %, i.e. −177 µs at this frame time); the µs estimator on the
  same pairs reads −140. They disagree by 26 %. Write the threshold in the statistic the tool prints.
* **Do not claim "arming reads exactly 0"** without checking the tail. `mw_n` is 0 on 98.4 % of
  arm-0 frames and up to 0.58 % of the armed value on the rest, recurring on the ABBA period.
* **Do not plan a mechanism before reading the function.** `DESIGN` step 1a proposed one that is
  already shipped.
* **Do not trust a port's silence.** Read its diagnostics: session 82's port printed the broken
  root chains and the line went unread for a session.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming proved
by a counter inside the run; `guards.py` check 10 hashes the exe installed *now*, so compare check
**lines**, not verdicts; check 6 (cores) FAILs routinely and is not an admission criterion; a gate
enum entry goes immediately before `Count`; every verify line needs a cap (32–64); never put a
printf's format string and its argument list in one patch call; never estimate a saving from a
population without a measured unit price; `dt_us` is not an endpoint inside the vblank plateau.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b`, all six criteria | **MEASURED — closes route A** |
| route A's requirement | `S ≤ 14 ms` **and** `f_eff ≤ 0.125` | **UNREACHABLE** |
| `bindpack` package | `cpu_net_us` −139.8 ± 81.2 µs; `cpu/draw` −0.548 %, t = −7.49 | **VALID, gate 0** (threshold −150) |
| `bda_us`'s map candidate | ~1 754 descents/frame ⇒ ≤ 0.35 ms | **BOUNDED OUT** |
| `bda_us` itself | reads 0 under `lite` | **NOT MEASURED** |
| route C's ceiling | — | **NOT MEASURED — the only one left** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | unchanged this session |

**The honest statement of the task.** Session 83 spent its budget on the one number that decided
whether a months-long rewrite was worth starting, and the answer was no — the serial part of the
frame is larger than a whole 60-FPS frame. What remains is route B (≤ 2.5 ms, ships in packages, one
package is already built and 10 µs short) and route C, whose ceiling nobody has measured and which
is the only thing left that could in principle reach 60. **Measure route C's ceiling before promising
anything about 60 FPS again.**
