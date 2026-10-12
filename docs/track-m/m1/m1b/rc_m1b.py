# M1b: curated lists of the review (hand-read of all 184 non-trivial class-G themes in g_rest.txt) -> rc1_themes.tsv.
# Kinds: FATAL - upstream removes an EXIT/fatal/skip of our path; evidence for G only "not seen on visited scenes"
#        RT    - translation/resource-tracking refusal removed; evidence only "no refusal on visited scenes / 281 entries"
#        PIC   - picture/data path of the game, applicability "not proven" or measured on visited scenes only
#        HLE   - HLE answer the game can observe changes; influence [U]
import csv, collections
D = 'docs/track-m/m1/'
L = {
 'FATAL': 'T001 T006 T022 T024 T056 T060 T065 T066 T070 T072 T074 T084 T090 T099 T101 T121 T131 T136 T167 T191 T217 T221 T224 T229 T242 T251 T284 T295 T296 T301',
 'RT': 'T057 T073 T085 T103 T112 T171 T180 T202 T207 T208 T209 T225 T227 T236 T245 T248 T287 T305',
 'PIC': 'T027 T047 T068 T087 T132 T134 T146 T157 T187 T192 T201 T215 T222 T223 T226 T228 T256 T259',
 'HLE': 'T044 T104 T130 T148 T166 T198 T235 T268 T288',
}
rows = list(csv.DictReader(open(D + 'upstream_detail.tsv', encoding='utf-8', newline=''), delimiter='\t', quoting=csv.QUOTE_NONE))
by = collections.OrderedDict()
for r in rows:
    by.setdefault(r['тема'], []).append(r)
out = open(D + 'm1b/rc1_themes.tsv', 'w', encoding='utf-8', newline='\n')
out.write('тема\tвид\tкласс_M1a\tувер_M1a\tподпись\tкоммиты\tключ\tзаголовок\tоснование_M1a\n')
n = collections.Counter()
for kind, s in L.items():
    for t in s.split():
        rs = by[t]
        assert all(r['класс'] == 'Г' for r in rs), t
        u = max((r['увер'] for r in rs), key=lambda x: 'cIU'.index(x) if x in 'cIU' else 0)
        out.write('\t'.join([t, kind, 'Г', u, rs[0]['подпись'], ' '.join(r['sha'][:9] for r in rs), rs[0]['ключ'],
                             rs[0]['заголовок'][:100], rs[0]['основание'][:120]]) + '\n')
        n[kind] += 1
out.close()
print(dict(n), 'total', sum(n.values()), 'ALL OK')
