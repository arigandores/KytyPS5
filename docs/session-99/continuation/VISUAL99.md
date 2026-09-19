# Session 99 visual check — bf99e versus no-floor control

The user reported many glitches, flashes and stalls in rec_bf99e.mp4. This is a real
limitation of that experimental recording; its CPU comparison was already rejected by
the sealed work check (-0.710639306%, limit abs<0.5%). No B is taken from bf99e.

## Control fixed before new data

Sealed pred/05_observer_separation.md: 8583 bytes, SHA256
fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0.
vis99base uses the same34206... binary, recording and fixed environment, but bindfloor=0
in BOTH label arms. One process, hold900.3s, no warmup; GPU released after normal completion.
The user independently reported after this run: "глитчей не видел при прогоне".

## Parent inspection (not an exhaustive proof)

visual_keyframes99.py selects exact decoded frame numbers from each .mp4.idx at fixed
wall times50/250/450/825/900s. Mapping is in video99_comparison/manifest.json. Independent
processes are not pixel-identical or guaranteed to have identical guest animation phases.

| recording | wall seconds | decoded frame | observation |
|---|---:|---:|---|
| bf99e |449.998|8868|large foreground birds and blue/white light effects|
| bf99e |824.998|16251|bright streaks/light effects across scene|
| bf99e |899.998|17697|large foreground birds/effects still present|
| vis99base |449.981|8701|idle scene, no corresponding conspicuous effects|
| vis99base |825.014|15999|idle scene, no corresponding conspicuous effects|
| vis99base |900.014|17459|idle scene, no corresponding conspicuous effects|

The no-floor control does not reproduce those late effects in these inspected frames.
This is evidence against them being inevitable in the ordinary recorded idle scene; it
does not identify the exact shader/state mechanism, prove every frame correct, or show a
new rendering fix. Early scene-entry UI is a different visual region and is not licensed
by these late-scene observations. Sleeping/prone Astro is an ordinary idle pose.

## Mechanisms, not established attribution

Source inspection rejects the simple claim that GDS shader atomics remain real: floor
descriptors null GDS too (descriptors.cpp:3611). However PM4 GDS DMA/export bypasses the
descriptor floor, BDA page-table/fault bindings remain real (descriptors.cpp:3600), and
mode2 intentionally preserves real compute-clear shortcuts. These can create partial
GPU-state updates. None has yet been measured as the cause of the observed bf99e effects.
No graphics-correctness optimisation is being shipped from this destructive CPU diagnostic.

Full streaming detector completed normally: vis99base17802 decoded frames/0 events versus
bf99e18037 frames/185 events with the same threshold4 and memory-bounded s32 algorithm.
Of bf99e's185 events,174 map to armed rows and11 to base rows. Independent raw audit finds
178/178 control GateArm records bindfloor=0 and17793/17793 main rows with inactive floor
counters. See verify99_visual_raw/VERIFY.md and video99_base_full/report.json.
Together with parent inspection and the user's live observation this supports non-reproduction
of the reported late artifacts in the no-floor control. It does not prove universal renderer
correctness or identify which partial GPU update causes the experimental-floor artifacts.
Do not interpret detector counts as an exhaustive count of rendering defects.
