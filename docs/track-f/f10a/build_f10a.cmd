@echo off
rem F10a (HPP-445): build sval_f10a.exe with the compiler and the SPIRV-Tools static library of the
rem emulator build tree (C:\kyty\build, clang-cl + lld-link, Release flags of SPIRV-Tools-static).
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set "LLVM=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\Llvm\x64\bin"
cd /d C:\kyty\f287\f10a || exit /b 1
"%LLVM%\clang-cl.exe" /nologo /EHsc /utf-8 /O2 /DNDEBUG -std:c++20 -MD -DFMT_HEADER_ONLY ^
  -IC:\kyty\KytyPS5\3rdparty\fmt\include -IC:\kyty\KytyPS5\3rdparty\SPIRV-Tools\include ^
  sval_f10a.cpp -fuse-ld=lld /Fe:sval_f10a.exe ^
  /link C:\kyty\build\3rdparty\SPIRV-Tools\source\SPIRV-Tools.lib || exit /b 1
echo BUILD OK
