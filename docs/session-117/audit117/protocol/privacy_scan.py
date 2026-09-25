import re, sys
t = open('C:/kyty/s117/audit117/protocol/all117.diff', encoding='utf-8', errors='replace').read()
cur = None
added = []
for l in t.split('\n'):
    if l.startswith('+++ '):
        cur = l[6:]
    elif l.startswith('+') and not l.startswith('+++'):
        added.append((cur, l[1:]))
pats = {
    'email': r'[\w.+-]+@[\w-]+\.[\w.]+',
    '<name>/<surname>/<user>': r'(?i)<name>|<surname>',
    'user path': r'(?i)Users.\w+',
    'github handle': r'(?i)arigandores|github\.com/\w+',
    'games': r'(?i)returnal|demon.?s souls|spider.?man|horizon zero|god of war|ratchet|gran turismo|bloodborne|last of us|uncharted|ghost of|elden|genshin|fortnite|minecraft|zelda|mario|pokemon|final fantasy|resident evil|call of duty|cyberpunk|stellar blade|helldivers|astro',
    'emus': r'(?i)shadps4|rpcs3|yuzu|ryujinx|dolphin|pcsx2|xenia|cemu|citra|ppsspp|obliteration|vita3k|fpps4|gpcs4',
    'people': r'(?i)\b(john|alex|anna|ivan|sergey|dmitr\w*|andrey|maxim|nikita|pavel|oleg|artem|kirill|egor|vladimir|mikhail|elena|olga|sasha|claude)\b',
    'urls': r'(?i)https?://\S+',
}
for k, p in pats.items():
    hits = {}
    for f, s in added:
        for m in re.finditer(p, s):
            hits.setdefault(m.group(0), set()).add(f)
    print(k, len(hits))
    for h, fs in sorted(hits.items())[:30]:
        print('   ', repr(h), sorted(fs)[:4])
