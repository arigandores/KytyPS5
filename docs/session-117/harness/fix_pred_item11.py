"""Session 117, ROADMAP item 11: the pre-registration text follows the pre-seal fixes."""
from pathlib import Path

p = Path('C:/kyty/s117/pred/01_spn117.md')
s = p.read_text(encoding='utf-8')


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)


rep("""Session 117. ROADMAP §0.1 "СЕССИЯ 117 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 3–6; design `docs/session-117/designA4_spine.md`.""",
    """Session 117. ROADMAP §0.1 "СЕССИЯ 117 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 3–11 (item 11: the pre-seal check and its fixes);
design `docs/session-117/designA4_spine.md`.""")
rep("""- Build `3cde1af8ed1af960a2216957288c6d9f54e606fd7c3e48bd97659b052a9c64b9` (git `36c8350`: `spine` knob, 0..2, default 0, measurement only; `operator== = default` on the 61
  register types of `hardwareContext.h`; nothing under `src/graphics/shader/**`).""",
    """- Build `3cde1af8ed1af960a2216957288c6d9f54e606fd7c3e48bd97659b052a9c64b9` (git `36c8350`: `spine` knob, 0..2, default
  0, measurement only; `operator== = default` on the 61 register types of `hardwareContext.h`; nothing under
  `src/graphics/shader/**`). Its embedded label reads `…-gfbcfd49-dirty`: it was built from the working tree a second
  before commit `36c8350`, whose only source change over `fbcfd49` is the `graphicsRun.cpp` fix it contains.""")
rep("""compares on kept frames, arm 1 compares); GPU idle before the run (median ≤ 10 %).""",
    """compares on at most 1 % of its elements on kept frames, arm 1 compares); `el_ops`: `spine_el` / (draws + dispatches)
over the kept frames of arm 1 within [0,95; 1,05]; GPU idle before the run (median ≤ 10 %).""")
rep("""- **K5 (reproduction)** over every frame after frame 1800: **FAIL** if any `spine_bad` or `spine_misal`; **PASS** if both
  are 0 and `spine_cmp` ≥ 90 % of `spine_el` over the kept frames (10–89) of arm-1 blocks; else **NOT_EVALUABLE**.
  `spine_pad` (bytes differ only in padding), `spine_lost` (a compare lost to another plan of the same processor) and
  `spine_abort` are reported, not failing.""",
    """- **K5 (reproduction)** over every `FrameTrace-x` line after frame 1800 (duplicates and frames missing other lines
  included): **FAIL** if any `spine_bad`, `spine_misal` (a submission's real element count differs from its plan) or
  `cram_write` (const RAM is outside the compare), or any `SpineMismatch:` / `SpineMisalign:` line in the log; **PASS**
  if none and `spine_cmp` ≥ 90 % of `spine_el` over the kept frames (10–89) of arm-1 blocks; else **NOT_EVALUABLE**.
  `spine_pad` (bytes differ only in padding), `spine_lost` (compares lost because another plan of the same processor
  replaced the snapshots — an instrument limit, caught by the ratio) and `spine_abort` are reported, not failing.""")
rep("""  **walker fit** = mean(`da_walk_us` + `spine_ns`/1000) < mean `dt_us` over the same frames.""",
    """  **walker fit** = mean(`da_walk_us` + `spine_ns`/1000) < mean(`dt_us` − `spine_ns`/1000) over the same frames (the
  frame the GuestGpu thread would have without the spine; the first draft compared with `dt_us`, which the spine itself
  lengthens, and could never fail).""")
rep("""real state at every submission start, so it proves reproduction within a submission, not the carry across submissions;
`float` register fields holding NaN would read as `spine_bad`.""",
    """real state at every submission start, so it proves reproduction within a submission, not the carry across submissions;
`m_num_instances` (rewritten by indirect draws from GPU-written arguments) and const RAM are not compared (const RAM
writes are counted by `cram_write`); `float` register fields holding NaN would read as `spine_bad`; the words the plan
reads early (predication, `COND_EXEC`, the 14-dword branch) were never met in Sky Garden in the smoke runs.""")
p.write_text(s, encoding='utf-8')
print('pred ok')
