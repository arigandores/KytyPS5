import re, os, sys
S = os.path.dirname(os.path.abspath(__file__))
RM = "C:/kyty/KytyPS5/docs/ROADMAP.md"
RG = "C:/kyty/KytyPS5/docs/track-f/register.md"
rm = open(RM, "rb").read().decode("utf-8")
assert "\r" not in rm
nums = [int(m.group(1)) for m in re.finditer(r"(?m)^(\d{3})\. \*\*", rm)]
n = max(nums) + 1
print("item number", n)
item = open(os.path.join(S, "p389.md"), "rb").read().decode("utf-8").replace("\r", "").replace("NNN", str(n))
reg = open(os.path.join(S, "reg389.md"), "rb").read().decode("utf-8").replace("\r", "").replace("NNN", str(n))
assert rm.endswith("\n")
open(RM, "wb").write((rm + item).encode("utf-8"))
rg = open(RG, "rb").read().decode("utf-8")
assert "\r" not in rg and rg.endswith("\n") and "## 35." not in rg
open(RG, "wb").write((rg + reg).encode("utf-8"))
print("OK")
