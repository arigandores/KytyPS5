from pathlib import Path
p = Path('C:/kyty/s108/FACTS.md')
s = p.read_text(encoding='utf-8')


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep("# Session 108 — SHIPPED `cspfam=4`: the walker skips its steady-state compute prefetch per shader family — Δ mean frame −141.8 µs at the pin (≈ +0.46 % game speed)",
    "# Session 108 — `cspfam=4` shortened the mean frame by 141.8 µs at the pin and shipped, then the powered safety guard failed its rule (6 vs 3 + 2 dispatch-time compiles) and the default was rolled back to 0 — no speedup kept")
rep("**Opening numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3` (and now `cspfam=4`):",
    "**Opening numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3` (`cspfam=0` again):")
rep("""   `dab106`). Predictions F1 F2 F4 F5 F6 HIT, F3 MISS.""",
    """   `dab106`) — **corrected by the audit (§7 item 2): the gain is more 1-vblank frames (13.25 → 13.97 %), fewer
   2-vblank frames; the block-mean medians coincide because block means move in 575 µs steps.** Size marginal:
   sign-flip p 0.009, bootstrap 95 % CI [−246, −38] µs ⇒ +0.46 % (CI ≈ +0.12 … +0.79 %). Unreported side effect:
   `gpu_busy_us` +87.5 µs a frame in arm 1 (t 4.5), cause unknown. F3 was mis-specified (`cpu_net` tracks `dt`,
   per-pair correlation 0.93). Predictions F1 F2 F4 F5 F6 HIT, F3 MISS.""")
rep("""4. **Default `cspfam` = 4** (ROADMAP item 5 recorded first; `eed387b`, committed before the build so the label is
   clean of working-tree edits).""",
    """4. **Default `cspfam` = 4** (ROADMAP item 5 recorded first; `eed387b`; source-traceable to that commit, not
   bit-reproducible — PE link time and `__DATE__`).""")
rep("""   marker; `sf108b` 2.07 M prefetch skips. A one-scene smoke test, not a proof.""",
    """   marker; `sf108b` 2.07 M prefetch skips. **Without power (audit §7 item 1):** the startup precache builds all 121
   compute pipelines from `pipelines.bin`, so no new permutation was met — in this run or in `fam108`.
6. **Powered guard** (ROADMAP item 7, rule before the runs): Sky Garden 300 s, pinned, `KYTY_PIPELINE_PRECACHE=gfx`
   (compute precache off = first visit): `sf108c` (`cspfam=0`) `cspf_new` 74, **`cs_sync_new` 3** (the counter's first
   positive control), `cs_sync_wait` 0; `sf108d` (default 4) `cspf_new` 71, **`cs_sync_new` 6**, `cs_sync_wait` 0,
   2.53 M skips; no failure marker. Rule Σ(new + wait) ≤ 3 + 2 **not met** ⇒ **default rolled back to 0** (ROADMAP item
   8, `01f0c79`). The difference may be noise (separate runs), but the rule was recorded first. **Build
   `379777bba4271847b1b805c403944e4a6552acd0aac0b5cd3af12be36c489107`** (label `…-g01f0c79-dirty`), installed; its
   pinned video `vid108r`: 3 933 frames, 0 glitches, `cspfam_skip` 0, `cs_sync_new` 0 — `check108r.py` (`76543aa4…`,
   audit gaps closed) PASS. The knob stays in the tree (default 0).""")
rep("""`go108.sh` / `go108v.sh` / `go108s.sh` (each holds `C:/kyty/SEALED_RUN.lock`), `check108.py`, `seal108.py` (the
one-shot that placed and sealed), `kyty_emulator_fd1d0bd7.exe` (the scored build, kept for re-scoring).""",
    """`go108.sh` / `go108v.sh` / `go108s.sh` / `go108p.sh` / `go108r.sh` (each holds `C:/kyty/SEALED_RUN.lock`),
`check108.py`, `check108r.py`, `seal108.py` (the one-shot that placed and sealed), `kyty_emulator_fd1d0bd7.exe` and
`kyty_emulator_fc78c564.exe` (scored builds, kept for re-scoring), `audit108/` (the auditor's parsers and mutants).""")
rep("""(pause documentation), `e687a78` (resumption record + seal + fixtures + run chain), `eed387b` (fam108 SHIP record +
default 4), `3c988bb` (build video PASS + desert rule), the session commit. Build `fd1d0bd7…` (scored; built from
the working tree 7 s before `f9e19f7`, label `…-g3cc53a2-dirty`, same code; not reproducible — a copy is kept in
`C:/kyty/s108`). Build `fc78c564…` (installed; `eed387b`). No push.""",
    """(pause documentation), `e687a78` (resumption record + seal + fixtures + run chain), `eed387b` (fam108 SHIP record +
default 4), `3c988bb` (build video PASS + desert rule), `22d5ad4` (audit + powered-guard rule), `01f0c79` (rollback
record + default 0), the session commit. Build `fd1d0bd7…` (scored `fam108`; built from the working tree 7 s before
`f9e19f7`, label `…-g3cc53a2-dirty`, same code; copy kept). Build `fc78c564…` (`eed387b`, default 4; `vid108`,
`sf108a/b`, `sf108c/d`; copy kept). Build `379777bb…` (`01f0c79`, default 0; installed). The "-dirty" of every label
is 5 deleted PNGs in the `3rdparty/nlohmann_json` submodule, nothing else. No push.""")
rep("""| `sf108a`/`sf108b` | desert 300 s, `cspfam=0` / default 4 | `cs_sync_new` 0 / 0, no marker |""",
    """| `sf108a`/`sf108b` | desert 300 s, `cspfam=0` / default 4 | `cs_sync_new` 0 / 0, no marker — no exposure |
| `sf108c`/`sf108d` | Sky Garden 300 s, compute precache off, `cspfam=0` / 4 | `cs_sync_new` 3 / 6 ⇒ rule failed, rollback |
| `vid108r` | video of build `379777bb`, default 0 | 3 933 frames, 0 glitches; `check108r` PASS |""")
rep("""## 5. Next

The walker's second hold""",
    """## 5. Next

**First, `cspfam` v2:** the skip without the first-contact window — a global atomic count of compute-pipeline
creations (by the prefetch or synchronously on the dispatch) joins the table's stamps, so any creation clears every
streak and the walker prefetches everything again for K rounds; then a sealed ABBA in the shipping configuration
AND a powered-guard ABBA (compute precache off, ABBA rather than separate runs). Then the walker's second hold""")
rep("""**Measured.** At the pin in Sky Garden, skipping the steady-state compute prefetch shortens the mean frame by
141.8 µs (t −2.65) with no dispatch-time compute compile in 600 s; the desert entry shows none either.
**Not measured.** The contention left after `cspfam=4`; the gain without the pin. **Not proved.** That the skip is
safe in every scene (scene loads bring new permutations; `cs_sync_new` is the guard); additivity with other gains;
60 FPS.""",
    """**Measured.** At the pin in Sky Garden, skipping the steady-state compute prefetch shortens the mean frame by
141.8 µs (t −2.65, 95 % CI [−246, −38]) when every permutation is precached; with the compute precache off it lets
through 6 dispatch-time compiles in 300 s against 3 without it (separate runs). `cs_sync_new` counts (positive
control). **Not measured.** The contention left after the skip; the gain without the pin; the cost of one
dispatch-time compile. **Not proved.** Any kept speedup this session (none); safety of a skip in scenes with new
content; additivity; 60 FPS.""")
audit = """One agent, three lenses, sealed as `pred/02_audit108.md` (`401a76cc…`). **Recount CONFIRMED**, **Protocol HOLDS**
(MINOR deviations), **Code NOT REFUTED**. Findings: (1) **MAJOR** — the guard and the desert smoke had no power →
powered test, rule failed, rollback (§1 items 5–6); (2) the gain is more 1-vblank frames, not "the tail"; (3) size
marginal (CI [−246, −38]); (4) `gpu_busy_us` +87.5 µs in arm 1, cause unknown; (5) F3 mis-specified; (6) the
heartbeat ran `ls` + `tasklist` during `vfm108` (not `fam108`) because its prompt told it to — prompt replaced; (7)
stray `grep` + orphaned `tail -F` watchers alive in every sealed run — killed; (8) provenance wording (not
bit-reproducible); (9) `cs_sync_*` exist only in traced runs; `check108.py` gaps closed in `check108r.py`; (10) two
fixture mutants survive (GATEARM order clause, `spin_gpu_us` in `cpu_net`) → fixtures for the next derived scorer.
Full report `C:/kyty/s108/audit108/AUDIT108.md`.
"""
rep("AUDIT_PLACEHOLDER\n", audit)
p.write_text(s, encoding='utf-8')
print('ok')
