@echo off
rem P23 (HPP-404): builds and runs test_gamepatchfile.cpp against src/loader/gamePatchFile.h and src/kernel/pvar.h of the
rem tree given as %1 (default the P23 worktree); %2 - eboot.bin (default the game's).
setlocal
set "SRC=%~1"
if "%SRC%"=="" set "SRC=C:\kyty\p283\p23\wt"
set "EBOOT=%~2"
if "%EBOOT%"=="" set "EBOOT=C:\kyty\KytyPS5\ps5 em\games\PPSA21564-app\eboot.bin"
set "OUT=%~dp0"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
clang-cl /nologo /std:c++20 /EHsc /O2 /W4 /I "%SRC%\src" "%OUT%test_gamepatchfile.cpp" /Fe"%OUT%test_gamepatchfile.exe" /Fo"%OUT%test_gamepatchfile.obj" || exit /b 1
"%OUT%test_gamepatchfile.exe" "%SRC%" "%EBOOT%"
