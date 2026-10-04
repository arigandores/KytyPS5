@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d "%~dp0"
clang-cl /nologo /std:c++latest /O2 /EHsc race_demo.cpp /Fe:race_demo.exe || exit /b 1
echo COMPILED
