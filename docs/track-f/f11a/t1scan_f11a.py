# F11a (HPP-455, ROADMAP p.369(d) member (3)): static count of S_TRAP (SOPP op 18) and
# IMAGE_BVH(64)_INTERSECT_RAY (MIMG op 0xe6/0xe7) over the T1 corpus C:/kyty/s288/s7/t1_base.tsv.
# Code of a corpus shader: the AMDGPU ELF of eboot.bin / sce_module whose .text XXH3-64 = hash16
# (method of bvhmap_f3b.py); calibration: sha256 of the first gcn_words words = gcn_sha256 of the base.
# Decode: the reachable walk of reach_f3b.py with the decoder of bvhmap_f3b.py (checked there against
# the emulator disassembly of 380bb9d636390bae, 1917 of 1917 pcs). Also the same count over every ELF.
# Exits 3 (no output written) as soon as C:/kyty/SEALED_RUN.lock appears.
import sys, os, struct, mmap, hashlib, collections

LOCK = "C:/kyty/SEALED_RUN.lock"


def lock_exit():
    if os.path.exists(LOCK):
        print("LOCK appeared - exit 3, nothing written")
        sys.exit(3)


lock_exit()
import xxhash

sys.path.insert(0, "C:/kyty/f287/f3b")
from reach_f3b import reachable  # noqa: E402

NL = chr(10)
TAB = chr(9)
OUT = "C:/kyty/f287/f11a/"
GAME = "C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/"
lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


def sdst_regs(base, count):
    return list(range(base, base + count))


# decode(): copy of C:/kyty/f287/f3b/bvhmap_f3b.py lines 64-170 (family and length rules), comments dropped
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
                wide = op in (4, 6, 8, 10, 12, 28, 30, 31, 33, 36, 37, 38, 39, 40, 41, 42, 43, 45, 47, 49, 55, 56, 57, 58, 59)
                rec["writes"] = sdst_regs(d, 2 if wide else 1)
                if op in (27, 29):
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
                if op in (0, 2, 15, 16, 18):
                    rec["writes"] = [d]
                if op == 22:
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
                    d = w & 0xFF
                    if op < 0x80:
                        rec["writes"] = [d]
                    elif op in (0x360,):
                        rec["writes"] = [d]
                    else:
                        sd = (w >> 8) & 0x7F
                        if op in (0x30F, 0x310, 0x319, 0x31A, 0x176, 0x177):
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
        if rec["fam"] == "VOP1" and ((w >> 9) & 0xFF) == 2:
            rec["writes"] = [(w >> 17) & 0xFF]
        rec["size"] = size
        rec["words"] = words[i:i + size]
        out.append(rec)
        i += size
    return out


MAGIC = bytes([0x7F, 0x45, 0x4C, 0x46, 2, 1, 1])


def elf_programs(path):
    f = open(path, "rb")
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    progs = []
    e = mm.find(MAGIC)
    while e != -1:
        if struct.unpack_from("<H", mm, e + 18)[0] == 0xE0:
            secs = []
            try:
                shoff = struct.unpack_from("<Q", mm, e + 0x28)[0]
                shentsize, shnum, shstrndx = struct.unpack_from("<HHH", mm, e + 0x3A)
                for k in range(shnum):
                    b = e + shoff + k * shentsize
                    name, typ, flags, addr, off, size = struct.unpack_from("<IIQQQQ", mm, b)
                    secs.append((name, typ, off, size))
            except struct.error:
                secs = []
            if secs and shstrndx < len(secs):
                stroff = e + secs[shstrndx][2]
                for name, typ, off, size in secs:
                    end = mm.find(bytes([0]), stroff + name)
                    nm = mm[stroff + name:end].decode("latin1")
                    if nm in (".text", ".shader_text"):
                        code = bytes(mm[e + off:e + off + size])
                        progs.append(dict(src=os.path.basename(path), elf=e, code=code,
                                          hash=xxhash.xxh3_64_intdigest(code)))
        e = mm.find(MAGIC, e + 1)
    return progs


files = [GAME + "eboot.bin"]
mod = GAME + "sce_module/"
if os.path.isdir(mod):
    files += [mod + x for x in sorted(os.listdir(mod)) if x.lower().endswith((".prx", ".sprx", ".elf"))]
programs = []
for fp in files:
    lock_exit()
    ps = elf_programs(fp)
    p("source", os.path.basename(fp), "sha256", hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16],
      "AMDGPU ELFs with .text:", len(ps))
    programs += ps
by_hash = collections.OrderedDict()
for x in programs:
    by_hash.setdefault(x["hash"], []).append(x)
p("programs:", len(programs), "unique .text hashes:", len(by_hash))


def scan(code):
    words = list(struct.unpack_from("<%dI" % (len(code) // 4), code, 0))
    recs, bad = reachable(decode, words)
    traps = [r for r in recs if r["fam"] == "SOPP" and r["op"] == 18]
    bvh = [r for r in recs if r["fam"] == "MIMG" and r["op"] in (0xE6, 0xE7)]
    return recs, bad, traps, bvh


# every ELF program (context for the corpus) - only with --all (long); default: the T1 corpus only
all_trap = all_bvh = all_bad = 0
trap_hashes = set()
bvh_hashes = set()
for k, (h, xs) in enumerate(by_hash.items() if "--all" in sys.argv else []):
    if k % 200 == 0:
        lock_exit()
    recs, bad, traps, bvh = scan(xs[0]["code"])
    all_bad += 1 if bad else 0
    if traps:
        all_trap += len(traps)
        trap_hashes.add(h)
    if bvh:
        all_bvh += len(bvh)
        bvh_hashes.add(h)
if "--all" in sys.argv:
    p("ALL unique programs: with S_TRAP", len(trap_hashes), "(instructions", all_trap, ") ; with IMAGE_BVH*", len(bvh_hashes),
      "(instructions", all_bvh, ") ; reachable decode met UNKNOWN in", all_bad)
else:
    p("ALL unique programs: not scanned (run without --all)")

# the T1 corpus
rows = []
hdr = None
for ln in open("C:/kyty/s288/s7/t1_base.tsv", encoding="utf-8"):
    f = ln.rstrip(chr(13) + NL).split(TAB)
    if hdr is None:
        hdr = f
        continue
    rows.append(dict(zip(hdr, f)))
t1sha = hashlib.sha256(open("C:/kyty/s288/s7/t1_base.tsv", "rb").read()).hexdigest()
p("t1_base.tsv sha256", t1sha, "rows", len(rows), "by row class", dict(collections.Counter(r["row"] for r in rows)))
uniq = collections.OrderedDict()
for r in rows:
    uniq.setdefault(r["hash16"], []).append(r)
p("T1 unique hash16:", len(uniq), "by stage:", dict(collections.Counter(",".join(sorted(set(r["stage"] for r in rs))) for rs in uniq.values())))
found = calib_ok = calib_bad = calib_na = 0
out_rows = []
n_trap = n_bvh = 0
detail = []
for k, (h16, rs) in enumerate(uniq.items()):
    if k % 200 == 0:
        lock_exit()
    h = int(h16, 16)
    stages = sorted(set(r["stage"] for r in rs))
    classes = "".join(sorted(set(r["row"] for r in rs)))
    xs = by_hash.get(h)
    if not xs:
        out_rows.append([h16, ",".join(stages), classes, "NOT_FOUND", "", "", ""])
        continue
    found += 1
    code = xs[0]["code"]
    gw = [r.get("gcn_words", "") for r in rs if r.get("gcn_words", "").isdigit()]
    gs = [r.get("gcn_sha256", "") for r in rs if len(r.get("gcn_sha256", "")) == 64]
    cal = "NA"
    if gw and gs:
        n = int(gw[0])
        cal = "OK" if hashlib.sha256(code[:n * 4]).hexdigest() == gs[0] else "MISMATCH"
    if cal == "OK":
        calib_ok += 1
    elif cal == "MISMATCH":
        calib_bad += 1
    else:
        calib_na += 1
    recs, bad, traps, bvh = scan(code)
    n_trap += 1 if traps else 0
    n_bvh += 1 if bvh else 0
    out_rows.append([h16, ",".join(stages), classes, cal, str(len(traps)), str(len(bvh)), "unknown" if bad else ""])
    if traps or bvh:
        idx = {r["pc"]: j for j, r in enumerate(recs)}
        for t in traps:
            j = idx[t["pc"]]
            ctx = recs[max(0, j - 3):j + 2]
            detail.append("  %s %s S_TRAP pc=0x%x trap_id=%d ctx: %s" % (
                h16, ",".join(stages), t["pc"], t["words"][0] & 0xFF,
                " | ".join("0x%x %s op%s %s" % (c["pc"], c["fam"], c["op"], " ".join("%08x" % w for w in c["words"])) for c in ctx)))
        for b in bvh:
            detail.append("  %s %s %s pc=0x%x srsrc=s%d" % (
                h16, ",".join(stages), "IMAGE_BVH64_INTERSECT_RAY" if b["op"] == 0xE7 else "IMAGE_BVH_INTERSECT_RAY", b["pc"], b["srsrc"]))
p("T1 unique hashes found among ELF programs:", found, "of", len(uniq), "; calibration gcn_sha256 OK", calib_ok,
  "MISMATCH", calib_bad, "NA", calib_na)
p("T1 shaders with S_TRAP:", n_trap, "; with IMAGE_BVH*:", n_bvh)
p("T1 instructions S_TRAP:", sum(int(r[4]) for r in out_rows if r[4]), "; IMAGE_BVH*:", sum(int(r[5]) for r in out_rows if r[5]))
p("details (hash16 stage instruction pc context):")
lines.extend(detail)
p("T1 hashes among the BVH programs of all ELFs:", sorted("%016x" % h for h in bvh_hashes if "%016x" % h in uniq))
p("T1 hashes among the S_TRAP programs of all ELFs:", sorted("%016x" % h for h in trap_hashes if "%016x" % h in uniq))
p("all-ELF S_TRAP program hashes:", " ".join(sorted("%016x" % h for h in trap_hashes)))
p("all-ELF BVH program hashes:", " ".join(sorted("%016x" % h for h in bvh_hashes)))
lock_exit()
open(OUT + "t1scan_f11a.out.txt", "wb").write((NL.join(lines) + NL).encode("utf-8"))
open(OUT + "t1scan_f11a.tsv", "wb").write(
    (NL.join(TAB.join(r) for r in [["hash16", "stage", "rows", "calib", "s_trap", "bvh", "decode"]] + out_rows) + NL).encode("utf-8"))
print(NL.join(lines))
