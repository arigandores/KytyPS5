# F12f (HPP-480): edition 2 of go_f12f.sh (seal section 8): a tag whose caches before the start differ from the reference of the first
# tag does not start (exit 6, the lock is released - the per-tag return is still checked, the reference compare is then not a member);
# the reads of the captures are not done inside the f12_rd lock any more (they moved to rd_sd_f12f.py after the series).
p = 'C:/kyty/f287/f12f/go_f12f.sh'
s = open(p, encoding='ascii').read()
reps = [
("#   4 stop file; 5 procload busy.\n",
 "#   4 stop file; 5 procload busy; 6 caches before the tag differ from the reference of the first tag (edition 2, seal section 8).\n"),
("INSTALLED=0; COPIED=\"\"\n", "INSTALLED=0; COPIED=\"\"; REFOK=1\n"),
("    [ $MC = 0 ] && [ $MR = 0 ] || OK=0\n",
 "    [ $MC = 0 ] || OK=0\n    [ $MR = 0 ] || [ \"$REFOK\" != \"1\" ] || OK=0\n"),
("log \"before vs reference: $(head -1 $OUT/manifest_cmp_ref_before.txt)\"\n",
 "log \"before vs reference: $(head -1 $OUT/manifest_cmp_ref_before.txt)\"\n"
 "if ! head -1 $OUT/manifest_cmp_ref_before.txt | grep -q '^manifest cmp EQUAL'; then\n"
 "  REFOK=0; log \"caches before the tag differ from the reference - not starting (exit 6)\"; exit 6\n"
 "fi\n"),
]
for a, b in reps:
    assert s.count(a) == 1, (a[:60], s.count(a))
    s = s.replace(a, b)
open(p, 'w', encoding='ascii', newline='\n').write(s)
print('patched')
