#!/bin/bash
# Session 122, ROADMAP §0.1 "СЕССИЯ 122" items 1-2 (design docs/session-122/design122.md): the bottleneck map across
# scenes through the measurement knob burn, on the build EXPECT below.  One attempt per sealed run (smokes: up to 3),
# pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, gates_base.txt.
#   smoke tags (UNSEALED, disclosed; entry check of a level, 120-s hold, video, no schedule):
#     esky122 eatl122 eght122 ednn122 edes122 + fallbacks emgg122 ehub122 ehov122 eice122
#   burn smoke tag (UNSEALED, disclosed; ROADMAP s.122 item 7): bsky122 - Sky Garden, six arms 300+1800
#     burn=0|102000|402000|802000|202000|302000, no ABBA, 200-s hold, video; the schedule wraps back to
#     burn=0 on its own (the placebo-noise check).  Read it with smoke122.py.
#   codes 5/6/7 smoke tag (UNSEALED, disclosed; ROADMAP s.122 item 13 (a)): csky122 - Sky Garden, four
#     arms 300+1800 burn=0|502000|602000|702000 (record thread block, M1 worker 0 block, GuestGpu::Submit),
#     no ABBA, 200-s hold, video.  It decides whether the code-7 arm may replace the dead code 4 in the
#     seal; no number of it enters a verdict.  Read it with smoke122.py.
#   sealed tags (seal pred/01_map122.md, scorer map122.py; ABBA 90+1800, 300-s hold, no video):
#     sky122  Sky Garden   burn=0|burn=102000   (GuestGpu 2 000 us)
#     skym122 REFUSED: the main-guest-thread arm left the map (ROADMAP s.122 item 13 (b); csky122: code 7 armed,
#             burn_s_main = 0 in every block)
#     skyp122 Sky Garden   burn=0|burn=802000   (placebo)
#     atl122 / ght122 / dnn122 / des122 (and the fallbacks mgg122 hub122 hov122 ice122): the scene's level, burn=0|burn=102000
#     each with an 'r' repeat tag (e.g. sky122r) only on NOT_ADMITTED
#   order of step 4 (ROADMAP s.122 item 17 (d), 13 (b)): sky122, skyp122, then des122 (intro_next) first additional.
# After every run the host-event witness writes hostdev_<tag>.txt (hostdev122.py <tag> --pad 0, offline, never touches
# the GPU or the installed build): map122.py refuses admission without it (ROADMAP s.122 item 17 (a)).
# Refuses: a held lock (noclobber), a busy machine (procload; also while any mutation harness lives), a live
# mutant/fixture process of this session (by name), a pre-registration whose sha differs from the scorer's PRED_SHA
# (sealed tags), a non-idle CPU/GPU.  Both the busy-machine and the name checks are repeated BEFORE the lock is taken and
# the build is installed (audit 121).  Stale artefacts of the tag move to C:/kyty/s122/old/<ts>/.
#   usage: go122a.sh <tag>
T=${1:-}
BASE=${T%r}
case "$BASE" in
  esky122|bsky122|csky122|sky122|skym122|skyp122) LEVEL=underwater_aerial_garden;;
  eatl122|atl122) LEVEL=penguin_atlantis;;
  eght122|ght122) LEVEL=time_stopper_ghost_world;;
  ednn122|dnn122) LEVEL=rotating_level_day_and_night;;
  edes122|des122) LEVEL=intro_next;;
  emgg122|mgg122) LEVEL=mini_giants_garden;;
  ehub122|hub122) LEVEL=hub_crashsite;;
  ehov122|hov122) LEVEL=hoover_beach;;
  eice122|ice122) LEVEL=ice_iceberg;;
  *) echo "usage: go122a.sh <tag>  (see the header)"; exit 2;;
esac
case "$BASE" in
  bsky122) SEALED=0; HOLD=200; ATT=2; SCHED="KYTY_GATE_SCHEDULE=300+1800:burn=0|burn=102000|burn=402000|burn=802000|burn=202000|burn=302000"; EXTRA=""; RECARG="--rec"; SD="--stable-draws 300 --timeout 480";;
  csky122) SEALED=0; HOLD=200; ATT=2; SCHED="KYTY_GATE_SCHEDULE=300+1800:burn=0|burn=502000|burn=602000|burn=702000"; EXTRA=""; RECARG="--rec"; SD="--stable-draws 300 --timeout 480";;
  e*) SEALED=0; HOLD=120; ATT=3; SCHED=""; EXTRA=""; RECARG="--rec"; SD="--stable-draws 300 --timeout 480";;
  skym122) echo "skym122 left the map (ROADMAP s.122 item 13 (b): csky122 read burn_s_main = 0) - refused"; exit 2;;
  skyp122) SEALED=1; HOLD=300; ATT=1; SCHED="KYTY_GATE_SCHEDULE=90+1800:burn=0|burn=802000"; EXTRA="KYTY_GATE_SCHEDULE_ABBA=1"; RECARG=""; SD="--stable-draws 300 --timeout 480";;
  *) SEALED=1; HOLD=300; ATT=1; SCHED="KYTY_GATE_SCHEDULE=90+1800:burn=0|burn=102000"; EXTRA="KYTY_GATE_SCHEDULE_ABBA=1"; RECARG=""; SD="--stable-draws 300 --timeout 480";;
esac
L=/c/kyty/s122/go122a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=2baf8742676255fefd37c72f727e6c27c024be9b67d3afa987bed7fe334af86b
PINNED=/c/kyty/s122/kyty_emulator_2baf8742.exe
GAME="/c/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
GATES=C:/kyty/s122/gates_base.txt
PRED=pred/01_map122.md
SC=map122.py
cd /c/kyty/s122
# 2026-09-26: the agent shell inherits an environment WITHOUT %ProgramFiles%; nvml.dll then fails to
# initialise ("Failed to initialize NVML: Unknown Error") while Vulkan keeps working.  Restoring the
# variable is the whole fix (bisected; the user's own shell has it and nvidia-smi works there).
# Exported here so the nvidia-smi clock logger started by enter_scene.py inherits it as well.
export ProgramFiles="${ProgramFiles:-C:\Program Files}"
export ProgramData="${ProgramData:-C:\ProgramData}"
export LOCALAPPDATA="${LOCALAPPDATA:-$USERPROFILE\AppData\Local}"
export APPDATA="${APPDATA:-$USERPROFILE\AppData\Roaming}"
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
guards() {
  python C:/kyty/s122/procload.py --wait-s "$1" >> $L 2>&1 || { log "a process stays busy (or the mutation harness lives) - not starting"; return 1; }
  BUSY=$(powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'mut_map122|test_map122|mutlib' -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r')
  if [ -z "$BUSY" ] || [ "$BUSY" != "0" ]; then log "a mutant/fixture process lives ($BUSY) - not starting"; return 1; fi
  return 0
}
log "go122a.sh $T requested (level $LEVEL, sealed $SEALED)"
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
guards 1800 || exit 1
PREDARG=""
if [ "$SEALED" = "1" ]; then
  NSHA=$(sha256sum $PRED | cut -c1-64)
  PSHA=$(grep -o "^PRED_SHA = '[0-9a-f]*'" $SC | cut -d"'" -f2)
  if [ -z "$PSHA" ] || [ "$PSHA" != "$NSHA" ]; then log "pred sha $NSHA != $SC PRED_SHA '$PSHA' - not starting"; exit 1; fi
  PREDARG="--pred C:/kyty/s122/$PRED"
  if ! python C:/kyty/s122/chk_map122.py --tag $BASE >> $L 2>&1; then
    log "chk_map122 refused the pre-seal check (see above) - not starting"; exit 1
  fi
fi
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ "$CPU" -ge 15 ]; then log "machine not idle (cpu='$CPU') - not starting"; exit 1; fi
SMIARG=""
case "$GPU" in
  ''|*[!0-9]*)
    # NVML answers again since ProgramFiles is exported above; a run without a numeric GPU sample is
    # refused for every tag, sealed or not (the substitution of 2026-09-26 is withdrawn).
    log "no numeric GPU utilisation ($GPU) - not starting; is ProgramFiles exported? see FACTS.md 4"
    exit 1;;
    # 2026-09-26: NVML is down on this machine ("Failed to initialize NVML"), Vulkan is not.  A SEALED run refuses:
    # its admission needs gpuclk_<tag>.csv and the throttle mask.  An UNSEALED smoke may go on with the substitute
    # census below; the substitution is logged, and no smoke number enters a verdict (ROADMAP s. 122 item 7).
  *)
    if [ "$GPU" -ge 10 ]; then log "machine not idle (gpu=$GPU) - not starting"; exit 1; fi;;
esac
guards 0 || exit 1
set -o noclobber
if ! { echo "go122a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  log "lock taken by someone else: $(cat $LOCK 2>/dev/null) - not starting"; exit 1
fi
set +o noclobber
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$PINNED" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
cp "$PINNED" "$GAME"
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
if [ "$SEALED" = "1" ]; then
  log "files: $(sha256sum $SC test_${SC} mut_${SC} gates_base.txt enter_scene.py procload.py hostdev122.py $PRED | cut -c1-16,65- | tr '\n' ';')"
fi
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" "rec_$T.mp4" "rec_$T.mp4.idx" "hostdev_$T.txt" \
         log_${T}_a*.txt stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
mkdir -p runs122
log "$T start (level $LEVEL, hold $HOLD)"
if [ -n "$SCHED" ]; then
  python C:/kyty/s122/enter_scene.py $T --level $LEVEL --attempts $ATT $SD --no-install --gates-file $GATES $PREDARG $RECARG $SMIARG \
    --hold $HOLD "$SCHED" $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
else
  python C:/kyty/s122/enter_scene.py $T --level $LEVEL --attempts $ATT $SD --no-install --gates-file $GATES $RECARG $SMIARG \
    --hold $HOLD KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
fi
log "$T rc=$? $(tail -1 $T.stdout.txt)"
# ROADMAP s.122 item 17 (a): the host-event witness over launched .. finished of $T.json, unpadded; its report is an
# admission input of map122.py (a missing report = NOT CHECKED = not admitted).  Offline: GPU and build untouched.
python C:/kyty/s122/hostdev122.py $T --pad 0 > hostdev_$T.txt 2>&1
log "hostdev $T rc=$? $(grep '^VERDICT:' hostdev_$T.txt | head -1)"
log "done"
