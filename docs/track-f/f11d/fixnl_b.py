from pathlib import Path
q = Path("C:/kyty/f287/f11d/patch_f11d_tests_b.py")
u = q.read_text(encoding="utf-8")
bad = 'bytes=%llu\n",'
assert u.count(bad) == 1, u.count(bad)
u = u.replace(bad, 'bytes=%llu\\n",')
q.write_bytes(u.encode("utf-8"))
print("fixed")
