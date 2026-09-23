# Session 106 — under `dawalk=1` GuestGpu waits +616 µs a flip on `PipelineCache::m_mutex` (its on/off-CPU split inferred, not measured); `dabatch=8` shipped (Δ mean `dt` −169.3 µs)

**Single source of truth for session 106.** Mirrored into git as `docs/local-session-106.md`.
Harness root `C:/kyty/s106`. Everything below is measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned: median of block means `dt_us` ≈ 31.6 ms (`dwk104` arm `dawalk=1`; the mean is 31 772 µs, 0.525×), game speed ≈ 0.53×.
**Speedup this session: Δ mean `dt` −169.3 µs pinned ≈ +0.55 % game speed** (`dab106`; unpinned default setup
not measured). 60 FPS stays the direction without a route with a live estimate.

---

## 1. Result

1. **Exploratory re-reading of `dwk104`** (not a test; `explore106_dwk104.py`, the `dwk104.py` blocks and
   quartets, 92 pairs; its numbers reproduced: Δ`dt` −265.9, Δ`cpu_gpu_us` −462.0): **D = Δ`dt` − Δ`cpu_net` =
   +192.5 µs (SE 30.8 / t 6.25 over 46 quartets; over the 92 pairs SE 25.9, t 7.44)**, GuestGpu wall not on its CPU 866 → ~1 058 µs a flip. Side shifts (t ≥ 3): submits
   −2.8 a flip, `release-mem-irq` submit site −3.8, record-thread sleeps −3.5, record-thread spin +424 µs,
   `prot_spin_gpu_us` +134, `rec_direct_us` +110.
2. **Instrument `KYTY_GPU_WALL=1`** (measurement only, env var read once, no gate; source `d6b23c0`, build
   `d23094df…`): `gw_idle/blk/flip/proc/cmd` `_ns`/`_n` on `FrameTrace-x`, live in lite, 0 without the variable.
   Decision recorded before code (`276437f`).
3. **`gw106`** (sealed `pred/01_gwall.md` `432e3c5b…`, ABBA `dawalk=0|1` with `plkstat=1` both arms, 600 s,
   pinned, 94 pairs, ADMITTED): **NAMED `lock_wait_us`** — GuestGpu waits on `PipelineCache::m_mutex` 92.5 → 710.5 µs
   a flip (Δ +616.5, t 210): `pl_prog_wait` 43 → 204, `pl_pipe_wait` 47 → 234, `pl_cs_wait` 2 → 270 (268
   acquisitions). ΔD +109.8 (2·SE 43.6); ΔR −518 (t −23). **Corrected by the audit (§7 item 1):** plkstat's wait is
   the whole acquisition wall (spin of the `CRITICAL_SECTION`, 4 000 iterations, is on-CPU and inside `cpu_net`), so
   the decomposition is not a partition and "NAMED" means "the largest wall term", not "explains D". That most of
   the +616 µs is spin is an INFERENCE (it needs the other off-CPU waits not to have fallen by > ~210 µs) and a split
   of R that pred/01 §7 forbade. Holder [I]: the walker thread (`QueueAhead` under the lock, `da_queue_us` 851 incl.
   its own wait, 134 calls of 64; `PrefetchComputePipeline` under the lock) — plkstat sees only GuestGpu's waits.
   Predictions: G1 G2 G5 G6 HIT; **G3 (R carries) and G4 (lock ≤ +100) MISS**.
4. **`dab106`** (sealed `pred/02_dabatch.md` `bde73d27…`, ABBA `dabatch=64|8` under `dawalk=1`, no `plkstat`,
   no `KYTY_GPU_WALL`, 600 s, pinned, 94 pairs, ADMITTED): **SHIP — Δ mean `dt` −169.3 µs (2·SE 94.1, t −3.60)**;
   Δ`cpu_net` −180.3 (t −3.80); `da_qcall` ×8.06; `da_queue_us` +214 and `da_walk_us` +323 on the walker thread;
   `da_miss` +7.7 (t 1.76). Video `vdb106` (gate text `dabatch=8`, pinned): 3 989 frames, 0 glitches. B1–B6 all HIT.
   Audit: permutation p 0.0003, bootstrap 95 % CI [−265, −79]; frame time is vblank-quantised — the gain is +26
   short frames of 2 726 an arm (per-pair median −15 µs), real in the mean (game speed), not a uniform per-frame
   saving and not additive with other candidates; that it works by shortening walker holds is [I] (no plkstat).
5. **Shipped:** knob `dabatch` default 64 → **8** (`8736198`), decision recorded before the edit (`b3ed604`); build
   **`2b30f836…`**; video `vid106` with the compiled default (pinned): **3 993 frames, 0 one-frame glitches**,
   `da_qcall` median 1 067 a flip (the default is in force).

## 2. Harness

`C:/kyty/s106`, ported by a fresh `C:/kyty/s105/s106_port.py` (sha256 `70157bbf…`): `PRECONDITIONS PASS: 5 root
constructs; 44 sealed texts (42 land in prev105/pred, 2 stay in carried prev103/pred and prev100/pred); 31 live
paths (20 files) + 10 expression paths (8 files); gates 1092 B / 99 names (sha 303a7849..., dawalk=1, no ctxtick);
gates.cpp 136 entries (111 gates + 25 knobs); ABSENT 37` → `PORT DIAGNOSTIC: clean; carried=6387 ledger=61
skipped=41`. New: `gw106.py` (+`make_gw106.py`, `fixture_gw106.py`: two fixtures, R-effect and flip-effect, each
named its term before the seal), `dab106.py` (+`make_dab106.py`, `fixture_dab106.py`), `go106.sh`, `go106b.sh`,
`gates_dab8.txt`. Both derived scorers hash themselves into their output (`scorer_sha256`).

## 3. Source, builds, provenance

Commits: `600b500` (session 105 close), `276437f` (records before action), `d6b23c0` (instrument), `49a13e7`
(seal 01 + scorer + port), `8ab9b5d` (gw106 result + candidate record), `92fce7e` (seal 02 + scorer), `b3ed604`
(ship decision), `8736198` (`dabatch` default 8), the session commit. Builds: `d23094df…` (instrument; gw106,
dab106, vdb106), `2b30f836…` (default 8; vid106, installed). Nothing under `src/graphics/shader/**`; gate tables
unchanged in shape (`check_gate_order.py`: clean). No push.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `gw106` | ABBA `dawalk=0|1` + `plkstat=1`, `KYTY_GPU_WALL=1`, 600 s | ADMITTED, NAMED `lock_wait_us` (+616.5 µs) |
| `dab106` | ABBA `dabatch=64|8`, 600 s | ADMITTED, SHIP (Δ`dt` −169.3) |
| `vdb106` | video `dabatch=8` gate text, pinned | 3 989 frames, 0 glitches |
| `vid106` | video of build `2b30f836` (default 8), pinned | 3 993 frames, 0 glitches |

## 5. Next

First measure what `gw106` could not: the holder (hold counters on the walker's `PrefetchComputePipeline` and
`QueueDrawAhead`) and the spin share of each wait (try-lock first; thread cycle time only around a failed try),
at `dabatch=8`. Then the other half of the contention — `PrefetchComputePipeline` holds `m_mutex` around
`m_program_cache->Get` (which runs `MaterializeResources` incl. the SRT walk) on the walker (`pl_cs_wait` +268 µs at
268 dispatch acquisitions in `gw106`; `dabatch` should not touch it [I]): a per-thread "already present" memo that
skips the lock, keyed on the `PrepareProgram` result plus a hash of the user SGPRs, stamped with atomic mirrors of
`programs_epoch`/`memo_generation`/`ShaderRegistrations()` (sketch: audit code lens), behind a gate with its own
sealed ABBA. Then M3.2. Plan: `docs/next-session-107.md`.

## 6. Proved, and not proved

**Measured.** Under `dawalk=1` GuestGpu's wall at `PipelineCache::m_mutex` acquisitions grows +616 µs a flip;
`dabatch=8` shortens the mean frame by 169 µs pinned; both videos clean. **Inferred, not measured.** That most of
that wait is spin inside `cpu_net`; that the walker is the holder; that `dabatch` works by shortening holds; where
the +110 µs of D goes. **Not proved.** The unpinned default setup's gain; how much of the remaining +268 µs `cs`
wait a code fix removes; 60 FPS.

## 7. Adversarial audit

Two lenses (recount + protocol; code review of `d6b23c0` and `8736198`), sealed as `pred/03_audit106.md` (5 540 B,
`b5b9695f…`). **Recount CONFIRMED** (every number reproduced by independent code; `dab106` permutation p 0.0003,
bootstrap CI [−265, −79]). **Protocol HOLDS** (records before actions, seals before runs, hashes match, pin on
every run, no other file changed during the sealed windows). **Code NOT REFUTED** (the instrument is inert without
its variable; `dabatch=8` queues the same requests). Findings:

1. **MAJOR (both lenses):** the lock-mechanism claim exceeded the data — plkstat's wait is the whole acquisition
   wall, spin is on-CPU inside `cpu_net`, so D = idle + blk + flip + lock + R is not a partition; "most of the wait
   is spin" is an inference and a split of R forbidden by pred/01 §7. Title, §1 item 3 and §6 corrected above.
   The ship stands on Δ`dt` measured directly.
2. Frame time is vblank-quantised (the gain is +26 short frames of 2 726; per-pair median −15 µs; S1 sensitive:
   −88 without the 10 most negative pairs, halves −230 / −109) — not additive with other candidates.
3. Exploratory SE was over quartets (over pairs: SE 25.9, t 7.44). 4. "~6.3 µs a hold" includes the walker's own
   wait; GuestGpu's gap is ~3 µs per acquisition. 5. Holder identity and the `dabatch` mechanism are [I].
6. Medians of block means were labelled means. 7. **A heartbeat ran `cat` + `tasklist` during `dab106`** (outside
   kept rows; dropping blocks 20–27 gives −170.9) → rule: during a sealed run a heartbeat only reschedules.
8. Fixture gaps (no effect planted in the lock term that was named; the ship branch and video re-read never
   exercised; no KEEP case) → rule: plant an effect in every decision term and exercise every verdict branch.
9. Fixture run on the pre-seal copy. 10. Build `d23094df` from the working tree before its commit (same content);
   "identical behaviour to `810bb54b` plus dark counters" has no A/A. 11. `vid106` not machine-scored (hand-checked
   twice). 12. Stale labels (`gates.h` "64 = the constant it replaces"; ROADMAP rows calling the lock uncontended).
13. `dabatch=8` costs ~+70 µs a flip [I] on the rare `dawalk=0`/walker-drop path. 14. `pl_*` sum all threads'
   shards (valid while `m4baton=0`); D also contains the TrackingSpinLock spin.
