# F24a (HPP-658, ROADMAP s122 item 593(d)(1)): the guard primitives of tests/B27DaSlotStand.cpp between the VERBATIM
# markers must be the text of pipelineCache.cpp (from the line "// Slot guards: the draw gives up" to the closing brace of
# UnguardSlot) at each commit given, line by line with the indentation. Usage: python check_b27_copy.py <stand file>
# <commit> [<commit> ...]
# Prints one line per commit and ALL OK when every commit matches.
import subprocess
import sys

GIT = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
PATH = "src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp"


def stand_block(path):
    lines = open(path, "rb").read().decode("utf-8").replace("\r\n", "\n").split("\n")
    begin = [i for i, l in enumerate(lines) if l.strip() == "// BEGIN VERBATIM pipelineCache.cpp"]
    end = [i for i, l in enumerate(lines) if l.strip() == "// END VERBATIM pipelineCache.cpp"]
    if len(begin) != 1 or len(end) != 1:
        sys.exit("markers not found once")
    # Inside struct Guards the block has the indentation of the struct ProgramCache members: one tab, as in the code.
    return lines[begin[0] + 1:end[0]]


def code_block(commit):
    text = subprocess.run([GIT, "-C", REPO, "show", "%s:%s" % (commit, PATH)], capture_output=True, check=True).stdout
    lines = text.decode("utf-8").replace("\r\n", "\n").split("\n")
    start = [i for i, l in enumerate(lines) if l.startswith("\t// Slot guards: the draw gives up after a bounded spin")]
    if len(start) != 1:
        sys.exit("%s: start anchor hits %d" % (commit, len(start)))
    unguard = [i for i, l in enumerate(lines) if l == "\tstatic void UnguardSlot(AheadSlot& slot) {"]
    if len(unguard) != 1 or unguard[0] < start[0]:
        sys.exit("%s: UnguardSlot anchor hits %d" % (commit, len(unguard)))
    stop = unguard[0]
    while lines[stop] != "\t}":
        stop += 1
    return lines[start[0]:stop + 1], start[0] + 1, stop + 1


def main():
    stand = stand_block(sys.argv[1])
    ok = True
    for commit in sys.argv[2:]:
        code, first, last = code_block(commit)
        same = code == stand
        ok &= same
        print("%s %s:%d-%d lines=%d %s" % (commit, PATH, first, last, len(code), "SAME" if same else "DIFFERENT"))
        if not same:
            for a, b in zip(code, stand):
                if a != b:
                    print("  code : %r" % a)
                    print("  stand: %r" % b)
                    break
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


main()
