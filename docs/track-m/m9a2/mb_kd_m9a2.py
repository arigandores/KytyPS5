# M9a2 (HPP-866, track M): offline M_b and the detector control K-D for the T188 tint measure, ROADMAP item 780(b)(7).
#  M_b  = max N_mag over EVERY video record of the M6c tag in the window present >= first_scene_n (reader m6c_read.py,
#         runs/m6_<t>/read.json), N_mag = pixels with R >= 200, G <= 60, B >= 200 after decode to rgb24 960x540.
#  K-D  = 30 single-record insertions of pure magenta (255, 0, 255) in three forms (32x32, 15x15, stripe 64x4), one every
#         10 s of host time from the first scene record + 5 s; each insertion sits in a 120-record segment of the decoded
#         M6c video at segment offset 30 + (13*i mod 60) (spread over GOP positions); positions cycle a grid, half of them on
#         odd pixels (chroma 4:2:0 misalignment). Segments are re-encoded with the KYTY_REC encoder line of
#         screenshot.cpp (rgb24 -> h264_nvenc -preset p4 -cq 24 -g 60 -pix_fmt yuv420p, 60 fps), decoded again and the
#         detector "N_mag > max(2*M_b, 200)" is applied to every record of the segments.
#  Second-generation encode (the source is already NVENC output) - [I] about equality with a first encode.
# Usage: python mb_kd_m9a2.py <sg|hb|mg> <out dir>   (ffmpeg at IDLE priority; exits 3 if the lock exists, also mid-run)
import os, sys, subprocess, hashlib, json
import numpy as np

LOCK = "C:/kyty/SEALED_RUN.lock"
G = "C:/kyty/m657/m6c"
W, H = 960, 540
FB = W * H * 3
IDLE = 0x00000040
SEG, NINS = 120, 30
FORMS = [("sq32", 32, 32), ("sq15", 15, 15), ("st64x4", 64, 4)]
XS, YS = [100, 300, 500, 700, 860], [80, 260, 440]
ENC = ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "24", "-g", "60", "-pix_fmt", "yuv420p"]


def lock():
    if os.path.exists(LOCK):
        sys.exit(3)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def nmag(a):
    return int(((a[:, :, 0] >= 200) & (a[:, :, 1] <= 60) & (a[:, :, 2] >= 200)).sum())


def decoder(path):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE, creationflags=IDLE)


def main():
    lock()
    t, od = sys.argv[1], sys.argv[2]
    os.makedirs(od, exist_ok=True)
    tag = "m6_" + t
    vid, idx, rj = "%s/rec_%s.mp4" % (G, tag), "%s/rec_%s.mp4.idx" % (G, tag), "%s/runs/%s/read.json" % (G, tag)
    fsn = json.load(open(rj))["info"]["first_scene_n"]
    recs = []
    for ln in open(idx, "rb").read().decode().split("\n"):
        p = ln.split()
        if len(p) == 3:
            recs.append((int(p[0]), int(p[1]), float(p[2])))
    win = [r for r, pr, _ in recs if pr >= fsn]
    w0 = win[0]
    t0 = recs[w0][2]
    ins = []
    for i in range(NINS):
        tt = t0 + 5.0 + 10.0 * i
        r = next(r for r in win if recs[r][2] >= tt)
        off = 30 + (13 * i) % 60
        ins.append((r - off, r, (XS[i % 5] + (i % 2), YS[(i // 5) % 3] + (i % 2))))
    for a, b in zip(ins, ins[1:]):
        assert a[0] + SEG <= b[0]
    assert ins[-1][0] + SEG <= len(recs)
    seg_of = {}
    for k, (s, r, pos) in enumerate(ins):
        for j in range(SEG):
            seg_of[s + j] = (k, s + j == r, pos)
    encs = {}
    for name, _, _ in FORMS:
        outp = os.path.join(od, "kd_%s_%s.mp4" % (t, name))
        encs[name] = (outp, subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
                                               "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", "60", "-i", "-"] + ENC +
                                              ["-movflags", "+frag_keyframe+empty_moov", outp],
                                              stdin=subprocess.PIPE, creationflags=IDLE))
    d = decoder(vid)
    n = []
    pre = {name: [] for name, _, _ in FORMS}
    i = 0
    while True:
        buf = d.stdout.read(FB)
        if len(buf) < FB:
            break
        a = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3)
        n.append(nmag(a))
        if i in seg_of:
            k, is_ins, (x, y) = seg_of[i]
            for name, fw, fh in FORMS:
                if is_ins:
                    b = a.copy()
                    b[y:y + fh, x:x + fw] = (255, 0, 255)
                    pre[name].append(nmag(b))
                    encs[name][1].stdin.write(b.tobytes())
                else:
                    encs[name][1].stdin.write(buf)
        i += 1
        if i % 500 == 0 and os.path.exists(LOCK):
            for _, p in encs.values():
                p.kill()
            d.kill()
            sys.exit(3)
    d.wait()
    for _, p in encs.values():
        p.stdin.close()
        p.wait()
    lock()
    nw = [n[r] for r in win if r < len(n)]
    mb = max(nw)
    thr = max(2 * mb, 200)
    sw = sorted(nw)
    out = []
    out.append("tag %s video %s sha256 %s" % (tag, os.path.basename(vid), sha(vid)))
    out.append("  idx sha256 %s records %d decoded %d; read.json sha256 %s first_scene_n %d" % (sha(idx), len(recs), len(n), sha(rj), fsn))
    out.append("  window present >= %d: records %d (first record %d, host %.3f s)" % (fsn, len(nw), w0, t0))
    out.append("  M_b (max N_mag in window, every record) %d at record %d; p99.9 %d; mean %.3f; records >0 %d; >=100 %d; >=200 %d" % (
        mb, win[nw.index(mb)], sw[min(len(sw) - 1, int(0.999 * len(sw)))], sum(nw) / len(nw), sum(1 for v in nw if v > 0),
        sum(1 for v in nw if v >= 100), sum(1 for v in nw if v >= 200)))
    out.append("  whole video max N_mag %d (before the window %d)" % (max(n), max(n[:w0]) if w0 else 0))
    out.append("  detector threshold max(2*M_b, 200) = %d" % thr)
    for name, fw, fh in FORMS:
        outp = encs[name][0]
        dd = decoder(outp)
        m = []
        while True:
            buf = dd.stdout.read(FB)
            if len(buf) < FB:
                break
            m.append(nmag(np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3)))
        dd.wait()
        hits, vals, nxt, false, fmax = 0, [], [], 0, 0
        for k, (s, r, pos) in enumerate(ins):
            off = r - s
            v = m[k * SEG + off] if k * SEG + off < len(m) else -1
            vals.append(v)
            hits += v > thr
            nxt.append(m[k * SEG + off + 1] if k * SEG + off + 1 < len(m) else -1)
            for j in range(SEG):
                if j != off and k * SEG + j < len(m):
                    fmax = max(fmax, m[k * SEG + j])
                    false += m[k * SEG + j] > thr
        out.append("  K-D %s (%dx%d, area %d): encoded records %d (want %d), sha256 %s" % (name, fw, fh, fw * fh, len(m), SEG * NINS, sha(outp)))
        out.append("    before encode N_mag at insertions min %d max %d" % (min(pre[name]), max(pre[name])))
        out.append("    detected %d of %d; N_mag at insertions min %d median %d max %d; next record max %d" % (
            hits, NINS, min(vals), sorted(vals)[NINS // 2], max(vals), max(nxt)))
        out.append("    false detections outside insertions %d of %d (max N_mag outside %d)" % (false, SEG * NINS - NINS, fmax))
        out.append("    per insertion (record, x, y, N_mag): " + " ".join("%d,%d,%d,%d" % (r, p[0], p[1], v) for (s, r, p), v in zip(ins, vals)))
    with open(os.path.join(od, "nmag_%s.tsv" % t), "wb") as f:
        f.write(("\n".join("%d\t%d\t%d" % (r, recs[r][1], n[r]) for r in range(min(len(n), len(recs)))) + "\n").encode())
    out.append("  per-record N_mag: nmag_%s.tsv sha256 %s" % (t, sha(os.path.join(od, "nmag_%s.tsv" % t))))
    out.append("  script sha256 %s" % sha(os.path.abspath(__file__)))
    txt = "\n".join(out) + "\n"
    open(os.path.join(od, "mb_kd_%s.out.txt" % t), "wb").write(txt.encode())
    print(txt)


main()
