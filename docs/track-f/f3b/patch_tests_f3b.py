# F3b (HPP-340): splice the B1b cases and the --fix-b1b-only mode into tests/ShaderRecompilerComputeTests.cpp.
# Whole-line anchors; CRLF-safe; writes bytes.
import os, sys

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
NL = chr(10)
P = "C:/kyty/KytyPS5/tests/ShaderRecompilerComputeTests.cpp"
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
lines = raw.decode("utf-8").replace("\r\n", NL).split(NL)


def frag(name):
    return open("C:/kyty/f287/f3b/" + name, "rb").read().decode("utf-8").replace("\r\n", NL).rstrip(NL).split(NL)


def at(anchor):
    hits = [i for i, l in enumerate(lines) if l == anchor]
    assert len(hits) == 1, (anchor, len(hits))
    return hits[0]


assert not any("--fix-b1b-only" in l for l in lines), "already patched"
i = at("TestCase VectorVop3CompareEqI64OnGpu() {")
lines[i:i] = frag("tests_cases_f3b.cpp.txt") + ["", ""]
j = at('  if (argc == 3 && std::strcmp(argv[1], "--b26-pass") == 0) {')
lines[j:j] = frag("tests_main_f3b.cpp.txt")
out = NL.join(lines)
if crlf:
    out = out.replace(NL, "\r\n")
open(P, "wb").write(out.encode("utf-8"))
print("patched tests", "crlf" if crlf else "lf")
print("ALL OK")
