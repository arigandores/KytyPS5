# Automatic shader preparation for every title

Decision, 2026-09-10: manual scene analysis and distributing an ASTRO-only seed are test
procedures, not the product workflow. Normal play must collect the information automatically;
the next launch must prepare it before guest execution. No title-specific addresses or routes
belong in that mechanism.

## What already works

`PipelineCache::StartPrecache` loads `_ShaderCache/<TITLE_ID>/pipelines.bin` for every title.
`RecordGraphicsRecipe` and `RecordComputeRecipe` record newly encountered pipeline combinations
automatically, and `MaybeWriteRecipes` periodically saves the growing catalogue. The startup
screen waits for known pipelines. Seeds are optional first-launch input, not a prerequisite
for automatic collection. This code has no ASTRO title check; runtime validation so far is
ASTRO-only, so other games are not claimed tested.

The AGC registration hook also starts bounded CPU translation of new compute shaders before
their first dispatch. Final resource specialization and driver compilation still need the
ordinary pipeline path. Registration is not necessarily before guest startup: it can happen
while loading a later level. Games bypassing the AGC creation entry point require discovery
at the shared shader-program lookup as well.

## Why scanning the game files is insufficient

A guest shader binary is not a finished Vulkan pipeline. Current translation specializes on
resource descriptors (including image formats/dimensions and buffer properties), stage
interfaces and execution state; graphics compilation also needs render-target and fixed-function
state. Game archives may load or construct code later. Enumerating byte patterns in one ELF
does not enumerate every combination, and trying the Cartesian product is unbounded.

Vulkan pipeline caches reuse previously created pipelines across launches; they do not infer
missing create information. See the [Khronos pipeline-cache guide](https://docs.vulkan.org/guide/latest/pipeline_cache.html).
Graphics pipeline libraries can compile parts separately and reduce later combination cost,
but still require each part's state. Their fast-linking property must be queried; support alone
does not establish hitch-free linking. See [Khronos graphics pipeline libraries](https://docs.vulkan.org/features/latest/features/proposals/VK_EXT_graphics_pipeline_library.html).

## Recommended next implementation

The most useful next step is a durable **guest replay catalogue**, separate from generated IR,
SPIR-V and driver caches. Today a translator-source change invalidates recipes and translations
together; raw GCN is not stored in `ShaderTranslationCache::Entry`. The offline recompiler needs
separate debug GCN dumps. Consequently known coverage cannot yet be rebuilt automatically after
such an update. Do not bypass the translator signature to reuse stale IR/SPIR-V.

1. Capture owned GCN bytes and explicit static stage state at the common program-lookup path;
   optionally discover them earlier at AGC registration. Deduplicate by full content and state,
   use a bounded background writer, and never retain pointers into guest memory.
2. At resource materialization/pipeline creation, capture the semantic inputs needed to replay
   specialization: descriptor words/metadata read by the current plan, SRT decisions, stage
   interfaces and pipeline state. Do not persist host handles, struct padding, permutation
   indices, IR node IDs or the whole guest address space as stable identifiers. A translator
   change that needs previously uncaptured data must reject that record and relearn it.
3. Give this replay format its own version, title/game-version identity, lengths and checksums.
   Publish sources before dependent recipes, retain the last complete generation after an
   interrupted write, and keep incompatible records available for explicit format migration.
   Derived caches remain keyed by translator capabilities/options and host GPU requirements.
4. At launch, rebuild stale derived entries from valid replay inputs in bounded workers, then
   feed them into the existing preparation screen. Count prepared, rejected and pending entries
   separately. Cancel cleanly on window close and fall back to normal compilation for unsupported
   records. Automatically append newly observed records during play, without requiring exports.
5. For genuinely unseen combinations, extend safe early CPU translation to VS/PS/mesh only after
   auditing their static input requirements; use generic PM4 lookahead when complete state is
   available. Prototype graphics pipeline libraries separately with measured driver support and
   a correct full-pipeline fallback. Never hide compile stalls by silently dropping draw calls.

This gives all games automatic warm starts and allows known coverage to survive translator
updates where the captured inputs suffice. It does not promise complete first-launch coverage
for never-observed scenes. Optional shared guest catalogues could bootstrap that case later;
the present seed format is tied to its translator and GPU model, and is not that portable format.

For unseen resource combinations, a longer-term experiment is a less-specialized translation
of an already discovered guest program, with resource properties read dynamically, while an
optimized specialization compiles in the background. This is a design hypothesis, not an
implemented fallback. The [Dolphin hybrid ubershader approach](https://dolphin-emu.org/blog/2017/07/30/ubershaders/)
illustrates the general strategy, but it cannot simply be transplanted to arbitrary PS5 GCN
programs. Correct wave operations, image types, derivatives and memory semantics still have to
be supported; the generic path itself must be available before use. A GPU interpreter for the
entire guest shader ISA is a separate major project with unknown practical performance here.

## Acceptance checks for that implementation

- A new title with no seed learns records through ordinary play; its next launch prepares them
  before `Execute: Main`, with no route scripts, debug dumps or manual exports.
- A translator update rebuilds captured supported records without replaying their scenes; a
  change needing extra resource inputs rejects affected records instead of guessing.
- Interrupted writes, corrupt lengths/checksums, game updates, unsupported stages, worker
  failures, cancellation and queue limits preserve a usable ordinary compilation path.
- Warm, fully cold and derived-cache-cold runs report startup cost, runtime CPU translation,
  driver creation and long present intervals independently. Compare matching scenes and verify
  complete videos. Use a second available title to test generality before claiming it empirically.

Status: architecture decision only; the durable replay format and graphics pipeline-library
prototype are not implemented by the CPU BDA/SRT performance changes of session 40.
