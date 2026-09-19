# Causal composition (diagnostic only)

GC is mapped from reported operator():3402, confirmed at textureCache.cpp:3402. The baseline printed-name assumption was corrected explicitly. No change of acceptance rules.

## Coverage and exclusion of an armed-interior eviction storm

Whole raw SHA256 matches fd5f717d1b9ecdc0ee70b4e4c24a9607f96cfc3fffab895b4c2de8128a7172d5. 64,121 events =32,652 creates+31,469 frees. Sum img_new32,593 differs by59, exactly55 creates before first draw snapshot plus4 after last. Sum img_free31,465 differs by4 terminal frees at frame6210. Thus there is no unexplained global create/free deficit. First/last FrameTrace n=2/6210.

All31,469 frees are assigned:15,942 before gates,15,446 unarmed,81 armed boundary, ZERO armed interior. GC subset10,581=6,679 pregate+3,901 unarmed+1 armed boundary+ZERO armed interior. Interior conservatively means event_idx2..87 so both +/-1 boundary placements stay armed. Free reasons:depth overlap15,535; GC10,581; overlap5,348; DeleteImage3; FindImage2. No armed-interior GC-loss storm is present in this complete event stream.

The81 armed-boundary frees are depth52 at idx0+24 at idx1, overlap4 at idx0, GC1 at idx0. The lone GC free is rawline886697, frame4770/block33/rising idx0, BC5 2048x2048, last_frame4759. None of the recovery GC candidates point to it. Its boundary phase remains uncertain; the analysis does not claim that every possible boundary eviction is excluded.

## Event.frame = row.n -1

fall: new printed signatures=311; first-ever addresses=153, earlier address with different printed signature=158. GC candidates=181, before current floor start=181.

Top new-signature shapes (w,h,mips,fmt,bytes): [((2048, 2048, 12, 141, 5636096), 172), ((1024, 1024, 11, 141, 1441792), 93), ((1024, 1024, 11, 139, 720896), 18), ((512, 512, 10, 141, 393216), 7), ((256, 256, 9, 141, 131072), 6), ((2048, 2048, 12, 139, 2818048), 3), ((4096, 4096, 13, 141, 22413312), 3), ((1, 1, 1, 43, 256), 2)].

sameU: new printed signatures=24; first-ever addresses=3, earlier address with different printed signature=21. GC candidates=30, before current floor start=13.

Top new-signature shapes (w,h,mips,fmt,bytes): [((2048, 2048, 12, 141, 5636096), 8), ((1024, 1024, 11, 141, 1441792), 8), ((4096, 4096, 13, 141, 22413312), 2), ((512, 512, 10, 141, 393216), 2), ((512, 512, 10, 139, 196608), 2), ((1024, 1024, 11, 146, 1441792), 1), ((256, 256, 9, 141, 131072), 1)].

## Event.frame = row.n +0

fall: new printed signatures=273; first-ever addresses=130, earlier address with different printed signature=143. GC candidates=163, before current floor start=163.

Top new-signature shapes (w,h,mips,fmt,bytes): [((2048, 2048, 12, 141, 5636096), 155), ((1024, 1024, 11, 141, 1441792), 79), ((1024, 1024, 11, 139, 720896), 13), ((512, 512, 10, 141, 393216), 6), ((256, 256, 9, 141, 131072), 6), ((4096, 4096, 13, 141, 22413312), 3), ((2048, 2048, 12, 139, 2818048), 2), ((1, 1, 1, 43, 256), 2)].

sameU: new printed signatures=21; first-ever addresses=2, earlier address with different printed signature=19. GC candidates=38, before current floor start=16.

Top new-signature shapes (w,h,mips,fmt,bytes): [((1024, 1024, 11, 141, 1441792), 9), ((2048, 2048, 12, 141, 5636096), 5), ((512, 512, 10, 141, 393216), 2), ((512, 512, 10, 139, 196608), 2), ((4096, 4096, 13, 141, 22413312), 1), ((1024, 1024, 11, 146, 1441792), 1), ((256, 256, 9, 141, 131072), 1)].

## Event.frame = row.n +1

fall: new printed signatures=40; first-ever addresses=15, earlier address with different printed signature=25. GC candidates=9, before current floor start=9.

Top new-signature shapes (w,h,mips,fmt,bytes): [((2048, 2048, 12, 141, 5636096), 35), ((1024, 1024, 11, 141, 1441792), 4), ((1024, 1024, 11, 139, 720896), 1)].

sameU: new printed signatures=14; first-ever addresses=2, earlier address with different printed signature=12. GC candidates=37, before current floor start=21.

Top new-signature shapes (w,h,mips,fmt,bytes): [((2048, 2048, 12, 141, 5636096), 7), ((1024, 1024, 11, 141, 1441792), 5), ((1024, 1024, 11, 139, 720896), 1), ((256, 256, 9, 141, 131072), 1)].

## Whole block classification by event.frame (no first3 slicing)

|block|arm|events creates|classes|
|---|---|---|---|
|0|{'unarmed': 923}|923|{'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 180, 'first_observed_signature': 239, 'prior_free_RunGarbageCollector': 180, 'prior_free_ResolveOverlap': 54}|
|1|{'armed_boundary': 6}|6|{'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|3|{'unarmed': 644}|644|{'prior_free_RunGarbageCollector': 28, 'first_observed_signature': 164, 'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 181}|
|4|{'unarmed': 567}|567|{'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 180, 'prior_free_RunGarbageCollector': 52, 'first_observed_signature': 65}|
|5|{'armed_boundary': 6}|6|{'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|7|{'unarmed': 597}|597|{'first_observed_signature': 77, 'prior_free_RunGarbageCollector': 68, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181, 'prior_free_ResolveOverlap': 1}|
|8|{'unarmed': 539}|539|{'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 180, 'first_observed_signature': 40, 'prior_free_RunGarbageCollector': 45, 'prior_free_ResolveOverlap': 3}|
|9|{'armed_boundary': 6}|6|{'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|11|{'unarmed': 561}|561|{'first_observed_signature': 54, 'prior_free_RunGarbageCollector': 55, 'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 181}|
|12|{'unarmed': 548}|548|{'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 180, 'first_observed_signature': 27, 'prior_free_RunGarbageCollector': 69, 'prior_free_ResolveOverlap': 2}|
|13|{'armed_boundary': 6}|6|{'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|15|{'unarmed': 616}|616|{'first_observed_signature': 76, 'prior_free_ResolveOverlap': 3, 'prior_free_RunGarbageCollector': 86, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181}|
|16|{'unarmed': 601}|601|{'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 180, 'first_observed_signature': 75, 'prior_free_RunGarbageCollector': 75, 'prior_free_ResolveOverlap': 1}|
|17|{'armed_boundary': 7}|7|{'prior_free_ResolveDepthOverlap': 4, 'ambiguous_live_signature': 3}|
|19|{'unarmed': 636}|636|{'prior_free_RunGarbageCollector': 94, 'first_observed_signature': 90, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181, 'prior_free_ResolveOverlap': 1}|
|20|{'unarmed': 573}|573|{'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 180, 'first_observed_signature': 60, 'prior_free_RunGarbageCollector': 62, 'prior_free_ResolveOverlap': 1}|
|21|{'armed_boundary': 7}|7|{'prior_free_ResolveDepthOverlap': 4, 'ambiguous_live_signature': 3}|
|23|{'unarmed': 640}|640|{'prior_free_RunGarbageCollector': 103, 'first_observed_signature': 83, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181, 'prior_free_ResolveOverlap': 3}|
|24|{'unarmed': 612}|612|{'prior_free_ResolveDepthOverlap': 270, 'first_observed_signature': 67, 'ambiguous_live_signature': 180, 'prior_free_RunGarbageCollector': 94, 'prior_free_ResolveOverlap': 1}|
|25|{'armed_boundary': 7}|7|{'prior_free_ResolveDepthOverlap': 4, 'ambiguous_live_signature': 3}|
|27|{'unarmed': 648}|648|{'prior_free_RunGarbageCollector': 118, 'first_observed_signature': 75, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181, 'prior_free_ResolveOverlap': 4}|
|28|{'unarmed': 574}|574|{'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 180, 'prior_free_RunGarbageCollector': 82, 'first_observed_signature': 37, 'prior_free_ResolveOverlap': 4}|
|29|{'armed_boundary': 6}|6|{'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|31|{'unarmed': 619}|619|{'prior_free_RunGarbageCollector': 112, 'first_observed_signature': 51, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181, 'prior_free_ResolveOverlap': 5}|
|32|{'unarmed': 574}|574|{'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 180, 'prior_free_RunGarbageCollector': 87, 'first_observed_signature': 32, 'prior_free_ResolveOverlap': 5}|
|33|{'armed_boundary': 8}|8|{'prior_free_ResolveDepthOverlap': 4, 'first_observed_signature': 1, 'ambiguous_live_signature': 3}|
|35|{'unarmed': 630}|630|{'first_observed_signature': 82, 'prior_free_RunGarbageCollector': 93, 'prior_free_ResolveOverlap': 4, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181}|
|36|{'unarmed': 593}|593|{'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 180, 'prior_free_RunGarbageCollector': 78, 'first_observed_signature': 63, 'prior_free_ResolveOverlap': 1}|
|37|{'armed_boundary': 6}|6|{'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|39|{'unarmed': 632}|632|{'first_observed_signature': 104, 'prior_free_RunGarbageCollector': 75, 'prior_free_ResolveOverlap': 1, 'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 181}|
|40|{'unarmed': 622}|622|{'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 180, 'first_observed_signature': 70, 'prior_free_RunGarbageCollector': 99, 'prior_free_ResolveOverlap': 3}|
|41|{'armed_boundary': 7}|7|{'first_observed_signature': 1, 'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|43|{'unarmed': 632}|632|{'first_observed_signature': 108, 'prior_free_RunGarbageCollector': 70, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181, 'prior_free_ResolveOverlap': 3}|
|44|{'unarmed': 621}|621|{'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 180, 'prior_free_RunGarbageCollector': 96, 'first_observed_signature': 72, 'prior_free_ResolveOverlap': 2}|
|45|{'armed_boundary': 6}|6|{'prior_free_ResolveDepthOverlap': 3, 'ambiguous_live_signature': 3}|
|47|{'unarmed': 645}|645|{'first_observed_signature': 95, 'prior_free_RunGarbageCollector': 95, 'prior_free_ResolveDepthOverlap': 270, 'ambiguous_live_signature': 181, 'prior_free_ResolveOverlap': 4}|
|48|{'unarmed': 585}|585|{'prior_free_ResolveDepthOverlap': 271, 'ambiguous_live_signature': 180, 'prior_free_RunGarbageCollector': 90, 'prior_free_ResolveOverlap': 5, 'first_observed_signature': 39}|
|49|{'armed_boundary': 4}|4|{'prior_free_ResolveDepthOverlap': 2, 'ambiguous_live_signature': 2}|

## Interpretation and next concrete engineering step

The excess is overwhelmingly first observed compressed texture signatures plus recreation candidates last freed by ordinary unarmed GC BEFORE the current floor began. At the complete-count -1 alignment, first-signature excess287 and old-GC-candidate excess151 dominate net402 extra inserts (other classes offset36). At nominal alignment the same two classes give252+125 of net406. First-signature textures are chiefly BC5_UNORM mip chains (fmt141); BC4_UNORM is fmt139 (Vulkan SDK vulkan_core.h:1989,1987). Recovery has ZERO fmt0 stencil bookkeeping in all three alignments; there are only5 such creates in the entire process.

This supports deferred materialization/rebinding of sampled texture requests skipped during mode2, and contradicts the specific hypothesis that the floor evicted live images in its armed interior. It does not certify legitimacy of every requested new texture: guest generation, full samples/layout and stable host ImageId are absent; old-signature recreation is a candidate rather than proven same object. Fresh-address samples cannot be recreation of an earlier printed address in this process. The shift+1 windows exclude much of the actual burst; they remain reported, never chosen to reduce R6.

For the next implementation, distinguish loss of live pre-floor cache entries from legitimate requests after return. A direct pre-floor ImageId/generation membership witness with free reason/phase and per-create previous-membership output is narrowly sufficient; keep explicit uncertain/new-signature counts. This can support a separately sealed replacement for an overbroad total-insert proxy while still detecting the historical1000-image cache-loss storm. Do not increase50 to52 and do not alter recycle-pool policy to reduce img_new: pool reuse occurs after the insertion counter and changes backing allocation, not insertion count. All old failures remain failures.

Example fall shift-1: firstsignature rawline562602; priorGC recreation rawline562618, previous free rawline525258.
Example sameU shift-1: firstsignature rawline616435; priorGC recreation rawline574145, previous free rawline571331.
Example fall shift0: firstsignature rawline562871; priorGC recreation rawline562618, previous free rawline525258.
Example sameU shift0: firstsignature rawline657452; priorGC recreation rawline574163, previous free rawline571431.
Example fall shift1: firstsignature rawline562942; priorGC recreation rawline563187, previous free rawline530513.
Example sameU shift1: firstsignature rawline616890; priorGC recreation rawline574487, previous free rawline569615.