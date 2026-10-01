# F1d (HPP-293) lead recount of register.md section 4/5: row sums and key 1-3 order. Own code, no import from f0/.
import re, sys, hashlib
P = 'C:/kyty/KytyPS5/docs/track-f/register.md'
raw = open(P, 'rb').read()
print('register sha256', hashlib.sha256(raw).hexdigest())
L = raw.decode('utf-8').split('\n')
def sect(title):
    i = next(k for k, l in enumerate(L) if l.startswith(title))
    out = []
    for l in L[i + 1:]:
        if l.startswith('## '):
            break
        out.append(l)
    return out
def rows(lines):
    r = []
    for l in lines:
        if l.startswith('| ') and not l.startswith('|---'):
            c = [x.strip() for x in l.strip().strip('|').split('|')]
            r.append(c)
    return r[1:]
reg = rows(sect('## 4. '))
ok = True
ids = [r[0] for r in reg]
print('rows', len(reg), 'unique', len(set(ids)))
ok &= len(reg) == 41 and len(set(ids)) == 41
def k1(cls, row):
    c = cls
    if c.startswith('K5'):
        return 'K5'
    if c.startswith('K4'):
        return 'K4'
    if c.startswith('K3') or c.startswith('картинка'):
        return 'K3'
    if c.startswith('K1') or c.startswith('K2'):
        if 'при выходе' in c:
            return 'K12_out'
        return 'K12_in'
    return '?'
cnt = {}
for r in reg:
    k = k1(r[1], r)
    cnt[k] = cnt.get(k, 0) + 1
print('key1 counts', cnt)
ok &= cnt == {'K12_in': 2, 'K3': 7, 'K12_out': 1, 'K4': 24, 'K5': 7}
k14 = sum(v for k, v in cnt.items() if k != 'K5')
print('K1-K4', k14)
ok &= k14 == 34
dob = {'def': 0, 'obs': 0, 'out': 0}
for r in reg:
    c = r[2]
    if c.startswith('вне трека'):
        dob['out'] += 1
    elif c.startswith('дефект'):
        dob['def'] += 1
    elif c.startswith('наблюдение'):
        dob['obs'] += 1
    else:
        print('?', r[0], c[:40])
print('defect/observation/out', dob)
ok &= dob == {'def': 14, 'obs': 20, 'out': 7}
# key order section 5
rk = rows(sect('## 5. '))
print('ranked', len(rk))
ok &= len(rk) == 41
rank1 = {'K1/K2 на входе/удержании': 0, 'K3': 1, 'K1/K2 вне входа и удержания': 2, 'K4': 3, 'K5': 4}
def k3v(s):
    m = re.match(r'≈ ([\d ]+) с', s)
    if m:
        return (0, int(m.group(1).replace(' ', '')))
    if s.startswith('[U]'):
        return (1, 0)
    if s.startswith('нужен пользователь'):
        return (2, 0)
    return (9, 0)
keys = []
for r in rk:
    keys.append((rank1[r[2]], -int(r[3]), k3v(r[4]), -float(r[5].replace(',', '.'))))
srt = sorted(keys)
print('order by keys 1-3 (+P) is sorted:', keys == srt)
ok &= keys == srt
# section 5 rows match section 4 rows
names5 = [r[1].split(' — ')[0] for r in rk]
print('sec5 ids == sec4 ids as sets:', set(names5) == set(ids))
ok &= set(names5) == set(ids)
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
