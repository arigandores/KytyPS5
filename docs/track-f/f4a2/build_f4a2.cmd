@echo off
rem F4a2 (HPP-346, ROADMAP p.262(v)): Release build of kyty_emulator from the worktree C:\kyty\f287\f4a2\wt
rem (4fc501f4 + 1713a8be + 65a09c82) into C:\kyty\f287\f4a2\build - the same flags as C:\kyty\build_local.cmd; the two
rem FetchContent sources are the already fetched ones of C:\kyty\build (same pinned revisions, no network); a copy of
rem C:\kyty\s288\s5c\build_s5c.cmd with the two paths changed.
rem GIT_EXECUTABLE: the real git (the agent PATH has a wrapper that leaves the version strings "unknown").
rem Usage: build_f4a2.cmd [configure] [version] [tests]
setlocal
set "SRC=C:\kyty\f287\f4a2\wt"
set "BUILD=C:\kyty\f287\f4a2\build"
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
cmake --build "%BUILD%" --target kyty_emulator --parallel || exit /b 1
cmake --install "%BUILD%" --prefix "%BUILD%\install" || exit /b 1
echo BUILD OK: %BUILD%\install\kyty_emulator.exe
