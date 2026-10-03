@echo off
rem F10c (HPP-451, ROADMAP s122 item 369(v)(1)): copy of the F10a build_f10a.cmd for sval_f10c.exe - the same compiler, flags and
rem SPIRV-Tools static library of the emulator build tree; plus the include path of the F10c worktree for common/envFlag.h.
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set "LLVM=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\Llvm\x64\bin"
cd /d C:\kyty\f287\f10c || exit /b 1
"%LLVM%\clang-cl.exe" /nologo /EHsc /utf-8 /O2 /DNDEBUG -std:c++20 -MD -DFMT_HEADER_ONLY ^
  -IC:\kyty\KytyPS5\3rdparty\fmt\include -IC:\kyty\KytyPS5\3rdparty\SPIRV-Tools\include -IC:\kyty\f287\f10c\wt\src ^
  sval_f10c.cpp -fuse-ld=lld /Fe:sval_f10c.exe ^
  /link C:\kyty\build\3rdparty\SPIRV-Tools\source\SPIRV-Tools.lib || exit /b 1
echo BUILD OK
