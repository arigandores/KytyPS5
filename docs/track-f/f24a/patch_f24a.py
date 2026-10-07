# F24a (HPP-658, ROADMAP s122 item 593(d)(1)): test-build hooks of RegionManager::ChangeState<Cpu, true> for the B13
# stand, and the CMake targets of the B13 and B27 stands. Usage: python patch_f24a.py <repo root>
# Whole-line anchors; LF files are kept LF (CR is stripped before the search and put back if the file had it).
import sys

root = sys.argv[1].rstrip("/")


def patch(rel, edits):
    path = root + "/" + rel
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    lines = text.split("\n")
    for anchor, new_lines, where in edits:
        anchor_lines = anchor.split("\n")
        hits = [i for i in range(len(lines) - len(anchor_lines) + 1)
                if lines[i:i + len(anchor_lines)] == anchor_lines]
        if len(hits) != 1:
            sys.exit("anchor hits %d in %s: %r" % (len(hits), rel, anchor_lines[0]))
        i = hits[0]
        if where == "replace":
            lines[i:i + len(anchor_lines)] = new_lines
        elif where == "after":
            lines[i + len(anchor_lines):i + len(anchor_lines)] = new_lines
        elif where == "before":
            lines[i:i] = new_lines
        else:
            sys.exit("bad where")
    out = "\n".join(lines)
    if crlf:
        out = out.replace("\n", "\r\n")
    open(path, "wb").write(out.encode("utf-8"))
    print("patched", rel)


T = "\t"

patch("src/graphics/host_gpu/regionManager.h", [
    ("namespace Libs::Graphics {", [
        "",
        "// Track F, F24a (B13 stand, ROADMAP s122 item 593(d)(1)): test-build hooks of ChangeState<Cpu, true>. Hook() is",
        "// defined only by tests/B13EpochStand.cpp (CMake targets b13_epoch_stand*, KYTY_TEST_B13_HOOK); every hook and the",
        "// reversed order (KYTY_TEST_B13_SWAP) are inside #if blocks, so the emulator compiles the text before F24a.",
        "#if defined(KYTY_TEST_B13_HOOK)",
        "namespace B13Test {",
        "void Hook(int point) noexcept;",
        "} // namespace B13Test",
        "#endif",
    ], "after"),
    (T * 3 + "m_cpu_epoch.fetch_add(1, std::memory_order_release);\n" +
     T * 3 + "m_epoch.fetch_add(1, std::memory_order_release);", [
        "#if defined(KYTY_TEST_B13_SWAP)",
        T * 3 + "// Track F, F24a: the reversed order (region epoch first), test build only - the control arm of the stand.",
        T * 3 + "m_epoch.fetch_add(1, std::memory_order_release);",
        T * 3 + "B13Test::Hook(1);",
        T * 3 + "m_cpu_epoch.fetch_add(1, std::memory_order_release);",
        "#else",
        T * 3 + "m_cpu_epoch.fetch_add(1, std::memory_order_release);",
        "#if defined(KYTY_TEST_B13_HOOK)",
        T * 3 + "B13Test::Hook(1); // Track F, F24a: between the global and the region epoch",
        "#endif",
        T * 3 + "m_epoch.fetch_add(1, std::memory_order_release);",
        "#endif",
    ], "replace"),
    (T * 3 + "// Gate \"bdabits\": the map mirrors this epoch, so it is set here and never later.", [
        "#if defined(KYTY_TEST_B13_HOOK)",
        T * 3 + "B13Test::Hook(2); // Track F, F24a: after both epochs, before the bdabits bit",
        "#endif",
    ], "before"),
])

patch("CMakeLists.txt", [
    ("target_include_directories(memory_tracker_tests PRIVATE ${inc_headers})", [
        "",
        "# Track F, F24a (HPP-658, ROADMAP s122 item 593(d)(1)): the B13 epoch-order stand (tests/B13EpochStand.cpp) with the",
        "# test-build hooks of RegionManager::ChangeState - the order of the code (b13_epoch_stand) and the reversed order",
        "# (b13_epoch_stand_swap, KYTY_TEST_B13_SWAP); the B27 daslot protocol stand (tests/B27DaSlotStand.cpp). Run by",
        "# docs/track-f/f24a/run_stand_f24a.py, not by ctest.",
        "foreach(b13_target b13_epoch_stand b13_epoch_stand_swap)",
        "\tadd_executable(${b13_target} EXCLUDE_FROM_ALL",
        "\t\t\"${KYTY_TESTS_DIR}/B13EpochStand.cpp\"",
        "\t\t\"${KYTY_SOURCE_DIR}/graphics/host_gpu/pageManager.cpp\"",
        "\t\t\"${KYTY_SOURCE_DIR}/graphics/host_gpu/memoryTracker.cpp\"",
        "\t)",
        "\ttarget_link_libraries(${b13_target} fmt::fmt common)",
        "\ttarget_include_directories(${b13_target} PRIVATE ${inc_headers})",
        "\ttarget_compile_definitions(${b13_target} PRIVATE KYTY_TEST_B13_HOOK=1)",
        "endforeach()",
        "target_compile_definitions(b13_epoch_stand_swap PRIVATE KYTY_TEST_B13_SWAP=1)",
        "",
        "add_executable(b27_daslot_stand EXCLUDE_FROM_ALL",
        "\t\"${KYTY_TESTS_DIR}/B27DaSlotStand.cpp\"",
        ")",
        "target_link_libraries(b27_daslot_stand common)",
        "target_include_directories(b27_daslot_stand PRIVATE ${inc_headers})",
    ], "after"),
])
