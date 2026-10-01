@echo off
rem F4a2 (HPP-346): build proof_f4a2.exe with the emulator's compiler; %1 = source tree root (src parent).
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d C:\kyty\f287\f4a2 || exit /b 1
clang-cl /nologo /std:c++20 /O2 /EHsc /W4 /I "%~1\src" proof_f4a2.cpp /Fe:proof_f4a2.exe || exit /b 1
echo PROOF BUILD OK
