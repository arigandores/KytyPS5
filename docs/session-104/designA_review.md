# Route A (parallel command-stream processing) — re-review under "maximum FPS", session 104

Tags: **[M]** measured (run named), **[I]** inferred from source/arithmetic, **[U]** unknown.

## 1. What A proposed, and why K2 closed it

`DESIGN_82_parallel.md`: GuestGpu becomes a **spine** (PM4 decode, a 6,803-byte `CpSnapshot` per fork point, guest-visible writes in stream order, tick issue); W **RecordCtx** threads each own a `CommandScheduler`/`MasterSemaphore`/pool/recorder, `DescriptorHeap`, four `StreamBuffer`s, `RenderExecutor`+memo and a private `ProgramCache` slice; locks L0–L8. Eight steps, ~15 weeks by its own estimate, **no speed until step 6**. Model `T = S + max(f_max,1/W)·(cpu_total − S)`, `f_max` 0.23–0.39 at DCB granularity (four DCBs carry ≥79 %).

K2 ("S ≥ 16 ms ⇒ close") fired in s83: `flr83b` **S_hi = 20,838 µs** [M] (six sites 13,437 + `mh_rt`/`mh_prog`/`mh_disp`/`PrepareBda` via `mutwide=15`, instrument 135 µs subtracted); `plk83a` 20,998 [M]. `PipelineCache::m_mutex` holds 4,998 µs (68.9 % of `mh_prog`) [M]; freeing all of it still left 15,840 > 14,100.

K2 was a 60-FPS argument. Under max FPS the model gives 20.8 ms (1.5×) **only at pass granularity** (K3 never evaluated); at DCB granularity (`f` = 0.30) it is **24.3 ms for any W ≥ 4 (1.30×)** [I].

## 2. What changed since s83

- **Recording is already off GuestGpu.** `recordthread`/`recpack`: the record thread runs `vkCmd*`, `updateDescriptorSets` and binds from a single-producer ring (`commandRecorder.cpp:574-737`) and spins ~27 of ~30 ms [M s95 ETW]. What stays serial is **resolution**, not recording.
- **M1** puts SRT materialisation on 4 workers (`da_hit` ~97 % [M s87]). GuestGpu keeps `AheadTake` ≈ 2.35 ms/flip [M s100] under `PipelineCache::m_mutex` (`pipelineCache.cpp:3250`, lock `:4541`). It cannot leave GuestGpu: the witness reads through `IsGpuCleanRange` (`kernel/memory.cpp:1031`), which returns false off-thread.
- **Spine precursor exists:** `DrawAheadWalker` (gate `dawalk`, default 0, `graphicsRun.cpp:1443-1589`) walks PM4 off-thread, carrying SH/gfx shadow state.
- **Migration is cheap:** `m4baton` ran the real draw path on another thread at `f_full` = 1.02, splice 15.8 µs per 512 draws [M s68].
- **Concurrency is not cheap:** `shadowresolve` (s64) — one concurrent reader of the texture/buffer caches taxed GuestGpu +4.1…+6.3 %, four readers +4.2…+8.2 %; the worker spent 2.6× the critical thread's time on the same reads [M]. DESIGN_82's model leaves it out; `PLAN_82_bind` §4.3 cites it. **It is the strongest prior against A.**
- **`dawalk`** (s59/60): moving the walk off-thread cooled M1 results by as much as it saved (`da_take` +0.5–1.0 ms, `da_miss` ×2). With `dawalklead=1/2`: −0.3…−1.4 % CPU/draw at ±1.4 % resolution. **Never re-measured under ABBA + pin.**
- Outside the mutex 4,621 µs/flip: `PrefetchComputePipelines` (the walk) 1,961, `ProcessCommands` 564, unattributed 1,922 [M s96]. The walk is 1,837, of which 769 is `QueueDrawAhead` under `PipelineCache::m_mutex` [M s100]. **A bare spine therefore costs ≈1.1 ms [I], right at K1's 1.2 ms.**
- `mh_emit` split [M s96]: `CommitBindings` 2,245 (write-list 675, emit 440 [M s101]), `AcquireRenderTargets` 1,547, VB/IB 1,337, record 1,216, `GetGraphicsPipeline` 749.
- s104: mean `dt_us` follows GuestGpu CPU ~1:1 [M/I].

**Floor today:** nothing has re-measured S since s83. The only shipped change since is `bindpack` (−252 µs, partly inside the `FindImage` scope), so S_now ≈ 20.5–20.8 ms [I]. `pl96a` hold 26,416 vs 28,686 in s83 is a cross-run comparison with a different pin, so it is **not** a measurement.

**The floor A's own architecture would face (`S_ctx`) is not S.** S counts all of `mh_emit` as serial (`renderDraw.cpp:2302`), yet per-context write-list, emit and record (≈2.3 ms) would leave it; spine (≈1.1 ms) and concurrency tax enter. S_ctx ≈ 18.4 ms [I]. At W=4 with spine plus s64-size tax: **T ≈ 25–26.5 ms, 1.2–1.26× best case [I]**. A tax at the top of the s64 range erases it.

### Per draw under the render mutex (`renderDraw.cpp:2989`/`:3160`; dispatch `renderCompute.cpp:284`)

| phase | pure function of draw inputs | mutates shared state |
|---|---|---|
| prologue | early-outs, topology, 8-bit index expansion | `MaterializeBoundTargetDccClears` |
| `mh_rt` 0.87 | — | `FindRenderTarget`/`FindDepthTarget` (texture cache) |
| `mh_prog` 5.85 | `PrepareProgram`, `progmemo` compare (1.54 pre-lock); SRT materialisation (on M1) | program memo, `kept_snapshots`, ahead slots under `m_mutex`; `AheadTake` witness (GuestGpu-only) |
| `mh_bind` 11.4 | T#/V#/S# decode, `ImageDesc`, memo hash/memcmp (`descriptors.cpp:1372-1474`), shader_data, `FindBuffer` lookups | memo hit: `ConfigureImageSource`, `tick_accessed_last=CurrentTick()`, `TouchImage`, `AdoptPendingDcc`, `LodStats::Touch` (`:1442-1511`); `BindImage` `is_bound` (`:2258`); `FindTexture`/`FindImage`; `PrepareBda`; `ObtainBuffer`/`SynchronizeBuffer` (dirty bits, page protection, uploads); `NativeUpload` stream ring (`:1768`) |
| `mh_emit` 7.6 | write-list build, pipeline key hash | `Image::Transit` (can close the pass, `:3749-3801`), `AcquireRenderTargets`, VB/IB uploads, `DescriptorHeap::Commit` (tick-stamped, `:3970`), recorder ring (`:3974`), pipeline create (`:4655`) |

## 3. Staged plan (maximum FPS)

Record in ROADMAP before any code: **A overlaps route P**, which the 10.88-CPU M1 rule closed for **60 FPS**. §2 E requires the rule decision for max FPS to be written first.

**Stage 1 — kill-or-go (one session, zero code, two ABBA runs, pin=1, 300 s).**
(1a) `mutwide=0|15`, with `mutsite=1 amut=1 plkstat=1 pathlap=1` in both arms. This gives S_now (subtract `pathlap`'s own price, ≈0.36 ms [M s96], which sits inside the scopes), then S_ctx = S_now − `pl_em_rec_ns` − (write 675 + emit 440 from s101; cross-run, flagged).
(1b) `shadowresolve=0|4` (gates exist; measurement-only, unprotected probes, ran clean in s64) gives the W=4 tax T4 in µs of `cpu_net`.
**Acceptance:** the six standard criteria, `mw_n` identity ±2 %.
**Sealed rule:** G = cpu_net − [S_ctx + 0.30·(cpu_net − S_ctx)] − spine(`da_walk_us` − `da_queue_us`) − T4. **G < 3 ms ⇒ A closed for max FPS too** (≥10 sessions of enabler work cannot carry a <10 % ceiling given 2–20× over-optimism); only Stage 2 survives. Saving 0.

**Stage 2 — spine half one: `dawalk=0|1`, `dawalklead=1` (one session, zero code).** Expected −0…−1.2 ms [I]; ceiling 1.96 ms minus the cooling cost.
**Risk:** low. M1 results stay witness-checked, compute prefetch only compiles, and `MaxLag`/`da_wdrop` guard stale command memory. One more thread lands on the preferred CCD.
**Acceptance:** arming `da_wskip` ≈ walks/flip and `pl_pref_ns` → ~0 in arm 1 (needs `pathlap=1 mutsite=1`); `cpu_net` ≤ −150 µs with 2·SE excluding 0; mean `dt_us` same sign; `da_take_us`/`da_miss`/`da_late` reported; video 0 glitches on ≥3000 frames. Ship on pass.

**Stage 3 — enabler at N=1 (3–5 sessions): DESIGN steps 3–4.** `RecordCtx`, explicit tick/context through the 43 `CurrentTick()` uses, `EXIT` on blocking calls from recorder threads. Saving 0.
**Acceptance:** A/A |Δcpu_net| inside ±90 µs; video clean; entry-hang rate ≤6.67 % over ≥60 entries.

**Stage 4 — shadow spine fused with the walker (2 sessions).**
**Acceptance:** `spine_mismatch`=0, `cram_write`=0, `spine_us` ≤1.2 ms (K1), per-pass histogram (K3), adjacent-DCB image overlap ≤30 % (K4).

**Stage 5 — W=2 on DCB boundaries, `sliceN` latched per frame (≈3 sessions).** Expected −1…−3 ms [I].
**Acceptance:** ABBA `cpu_net` and mean `dt_us`; K6 (spin ≤1 ms); `plkstat` wait (92 µs today) reported; video; hang rate.

**Stage 6 — W=4, L3 split after hoist, pass granularity.** A further 0…−2 ms [I].

Route total, best case: −3…−6 ms (10–20 %) [I]; the probability-weighted value is well below that.

## 4. The three largest risks, and early detection

1. **Concurrency tax** (shared cache lines, `TextureCache::m_lock`, 8-core CCD already hosting ~10 threads). s64 shows the tax can equal the moved work. Detect in Stage 1b; at W=2 read per-context spin, `plkstat` wait and `rec_ccd_x`.
2. **Structural serialisers beyond lock granularity.** The `IsGpuCleanRange`-bound witness (2.35 ms), `PipelineCache::m_mutex` (5.0 ms hold), layout authority in `Transit`, the implicit tick. A wrong tick is silent buffer reuse or the s81 hang signature. Detect with S_ctx (1a), `plkstat` wait growth, and tick-owner bits plus the Stage 3 asserts.
3. **Pinned gain ≠ real game speed; hangs.** When CPU sped up, DRS quadrupled area within 30 frames and overflowed the 32 MiB download ring (`textureCache.cpp:2842`, s96). New submit patterns can raise the 6.67 % entry-hang rate. Detect by measuring pinned, then confirming with one unpinned run (`rt_kpx/rt_att`, mean `dt_us`); count hangs over ≥60 entries.
