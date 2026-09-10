# Shader preparation and cold-run tests

Before executing a game, Kyty waits for its known graphics and compute pipeline recipes to
finish compiling. A responsive **Preparing shaders** screen shows progress; closing the window
cancels launch. Compilation starts during graphics initialization, overlapping normal loading.
The driver cache is saved before guest execution without destroying the live Vulkan cache.
Preparation frames do not advance scripted input or the guest video recorder's present count.

This mechanism applies to all titles. It prepares only known recipes. With no catalogue, the
game starts normally and records newly encountered shaders/pipelines for subsequent launches.
It cannot predict every unseen shader specialization, or eliminate texture streaming and heavy
rendering costs. Progress counts processed recipes; skipped/incompatible entries are logged.

Manual per-scene analysis is a regression-testing procedure, not a requirement for using this
feature. Ordinary play records recipes automatically for all titles. The next architectural
step is a durable guest replay catalogue that can rebuild known coverage after translator
updates; see [the all-title startup design](shader-startup-design.md) for the current limitations,
implementation sequence and acceptance checks. That replay format is not implemented yet.

## Startup catalogues

An optional `_ShaderSeeds/<TITLE_ID>/` directory supplies a catalogue for a first launch without
a local translation cache. Its contents are the matching shader translation files,
`pipelines.bin`, and `compatibility.txt`. Export one after a verified run:

```powershell
python tools/shader_seed.py --cache _ShaderCache/PPSA21564 --log _kyty.txt --output _ShaderSeeds/PPSA21564
```

The exporter rejects missing referenced shader sources, truncated recipes, mixed profiles and
existing output directories. It also writes `manifest.json` with file sizes and SHA-256 hashes.
Copy the entire directory when distributing a catalogue; recipes reference permutation indices
inside its matching translation files. Catalogues are generated artifacts, not source files.

At startup, Kyty checks the title, game version, translator signature/options, recipe structure
sizes and GPU vendor/device ID. Shader payloads also have checksums. Currently a seed is accepted
only for the GPU model used to generate it; cross-GPU portability is not assumed. Drivers compile
the supplied SPIR-V locally. An incompatible seed is ignored, and ordinary runtime compilation
continues. Updating the driver does not itself invalidate the seed, but can invalidate the local
driver cache.

The seed bootstraps a missing/stale recipe cache; an already compatible local catalogue wins.
Installation replaces matching translation files as a set and publishes recipes last, so the
permutation indices stay aligned. Local files are then free to grow during play. New catalogues
do not silently merge into an existing compatible recipe set. The ASTRO BOT catalogue provided
with this local installation covers the verified intro and initial desert gameplay (movement, jumps and attacks), not the whole game.

Local verification after session 39 (2026-09-10): the installed ASTRO BOT seed contains
380 shaders / 438 recipes. With the local translation catalogue moved aside, `prepare-cold`
restored all 380 sources and prepared 438/438 recipes (341 graphics + 97 compute), with zero
skips. Preparation took 20.482 seconds overall, including 13.444 seconds of additional startup
waiting. This tests catalogue restoration and fresh salted driver compilation, not cold gameplay fps.
The verified final recording contains 18,809 frames with no detected one-frame glitches or decode
errors. Coverage includes the initial desert and attacks; extraction of the cable or reaching a
subsequent level was not established. Heavy gameplay remains around 35–36 fps in the recorded
angles despite cheaper BDA preparation. See workspace HANDOFF §2.45 and `C:/kyty/s39/REPORT.md`.

Session 41 verified and installed the refreshed seed: **383 shaders / 447 recipes**.
With the local catalogue moved aside, `prepare-cold` restored the seed and prepared 447/447
pipelines (350 graphics + 97 compute), zero skipped, before guest execution. Preparation took
22.285 seconds overall and 10.448 seconds of additional startup waiting, with ordinary Vulkan
validation enabled. The subsequent gameplay route reached present 21066 without Vulkan
errors. The 20469-frame recording decodes cleanly, with one observed A-B-A animation
episode at menu frame 543 whose cause remains unresolved; no other detector candidates appeared.
A short ordinary menu control rendered at 60 fps; its 3081 reviewed frames had no
detector candidates or decode errors. That warm launch automatically prepared the grown local
catalogue, 448/448 recipes with zero skips, in 164 ms overall / 36 ms additional waiting.
This is bounded intro/desert coverage, not the whole game or cross-GPU portability. See
[session 41](local-session-41.md) and the [all-title startup design](shader-startup-design.md).

Driver caches use a versioned wrapper plus vendor ID, device ID, driver version and pipeline
cache UUID. They no longer expire just because the emulator's git revision changed. The Vulkan
driver matches the actual shader/pipeline keys inside its opaque cache. The wrapper format
change invalidates the previous `KytyPC1` file once.

## Diagnostic switches

All switches are process-local environment variables. Defaults prepare known shaders and use
compatible caches.

| Variable | Effect |
| --- | --- |
| `KYTY_CACHE_MODE=cold` | Ignore translation and driver caches and starter seeds; salt all guest shader modules with a fresh value on every launch. Does not write either normal cache. |
| `KYTY_CACHE_MODE=prepare-cold` | Retain translation/seed catalogues, ignore the driver cache and compile fresh salted modules before guest execution. Measures preparation for a first user launch; does not save driver results. |
| `KYTY_SHADER_PREPARE=0` | Skip the startup wait/screen; the existing background precache still runs. |
| `KYTY_PIPELINE_PRECACHE=0` | Disable recipe precache and recording. |
| `KYTY_SHADER_SEED=0` | Disable starter catalogue installation. |
| `KYTY_SHADER_SEED_PATH=<root>` | Read starter catalogues from `<root>/<TITLE_ID>`. |
| `KYTY_SHADER_CACHE=0` | Ignore and do not write shader translations; also disables recipe precache and seeds. |
| `KYTY_PIPELINE_CACHE=0` | Ignore and do not write Kyty's Vulkan driver cache. Does not alone defeat the driver's internal disk cache. |
| `KYTY_PIPELINE_SALT=<tag>` | Salt modules at Vulkan creation, including cached SPIR-V. Saved translations remain unchanged. Driver files use a separate hash-of-tag filename; repeat the tag for a warm comparison. |
| `KYTY_SHADER_REGISTER_TRACE=1` | Log AGC shader registration and the first program lookup per stage/hash, with monotonic host timestamps. Independent of background translation. |
| `KYTY_CS_PRETRANSLATE=0` | Disable resource-independent compute translation at AGC registration. Enabled by default in builds with C++ exception unwinding, including the local clang-cl build. Does not disable seed preparation or PM4 pipeline lookahead. |

The combined `KYTY_CACHE_MODE` switches generate their own salt. `KYTY_SPV_SALT` is the older
translator-only switch; it does not affect modules loaded directly from translation caches.
Salting changes debug names without shader semantics and produces fresh compilation on the
tested NVIDIA driver; other drivers may normalize debug information, so verify actual timings
before calling such a run cold. Cold mode does not flush OS file caches or texture residency.

Example using the local project runner:

```bash
KYTY_CACHE_MODE=cold KYTY_REC=C:/kyty/s34/cold.mp4 bash /c/kyty/run_ab.sh cold 255
KYTY_CACHE_MODE=prepare-cold KYTY_REC=C:/kyty/s34/prepared.mp4 bash /c/kyty/run_ab.sh prepared 255
```

`ShaderPreparation: ready` must precede `Execute: Main`, and its completed/total/skipped counts
describe catalogue coverage. `PipelinePrecache: all pipelines created` measures total preparation
time; `startup wait finished` measures the extra wait after ordinary initialization. Distinguish
`AvTrace: pipeline ... precache` from pipeline compilation during play when analyzing freezes.

Exporter checks: `python tests/shaderSeedTests.py`.

## Discovering shaders before first use

`AgcCreateShader` exposes shader code, its size/hash and shader register tables before drawing.
With registration tracing enabled, `ShaderRegister` records that event; `ShaderFirstUse` records
the first program-cache lookup, before translation/loading. These are CPU timing points, not
GPU execution timestamps. The hook works for games using this AGC entry point, without title IDs
or ASTRO BOT addresses in the emulator. Games using another creation path may need another hook.

Analyze a trace and optionally inspect an already available flat ELF64:

```powershell
python tools/shader_inventory.py --log _kyty.txt --elf C:/kyty/eboot.elf --output inventory.json
python tests/shaderInventoryTests.py
```

The ELF scanner searches version-0x18 AGC header candidates, validates segment bounds and relative
register-table pointers, and reports metadata. It does not unpack SELF files, decompress shader
payloads, prove that candidates are unique shaders, or create a compilable pipeline catalogue.
It only reads its inputs and refuses to replace an existing report. The log analyzer streams large
logs, handles out-of-order timestamps, and reports unmatched hashes separately. Mesh shaders can
combine multiple registered shaders, so unmatched hashes do not establish that code is unused.

ASTRO BOT measurement (session 35, full 210-second warm run):

| Stage | First-use hashes / matching registrations | Median lead | Lead >=5 seconds |
| --- | --- | --- | --- |
| Compute | 94 / 94 | 42.29 s | 59 |
| Pixel | 97 / 97 | 27.39 s | 72 |
| Vertex | 75 / 75 | 36.10 s | 59 |
| Mesh | 4 / 1 | 15.61 s for the single match | 1 |

There were 1,664 registration events and 1,123 registered hashes, including 660 compute hashes.
Compute `5323c4ef4f785055` was registered 43.91 seconds before first use. The ELF contained 6,599
header candidates, including 715 compute entries. These counts describe different populations
and do not measure whole-game coverage. Warm-run lead times are not cold-run guarantees; the
shortest pixel lead was only 20.8 ms.

## Background compute translation at registration

The AGC registration hook now copies compute code and static metadata into a separate CPU queue.
It requires the complete thread-dimension/resource-register set and dispatch modifier. The same
register decoder and static-input builder as the dispatch path supply wave size, LDS, scratch,
workgroup and thread IDs. It does not read resource descriptors or retain guest pointers.

One worker performs decode, CFG/IR construction and resource tracking. At first use, the normal
program cache takes a ready result only when **every runtime static-key word**, user-data count,
code length, hash and actual code bytes match. Taking the IR is a one-time move. A pending,
failed, evicted or incompatible result falls back immediately to normal translation; late work
for a request already handled normally is discarded. New resource permutations may still need
normal translation. Complete shader debug dumps bypass the speculative cache.

Known source keys already loaded by startup precache are skipped when the program-cache lock is
available without waiting. Final resource materialization, specialization, SPIR-V emission and
Vulkan driver compilation still happen through the ordinary path. Registration is therefore
not a replacement for the startup seed or a catalogue of every possible pipeline.

Limits: 1,024 entries, 8 MiB of copied source, 128 KiB per source and 192 MiB of retained IR
accounting. IR accounting measures container capacities with a 2x allowance; it is not a limit
on total emulator RAM. Completed entries can be retired for later registrations. Large retired
IR is destroyed outside the queue lock. A speculative job also has limits of 16,384 decoded
instructions, 1,024 initial CFG blocks and 500,000 constructed IR instructions, with cooperative
three-second checks at pass boundaries and periodically during instruction construction. This
is not a hard process timeout or protection from arbitrary memory corruption.

A thread-local fatal-error interceptor turns normal translator rejections into exceptions only
inside the worker, before fatal logging/emergency shutdown. Stack unwinding discards the partial
IR; other threads retain their normal fatal policy. Builds without exception unwinding leave
the feature disabled. The predication pass now passes temporary state explicitly, avoiding
shared mutable state between foreground graphics and background compute translation.

Diagnostics: `CsPretranslate: ready|hit|miss|skipped|summary`. A hit's `saved_us` is the duration
of that background translation, not a measured reduction in frame stalls; compare foreground
`AvTrace` timings and matched cold runs for the actual effect. The existing cold/prepare-cold
switches and seed preparation retain their meanings.

Validation uses `TestComputePretranslation` in `shader_cfg_tests` (owned code, exact static keys,
failure recovery, budgets and lifecycle). With `KYTY_RECOMPILE_EARLY_VERIFY=1`, the existing
`KYTY_RECOMPILE` harness runs background and foreground compute translation concurrently and
requires identical IR text and final SPIR-V for the stored specialization.
