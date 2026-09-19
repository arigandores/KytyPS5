#!/bin/sh
# Offline acceptance only. No game launch, retry, replacement, or rebuild.
# Historical guards/summary are reported. bf99 enforces criterion 3 and its sealed controls.
set -u
TAG=${1:?usage: accept99.sh TAG a\|c [--calibration]}
INSTRUMENT=${2:?instrument a or c required}
MODE=${3:-}
R=C:/kyty/s99
export PYTHONIOENCODING=utf-8
case "$INSTRUMENT" in a|c) ;; *) echo 'unknown instrument'; exit 2 ;; esac
case "$MODE" in ''|--calibration) ;; *) echo 'unknown mode'; exit 2 ;; esac
echo '1. guards (reported; deciding survival/protocol is also enforced by bf99)'
python "$R/guards.py" "$TAG" --first-frame 2100
echo '2. area (criterion 3)'
python "$R/area_series.py" "$TAG" || exit 1
python "$R/area_verdict.py" "$TAG" || exit 1
if [ "$MODE" != '--calibration' ]; then
  echo '3. historical summary4 and endpoint84 (reported only)'
  python "$R/summary4.py" "$TAG" --blocks || exit 1
  python "$R/endpoint84.py" "$TAG" || exit 1
fi
echo '4. own process controls, reversibility and mode2 endpoint'
if [ "$MODE" = '--calibration' ]; then
  python "$R/bf99.py" "$TAG" --instrument "$INSTRUMENT" --calibration || exit 1
else
  python "$R/bf99.py" "$TAG" --instrument "$INSTRUMENT" || exit 1
fi
echo '5. identities included in bf99: C3, C4_B, R3/R4/R8 and live darkness'
