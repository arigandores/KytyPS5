@echo off
rem FS5b (HPP-510, Red Team): port of my FS4b build_fx.cmd by mk_fx_scripts_fs5b.py. Was:
rem FS4b (HPP-471, Red Team): compile the two fixture programs with the same clang-cl as build_fs4b.cmd (vcvars64), the
rem include root = src of my worktree (0e72bc19). Usage: build_fx.cmd
setlocal
if not defined PROCESSOR_ARCHITECTURE set "PROCESSOR_ARCHITECTURE=AMD64"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d C:\kyty\f287\fs5\fs5b
clang-cl /nologo /std:c++17 /O2 /EHsc /I C:\kyty\f287\fs5\fs5b\wt\src fx_0e72bc19.cpp /Fe:fx_0e72bc19.exe || exit /b 1
clang-cl /nologo /std:c++17 /O2 /EHsc /I C:\kyty\f287\fs5\fs5b\wt\src fx_8a56dc2a.cpp /Fe:fx_8a56dc2a.exe || exit /b 1
echo FX BUILD OK
