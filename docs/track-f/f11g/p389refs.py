import subprocess, sys
# (commit, path, line, anchor, +1 control)
REFS = [
    ("e442ec59", "docs/ROADMAP.md", 20096,
     "**Правило вывода Ф10 (решено сейчас, применяется лидом после прогонов F11):**",
     "нарушений `size` > 0 хоть в одном теге — «дефект достижим»"),
    ("e442ec59", "docs/ROADMAP.md", 20434,
     "376. **Звено F11c трека F (`HPP-457`, лид): проект F11a (`HPP-455`) ПРИНЯТ",
     "с правками RC1–RC8 отзыва F11b (`HPP-456`, SOUND_WITH_CHANGES) кодом звена F11d"),
    ("e442ec59", "docs/ROADMAP.md", 20486,
     "(ж) **Чтения — поправка п. 369(д) до первого тега**",
     "принят:** сцена с `lanes = 0` и строкой `DiagBvhNodes: mode=1` — `NO_BVH`"),
    ("e442ec59", "docs/track-f/f11f.md", 178,
     "| `d11_sg` | 140 956 303 | 5 075 932 | 3 806 949 | 2 537 966 | 3 806 949 |",
     "| `d11_ef` | — (строки нет; есть только `DiagBvhNodes: mode=1 words=64 tail_bytes=320`)"),
    ("e442ec59", "docs/track-f/f11f.md", 51,
     "| 5 | `lanes = 0` (или строк `lanes=` нет) при строке режима | `NO_BVH`",
     "| 6 |"),
    ("e442ec59", "src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", 2232,
     "const auto is_tri   = Binary(state, OpULessThan, boolt, node_type, U(2u));",
     "const auto is_tri1  = ieq(node_type, U(1u));"),
    ("e442ec59", "docs/track-f/register.md", 585,
     "| Ф10 (поправка к §16) | K4 | наблюдение (путь достижим после Ф9 [I], исполнение [U])",
     ""),
]
ok = True
for c, p, n, a, b in REFS:
    txt = subprocess.run(["git", "-C", "C:/kyty/KytyPS5", "show", f"{c}:{p}"], capture_output=True).stdout.decode("utf-8").split("\n")
    la = a in txt[n - 1]
    lb = (b in txt[n]) if b else (txt[n].strip() == "")  # "" = +1 is an empty line
    print(f"{c}:{p}:{n} anchor={'OK' if la else 'FAIL'} +1={'OK' if lb else 'FAIL'}")
    ok &= la and lb
print(f"{sum(1 for _ in REFS)} refs")
print("ALL OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
