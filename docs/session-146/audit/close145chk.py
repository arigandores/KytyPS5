# close145chk.py - Session Auditor s146 step 3 (HPP-389): the s145 close (ROADMAP s122 items 309-310) against general rule 25.
#  (1) the five "Process" lines of AUDIT145 s.7 - are they in the instruction files / agent-team.md verbatim (whitespace folded)?
#  (2) the files of the close (C:/kyty/s145/step4, instruction files, emulator-folder docs) against the lock windows of the
#      track P series P17 that ran during the close (C:/kyty/p283/p17/runs/lock.log);
#  (3) the order of general rule 25: instruction sha table -> item 309 -> Process applied -> chain created -> documents.
# READ ONLY. No process or application names are printed.
import os, re, datetime, hashlib

UTC = datetime.timezone.utc
EM = 'C:/kyty/KytyPS5/ps5 em'
home = os.environ.get('USERPROFILE', '').replace(chr(92), '/')
CO = home + '/.paperclip/instances/default/companies/f6a17988-768c-4cca-805c-868da6fede4f/agents'
ROLE = {'06386e1c': 'Session Auditor', '2f5a0935': 'Harness Engineer', '8e98843f': 'Probe Designer', 'aabc0a15': 'Lever Researcher',
        'dc34de0a': 'Red Team', 'eb15eb75': 'Emu Engineer', 'f1276629': 'Roadmap Lead'}


def ts(s):
    return datetime.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=UTC).timestamp()


def iso(t):
    return datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def fold(s):
    return re.sub(r'\s+', ' ', s)


def text(p):
    try:
        return fold(open(p, 'rb').read().decode('utf-8', 'replace'))
    except OSError:
        return None


P1 = ('Пока идёт серия цепочки сессии, звено без замка не пользуется инструментами Edit и Write: правка — скриптом из файла одной командой Bash с '
      'проверкой замка в ней же. Звено трека, назначенное исполнителю серии, создаётся и остаётся `blocked` на звене прогонов серии.')
P2 = ('Вопрос, требующий решения лида, — комментарием в своём звене с упоминанием лида И одной строкой в `HPP-3` (она будит лида); монитор ожидания '
      'ставится только записью `executionPolicy` с текущими `stages`, ответ API проверяется на непустые `stages` в той же команде (ловушка платформы 12).')
P3 = ('Пункт, предсказывающий поведение шлюза, цепочки или скорера либо меняющий файлы состояния серии (маркеры попыток, json, манифесты), сверяется со '
      'всеми скриптами пути вызова — `pre_one.sh`, шлюз, `next_one.sh`, цепочка, скорер (путь:строка) — до записи. Список уровней „не входили“ для '
      'печати сверяется со строками `Level has started:` всех логов с даты инвентаря, включая корни треков.')
P4 = ('Отсоединённый вызов тега ждать только `wait_one.sh`; внешний `timeout`, `kill` и повторный вызов тега до строки `rc=` его вывода запрещены; '
      'вывод отказанного вызова переносится до нового вызова.')
P5 = ('Имя постороннего процесса или приложения в `times.txt`, FACTS, комментарии и коммите не пишется — `<app>` и pid; перед каждым `git commit --only` '
      'в той же команде — `git grep -P -f C:/kyty/scrub/checks.txt -- <добавляемые пути>` с выводом строкой `times.txt`; харнесс следующей серии '
      'печатает строку BUSY уже с `<app>`.')
ins = {a[:8]: text('%s/%s/instructions/AGENTS.md' % (CO, a)) for a in (os.listdir(CO) if os.path.isdir(CO) else [])}
team = text(EM + '/docs/agent-team.md')


def probe(name, line, where):
    f = fold(line)
    full = f in where if where else None
    # a shorter probe: the first 60 characters, for a line that was reworded
    head = f[:60] in where if where else None
    return '%s: verbatim %s; first 60 characters %s' % (name, full, head)


print('PROCESS 1 (agent-team.md, general rule 27): %s' % probe('agent-team.md', P1, team))
for k in ('2f5a0935', 'eb15eb75', 'dc34de0a', '8e98843f', 'aabc0a15', '06386e1c'):
    print('PROCESS 2 (%s): %s' % (ROLE[k], probe('instructions', P2, ins.get(k))))
print('PROCESS 3 (Roadmap Lead): %s' % probe('instructions', P3, ins.get('f1276629')))
print('PROCESS 4 (Harness Engineer): %s' % probe('instructions', P4, ins.get('2f5a0935')))
print('PROCESS 5 (agent-team.md, general rule 28): %s' % probe('agent-team.md', P5, team))

# (2) P17 windows
W = []
cur = {}
for ln in open('C:/kyty/p283/p17/runs/lock.log', encoding='utf-8', errors='replace').read().splitlines():
    m = re.match(r'lock (taken|released) (\S+) (\S+Z)', ln)
    if m and m.group(1) == 'taken':
        cur[m.group(2)] = ts(m.group(3))
    elif m and m.group(2) in cur:
        W.append((m.group(2), cur.pop(m.group(2)), ts(m.group(3))))
W = [w for w in W if w[1] >= ts('2026-10-02T05:40:00')]
print('P17 LOCK WINDOWS during the s145 close: %d, %s .. %s' % (len(W), iso(W[0][1]), iso(W[-1][2])))


def inw(t):
    for tag, a, b in W:
        if a <= t <= b:
            return tag
    return None


n = 0
hits = []
roots = ['C:/kyty/s145/step4', EM + '/docs', 'C:/kyty/KytyPS5/docs/session-145/close']
files = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        for f in fn:
            files.append(os.path.join(dp, f).replace(chr(92), '/'))
files += [EM + '/CLAUDE.md', EM + '/AGENTS.md', EM + '/HANDOFF.md', 'C:/kyty/LOOP_STATE.md', 'C:/kyty/KytyPS5/docs/next-session-146.md',
          'C:/kyty/KytyPS5/docs/local-session-145.md', 'C:/kyty/KytyPS5/docs/track-f/register.md', 'C:/kyty/s145/FACTS.md']
files += ['%s/%s/instructions/AGENTS.md' % (CO, a) for a in (os.listdir(CO) if os.path.isdir(CO) else [])]
for p in files:
    try:
        m = os.stat(p).st_mtime
    except OSError:
        continue
    n += 1
    t = inw(m)
    if t:
        hits.append((m, t, p))
print('FILES of the s145 close (step4, emulator docs, close folder, state documents, instruction files): %d; mtime inside a P17 lock window: %d' % (n, len(hits)))
for m, t, p in sorted(hits):
    q = p.replace(home, '<home>')
    q = re.sub(r'agents/([0-9a-f]{8})[0-9a-f-]*/', lambda mm: 'agents/%s (%s)/' % (mm.group(1), ROLE.get(mm.group(1), '?')), q)
    print('   IN-P17-LOCK %s under %s %s' % (iso(m), t, q))
# (3) order
st4 = 'C:/kyty/s145/step4/times.txt'
if os.path.isfile(st4):
    L = open(st4, encoding='utf-8', errors='replace').read().splitlines()
    print('step4/times.txt of the s145 close: %d rows, first %s, last %s, sha256 %s' % (len(L), L[0][:20], L[-1][:20], hashlib.sha256(open(st4, 'rb').read()).hexdigest()[:16]))
    for ln in L:
        if re.search(r'instr_sha|course145|item 309|p[.] ?309|proc309|Process|mk_chain146|chain_check|summary145_viewed|register|next-session-146|commit', ln):
            print('   ROW %s (P17 lock: %s)' % (ln[:230], inw(ts(ln[:19])) if re.match(r'\d{4}-', ln) else None))
print('ALL DONE')
