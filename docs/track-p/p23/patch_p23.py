# P23 (HPP-404, ROADMAP s122 p.333(d),(g)): hooks of the opt-in patch file KYTY_GAME_PATCH into the ported P-var tree.
# Anchors are whole lines; CR is dropped before matching and the files are written back LF (the worktree is LF).
import sys

WT = sys.argv[1] if len(sys.argv) > 1 else "C:/kyty/p283/p23/wt"


def patch(rel, edits):
    path = WT + "/" + rel
    raw = open(path, "rb").read()
    had_cr = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            sys.exit("anchor count %d in %s: %r" % (n, rel, old[:80]))
        text = text.replace(old, new)
    out = text.replace("\n", "\r\n") if had_cr else text
    open(path, "wb").write(out.encode("utf-8"))
    print("patched", rel, "CRLF" if had_cr else "LF")


patch("src/emulator.cpp", [
    ('#include "loader/runtimeLinker.h"\n',
     '#include "loader/gamePatchFile.h"\n#include "loader/runtimeLinker.h"\n'),
    ("\tMountSandboxDirs();\n\n\tauto* rt = Common::Singleton<Loader::RuntimeLinker>::Instance();\n",
     "\tMountSandboxDirs();\n\n"
     "\t// Track P, KYTY_GAME_PATCH (loader/gamePatchFile.h, ROADMAP s122 item 333(d)): the decision before Libs::InitAll,\n"
     "\t// whose registration reads PVar::Mode(); without the variable nothing is called.\n"
     "\tif (const char* game_patch_file = std::getenv(\"KYTY_GAME_PATCH\");\n"
     "\t    game_patch_file != nullptr && game_patch_file[0] != '\\0') {\n"
     "\t\tLoader::GamePatchFile::Load(\n"
     "\t\t    Libs::LibKernel::FileSystem::GetRealFilename(Common::PathToGenericString(options.elf)));\n"
     "\t}\n\n"
     "\tauto* rt = Common::Singleton<Loader::RuntimeLinker>::Instance();\n"),
])

patch("src/kernel/pvar.cpp", [
    ('#include "kernel/pthread.h"\n',
     '#include "kernel/pthread.h"\n#include "loader/gamePatchFile.h"\n'),
    ("\tstatic const int mode = [] {\n\t\tconst char* value = std::getenv(\"KYTY_PVAR\");\n",
     "\tstatic const int mode = [] {\n"
     "\t\t// Track P, the patch file (loader/gamePatchFile.h, ROADMAP s122 item 333(d)): an applied \"pvar 2\" is mode 2\n"
     "\t\t// (an explicit KYTY_PVAR other than \"2\" refuses the file, so the two never disagree).\n"
     "\t\tif (Loader::GamePatchFile::PvarOn()) {\n"
     "\t\t\treturn 2;\n"
     "\t\t}\n"
     "\t\tconst char* value = std::getenv(\"KYTY_PVAR\");\n"),
])

patch("src/kernel/pthread.cpp", [
    ('#include "loader/runtimeLinker.h"\n#include "loader/timer.h"\n',
     '#include "loader/gamePatchFile.h"\n#include "loader/runtimeLinker.h"\n#include "loader/timer.h"\n'),
    ("bool GuestSpeedEnabled() {\n"
     "\tstatic const bool enabled = [] {\n"
     "\t\tconst char* value = std::getenv(\"KYTY_AUDIO_SYNC\");\n"
     "\t\treturn value == nullptr || std::atoi(value) != 0;\n"
     "\t}();\n"
     "\treturn enabled;\n"
     "}\n",
     "bool GuestSpeedEnabled() {\n"
     "\tstatic const bool enabled = [] {\n"
     "\t\tconst char* value = std::getenv(\"KYTY_AUDIO_SYNC\");\n"
     "\t\treturn value == nullptr || std::atoi(value) != 0;\n"
     "\t}();\n"
     "\t// Track P, the patch file (loader/gamePatchFile.h, ROADMAP s122 item 333(g)): an applied \"audio_sync 0\" turns the\n"
     "\t// guest speed off as KYTY_AUDIO_SYNC=0 does. An atomic flag read on every call, not folded into the static: the\n"
     "\t// window and present threads may read the guest TSC before the file is loaded; false without KYTY_GAME_PATCH.\n"
     "\treturn enabled && !Loader::GamePatchFile::AudioSyncOff();\n"
     "}\n"),
])

patch("src/loader/runtimeLinker.cpp", [
    ('#include "loader/gamePatch.h"\n',
     '#include "loader/gamePatch.h"\n#include "loader/gamePatchFile.h"\n'),
    ("\t// KYTY_POKE=<hex addr>:<hex bytes>[,<addr>:<bytes>...] - write bytes into guest memory before the entry\n",
     "\t// Track P, KYTY_GAME_PATCH (loader/gamePatchFile.h, ROADMAP s122 item 333(d)): the pokes of the applied file, written\n"
     "\t// as the KYTY_POKE loop below writes them (offsets from the main module base), before it; no file - no pokes.\n"
     "\tif (GamePatchFile::Active() && !m_programs.empty()) {\n"
     "\t\tconst auto base = m_programs.front()->base_vaddr;\n"
     "\t\tfor (const auto& poke: GamePatchFile::Pokes()) {\n"
     "\t\t\tconst auto addr = base + poke.offset;\n"
     "\t\t\tfor (size_t i = 0; i < poke.bytes.size(); i++) {\n"
     "\t\t\t\t*reinterpret_cast<uint8_t*>(addr + i) = poke.bytes[i];\n"
     "\t\t\t}\n"
     "\t\t\tLOGF(\"GamePatch: poke 0x%016\" PRIx64 \" <- %s\\n\", addr, poke.hex.c_str());\n"
     "\t\t}\n"
     "\t}\n\n"
     "\t// KYTY_POKE=<hex addr>:<hex bytes>[,<addr>:<bytes>...] - write bytes into guest memory before the entry\n"),
])
print("ALL PATCHED")
