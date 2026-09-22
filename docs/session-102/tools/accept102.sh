#!/bin/sh
# Session 102 offline acceptance.  No game launch, retry, replacement or rebuild; never between a
# measurement and its acceptance (the scorers' IDENTITY hashes the exe installed NOW).
#
#   sh C:/kyty/s102/accept102.sh ckpt TAG                 # pred/04, the checkpoints witness
#   sh C:/kyty/s102/accept102.sh dab TAG pilot|decision   # pred/03, the dabatch runs
#
# guards.py and endpoint84.py are REPORTED only (guards checks 3b and 6 fail with nothing else
# running; summary4 cpu_net_us under lite IS cpu_gpu_us).  area_verdict.py is criterion 3 of
# session 101: its INVALID makes this script exit 1 even though dab102.py (which mirrors it) is
# still run so that the score JSON records every control.  The sealed scorers decide; they write
# $R/runs102/<TAG>_score.json and never overwrite it.
# accept101.sh (and older) carry their own roots inside: do not run them.
set -u
R=C:/kyty/s102
export PYTHONIOENCODING=utf-8
CMD=${1:?usage: accept102.sh ckpt TAG | accept102.sh dab TAG pilot|decision}
TAG=${2:?usage: accept102.sh ckpt TAG | accept102.sh dab TAG pilot|decision}
case "$CMD" in
  ckpt)
    mkdir -p "$R/runs102"
    echo '1. guards (reported only; a plain run without a schedule)'
    python "$R/guards.py" "$TAG" --first-frame 2100
    echo '2. endpoint84 (reported only; one arm, no pairs)'
    python "$R/endpoint84.py" "$TAG" --counters rec_n,gpu_busy_us
    echo '3. the sealed witness scorer (pred/04 2 items 1-6; cm101a printed as the A arm, never deciding)'
    python "$R/ckpt102.py" "$TAG" --out "$R/runs102/${TAG}_score.json" || exit 1
    ;;
  dab)
    PHASE=${3:?usage: accept102.sh dab TAG pilot|decision}
    case "$PHASE" in pilot|decision) ;; *) echo 'unknown phase (pilot|decision)'; exit 2 ;; esac
    mkdir -p "$R/runs102"
    echo '1. guards (reported only; checks 3b and 6 are not criteria of this rule)'
    python "$R/guards.py" "$TAG" --first-frame 2100
    echo '2. area (criterion 3 of session 101)'
    python "$R/area_series.py" "$TAG" || exit 1
    python "$R/area_verdict.py" "$TAG"
    AREA=$?
    echo '3. summary4 --blocks and endpoint84 (reported only)'
    python "$R/summary4.py" "$TAG" --blocks || exit 1
    python "$R/endpoint84.py" "$TAG" \
      --counters da_qcall,da_queue_us,da_walk_us,da_walks,da_req,da_nohint,da_hit,da_miss,da_late,da_busy,rec_n,gpu_busy_us \
      || exit 1
    echo "4. the sealed dabatch scorer (pred/03, phase $PHASE)"
    if [ "$PHASE" = 'decision' ]; then
      python "$R/dab102.py" "$TAG" --phase decision --out "$R/runs102/${TAG}_score.json" \
        --pilot-score "${PILOT_SCORE:-$R/runs102/dab102a_score.json}"
      SCORE=$?
    else
      python "$R/dab102.py" "$TAG" --phase pilot --out "$R/runs102/${TAG}_score.json"
      SCORE=$?
    fi
    if [ "$AREA" -ne 0 ]; then
      echo 'area_verdict.py: INVALID - the run may not be quoted, whatever the scorer printed'
      exit 1
    fi
    [ "$SCORE" -eq 0 ] || exit 1
    ;;
  *)
    echo 'unknown command (ckpt|dab)'
    exit 2
    ;;
esac
