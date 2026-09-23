# Session 104 — launch and scoring commands for Stage 1 (`sh104`, `mut104`) and Stage 2 (`dwk104`, `vwk104`)

Git Bash. Every `KYTY_*` goes to `enter_scene.py` **positionally** (session 96 trap: exported
variables are dropped, except `KYTY_GATE_SCHEDULE`). **Never pass `KYTY_GPU_CHECKPOINTS` or
`KYTY_REC`** to a measurement run. Binary: the installed `16ef56b6…` (`--no-install`). One game at a
time; nothing else on the GPU (`nvidia-smi` before each run); no scorer or agent running during a
run (session 98 guards check 6).

## 0. Before the first run

1. Seal: `pred_drafts/02_a_stage1.draft.md` → `pred/02_a_stage1.md` and
   `pred_drafts/03_dawalk.draft.md` → `pred/03_dawalk.md` (drop each "Draft notes" section), then

       sha256sum C:/kyty/s104/pred/02_a_stage1.md C:/kyty/s104/pred/03_dawalk.md >> C:/kyty/s104/SEALS104.txt
       wc -c C:/kyty/s104/pred/02_a_stage1.md C:/kyty/s104/pred/03_dawalk.md

   and put the hashes and byte counts into `a104.py` / `dwk104.py` (`PRED_SHA`, `PRED_BYTES`).
2. `python C:/kyty/s104/test_a104.py` and `python C:/kyty/s104/test_dwk104.py` — both must read
   `0 failed` after the constants are filled (the tests seal a text of their own and are not affected).
3. `sha256sum "C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"` = `16ef56b69c4a99fa…c4780352`.

## 1. Stage 1 — `sh104` first, then `mut104` (each ≈ 5.5 min, inside the 600-s tool limit)

    python C:/kyty/s104/enter_scene.py sh104 --hold 300 --attempts 1 --no-install \
      --gates-file C:/kyty/s104/gates_base.txt --pred C:/kyty/s104/pred/02_a_stage1.md \
      "KYTY_GATE_SCHEDULE=90+1800:shadowresolve=0 shadowmask=3|shadowresolve=4 shadowmask=3" \
      KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0

    python C:/kyty/s104/enter_scene.py mut104 --hold 300 --attempts 1 --no-install \
      --gates-file C:/kyty/s104/gates_base.txt --pred C:/kyty/s104/pred/02_a_stage1.md \
      "KYTY_GATE_SCHEDULE=90+1800:mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1|mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1" \
      KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0

Check right after each: `<tag>.json` → `schedule` is exactly the string above, `env` has no
`KYTY_GPU_CHECKPOINTS`/`KYTY_REC`, `prereg.sha256` is the sealed hash; the log's first `GateArm:`
line reads `period=90 abba=1 text=<arm 0 text>`; for `sh104`, four `ShadowResolve: worker N started`.
Entry hang → `sh104_entry1` / `mut104_entry1` (one further isolated attempt). INVALID → one repeat
`sh104b` / `mut104b` (`pred/02` §2).

Score (offline, after both runs; never overwrites):

    mkdir -p C:/kyty/s104/runs104
    python C:/kyty/s104/a104.py --mut mut104 --sh sh104 --out C:/kyty/s104/runs104/a104_score.json

## 2. Stage 2 — `dwk104` (≈ 10.5 min: launch it with `run_in_background`, the tool limit is 600 s)

    python C:/kyty/s104/enter_scene.py dwk104 --hold 600 --attempts 1 --no-install \
      --gates-file C:/kyty/s104/gates_base.txt --pred C:/kyty/s104/pred/03_dawalk.md \
      "KYTY_GATE_SCHEDULE=90+1800:dawalk=0 dawalklead=1|dawalk=1 dawalklead=1" \
      KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0

Score it first without the video (a non-SHIP verdict ends Stage 2 here and `vwk104` is not run):

    python C:/kyty/s104/dwk104.py dwk104 --out C:/kyty/s104/runs104/dwk104_score.json

Only if that prints `SHIP_PENDING_VIDEO`: the video pass on the same binary, `dawalk=1` in the gate
TEXT (no schedule), recorded, not pinned:

    python C:/kyty/s104/gen_gates.py --with dawalk=1 --out C:/kyty/s104/gates_dawalk1.txt
    python C:/kyty/s104/enter_scene.py vwk104 --hold 120 --attempts 1 --no-install --rec \
      --gates-file C:/kyty/s104/gates_dawalk1.txt --pred C:/kyty/s104/pred/03_dawalk.md \
      KYTY_GPU_MARKERS=0
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s104/rec_vwk104.mp4 4 6 C:/kyty/s104/vidframes_vwk104 \
      > C:/kyty/s104/vwk104_glitch.txt
    python C:/kyty/s104/dwk104.py dwk104 --out C:/kyty/s104/runs104/dwk104_score_video.json \
      --video-meta C:/kyty/s104/vwk104.json --video-report C:/kyty/s104/vwk104_glitch.txt

(`vid103` gave 3 842 frames from `--hold 120`; if the report shows < 3 000 frames the pass FAILS and
is re-taken with `--hold 180`, never argued.)

## 3. Draft arithmetic on old logs (no seal needed; never a verdict)

    python C:/kyty/s104/a104.py --sh dab102a --root C:/kyty/s102 --draft
    python C:/kyty/s104/a104.py --mut flr83b --root C:/kyty/s83 --draft --period 30 --keep 20:29
    python C:/kyty/s104/a104.py --mut pl96a  --root C:/kyty/s96 --draft --period 30 --keep 20:29
    python C:/kyty/s104/dwk104.py dab102a --root C:/kyty/s102 --draft
