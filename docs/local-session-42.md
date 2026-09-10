# Session 42 — merge upstream through 2e315a3

Date: 2026-09-10. User requested publishing accumulated work first, then integrating the
11 missing upstream commits while preserving the fork's improvements.

## Publication and merge

- Initial push: `fork/main` fast-forwarded from `57fc80b` to `6e2c892`; all five previously
  unpublished commits are on GitHub. No force push.
- Local recovery branch: `backup/pre-upstream-s42-6e2c892`.
- Merge parents: `6e2c892` and upstream `2e315a3`; common ancestor `0b4e78c`.
- Unrelated deletions of five PNG files in `3rdparty/nlohmann_json` remain untouched.

## Upstream changes and conflict decisions

All 11 commits are integrated:

| Commit | Change |
| --- | --- |
| 20ea54c | JSON value copy constructor ABI |
| ae573f9 | Shared vertex format mapping, packed floating-point colors |
| 3902b42 | Shared direct/conditional branch classification |
| c913951 | RDNA2 subvector loop mask and branch semantics |
| c354657 | S_WQM_B32 implementation |
| fe6f496 | Supported OpenType CFF font faces |
| 635fb88 | Configured language for PS5 system parameter 400 |
| a305a6c | Shared packed texture/render-target channel layouts |
| 23e7df2 | Texture upload and component mapping refactor |
| d2fa865 | Shared directory stream for read, seek and enumeration |
| 2e315a3 | Gapless control data before codec initialization |

Five conflicted files were resolved by combining behavior:

- `descriptors.cpp`: upstream `SurfaceFormatInfo::host_to_storage` swizzle composition plus
  our T# MIN_LOD and image-view-min-LOD fallback. The fork's BDA/SRT, comparison-depth and
  sampled read-only depth handling are retained.
- `Control.cpp`, `Scalar.cpp`, `Translator.h`: upstream unified WQM and raw 32-bit writes
  preserve the other EXEC/VCC half and invalidate overlapping SGPR-pair provenance. Retained
  the fork's initial pixel EXEC folding, which prevents ASTRO video miscompilation. A narrow
  WQM may fold the whole invocation predicate only in wave32; wide WQM can fold both wave sizes.
  Upstream subvector loop translation and branch conditions are integrated.
- `ShaderRecompilerComputeTests.cpp`: retain both controller-motion and packed-texture selectors,
  all fork tests and upstream wave32/wave64 WQM/subvector tests.

Automatically merged frontend/CFG, SPIR-V branch logic, texture upload, vertex format mapping,
file-system and library changes were reviewed. `ValueOpcodes.inc` is unchanged, preserving IR
opcode numbering. Existing fork changes outside the upstream change set remain unchanged.

Windows portability fix: the newly included SDL header in `KernelFileSystemTests.cpp` renamed
`main` and caused an undefined-main link failure. Added `SDL_MAIN_HANDLED`. Added an explicit
`--filesystem-only` selector to exercise the directory/seek changes independently of the
existing socket test; default execution still runs that socket test.

## Build and tests

- Release emulator build and installation into `C:/kyty/build/install`: passed.
- Test targets `shader_cfg_tests`, `shader_recompiler_compute_tests`,
  `kernel_file_system_tests`: built after the SDL entry-point fix.
- Shader CFG: **116 tests, exit 0**.
- `--wave64-only`: passed, including subvector loops and WQM B32 in wave32/wave64,
  B64 partial masks and SCC, existing scalar provenance and wave tests.
- `--packed-texture-only`: passed.
- `--gpu-tiler-only`: passed, **330 cases / 236 format-mode pairs**.
- `--image-view-cache-only`, `--readonly-depth-reuse-only`, `--null-comparison-only`,
  `--bda-dirty-only`, `--scheduler-only`, `--controller-motion-only`: passed.
- Packed textures, BDA and read-only depth additionally passed with the Khronos validation
  layer and `VK_VALIDATION_VALIDATE_SYNC=1`; loader logs confirm the layer was loaded.
  No Validation Error, VUID or synchronization hazard was emitted in these focused runs.
- `kernel_file_system_tests --filesystem-only`: passed (directory read/seek/enumeration,
  overflow/invalid offsets, APR paths, save replacement).
- Full `kernel_file_system_tests`: fails in socket `PEEK|WAITALL` on Windows after the
  file-system checks. Both the socket test body and `src/libs/network.cpp` are unchanged
  by this merge. This is not reported as a clean full suite.
- `--storage-mip-host-only`: fails at the over-wide fixed storage mip assertion; the same
  failure reproduced using the saved pre-merge compute test executable. No new regression
  established for this check. The broad GPU suite is not reported clean.

Logs and saved pre-merge executables/cache/seed are in `C:/kyty/s42`.

## Runtime verification

The first cold run shared the GPU with No Man's Sky (about 15 GB of 16 GB VRAM occupied).
It reached present 6677 / 335.265 seconds in the recording index, then the guest asserted:
`command_buffer_writer.ppr.cpp:31: There are too many objects/batches in this scene.`
Fault PC `0x9004a020e`, thread `Draw Shadow`, intentional guest `int 0x42`.
Eight `ReadFile error=1784` messages preceded it, but these messages also occur in successful
session-40 logs; they do not establish the cause of this assertion. No causal attribution to
the merge or the competing game is made from this run alone. Performance is not comparable
to the previous sessions under that competing GPU load.

The first reviewed video segment contains 6081 frames, no detector candidates and no decode
errors. This does not make the crashed run successful. Video-derived contact sheets were also
inspected; the reviewed menu/intro textures and lighting showed no obvious persistent defect.

The user closed No Man's Sky. The second recorded run completed its 470-second timeout
(exit 124, deliberate stop), with **25190 presents / 466.083 seconds from the first recorded
present**. No guest assertion, fatal error or device loss was found. It passed intro, shake,
movement/jumps, the slope, five additional W holds through present 19000 and K at 19500.
The first assertion did not reproduce. This is one successful repeat; concurrent load and
cache warmth changed together, so its root cause remains unproven.

Startup prepared 312/312 collected recipes, 0 skipped, 144 ms total / 32 ms additional wait.
The repeat still translated 89 newly encountered shaders after that partially warm start.
The repeated-W windows were 43.32, 41.57, 40.09, 41.53 and 40.36 fps; GPU time was about
6.6–8.2 ms and CPU GPU-thread time about 22–24.5 ms on average in those windows. This preserves
the known CPU-limited sand behavior; it is not a controlled before/after performance experiment
or a claim of stable 60 fps. Detailed profiles are in `profile_s42_merged_warm.json`.

Video-derived contact sheets cover intro, the transition to control, sand and repeated trails.
Reviewed video: **24593 frames, 0 one-frame detector candidates, decode exit 0, no decode
errors** (`rec_merged_warm_review.mp4`, `video_merged_warm/report.json`). As in prior sessions,
the review copy omits approximately the final 600 recorded frames around forced shutdown;
the full scripted gameplay route and final K action are included in the reviewed portion.

## Refreshed seed and installed binary

- The old 383/447 seed and local cache were backed up before launching the merged code.
  Its translator signature is incompatible and was correctly ignored, not bypassed.
- Exported and installed the new **372-shader / 432-recipe** seed from the completed route.
  This is the newly collected route's catalogue, not a claim that it is a superset of the old
  447-recipe coverage. Both previous seeds/caches and the new candidate are retained in `s42`.
- Verified manifest SHA256 and file lengths before installation. Archived the active local
  catalogue, then started with no local title directory in `prepare-cold` mode.
- Automatic restoration: `ShaderSeed: installed (372 shaders)`; **432/432 prepared, 0 skipped**,
  335 graphics + 97 compute. **21638 ms total / 11876 ms additional startup wait**.
- The restoration/startup/menu run lasted 90 seconds with ordinary Vulkan validation enabled,
  no filters, **no validation errors or VUIDs**. It is not a full-route Vulkan validation run;
  full gameplay above used normal execution. Focused synchronization validation is listed above.
- Installed executable SHA256:
  `0FDD0861F22AC19257140C69C015CD750FCCED380A8C845B0CEAF7C30455E246`.
  Embedded build label remains `6e2c892-dirty`; no rebuild solely to change that label.
- Shader source signature: `2a74ab635c7f718cb351487e16dd81afa3a0e769`.

The general guest replay catalogue remains a separate planned task. CPU cost with many sand
draws and the unreproduced assertion under competing load remain recorded limitations.
