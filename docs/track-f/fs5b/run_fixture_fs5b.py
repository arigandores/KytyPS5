# FS5b (HPP-510, Red Team): port of my FS4b run_fixture_fs4b.py by mk_fx_scripts_fs5b.py (FixF10Enabled, 0e72bc19 vs 8a56dc2a). Was:
# FS4b (HPP-471, Red Team): driver of the KYTY_FIX_F10 default-parsing fixture (programs from mk_fixture_fs4b.py).
# Each case runs the program as a new process with a clean copy of the environment where KYTY_FIX_F10 is removed
# ("absent") or set to the value; plus "arg" mode for every value (no CRT environment in between).
# Expected for 0e72bc19 (FS4, item 410(g)(1)): absent / "" -> 1; 0/false/off/no in any ASCII case, exact -> 0; else -> 1.
# Expected for 8a56dc2a (F12d, negative control of the fixture): absent / "" -> 0; 0/false/off/no -> 0; else -> 1.
# Prints ALL OK when every row matches.
import os, subprocess
D = "C:/kyty/f287/fs5/fs5b/"
OFF = ("0", "false", "FALSE", "False", "off", "OFF", "Off", "no", "NO", "No")
OTHER = ("1", "00", " 0", "0 ", "yes", "on", "true", "2", "nv", "offf", "n", "-0", "0x0", "fals")
ok = True
for c, unset_on in (("0e72bc19", 1), ("8a56dc2a", 0)):
    exe = D + "fx_" + c + ".exe"
    rows = [("absent", None, unset_on), ("empty", "", unset_on)]
    rows += [("off-word", v, 0) for v in OFF] + [("other", v, 1) for v in OTHER]
    for kind, v, want in rows:
        env = {k: x for k, x in os.environ.items() if k.upper() != "KYTY_FIX_F10"}
        if v is not None:
            env["KYTY_FIX_F10"] = v
        out = subprocess.run([exe, "env"], env=env, capture_output=True, text=True).stdout.strip()
        got = int(out.rsplit("on=", 1)[1])
        r = got == want
        ok &= r
        print("%s env %-8s %-10r -> %-30s want %d %s" % (c, kind, v, out, want, "ok" if r else "MISMATCH"))
        if v is not None:
            out = subprocess.run([exe, "arg", v], capture_output=True, text=True).stdout.strip()
            got = int(out.rsplit("on=", 1)[1])
            r = got == want
            ok &= r
            print("%s arg %-8s %-10r -> %-30s want %d %s" % (c, kind, v, out, want, "ok" if r else "MISMATCH"))
print("FIXTURE", "ALL OK" if ok else "FAILED")
