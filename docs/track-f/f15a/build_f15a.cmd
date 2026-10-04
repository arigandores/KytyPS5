@echo off
rem F15a (HPP-491, ROADMAP s122 item 400(d)(2)): copy of docs/track-f/f14a/build_f14a.cmd with SRC/BUILD set to f15a
rem (worktree on main, Release, the same flags as C:\kyty\build_local.cmd; FetchContent sources of C:\kyty\build, no network).
rem C:\kyty\build and its install directory are not touched.
rem Usage: build_f15a.cmd [configure] [version] [tests] [target <name>]
setlocal
set "SRC=C:\kyty\f287\f15a\wt"
set "BUILD=C:\kyty\f287\f15a\build"
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
if "%1"=="version" (
  cmake --build "%BUILD%" --target KytyGitVersion || exit /b 1
  exit /b 0
)
if "%1"=="tests" (
  cmake --build "%BUILD%" --target shader_cfg_tests --parallel || exit /b 1
  echo BUILD OK: %BUILD%\shader_cfg_tests.exe
  exit /b 0
)
if "%1"=="target" (
  cmake --build "%BUILD%" --target %2 --parallel || exit /b 1
  echo BUILD OK: %BUILD%\%2.exe
  exit /b 0
)
echo F15a builds only test targets
exit /b 2
