p='sc_s13.py'
t=open(p,encoding='ascii').read()
def rep(a,b,n=1):
    global t
    assert t.count(a)==n,(a,t.count(a))
    t=t.replace(a,b)
rep("PRED_PATH = 'C:/kyty/s288/pred/09_s.md'\n",
"SEAL_BASE = 'C:/kyty/s288/pred/09_s.md'       # the seal of S13a: the line \"installed: PENDING\"\n"
"SEAL_B = 'C:/kyty/s288/pred/09b_s.md'         # its edition: the same lines, the line \"installed:\" named (a lead item)\n")
rep("def seal_installed(pred=PRED_PATH):", "def current_seal():\n    \"\"\"The seal in force: the edition 09b when it exists, else 09.\"\"\"\n    return SEAL_B if os.path.isfile(SEAL_B) else SEAL_BASE\n\n\ndef seal_installed(pred=None):")
rep("    if not os.path.isfile(pred):\n        return None\n    got = []", "    pred = pred or current_seal()\n    if not os.path.isfile(pred):\n        return None\n    got = []")
rep("def score_arm(tag, root=LINK_DIR, pred_sha=None, pred_path=PRED_PATH, inst=None):", "def score_arm(tag, root=LINK_DIR, pred_sha=None, pred_path=None, inst=None):")
rep("def check_seal(pred=PRED_PATH, root=ROOT, me=None, game=None):\n    rows = []\n",
"""RX_EDITION = re.compile(r'^(installed|edition): ')


def edition_rows(base=None, ed=None):
    \"\"\"The edition 09b (when it exists): every line of 09 except the lines "installed:" / "edition:" is in 09b in the same order
    and nothing else; 09 says "installed: PENDING"; 09b names the installed binary.  Returns [(name, ok, detail)].\"\"\"
    base = base or SEAL_BASE
    ed = ed or SEAL_B
    if not os.path.isfile(ed):
        return []
    rows = []
    a = [x.rstrip('\n') for x in open(base, encoding='utf-8')] if os.path.isfile(base) else None
    b = [x.rstrip('\n') for x in open(ed, encoding='utf-8')]
    if a is None:
        return [('edition 09b: the seal 09 exists', False, base)]
    ka = [x for x in a if not RX_EDITION.match(x)]
    kb = [x for x in b if not RX_EDITION.match(x)]
    rows.append(('edition 09b: every line of 09 but "installed:" / "edition:" is in 09b, in order, nothing else', ka == kb,
                 '%d / %d lines' % (len(ka), len(kb))))
    ia, ib = seal_installed(base), seal_installed(ed)
    rows.append(('edition 09b: 09 says "installed: PENDING", 09b names the installed binary', ia is not None and
                 ia[0] == 'PENDING' and ib is not None and ib[0] != 'PENDING', '%s / %s' % (ia and ia[0][:16], ib and ib[0][:16])))
    return rows


def check_seal(pred=None, root=ROOT, me=None, game=None):
    pred = pred or current_seal()
    rows = []
""")
rep("    if inst is not None and inst[0] != 'PENDING' and game is not None:", "    if pred == current_seal():\n        rows.extend(edition_rows())\n    if inst is not None and inst[0] != 'PENDING' and game is not None:")
rep("def make_get(root=LINK_DIR, pred=PRED_PATH):\n    memo = {}\n", "def make_get(root=LINK_DIR, pred=None):\n    pred = pred or current_seal()\n    memo = {}\n")
rep("def main(argv=None, root=LINK_DIR, pred=PRED_PATH):", "def main(argv=None, root=LINK_DIR, pred=None):")
rep("    a = ap.parse_args(argv)\n    if a.installed:", "    ap.add_argument('--seal-path', action='store_true')\n    a = ap.parse_args(argv)\n    pred = pred or current_seal()\n    if a.seal_path:\n        print(os.path.relpath(pred, ROOT).replace(chr(92), '/'))\n        return 0\n    if a.installed:")
open(p,'w',encoding='ascii',newline='\n').write(t)
print('ok')
