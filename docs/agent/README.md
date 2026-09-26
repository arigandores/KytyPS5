# Agent docs mirror

Snapshot of the working documents that live next to the emulator binary (outside git), copied here so they are
versioned and visible on GitHub:

| File | Source in the emulator folder | What it is |
|---|---|---|
| `PROJECT_CONTEXT.md` | `CLAUDE.md` (identical to `AGENTS.md`) | project context for agents: state of the last four sessions, commands, environment variables, rules |
| `HANDOFF.md` | `HANDOFF.md` | full session history (state after every session) |
| `INDEX.md` | `INDEX.md` | map of files and tools |

The plan above session level is `docs/ROADMAP.md`; per-session sources of truth are `docs/local-session-<NN>.md`.

Personal identifiers (user names, e-mail addresses, account names) are replaced with placeholders such as `<user>`
when the snapshot is taken; local paths therefore read `C:\Users\<user>\...`. The snapshot is refreshed by a local
script before a commit and may lag behind the working copy.
