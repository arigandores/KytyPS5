@echo off
rem FS11b (HPP-715, Red Team, ROADMAP s122 item 647(g) H3): build and run the size probe h3_size.cpp.
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d C:\kyty\f287\fs11b
clang-cl /nologo /O2 /EHsc h3_size.cpp /Feh3_size.exe || exit /b 1
h3_size.exe
