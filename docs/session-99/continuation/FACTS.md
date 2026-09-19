# Session 99 — bindings-only measurement completed; experimental video artifacts isolated

Budget for60FPS: <=~3.0us/draw, <=~2.3us at p99 (7284 draws). The historical admitted
reference is6.4us/draw,31.6ms/frame,GPU busy12.8ms; it is NOT a new baseline measured here.
M3's requested bindings-only experiment is completed below; global M3 remains GAP,
G/R1 are not licensed or closed, and M4/M5 remain undone in the user's chosen order.
No frame-rate improvement or60FPS is proved by this destructive diagnostic.

## 1. Final accepted result

| independent confirmation | CPU endpoint ms | wall compatibility ms | work difference | technical / strict | pairs / falls |
|---|---:|---:|---:|---|---|
|bf99g (a)|30.049869086|30.596798362|-0.245535675%|43/43 + 6/6 PASS|88 / 45|
|bf99h (c)|37.367904034|37.984519672|+0.105147315%|44/44 + 6/6 PASS|88 / 45|

Both confirmations ran900.3s without recording; each retains2552 rows/arm and44 AB +44 BA pairs.

The endpoint is the median of the retained ARMED block means of
`(cpu_gpu_us - spin_gpu_us - bf_burn_cpu_ns/1000)/1000`. The wall-burn endpoint is printed
alongside for compatibility and is not the deciding clock. The CPU query indicator is
about1.7ms/retained frame; it is not total instrumentation cost and is not silently deducted.
Instrument a keeps drawahead=1 in both arms. Instrument c keeps it in BASE and switches
it off under the floor. Mode2 retains real materialisation, including actual clears;
it removes the ordinary bindings path and directs ordinary shader descriptors to nulls.

**Combined: HIGH, DIAGNOSTIC ONLY**: min(B_a,B_c)=30.049869086ms >=15.5ms.
The requested bindings-only pair is measured on both instruments; no global M3 closure follows.

The sealed rule produces a limited HIGH/LOW/GAP diagnostic with no additional2.2535 term.
It does not reinterpret session98's full-floor values14.274/12.825ms or their global GAP.
Differences against those older binaries/clocks are descriptive, not pure materialisation
timers. No bound on all residual pessimism or a correctness-preserving replacement follows.

## 2. What changed, and why the first attempts remain failures

The user explicitly authorised runs and then required completion in THIS session. Earlier
stopping point cal99a and the proposed next-session100 continuation are superseded as the
current plan, not erased as historical results. The exact former FACTS is saved in
FACTS_cal99a.md (SHA d6042c2f06705b0db5f75f8f1dbfb98c7cc508bc09f0b8c9c7f6a3686bc92d77).

| tag | rule / purpose | actual result |
|---|---|---|
| cal99a |01,180.1s,period30,burn12000|NOT ADMITTED: work-4.097420%,17falls<30; no accepted burn/B|
| eng99a1 |02,300.1s,burn20000|technical/work/area PASS; dt1.833857% ->TUNE19100|
| eng99a2 |02,300.1s,burn19100|technical/work/area PASS; dt2.59784% ->TUNE17800|
| eng99a3 |02,300.1s,burn17800|dt0.209276%,work+0.242228%; image proxy R6'=52>50 FAIL; noLOCK/B|
| life99a |03,300.1s,all image lifetimes|diagnostic only;64121events,0 armed-interior frees, noCPU endpoint|
| eng99a4 |04,fresh300.1s,burn17800|LOCK17800;40/40 technical,6/6 strict; work-0.023650%,dt0.004225%|
| bf99e |04,900.3s WITH recording|NOT MEASUREMENT: work-0.710639% fails0.5%;41/41 technical and other5strict pass; noB|
| vis99base |05,900.3s recorded, bothfloor0|normal-mode visual control;17802frames,0 detector events|
| aa99plain |05,300.1s,no-record bothfloor0|AA_PASS:14/14+6/6,22pairs,work+0.034829%,dt0.102928%; noB|
| bf99g |05,900.3s,no-record,a|admitted independent confirmation from exacteng99a4 LOCK|
| eng99c1 |05,300.1s,reset17800|43/43technical; C9FAIL15.35058%,work+0.414749%; TUNE10200, noB|
| eng99c2 |05,300.1s,burn10200|LOCK10200;43/43+6/6,work+0.208306%,dt0.424619%; noB|
| bf99h |05,900.3s,no-record,c|admitted independent confirmation from exacteng99c2 LOCK|

No run was blindly repeated to erase a failure. Engineering TUNE/LOCK, fixed hold lengths,
source chains and independent confirmations were specified before the corresponding data.
No default rendering optimisation was enabled or shipped.

## 3. Clock, settled population, and GC audit

The old wall burn cannot be subtracted as if it were thread CPU. Added default-off
`KYTY_BIND_FLOOR_CPU=1`: sample the same ThreadCpuNs(Gpu) used by cpu_gpu_us around each
actual burn, count positive samples/bad samples and query elapsed time. Budget and burn
loop still use the original wall clock. Residual query/counter overhead remains in B.
The two CPU queries and cross-counter snapshots are not an atomic per-guest-frame observer.

Raw cal99a diagnosis found a long transition in presentation-row composition. Pred02
therefore fixed period90,start1800,n>=2100,idx60..88 (29 rows), and COMPLETE original
ABBA quartets BEFORE new data. Each quartet yields two disjoint pairs; no re-pairing,
re-use, missing internal block or posthoc window selection is allowed. Work abs<0.5%,
area abs<1%,pair matching>=90%,C9<=3% remain unchanged. Full-log technical controls remain.
Historical whole-window work checks still fail in several admitted settled experiments
(bf99g about-1.491%); the old outcomes are printed, not relabelled or used as the endpoint.

The image birth proxy failed although the actual mechanism it was meant to catch did not
occur. Full life99a traces:32652 creates,31469 frees, no armed-interior free. Excess recovery
births include new BC5/BC4 signatures and recreations whose GC deletion happened BEFORE the
current floor interval. Alignment alternatives were reported, not selected to admit a run.
GC's age is per CALL, not per guest frame. A recycle pool affects reuse, not Insert count.

Added default-off `KYTY_BIND_FLOOR_GC_AUDIT=1` without changing collection policy. It checks
the actual age delta, held-clock state, critical override and GC root evictions; an independent
current-slice sticky subset catches missed holds without adopting a latch. It does NOT
independently prove every base/pending path of BindFloorGcHold. Future pred04 admission
requires checks/held counts positive as prescribed, bad/critical/evict zero. Image R6/R6'
remain visible REPORT-ONLY (bf99g54/64 FAIL), while buffer R7/R7' still decide (bf99g2/4 PASS).
No threshold was raised; a direct mechanism audit replaced an invalid proxy for future data.

## 4. The user's glitch report and the separate control

bf99e contains conspicuous late flashes/effects, including BASE rows after the floor falls.
The same streaming three-frame detector reports185 events on18037 frames:174 in armed rows,
11 in base rows. Deliberately null bindings do not provide a correctness-preserving render.
There are real PM4 GDS DMA/export, BDA table/fault and compute-clear paths outside ordinary
null bindings. Shader GDS itself IS nulled. These are mechanisms to investigate, not a
proven attribution of the visible effects.

Sealed05 then ran one900.3s control with recording and both label arms floor0. All178 gate
assignments were0;17793 main rows have inactive floor counters.17802 decoded frames,0 detector
events; parent inspected fixed450/825/900s wall-time frames and did not see the reported late
effects. The user independently said "глитчей не видел при прогоне". This supports non-reproduction
without the floor. It does not identify the exact corrupting operation or prove every pixel
correct. See VISUAL99.md, video99_comparison/manifest.json and verify99_visual_raw/VERIFY.md.

Video MP4 is encoded at60fps while .idx maps frames to real elapsed time. vis99base playback
296.7s corresponds to917.981s in its index; bf99e300.6167s to917.681s. Timing comparisons use
the raw/index clocks, not playback minutes. Sleeping/prone Astro is ordinary idle animation.

Recording puts copy/wait/queue work before asynchronous presentation statistics. bf99e has
52 retained BASE rows with draws<10, versus0 in its no-record pilot. Work difference tracks
GC-call count but GC calls are NOT a new guest-frame denominator. Recording is a plausible
observer contribution, not proved to be the sole cause. Pred05 separated video from CPU:
KYTY_REC must be absent and no runtime Recording marker; RecordThread remains a normal
backend thread. Failed bf99e was not rescued by new normalization, windows or a relaxed limit.

## 5. Independent verification and immutable provenance

CPU observer C++ fresh review PASS; direct GC C++ review PASS with38 model cases including
10 detected mutants. Both builds passed through build_local.cmd, one builder at a time.
Scorer02:19 tests; scorer04:22 tests plus40 focused independent cases. Fresh05 review found
a wholly missing internal block could escape continuity checks; fixed ONLY05 before new
data.14 tests and independent missing-block/duplicate/order mutants now pass the intended
rejection. A runtime marker format mismatch in04 was fixed before its first inferential run.
Earlier failed review/test artifacts remain in the archive.

Fresh verify99_observer actually replayed eng99a4 under unchanged04: byte-identical JSON,
not just a trusted LOCK label. Fresh verify99_confirm_raw independently counted bf99g;
fresh verify99_c_raw independently confirmed c and the limited combined HIGH. Parent's own separate parent_recount99.py checks the raw fixed populations,
work/area/dt and CPU endpoint against the scorer. Final combination replays both inputs.

| immutable rule | bytes | SHA256 |
|---|---:|---|
|01_bindings_only.md|10848|8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d|
|02_settled_bindings.md|13461|1d1ebf286869ab59944fe135fc5c69d1315d4c61667b6c3dd2ab3ca14839724c|
|03_image_lifetime_diagnostic.md|4724|d17745315149f0caad27f4c4764350f3e255fc9949a5b0287d9ea2a5e2c42c90|
|04_gc_audit.md|7835|a93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b|
|05_observer_separation.md|8583|fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0|

Final scorer05 SHA8216acd9797f7b2eeb61f2654a7827daed3f103ac0a07ec3b80a570ae6626399;
unchanged04 SHAbe2a9a317fded5ee3ee6b421312d60e3fb6e9cd22c643eb3b7ec89a1258adef6.
AA source SHA3c8c8ed44a93ad1d9295016e0e5cdc7602f142d6be443ad6863e292b1068a55e;
a LOCK SHA9f021e8bcc080f03a3309c851629f01c49b7f54868dd75b2a62b6ee28e175e8e;
c LOCK SHAf8df75ffde566f43e7120462877fa30a81fe7803b1669ae5e26bf21f4069d6a4.
Source and AA tags/hashes were positional launch arguments, raw-replayed rather than trusted.

## 6. Installed state, archive, and remaining work

Installed/saved/build executable:34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f,
23743488 bytes. Earlier CPU-observer build2a6bb538...23741440 bytes and first99 buildee9cc8ab...
23739904 bytes remain local. Gates base is unchanged1092 bytes/99 names,
SHA00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8.
After testing only stale Session100 comments were corrected to99; executable code was not
changed or rebuilt. Executables/raw logs/maps/videos remain local with hashes; small rules,
scorers, raw summaries and reviews are archived under docs/session-99/continuation. Old seals
and33 original canonical entries remain unchanged. No push; unrelated submodule deletions
are excluded from the task commit. Earlier commits are a3558a2(preparation),b129fbb(first fail).

Proved: both bindings-only CPU endpoints, fixed-population admission, direct GC checks,
and non-reproduction of the reported late artifacts in the separate no-floor visual control. Not proved: a frame-rate gain, correctness-preserving bindings removal,
all instrumentation pessimism, exact cause of floor artifacts, global G/R1 licensing or60FPS.
Remaining: complete the broader M3 decision with an explicit valid rule/bound; then M4 andM5
in the user's order. The inter-queue ACB latch gap, entry BVH hang and prior ROADMAP debts
remain open. Do not spend another session recalibrating these completed bindings-only numbers
or silently treat their HIGH/LOW diagnostic as a global M3 close.
