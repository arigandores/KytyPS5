@echo off
rem FS2a (HPP-381, ROADMAP p.298(v)): Release build of kyty_emulator from the worktree C:\kyty\f287\fs2a\wt
rem (main 9c9d86ae, LF) into C:\kyty\f287\fs2a\build - the same flags as C:\kyty\build_local.cmd; the two
rem FetchContent sources are the already fetched ones of C:\kyty\build (same pinned revisions, no network); a copy of
rem C:/kyty/f287/fsa/build_fsa.cmd with the two paths changed and audio_propagation_tests added to "tests" (as build_f6c.cmd).
rem GIT_EXECUTABLE: the real git (the agent PATH has a wrapper that leaves the version strings "unknown").
rem Usage: build_fsa.cmd [configure] [version] [tests]
setlocal
set "SRC=C:\kyty\f287\fs2a\wt"
set "BUILD=C:\kyty\f287\fs2a\build"
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
  cmake --build "%BUILD%" --target audio_propagation_tests shader_cfg_tests --parallel || exit /b 1
  echo BUILD OK: %BUILD%\audio_propagation_tests.exe %BUILD%\shader_cfg_tests.exe
  exit /b 0
)
cmake --build "%BUILD%" --target kyty_emulator --parallel || exit /b 1
cmake --install "%BUILD%" --prefix "%BUILD%\install" || exit /b 1
echo BUILD OK: %BUILD%\install\kyty_emulator.exe
