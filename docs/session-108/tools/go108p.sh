#!/bin/bash
# Session 108, ROADMAP §0.1 "СЕССИЯ 108" item 7: the guard with power - compute precache off
# (KYTY_PIPELINE_PRECACHE=gfx), Sky Garden 300 s, pinned: sf108c (cspfam=0) then sf108d (default 4).
# Installed build fc78c564.  Holds the sealed-run lock.
L=/c/kyty/s108/go108p.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s108
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go108p.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
for pair in "sf108c gates_fam0.txt" "sf108d gates_base.txt"; do
  set -- $pair
  log "$1 start ($2)"
  python C:/kyty/s108/enter_scene.py $1 --hold 300 --attempts 1 --no-install \
    --gates-file C:/kyty/s108/$2 KYTY_PIPELINE_PRECACHE=gfx KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $1.stdout.txt 2>&1
  log "$1 rc=$? $(tail -1 $1.stdout.txt)"
done
log "done"
