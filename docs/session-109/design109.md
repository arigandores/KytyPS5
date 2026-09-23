# Session 109 design (Plan agent, read-only source study): the walker's two holds of `PipelineCache::m_mutex`

Paths relative to `C:/kyty/KytyPS5/src/`; `pc.cpp` = `graphics/host_gpu/renderer/pipeline/pipelineCache.cpp` (HEAD
`600ca26`). Tags: [I] inferred from source.

## A. Tag 1 — `QueueDrawAhead` (pc.cpp ~4742 → `QueueAhead` ~2628 / `QueueAheadSource` ~2533)

State and owners (all serialised by `m_mutex` today): `AheadSlot` (only `state` atomic; key fields, `walk`, `uses`,
`taken`, `pixel` plain) — walker writes key/walk/uses, GuestGpu `AheadTake` reads the key and writes uses/taken/state,
workers move Queued→Running→Ready/Failed; `ahead_hints`/`ahead_variants` written only by `AheadNote` (called from
`Get` ~3391 under `m_mutex`), read by the walker; `ahead_walk`/`ahead_fresh` walker only; `memo_generation` bumped
only on the drop path (~3501); `SourceEntry::plan_fingerprint` and `plan_class` written lazily from both the walker
and `AheadTake`; `srt_compiled` written null→non-null once inside `MaterializeResources`. `ahead_mutex` protects only
the ring, `ahead_stop` and the cv predicate (one pre-existing race: `ahead_threads.size()` read under it at ~2868,
`emplace_back` at ~2510 outside it). Lifetime: source entries never freed (drop = `programs.extract` into
`retired_sources`), unordered-map nodes stable, `PlanClass` never freed, permutation deques append-only.

Rejected: a coarse `ahead_table_mutex` (GuestGpu would take it on ~8.7 k take-side probes a frame; ~125 contended
acquisitions × ~1.3 µs + 8.7 k uncontended pairs ⇒ net ≈ 0).
Proposed `daslot`: publish-once hints (store a source into a hint only when `srt_compiled != nullptr`, fingerprint
and class computed before the store); atomic hint/variant fields and `memo_generation`; `ahead_slots` behind an
atomic pointer under a new `ahead_queue_mutex` serialising `QueueAhead` callers; a per-slot guard byte and a state
`AheadTaking` (take: guard with bounded spin, else miss; `slot.taken = 1` must move before the state store);
`QueueDrawAhead` takes `ahead_queue_mutex` instead of `m_mutex`. Lock order: GuestGpu `m_mutex` → ≤ 1 guard (never
blocks); walker `ahead_queue_mutex` → ≤ 2 guards ascending → release → `ahead_mutex`. Estimate [I]: GuestGpu ≈ 45
µs/frame of guard atomics, contention ≈ 0, net −150…−200 µs against today's tag-1 share (~243 µs); the 1 080
`CRITICAL_SECTION` line transfers a frame disappear. ~300–400 lines, medium risk.

## B. Tag 2 — `PrefetchComputePipeline` (pc.cpp ~5111)

Under the lock via `Get(..., tolerant, slot 2)`: `lookup_keys[2]` scratch (shared with GuestGpu's
`GetComputeProgram`), `programs.find`, on a miss `LoadFromTranslationCache` (disk, insert, epoch), memo
find/verify/store (gate `srtmemo`, default 0), the permutation `find_if` (predicate: push-data start for cursor 0
and `specialization ==`), the drop path, `Compile`; then `m_compute_pipelines.contains` and, if missing, recipe +
emplace + enqueue. Pure computation + guest reads: `BuildStageStaticKey`, `MaterializeResources` (its only write is
the one-time `srt_compiled`; `CompiledSrt` native code guarded by `std::once_flag`). The walker already materialises
today (same thread, same readers; off the GuestGpu thread `IsGpuCleanRange` fails for GPU ranges → the same
flattened values as today).

Rejected: the three-phase split (two acquisitions a call, ~532 a frame; `dab107` showed more acquisitions hurt).
Proposed `cspfree`: a per-thread memo keyed on `ProgramKey` → source entry (recorded under the lock only when
`srt_compiled != nullptr`) and, per source, "specialization → id with a pipeline"; before the lock:
`MaterializeResources` unlocked, search; hit ⇒ return without the lock (0 acquisitions in the steady scene, where
`cspf_have` = 266/266); miss ⇒ today's locked path + record. Sound because (source, specialization) is exactly the
permutation predicate (cursor 0), permutations append-only (first match stable), `m_compute_pipelines` never erased;
the `cspmemo` failure (user SGPRs → two permutations) is keyed away. Verify mode: on a hit run the locked path too;
different ids with equal specializations ⇒ bad; different specializations ⇒ moved (benign). ~150 lines, low risk.
Side effect [I]: the walker stops writing the shared SRT memo (only when `srtmemo` is on).

## C. Order

B first (expected ≈ the family skip's −142 µs ceiling, safe by construction), then A (−150…−200 µs [I]). Optional
cheap step for A: time the ring push + notify inside today's tag-1 hold (~2796–2819); if large, move it out of
`m_mutex` (~20 lines).
