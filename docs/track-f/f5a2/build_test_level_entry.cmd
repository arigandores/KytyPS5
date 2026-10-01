@echo off
rem F5a2 (HPP-366): builds and runs test_level_entry.cpp against the header in the tree given as %1 (default C:\kyty\KytyPS5).
setlocal
set "SRC=%~1"
if "%SRC%"=="" set "SRC=C:\kyty\KytyPS5"
set "OUT=%~dp0"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
clang-cl /nologo /std:c++20 /EHsc /O2 /W4 /I "%SRC%\src" "%OUT%test_level_entry.cpp" /Fe"%OUT%test_level_entry.exe" /Fo"%OUT%test_level_entry.obj" || exit /b 1
"%OUT%test_level_entry.exe"
