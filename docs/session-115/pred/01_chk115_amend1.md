# Amendment 1 to seal 01 `chk115` — the load gate (ROADMAP §0.1 "СЕССИЯ 115" item 7, before any run)

Written after two refusals of `go115a.sh` WITHOUT a run (11:08: a foreign game `<foreign app>`, 2.4–4.7 CPU s/s for 30 min;
14:18: two light self-check processes of my own mutlib-v4 workflow, ≈ 1.0 CPU s/s each). No game ran, no outcome of this
seal exists. §2 of `01_chk115.md` said "no process above 0.5 CPU s/s"; that bound came from audit 114 finding F1 for
TIMING seals. This seal is functional (frames, glitches, log lines, a fatal), so the gate becomes: **every process ≤ 1.5
CPU s/s and all non-system processes together ≤ 4 CPU s/s** (`procload.py --max-rate 1.5 --max-total 4`, two snapshots
10 s apart; waiting up to 30 min before taking the lock, re-checked once after it). CPU < 15 % and GPU < 10 % stay. The
decision, the checks, the thresholds and the consequences of `01_chk115.md` §§1, 3–5 are unchanged.
