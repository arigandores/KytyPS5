# Session 90 — FACTS

**The single source of truth for this session's numbers.** `README.md` is the harness and the
traps, `PLAN.md` §0 is the reading that fixed the plan, `pred/01_bufimp.md` and `pred/02_pmlap.md`
are sealed and were not edited.

Every number below is a **ratio of sums over the settled window** or an **exact zero**. Never a
per-frame identity between two different counters: `videoOut.cpp:1238-1240` snapshots the counters
one at a time, in enum-index order, so parts and whole are sampled hundreds of calls apart.

---

## 0. In one sentence

**D1 was built, it reaches 100 % of the bytes it was built for, and the measurement that matters
is the one nobody had to run: its memcpy was never on the thread this programme measures.**
`CopyGuestToStaging` hands a copy region to the copy pool when it is ≥ 64 KiB and lies inside one
guest mapping (`bufferCache.cpp:219-222`, `ASYNC_COPY_MIN_BYTES = 64 << 10`); the census proves
the second condition holds for **100.00 %** of regions (`bi_ok / bi_try` = 1.0000, `bi_noback` =
`bi_nochunk` = 0) and that the mean region is **306 KB over 1.003 regions an upload** — 4.8× the
threshold. **So the 22.8 MB a frame of "D1" is already parallel, and `bda_up_us` = 2 118.3 µs is
not the memcpy.** And the first A/B of the import is **INVALID**: the import arm loses its
one-vblank frames and gains three-vblank ones, the DRS step moves, the area split reads −21.9 %
and the paired estimator refuses. **Its contrast is quoted nowhere.**

**The session's valid A/B is the other one.** `pgl90a` (`proglap=0|1`, area split +0.001 %, pairs 125/125) divides the last unattributed part of `pg_pm_us`: **the `specialization ==` compare is 76.5 % of the search at 31.77 ns a candidate**, against 23.5 % for `PushData::StartFor` and the loop — the second of the two candidates the brief named — and it prices the whole `proglap` chain at **+504.4 µs a frame = 5.61 ns a mark**, a debt open since session 86. **It is a proof, not work, and nothing here proposes to remove it.**

### 0.1 Defects of this session's own sealed text, listed first

1. **`pred/01` §4 A2 demanded an arm-labelled counter be EXACTLY 0 and no run could give that.**
   `bi_cp` read 0.0003 a frame in the census arm — about one count in 3 567 frames — because a
   frame whose flip straddles an arm boundary carries a count across the label. **This is session
   89's C1 defect, committed by the same hand one section after writing the rule against it.**
   The exact-zero form is legitimate only where the counter is *never* `Add`ed: the pre-schedule
   window, where G1/A1 used it and passed. Repaired in `pred/02` §0.1 as a share (≤ 0.10 %);
   `bim90a` reads **0.0004 %**.
2. **`pred/01` §3 carried the record's unit error into a sealed table** ("22 803.8 KiB"). The
   counter is kB = 1000 bytes. Sealed, not edited; corrected in §5 below.
3. **`pred/01` §1 mistypes the `gates_base.txt` hash prefix as `00c116cd…`.** It is `00c116dc…`.
   Sealed, not edited.
4. **`pred/01` §6 E2 was a band on a quantity the run could not deliver**, because admission
   failed before the endpoint could be read. It is scored NOT EVALUABLE, not HIT.

---

## 1. The runs

| tag | what | pre-registration | verdict |
|---|---|---|---|
| `bim90a` | ABBA `bufimp=1 bufimpcheck=1 proglap=1 \| bufimp=2 bufimpcheck=1 proglap=1`, period 30+1800, `--hold 300`, `--warmup-first` | `pred/01_bufimp.md`, 12 962 B, sha256 `966ca8cf950df2ad` | **INVALID on `area_verdict.py`** — area split **−21.877 %**, pair match **42.9 % (51/119)**, work −0.156 %. **The contrast is quoted nowhere.** The census and the self-check are read as configuration, exactly as session 88 read `dap88a`'s |
| `pgl90a` | ABBA `proglap=0 \| proglap=1`, `bufimp=0` in both arms, period 30+1800, `--hold 300`, `--warmup-first` | `pred/02_pmlap.md`, 7 578 B, sha256 `f03a10937bf7bb9b` | **VALID** — area split **+0.001 %**, pair match **125/125 = 100.0 %**, work **+0.057 %**. `guards.py` 9 PASS / 1 FAIL (check 6, not a criterion) / 0 WARN / 2 SKIP |

Binary **`12b0940a00e951bb…`**, 23 619 584 B, built **twice** (`patch_s90.py`, then
`patch_s90b.py` for the arming counter), installed, and **not rebuilt since** — `guards.py` check
10 confirms it against `bim90a.json`. `gates_base.txt` is back to **1092 B, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`** after this session
overwrote it with a mis-used tool flag (README, and §5 item 5).

---

## 2. §3.1 — D1, built, and its population measured [M, within-arm]

Knob **`bufimp`** (`KYTY_BUF_IMPORT`, 0 / 1 / 2, compiled default **0**) and gate `bufimpcheck`.
`TryImportUploadCopies` resolves each copy region of an upload through
`TryGetBackingPointer` → backing offset → `HostImport::Resolve`, and at 2 `RecordBufferCopies`
issues the copies from the imported chunk buffers instead of from the staging ring, grouped by
source exactly as the multi-piece image import does. **The destination is untouched.**

**The census, read in BOTH arms of `bim90a` (identical code in both, so this is not a contrast):**

| | census arm (`bufimp=1`) | import arm (`bufimp=2`) |
|---|---:|---:|
| `bi_try` — uploads that attempted the resolution | 75.53 | 69.10 |
| `bi_ok` — uploads where **every** region resolved | 75.53 | 69.10 |
| **`bi_ok / bi_try`** | **1.0000** | **1.0000** |
| `bi_reg` — regions resolved | 75.78 | 69.35 |
| **regions an upload** | **1.003** | **1.004** |
| `bi_b` — bytes taken | 23 201 860 | 22 371 899 |
| **`bi_b / (sync_up_kb × 1000)`** | **1.0000** | **1.0000** |
| **mean region** | **306 174 B = 299 KiB** | **322 594 B = 315 KiB** |
| `bi_noback`, `bi_nochunk`, `bi_split` | **0.00, 0.00, 0.00** | **0.00, 0.00, 0.00** |
| **`bi_bad`** (gate `bufimpcheck` = 1) | **0.00** | **0.00** |
| `bi_us` — the resolution's own wall time | 11.02 µs | 9.68 µs |
| `bi_cp` — uploads whose copies came from imported pages | **0.0003** | **69.10 = `bi_ok`** |

* **100 % of buffer upload bytes are importable in this scene**, with not one region refused by
  `TryGetBackingPointer` or by `HostImport::Resolve`, and not one crossing a 512 MB chunk
  boundary. P2 — the sealed "decisive unknown of the session" — passes at its ceiling.
* **The self-check passes.** `bufimpcheck` recomputed every resolved offset with
  `TryGetBackingPieces`, a second independent walk of the same mapping table, over the whole run:
  `bi_bad` = 0, and `guards.py` reports the counter **REACHABLE** and zero rather than
  unreachable-because-the-gate-was-off.
* **The resolution costs ~10 µs a frame** and replaces, at most, the whole staging memcpy.
* **`bi_cp` = `bi_ok` to 0.004 %** in the import arm: the import was taken for every upload that
  resolved.
* `bi_b` = `sync_up_kb` × 1000 **to four decimals**, which is the unit correction of §5 item 1
  measured rather than argued.

### 2.1 AND THE RESULT THAT NEEDS NO CONTRAST: the memcpy was already parallel

`CopyGuestToStaging` (`bufferCache.cpp:217-228`):

    if (size >= Common::ASYNC_COPY_MIN_BYTES &&
        Libs::LibKernel::Memory::TryGetBackingPointer(vaddr, size, &backing)) {
            Common::AsyncMemcpy(staging, backing, static_cast<size_t>(size));
            return;
    }

`ASYNC_COPY_MIN_BYTES` is **64 KiB** (`parallelCopy.h:44`) and `AsyncMemcpy` "queues the copy to
the pool and returns at once" (`parallelCopy.h:15`). **The import's admission test is the SAME
`TryGetBackingPointer`**, and the census says it succeeds for 100.00 % of regions. The mean region
is **306 KB, 4.8× the threshold**, over **1.003 regions an upload** — i.e. a dirty run per upload,
not a scatter of pages.

**Therefore the buffer staging memcpy is, to the extent the mean says, already on the copy pool
and off the GuestGpu thread — and `acopy_wait_us` reads 0.51 / 0.01 µs a frame, so nothing waits
for it.** This is a source-plus-census argument and it uses **no contrast between the arms**.

**And the pool was live.** `CopyPool` starts `clamp(hardware_concurrency/2, 2, 7)` workers
unless `KYTY_PARALLEL_COPY=0` (`parallelCopy.cpp:112-122`), and `AsyncMemcpy` takes the queue
unless `KYTY_ASYNC_COPY=0` (`:260-266`). **`bim90a.json` records neither variable**, so the
queue was open for every region that passed the two tests above.

**What is NOT established: the exact share of bytes in regions below 64 KiB.** The mean cannot
rule out a bimodal split, and this session did not add the one counter that would settle it —
`bi_b` split at `ASYNC_COPY_MIN_BYTES`. **That is one line and it is named in §8 as the next
number.** Everything above is a statement about the mean, and it is labelled as one.

---

## 3. §3.1 — the A/B, and why it is INVALID

`area_verdict.py bim90a`:

    [FAIL] area split < 1.0 %       -21.877 %
    [FAIL] pair match >= 90 %       42.9 % (51/119)
    [PASS] work within 0.5 %        -0.156 %
    VERDICT: INVALID - this run may not be quoted. Take another run.

**The rule is that a run failing admission is REPLACED and its contrast quoted nowhere. It is
quoted nowhere.** What follows is a DIAGNOSIS of the failure, read from counters that describe
each arm rather than compare them, and it is labelled as such.

**The import arm holds the low DRS rung and the census arm does not:**

| | census arm | import arm |
|---|---:|---:|
| frames on the high rung (`rt_kpx/rt_att` > 2600) | **53.0 %** (1 889 / 3 567) | **5.3 %** (188 / 3 571) |
| `rt_kpx / rt_att`, whole arm | 2 645.9 | 2 067.1 |

**and the vblank plateau is where the damage lands** (`dt_us` rounded to 16 666.7 µs):

| | 1 vblank | 2 vblanks | 3 vblanks |
|---|---:|---:|---:|
| census arm | **14.1 %** | 85.6 % | — |
| import arm | **1.0 %** | 87.2 % | **11.8 %** |

`ROADMAP.md` §4 says this in advance — which is why `pred/01` put the primary endpoint on
`cpu_net_us` and not on `dt_us`. **The estimator is right to refuse: at a 21.9 % area difference
the two arms are not doing the same work, and `bi_try` (−8.5 %) and `sync_ups` (−8.5 %) — sealed
null controls A4 and E7 — say so independently.**

**Where the time goes is NOT attributed by this run, and the honest form of that is a table of
what moved:** `dt_us` **+4 110.8 µs**, `cpu_gpu_us` **−386.7**, `cpu_main_us` **+128.9**,
`cpu_present_us` **−12.2**, `cpu_proc_us` **−1 026.1**, `gpu_busy_us` **−1 124.2**,
`submit_us` **+207.0**. **The frame got 4.1 ms longer while every counted thread and the GPU did
LESS.** Two candidates are named and neither is measured:

1. **The forced submit.** `WaitPendingHostReads` calls `m_scheduler.Wait(tick)`, which "submits
   the recording command buffer when tick is current" (`bufferCache.cpp:1611`), and off the
   GuestGpu thread it does so through `SendCommandSync` (`:1617`). `hostread_waits` reads
   **19.468 a frame** in the import arm against **0.009** in the census arm — the hazard fires —
   while `hostread_wait_us` reads **0** in both, so the waits themselves are under ~50 ns each.
   **A wait that costs nothing can still cut the frame into more submissions**, and `submit_us`
   moved +207 µs.
2. **The GPU reading host-cached, pagefile-backed guest pages** instead of the staging ring
   (`MemoryUsage::Upload`). Both are host memory, so this is not the device-locality objection —
   it is a cache-attribute and residency objection, and nothing here measures it.

**Neither candidate is established, and the run cannot choose between them.** §8 names the
measurement for each.

---

## 4. §3.2 — `pg_pm_us`'s search half, divided, and the instrument priced [M]

`pgl90a`, ABBA `proglap=0 | proglap=1`, **VALID**: area split **+0.001 %**, pair match
**125/125 = 100.0 %**, work **+0.057 %**. `guards.py`: 9 PASS, 1 FAIL (check 6, cores — not an
admission criterion), 0 WARN, 2 SKIP. `bufimp` = 0 in both arms, and every `bi_*` counter reads
exactly 0 over the whole run.

**The armed arm, 3 751 frames, 8 878.18 `ProgramCache::Get` calls and 9 401.59 candidates a
frame** (`pg_perm / pg_get_n` = **1.0590**, unchanged since session 86):

| phase | µs a frame | ns a CANDIDATE | share of the search |
|---|---:|---:|---:|
| `pg_pmp_us` — the loop iteration, the `ProgLapPerms` Add and `push_data_start_dword == PushData::StartFor(cursor, ShaderDataDwords())` | **91.85** | **9.77** | **0.2352** |
| **`pg_pms_us` — `candidate.specialization == specialization`** | **298.72** | **31.77** | **0.7648** |
| `pg_pmf_us` — what is left: the `find_if` return, the `permutation != end()` test and a `lap.Mark` | 85.00 | 9.04 | — |
| **sum of the three** | **475.58** | | |

**VERDICT by the rule sealed in `pred/01` §8 BEFORE any number: `f` = 298.72 / (91.85 + 298.72) =
0.7648 ≥ 0.60 ⇒ THE `specialization ==` COMPARE.** `bim90a` read the same quantity at **0.7638**
and **0.7609** in its two arms across a 21.9 % area difference, so the split is invariant to the
DRS rung. **`docs/next-session-90.md` §3.3 named two candidates and it is the second one.**

**What that compare IS.** `ResourceSpecialization` (`ResourceMaterialization.h:16-45`) is two
`std::vector`s — `buffers` of a 3-field struct and `images` of an 11-field struct — with
`operator==` defaulted, i.e. size check then element-wise comparison of plain scalars. **31.77 ns
a candidate is that walk.** The per-element price is NOT measured and no counter gives the vector
lengths; that is named in §8.

**And what it MEANS was fixed before the number, in `pred/01` §8: it is a PROOF, not work.** The
compare is what establishes that a cached permutation still matches the specialization this draw
computed. A cached digest cannot replace it: at **1.0590 candidates a call** almost every compare
SUCCEEDS, and a digest only saves work on a MISMATCH — replacing a successful compare with a hash
equality would be trusting a hash, which is the `dawitness=0` category, not an optimisation.
**This closes a debt opened in session 87. It finds no saving, and this session does not claim
one.**

### 4.1 THE PRICE OF THE INSTRUMENT — the debt sessions 86 and 89 could not pay [M]

Session 86 made this unmeasurable by riding its instrument in both arms (its own I1 defect);
session 89 inherited the same defect for the `pg_pmf` mark and said so. `pgl90a` pays it.

| | reading |
|---|---|
| paired `cpu_net_us`, 130 pairs | **+1.5760 % ± 0.1096 % (2·SE 0.2192), t = +14.38** |
| paired `cpu/draw`, 130 pairs | +1.5864 % ± 0.1110 %, t = +28.58 |
| whole-arm `cpu_net_us` | 30 719.0 → 31 223.4 µs = **+504.4 µs a frame** |
| paired `gpu_busy_us` | +0.0793 %, t = +1.00 — **inside its own 2·SE**, as it must be |
| paired `dt_us` | +1.5825 %, t = +13.91 — it moves with the CPU, and the arms sat on the SAME rung (high-rung share **0.0 %** in both) |

**The chain takes 8 timestamps a call plus 2 a candidate = 89 829 a frame**, so
**+504.4 µs / 89 829 = 5.61 ns a mark** — where a "mark" is one `NowNs()` **plus** one
`FrameStats::Add`, because both are inside the gate and the numerator owns both. **It is a price
for that pair, not for an `rdtsc`.**

**A THIRD value on the same machine: 7.5 ns (`pgl87a`, six marks), 3.45 ns (`tkl89a`, the
`takelap` chain), 5.61 ns here.** The standing rule holds and is now confirmed three times: **a
mark's price does not carry between chains.** The cross-binary consistency read —
475.58 − session 89's 336.9 = 138.7 µs over 2 × 9 401.59 new marks = **7.38 ns** — is [I], a
different binary, and it is quoted as a consistency note and never as a measurement.

---

## 5. Corrections to this programme's own record

1. **`sync_up_kb` is kB (1000 bytes), not KiB, and the source says so.**
   `videoOut.cpp:1550`: *"A byte counter through the micros column: kB (1000 bytes)."* So
   `blp85a`'s 22 803.8 is **22.80 MB = 21.75 MiB**, and the "**22,8 МиБ/кадр**" carried by
   `ROADMAP.md` §2 D, `FACTS` s85 and every brief since is an overstatement of **4.6 %**. Measured
   this session: `bi_b` (raw bytes) = `sync_up_kb` × 1000 to four decimals.
2. **`bda_up_us` = 2 118.3 µs is not the memcpy.** It times `SynchronizeBuffersOfDirtyRanges`
   whole — the buffer walk, the page-protection arming, `ForEachUploadRange`, the staging
   `Map`/`Commit`, the copy and the barrier/`vkCmdCopyBuffer` recording. Session 85's "92,7 % —
   staging-`memcpy` на 11 ГБ/с" is arithmetic from bytes and an assumed bandwidth that returns
   100 % of the timer by construction. **§2.1 gives the reason it cannot be the memcpy.**
3. **"Images already avoid the staging copy and buffers do not" is true of the code path and false
   of the bytes.** In this scene `img_imp_kb / img_up_kb` = 2 072.6 / 101 383 = **2.0 %**; most
   image uploads take the *owner* branch (`bufferCache.cpp:1217-1225`).
4. **Session 28 never rejected buffers.** It measured the buffer memcpy in the same profile —
   "memcpy буферов (`TryTransferBacking`) 10,6" ms of a 97 ms cut frame, HANDOFF §2.34 — and
   walked past it with no recorded reason. **Silence, not refusal.** The nearest thing to a ground
   is an inference: the one image class it EXCLUDED from import is data the CPU rewrites often
   (`KYTY_HOST_IMPORT_REUPLOAD_TICKS`), and buffers are by the record's own description exactly
   that.
5. **`gen_gates.py --out <file>` is honoured only with `--with`; without it the flag is ignored
   and `gates_base.txt` is rewritten.** It was, and it was restored from `C:/kyty/s89` and
   re-verified (1092 B, 99 names, sha256 `00c116dc…0594d8`). No run used the damaged file.
6. **The brief's file pointer for `HostImport` is stale**: it is
   `graphics/host_gpu/renderer/cache/hostImport.{h,cpp}`, not `hostMemory.{h,cpp}`.
7. **`daepceil`'s comment still says "(default 1)" and it is 0** — carried from session 89, still
   not fixed.
8. **There are three CPU-side copy populations, not one.** Per frame: the buffer upload path
   23.10 MB in 73.1 calls; the `ObtainBuffer` stream ring **19.23 MB in 13 325 memcpys of
   1 443 B**; const-bank copies 0.78 MB in 7 845 copies of ~100 B. `bufimp` touches only the
   first, and the second has never been examined.

---

## 6. WHAT WAS NOT DONE

* **No default moved.** `bufimp` ships at 0, `bufimpcheck` at 0, `proglap` at 0.
* **The shipping contrast `bufimp=0|2` was not measured** — `pred/01` §1 opened it as a debt
  before the run, and after `bim90a` it is blocked by the same obstacle.
* **The failed A/B was NOT re-run at a shorter period.** The area split is −21.9 %, not a
  marginal 1–2 %; a shorter block does not repair an effect that moves the DRS step. `pred/02` §0
  says so before the replacement run rather than after it.
* **No `--rec`**, so `guards.py` checks 8 and 9 SKIP. `bufimp` ships at 0, so the shipped render
  path is byte-for-byte unchanged and no video debt is incurred; `pred/01` §10 makes the video
  pass mandatory before any default moves.
* **The 64 KiB split of `bi_b` was not added** — the one counter that would turn §2.1's statement
  about the mean into a statement about the distribution.
* **`dapin`'s GPU cost, TENTH session: NOT TAKEN**, and not struck. It is now joined by a second
  knob with the same failure mode.

---

## 7. THE SCOREBOARD — 27 pre-registered entries in two files

### `pred/01_bufimp.md` — 19 entries on `bim90a`

The run is INVALID, so the EFFECT bands are scored against what the run could deliver and the
verdict rule of §7 **did not fire**. The census and the self-check bands are scored normally:
they describe each arm and do not compare them.

| # | prediction | reading | verdict |
|---|---|---|---|
| A1 | every new counter exactly 0 in the pre-schedule window | 0 by sum and max over 1 798 frames | **HIT** |
| **A2** | `bi_cp` exactly 0 in the census arm | **0.0003 a frame** | **MISS — A DEFECT OF MY OWN PREDICTION.** An arm-labelled window cannot carry an exact zero for a counter that is `Add`ed in the other arm. §0.1 item 1 |
| A3 | \|`bi_cp` − `bi_ok`\| / `bi_ok` ≤ 0.1 % | 0.0041 % | **HIT** |
| **A4** | `bi_try` between arms within 1.5 % | **−8.51 %** | **MISS — and the control did its job**: the arms did different work because their DRS rungs differed |
| P1 | `bi_try` ∈ [40, 120] a frame | 75.53 / 69.10 | **HIT** |
| **P2** | **`bi_ok / bi_try` ≥ 0.50 — "the decisive unknown"** | **1.0000 in both arms** | **HIT at the ceiling** |
| P3 | `bi_b` ≥ 0.50 of the upload bytes | 0.9766 on the sealed (wrong-unit) denominator, **1.0000** on the correct one | **HIT** |
| P4 | `bi_nochunk` exactly 0 | 0 | **HIT** |
| P5 | `bi_split / bi_reg` ≤ 0.02 | 0.0000 | **HIT** |
| P6 | `bi_us` ≤ 400 µs a frame | 11.02 / 9.68 | **HIT** |
| **P6b** | `bi_us` between arms within 10 % | **−12.10 %** | **MISS — a consequence of A4**, not of the instrument; the per-upload price agrees to 3.9 %. Repaired in `pred/02` §0.1 as a normalised form |
| **P7** | **`bi_bad` exactly 0** | **0**, and `guards.py` calls it REACHABLE | **HIT — the self-check passed** |
| E1 | paired `cpu_net_us` negative with \|t\| ≥ 3 | admission failed first | **NOT EVALUABLE** |
| **E2** | the effect ∈ [−2 500, −100] µs | admission failed first | **NOT EVALUABLE — and §0.1 item 4 says the band should never have been written as if the run would reach it** |
| E3 | `hostread_wait_us` ≤ 500 µs in the import arm | **0.00**, on **19.468 waits a frame** | **HIT** |
| E4 | `gpu_busy_us` inside its own 2·SE | −8.07 % — the area difference, not the mechanism | **NOT EVALUABLE** |
| E5 | `sync_up_kb` between arms within 5 % | −3.58 % | **HIT** |
| E6 | `draws` between arms within 1.5 % | −0.16 % | **HIT** |
| **E7** | `sync_ups` between arms within 2 % | **−8.52 %** | **MISS — the same control as A4, doing the same job** |

### `pred/02_pmlap.md` — 12 entries on `pgl90a`

| # | prediction | reading | verdict |
|---|---|---|---|
| G1 | every new counter exactly 0 in the pre-schedule window | 0 by sum and max, 1 798 frames | **HIT** |
| G2 | `pg_pmp_us + pg_pms_us` in the unarmed arm ≤ 0.10 % of the armed | **0.0051 %** | **HIT — the repaired form of A2, and it works** |
| G3 | every `bi_*` exactly 0 in both arms | 0 | **HIT** |
| **G4** | `pg_perm` between arms within 1.5 % | 0.53 against 9 401.59 | **NOT EVALUABLE — A SECOND DEFECT OF MY OWN PREDICTION, in the repair file itself.** `ProgLapPerms` is `Add`ed only when `prog_lap` is true, and always has been, so it cannot be compared across a `proglap=0\|1` contrast. N1 (`draws`, +0.057 %) carries what G4 was for |
| I1 | paired `cpu_net_us` positive, \|t\| ≥ 3 | **+1.5760 %, t = +14.38** | **HIT** |
| I2 | the whole-arm difference ∈ [200, 900] µs | **+504.4 µs** | **HIT** |
| I3 | the per-mark price reported and NOT carried | **5.61 ns a mark**, against 7.5 (s87) and 3.45 (s89) | **HIT** |
| S1' | the three phases sum to [300, 550] µs | **475.58** | **HIT** |
| S3' | the rule of `pred/01` §8 applied | **f = 0.7648 ⇒ the `specialization ==` compare** | **HIT (a REPLICATION, not a blind test — `bim90a` had already read it, and `pred/02` §2 says so)** |
| S4' | `pg_pmp_no / pg_perm` ≤ 0.10 | **0.0366** | **HIT** |
| S5 | the sum exceeds session 89's 336.9 µs by [60, 250] µs | **+138.7** | **HIT** |
| N1–N4 | `draws` ±1.5 %, `sync_ups` ±2 %, `sync_up_kb` ±5 %, `gpu_busy_us` inside 2·SE | +0.057 %, −0.277 %, +0.071 %, +0.0793 % (2·SE 0.158) | **HIT** |

**27 pre-registered entries, 20 hits, 4 misses, 3 not evaluable. THREE of the seven non-hits are
defects of predictions I wrote myself** (A2, P6b's form, G4), **and one of those three is in the
file written expressly to repair the first.** A4 and E7 are controls doing their job; E1, E2 and
E4 could not be reached because the run failed admission. That is the fourth consecutive session
in which my own prediction defects outnumber the world proving me wrong.

---

## 8. WHAT IS NOT CLOSED, with the next measurement named for each

| debt | next number | since |
|---|---|---|
| **The share of upload BYTES in regions below `ASYNC_COPY_MIN_BYTES`** | split `bi_b` at 64 KiB — ONE line, rides free in the census arm, and it turns §2.1's mean into a distribution | **90** |
| **Where `bim90a`'s 4.1 ms a frame went** | it is not on any counted thread. Either a `SiteScope` on `host-read` submissions, or an ABBA of a knob value that imports WITHOUT `NotePendingHostRead` (a ceiling, unsafe, measurement only) | **90** |
| **An estimator that survives a DRS shift** | **the `dapin` debt, now TENTH session, and now shared by `bufimp`.** Two knobs whose effect is too large for the paired area estimator | 79 → **90** |
| **The shipping contrast `bufimp=0\|2`, and the video pass** | blocked behind the estimator debt | **90** |
| **The `ObtainBuffer` stream ring: 19.23 MB a frame in 13 325 memcpys of 1 443 B** | never examined; `ob_stream_us` needs `KYTY_FRAME_TRACE=1`, not `lite` | **90** |
| **The per-element price of `ResourceSpecialization::operator==`** — 31.77 ns a candidate is measured, the vector lengths are not | a counter on `specialization.images.size()` and `.buffers.size()`, or a microbench outside the game | **90** |
| ~~`pg_pm_us`: `PushData::StartFor` or the `specialization ==` compare~~ | **CLOSED in session 90: the compare, 0.7648 of the search, 31.77 ns a candidate (`pgl90a`, VALID)** | 89 → 90 |
| What fraction of the 21.42 prefetched lines a take ever reads | a counter on first touch, or an A/B with a truncated vector set | 89 |
| The 459.4 µs take, unsplit | one mark between the two `std::swap`s and the retire | 89 |
| The witness share of the 19.66 ns of `RebindImages` | it can only lower 514 µs | 87 |
| Route B items 2, 8, 10, 12 and the corrected item 3 | `FACTS` s85 §8 | 83 |

---

## 9. THE ARITHMETIC

| article | measured | state |
|---|---|---|
| the sequential floor `S` | 20 838 µs, `flr83b` | MEASURED — closes route A [I] |
| **D1's bytes** | **22.80 MB a frame, not 22.8 MiB** | **CORRECTED (s90) — a five-session unit error** [M] |
| **D1's reachable share** | **100.00 % of uploads and of bytes** | **MEASURED (s90), within-arm** [M] |
| **D1's memcpy, on the GuestGpu thread** | **already pooled at the mean: 306 KB a region against a 64 KiB threshold, and `TryGetBackingPointer` succeeds for 100 % of regions** | **DERIVED (s90) from source + census, no contrast** [M·I] |
| **`bda_up_us` = 2 118.3 µs** | **NOT the memcpy** | **CORRECTED (s90)** [I] |
| **D1's A/B** | **INVALID: area split −21.9 %, pair match 42.9 %** | **NOT MEASURED — the effect moves the DRS step** |
| **`pg_pm_us`: the search half, DIVIDED** | **`specialization ==` 298.72 µs (76.5 %), the push-data half 91.85 µs (23.5 %), residue 85.00** | **MEASURED (s90, `pgl90a` VALID) — a proof, not work** [M] |
| **the `proglap` chain's own price** | **+504.4 µs a frame = 5.61 ns a mark** | **MEASURED (s90) — a debt open since session 86** [M] |
| D2: the two prefetch passes | 944.2 µs | MEASURED (s89) [I] |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured since session 82 [I] |

**The honest statement of the task.** 60 FPS is 16 667 µs; the shipped frame is 31 642 µs, so
~15 ms has to go. **Session 90 took the one measured ceiling nobody had started, built it, and
found that its headline number was the wrong kind of number twice over: the bytes were overstated
by 4.6 % by a unit, and the 2 118 µs timer it was attributed to does not contain the work it was
attributed to, because that work has been on the copy pool since session 27.** The import itself
reaches every byte it aims at and costs 10 µs a frame to resolve — and its first A/B could not be
read, because the change is large enough to move the game's own resolution step. **Nothing
shipped. Expect hundreds of microseconds from what is left, not milliseconds, and do not promise
60 FPS on the strength of any of it.**
