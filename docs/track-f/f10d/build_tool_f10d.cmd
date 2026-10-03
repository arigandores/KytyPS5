@echo off
rem F10d (HPP-452, Red Team, ROADMAP s122 item 369(v)(2)): own build of the F10c offline tool for one variant directory.
rem Copy of the F10c build_tool_f10c.cmd: the same compiler, flags and SPIRV-Tools static library of the emulator build tree;
rem the variant directory %1 holds sval_f10c.cpp (byte copy of docs/track-f/f10c/sval_f10c.cpp at 1a588fc2) and its own
rem sval_body_f10c.inc (own extraction from the 68602c4f blob, or a mutant of it); common/envFlag.h from the 68602c4f blob
rem (C:\kyty\f287\f10d\inc). Usage: build_tool_f10d.cmd <variant dir>
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set "LLVM=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\Llvm\x64\bin"
cd /d %1 || exit /b 1
"%LLVM%\clang-cl.exe" /nologo /EHsc /utf-8 /O2 /DNDEBUG -std:c++20 -MD -DFMT_HEADER_ONLY ^
  -IC:\kyty\KytyPS5\3rdparty\fmt\include -IC:\kyty\KytyPS5\3rdparty\SPIRV-Tools\include -IC:\kyty\f287\f10d\inc ^
  sval_f10c.cpp -fuse-ld=lld /Fe:sval.exe ^
  /link C:\kyty\build\3rdparty\SPIRV-Tools\source\SPIRV-Tools.lib || exit /b 1
echo BUILD OK
