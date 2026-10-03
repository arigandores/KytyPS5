#!/bin/bash
# Track F link F12f (HPP-480): run rd_cs_f12f.py on one capture with a watchdog (form of the rd_list block of go_f13a.sh).
# usage: bash rdcs_f12f.sh <capture.rdc> <out.txt> [watchdog_s]
# The marks are the =0 SPIR-V of 380bb9d636390bae of F12d section 5 (native perm 0/1, native perm 2, IR perm 0/1, IR perm 2).
# EXIT: 0 'done' in the output; 1 no 'done' (watchdog, failure); 2 usage.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
CAP=${1:-}; OUTF=${2:-}; WMAX=${3:-540}
[ -n "$CAP" ] && [ -n "$OUTF" ] || { echo "usage: rdcs_f12f.sh <capture.rdc> <out.txt> [watchdog_s]"; exit 2; }
RDHOME="/c/Program Files/RenderDoc"
MARKS=3e034e543b3c8d5cac27a617bcc2c0ac6282f71556b8c5cbdf2122daf305d6f6,c30f0c0f86b11bf18f9e4ce7932b888ecf2cac8affb01c86925cbe6ef118d825,9099e4268d3db232aa7a51a00d9f1b8e331648d3f2c25bcec16d3cd9dc37001e,b5fdfdfae35384dfe019dd1eb8406a8ea2e3549abb42fb032a118d8443c2522e
rm -f "$OUTF"
RD_CAP="$CAP" RD_OUT="$OUTF" RD_MARK="$MARKS" "$RDHOME/qrenderdoc.exe" --python C:/kyty/f287/f12f/rd_cs_f12f.py > "$OUTF.qrd.txt" 2>&1 &
QP=$!
WS=0
while kill -0 $QP 2>/dev/null; do
  if grep -q '^done' "$OUTF" 2>/dev/null; then sleep 15; break; fi
  if [ $WS -ge $WMAX ]; then echo "watchdog $WMAX s expired"; break; fi
  sleep 5; WS=$((WS+5))
done
if kill -0 $QP 2>/dev/null; then taskkill //F //IM qrenderdoc.exe > /dev/null 2>&1; echo "qrenderdoc still alive - taskkill"; fi
wait $QP 2>/dev/null
echo "rdcs end after ~$WS s: $(grep '^SUMMARY' "$OUTF" 2>/dev/null)"
grep -q '^done' "$OUTF" 2>/dev/null || exit 1
exit 0
