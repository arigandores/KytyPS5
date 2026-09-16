# Session 74 — FACTS

**Single source of truth for session 74.** Every number here was produced by running the named tool
on the named log. Where a number is an estimate it says so in those words. Where something was not
measured it says NOT MEASURED and names what would measure it.

Tree: `merge-upstream`, base `ca2a8ae` (session 73's `d04cff7` plus its doc commit).
Installed binary: **`017FC03107D569CA047E24F802CCCE0D9187A21AFF747EE7A0F622D8E42631C3`**
(short `017fc031`), 23 555 584 bytes.
Five binaries carried runs; each run's `<tag>.json` records which, and guards check 10 verifies it:

| binary | what it is | runs |
|---|---|---|
| `86e9f125` | M4 counters + the four `dg_*` counters | `smk74a`, `base74a`, `m4r74a`, `m4r74b` |
| `8d5c6485` | + the clean-page probe | `probe74a` |
| `01315ff6` | + the table behind gate `dawitcg`, default 0 | `cgv74a`, `aa74a`, `cg74a`, `cg74b` |
| `63af1620` | + `dawitcg` shipped at 1 | `acc74a` |
| **`017fc031`** | **+ one comment in `gates.cpp` — INSTALLED** | `acc74b` |

---

## 0. In one sentence

The session **killed both patches session 73 left ready** — one does not compile and one is unsound
with a population 4.4× smaller than the number that justified it — **answered M4's transport
question negatively by measurement**, and then **shipped a third win from the M1 witness's clean
loop**: the loop's page table now survives the `AheadTake` call under a new monotonic GPU-dirty
generation, **−0.31…−0.32 ms of CPU wall per frame, t = −11.84**, with `da_cl_miss` collapsing
**15 140.6 → 1 406.3** per frame. Every step was priced before it was written: a four-counter
reading sized the witness's bump rate at **0.515 %** of the table-build rate, and a 60-line probe
predicted the post-patch miss count at **1 402.9** — which the shipped gate then reproduced **to
0.03 %**.

**0.31–0.32 ms of CPU shipped this session, on top of session 73's 0.37–0.41 ms.**

---

## 1. The runs

| tag | what | hold | entry | `pre_run` | binary | verdict |
|---|---|---:|---:|---|---|---|
| `smk74a` | smoke, video | 90 s | 18.4 s | 2.0 % / 27.6 W | `86e9f125` | 0 errors |
| `base74a` | base + the four `dg_*`, video | 300 s | 14.9 s | 2.0 % / 28.6 W | `86e9f125` | **9 PASS, 0 FAIL, 0 WARN**, 0 glitches / 8516 |
| `m4r74a` | `m4baton=32` | 180 s | 15.3 s | 2.0 % / 28.2 W | `86e9f125` | 0 errors, `bat_drop` 0 |
| `m4r74b` | `m4baton=128` | 180 s | 15.9 s | 2.0 % / 29.1 W | `86e9f125` | 0 errors, `bat_drop` 0 |
| `probe74a` | the clean-page probe | 300 s | 15.3 s | 2.0 % / 28.1 W | `8d5c6485` | 0 errors |
| `cgv74a` | `dawitcg=1 dawitcgcheck=1` | 180 s | 14.8 s | 2.0 % / 28.3 W | `01315ff6` | **0 MISMATCH**, `da_cl_bad` 0 |
| `aa74a` | idle A/A | 300 s | 14.9 s | 3.0 % / 29.8 W | `01315ff6` | FAIL check 6 — Slack, §6.1 |
| `cg74a` | ABBA `dawitcg=0\|1` | 300 s | 16.3 s | 2.0 % / 28.7 W | `01315ff6` | FAIL check 6 — host noise, §6.2 |
| **`cg74b`** | **ABBA `dawitcg=0\|1`, the decision** | 300 s | 16.3 s | 2.0 % / 27.8 W | `01315ff6` | **10 PASS, 0 FAIL, 0 WARN** |
| `acc74a` | acceptance, video | 300 s | 15.4 s | 3.0 % / 28.1 W | `63af1620` | **8 PASS, 0 FAIL, 1 WARN**, 0 glitches |
| `acc74b` | acceptance on the INSTALLED binary, video | 300 s | 14.9 s | 7.0 % / 30.8 W | `017fc031` | **9 PASS, 0 FAIL, 0 WARN**, 0 glitches |

**Eleven runs, every one entered Sky Garden at the first attempt**, in 14.8–18.4 s.
**0 `GpuWaitSlow` / `GpuHangAbort` / `ErrorDeviceLost` / `Unhandled exception` / `MISMATCH` / `VUID`
in all eleven logs.** `guards.py` check 2 reads **11/11** self-check counters present and zero on
every run — eleven, not ten, because this session taught the guard about `da_cl_bad`.

**Between-run absolutes are not measurements.** This session's own spread on identical
configurations makes the point better than any argument:

| tag | draws/fr | cpu/draw | `cpu_gpu_us` | `gpu_busy_us` | `dt_us` | FPS |
|---|---:|---:|---:|---:|---:|---:|
| `base74a` | 5039.3 | 6.5805 | 33 161 | 15 024 | 36 032 | 27.75 |
| `probe74a` | 5043.9 | 6.3711 | 32 135 | 13 014 | 32 505 | 30.76 |
| `aa74a` | 5040.3 | 6.3121 | 31 815 | 13 725 | 32 133 | 31.12 |
| `cg74a` | 5037.9 | 6.2363 | 31 418 | 14 043 | 31 826 | 31.42 |
| `cg74b` | 5050.3 | 6.4311 | 32 479 | 13 990 | 34 911 | 28.64 |
| `acc74a` | 5042.3 | 6.4227 | 32 385 | 14 832 | 32 813 | 30.48 |
| `acc74b` | 5042.3 | 6.6515 | 33 539 | 14 432 | 36 025 | 27.76 |

`cpu/draw` spans 6.236…6.694 (**7.3 %**) and FPS 27.75…31.42 across runs whose draws per frame agree
to 0.25 %. **Only the in-run ABBA is a measurement.**

---

## 2. W8 — the clean loop's table, shipped

### 2.1 What was established before a line of the table was written

Session 73 left the question as reading: is there, or can there be, a monotonic witness for
"something that was GPU-clean has become GPU-dirty"? The answer is yes, and the surface is small.
`IsGpuCleanRange` (`kernel/memory.cpp:1031-1040`) is the whole predicate and reads exactly
`BufferCache::HasGpuDirtyBytes` and `TextureCache::IsRegionGpuModified` — **it never reads the
MemoryTracker's GPU page bits**, so `Mark/UnmarkRegionAsGpuModified` are not in the surface at all.
Half the witness already exists: `NoteGpuWrite` (`bufferCache.cpp:1948-1949`) opens with
`++m_gpu_write_seq` and has exactly one call site, immediately after the only `Add`.

**The naive form — bump at every site — is refuted by measurement, not by argument.**
`renderDraw.cpp:812` alone is counted exactly by `rt_fast_ok`, which reads **17 376.4 per frame** on
`base74a` against `da_hit + da_miss` = **8 700.5** clean tables per frame: **2.00 bumps per table**.
A table keyed on it would be flushed twice during the life of each call it is meant to outlive.

**The transition-guarded form was then measured, on four independent runs:**

| run | `dg_img` | `dg_buf` | sum | tables | ratio |
|---|---:|---:|---:|---:|---:|
| `smk74a` | 19.952 | 24.499 | 44.451 | 8 437.9 | **0.527 %** |
| `base74a` | 20.269 | 24.511 | 44.780 | 8 700.5 | **0.515 %** |
| `m4r74a` | 20.816 | 24.504 | 45.320 | 8 721.1 | **0.520 %** |
| `m4r74b` | 16.063 | 24.499 | 40.562 | 8 698.2 | **0.466 %** |

`dg_img` is `Image::MarkGpuModified` guarded on the flag having been false — **857× fewer than the
calls**. `dg_buf` is the one `m_gpu_modified_ranges.Add` restricted to Adds that actually grew the
covered set — **24.5 of 1 041.6, so 97.6 % of Adds land inside an already-covered range**.
`dg_img_cl` equals `dg_img` to one count in 129 801 on `base74a`: images cycle dirty and clean in
perfect balance.

### 2.2 The probe — the prize predicted before the table existed

Adversarial reading of the tree found that the prize was **not bounded away from zero** by anything
in it. After gate `dawitcp` a miss costs one `Pages::Find`, one cross-TU `Memory::IsGpuClean`,
`IsGpuThread`, one `RangeSet::Intersects`, one `IsRegionGpuModified` answered from the lock-free
hint, three `FrameStats::Add`, two `Gates::Enabled` and one `Store` — **25-40 ns, hard ceiling
53 ns** — and the number of misses that would SURVIVE the table is `bumps × U + residual`, where U
is the union of distinct clean pages inside one generation epoch and is bounded only by
`1.734 <= U <= 336.9`. **At the top of that range the table saves nothing.** Nothing in the tree
measured U.

So the table was not written yet. A **60-line probe** was: a thread-local direct-mapped array of
`{page, stamp}` with the same 4096 slots and the same slot function the real table would use,
stamped with a monotonic key that moves when either witness moves, never filled, never read back —
its only output is `da_cl_pmiss`, **the predicted post-patch `da_cl_miss`**. It deliberately does
not model `Pages::last`, so it can only over-count.

`probe74a`, 7265 settled frames:

    da_cl_miss    15 098.406 /frame   today
    da_cl_pmiss    1 402.875 /frame   predicted  ->  a 10.8x cut
    da_cl_pdrop       12.011 /frame   the stamp moves 12 times, not the 44.8 the bumps suggest:
                                      generation moves CLUSTER between lookups, so the table lives
                                      ~2 660 lookups per epoch, not the ~712 the bump rate implies
    da_cl_live == da_cl_miss == tgm_call == tgm_hint == 15 098.406, all four TO THE DIGIT

### 2.3 The table

Gate **`dawitcg`** (`KYTY_DA_CLEAN_GEN`, **shipped at 1**). `PersistentClean()` mirrors the shipped
`PersistentLive()` with a two-part key — `BackingMapEpoch` and the new `GpuDirtyGen` — and
`ShaderReadCache::clean` becomes a pointer, as `live` already is.

Three things the adversarial review forced, each of which would have cost real time:

* **Bound lazily, not in the constructor.** The four M1 draw-ahead workers construct a
  `ShaderReadCache` too, but install `ReadShaderAheadClean`, which only ever calls `LiveBackingPage`
  — `IsGpuCleanRange` returns false off GuestGpu, so a worker can never store a clean verdict.
  Binding in the constructor gave each worker a 64 KiB table it never queried and inflated
  `da_cl_drop` about fivefold.
* **Tag-invalidated, not cleared.** `PersistentLive` can afford `storage.fill(Page{})` because the
  backing map moves a handful of times in a whole run. This witness moves 44.8 times a frame, so a
  wholesale wipe is ~2.9 MiB of memset a frame on GuestGpu inside the render mutex. `Page` and
  `Pages` grew a `key`; a drop is `++key`. **The live table is untouched**: its key stays 0 on both
  sides of every comparison.
* **The self-check is capped at 40 lines** and evicts the entry it caught. Uncapped, on a branch
  taken ~31 900 times a frame, a systematic staleness would have produced ~10⁶ flushed log and
  console lines a second on GuestGpu inside the render mutex — the operator would have read "the
  build hangs", not "the gate is stale".

### 2.4 Correctness — `cgv74a`

180 s with `dawitcg=1 dawitcgcheck=1`: the real predicate was evaluated alongside **every hit** —
about **98 million checks over 3245 settled frames** — and printed **zero** `DaCleanGenVerify:
MISMATCH` lines, with `da_cl_bad` **0**. `da_cl_fail` and every `da_stale*` also 0.
`guards.py` check 2 now judges `da_cl_bad` automatically: **11/11**, not 10.

### 2.5 The measurement — two ABBA runs

| run | pairs | `cpu/draw` | 2·SE | t | whole-arm `cpu/fr` | guards |
|---|---:|---:|---:|---:|---|---|
| `cg74a` | 130 | −0.763 % | 0.151 % | −10.12 | 31 511 → 31 337 = **−174 µs** | FAIL check 6 (§6.2) |
| **`cg74b`** | **116** | **−0.956 %** | **0.162 %** | **−11.84** | 32 657 → 32 333 = **−324 µs** | **10 PASS, 0 FAIL** |

The clean run is the authority: **−0.31…−0.32 ms of CPU wall per frame** (paired −0.956 % of
32 657 µs = −312 µs; whole-arm −324 µs). Work check −0.028 % apart; whole-arm ratio of sums
−0.964 % against paired −0.956 %, gap **0.008 pp**. FPS 28.47 → 28.80 in `cg74b`, 31.33 → 31.50 in
`cg74a`.

**Armed, and behaviour bit-identical, in both runs** (`cg74b` shown):

    da_cl_drop     0.015 -> 12.048      reachable only through the gated bind
    da_cl_miss  15 140.6 ->  1 406.3    a 10.8x collapse
    da_cl_pmiss  1 406.7 /  1 404.7     the probe, which arm1's ACTUAL da_cl_miss 1 406.295
                                        lands on to 0.03 %
    da_hit == da_direct in both arms (8 646.834/8 646.865 and 8 639.781/8 639.748)
    da_cl_fail = da_cl_bad = da_stale* = 0

**`gpu_busy_us` reads +0.157 % ± 0.193 % (`cg74a`, noise) and +0.760 % ± 0.486 % (`cg74b`,
significant on its own 2·SE).** This is a CPU-only change and the arms drew the same work to
0.028 %; the rise is the documented booking caveat — `gpu_busy_us` is charged to the interval that
HARVESTS the timestamps, so a faster arm packs more already-submitted work into each interval.
**NOT a GPU regression, and NOT independently verified either** — the clean way to settle it would
be one `KYTY_GPU_TIME` run per arm, NOT DONE.

### 2.6 Acceptance

`acc74a` (binary `63af1620`): **8 PASS, 0 FAIL, 1 WARN, 3 SKIP — VERDICT PASS, 0 one-frame
glitches**; CPU 32 385 µs, GPU 14 832 µs, wall 32 813 µs, **30.48 FPS**.
`acc74b` (the INSTALLED `017fc031`): **9 PASS, 0 FAIL, 0 WARN, 3 SKIP — VERDICT PASS, 0 one-frame
glitches**, check 10 confirms the binary. `da_cl_miss` = `da_cl_pmiss` = 1 401.786, `da_cl_bad` 0.

`acc74b` was taken only because a comment-only rebuild had changed the installed hash after
`acc74a`; the two differ by one comment in `gates.cpp` and nothing else.

---

## 3. M4 / the transport fork — answered negatively, by measurement

Session 73 named the kill condition before any run: *"`rng_inpass / rng_total` near 1.0 at every L
that makes the splice tolerable ... there is no operating point, and the transport fork is answered
negatively by arithmetic before a line of it is written."*

**Measured:**

| L | hand-offs/frame | in an open pass | ratio | splice | CPU tax | GPU tax |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 163.272 | 154.102 | **94.38 %** | 11.76 µs | 1.033 ms | 237 µs |
| 128 | 38.909 | 36.163 | **92.94 %** | 11.33 µs | 0.292 ms | 56 µs |
| 512 | ~0 internal (session 68) | — | — | — | — | nothing to fork |

**The ratio does not fall with L.** Raising L does not buy a smaller in-pass fraction; it destroys
the boundaries themselves, because they collapse onto the submission slices — and the slice count is
**12.42 at L=32 and 12.55 at L=128, invariant in L** (`rng_total` against
`bat_ranges + bat_self_ranges`, which reproduces session 68's 171.65 ranges/frame at L=32 as
175.693). At L=512 session 68 measured ranges/frame equal to the slice count, i.e. **zero internal
hand-offs**. `bat_drop` read **0 on every frame of both runs** — the built-in overlap detector.

**`cram_write` = 0.000 per frame** at the defaults and in every run. `m_const_ram` is 49 152 of the
55 955 bytes a register-context fork would copy, so **the fork is 6 803 bytes, not 55 955** — 87.8 %
of the sizing question closed at zero extra runs.

**Verdict: there is no operating point.** At every L where a fork would have something to fork,
93–94 % of its hand-offs land inside an open render pass; the only L that makes the splice small is
the L at which the hand-offs cease to exist.

### 3.1 The patch session 73 left for this does not compile

`C:/kyty/s73/patch_m4_range.py` inserts `FS::Add(FS::Counter::ConstRamWrites, 1)` into
`CommandProcessor::WriteConstRam` at `graphicsRun.cpp:453`, where **no `FS` alias is in scope** —
every `namespace FS = Common::FrameStats;` in that file is block-scoped, at :1259, :1311, :1472,
:1541, :1657. `PATCH_DRY=1` passes because it only checks anchor uniqueness. Its `5044 / L` boundary
model is also wrong: session 68's own logs give 171.65 / 50.42 / 20.79 ranges per frame at
L = 32 / 128 / 512 against the model's 157.6 / 39.4 / 9.9 — an error reaching **2.11× exactly where
the patch proposed to look**. Both defects are fixed in `C:/kyty/s74/patch_m4_range_fixed.py`, which
also counts hand-offs rather than range starts. The session-73 file carries a banner.

---

## 4. `clrwide` — closed, on soundness AND on population, without a run

### 4.1 It is not sound

When `ClearImageFromBuffer` returns true the caller **consumes the guest dispatch**
(`renderCompute.cpp:379-383`). On an EXACT match that is safe: the image spans the whole fill range
and now owns it. Under CONTAINMENT the bytes of `[fill_base, image_base)` and
`[image_end, fill_end)` are then written by **nobody** — no guest store loop, no host buffer write,
no `m_gpu_modified_ranges.Add`, no `NoteGpuWrite`, no `InvalidateMemoryFromGPU`. `ClearImage`
touches one image and `CommitGpuWrite` records no range at all. The remainder has no owner and no
repair path. The predicate also bounds nothing about `size − image_size`: a 4 KiB alias inside an
8 MiB fill would drop the whole 8 MiB dispatch and clear 4 KiB.

### 4.2 Its population is 4.4× smaller than the number that justified it

`clr_over` is an **image count summed over declined fills**, not a fill count
(`textureCache.cpp:2499-2502` increments per image; `:2507`/`:2517` flush the accumulated total, and
`frameStats.h:678-679` says exactly this). Dividing 3.776 images by 14.825 fills to get "roughly a
quarter of the declined fills" is a category error.

Decomposed from the session's own logs, with no new run:

* On `base73a` `clr_over` is **ternary** — 0 on 18.1 % of frames, 4 on 17.2 %, 5 on 64.7 % — and
  **never 1, 2 or 3**.
* Conditioned on `clr72a`'s trace, **100 % of it comes from the single fill `0x53be70000`**: on the
  1023 frames that fill reads `ok`, `clr_over` is **0 on every frame**, while ~14 other fills still
  decline. The other declined fills have **zero** byte-overlapping images.
* Ceiling: **≤ 0.849 fills/frame (5.7 %, not 25 %)** and ≤ 7 343 KiB/frame.

### 4.3 Where the declined bytes actually are

Re-reading `C:/kyty/s72/log_clr72a.txt` (101 516 traced fills over 4691 frames):

| declined fill size | per frame | KiB/frame | % of declined bytes |
|---|---:|---:|---:|
| < 64 KiB | 7.802 | 209.7 | 1.3 % |
| 64–256 KiB | 2.170 | 191.5 | 1.2 % |
| 256K–1 MiB | 3.092 | 798.4 | 5.1 % |
| 1–4 MiB | 0.006 | 14.2 | 0.1 % |
| **≥ 4 MiB** | **1.734** | **14 419.6** | **92.2 %** |

and those 1.73 fills are two addresses: `0x55ac08000` (8192 KiB, **never accepted in the whole
log** — the clear shader's own storage buffer) and `0x53be70000` (8640 KiB, declined 0.735/frame and
accepted 0.218/frame at the *same base and size*). The second toggles almost every frame — **580
`ok` blocks of median 1 frame against 580 `none` blocks of median 4**, exactly one fill per frame —
so an exactly matching image exists on ~23 % of frames and is absent on the rest. **That is a
registration-lifetime question, not a size question**, and widening exact → contained does nothing
for either address.

Other defects found: accepting a fill skips `TrackDccFill`, the only producer of `PendingDcc`
entries (the crowd-silhouette regression class of sessions 9 and 21); "`full_image` stays true" is
false for a depth image with stencil; and the best case is at or below the stand's honest GPU
resolution. `C:/kyty/s73/patch_clrwide.py` carries a banner and must not be run.

---

## 5. Two open items closed offline, with no runs

### 5.1 §9.9 — why between-run GPU comparison is void

From three session-73 logs already on disk:

| run | `img_up`/fr | KiB/upload | `rt_att` | `gpu_busy_us` |
|---|---:|---:|---:|---:|
| `base73a` | 18.791 | 7 861 | 12 497.4 | 15 110 |
| `wcp73a` | 14.866 | 6 849 | 12 492.5 | 12 896 |
| `acc73a` | 18.678 | 7 802 | 12 494.7 | 14 867 |

`rt_att` agrees to **0.04 %** — the rendered content is identical. The swing is the upload **count**,
at **517–564 µs of GPU per upload** on both pairs. Video recording is refuted as the cause:
`fus73a`, which had no `--rec`, carries the highest count of all (19.650). **What drives the count
itself is still NOT ATTRIBUTED**; what is attributed is the mechanism by which it voids every
cross-run GPU comparison.

### 5.2 §9.6 — the DRS rung does not always latch

| run | high-rung share | episodes | median length | Q1 / Q2 / Q3 / Q4 |
|---|---:|---:|---:|---|
| `base73a` | 3.3 % | 5 | 62 fr | 13.2 / 0.0 / 0.0 / 0.0 % |
| `aa73a` | 54.1 % | 132 | 24 fr | 60.6 / 32.9 / 46.9 / 76.0 % |

`base73a` latched low after the first quarter and never returned; `aa73a` oscillated the whole run.
**Whether a run latches is itself the variable**, and it is what moves the stand's `gpu_busy_us`
2·SE by a factor of four. **Why it latches is still NOT ESTABLISHED.**

---

## 6. Failures recorded openly

### 6.1 `aa74a` — the stand is contaminated and is not quoted

`+0.334 % ± 0.260 %` on `cpu/draw`, t = +2.57, honest resolution 0.593 %. Check 0 WARN names
`slack.exe`, which restarted itself during the run, and check 6 FAILs on 9 of 49 core groups.
**The stand of this session is therefore not usable as a threshold**; both decisions were taken from
the measuring run's own 2·SE (0.151 % and 0.162 %), which is the session-73 rule for GPU applied to
CPU as well. The bias runs **against** arm1, which is where the gate is on, so it understates the
improvement.

### 6.2 `cg74a` — check 6, and why the number survives

8 of 50 core groups more than 10 % off their arm median, with `pre_run` clean and no foreign process
on the GPU. The deviations are **symmetric and bidirectional**: 5 groups in arm0 and 3 in arm1, at
+12.2 / −11.5 / +10.1 / −10.2 / −11.3 % and +10.3 / −11.1 / −10.1 %. A paired-by-block estimator
cancels exactly that, and the signature is visible — whole-arm −0.769 % against paired −0.763 %, a
gap of 0.006 pp. `cg74b` was taken to settle it and came back **10 PASS, 0 FAIL, 0 WARN** with a
LARGER effect, consistent with noise having diluted the first. **What used the machine during those
groups is NOT ESTABLISHED**; the likeliest source is the agent tooling resident on the same host.

### 6.3 A comment-only rebuild invalidated an acceptance

`acc74a` was taken, then one comment in `gates.cpp` was tidied, which changed the installed hash and
would have made guards check 10 fail on the very run that accepted the ship. `acc74b` was re-taken
on the final binary. **The session-73 trap is confirmed to bite in both directions: do not rebuild
between acceptance and the final answer, for any reason.**

---

## 7. What this session did NOT close, with the next measurement named

1. **The live loop's 0.896 ms.** W3 (`PrefetchVectorData`'s 192-byte cap), W4 (prefetch with real
   distance) and W5 (`SameRecordedWords`' 4-byte compare) are still unwritten. This is now the
   largest named CPU article that is not M4.
2. **The clean loop's residue.** `da_cl_miss` is 1 402–1 408 per frame after W8, down from 15 098.
   At 25–40 ns that is 35–56 µs — below the stand. *Next step, if it is ever wanted:* nothing; the
   article is spent.
3. **Whether W8's `gpu_busy_us` rise is really frame packing** — NOT INDEPENDENTLY VERIFIED.
   *Next measurement:* one `KYTY_GPU_TIME` run per arm, comparing `GpuTime-kind` shares rather than
   per-interval absolutes.
4. **Why the upload count gyrates 14.9–20.0 per frame** — the mechanism is attributed (§5.1), the
   cause is not. *Next measurement:* `imgwhy.py` on two runs at opposite ends.
5. **Why the DRS rung latches** — NOT ESTABLISHED (§5.2). *Next measurement:* one 300 s base run
   with `KYTY_POKE="27e46c:909090909090"`, reading `GuestOut:` around each `rt_kpx/rt_att` crossing
   of 2600.
6. **The wall-clock cost of the counters — still NOT MEASURED**, and session 73's named method (an
   A/A on `bac1155d` against one on `a57a6f50`) is **void**: that binary no longer exists, and the
   programme's own rule forbids between-run comparison anyway. *Better next measurement, designed
   and not run:* one ABBA on `fslean=0|1`, which silences every counter past `Counter::LogNs`
   in-run. It measures the accumulate half only — `Scope`'s `NowNs()` reads are gated by
   `TimingsEnabled()` and are unaffected — so it is a lower bound, and it must be stated as one.
7. **The external C3 closure `c3_pop == img_skip` — NOT RUN for the fourth session.**
8. **Whether `KYTY_GPU_TIME`'s mark loss is selective against the detile phase** — carried from
   session 72, untouched.
9. **The sequential mutating floor is above 13.9–14.9 ms by an unmeasured amount.**
10. **`0x53be70000`'s registration lifetime** (§4.3): why an image with exactly that base and size
    is registered on ~23 % of frames and absent on the rest. This is the only live question left in
    the `clr_none` area, and it is a READING question.
11. **Gate `dawitfb` is still dead code with an empty population**, kept at 0 as the record.

---

## 8. Code and tools

### 8.1 Source, 10 files + 1 new

**One shipped gate:** `dawitcg` (`KYTY_DA_CLEAN_GEN`) **0 → 1** — −0.31…−0.32 ms of CPU
(`cg74b`, 116 pairs, t = −11.84).
**One self-check gate, default 0:** `dawitcgcheck` (`KYTY_DA_CLEAN_GEN_VERIFY`).

**New file:** `graphics/host_gpu/gpuDirtyGen.h` — one `inline constinit std::atomic<uint64_t>`,
`Bump()` and `Read()`. Bumped at exactly two sites, **after** the state change at both.

**Nine counters**, all past `Counter::LogNs` so `fslean=1` silences them (`gates_base.txt` pins
`fslean=0`; leave it):

* `dg_img`, `dg_img_cl`, `dg_buf`, `dg_buf_all` — the witness's bump rate and its denominator.
* `da_cl_pmiss`, `da_cl_pdrop` — the probe: the predicted post-patch miss count.
* `da_cl_drop`, `da_cl_bad` — the table's arming proof and its self-check.
* `rng_total`, `rng_inpass`, `cram_write` — M4 (three of them, so twelve in all).

**Non-counter edits:** `RangeSet::Add` returns whether the covered set may have grown. The early
return was proved **exactly equivalent** to the existing body by construction, by a 48 M-case brute
force over the reachable state space, and by a differential test over 179 827 real Adds with zero
disagreements; `Add() == true` is **exactly** `!Contains(address, size)`. It is also strictly
cheaper — it skips a node erase and re-insert on 97.6 % of Adds, an estimated **20–50 µs/frame**.
**That win is ungated and lands in both arms, so no A/B of this session can see it: it is recorded,
not claimed.** `ShaderReadCache::Page`/`Pages` grew a tag (`key`, `key_gen`) and `Pages::Evict`.

**Checks:** six clean builds, 0 errors and no new warnings; five test binaries pass (plus
`memory_tracker_tests` with `KYTY_ARM_DEFER=1`) and the four `shader_recompiler_compute_tests`
groups that touch the tiler and the image-view cache; `resource_tracking_tests` fails as always with
a **byte-identical 1478-byte log, sha256 `06aef666…`**, matching s60/s63/s64/s67–s73.

### 8.2 Harness `C:/kyty/s74`

Port of `C:/kyty/s73` with the roots rewritten; session 73's applied one-shot patches are parked in
`prev73/`, 72's in `prev72/`, 71's in `prev71/`. `.txt`/`.json` copied byte-exact.
`gates_base.txt` now pins **97 names — 82 gates and 15 knobs, 1072 bytes**; `gen_gates.py --check`
exits 0 and `--selftest` passes.

**`guards.py` gained a row**: check 2 now judges `da_cl_bad` through
`DaCleanGenVerify: MISMATCH`, so it reports **11/11** self-check counters, not 10
(`patch_guards_cleangen.py`, applied).

New patch scripts: `patch_m4_range_fixed.py`, `patch_cleanprobe.py`, `patch_cleangen.py`,
`patch_ship_cleangen.py`, `patch_guards_cleangen.py` (all applied) and
`patch_clrover_split.py` (**written, validated, deliberately NOT applied** — superseded before it
was built, kept as the record of the design).

Three session-73 files carry banners and must not be run: `patch_m4_range.py` (does not compile),
`patch_clrwide.py` (unsound), and `patch_clrover_split.py` (superseded).

---

## 9. The arithmetic, restated

**Today**, at the final shipping defaults (`acc74a`, the cleaner of the two acceptances):
CPU **32 385 µs**, GPU **14 832 µs**, wall **32 813 µs**, **30.48 FPS**.

**CPU is still the wall**, and the deficit has barely moved.

| article | axis | measured | state |
|---|---|---:|---|
| `dawitptr` | CPU | 0.152 ms | shipped, session 72 |
| `daepceil` | CPU | 0.174–0.190 ms | shipped, session 72 |
| `imgfuse` (C1) | GPU / CPU | 1.268 / 0.182 ms | shipped, session 73 |
| `dawitcp` (W7) | CPU | 0.19–0.23 ms | shipped, session 73 |
| **`dawitcg` (W8)** | **CPU** | **0.31–0.32 ms** | **SHIPPED, session 74**, accepted with video |
| `RangeSet::Add` early return | CPU | 20–50 µs (ESTIMATE) | shipped ungated, not measurable by A/B |
| M1 witness, live loop | CPU | 0.896 ms | W3/W4/W5 unwritten |
| M1 witness, clean loop, residue | CPU | 35–56 µs | spent |
| `imgskip` | GPU | 1.142 ms | a ceiling, not a patch |
| C2 (dirty sub-range) | GPU | 0.252 ms | unexamined |
| `clr_none` | GPU | ≤ 0.849 fills/frame reachable | **CLOSED**, §4 |

**Shipped on the CPU axis across sessions 72–74: 1.01–1.07 ms against a deficit of 15.7 ms —
6.4–6.8 %**, up from 4.4–4.9 % after session 73.

**The conclusion is unchanged, and this session sharpened it.** 60 FPS by the median needs the
GuestGpu thread down to its sequential mutating floor, and that needs M4 — but M4's transport is now
answered **negatively by measurement**, not left open: 93–94 % of a fork's hand-offs would land
inside an open render pass at every range length where hand-offs exist at all, and the boundaries
collapse onto ~12.5 submission slices a frame that no range length can move. **The next
M4 question is therefore not the transport but the submission structure itself**, and the largest
remaining article that does not need M4 is the witness's live loop at 0.896 ms.
