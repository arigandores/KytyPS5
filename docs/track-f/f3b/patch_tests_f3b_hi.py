# F3b (HPP-340): BVH64 test case - the high dword of the node pointer comes from a buffer load (a runtime value),
# so the native emitter does not take the instruction for a 32-bit one (spirvEmitterMemory.cpp: node64 is decided
# by "arg 1 is not the immediate 0"). Whole-line anchors; CRLF preserved; output written with write_bytes.
import sys

PATH = "C:/kyty/KytyPS5/tests/ShaderRecompilerComputeTests.cpp"
raw = open(PATH, "rb").read()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
lines = text.split("\n")


def replace_block(old, new):
    global lines
    n = len(old)
    hits = [i for i in range(len(lines) - n + 1) if lines[i:i + n] == old]
    if len(hits) != 1:
        print("anchor hits", len(hits), "for", old[0])
        sys.exit(1)
    i = hits[0]
    lines = lines[:i] + new + lines[i + n:]


replace_block(
    [
        "  if (node64) {",
        "    // 64-bit node pointer: the node address is the pointer itself (<< 3), the base is not used.",
        "    const uint64_t pointer = ((B1bBvhBase + 0x100u) >> 3u) | 5u;",
        "    AppendVMovU32(&code, vgpr++, static_cast<u32>(pointer));",
        "    AppendVMovU32(&code, vgpr++, static_cast<u32>(pointer >> 32u));",
        "  } else {",
    ],
    [
        "  if (node64) {",
        "    // 64-bit node pointer: the node address is the pointer itself (<< 3), the base is not used.",
        "    // The high dword (0 here) is loaded from dword 0 of the buffer, a runtime value: the native",
        "    // emitter takes an instruction whose high dword is the immediate 0 for the 32-bit form.",
        "    const uint64_t pointer = ((B1bBvhBase + 0x100u) >> 3u) | 5u;",
        "    static_assert((((B1bBvhBase + 0x100u) >> 3u) >> 32u) == 0u, \"the loaded high dword is 0\");",
        "    AppendVMovU32(&code, vgpr++, static_cast<u32>(pointer));",
        "    AppendVMovU32(&code, 30, 0u);",
        "    AppendBufferLoadDword(&code, vgpr++, 30);",
        "  } else {",
    ],
)

replace_block(
    [
        "  test.opcodes = {O::S_MOV_B32, O::V_MOV_B32,",
        "                  node64 ? O::IMAGE_BVH64_INTERSECT_RAY : O::IMAGE_BVH_INTERSECT_RAY,",
        "                  O::BUFFER_STORE_DWORD, O::S_ENDPGM};",
    ],
    [
        "  test.opcodes = {O::S_MOV_B32, O::V_MOV_B32,",
        "                  node64 ? O::IMAGE_BVH64_INTERSECT_RAY : O::IMAGE_BVH_INTERSECT_RAY,",
        "                  O::BUFFER_STORE_DWORD, O::S_ENDPGM};",
        "  if (node64) {",
        "    test.opcodes.push_back(O::BUFFER_LOAD_DWORD);",
        "  }",
    ],
)

out = "\n".join(lines)
if crlf:
    out = out.replace("\n", "\r\n")
open(PATH, "wb").write(out.encode("utf-8"))
print("patched, crlf =", crlf)
