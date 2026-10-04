@echo off
rem F14f2 (HPP-546, ROADMAP s122 item 443(g)): own build of shader_cfg_tests from the own worktree C:\kyty\f287\f14f2\wt
rem into C:\kyty\f287\f14f2\build. Copy of C:\kyty\f287\f14e2\build_f14e2.cmd with SRC/BUILD set to f14f2 (same flags as
rem C:\kyty\build_local.cmd; FetchContent sources of C:\kyty\build, no network). Usage: build_f14f2.cmd [configure] [tests]
setlocal
set "SRC=C:\kyty\f287\f14f2\wt"
set "BUILD=C:\kyty\f287\f14f2\build"
if not defined PROCESSOR_ARCHITECTURE set "PROCESSOR_ARCHITECTURE=AMD64"
set "PATH=C:\kyty\tools\glslang\bin;C:\Program Files\CMake\bin;%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
if "%1"=="configure" (
  cmake -S "%SRC%" -B "%BUILD%" -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON ^
    -DKYTY_BUILD_LAUNCHER=OFF ^
    -DKYTY_BUILD_ORIGIN=Fork ^
    -DKYTY_BUILD_REPOSITORY=arigandores/KytyPS5 ^
    -DKYTY_RELEASE_TAG=local ^
    -DFETCHCONTENT_SOURCE_DIR_XBYAK=C:/kyty/build/_deps/xbyak-src ^
    -DFETCHCONTENT_SOURCE_DIR_ZYDIS=C:/kyty/build/_deps/zydis-src ^
    -DCMAKE_C_COMPILER=clang-cl ^
    -DCMAKE_CXX_COMPILER=clang-cl ^
    "-DGIT_EXECUTABLE=C:/Program Files/Git/cmd/git.exe" || exit /b 1
  exit /b 0
)
if "%1"=="tests" (
  cmake --build "%BUILD%" --target shader_cfg_tests --parallel || exit /b 1
  echo BUILD OK: %BUILD%\shader_cfg_tests.exe
  exit /b 0
)
echo usage: build_f14f2.cmd configure^|tests
exit /b 2
