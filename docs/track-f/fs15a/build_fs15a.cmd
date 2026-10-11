@echo off
rem FS15a (HPP-820): copy of the FS14a build_fs14a.cmd (fs14a -> fs15a). Was:
rem FS14a (HPP-812): copy of the FS11a build_fs11a.cmd (fs11a -> fs14a, FS11a -> FS14a, HPP-714 -> HPP-812). Was:
rem FS11a (HPP-714): copy of the FS10a build_fs10a.cmd (fs10a -> fs11a, FS10a -> FS11a, HPP-684 -> HPP-714). Was:
rem FS10a (HPP-684): copy of the FS9a build_fs9a.cmd (fs9a -> fs10a, FS9a -> FS10a, HPP-671 -> HPP-684). Was:
rem FS9a (HPP-671): copy of the FS8a build_fs8a.cmd with SRC/BUILD set to fs9a. Was:
rem FS8a (HPP-571): copy of the FS7a build_fs7a.cmd, paths and names changed. Was:
rem FS8a (HPP-571, ROADMAP s122 items 467(g)(1), 487(g)(1)): copy of build_fs6a.cmd with SRC/BUILD set to fs8a. Was:
rem FS8a (HPP-571, ROADMAP s122 item 454(g)(1)): copy of build_f15c.cmd with SRC/BUILD set to fs8a. Was:
rem F15c (HPP-514, ROADMAP s122 item 412(v)): copy of build_f14e.cmd with SRC/BUILD set to f15c. Was:
rem F14e (HPP-505, ROADMAP s122 items 409(v), 415): copy of build_f12d.cmd with SRC/BUILD set to f14e. Was:
rem F12d (HPP-477, ROADMAP s122 item 391(v)-(g)): copy of build_f11d.cmd with SRC/BUILD set to f12d. Was:
rem F11d (HPP-466, ROADMAP s122 item 376(v)-(d)): copy of build_f10c.cmd with SRC/BUILD set to f11d and a
rem "target <name>" step (any CMake target of the worktree build, e.g. shader_recompiler_compute_tests). Was:
rem F10c (HPP-451, ROADMAP s122 item 369(b)): copy of build_fs3a.cmd with SRC/BUILD set to f10c. Was:
rem FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): copy of build_f9e2c.cmd with SRC/BUILD set to fs3\fs3a. Was:
rem F9e2c (HPP-436, ROADMAP s122 item 357(g)(4)): copy of build_f9e2b.cmd with SRC/BUILD set to f9e2c. Was:
rem F9e2b (HPP-429, ROADMAP s122 item 353(g)(4)): copy of the F9e2 build_f9e2.cmd with SRC/BUILD set to f9e2b. Was:
rem F9e2 (HPP-426, ROADMAP s122 item 351(v)(4)): Release build of kyty_emulator from the worktree C:\kyty\f287\f9\f9e2\wt
rem (4414e235 + the F9e2 commit, LF) into C:\kyty\f287\f9\f9e2\build - a copy of C:\kyty\p283\p30b\build_p30b.cmd with the
rem two paths changed: the same flags as C:\kyty\build_local.cmd; the two FetchContent sources are the already fetched
rem ones of C:\kyty\build (same pinned revisions, no network).
rem GIT_EXECUTABLE: the real git (the agent PATH has a wrapper that leaves the version strings "unknown").
rem Usage: build_f14e.cmd [configure] [version] [tests] [target <name>]
setlocal
set "SRC=C:\kyty\f287\fs15a\wt"
set "BUILD=C:\kyty\f287\fs15a\build"
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
