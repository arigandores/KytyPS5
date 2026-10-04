#!/bin/bash
# FS5a: general rule 30 check before a command > 60 s - prints in_progress issues (identifier, assignee, run) and the
# number of comments of HPP-509; exit 7 when an in_progress issue is assigned to an agent whose name contains "Harness".
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
H="Authorization: Bearer $PAPERCLIP_API_KEY"
curl -s -H "$H" "$B/api/companies/$PAPERCLIP_COMPANY_ID/agents" > "$PAPERCLIP_RUN_SCRATCH_DIR/agents.json"
curl -s -H "$H" "$B/api/companies/$PAPERCLIP_COMPANY_ID/issues?status=in_progress" > "$PAPERCLIP_RUN_SCRATCH_DIR/inprog.json"
curl -s -H "$H" "$B/api/issues/$PAPERCLIP_TASK_ID/comments" > "$PAPERCLIP_RUN_SCRATCH_DIR/comments.json"
python - "$PAPERCLIP_RUN_SCRATCH_DIR" <<'PYEOF'
import json, sys, os
d = sys.argv[1]
ag = json.load(open(os.path.join(d, "agents.json"), encoding="utf-8"))
ag = ag if isinstance(ag, list) else ag.get("items", [])
names = {a["id"]: a.get("name", "") for a in ag}
iss = json.load(open(os.path.join(d, "inprog.json"), encoding="utf-8"))
iss = iss if isinstance(iss, list) else iss.get("items", [])
he = []
out = []
for i in iss:
    n = names.get(i.get("assigneeAgentId"), "?")
    out.append("%s:%s:%s" % (i.get("identifier"), n.replace(" ", "_"), (i.get("executionRunId") or "-")[:8]))
    if "Harness" in n and i.get("executionRunId"):
        he.append(i.get("identifier"))
cm = json.load(open(os.path.join(d, "comments.json"), encoding="utf-8"))
cm = cm if isinstance(cm, list) else cm.get("items", [])
print("in_progress:", " ".join(out), "| HE series:", (",".join(he) or "none"), "| comments HPP-509:", len(cm))
sys.exit(7 if he else 0)
PYEOF
