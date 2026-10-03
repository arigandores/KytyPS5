@echo off
rem FS4b (HPP-471, Red Team): compile the two fixture programs with the same clang-cl as build_fs4b.cmd (vcvars64), the
rem include root = src of my worktree (3d0e46da). Usage: build_fx.cmd
setlocal
if not defined PROCESSOR_ARCHITECTURE set "PROCESSOR_ARCHITECTURE=AMD64"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d C:\kyty\f287\fs4\fs4b
clang-cl /nologo /std:c++17 /O2 /EHsc /I C:\kyty\f287\fs4\fs4b\wt\src fx_3d0e46da.cpp /Fe:fx_3d0e46da.exe || exit /b 1
clang-cl /nologo /std:c++17 /O2 /EHsc /I C:\kyty\f287\fs4\fs4b\wt\src fx_92d11340.cpp /Fe:fx_92d11340.exe || exit /b 1
echo FX BUILD OK
