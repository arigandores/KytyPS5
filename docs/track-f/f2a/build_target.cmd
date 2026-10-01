@echo off
rem F2a (HPP-307): build one test target in the same tree as build_local.cmd (cmake --build only, no configure).
rem Usage: build_target.cmd <target>
setlocal
set "BUILD=C:\kyty\build"
set "PATH=C:\kyty\tools\glslang\bin;C:\Program Files\CMake\bin;%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cmake --build "%BUILD%" --target %1 --parallel || exit /b 1
echo BUILD OK: %BUILD%\%1.exe
