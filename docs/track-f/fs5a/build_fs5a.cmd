@echo off
rem FS5a (HPP-509, ROADMAP s122 item 410(g)(1)): copy of build_fs4a.cmd with SRC/BUILD set to fs5\fs5a and the "target <name>"
rem argument of build_f12d.cmd (for shader_recompiler_compute_tests). Was:
rem FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): copy of build_fs3a.cmd with SRC/BUILD set to fs4\fs4a. Was:
rem FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): copy of build_f9e2c.cmd with SRC/BUILD set to fs3\fs3a. Was:
rem F9e2 (HPP-426, ROADMAP s122 item 351(v)(4)): Release build of kyty_emulator from a worktree - the same flags as
rem C:\kyty\build_local.cmd; the two FetchContent sources are the already fetched ones of C:\kyty\build (no network).
rem GIT_EXECUTABLE: the real git (the agent PATH has a wrapper that leaves the version strings "unknown").
rem Usage: build_fs5a.cmd [configure] [version] [tests] [target <name>]
setlocal
set "SRC=C:\kyty\f287\fs5\fs5a\wt"
set "BUILD=C:\kyty\f287\fs5\fs5a\build"
rem The agent environment has no PROCESSOR_ARCHITECTURE: CMake then detects CMAKE_SYSTEM_PROCESSOR "" and cpuinfo
rem drops its x86 sources (C:\kyty\build has AMD64).
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
cmake --build "%BUILD%" --target kyty_emulator --parallel || exit /b 1
cmake --install "%BUILD%" --prefix "%BUILD%\install" || exit /b 1
echo BUILD OK: %BUILD%\install\kyty_emulator.exe
