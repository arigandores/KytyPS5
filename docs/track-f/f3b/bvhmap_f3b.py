# F3b (HPP-340, ROADMAP p.259(e)(2)): every BVH program of eboot.bin and the form of its BVH descriptor.
# 1. Enumerate embedded AMDGPU ELFs (e_machine 0xe0), take the .shader_text (or .text) section, hash it with XXH3-64.
# 2. Linear decode by the emulator's family/length rules (ShaderDecoder.cpp GetInstructionFamily,
#    VectorAluOps.cpp IsVop2LiteralMadOpcode, ImageOps.cpp DecodeMimg); the decoder is checked against
#    the emulator's own disassembly of 380bb9d636390bae (C:/kyty/f287/f3a/asm_380b.txt, every pc).
# 3. Every IMAGE_BVH(64)_INTERSECT_RAY (MIMG op 0xe6 / 0xe7 = ((w>>18)&0x7f) | ((w&1)<<7)): its
#    SRSRC quad; every write in the program to the base pair s[n], s[n+1] and to s[n+2], s[n+3].
# 4. The 40 S_BFE_U64 ..., 0x00280008 sites of eboot.bin -> owning program.
import sys, os, re, struct, mmap, collections, hashlib, json
import xxhash

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
EBOOT = "C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin"
OUT = "C:/kyty/f287/f3b/"
f = open(EBOOT, "rb")
mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


# ---- 1. ELFs
elfs = []
i = mm.find(b"\x7fELF\x02\x01\x01")
while i != -1:
    if struct.unpack_from("<H", mm, i + 18)[0] == 0xE0:
        elfs.append(i)
    i = mm.find(b"\x7fELF\x02\x01\x01", i + 1)
programs = []
for e in elfs:
    shoff = struct.unpack_from("<Q", mm, e + 0x28)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", mm, e + 0x3A)
    secs = []
    for k in range(shnum):
        b = e + shoff + k * shentsize
        name, typ, flags, addr, off, size = struct.unpack_from("<IIQQQQ", mm, b)
        secs.append((name, typ, off, size))
    if shstrndx >= len(secs):
        continue
    stroff = e + secs[shstrndx][2]
    text = None
    for name, typ, off, size in secs:
        end = mm.find(b"\x00", stroff + name)
        nm = mm[stroff + name:end].decode("latin1")
        if nm in (".text", ".shader_text"):
            text = (e + off, size)
    if text is None:
        continue
    start, size = text
    code = mm[start:start + size]
    programs.append(dict(elf=e, start=start, size=size, hash=xxhash.xxh3_64_intdigest(code)))
p("AMDGPU ELFs in eboot.bin:", len(elfs), "with .text:", len(programs))
p("unique .text hashes:", len({x["hash"] for x in programs}))


# ---- 2. decoder (lengths and the few fields we need)
def sdst_regs(base, count):
    return list(range(base, base + count))


def decode(words):
    out = []
    i = 0
    n = len(words)
    while i < n:
        w = words[i]
        size = 1
        rec = dict(pc=i * 4, fam="?", op=None, writes=[], text="")
        if (w & 0x80000000) == 0:
            fam = {0x3E: "VOPC", 0x3F: "VOP1"}.get((w >> 25) & 0x3F, "VOP2")
            s0 = w & 0x1FF
            if s0 == 255:
                size += 1
            if s0 in (0xF9, 0xFA, 0xE9, 0xEA):
                size += 1 if s0 != 0xEA else 1
            if fam == "VOP2" and ((w >> 25) & 0x3F) in (0x20, 0x21, 0x2C, 0x2D, 0x37, 0x38) and s0 != 255:
                size += 1
            rec["fam"] = fam
        elif (w & 0xC0000000) == 0x80000000:
            op7 = (w >> 23) & 0x7F
            if op7 == 0x7D:
                op = (w >> 8) & 0xFF
                s0 = w & 0xFF
                d = (w >> 16) & 0x7F
                size += 1 if s0 == 255 else 0
                rec.update(fam="SOP1", op=op, dst=d, s0=s0)
                # 64-bit SOP1 ops write two SGPRs (mov_b64, not_b64, brev_b64, bitset*_b64 ...)
                wide = op in (4, 6, 8, 10, 12, 28, 30, 31, 33, 36, 37, 38, 39, 40, 41, 42, 43, 45, 47, 49, 55, 56, 57, 58, 59)
                rec["writes"] = sdst_regs(d, 2 if wide else 1)
                if op in (27, 29):  # s_bitset0/1_b32: read-modify-write of one bit
                    rec["bitop"] = (op, s0)
            elif op7 == 0x7E:
                s0, s1 = w & 0xFF, (w >> 8) & 0xFF
                size += 1 if 255 in (s0, s1) else 0
                rec["fam"] = "SOPC"
            elif op7 == 0x7F:
                rec.update(fam="SOPP", op=(w >> 16) & 0x7F)
            elif op7 >= 0x60:
                op = (w >> 23) & 0x1F
                d = (w >> 16) & 0x7F
                if op == 21:
                    size += 1
                rec.update(fam="SOPK", op=op)
                if op in (0, 2, 15, 16, 18):  # movk, cmovk, addk, mulk, getreg
                    rec["writes"] = [d]
                if op == 22:  # s_call_b64
                    rec["writes"] = [d, d + 1]
            else:
                op = op7
                s0, s1 = w & 0xFF, (w >> 8) & 0xFF
                d = (w >> 16) & 0x7F
                lit = None
                if 255 in (s0, s1):
                    lit = words[i + 1] if i + 1 < n else None
                    size += 1
                wide = op in (11, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 41, 42)
                rec.update(fam="SOP2", op=op, dst=d, s0=s0, s1=s1, lit=lit, writes=sdst_regs(d, 2 if wide else 1))
        else:
            enc = w >> 26
            fam = {0x32: "VINTRP", 0x33: "VOP3P", 0x35: "VOP3", 0x36: "DS", 0x37: "FLAT", 0x38: "MUBUF",
                   0x3A: "MTBUF", 0x3C: "MIMG", 0x3D: "SMEM", 0x3E: "EXP"}.get(enc, "UNKNOWN")
            rec["fam"] = fam
            if fam == "VINTRP":
                size = 1
            elif fam in ("VOP3", "VOP3P"):
                size = 2
                if i + 1 < n:
                    w1 = words[i + 1]
                    srcs = [w1 & 0x1FF, (w1 >> 9) & 0x1FF, (w1 >> 18) & 0x1FF]
                    if 255 in srcs:
                        size = 3
                if fam == "VOP3":
                    op = (w >> 16) & 0x3FF
                    rec["op"] = op
                    # VOP3 writes VGPRs except the VOPC-in-VOP3 forms (op < 0x100) and readlane/readfirstlane
                    d = w & 0xFF
                    if op < 0x80:
                        rec["writes"] = [d]
                    elif op in (0x360,):  # v_readlane_b32 (VOP3 0x360)
                        rec["writes"] = [d]
                    else:
                        sd = (w >> 8) & 0x7F
                        if op in (0x30F, 0x310, 0x319, 0x31A, 0x176, 0x177):  # VOP3B carry-out / div_scale
                            rec["writes"] = [sd]
            elif fam == "MIMG":
                nsa = (w >> 1) & 3
                size = 2 + nsa
                op = ((w >> 18) & 0x7F) | ((w & 1) << 7)
                w1 = words[i + 1] if i + 1 < n else 0
                rec.update(op=op, srsrc=((w1 >> 16) & 0x1F) * 4, ssamp=((w1 >> 21) & 0x1F) * 4, nsa=nsa)
            elif fam == "SMEM":
                size = 2
                op = (w >> 18) & 0xFF
                sdata = (w >> 6) & 0x7F
                cnt = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 8: 1, 9: 2, 10: 4, 11: 8, 12: 16, 36: 2, 37: 2}.get(op, 0)
                rec.update(op=op, writes=sdst_regs(sdata, cnt), sbase=(w & 0x3F) * 2)
            elif fam in ("DS", "FLAT", "MUBUF", "MTBUF", "EXP"):
                size = 2
            else:
                size = 1
        if rec["fam"] == "VOP1" and ((w >> 9) & 0xFF) == 2:  # v_readfirstlane_b32 -> SGPR
            rec["writes"] = [(w >> 17) & 0xFF]
        rec["size"] = size
        rec["words"] = words[i:i + size]
        out.append(rec)
        i += size
    return out


# ---- check the decoder on 380bb9d636390bae against the emulator's disassembly
asm = open("C:/kyty/f287/f3a/asm_380b.txt", "rb").read().decode("latin1")
ref_pcs = [int(m.group(1), 16) for m in re.finditer(r"^0x([0-9a-f]{8}):", asm, re.M)]
target = [x for x in programs if x["hash"] == 0x380BB9D636390BAE]
assert len(target) >= 1, "380b not found among ELF .text"
t = target[0]
words = list(struct.unpack_from("<%dI" % (t["size"] // 4), mm, t["start"]))
mine = decode(words)
my_pcs = [r["pc"] for r in mine]
p("380bb9d636390bae: .text bytes", t["size"], "words", t["size"] // 4, "eboot", hex(t["start"]),
  "decoded", len(mine), "emulator", len(ref_pcs), "pc lists equal:", my_pcs[:len(ref_pcs)] == ref_pcs)
assert my_pcs[:len(ref_pcs)] == ref_pcs, "decoder disagrees with the emulator on 380b"
sys.path.insert(0, OUT)
from reach_f3b import reachable
rmine, rbad = reachable(decode, words)
p("380bb9d636390bae reachable decode:", len(rmine), "instructions, unknown", rbad, "; subset of the emulator pcs:", set(r["pc"] for r in rmine) <= set(ref_pcs),
  "; emulator pcs not reached:", len(set(ref_pcs) - set(r["pc"] for r in rmine)))
assert set(r["pc"] for r in rmine) <= set(ref_pcs)

# ---- 3. all BVH programs
bfe_sites = []
lit = struct.pack("<I", 0x00280008)
i = mm.find(lit)
while i != -1:
    if i % 4 == 0 and i >= 4:
        w = struct.unpack_from("<I", mm, i - 4)[0]
        if (w >> 30) == 2 and ((w >> 23) & 0x7F) == 41 and ((w >> 8) & 0xFF) == 255:
            bfe_sites.append(i - 4)
    i = mm.find(lit, i + 1)
p("S_BFE_U64 ..., 0x00280008 sites in eboot.bin:", len(bfe_sites))

by_hash = collections.OrderedDict()
decode_problems = 0
for prog in programs:
    words = list(struct.unpack_from("<%dI" % (prog["size"] // 4), mm, prog["start"]))
    recs, bad = reachable(decode, words)
    if bad:
        decode_problems += 1
    prog["recs"] = recs
    prog["bvh"] = [r for r in recs if r["fam"] == "MIMG" and r["op"] in (0xE6, 0xE7)]
    prog["bfe"] = [r for r in recs if r["fam"] == "SOP2" and r["op"] == 41 and r.get("lit") == 0x00280008 and r["s1"] == 255]
    prog["bfe_eboot"] = [prog["start"] + r["pc"] for r in prog["bfe"]]
p("programs whose reachable decode meets an UNKNOWN family:", decode_problems)

bvh_progs = [x for x in programs if x["bvh"]]
p("ELF programs with IMAGE_BVH(64)_INTERSECT_RAY:", len(bvh_progs), "unique hashes:", len({x["hash"] for x in bvh_progs}))
mapped = set()
for x in programs:
    mapped.update(x["bfe_eboot"])
p("BFE sites inside some program .text:", len(mapped & set(bfe_sites)), "of", len(bfe_sites),
  "; BFE sites outside any program:", sorted(hex(s) for s in set(bfe_sites) - mapped))
p("BFE sites in programs WITHOUT a BVH instruction:",
  sum(len(x["bfe"]) for x in programs if not x["bvh"]))


def reg(n):
    return "s%d" % n


forms = collections.Counter()
rows = []
for x in bvh_progs:
    recs = x["recs"]
    for b in x["bvh"]:
        q = b["srsrc"]
        defs = {k: [] for k in range(4)}
        for r in recs:
            for k in range(4):
                if q + k in r["writes"]:
                    defs[k].append(r)
        def describe(r):
            if r["fam"] == "SOP2":
                return "SOP2 op%d%s @0x%x" % (r["op"], " lit=0x%08x" % r["lit"] if r.get("lit") is not None else "", r["pc"])
            return "%s op%s @0x%x" % (r["fam"], r["op"], r["pc"])
        base_defs = [describe(r) for r in defs[0]] + [describe(r) for r in defs[1] if r not in defs[0]]
        lo_ok = all(r["fam"] == "SOP2" and r["op"] == 41 and r.get("lit") == 0x00280008 and r["dst"] == q for r in defs[0]) and defs[0]
        # hi dword: written by the same BFE (64-bit) and optionally by s_bitset1_b32 bit 31 (box_sort_en)
        hi_ok = all((r["fam"] == "SOP2" and r["op"] == 41 and r.get("lit") == 0x00280008 and r["dst"] == q) or
                    (r["fam"] == "SOP1" and r.get("bitop") == (29, 128 + 31)) for r in defs[1]) and defs[1]
        form = "addr>>8 (BFE 8,40)" if (lo_ok and hi_ok) else "OTHER"
        forms[form] += 1
        rows.append(dict(hash="%016x" % x["hash"], elf=hex(x["elf"]), pc=hex(b["pc"]), op=hex(b["op"]), srsrc=reg(q),
                         form=form, base_defs=base_defs,
                         hi_defs=[describe(r) for r in defs[1]], w23_defs=[describe(r) for r in defs[2] + defs[3]]))

uniq = collections.OrderedDict()
for x in bvh_progs:
    uniq.setdefault(x["hash"], []).append(x)
p("")
p("unique BVH programs (hash, copies in eboot, .text words, BVH instr, BFE sites, BFE eboot offsets):")
for h, xs in uniq.items():
    x = xs[0]
    p("  %016x copies=%d words=%d bvh=%d (%s) bfe=%d at %s" % (
        h, len(xs), x["size"] // 4, len(x["bvh"]), ",".join("%s@0x%x" % ("BVH64" if r["op"] == 0xE7 else "BVH", r["pc"]) for r in x["bvh"]),
        len(x["bfe"]), ",".join("0x%x" % s for s in x["bfe_eboot"])))
p("")
p("form of the descriptor at every BVH instruction (all copies):", dict(forms))
p("rows (hash pc op srsrc form | base pair writers | hi writers | dwords 2-3 writers):")
seen = set()
for r in rows:
    key = (r["hash"], r["pc"])
    if key in seen:
        continue
    seen.add(key)
    p("  %s %s %s %s %s | %s | %s | %s" % (r["hash"], r["pc"], r["op"], r["srsrc"], r["form"],
                                          "; ".join(r["base_defs"]), "; ".join(r["hi_defs"]), "; ".join(r["w23_defs"])))
bfe_in_bvh = sorted(s for x in bvh_progs for s in x["bfe_eboot"])
p("")
p("BFE sites in BVH programs (all copies):", len(bfe_in_bvh), "of", len(bfe_sites), "; equal sets:", set(bfe_in_bvh) == set(bfe_sites))
p("BVH64 instructions (node64 path, base not used by the emulator):", sum(1 for x in bvh_progs for r in x["bvh"] if r["op"] == 0xE7))
open(OUT + "bvhmap_f3b.out.txt", "wb").write(("\n".join(lines) + "\n").encode("utf-8"))
json.dump(rows, open(OUT + "bvhmap_f3b.rows.json", "w"), indent=1)
print("\n".join(lines))
