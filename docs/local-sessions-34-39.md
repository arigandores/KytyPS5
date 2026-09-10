# Local sessions 34–39: shader preparation, controls and desert CPU work

This change records the validated local work accumulated on top of 03b9643.
It prepares known shader pipelines before guest execution, adds a compatible startup
catalogue exporter and shader inventory tools, and pretranslates registered compute
shaders in a bounded background worker with exact key/code matching and isolated failures.

Presentation retains CPU-copy host-signal completion before signaling present semaphores
and separate acquire-semaphore retirement ticks. Removing the prepared-frame wait did not
improve performance and is not included. SRT page-pointer caching and reusable binding
arrays reduce repeated CPU work. BDA preparation now scans CPU-modified ranges within
registered buffer bounds; KYTY_BDA_DIRTY_RANGES=0 restores the former complete scan.

Keyboard motion supplies shake on R and tilt on Z/X; R passes the initial desert prompt.
Color depth comparisons use the shader path, null native comparisons bind a D32 view,
and shared samplers preserve the comparison operation when falling back to shader comparison.

Validation of the recorded source state:

- 116 shader CFG tests pass. MemoryTracker and ResourceMaterialization tests pass.
- Focused BDA GPU readback tests pass on the old path, the new path and its enabled default.
  NullComparisonBindings, SchedulerTimeline, GraphicsPushConstantStages and UnifiedImageViewCache pass.
- A 600-second ordinary Vulkan validation run, without message filters, reaches present 9905
  in the intro with no Vulkan errors. Gameplay after the control prompt and a separate
  synchronization-validation pass are not covered by this result.
- The final reviewed recording contains 18,809 frames with no detected one-frame glitches
  and no decoding errors.
- The locally installed catalogue contains 380 shaders / 438 recipes. With the local cache
  moved aside, prepare-cold restores the seed and prepares 438/438 recipes without skips:
  20.482 seconds overall, 13.444 seconds additional startup waiting. Generated catalogues,
  emulator binaries, game files and recordings are not stored in this source commit.

The last comparison measures BDA preparation at about 34 versus 15 microseconds per call.
Final heavy desert windows run at 35–36 fps, with p99 around 68 ms; stable 60 fps is not achieved.
Player positions and draw counts differ between scripted routes, so the entire fps difference
cannot be attributed to BDA. The final traced intro measures 59.09 fps / p99 32.47 ms;
elimination of intro microstutters is not demonstrated. The 64 MiB deferred-mip budget is retained.

Known GPU-suite failures remain: partial-page readback values, over-wide fixed storage mip
views, and ComparisonDepthTexture's D16 native-Dref expectation. The latter also fails with
the original ResourceMaterialization.cpp from 03b9643. The full GPU suite is not claimed clean.
The test harness now drains deferred image destruction before destroying its allocator/device.

The route covers initial desert movement, jumping and attacks; cable extraction and a subsequent
level are not confirmed. Next work is a more repeatable heavy view, the remaining BDA/SRT CPU
cost, and gameplay coverage beyond the cable.
