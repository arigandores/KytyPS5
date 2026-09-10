# Session 43 â€” sand footprints, sparse MRT attachments and CPU SRT cost

Date: 2026-09-10. Base: `merge-upstream` at `162915a`.
Renderer fixes, normal video review, integration validation and seed restoration are complete.

## Result

Walking footprints and the lighting of sliding grooves are restored. The renderer compacted
active guest render targets while fragment shaders kept their original output locations.
A normal-only sand decal targeting MRT2 therefore received MRT0's color output. Keeping the
guest attachment indices fixes the normal-map contribution. The fix is generic; no title ID,
game addresses or skipped effects are used in the rendering path.

Two CPU improvements share identical pure SRT calculations and retain temporary descriptor
arrays that were previously freed after every materialization. SRT time decreased modestly in
the measured pair, but a meaningful overall FPS improvement is **not established**. The heavy
continuous interval was 39.08 versus 39.36 fps; stable 60 fps with many trails is not achieved.

## Footprint investigation and implementation

The defect is present in the user's session-40 capture, before the latest upstream merge:
`_RenderDoc/kyty_1789053375456011_capture.rdc`.

- Texture `ResourceId::600389` matches `ground_sand_run_02_n.gnfp`: 19 of 24 selected
  nontrivial BC blocks match the asset. The captured pass uses PS `9efa7951e382fce0` and
  VS `db84242a5168ab54`, identified by exact SPIR-V matches against the saved cache.
- The shader exports MRT0 through MRT4. Its normal contribution is MRT2; the actual
  normal attachment was at Vulkan slot 0 because lower guest targets were disabled.
- EID 3001 changes 690 pixels with the original mapping. Replaying with MRT2 routed to
  the attachment changes 691 pixels and perturbs the normal direction. The original output
  mostly scales the existing normal, which does not produce the intended footprint relief.
  EID 2939 is offscreen and changes no pixels under either mapping; it is not evidence of
  a missing draw. `rd_foot_scan.txt` and raw before/after buffers retain these experiments.
- `AcquireRenderTargets` places each attachment at `target_slot`; lower unused slots remain
  null. The pipeline's format, mask and blend arrays use the same indices. Dynamic color-write
  enables also cover the full range through the highest active slot.

This follows Vulkan's null-attachment/output-location rules and matching undefined pipeline
formats ([render-pass specification](https://docs.vulkan.org/spec/latest/chapters/renderpass.html),
[pipeline rendering formats](https://docs.vulkan.org/refpages/latest/refpages/source/VkPipelineRenderingCreateInfo.html)).

Picture checks use recordings, not direct screenshots. Extracted video frames show footprints
behind Astro at the rocks and on the return walk; the grooves now retain their sand lighting
instead of the earlier dark strips. Useful clips, left original / right fixed:

- `C:/kyty/s43/footprints_near_rocks_before_after.mp4` â€” 13 seconds.
- `C:/kyty/s43/footsteps_before_after.mp4` â€” 29 seconds of ordinary movement.

## CPU implementation and measurements

`KYTY_SRT_COMMON_VALUES=0` disables sharing of pure compiled SRT nodes. Equality includes all
semantic node fields and operand indices. Memory reads and PhiAgree are excluded; memory
contents and failures are evaluated on every call. Optional `KYTY_SRT_PLAN_STATS` logs static
plan sizes. The heavy sand PS `7a46be05e11e081b` has 343 nodes after sharing 8 calculations,
131 reads and 116 flat slots. Other large plans still perform hundreds of scalar reads.

`KYTY_SRT_MATERIAL_SCRATCH=0` disables retained caller arrays in resource materialization.
The compiled evaluator swaps its scratch vectors into caller outputs. Previously those
outputs were fresh locals and were destroyed immediately, defeating part of the earlier
scratch reuse. Descriptor and active-source arrays now survive to the next call; all entries
are re-evaluated. Returned snapshots still own their data, and failure remains transactional.

Final A/B uses the **same executable**, with the MRT fix enabled in both parts. `control_off`
sets both new CPU switches to 0; `warm_on` uses defaults. Both use warmed catalogues, identical
present-based inputs and recording, with GPU clock sampling through `run_ab.sh`.

| Present interval | CPU switches off, fps | CPU switches on, fps |
| --- | ---: | ---: |
| 15200â€“15800 | 43.17 | 42.85 |
| 16000â€“16600 | 40.64 | 40.54 |
| 16800â€“17400 | 41.48 | 40.13 |
| 17600â€“18200 | 37.50 | 41.24 |
| 18400â€“19000 | 39.99 | 36.68 |
| Continuous 15200â€“19000 | 39.08 | 39.36 |

Across the five equal-sized W windows, SRT averaged **5.504 -> 5.369 ms** (about 2.4% less),
with 1362 -> 1367 draws per present. SRT cost per draw was 4.041 -> 3.927 microseconds.
Total GPU-thread CPU time was 24.09 -> 24.20 ms and GPU time 7.25 -> 7.25 ms. Other CPU phases,
small route differences and frequency/temperature variation offset the small SRT saving;
do not advertise this as an established overall FPS improvement.

In the continuous heavy interval, p99 was 46.98 -> 39.78 ms, worst 60-present window
27.68 -> 29.55 fps, and max draw count 2868 -> 3086. Neither part had intervals over 100 ms
there. These are the observed pair's statistics, not a guarantee that long stalls are gone.
The additional separated W route measured 38.79 -> 40.41 fps, but its draw count and position
also differ, so its whole FPS difference is not attributed to the CPU changes.

Earlier `base`, `cse_cold` and `sparse_material_cold` runs are exploratory controls. Their
temperature, cache warmth and positions differ. Builds began only after their main measurement
windows. A short video extraction near present 13263 in `sparse_material_cold` excludes that
early window from strict comparison. All final repeated-W windows were free of those jobs.

`profile_*.json`, `compare_control_off_warm_on.json`, GPU-clock CSVs and logs retain the data.

## Routes and video review

The original route covers intro, controller shake, movement/jumps, the slope, five W holds
through present 19000, and K at 19500. Added ordinary walking:
`@20000:s/@480,@20600:a/@240,@21000:d/@480,@21600:w/@240`.

Two additional series attempt distinct overlapping grooves: five W220 holds at 22500, 22800,
23100, 23400 and 23700 with lateral movement; then five W100 holds at 24500, 24640, 24780,
24920 and 25060 with lateral movement. Multiple grooves and the heavy CPU case are reproduced.
Contact sheets show overlapping/fading tracks, but **five simultaneously distinct persistent
grooves are not established**. Do not claim an exact reproduction of the user's 4â€“5-track case.

| Reviewed recording | Frames | One-frame candidates | Decode errors |
| --- | ---: | ---: | ---: |
| `rec_base_review.mp4` | 23037 | 0 | 0 |
| `rec_sparse_material_cold_review.mp4` | 23657 | 0 | 0 |
| `rec_control_off_review.mp4` | 24725 | 0 | 0 |
| `rec_warm_on_review.mp4` | 27573 | 0 | 0 |

Review copies omit about 600 final frames around forced termination. The final `warm_on`
copy includes both added five-attempt series in full. The cold fixed run and `control_off`
have shorter review tails; do not extend their review claims to the omitted last attempts.
Representative intro/gameplay contact sheets were inspected. No guest object/batch assertion
or device loss was observed in these normal runs. The earlier session-42 assertion's cause
is still unknown.

## Tests

- 116 shader CFG tests pass with `KYTY_SRT_VERIFY=1`; no SrtVerify mismatches.
- ResourceMaterialization passes with verification, both CPU changes disabled, and the
  interpreter path. The added regression covers shared expressions, U32 wrap, changed runtime
  values and preservation of separate memory reads. Existing cases cover snapshot ownership
  and failed materialization preserving the prior stage.
- New `--sparse-mrt-only` readback cases use isolated MRT2 and MRT7 with a different MRT0
  output, null lower slots, polygon-mode/cache variants and provoking-vertex changes. They
  pass normal execution and synchronization validation.
- Read-only depth reuse, image-view cache, packed textures and polygon mode additionally pass
  synchronization validation after the final source changes.
- The synchronous GPU harness needs `KYTY_ASYNC_PIPELINES=0`. Initial validation exposed
  missing `independentBlend` in the **test harness**; production already enables/requires it.
  The harness now matches production. `test_sparse_sync.log` retains the initial errors;
  `test_sparse_sync_fixed.log` is the corrected passing run.
- Unused fragment-output warnings are expected in the sparse tests' deliberately unbound MRT0.
  They are warnings, not a claim of no validation messages. Final focused logs have no
  Validation Error, VUID or synchronization hazard.
- The broad GPU/filesystem suites are not declared clean. Previously documented failures
  were not part of this task and are not claimed fixed.

## Startup seed and integration validation

Candidate/exported seed: **385 shaders / 437 recipes**, source signature
`1693ffd701dec904641a016e8b5c0ad75c26eef6`. This is the current route's compatible catalogue,
not a claim of superset coverage of every earlier incompatible seed.

The previous installed seed and local catalogue were archived under
`seed_previous_installed` and `cache_before_seed_restore`. Manifest lengths and SHA256 values
were checked before installation. With no local title directory, automatic restoration
installed 385 shaders and prepared **437/437, 0 skipped** (340 graphics + 97 compute).
Preparation took **20.692 s total / 10.600 s additional startup wait** under ordinary Vulkan
validation. The game route continues from this same restored catalogue.
The local catalogue still contains 437 recipes after this run, matching the installed seed.

Ordinary Vulkan validation completed **23867 presents / 1829.816 seconds**
from the first recorded present, with **0 validation errors** and no VUID or synchronization-hazard
messages. The Khronos validation DLL was confirmed loaded (`validation_layer.json`); no message
filters were used. The log contains 10 warnings about unused
fragment outputs (Location 1). This is not a claim of zero warnings or full-route synchronization
validation; synchronization validation was run separately on the focused GPU tests above.

The restored-seed run covers the intro, transition to control, slope, all five original W holds,
K and ordinary walking through the action ending at present 21840. The two additional short
five-attempt series were tested in normal execution and are excluded from this validation route.
The run ended by normal window close before the 2400-second fallback timeout. The first
automatic-close helper used its script-initialization time as an ownership bound and did not
select the emulator, which had started slightly earlier. The emulator was closed explicitly
by its verified owned PID (`close_validate_manual.log`); the helper now uses its process
creation time. This did not truncate the required route.

Reviewed validation recording: **23269 frames, 0 one-frame
candidates**, decoder exit 0 and no decode errors (`video_restore_validate/report.json`).
Like the other review copies, it omits about 600 final frames. The whole basic gameplay route
remains included. Video frame 13000 was additionally inspected to confirm the restored
catalogue renders the footprint trail at the rocks.

No guest object/batch assertion or device loss was observed. No speed comparison uses this
validation run: validation substantially increases CPU cost.

## Installed binary and remaining work

Installed executable SHA256:
`D9FE630FAE4257E226A2B03B0D4D2A1DA312D2487A198D05CD1B4A36BB0EF2A4`.
The executable's code matches the reviewed source; its build label predates the final commit.

User clarification, 2026-09-10: FPS drops with sand trails have already been reproduced
many times. The uncertainty about exactly 4-5 visually distinct grooves is only a limit
of the visual count, not a missing reproduction of the performance problem. Do not make
another reproduction or an exact groove count a prerequisite for optimization.

Next: profile and reduce CPU cost on the existing heavy route, focusing on SRT /
EvaluateCompiled, resource bindings and thousands of draws. Compare before/after on
the same route and present windows, with video. The general durable guest replay
catalogue remains a separate task. No stable 60-fps claim is made.
The session-42 object/batch assertion remains unexplained. Unrelated PNG deletions inside
`3rdparty/nlohmann_json` are untouched and excluded from the task commit. No push is authorized.
Final stdout contains ReadFile error codes 998 and 1784; both codes also occur in the saved
unmodified `base` run (`io_tail_audit.json`). These I/O messages were not investigated or claimed
fixed, and are not Vulkan validation errors.
