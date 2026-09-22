# Sealed pre-registration 04 — session 102, candidate code 1: the value, not the presence, of `KYTY_GPU_CHECKPOINTS` (and of its class)

**Immutable once written.** Written after the build and before the witness run.

---

## 0. The defect and the fix

Session 101 found `vulkanWindow.cpp:1195` testing `KYTY_GPU_CHECKPOINTS` for **presence**:
`=0` switched diagnostic checkpoints **on**, `RecordThreadWanted` (`commandRecorder.cpp:1078`)
refused the record thread, and every draw paid an `EndRendering` before and after plus an
`eAllCommands` barrier and a global mutex per operation. Measured in `cm101a` against `cm101d`
(same binary `b70d0096…`, same scene, sole difference the variable): `rec_n` 0 against 10 957,
`dt` 48.9 against 32.4 ms, `gpu_busy_us` 48.6 against 12.8 ms, render-pass ends 5 283 against 188 a
flip.

The fix (session 102): a header `common/envFlag.h` with `EnvValueOn` / `EnvFlagOn` — unset, `""`,
`0`, `false`, `off`, `no` (ASCII case-insensitive, exact) are OFF, anything else ON — and every
presence-only switch **outside the translator's hashed sources** converted to it (the class: 52
variables at 90 sites were found; the sites inside `src/graphics/shader/**` are deferred to the next
translator change so that the shader cache stays warm, and are listed in the report). For
`KYTY_GPU_CHECKPOINTS` the body is unchanged (`nv` = NV only, any other truthy value =
breadcrumbs + NV), and a present-but-falsy value logs `Vulkan: GPU checkpoints off
(KYTY_GPU_CHECKPOINTS=<v>)`. **At every truthy value and when unset, behaviour is unchanged by
construction** (the old predicate `v != nullptr` and the new one differ exactly on the falsy set).

## 1. The A/B — same environment string, old binary against new

The A arm already exists: **`cm101a`** (binary `b70d0096…`, `KYTY_GPU_CHECKPOINTS=0`, 300.1 s). The B
arm is one witness run on the session-102 binary with the **same** string:

    python C:/kyty/s102/enter_scene.py ckpt102 --hold 180 --attempts 1 --no-install
      --gates-file C:/kyty/s102/gates_base.txt --pred C:/kyty/s102/pred/04_checkpoints_fix.md
      KYTY_GPU_CHECKPOINTS=0 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0

This is the **one** run of the session in which the variable is deliberately passed; it is the test.
No schedule (plain `gates_base.txt`). It is an inter-run comparison, which this programme does not
accept for small effects (`ROADMAP.md` §3); it is accepted here **only** because the predicted effect
is categorical (a thread that exists or does not; a factor ≈ 3.8 in `gpu_busy_us`), and every limit
below sits far outside any run-to-run spread seen in sessions 94–101.

## 2. Acceptance — the fix PASSES only if every line holds on `ckpt102`

Frames from 2100 to the end of the hold (medians over rows of the main and draw lines):

1. the log carries `Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)` exactly once and **no**
   `Vulkan: GPU checkpoints mode=` line and no `diagnostic checkpoints enabled` line;
2. `RecordThread: started` appears (≥ 1);
3. median `rec_n` ≥ **9 000** (`cm101a` 0; `cm101d` 10 957);
4. median `gpu_busy_us` ≤ **16 000** (`cm101a` 48 631; `cm101d` 12 763);
5. median `dt_us` ≤ **40 000** (`cm101a` 48 941; `cm101d` 32 365);
6. no `GpuHangAbort`, no fatal marker, `GpuClockPin: mode 1` once.

Any failure ⇒ the fix is **not** accepted, and the report says so.

## 3. What this does not show

That any truthy value still enables checkpoints (argued from the diff, not run: `=1` hangs entries,
`hg97a`) · that any of the other converted variables behaves as intended at runtime (argued from the
diff; none is exercised) · any speedup — nothing was made faster for a user who does not pass a
falsy value; for one who does, a diagnostic that was on by accident is off.

---

## Provenance at sealing time

* Emulator binary built this session, NOT yet installed or run: `346ba4f6448c35cba8677101a1599c6ddd0b907d3ea76015ada692cd3b3dc776` (source HEAD `0d35faa` + uncommitted session-102 changes; translator hash `2db9065aef8b54a24a7d29b3584df9647f61dd95` unchanged).
* `shader_cfg_tests.exe` `cfe15c6cf5ce14ed2988d4da4d7e6590c65f2b319b751d1937ccd71b825a73a5`.
* Sealed at 2026-09-22T22:12:14.
