from pathlib import Path
p = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em/HANDOFF.md')
s = p.read_text(encoding='utf-8')
start = s.index('Дата: 2026-09-23. **Сессия 108 (WIP')
end = s.index('Дата: 2026-09-23. **Сессия 107 (кратко')
new = """Дата: 2026-09-23. **Сессия 108 (кратко; источник истины — `C:/kyty/s108/FACTS.md`, план — ROADMAP §0.1 и
`docs/next-session-109.md`).** Возобновлена после паузы циклом сессий. `cspfam=4` (пропуск префетча compute по
семейству шейдера) дал Δ среднего кадра −141,8 мкс при пине (`fam108`, SHIP по печати) и был отгружен, но проверка
стража в силе (`KYTY_PIPELINE_PRECACHE=gfx`) пропустила 6 синхронных компиляций на диспатче против 3 — умолчание
откатано к 0 (`01f0c79`, сборка `379777bb…` установлена, видео чистое). Ускорения не осталось. Аудит: пересчёт
CONFIRMED, протокол HOLDS, код NOT REFUTED, MAJOR — страж без экспозиции (печать `C:/kyty/s108/pred/02_audit108.md`).
Сессия 109 — `cspfam` v2 (сброс серий по счётчику созданий пайплайнов) со стражем в силе, затем `QueueDrawAhead`
вне `m_mutex`.

"""
s = s[:start] + new + s[end:]
p.write_text(s, encoding='utf-8')
print('ok')
