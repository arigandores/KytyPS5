@echo off
rem P23 (HPP-404, ROADMAP s122 p.333(e)): Release build of kyty_emulator from the worktree C:\kyty\p283\p23\wt
rem (main 827fcef4 = FS2a 9c9d86ae outside docs/, + P-var port 0d98550d + loader 4414e235, LF) into C:\kyty\p283\p23\build -
rem a copy of C:\kyty\f287\fs2a\build_fs2a.cmd with the two paths changed: the same flags as C:\kyty\build_local.cmd; the two
rem FetchContent sources are the already fetched ones of C:\kyty\build (same pinned revisions, no network).
rem GIT_EXECUTABLE: the real git (the agent PATH has a wrapper that leaves the version strings "unknown").
rem Usage: build_p23.cmd [configure] [version] [tests]
setlocal
set "SRC=C:\kyty\p283\p23\wt"
set "BUILD=C:\kyty\p283\p23\build"
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
