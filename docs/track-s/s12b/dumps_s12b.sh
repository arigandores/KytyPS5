#!/bin/bash
# S12b (HPP-495, Red Team): PDB dumps for sc_s12b.py / shift_s12b.py / outside_s12b.py, and the S-pcw init lambdas.
# Usage: bash dumps_s12b.sh <work dir>; every step < 60 s (general rule 30); lock check first.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
W="$1"
L="/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/Llvm/x64/bin"
P12=C:/kyty/s288/s12a/build/kyty_emulator.pdb
P5=C:/kyty/f287/fs5/fs5a/build/kyty_emulator.pdb
"$L/llvm-pdbutil.exe" dump -publics "$P12" > "$W/pub_s12.txt" || exit 1
"$L/llvm-pdbutil.exe" dump -publics "$P5" > "$W/pub_fs5.txt" || exit 1
"$L/llvm-pdbutil.exe" dump -section-contribs "$P12" > "$W/sc_s12.txt" || exit 1
"$L/llvm-pdbutil.exe" dump -section-contribs "$P5" > "$W/sc_fs5.txt" || exit 1
"$L/llvm-pdbutil.exe" dump -modules "$P12" | grep -E "^Mod 0(720|826) " > "$W/mods.txt"
"$L/llvm-pdbutil.exe" dump -modules "$P5" | grep -E "^Mod 0(720|826) " >> "$W/mods.txt"
for r in 0x1408a7d60 0x1408a7e00; do
  e=$(printf '0x%x' $((r + 46)))
  "$L/llvm-objdump.exe" -d --no-show-raw-insn --start-address=$r --stop-address=$e C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe | tail -n +7
done > "$W/lambdas.txt"
"$L/llvm-objdump.exe" -d --no-show-raw-insn --start-address=0x140870000 --stop-address=0x1408e0000 C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe | grep -E "callq\s+0x1408a7(d60|e00)" > "$W/lambda_calls.txt"
sha256sum "$P12" "$P5" C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe C:/kyty/f287/bin/kyty_emulator_631ff987.exe C:/kyty/s288/s12a/build/install/kyty_emulator.exe > "$W/sha_s12b.txt"
echo DUMPS OK
