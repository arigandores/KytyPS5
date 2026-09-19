# Session 99 addendum03 — identify the R6' recovery burst

SEALED before the diagnostic run below. This does not edit pred01/pred02, admit eng99a3,
freeze its budget, change50 to52, or publish any B from a pilot. The user authorised the
necessary work and game runs to complete both instruments in THIS session.

## Prior facts and question

eng99a3 has matched settled dt0.2093% and work0.2422%, but R6' median52>50, hence remains
NOT_MEASUREMENT. Raw investigation found actual extra insertion activity after falling
edges even after draw normalization; first3 rows average54.167 inserts/8.25 recycle hits,
versus clean windows20.329/20.107. Frees peak later around idx9. This is not merely a
different mix of presentation rows, and does not identify the inserted objects or their cause.

Source says img_new counts every TextureCache::InsertImage, including undefined-format
stencil records and inserts reusing VkImage backing. GC hold suppresses noncritical collection
and freezes its clock in mode2, but critical pressure and other deletion paths remain possible.
Existing ImageLife tracing prints create/free, reason, source line, present counter and
address/size/geometry/format/tiling/pitch. It has no ImageId/samples/full mip layout.

## One diagnostic process, not a measurement

Tag life99a, one process, --hold300 --attempts1, no warmup-first/video. Binary remains
2a6bb5388d8fdd97a4aab20e1bde2715e3d92ad499c49b7cd2ea094ec0385c87 (23741440 bytes).
Same gates_base, p90+1800 ABBA, mode2, drawahead1 both arms, fixed bfburn17800 both arms,
latch1/clear0/pin1/CPUobserver1/markers0/checkpoints0. The fixed17800 is a diagnostic
setting, not an admitted freeze. Add positionally:
KYTY_IMAGE_LIFETIME_TRACE=1 KYTY_IMAGE_LIFETIME_MIN_KB=0 KYTY_IMAGE_LIFETIME_FROM=0.
The logger is uncapped and starts at process beginning; no filters chosen after the trace.

One executor only. No build, other scorer or analysis during the hold. Preserve full raw,
metadata and stdout. Check survival and log completeness after closure; do not run the
settled B scorer on this tracing process. Tracing changes workload, so no B/time benefit,
work acceptance, tuning correction or architecture verdict can come from it.

## Fixed analysis

1. Count every ImageLife create/free by reason and printed signature. Compare total create
   coverage against img_new, accounting explicitly for first/last snapshot boundaries.
2. Enumerate EVERY falling edge and its first3 FrameTrace rows, plus the immediately following
   same-arm block's first3 rows as a fixed clean control. Keep incomplete controls labelled
   incomplete; do not select windows for a desired count. Also print the complete per-index
   profile through the first30 rows and the already fixed idx60..88 window.
3. Attribute creates conservatively: undefined-format bookkeeping; first observed signature;
   a signature previously freed directly by RunGarbageCollector; other prior free reasons
   (ResolveOverlap/ResolveDepthOverlap/ExpandImage/UnmapMemory/etc); ambiguous identity.
   Address equality alone does not prove object identity. Exact printed signature is still
   missing samples/full layout, so uncertain matches remain ambiguous. Separate frees during
   armed interior from frees before it, rather than attributing all past GC to the floor.
4. ImageLife.frame is GpuTimeProfiler::Frame, set on the presentation thread before Poll and
   the asynchronous FrameTrace snapshot. Events near a row boundary can straddle snapshots.
   Report whole-period classifications and explicit +/-1 boundary uncertainty; do not choose
   a shift that makes R6 pass. Correlating lifetimes is diagnostic, not a new admission.

## Outcomes and continuation

If floor-induced GC eviction/recreation or an incorrect alias/lifetime change is identified,
fix that concrete source mechanism, review/build, then independently reconfirm both instruments.
If the burst consists of legitimate bookkeeping/rebinding of resources skipped by the floor,
document that R6' is an overbroad proxy for this instrument. A better control must be written
under a separate addendum before new measurement data, with unchanged old FAILs and a test
that still detects a real cache-loss storm. Do not silently turn the old52 into an allowed50.
If signatures cannot identify the cause, add a direct identity/cause witness, not a new
arbitrary tolerance. Continue the user's task; this diagnostic is not its final deliverable.

Predictions before data: no process hang; create tracing is present from startup; fewer than
1000 recovery inserts (the historical eviction avalanche) per falling edge; the type/cause
composition remains a hypothesis until counted. No prediction is an admission threshold.
