# Image lifetime diagnostic — fixed exploratory analysis

Printed-signature matches are candidates, not proven object identity: ImageID/samples/full mip layouts are absent. Nominal mapping uses event.frame = row.n. Shifts -1,0,+1 are all printed, never selected for admission. No B or admission computed. Source correction: reported reason=operator(),line=3402 is the GC lambda, mapped to RunGarbageCollector; original reported_reason is preserved.

## Global coverage

{
  "raw_sha256": "fd5f717d1b9ecdc0ee70b4e4c24a9607f96cfc3fffab895b4c2de8128a7172d5",
  "events": 64121,
  "creates": 32652,
  "frees": 31469,
  "rows": 6209,
  "row_img_new": 32593,
  "row_img_free": 31465,
  "free_reasons": {
    "ResolveOverlap": 5348,
    "RunGarbageCollector": 10581,
    "DeleteImage": 3,
    "ResolveDepthOverlap": 15535,
    "FindImage": 2
  },
  "create_classes": {
    "first_observed_signature": 8287,
    "undefined_bookkeeping": 5,
    "prior_free_RunGarbageCollector": 4574,
    "ambiguous_live_signature": 7751,
    "prior_free_ResolveDepthOverlap": 11627,
    "prior_free_ResolveOverlap": 407,
    "prior_free_DeleteImage": 1
  },
  "create_candidate_causes": {
    "first_observed_signature": 8291,
    "prior_free_RunGarbageCollector": 4574,
    "ambiguous_live_signature": 7751,
    "prior_free_ResolveDepthOverlap": 11627,
    "prior_free_ResolveOverlap": 407,
    "prior_free_DeleteImage": 2
  },
  "free_phases": {
    "pregate": 15942,
    "unarmed": 15446,
    "armed_boundary": 81
  },
  "gc_frees_by_phase": {
    "pregate": 6679,
    "unarmed": 3901,
    "armed_boundary": 1
  },
  "negative_live_signatures": 0,
  "create_boundary_counts": {
    "before_first_draw": 55,
    "after_last_draw": 4,
    "first_row": 2,
    "last_row": 6210
  }
}

## Every fixed first3 window

|kind|block|shift|rows|img_new|event creates|event frees|classifications|prior GC phase|
|---|---|---|---|---|---|---|---|---|
|fall|3|-1|3|88|88|33|{'first_observed_signature': 69, 'prior_free_RunGarbageCollector': 7, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'unarmed': 4, 'pregate': 3}|
|sameU|4|-1|3|17|17|18|{'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 3}|{'unarmed': 3}|
|fall|3|0|3|88|74|38|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'first_observed_signature': 53, 'prior_free_RunGarbageCollector': 4}|{'unarmed': 3, 'pregate': 1}|
|sameU|4|0|3|17|20|15|{'prior_free_RunGarbageCollector': 6, 'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6}|{'unarmed': 6}|
|fall|3|1|3|88|24|37|{'first_observed_signature': 4, 'prior_free_ResolveDepthOverlap': 11, 'ambiguous_live_signature': 8, 'prior_free_RunGarbageCollector': 1}|{'unarmed': 1}|
|sameU|4|1|3|17|19|18|{'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 5}|{'unarmed': 5}|
|fall|7|-1|3|65|65|19|{'first_observed_signature': 32, 'prior_free_RunGarbageCollector': 21, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'pregate': 3, 'unarmed': 18}|
|sameU|8|-1|3|17|17|16|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'first_observed_signature': 1, 'prior_free_RunGarbageCollector': 1}|{'unarmed': 1}|
|fall|7|0|3|65|74|28|{'prior_free_ResolveDepthOverlap': 12, 'ambiguous_live_signature': 9, 'first_observed_signature': 32, 'prior_free_RunGarbageCollector': 21}|{'pregate': 3, 'unarmed': 18}|
|sameU|8|0|3|17|17|20|{'prior_free_ResolveDepthOverlap': 10, 'prior_free_RunGarbageCollector': 1, 'ambiguous_live_signature': 6}|{'unarmed': 1}|
|fall|7|1|3|65|19|25|{'prior_free_ResolveDepthOverlap': 11, 'ambiguous_live_signature': 8}|{}|
|sameU|8|1|3|17|19|21|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'first_observed_signature': 3}|{}|
|fall|11|-1|3|38|38|14|{'first_observed_signature': 15, 'prior_free_RunGarbageCollector': 11, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'unarmed': 9, 'pregate': 2}|
|sameU|12|-1|3|18|18|16|{'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 2}|{'unarmed': 2}|
|fall|11|0|3|38|45|22|{'prior_free_ResolveDepthOverlap': 11, 'ambiguous_live_signature': 8, 'first_observed_signature': 15, 'prior_free_RunGarbageCollector': 11}|{'unarmed': 9, 'pregate': 2}|
|sameU|12|0|3|18|18|16|{'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 2}|{'unarmed': 2}|
|fall|11|1|3|38|22|21|{'prior_free_ResolveDepthOverlap': 11, 'ambiguous_live_signature': 8, 'first_observed_signature': 3}|{}|
|sameU|12|1|3|18|19|18|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 2}|{'unarmed': 2}|
|fall|15|-1|3|38|38|13|{'first_observed_signature': 12, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5, 'prior_free_ResolveOverlap': 1}|{'unarmed': 12, 'pregate': 1}|
|sameU|16|-1|3|19|19|22|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 2}|{'pregate': 2}|
|fall|15|0|3|38|29|23|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'first_observed_signature': 5, 'prior_free_RunGarbageCollector': 7}|{'unarmed': 7}|
|sameU|16|0|3|19|17|20|{'prior_free_ResolveDepthOverlap': 10, 'prior_free_RunGarbageCollector': 1, 'ambiguous_live_signature': 6}|{'pregate': 1}|
|fall|15|1|3|38|19|20|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'first_observed_signature': 4}|{}|
|sameU|16|1|3|19|20|20|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 3, 'prior_free_ResolveOverlap': 1}|{'unarmed': 3}|
|fall|19|-1|3|58|58|14|{'prior_free_RunGarbageCollector': 20, 'first_observed_signature': 26, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'unarmed': 20}|
|sameU|20|-1|3|21|21|21|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 3}|{'unarmed': 3}|
|fall|19|0|3|58|64|24|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'first_observed_signature': 27, 'prior_free_RunGarbageCollector': 20}|{'unarmed': 20}|
|sameU|20|0|3|21|21|21|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 3}|{'unarmed': 3}|
|fall|19|1|3|58|24|26|{'first_observed_signature': 5, 'prior_free_ResolveDepthOverlap': 11, 'ambiguous_live_signature': 8}|{}|
|sameU|20|1|3|21|21|18|{'prior_free_RunGarbageCollector': 2, 'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6, 'first_observed_signature': 5}|{'unarmed': 2}|
|fall|23|-1|3|52|52|15|{'prior_free_RunGarbageCollector': 21, 'first_observed_signature': 19, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'unarmed': 20, 'pregate': 1}|
|sameU|24|-1|3|21|21|16|{'prior_free_ResolveDepthOverlap': 9, 'first_observed_signature': 2, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 4}|{'unarmed': 4}|
|fall|23|0|3|52|46|22|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'prior_free_RunGarbageCollector': 17, 'first_observed_signature': 12}|{'unarmed': 17}|
|sameU|24|0|3|21|20|19|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 4, 'first_observed_signature': 1}|{'unarmed': 4}|
|fall|23|1|3|52|21|21|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 5}|{'unarmed': 5}|
|sameU|24|1|3|21|20|20|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 4, 'first_observed_signature': 1}|{'unarmed': 4}|
|fall|27|-1|3|49|49|15|{'prior_free_RunGarbageCollector': 18, 'first_observed_signature': 19, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'unarmed': 16, 'pregate': 2}|
|sameU|28|-1|3|16|16|21|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6}|{}|
|fall|27|0|3|49|55|20|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'first_observed_signature': 20, 'prior_free_RunGarbageCollector': 18}|{'unarmed': 16, 'pregate': 2}|
|sameU|28|0|3|16|20|17|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 5}|{'unarmed': 5}|
|fall|27|1|3|49|22|23|{'first_observed_signature': 5, 'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7}|{}|
|sameU|28|1|3|16|19|16|{'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 5}|{'unarmed': 5}|
|fall|31|-1|3|56|56|22|{'prior_free_RunGarbageCollector': 25, 'first_observed_signature': 18, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5, 'prior_free_ResolveOverlap': 1}|{'pregate': 1, 'unarmed': 24}|
|sameU|32|-1|3|18|18|19|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 3}|{'unarmed': 3}|
|fall|31|0|3|56|61|27|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'first_observed_signature': 18, 'prior_free_RunGarbageCollector': 25, 'prior_free_ResolveOverlap': 1}|{'unarmed': 24, 'pregate': 1}|
|sameU|32|0|3|18|18|18|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 3}|{'unarmed': 3}|
|fall|31|1|3|56|19|17|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'first_observed_signature': 3, 'prior_free_RunGarbageCollector': 1}|{'unarmed': 1}|
|sameU|32|1|3|18|16|18|{'prior_free_ResolveDepthOverlap': 9, 'prior_free_RunGarbageCollector': 1, 'ambiguous_live_signature': 6}|{'unarmed': 1}|
|fall|35|-1|3|44|44|16|{'first_observed_signature': 19, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveOverlap': 1, 'prior_free_ResolveDepthOverlap': 6, 'ambiguous_live_signature': 5}|{'unarmed': 12, 'pregate': 1}|
|sameU|36|-1|3|16|16|20|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6}|{}|
|fall|35|0|3|44|50|22|{'prior_free_ResolveDepthOverlap': 10, 'first_observed_signature': 19, 'ambiguous_live_signature': 7, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveOverlap': 1}|{'unarmed': 12, 'pregate': 1}|
|sameU|36|0|3|16|21|21|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 4, 'first_observed_signature': 1}|{'unarmed': 4}|
|fall|35|1|3|44|22|19|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'first_observed_signature': 6}|{}|
|sameU|36|1|3|16|20|20|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 4, 'first_observed_signature': 1}|{'unarmed': 4}|
|fall|39|-1|3|49|49|21|{'first_observed_signature': 24, 'prior_free_RunGarbageCollector': 12, 'prior_free_ResolveOverlap': 1, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'unarmed': 12}|
|sameU|40|-1|3|19|19|15|{'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6, 'first_observed_signature': 3, 'prior_free_RunGarbageCollector': 2}|{'pregate': 2}|
|fall|39|0|3|49|55|26|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'first_observed_signature': 25, 'prior_free_RunGarbageCollector': 12, 'prior_free_ResolveOverlap': 1}|{'unarmed': 12}|
|sameU|40|0|3|19|22|17|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'first_observed_signature': 3, 'prior_free_RunGarbageCollector': 4}|{'pregate': 2, 'unarmed': 2}|
|fall|39|1|3|49|20|18|{'first_observed_signature': 5, 'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6}|{}|
|sameU|40|1|3|19|24|21|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 8, 'first_observed_signature': 1}|{'unarmed': 8}|
|fall|43|-1|3|50|50|16|{'first_observed_signature': 32, 'prior_free_RunGarbageCollector': 7, 'prior_free_ResolveDepthOverlap': 6, 'ambiguous_live_signature': 5}|{'unarmed': 5, 'pregate': 2}|
|sameU|44|-1|3|34|34|26|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 6, 'first_observed_signature': 12}|{'unarmed': 5, 'pregate': 1}|
|fall|43|0|3|50|58|22|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'prior_free_RunGarbageCollector': 9, 'first_observed_signature': 32}|{'unarmed': 7, 'pregate': 2}|
|sameU|44|0|3|34|32|25|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'first_observed_signature': 12, 'prior_free_RunGarbageCollector': 4}|{'unarmed': 3, 'pregate': 1}|
|fall|43|1|3|50|18|23|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 2}|{'unarmed': 2}|
|sameU|44|1|3|34|15|16|{'first_observed_signature': 1, 'prior_free_ResolveDepthOverlap': 8, 'ambiguous_live_signature': 6}|{}|
|fall|47|-1|3|51|51|18|{'first_observed_signature': 26, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveDepthOverlap': 7, 'ambiguous_live_signature': 5}|{'unarmed': 12, 'pregate': 1}|
|sameU|48|-1|3|20|20|23|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 4}|{'unarmed': 4}|
|fall|47|0|3|51|38|28|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 7, 'first_observed_signature': 15, 'prior_free_RunGarbageCollector': 6}|{'unarmed': 5, 'pregate': 1}|
|sameU|48|0|3|20|17|24|{'prior_free_ResolveDepthOverlap': 10, 'prior_free_RunGarbageCollector': 1, 'ambiguous_live_signature': 6}|{'unarmed': 1}|
|fall|47|1|3|51|20|20|{'prior_free_ResolveDepthOverlap': 9, 'ambiguous_live_signature': 6, 'first_observed_signature': 5}|{}|
|sameU|48|1|3|20|20|24|{'prior_free_ResolveDepthOverlap': 10, 'ambiguous_live_signature': 6, 'prior_free_RunGarbageCollector': 3, 'prior_free_ResolveOverlap': 1}|{'unarmed': 3}|

## Aggregate fixed first3 windows

fall, shift-1: windows=12, rows=36, img_new=638, event creates=638, classes={'first_observed_signature': 311, 'prior_free_RunGarbageCollector': 181, 'prior_free_ResolveDepthOverlap': 82, 'ambiguous_live_signature': 60, 'prior_free_ResolveOverlap': 4}, candidates={'first_observed_signature': 311, 'prior_free_RunGarbageCollector': 181, 'prior_free_ResolveDepthOverlap': 82, 'ambiguous_live_signature': 60, 'prior_free_ResolveOverlap': 4}, GC prior phases={'unarmed': 164, 'pregate': 17}.

sameU, shift-1: windows=12, rows=36, img_new=236, event creates=236, classes={'prior_free_ResolveDepthOverlap': 110, 'ambiguous_live_signature': 72, 'prior_free_RunGarbageCollector': 30, 'first_observed_signature': 24}, candidates={'prior_free_ResolveDepthOverlap': 110, 'ambiguous_live_signature': 72, 'prior_free_RunGarbageCollector': 30, 'first_observed_signature': 24}, GC prior phases={'unarmed': 25, 'pregate': 5}.

fall, shift0: windows=12, rows=36, img_new=638, event creates=649, classes={'prior_free_ResolveDepthOverlap': 123, 'ambiguous_live_signature': 87, 'first_observed_signature': 273, 'prior_free_RunGarbageCollector': 163, 'prior_free_ResolveOverlap': 3}, candidates={'prior_free_ResolveDepthOverlap': 123, 'ambiguous_live_signature': 87, 'first_observed_signature': 273, 'prior_free_RunGarbageCollector': 163, 'prior_free_ResolveOverlap': 3}, GC prior phases={'unarmed': 150, 'pregate': 13}.

sameU, shift0: windows=12, rows=36, img_new=236, event creates=243, classes={'prior_free_RunGarbageCollector': 38, 'prior_free_ResolveDepthOverlap': 112, 'ambiguous_live_signature': 72, 'first_observed_signature': 21}, candidates={'prior_free_RunGarbageCollector': 38, 'prior_free_ResolveDepthOverlap': 112, 'ambiguous_live_signature': 72, 'first_observed_signature': 21}, GC prior phases={'unarmed': 34, 'pregate': 4}.

fall, shift1: windows=12, rows=36, img_new=638, event creates=250, classes={'first_observed_signature': 40, 'prior_free_ResolveDepthOverlap': 120, 'ambiguous_live_signature': 81, 'prior_free_RunGarbageCollector': 9}, candidates={'first_observed_signature': 40, 'prior_free_ResolveDepthOverlap': 120, 'ambiguous_live_signature': 81, 'prior_free_RunGarbageCollector': 9}, GC prior phases={'unarmed': 9}.

sameU, shift1: windows=12, rows=36, img_new=236, event creates=232, classes={'prior_free_ResolveDepthOverlap': 107, 'ambiguous_live_signature': 72, 'prior_free_RunGarbageCollector': 37, 'first_observed_signature': 14, 'prior_free_ResolveOverlap': 2}, candidates={'prior_free_ResolveDepthOverlap': 107, 'ambiguous_live_signature': 72, 'prior_free_RunGarbageCollector': 37, 'first_observed_signature': 14, 'prior_free_ResolveOverlap': 2}, GC prior phases={'unarmed': 37}.

## Nominal per-index profile (all falls; following same-U controls)

|kind|idx|Nrows|img_new|create events|classes|free reasons|
|---|---|---|---|---|---|---|
|fall|0|12|72|483|{'first_observed_signature': 243, 'prior_free_RunGarbageCollector': 156, 'prior_free_ResolveDepthOverlap': 45, 'ambiguous_live_signature': 36, 'prior_free_ResolveOverlap': 3}|{'RunGarbageCollector': 30, 'ResolveDepthOverlap': 72, 'ResolveOverlap': 25}|
|fall|1|12|482|84|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 22, 'prior_free_RunGarbageCollector': 1}|{'RunGarbageCollector': 26, 'ResolveDepthOverlap': 48, 'ResolveOverlap': 15}|
|fall|2|12|84|82|{'first_observed_signature': 8, 'prior_free_ResolveDepthOverlap': 41, 'ambiguous_live_signature': 27, 'prior_free_RunGarbageCollector': 6}|{'ResolveDepthOverlap': 54, 'ResolveOverlap': 14, 'RunGarbageCollector': 18}|
|fall|3|12|82|84|{'prior_free_ResolveDepthOverlap': 42, 'ambiguous_live_signature': 30, 'prior_free_RunGarbageCollector': 2, 'first_observed_signature': 10}|{'ResolveDepthOverlap': 60, 'ResolveOverlap': 13, 'RunGarbageCollector': 22}|
|fall|4|12|84|90|{'first_observed_signature': 8, 'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 27, 'prior_free_RunGarbageCollector': 16}|{'RunGarbageCollector': 27, 'ResolveOverlap': 13, 'ResolveDepthOverlap': 54}|
|fall|5|12|90|92|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 26, 'prior_free_RunGarbageCollector': 12, 'first_observed_signature': 16}|{'RunGarbageCollector': 15, 'ResolveOverlap': 12, 'ResolveDepthOverlap': 52}|
|fall|6|12|94|86|{'prior_free_ResolveDepthOverlap': 43, 'ambiguous_live_signature': 31, 'prior_free_ResolveOverlap': 1, 'prior_free_RunGarbageCollector': 5, 'first_observed_signature': 6}|{'ResolveOverlap': 14, 'ResolveDepthOverlap': 62, 'RunGarbageCollector': 20}|
|fall|7|12|84|95|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 26, 'first_observed_signature': 18, 'prior_free_RunGarbageCollector': 13}|{'ResolveOverlap': 16, 'RunGarbageCollector': 60, 'ResolveDepthOverlap': 52}|
|fall|8|12|95|90|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 25, 'first_observed_signature': 13, 'prior_free_RunGarbageCollector': 14}|{'ResolveOverlap': 17, 'RunGarbageCollector': 400, 'ResolveDepthOverlap': 50}|
|fall|9|12|90|69|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 6, 'prior_free_RunGarbageCollector': 3}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 49, 'ResolveOverlap': 13}|
|fall|10|12|69|69|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 6, 'prior_free_RunGarbageCollector': 3}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 17}|
|fall|11|12|69|90|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 17, 'prior_free_RunGarbageCollector': 11}|{'ResolveOverlap': 14, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15}|
|fall|12|12|90|79|{'prior_free_ResolveDepthOverlap': 40, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 10, 'first_observed_signature': 5}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 20, 'ResolveOverlap': 16}|
|fall|13|12|79|85|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 26, 'prior_free_RunGarbageCollector': 16, 'first_observed_signature': 5, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 52, 'ResolveOverlap': 14, 'RunGarbageCollector': 14}|
|fall|14|12|85|72|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 22, 'prior_free_RunGarbageCollector': 11, 'first_observed_signature': 6}|{'ResolveDepthOverlap': 44, 'ResolveOverlap': 12, 'RunGarbageCollector': 18}|
|fall|15|12|72|74|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 9, 'prior_free_RunGarbageCollector': 5}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 14}|
|fall|16|12|75|77|{'first_observed_signature': 6, 'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 10}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15, 'ResolveOverlap': 14}|
|fall|17|12|76|81|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 12, 'prior_free_RunGarbageCollector': 8}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 28, 'ResolveOverlap': 15}|
|fall|18|12|81|90|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 15, 'first_observed_signature': 15}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 13, 'ResolveOverlap': 13}|
|fall|19|12|90|71|{'prior_free_ResolveDepthOverlap': 32, 'ambiguous_live_signature': 24, 'first_observed_signature': 10, 'prior_free_RunGarbageCollector': 4, 'prior_free_ResolveOverlap': 1}|{'ResolveOverlap': 8, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 7}|
|fall|20|12|71|75|{'first_observed_signature': 9, 'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 3}|{'RunGarbageCollector': 21, 'ResolveOverlap': 15, 'ResolveDepthOverlap': 48}|
|fall|21|12|75|80|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 14, 'prior_free_RunGarbageCollector': 5}|{'RunGarbageCollector': 20, 'ResolveOverlap': 14, 'ResolveDepthOverlap': 48}|
|fall|22|12|80|87|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 15, 'prior_free_RunGarbageCollector': 9, 'prior_free_ResolveOverlap': 1}|{'ResolveOverlap': 18, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 19}|
|fall|23|12|87|78|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 26, 'first_observed_signature': 15, 'prior_free_RunGarbageCollector': 1}|{'ResolveDepthOverlap': 52, 'RunGarbageCollector': 19, 'ResolveOverlap': 11}|
|fall|24|12|79|66|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 22, 'first_observed_signature': 4, 'prior_free_RunGarbageCollector': 7}|{'ResolveDepthOverlap': 44, 'ResolveOverlap': 12, 'RunGarbageCollector': 10}|
|fall|25|12|65|67|{'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 5, 'prior_free_ResolveOverlap': 1, 'first_observed_signature': 3}|{'RunGarbageCollector': 17, 'ResolveOverlap': 10, 'ResolveDepthOverlap': 48}|
|fall|26|12|67|80|{'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 24, 'first_observed_signature': 8, 'prior_free_RunGarbageCollector': 9}|{'ResolveOverlap': 15, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 22}|
|fall|27|12|80|81|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 12, 'prior_free_RunGarbageCollector': 8}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 19, 'ResolveOverlap': 13}|
|fall|28|12|81|68|{'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'first_observed_signature': 5, 'prior_free_RunGarbageCollector': 4, 'prior_free_ResolveOverlap': 1}|{'ResolveOverlap': 11, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 21}|
|fall|29|12|68|79|{'prior_free_ResolveDepthOverlap': 32, 'ambiguous_live_signature': 24, 'first_observed_signature': 17, 'prior_free_RunGarbageCollector': 6}|{'RunGarbageCollector': 8, 'ResolveOverlap': 8, 'ResolveDepthOverlap': 48}|
|fall|30|12|79|85|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 9, 'prior_free_ResolveOverlap': 1, 'first_observed_signature': 14}|{'ResolveOverlap': 20, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 14}|
|fall|60|12|70|80|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 24, 'first_observed_signature': 9, 'prior_free_RunGarbageCollector': 14}|{'ResolveOverlap': 9, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 6}|
|fall|61|12|80|84|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 13, 'prior_free_RunGarbageCollector': 9, 'prior_free_ResolveOverlap': 1}|{'RunGarbageCollector': 30, 'ResolveOverlap': 15, 'ResolveDepthOverlap': 48}|
|fall|62|12|84|84|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 11, 'first_observed_signature': 13}|{'ResolveOverlap': 13, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 18}|
|fall|63|12|84|80|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 5, 'first_observed_signature': 12, 'prior_free_ResolveOverlap': 2}|{'ResolveOverlap': 15, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15}|
|fall|64|12|80|74|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 8, 'first_observed_signature': 6}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 30, 'ResolveOverlap': 12}|
|fall|65|12|74|71|{'prior_free_RunGarbageCollector': 7, 'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 4}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 12, 'RunGarbageCollector': 23}|
|fall|66|12|71|76|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 9, 'first_observed_signature': 6}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 17, 'ResolveOverlap': 15}|
|fall|67|12|76|79|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 11, 'prior_free_ResolveOverlap': 1, 'prior_free_RunGarbageCollector': 6}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 14, 'ResolveOverlap': 15}|
|fall|68|12|79|69|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 7, 'prior_free_RunGarbageCollector': 2}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15, 'ResolveOverlap': 12}|
|fall|69|12|69|74|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 8, 'first_observed_signature': 9}|{'ResolveOverlap': 9, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 11}|
|fall|70|12|74|87|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 21, 'first_observed_signature': 3, 'prior_free_ResolveOverlap': 1}|{'RunGarbageCollector': 18, 'ResolveOverlap': 16, 'ResolveDepthOverlap': 48}|
|fall|71|12|87|74|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveOverlap': 1, 'first_observed_signature': 3}|{'RunGarbageCollector': 24, 'ResolveOverlap': 9, 'ResolveDepthOverlap': 48}|
|fall|72|12|74|77|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 9, 'prior_free_RunGarbageCollector': 7}|{'ResolveOverlap': 14, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 14}|
|fall|73|12|77|73|{'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 7, 'prior_free_ResolveOverlap': 2, 'first_observed_signature': 1}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 27, 'ResolveOverlap': 15}|
|fall|74|12|73|76|{'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 17, 'first_observed_signature': 1}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 10, 'RunGarbageCollector': 7}|
|fall|75|12|76|83|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 26, 'first_observed_signature': 8, 'prior_free_RunGarbageCollector': 13}|{'ResolveOverlap': 10, 'ResolveDepthOverlap': 52, 'RunGarbageCollector': 10}|
|fall|76|12|83|63|{'prior_free_ResolveDepthOverlap': 32, 'ambiguous_live_signature': 22, 'first_observed_signature': 7, 'prior_free_RunGarbageCollector': 2}|{'ResolveOverlap': 10, 'ResolveDepthOverlap': 44, 'RunGarbageCollector': 13}|
|fall|77|12|64|72|{'first_observed_signature': 4, 'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 7}|{'RunGarbageCollector': 15, 'ResolveOverlap': 13, 'ResolveDepthOverlap': 48}|
|fall|78|12|71|94|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 6, 'prior_free_RunGarbageCollector': 25, 'prior_free_ResolveOverlap': 1}|{'RunGarbageCollector': 15, 'ResolveOverlap': 15, 'ResolveDepthOverlap': 48}|
|fall|79|12|94|84|{'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 24, 'first_observed_signature': 13, 'prior_free_RunGarbageCollector': 8}|{'ResolveOverlap': 19, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 24}|
|fall|80|12|84|69|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 4, 'prior_free_RunGarbageCollector': 5}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 18, 'ResolveOverlap': 12}|
|fall|81|12|69|66|{'first_observed_signature': 3, 'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 5}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 23, 'ResolveOverlap': 10}|
|fall|82|12|66|87|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 13, 'first_observed_signature': 12}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 7, 'ResolveOverlap': 15}|
|fall|83|12|87|75|{'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 9, 'first_observed_signature': 8}|{'ResolveOverlap': 10, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 13}|
|fall|84|12|75|79|{'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 7}|{'ResolveOverlap': 11, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 16}|
|fall|85|12|79|86|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 16, 'first_observed_signature': 10, 'prior_free_ResolveOverlap': 1}|{'RunGarbageCollector': 12, 'ResolveOverlap': 11, 'ResolveDepthOverlap': 48}|
|fall|86|12|87|84|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 13, 'prior_free_RunGarbageCollector': 10}|{'RunGarbageCollector': 9, 'ResolveOverlap': 16, 'ResolveDepthOverlap': 48}|
|fall|87|12|83|76|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 8, 'prior_free_RunGarbageCollector': 9}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 22}|
|fall|88|12|77|80|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 12, 'prior_free_RunGarbageCollector': 8}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 13, 'RunGarbageCollector': 18}|
|sameU|0|12|73|92|{'prior_free_RunGarbageCollector': 14, 'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 16}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 19, 'RunGarbageCollector': 5}|
|sameU|1|12|91|72|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 4, 'prior_free_RunGarbageCollector': 8}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 21, 'ResolveOverlap': 13}|
|sameU|2|12|72|79|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 16, 'first_observed_signature': 1}|{'ResolveOverlap': 14, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 17}|
|sameU|3|12|79|81|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 24, 'first_observed_signature': 9, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveOverlap': 2}|{'RunGarbageCollector': 10, 'ResolveOverlap': 11, 'ResolveDepthOverlap': 48}|
|sameU|4|12|81|79|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 13, 'first_observed_signature': 5}|{'ResolveOverlap': 14, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 17}|
|sameU|5|12|79|74|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 5, 'prior_free_RunGarbageCollector': 7}|{'RunGarbageCollector': 25, 'ResolveOverlap': 15, 'ResolveDepthOverlap': 48}|
|sameU|6|12|74|71|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 8}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 13, 'RunGarbageCollector': 10}|
|sameU|7|12|71|83|{'first_observed_signature': 9, 'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 14, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 19, 'ResolveOverlap': 14}|
|sameU|8|12|83|68|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 7, 'prior_free_RunGarbageCollector': 2}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15, 'ResolveOverlap': 12}|
|sameU|9|12|69|84|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 13, 'prior_free_RunGarbageCollector': 11, 'prior_free_ResolveOverlap': 1}|{'RunGarbageCollector': 23, 'ResolveOverlap': 11, 'ResolveDepthOverlap': 48}|
|sameU|10|12|83|76|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 10, 'first_observed_signature': 5}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 18, 'ResolveOverlap': 14}|
|sameU|11|12|76|79|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 14, 'first_observed_signature': 6}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 18, 'ResolveOverlap': 12}|
|sameU|12|12|79|76|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 8, 'first_observed_signature': 8}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 24, 'ResolveOverlap': 13}|
|sameU|13|12|76|78|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 12, 'prior_free_RunGarbageCollector': 7}|{'ResolveOverlap': 11, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 18}|
|sameU|14|12|78|88|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 15, 'prior_free_RunGarbageCollector': 13}|{'ResolveOverlap': 13, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15}|
|sameU|15|12|88|84|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 5, 'prior_free_RunGarbageCollector': 16, 'prior_free_ResolveOverlap': 1}|{'RunGarbageCollector': 20, 'ResolveOverlap': 15, 'ResolveDepthOverlap': 48}|
|sameU|16|12|84|70|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 8, 'first_observed_signature': 2}|{'RunGarbageCollector': 23, 'ResolveOverlap': 13, 'ResolveDepthOverlap': 48}|
|sameU|17|12|70|81|{'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 24, 'first_observed_signature': 11, 'prior_free_RunGarbageCollector': 7}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 15, 'RunGarbageCollector': 16}|
|sameU|18|12|81|75|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 7, 'first_observed_signature': 9}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 20, 'ResolveOverlap': 12}|
|sameU|19|12|76|68|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 8, 'first_observed_signature': 3}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 9, 'RunGarbageCollector': 9}|
|sameU|20|12|67|85|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 22, 'first_observed_signature': 2}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 16, 'RunGarbageCollector': 13}|
|sameU|21|12|85|81|{'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 12, 'first_observed_signature': 10, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 12, 'RunGarbageCollector': 18}|
|sameU|22|12|81|71|{'prior_free_ResolveDepthOverlap': 37, 'prior_free_RunGarbageCollector': 8, 'ambiguous_live_signature': 24, 'first_observed_signature': 2}|{'RunGarbageCollector': 11, 'ResolveOverlap': 13, 'ResolveDepthOverlap': 48}|
|sameU|23|12|71|65|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 5, 'prior_free_RunGarbageCollector': 1}|{'RunGarbageCollector': 18, 'ResolveOverlap': 11, 'ResolveDepthOverlap': 48}|
|sameU|24|12|65|83|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 7, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 15, 'RunGarbageCollector': 20}|
|sameU|25|12|83|82|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 9, 'prior_free_RunGarbageCollector': 13, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 13, 'ResolveOverlap': 11}|
|sameU|26|12|82|69|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 3, 'prior_free_RunGarbageCollector': 7}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15, 'ResolveOverlap': 11}|
|sameU|27|12|69|83|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 11, 'prior_free_RunGarbageCollector': 13}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 11, 'RunGarbageCollector': 17}|
|sameU|28|12|84|82|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 16, 'first_observed_signature': 5}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 13, 'RunGarbageCollector': 17}|
|sameU|29|12|81|67|{'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 1, 'first_observed_signature': 3}|{'ResolveOverlap': 15, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 19}|
|sameU|30|12|67|69|{'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'first_observed_signature': 4, 'prior_free_RunGarbageCollector': 7}|{'ResolveOverlap': 10, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 13}|
|sameU|60|12|86|81|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 9, 'prior_free_RunGarbageCollector': 12}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 15, 'ResolveOverlap': 12}|
|sameU|61|12|81|65|{'prior_free_RunGarbageCollector': 2, 'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 3}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 25}|
|sameU|62|12|66|77|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 11, 'prior_free_ResolveOverlap': 1, 'first_observed_signature': 5}|{'RunGarbageCollector': 25, 'ResolveOverlap': 12, 'ResolveDepthOverlap': 48}|
|sameU|63|12|76|69|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 4, 'prior_free_RunGarbageCollector': 4}|{'RunGarbageCollector': 11, 'ResolveOverlap': 13, 'ResolveDepthOverlap': 48}|
|sameU|64|12|69|77|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 9, 'first_observed_signature': 6, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 13, 'RunGarbageCollector': 14}|
|sameU|65|12|77|88|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 11, 'prior_free_RunGarbageCollector': 18}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 19, 'ResolveOverlap': 11}|
|sameU|66|12|88|69|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 2, 'first_observed_signature': 7}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 18, 'ResolveOverlap': 13}|
|sameU|67|12|69|77|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 13, 'first_observed_signature': 2, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 13, 'RunGarbageCollector': 15}|
|sameU|68|12|77|87|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 15, 'first_observed_signature': 14, 'prior_free_ResolveOverlap': 1}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 17, 'ResolveOverlap': 11}|
|sameU|69|12|87|80|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 15, 'first_observed_signature': 5}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 14, 'RunGarbageCollector': 23}|
|sameU|70|12|80|64|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 2, 'first_observed_signature': 1}|{'RunGarbageCollector': 17, 'ResolveOverlap': 13, 'ResolveDepthOverlap': 48}|
|sameU|71|12|64|68|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 6}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 12}|
|sameU|72|12|68|108|{'prior_free_ResolveDepthOverlap': 35, 'first_observed_signature': 35, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 14}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 10}|
|sameU|73|12|108|75|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'first_observed_signature': 10, 'prior_free_RunGarbageCollector': 5}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 16}|
|sameU|74|12|75|64|{'prior_free_ResolveDepthOverlap': 39, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 1}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 15, 'RunGarbageCollector': 27}|
|sameU|75|12|64|74|{'prior_free_ResolveDepthOverlap': 33, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 11, 'first_observed_signature': 6}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 10, 'ResolveOverlap': 9}|
|sameU|76|12|74|104|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 31, 'prior_free_ResolveOverlap': 1, 'first_observed_signature': 13}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 11, 'ResolveOverlap': 12}|
|sameU|77|12|105|64|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 2}|{'RunGarbageCollector': 29, 'ResolveOverlap': 14, 'ResolveDepthOverlap': 48}|
|sameU|78|12|63|71|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 6, 'prior_free_RunGarbageCollector': 4}|{'ResolveOverlap': 13, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 31}|
|sameU|79|12|71|76|{'prior_free_ResolveDepthOverlap': 34, 'ambiguous_live_signature': 24, 'first_observed_signature': 5, 'prior_free_RunGarbageCollector': 13}|{'ResolveOverlap': 11, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 6}|
|sameU|80|12|76|90|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 15, 'first_observed_signature': 13, 'prior_free_ResolveOverlap': 1}|{'RunGarbageCollector': 9, 'ResolveOverlap': 14, 'ResolveDepthOverlap': 48}|
|sameU|81|12|90|63|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 2, 'prior_free_RunGarbageCollector': 2}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 11, 'RunGarbageCollector': 41}|
|sameU|82|12|63|71|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 10, 'first_observed_signature': 2}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 11, 'RunGarbageCollector': 23}|
|sameU|83|12|71|93|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 22, 'prior_free_ResolveOverlap': 1, 'first_observed_signature': 10}|{'ResolveDepthOverlap': 48, 'ResolveOverlap': 13, 'RunGarbageCollector': 2}|
|sameU|84|12|93|82|{'prior_free_ResolveDepthOverlap': 35, 'ambiguous_live_signature': 24, 'first_observed_signature': 10, 'prior_free_RunGarbageCollector': 12, 'prior_free_ResolveOverlap': 1}|{'ResolveOverlap': 12, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 10}|
|sameU|85|12|82|65|{'prior_free_ResolveDepthOverlap': 36, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 4, 'first_observed_signature': 1}|{'RunGarbageCollector': 34, 'ResolveOverlap': 12, 'ResolveDepthOverlap': 48}|
|sameU|86|12|65|82|{'prior_free_ResolveDepthOverlap': 37, 'first_observed_signature': 15, 'ambiguous_live_signature': 24, 'prior_free_RunGarbageCollector': 6}|{'ResolveOverlap': 14, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 17}|
|sameU|87|12|82|79|{'prior_free_ResolveDepthOverlap': 38, 'ambiguous_live_signature': 24, 'first_observed_signature': 12, 'prior_free_ResolveOverlap': 2, 'prior_free_RunGarbageCollector': 3}|{'ResolveOverlap': 15, 'ResolveDepthOverlap': 48, 'RunGarbageCollector': 8}|
|sameU|88|12|79|78|{'prior_free_ResolveDepthOverlap': 37, 'ambiguous_live_signature': 24, 'first_observed_signature': 7, 'prior_free_RunGarbageCollector': 10}|{'ResolveDepthOverlap': 48, 'RunGarbageCollector': 23, 'ResolveOverlap': 13}|