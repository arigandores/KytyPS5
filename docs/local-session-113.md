# Session 113 — WIP, PAUSED before its first game run: the BDA regime explained (a buffer registration invalidates every region stamp; the buffer GC runs above a device-memory threshold); within a build OLD is not slower (census); knob `bdanarrow` built, audited offline, verify seal 01b ready

**Single source of truth for session 113 while it is paused.** Mirrored into git as `docs/local-session-113.md`. Harness
root `C:/kyty/s113`. Everything below is measured (offline, archived logs) or read from code; **no game run happened in
this session** (the user paused it: "добиваем всё без запуска игры, документируем и останавливаемся").

**Opening numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1 daguard=1`;
installed build `b47b58a9…` (session 112). 60 FPS is not promised.

---

## 1. Result (offline)

1. **Port** `C:/kyty/s112/s113_port.py` (`04cfa646…`, 3 591 lines): `PORT DIAGNOSTIC: clean; carried=7591 ledger=87
   skipped=47`; 70 sealed texts (68 in `prev112/pred`); `gates.cpp` asserted at 141 entries / ABSENT 42 at port time
   (the `bdanarrow` knob added after the port makes it 142 / 43).
2. **Mechanism of the BDA regime** (code reading + 190 archived logs, `C:/kyty/s106_stage/bda113/MECHANISM.md`, git
   `docs/session-113/census/MECHANISM.md`): OLD = one extra full walk of the registered-buffer span per frame (1 068 − 52
   ≈ 1 016 four-MiB regions). `PrepareBda` (`renderContext.cpp:343-345` before the patch) called
   `InvalidateBdaRegionStamps()` on any move of the buffer registration epoch — every region's stamp went stale, not just
   the changed buffer's. In OLD the epoch moves ~1.2 times a frame: the buffer GC (`bufferCache.cpp:1935-1991`) evicts
   buffers idle for 160 ticks and they are created again (`buf_new` 1.1–2.4 a frame). The GC runs only when device-local
   usage ≥ a threshold fixed in the constructor (9 295.8 MiB here); NEW runs sit 225–567 MiB below, OLD 133–1 085 above
   (whole 256-MiB VMA blocks after the level load). Within-run evidence: the `bindfloor` arm that holds the GC reads 0–1.6 %
   OLD frames against 95–97 %.
3. **Census of 659 archived logs** (`census113.py`, 151 fixture checks; 579 usable runs of sessions 53–112,
   `docs/session-113/census/census_summary.md`): OLD 289, NEW 221, 11 switched; desert/intro/title all NEW, Sky Garden
   288 OLD / 135 NEW. `bda_scan` a flip = base ~50 + k full re-walks of ~1 014 regions (OLD: k = 1 on 59.9 % of flips, 2 on
   29.3 %; NEW: k = 0 on 96.8 %); a re-walk follows a flip that created a buffer (88 % in NEW), and OLD creates a buffer on
   84.6 % of flips. The regime settles when the load burst ends, but 8 runs switched later (NEW → OLD near n ≈ 940).
   **Within a build OLD is not slower:** identical-launch series Δ`dt` (OLD − NEW) **+17 ± 84 µs**; regression on the
   re-walk share +91 ± 193 µs; median over 28 build+scene groups +2.6 µs. OLD shows less `sync_up_kb` (−368 KiB a flip,
   27/27 groups), fewer `faults_gpu`, less `prot_gpu_us` — the full re-walk seems to take buffer syncs over from other
   paths. Session 112's audit indication (+27…+442 µs across builds) did not survive the within-build comparison.
4. **Code** (`37e0de1`; ROADMAP items 1–2 recorded first, `5a8970c`): knob **`bdanarrow`** (`KYTY_BDA_NARROW_STAMPS`,
   0..2, default 0, LAST knob row). Unconditionally `ChangeRegister<insert>` marks the stamps of the new buffer's regions
   stale (`MarkBdaRegions`, generation 0). `PrepareBda` reads the knob once: 0 — a registration still bumps the global
   generation; **1 — only a guest-map move bumps it**; 2 — 0 plus a check of every region 1 would skip (`bda_nwould`) and
   of those whose dirty ranges overlap a registered buffer (`bda_nmiss`). Counters `bda_ginv_reg`, `bda_ginv_map`,
   `bda_rinv`, `bda_nskip`, `bda_nwould`, `bda_nmiss`, `bda_nxthr`, `bgc_evict`. Build
   **`94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92`** (copy `s113/kyty_emulator_94362eae.exe`; NOT
   installed — `go113.sh` installs it). The binary carries every new counter name (checked offline).
5. **Seal 01** `pred/01_vbn113.md` (`e6b7b397…`, `942fd2f`) — **never run; superseded by seal 01b** (item 8).
6. **Offline adversarial audit before any run** (workflow of 31 agents: four lenses — safety of mode 1, validity of the
   check, threads, harness — and two skeptics per finding; `C:/kyty/s113/audit113pre/AUDIT113PRE.md`, git
   `docs/session-113/audit/`): the safety of mode 1 is NOT REFUTED; **MAJOR — races inflate `bda_nmiss`** (the stamp was
   read without the region lock and the dirty bits collected later under it, so a guest write in between counted as a
   miss that mode 1 would not suffer; 0.4–40 expected in 300 s ⇒ a NO_GO of seal 01 could not be read). MINOR: an old
   `bdastamp` hole (a 4-MiB region shared by two mapped ranges is walked only for the lower one — every knob; no such layout
   found in `vid112`); `armdefer` vs the three-epoch cache (gate off); `bda_nxthr` in BAD (0 by construction); B3–B5 were
   means not levels; no row-continuity check; the chain installed without a hash check; "nothing else on the machine"
   unchecked; mutants ran on the draft copy.
7. **Race-separating check** (`6eb7d14`; ROADMAP item 5 first, `505c589`): after the collect the region stamp is read
   again — `bda_nmiss` only if unchanged, else **`bda_nrace`**; the first 40 misses logged as `BdaNarrowMiss: region=…
   range=… buffer=…`. Build **`7d9fa0288099204f16974292a0d474afee80e58df43770612e11b8d5db5d6e5f`** (copy
   `s113/kyty_emulator_7d9fa028.exe`; not installed).
8. **Seal 01b** `pred/01b_vbn113b.md` (**`120d0ad9…`**, `b885fd4`), replacing seal 01 before any run: BAD = Σ`bda_nmiss`
   (races excluded) + Σ`bda_nxthr`; new branch INVESTIGATE (BAD made only of `bda_nxthr`); new admission terms PRE_RUN
   (launcher's pre-run GPU utilisation ≤ 10) and STREAMS (contiguous flips, x rows = main rows ±1); B3–B5 medians over the
   scene rows; B6 Σ`bda_nrace` ≤ 40. Scorer `vbn113b.py` (from `vbn113.py` by `make_vbn113b.py`; 83 fixture checks; 41
   mutants run on the SEALED copy, output `mut_vbn113b.out.txt`). Chain **`go113b.sh`** (refuses a held lock, installs
   the pinned copy after a sha check, verify only). **Not run.**
9. **Seal 02 (ship ABBA `bdanarrow=0|1`)** not written: scorer `shn113.py` derived from `net112.py` by `make_shn113.py`
   (draft copies `C:/kyty/s113/shn113_draft/`): 235 fixture cases ALL OK, **310/310 mutants killed** (that pass took ~3 h —
   the reason for ROADMAP item 7, the fast mutation harness), draft run on `net112` OK. It is built for `94362eae`
   without `bda_nrace` — re-pin before sealing; open: the NARROW_ARMED_ARM1 threshold (≥ 1 may refuse an armed run;
   decide from `vbn113`'s `bda_ginv_reg`) (RESUME POINT step 3).

## 2. Harness

`C:/kyty/s113`: `vbn113b.py`, `test_vbn113b.py`, `mut_vbn113b.py`, `make_vbn113b.py`, `go113b.sh` (seal 01b), the superseded
`vbn113.py`/`test_vbn113.py`/`mut_vbn113.py`/`go113.sh` (seal 01), `gates_narrow2.txt` (base + ` bdanarrow=2`),
`gates_narrow1.txt` (base + ` bdanarrow=1`, for the ABBA's video), `SEALS113.txt`, build copies
`kyty_emulator_94362eae.exe` (seal 01) and `kyty_emulator_7d9fa028.exe` (seal 01b); `audit113pre/`; census and mechanism scripts in `C:/kyty/s106_stage/bda113/` (git
`docs/session-113/census/`).

## 3. Source, builds, provenance

Commits: `d611c20` (session 112 close), `5a8970c` (records 1–3), `37e0de1` (code), `942fd2f` (seal 01 + port), `3931e65`
(census record 4), `505c589` (record 5 — audit and decisions), `6eb7d14` (race-separating check), `b885fd4` (seal 01b),
the pause commit. Builds `94362eae…` (`37e0de1`) and `7d9fa028…` (`6eb7d14`); installed exe still `b47b58a9…`. No push.

## 4. Runs

None in this session.

## 5. RESUME POINT

`docs/next-session-113.md`, section "RESUME POINT": run `go113b.sh` (nothing else running), record the verdict in ROADMAP
(item 7), then — on GO — re-pin `shn113` to `7d9fa028` (+ `bda_nrace`), seal 02, the ABBA, its video; then the session
audit and close. The heartbeat cron was deleted and the loop stopped at the pause.

## 6. Proved, and not proved

**Found (offline).** What makes a run OLD (the buffer GC above a device-memory threshold; each registration invalidating
every region stamp) and that, within a build, OLD runs are not measurably slower than NEW (+17 ± 84 µs).
**Not proved.** That knob 1 is safe (to be checked by the sealed verify); that it saves frame time (the census suggests
little: the extra walk seems to take buffer syncs over from other paths); anything about 60 FPS.

## 7. Offline audit

See §1 item 6; report `C:/kyty/s113/audit113pre/AUDIT113PRE.md` (merged findings S1–S9 with skeptic verdicts, refuted
items, "checked OK" per lens). Its MAJOR is fixed in code and seal (items 7–8); its MINORs are either fixed in seal 01b
(PRE_RUN, STREAMS, medians, INVESTIGATE, hash-checked install, mutants on the sealed copy) or recorded as ROADMAP §7 debts
(the `bdastamp` shared-region hole, the epoch order in `ChangeState`, `armdefer`).
