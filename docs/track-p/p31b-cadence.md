# P31b — каденсовая справка k̄ и правило чтения члена (е)(1) в обе стороны (трек P, `HPP-427`, Harness Engineer)

Основание — `ROADMAP.md` п. 352(в)(1)–(4) (`120079de:docs/ROADMAP.md:19181` «352. **Звено P32 трека P»; +1 — `:19182` «чтения члена (е)(1) в обе
стороны»); RC3 — `6856264a:docs/track-p/p32-review.md:143`–`:179`. Игру не запускал, сборок нет, установленный бинарь и кэши не трогал; константы
п. 346(е), правило окна п. 350(б) и бинарь P30b `4bb8bceb…` не менялись. Время — `C:/kyty/p283/p31b/times.txt` (`date -u`).

## Итог

- **Печать `C:/kyty/p283/pred/07b_p31.md`** — sha256 `b8ae563f36ee73c69759a7a9d5cdb4c1a8a8430ff99d3e9a0523b163f07e5adf` (116 строк; копия —
  `docs/track-p/p31b-seal-07b_p31.md`); `scp31b.py --check-seal` → `SEAL31B: PASS (5 names; the base seal C:/kyty/p283/pred/07_p31.md PASS)`, внутри
  `SEAL: PASS (35 names)` (`out/check_seal_p31b.txt` `83e4eb99…`).
- **Скорер `scp31b.py`** `130f6195…` — новый файл; запечатанный `scp31.py` (`7952ea58…`) **импортируется по sha**, не меняется; `gop31.sh` и
  `07_p31.md` не меняются.
- **Фикстуры** `test_scp31b.py` `a686621b…`: `checks: 44`, `ALL OK` (`out/test_scp31b_v1.txt` `8b78bbe9…`, первая строка — `suite … sha256 …
  target scp31b.py sha256 130f6195…`).
- **Мутанты** `mutlib` v4.1, полный, `--control --no-memo --workers 12`, `--work-dir`/`--cache-dir` `C:/kyty/p283/p31b/`: зачётный прогон 2 —
  **117 из 117 убито, контроли 3 из 3, стена 45,5 с** (`out/mut_scp31b_run2.txt` `34e1f05c…`); прогон 1 — 116 из 117 (выживший `te_gate_x`:
  горизонталь против порога по вертикали контроля — не было фикстуры с разными осями контроля на крае (i); добавлена r3b); сумма стены 84,7 с при
  прогнозе 40 с на прогон.
- **Регрессия без изменений** (запечатанный код через `scp31b.py`): `--regress26` — `REGRESS26 PASS`, 710 / 710, вывод байт в байт = P31
  `regress26_v2.txt` (`480e9d4d…`); `--regress28` — `REGRESS28 PASS`, байт в байт = P31 `regress28_v2.txt` (`a223c06e…`); кэши `p31/data28` не изменены.
- **Справка k̄ на P28** (`--kbar28`, `out/kbar28_v1.txt` `9152f12a…`; окна правила п. 350(б)): `iv_5` 2,2613, `play` 2,2175, `pr_C` 2,4548,
  `ia_A3` 2,2729; строк `FrameTrace` = кадров окна, кадров без строки 0. Против `iv_5` как `hv_0` (справка): `pr_C` `PASS` → `PASS`; `play`
  `FAIL` → `FAIL`; `ia_A3` `FAIL` → `FAIL` (доля смен 0,0886 ≤ 0,10, k̄ выше `iv_5`, приведённое при p = 2 СКО по вертикали 4,0069 > 3,9437 — (i) не
  срабатывает).

## Что добавлено (по членам п. 352(в))

| член | код `scp31b.py` | фикстуры |
|---|---|---|
| (в)(1) k̄: n = кадр − `FSTART_OFF` (= кадр + 1, отображение `start_of`), Σ `dt_us` / (16 667 × строк); кадр без строки — n/a; нет окна — n/a | `kbar_of`, `na`, `VB_US` | k1–k4 |
| сравнение k̄ — точно в целых (Σ_t·N_c против Σ_c·N_t) | `kcmp` | k5 |
| (в)(2) справка: строки `P31B KBAR` (`hv_0`, `hv_1`, `hv_2`) и `P31B NORM` (`hv_1`, `hv_2`: сырые, p = 1, p = 2, множитель, порог) | `factor`, `brought`, `print_kbar`, `print_norm` | k6, p1, p2 |
| (в)(3) `e1k`: по тегу — исход `e1_word(c, тег, тег)`, затем (iii), (i), (ii), (iv); слово — `FAIL` > `NOT_DETERMINED` > `PASS` | `tag_e1k`, `e1k_word` | r1–r13, r3b |
| P34 получает `e1k`; последняя строка `VERDICT_P31B e1=… e1k=… e2=… p24=… e4=… p34=…` | `drive31b` | d1–d10, v1 |
| `--kbar <tag>` (кэш видео не пишется), `--kbar28`, `--check-seal` печати 07b (база — запечатанная проверка `07_p31.md`) | `kbar_tag`, `kbar28`, `ft_rows`, `check_seal`, `main` | v1, v2, s1–s3, m1–m3 |

Края п. 352(в)(4) в фикстурах: k̄ равны (r1, r12 — `e1k` = `e1_word` на 55 × 55 парах тегов); k̄_tag на 1 мкс выше / ниже (Σ 333 341 / 333 339 против
333 340 на 10 строках — r2, r6); приведённое СКО ровно на пороге (2,0 × 0,25 = 0,5) и на 0,0001 выше (2,0004 → 0,5001) по каждой оси (r3, r5, r3b);
доля смен 0,10 / 0,1001 (r4); n/a у тега и у контроля (r8, d5, d6); обе стороны — (i) (r2–r4, d3) и (ii) (r5, r6, d7); порядок `FAIL` раньше
`NOT_DETERMINED` (r10, d4).

## Вопросы лиду (варианты исполнителя — в печати §5; до ответа скорер считает по ним)

1. `e1k` считается отдельным скорером после цепочки (`scp31b.py --all > p31/verdict_p31b.txt`), `gop31.sh` не меняется.
2. Повтор n в окне — считаются все строки (буква «число таких строк»); на P28 повторов нет.
3. (iii) при `FAIL` по доле смен — `NOT_DETERMINED` (буква); ослабления нет.
4. [c] k̄ по `dt_us` ≠ k записи: `pr_C` (k = 2 в записи) — k̄ 2,4548; буква мерит длину показанного кадра — ту, от которой зависит СКО на видеокадр.

## Не заявляется

Что показатель p одинаков у `hv_1` и `pr_C`; что метрика видит любой рывок; что удержание уберёт рывки; механизм рывка; что FPS показа не упадёт;
что привязка кадра строки к видео точна; ни одно число — не выигрыш; 60 FPS не обещаются; путь без `KYTY_GAME_PATCH` не меняется.

## sha256 (`C:/kyty/p283/p31b/SHA256SUMS_p31b.txt`)

```
130f6195b18e97ed9dff080440fb6fea18f333b868d51c26628ac92912139ad9 *scp31b.py
a686621b7f333b860c5f4cf1c4e6f35cc83488778b1f45063974326efa91b1cf *test_scp31b.py
cbdbb904c64323755e2a4a0d2f5e5ddeab432579de71754be4bf32f8b81f6aef *mut_scp31b.py
a8885b0a3c402fc7e52a9ceb6a1922c5d859c315964aeec9139b4bd5efe8ca89 *mk_test_p31b.py
7d8d2ab3237fb6bde851017f995c7f35d1728d2a09ec12b0d87d68c3695aeef4 *mkpred_p31b.py
81f7d4c211a6290cfa8836508e18830614be0aed2cc3ae797367dc923b5cb5d2 *test_src/head.py
ed384e36ac8473b79a9f3254c005ac9bf2175e7a52c286f21e41e8e74e6a9d6f *test_src/cases.py
cdf7035bc4c7eb97f56e65116cf98731157e5a394fcb03314fe7fd62e361a2ae *pred_src/seal_body.md
2dc71c4163e5ea6002e135b3ebebd70e6940ce48f22cdd0c105852d6ce4eb017 *pred_src/seal_res.md
8b78bbe95e0881ee804ed44ac4480483877ca8920b0ee5d56a90b704da38c8d3 *out/test_scp31b_v1.txt
ceeff59e437959b147476f6642ca9ec37d90fa2b7c817f2230e7aa6ef1f048c5 *out/mut_scp31b_run1.txt
34e1f05cc6767feec4d2401ad93d7435158272342e526a624d05b664ec540662 *out/mut_scp31b_run2.txt
480e9d4d7f609c7f8a06ed6bb4e9b0880ef945f025575c88685c1650a202e368 *out/regress26_v1.txt
a223c06e0c425d02d51d1211a74b084b1afec7d1fcc480e23c9727ff0d59604a *out/regress28_v1.txt
9152f12a8ea2af36890412ba6a45ae66922299751ad9befcec9958c81b5a38a0 *out/kbar28_v1.txt
83e4eb9930921f9a5d63ce59ecc1516ed04ec33382d8fd6d2c2f3dc530d54ac2 *out/check_seal_p31b.txt
b8ae563f36ee73c69759a7a9d5cdb4c1a8a8430ff99d3e9a0523b163f07e5adf *C:/kyty/p283/pred/07b_p31.md
```

## Diff скорера: новый файл `C:/kyty/p283/p31b/scp31b.py` (все строки добавлены; `scp31.py` не изменён)

```python
#!/usr/bin/env python3
"""scp31b.py - the amendment of the scorer of the iteration D1-1 of track P (link P31b, HPP-427; ROADMAP s122 item 352 (v)(1)-(4),
RC3 of the review P32 6856264a:docs/track-p/p32-review.md:143-179): the cadence print kbar and the reading of member (e)(1) of item
346 to NOT_DETERMINED in both directions.  The sealed scorer scp31.py of the seal 07_p31.md (sha256 SCP31_SHA) is IMPORTED, not
copied; its constants (item 346 (e): 0.10 / 0.50 / 0.5 x the control, 0.10), the window rule of item 350 (b), e1_word, the members
(e)(2) / (e)(4), the prints and the rule of P34 are the sealed code unchanged.  This file adds:
  - (v)(1) kbar of a tag: the sum of dt_us of the FrameTrace rows whose n is mapped to a frame of the window lo..hi of (e)(1) by the
    mapping of start_of (frame = n + FSTART_OFF of the sealed scp31.py, so n = frame - FSTART_OFF), divided by VB_US x the number of
    such rows; a frame of the window without a row - kbar n/a; no window - n/a;
  - (v)(2) the print (not a gate) of hv_0, hv_1, hv_2: kbar; for hv_1, hv_2 the SD of the 2nd difference vertical and horizontal
    brought to kbar of hv_0 by the factor (kbar_hv0 / kbar_tag)^p at p = 1 and p = 2;
  - (v)(3) the word e1k beside e1_word (it goes to the rule of P34): per tag of hv_1 / hv_2 the outcome of e1_word on that tag, then
    (iii) kbar n/a of the tag or of hv_0 with an outcome other than NOT_DETERMINED -> NOT_DETERMINED; (i) FAIL with the share of
    sign flips <= FLIP_MAX (a FAIL by the SD members only), kbar_tag > kbar_hv0 and both SD brought at p = P_RULE within SD_RATIO x
    the control -> NOT_DETERMINED; (ii) PASS with kbar_tag < kbar_hv0 and at least one SD brought at p = P_RULE above SD_RATIO x the
    control -> NOT_DETERMINED; (iv) else the outcome unchanged; the order of item 350 (v) (FAIL before NOT_DETERMINED) over the
    outcomes of the tags after (i)-(iv); kbar compared exactly (sum x rows cross-multiplied, integers);
  - the driver drive31b: the order of the sealed drive31 with the kbar lines, the print (v)(2), the line E1K and e1k going to the
    sealed p34_rule; the last line VERDICT_P31B (e1 - the sealed e1_word, a print; e1k - the member (1) of P34);
  - --check-seal of 07b_p31.md: every 'seal:' line of SEALED_NAMES against its file, the sealed scp31.py and 07_p31.md by their
    constants, and the base seal 07_p31.md by the sealed check of scp31.py (SEAL: PASS);
  - --kbar <tag>: the window and kbar of one tag of hv_0 / hv_1 / hv_2 (read only); --kbar28: kbar and the brought SD on the videos
    and logs of P28 on the windows of the rule (a print; iv_5 read as hv_0).
The runs of P33 are the runs of the seal 07_p31.md (gop31.sh, root C:/kyty/p283/p31, the prereg sha of every json = 07_p31.md), so
the sealed driver is called with RUN_PRED; 07b_p31.md seals this file.  The video caches runs/vid_<tag>.json are read, never
written (cache=False).  Never runs the game.  ASCII output only (item 175 (v)).
    python scp31b.py --all | --kbar <tag> | --kbar28 | --check-seal | --regress26 | --regress28
"""
import argparse
import hashlib
import importlib.util
import os
import re
import sys

SCP31_PATH = 'C:/kyty/p283/p31/scp31.py'
SCP31_SHA = '7952ea58255dc95af2255f4d81914531b5954162ddba0d68add2562a35d4603d'
RUN_PRED = 'C:/kyty/p283/pred/07_p31.md'
RUN_PRED_SHA = 'a7d62dd5350577dd6d799159297f95b6e689d16aa85987e7730e2f2a3163864d'
ROOT = 'C:/kyty/p283/p31'
HERE = 'C:/kyty/p283/p31b'
PRED_PATH = 'C:/kyty/p283/pred/07b_p31.md'
# item 352 (v): one vblank in microseconds (the divisor of (v)(1)); the powers of the print (v)(2); the power of the rule (v)(3)
VB_US = 16667
P_PRINT = (1, 2)
P_RULE = 2
PFX = 'P31B '
ND = 'NOT_DETERMINED'
SEALED_NAMES = ('scp31b.py', 'test_scp31b.py', 'mut_scp31b.py', 'C:/kyty/p283/p31/scp31.py', 'C:/kyty/p283/pred/07_p31.md')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
RX_FTD = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
CHUNK = 1 << 26


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def fmt(x, p=4):
    return 'n/a' if x is None else ('%.*f' % (p, x))


def load31(name):
    """A fresh module of the sealed scp31.py (its sha256 must be SCP31_SHA); it loads the sealed scp24.py by its own sha."""
    real = sha_file(SCP31_PATH) if os.path.isfile(SCP31_PATH) else None
    if real != SCP31_SHA:
        raise SystemExit('scp31b: %s sha256 %s is not the sealed scorer %s' % (SCP31_PATH, (real or 'missing')[:16], SCP31_SHA[:16]))
    spec = importlib.util.spec_from_file_location(name, SCP31_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S31 = None


def s31():
    global S31
    if S31 is None:
        S31 = load31('scp31_p31b')
    return S31


# ---------------------------------------------------------------- (v)(1) kbar
def kbar_of(rows, lo, hi, off):
    """Item 352 (v)(1): dict(k, s, n, frames, miss, lo, hi) of the frames lo..hi from FrameTrace rows (n, dt_us, ...): the rows with
    n in lo - off .. hi - off (frame = n + off, the mapping of start_of), s - the sum of their dt_us, n - their number, miss - the
    frames without a row, k = s / (VB_US x n) or None (n/a) when a frame has no row; None without a window."""
    if lo is None or hi is None or hi < lo:
        return None
    want = set(range(lo - off, hi - off + 1))
    s = n = 0
    seen = set()
    for r in rows:
        if r[0] in want:
            s += r[1]
            n += 1
            seen.add(r[0])
    miss = len(want) - len(seen)
    return dict(k=None if miss else s / (VB_US * n), s=s, n=n, frames=hi - lo + 1, miss=miss, lo=lo, hi=hi)


def na(kb):
    """kbar n/a: no window or a frame of the window without a row."""
    return kb is None or kb['k'] is None


def kcmp(a, b):
    """The sign of kbar a - kbar b, exact: s_a x n_b against s_b x n_a (integers)."""
    x = a['s'] * b['n'] - b['s'] * a['n']
    return (x > 0) - (x < 0)


def factor(kc, kt, p):
    """(kbar_hv0 / kbar_tag)^p = (s_c x n_t / (s_t x n_c))^p."""
    return ((kc['s'] * kt['n']) / (kt['s'] * kc['n'])) ** p


def brought(m, kc, kt, p):
    """(SD vertical, SD horizontal) of the metrics m brought to kbar of hv_0 at the power p."""
    f = factor(kc, kt, p)
    return m['sd2_dy'] * f, m['sd2_dx'] * f


# ---------------------------------------------------------------- (v)(3) the word e1k
def tag_e1k(c, v, kc, kt):
    """(outcome of e1_word on the tag, outcome after (i)-(iv), why) of one tag of hv_1 / hv_2."""
    S = s31()
    base = S.e1_word(c, v, v)[0]
    if base == ND:
        return base, base, '(iv) NOT_DETERMINED by e1_word'
    if na(kt) or na(kc):
        return base, ND, '(iii) kbar n/a of %s' % ('the tag' if na(kt) else S.TAG_C)
    m, cm = v['m'], c['m']
    dy, dx = brought(m, kc, kt, P_RULE)
    within = dy <= S.SD_RATIO * cm['sd2_dy'] and dx <= S.SD_RATIO * cm['sd2_dx']
    d = kcmp(kt, kc)
    if base == 'FAIL' and m['flips'] <= S.FLIP_MAX and d > 0 and within:
        return base, ND, '(i) a FAIL by the SD members only, kbar above %s, both SD brought at p = %d within' % (S.TAG_C, P_RULE)
    if base == 'PASS' and d < 0 and not within:
        return base, ND, '(ii) a PASS with kbar below %s and an SD brought at p = %d above the gate' % (S.TAG_C, P_RULE)
    return base, base, '(iv) unchanged'


def e1k_word(c, v1, v2, kc, k1, k2):
    """Item 352 (v)(3): (word, why, [(tag, base, outcome, why)]) - the outcomes of the tags after (i)-(iv), FAIL before
    NOT_DETERMINED (item 350 (v)), else PASS."""
    S = s31()
    per = [(t,) + tag_e1k(c, v, kc, kt) for t, v, kt in zip(S.TAG_V, (v1, v2), (k1, k2))]
    words = [w for t, b, w, y in per]
    if 'FAIL' in words:
        word = 'FAIL'
    elif ND in words:
        word = ND
    else:
        word = 'PASS'
    return word, '; '.join('%s %s -> %s %s' % x for x in per), per


# ---------------------------------------------------------------- the prints
def print_kbar(tag, kb, out):
    if kb is None:
        out(PFX + 'KBAR %s (item 352 (v)(1)): no window of (e)(1) -> kbar n/a' % tag)
        return
    out(PFX + 'KBAR %s (item 352 (v)(1)): window %d..%d (%d frames, n %d..%d), FrameTrace rows %d, frames without a row %d, sum dt_us '
        '%d, kbar %s' % (tag, kb['lo'], kb['hi'], kb['frames'], kb['lo'] - s31().FSTART_OFF, kb['hi'] - s31().FSTART_OFF, kb['n'],
                         kb['miss'], kb['s'], fmt(kb['k'])))


def print_norm(tag, v, kt, c, kc, out):
    """Item 352 (v)(2): the SD of a tag raw and brought to kbar of hv_0 at p = 1 and 2, the factors, the gate of the control."""
    S = s31()
    m = (v or {}).get('m') or {}
    cm = (c or {}).get('m') or {}
    raw = (m.get('sd2_dy'), m.get('sd2_dx'))
    ok = not (na(kt) or na(kc)) and None not in raw
    cols = []
    for p in P_PRINT:
        f = factor(kc, kt, p) if ok else None
        cols.append('p=%d factor %s vertical %s horizontal %s' % (p, fmt(f), fmt(raw[0] * f if ok else None),
                                                                 fmt(raw[1] * f if ok else None)))
    gy = S.SD_RATIO * cm['sd2_dy'] if cm.get('sd2_dy') is not None else None
    gx = S.SD_RATIO * cm['sd2_dx'] if cm.get('sd2_dx') is not None else None
    out(PFX + 'NORM %s (item 352 (v)(2), print): kbar %s against %s %s; SD raw vertical %s horizontal %s; %s; gate %.1f x %s vertical %s '
        'horizontal %s' % (tag, fmt(None if na(kt) else kt['k']), S.TAG_C, fmt(None if na(kc) else kc['k']), fmt(raw[0]), fmt(raw[1]),
                           '; '.join(cols), S.SD_RATIO, S.TAG_C, fmt(gy), fmt(gx)))


# ---------------------------------------------------------------- the driver
def drive31b(P, root, pred, out, vid=None, cache=False, ref=False, s1=None):
    """--all of P31b: the sealed driver of P24 (rebound by the sealed scp31.py), the prints of the sealed drive31 per tag, kbar of
    (v)(1), the print (v)(2), E1 (the sealed e1_word, a print), E1K (v)(3), E2, E4, the sealed rule of P34 on e1k, VERDICT_P31B."""
    S = s31()
    lines = []

    def o(line):
        lines.append(line)
        out(line)
    rule24 = P.drive('p24', root, pred, root, o, ref=ref, s1=s1)
    Q = P.m24().S15
    runs = dict((t, Q.run_of(t, root, pred)) for t in S.VID_TAGS)
    kc = {}
    vids = {}
    kb = {}
    for t in S.VID_TAGS:
        r = runs[t]
        if r is None:
            out(S.PFX + 'TAG %s not made' % t)
            kc[t] = vids[t] = kb[t] = None
            print_kbar(t, None, out)
            continue
        kc[t] = S.hold_print(r, out)
        vids[t] = vid[t] if vid is not None else S.vid_tag(t, root, r['log'], out, cache=cache)
        if vids[t] is not None:
            S.print_vid(t, vids[t], out)
        lo, hi = vids[t]['win'] if vids[t] is not None else (None, None)
        kb[t] = kbar_of(r['log']['rows'] if r['log'] is not None else [], lo, hi, S.FSTART_OFF)
        print_kbar(t, kb[t], out)
    C, V1, V2 = S.TAG_C, S.TAG_V[0], S.TAG_V[1]
    e1, why1 = S.e1_word(vids[C], vids[V1], vids[V2])
    out(S.PFX + 'E1 (item 346 (e)(1)): %s (%s); gate: %s and %s - sign flips <= %.2f, SD vertical and horizontal <= %.1f x %s; control '
        '%s sign flips >= %.2f' % (e1, S.asc(why1), V1, V2, S.FLIP_MAX, S.SD_RATIO, C, C, S.CTRL_MIN))
    for t in S.TAG_V:
        print_norm(t, vids[t], kb[t], vids[C], kb[C], out)
    e1k, whyk, per = e1k_word(vids[C], vids[V1], vids[V2], kb[C], kb[V1], kb[V2])
    out(PFX + 'E1K (item 352 (v)(3); the member (1) of P34): %s (%s); e1_word %s' % (e1k, S.asc(whyk), e1))
    e2 = S.e2_word(kc[V1], kc[V2])
    out(S.PFX + 'E2 (item 346 (e)(2)): %s (%s %s, %s %s; %s %s - print)' % (e2, V1, fmt(kc[V1]), V2, fmt(kc[V2]), C, fmt(kc[C])))
    rc = runs[C]
    if rc is None:
        e4, w4 = 'NOT_EVALUABLE', (False, 0, 0)
    else:
        w4 = S.wait_zero(rc['recs'])
        e4 = 'OK' if w4[0] else 'FAIL'
    out(S.PFX + 'E4 (item 346 (e)(4)): %s - %s record lines %d, with wait_us=0 %d' % (e4, C, w4[1], w4[2]))
    word = S.p34_rule(e1k, e2, rule24, e4, out)
    out('VERDICT_P31B e1=%s e1k=%s e2=%s p24=%s e4=%s p34=%s' % (e1, e1k, e2, rule24, e4, word))
    return word, lines


def kbar_tag(tag, root, pred, out):
    """--kbar <tag>: the window of (e)(1) of one tag of hv_0 / hv_1 / hv_2 from its video (cache read, not written) and its kbar."""
    S = s31()
    r = S.p31().m24().S15.run_of(tag, root, pred)
    if r is None:
        out(S.PFX + 'TAG %s not made' % tag)
        print_kbar(tag, None, out)
        return None
    v = S.vid_tag(tag, root, r['log'], out, cache=False)
    S.print_vid(tag, v, out)
    kb = kbar_of(r['log']['rows'] if r['log'] is not None else [], v['win'][0], v['win'][1], S.FSTART_OFF)
    print_kbar(tag, kb, out)
    return kb


# ---------------------------------------------------------------- --kbar28 (print)
def ft_rows(path, lo, hi, off):
    """The FrameTrace rows (n, dt_us) of a log with n in lo - off .. hi - off, by a streaming pass (the logs of P28)."""
    want = set(range(lo - off, hi - off + 1))
    rows = []
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            for m in RX_FTD.finditer(whole):
                n = int(m.group(1))
                if n in want:
                    rows.append((n, int(m.group(2))))
            if not b:
                break
    return rows


def kbar28(out=print, data=None):
    """kbar of (v)(1) and the SD brought by (v)(2) on the videos and logs of P28 (iv_5, play, pr_C, ia_A3) on the windows of the rule
    of item 350 (b) (the caches of --regress28, read only); iv_5 read as hv_0 and each other video as a tag: e1_word and e1k of the
    pair (a print, not a gate)."""
    S = s31()
    data = data or os.path.join(ROOT, 'data28')
    res = {}
    for tag, mp4, log, (w0, w1) in S.REG28:
        fs, n0 = S.start_of_log(log)
        c, ch = S.vid_cache(os.path.join(data, 'vid_%s.json' % tag), mp4)

        def rows_fn(a, b, c=c, mp4=mp4):
            return S.vid_rows(c, mp4, a, b)[0]
        v = S.e1_of(c['pink'], rows_fn, fs)
        v['fs'] = fs
        lo, hi = v['win']
        kb = kbar_of(ft_rows(log, lo, hi, S.FSTART_OFF), lo, hi, S.FSTART_OFF) if lo is not None else None
        res[tag] = (v, kb)
        print_vid28(tag, v, out, kb)
    if 'iv_5' in res:
        c, kc = res['iv_5']
        for tag in ('play', 'pr_C', 'ia_A3'):
            if tag not in res:
                continue
            v, kt = res[tag]
            print_norm(tag, v, kt, c, kc, out)
            w0, why0 = S.e1_word(c, v, v)
            b, w, why = tag_e1k(c, v, kc, kt)
            out(PFX + 'KBAR28 %s read as a tag against iv_5 as %s (print): e1_word %s, e1k %s %s' % (tag, S.TAG_C, w0, w, why))
    return res


def print_vid28(tag, v, out, kb):
    m = v['m'] or {}
    out(PFX + 'KBAR28 %s: frame of the line %s, window %s..%s %s, flips %s SD vertical %s horizontal %s' % (
        tag, v.get('fs'), v['win'][0], v['win'][1], v['oc'], fmt(m.get('flips')), fmt(m.get('sd2_dy')), fmt(m.get('sd2_dx'))))
    print_kbar(tag, kb, out)


# ---------------------------------------------------------------- the seal
def check_seal(seal=PRED_PATH, root=ROOT, run_pred=RUN_PRED, here=HERE, base=None):
    """Every 'seal: <sha> <name>' line of 07b_p31.md against its file, each SEALED_NAMES name exactly once; the sealed scp31.py and
    07_p31.md by SCP31_SHA / RUN_PRED_SHA; the base seal 07_p31.md by the sealed check of scp31.py (base: fixtures)."""
    got = {}
    try:
        with open(seal, encoding='utf-8') as f:
            for line in f:
                m = RX_SEAL.match(line.rstrip('\r\n'))
                if m:
                    got.setdefault(m.group(2), []).append(m.group(1))
    except OSError:
        print('SEAL31B: FAIL (no seal %s)' % seal)
        return False
    ok = True
    for name in SEALED_NAMES:
        shas = got.get(name, [])
        path = name if ':' in name else os.path.join(here, name)
        if len(shas) != 1:
            print('seal line of %s: %d lines' % (name, len(shas)))
            ok = False
            continue
        real = sha_file(path) if os.path.isfile(path) else None
        if real != shas[0]:
            print('seal mismatch %s: seal %s file %s' % (name, shas[0][:16], (real or 'missing')[:16]))
            ok = False
    for path, want in ((SCP31_PATH, SCP31_SHA), (RUN_PRED, RUN_PRED_SHA)):
        if got.get(path, [None])[0] != want:
            print('seal: %s is not the sealed file %s' % (path, want[:16]))
            ok = False
    bok = (base or s31().check_seal)(run_pred, root)
    ok &= bool(bok)
    print('SEAL31B: %s (%d names; the base seal %s %s)' % ('PASS' if ok else 'FAIL', len(SEALED_NAMES), run_pred,
                                                          'PASS' if bok else 'FAIL'))
    return ok


def main(argv=None, root=ROOT, pred=RUN_PRED, seal=PRED_PATH):
    p = argparse.ArgumentParser()
    p.add_argument('--kbar')
    for a in ('--all', '--kbar28', '--check-seal', '--regress26', '--regress28'):
        p.add_argument(a, action='store_true')
    o = p.parse_args(argv)
    if o.check_seal:
        return 0 if check_seal(seal, root, pred) else 1
    S = s31()
    if o.regress26:
        return 0 if S.regress26() else 1
    if o.regress28:
        return 0 if S.regress28() else 1
    if o.kbar28:
        kbar28()
        return 0
    if o.kbar is not None:
        if o.kbar not in S.VID_TAGS:
            print('kbar: %s is not a video tag (%s)' % (S.asc(o.kbar), ' '.join(S.VID_TAGS)))
            return 2
        kbar_tag(o.kbar, root, pred, print)
        return 0
    if o.all:
        drive31b(S.p31(), root, pred, print)
        return 0
    p.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
```
