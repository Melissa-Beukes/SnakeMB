# Structure Context Pack

Verified project organisation for the Snake Game repository.

## 1. Top-Level Folder Structure (verified by directory enumeration)

```
BA-Marlin-Test-Repo/
  README.md
  STRUCTURE.md
  Auto-PR-Solution.md
  requirements.txt
  pytest.ini
  pytest.bat
  run_game.bat
  run_pygame_version.bat
  run_web_game.bat

  game_logic.py               (shared logic module)
  leaderboard.py              (HighScoreManager class)
  snake_game.py               (Pygame entry point)
  snake_game_tkinter.py       (Tkinter entry point)
  snake_game_console.py       (Console entry point)
  snake_game.html             (Browser entry point)
  highscores.json             (persistent leaderboard data)

  snake_game.py.bak
  snake_game.py.bak-mds
  snake_game.py.bak-pre-white-food
  snake_game_tkinter.py.bak
  snake_game_tkinter.py.bak-mds
  snake_game_tkinter.py.bak-pre-white-food
  snake_game_console.py.bak
  snake_game_console.py.bak-mds
  snake_game.html.bak-mds

  test_food_color.py
  test_leaderboard.py
  test_snake_game_tkinter_display.py
  verify_color.py

  docs/
    .cursorrules
    architecture.md
    structure.md
    code.md
    dataflow.md
    decisions.md
    glossary.md
    risk.md

  flashing-mines/
    Build.md
    flashing-mines-plan.md
    ToDo.md
    post-implementation-lessons-learned.md

  mine-detonation-storm/
    Build.md
    Plan.md
    ToDo.md
    user-story.md
    feature.json
    run-log.md

  music/
    chiptune_triumphant.wav

  tests/
    __init__.py                (empty)
    conftest.py
    test_game_logic.py
    test_smoke.py

  .cursor/
    rules/
      rules.mdc                (109 lines; MDC variant with alwaysApply: true header)

  .roo/
    rules/
      rules.md                 (109 lines; identical body to .cursor/rules/rules.mdc)
```

The `.git/`, `.pytest_cache/`, and any `__pycache__/` folders are present but excluded from documentation context.

### 1.1 Cursor / Roo rule files exist in three locations (verified round-2)

The same mandatory-reference-doc rule set is encoded in three separate files:

1. `docs/.cursorrules` (107 lines) — the canonical Context-Pack rule file referenced by section 7 cross-references.
2. `.cursor/rules/rules.mdc` (109 lines) — Cursor MDC variant; adds `alwaysApply: true` at the top, body identical from line 3 onwards.
3. `.roo/rules/rules.md` (109 lines) — Roo variant; body identical to the MDC variant from line 3 onwards.

Verified by line read of all three files. They drift independently, so any rule update must be applied in three places or the AI assistant will load contradictory guidance depending on which tool is active. Tracked as technical debt in `risk.md` section 3 ("Cursor / Roo rule files duplicated in three locations") and as Suggested Future Enhancements item 2 in `decisions.md`.

### 1.2 `STRUCTURE.md` at the repo root is stale (verified round-2)

The legacy `STRUCTURE.md` at the repository root is heavily out of date. It claims `.cursor/commands/` with `start-snake-game.bat`, `start-snake-game.sh`, `start-snake-game.json`; `.vscode/` with `launch.json`/`settings.json`/`tasks.json`; and a `.cursor/README.md`. None of those files or directories exist (verified by directory enumeration; only `.cursor/rules/` is present). It also says "Three Versions Available" — there are four runtimes — and does not mention `game_logic.py`, `leaderboard.py`, `snake_game_console.py`, `tests/`, `highscores.json`, `music/`, `flashing-mines/`, `mine-detonation-storm/`, or any backup files. **This file (`docs/structure.md`) supersedes `STRUCTURE.md`.** See `risk.md` section 3 and Suggested Future Enhancements item 1 in `decisions.md`.


### 1.3 Verified file line counts (round-3 audit, 2026-05-20)

| File | LOC |
|---|---|
| `snake_game.py` | 574 |
| `snake_game_tkinter.py` | 730 |
| `snake_game_console.py` | 371 |
| `snake_game.html` | 776 |
| `game_logic.py` | 111 |
| `leaderboard.py` | 184 |
| `test_leaderboard.py` | 687 |
| `test_snake_game_tkinter_display.py` | 202 |
| `test_food_color.py` | 88 |
| `verify_color.py` | 28 |
| `tests/test_game_logic.py` | 125 |
| `tests/test_smoke.py` | 54 |

Counts verified by direct line read. Earlier estimates in prior context packs
were off by 1 due to trailing-newline counting differences.
## 2. Module Dependencies and Relationships (verified by import statements)

- `snake_game.py` imports from `game_logic`: GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, GRID_PIXEL_HEIGHT, SCORE_BAR_HEIGHT, UP, DOWN, LEFT, RIGHT, SNAKE_COLORS, check_wall_collision, check_self_collision, get_next_head, calculate_new_score, is_valid_food_position, is_valid_mine_position, spawn_mine. It also imports `pygame, random, sys, math`.
- `snake_game_tkinter.py` imports `tkinter`, `tkinter.font`, `winsound`, `random`, `time`, `os`, and `from leaderboard import HighScoreManager`. It does NOT import game_logic.
- `snake_game_console.py` imports `random`, `os`, `time` only. No internal imports.
- `snake_game.html` is self-contained - all JavaScript is inlined within the HTML file.
- `game_logic.py` imports `random` only. No internal imports.
- `leaderboard.py` imports `json`, `os`, `datetime`. No internal imports.
- `tests/test_game_logic.py` imports from `game_logic`.
- `tests/test_smoke.py` imports from `game_logic`.
- `tests/conftest.py` defines pytest fixtures referencing constants from `game_logic`.
- `test_leaderboard.py` imports from `leaderboard`.
- `test_snake_game_tkinter_display.py` imports a `format_leaderboard_message` symbol from `snake_game_tkinter` (and uses `unittest.mock` to patch display).
- `test_food_color.py` reads `snake_game.py` source as text and uses `re` to assert the FOOD_COLOR tuple - it does NOT import the module.
- `verify_color.py` imports from `snake_game` and prints the resolved FOOD_COLOR value.

Dependency graph:
```
                    +------------+
                    | game_logic |<--+ tests/test_game_logic.py
                    +------------+   + tests/test_smoke.py
                          ^
                          |
                  +---------------+
                  | snake_game.py |   (Pygame)
                  +---------------+
                          ^
                          |
                  verify_color.py
                  test_food_color.py (textual parse only)

+------------+
| leaderboard| <--- snake_game_tkinter.py
+------------+ <--- test_leaderboard.py

snake_game_tkinter.py <--- test_snake_game_tkinter_display.py

snake_game_console.py    (no dependents)
snake_game.html          (no dependents)
```

## 3. Code Organisation Patterns

- One file per game implementation; no class-package hierarchy.
- Shared logic confined to `game_logic.py` and `leaderboard.py`.
- Module-level constants block at the top of each runtime file; class definitions follow; module-level `main()` (or equivalent loop) at the bottom guarded by `if __name__ == "__main__":` in Python files.
- Comments are grouped into named sections (e.g. "Mine Detonation Storm constants", "Invincibility Power-Up constants") for navigability.
- Feature work is tracked in standalone folders (`flashing-mines/`, `mine-detonation-storm/`) containing the design plan, build guide, task checklist, user story, and post-implementation lessons. These are process artefacts, not runtime code.
- Backup files use `.bak`, `.bak-mds`, `.bak-pre-white-food` suffixes - manual snapshots preceding major feature changes.

## 4. Entry Points and Main Flows

| Entry point | Invocation | Loop driver |
|---|---|---|
| `snake_game.py` | `python snake_game.py` or `run_pygame_version.bat` | `while True` with pygame.time.Clock and dt-based timing |
| `snake_game_tkinter.py` | `python snake_game_tkinter.py` or `run_game.bat` | `root.after(ms, callback)` recursive scheduling |
| `snake_game_console.py` | `python snake_game_console.py` | `while True` with blocking `input()` between renders |
| `snake_game.html` | `start snake_game.html` or `run_web_game.bat` | `setInterval(tick, gameSpeed)` plus `setTimeout` for phase transitions |
| Pygame test suite | `pytest` or `pytest.bat` | Pytest collects only `tests/` per `pytest.ini` |
| Leaderboard / display / colour tests | `python test_leaderboard.py` etc. | Each file ends with `unittest.main()` |

## 5. Configuration and Environment Setup

- `requirements.txt`: pygame==2.5.2, pytest.
- `pytest.ini`: single key `[pytest]` `testpaths = tests`.
- No `.env`, no `setup.py`, no `pyproject.toml`, no `package.json`, no `tsconfig.json`, no `Pipfile`.
- No environment variables consumed by source code (verified by absence of `os.environ.get` / `os.getenv` calls).
- Hard-coded absolute paths exist in the codebase:
  - `snake_game.py` line 53: `INVINCIBILITY_MUSIC_PATH = r"C:\Users\GrahamSaunders\Downloads\snake_game_v1.1.0\music\chiptune_triumphant.wav"`
  - `snake_game_tkinter.py`: similar hard-coded music path (see code.md).
  - `pytest.bat`: `C:\Users\GrahamSaunders\AppData\Local\Programs\Python\Python314\Scripts\pytest.exe`
  - `README.md` references `cd C:\cursor\snake_game` (stale instruction).

## 6. Build and Deployment Structure

There is no build pipeline.

- Python code is run directly via the interpreter; no compilation, no bundling, no virtualenv configuration in the repo.
- The HTML version requires no build - it is served from the filesystem by the user's browser.
- Distribution is by source-only (clone or copy the folder; double-click the appropriate `.bat` or `.html`).
- Persistence is a single JSON file (`highscores.json`) created on first leaderboard write.
- No deployment targets, no Docker, no CI workflow files (no `.github/workflows/`, no `.gitlab-ci.yml`, no `azure-pipelines.yml`).

## 7. Cross-references

- `architecture.md` — describes the runtime topology corresponding to the entry-point files listed in section 1.
- `code.md` — function and class detail for each module listed in section 2.
- `dataflow.md` — describes how the modules connected by the dependency graph in section 2 exchange data.
- `risk.md` — every defect catalogued there points back to the exact file in the inventory in section 1.
- `code.md` section 8 — explains which of the files in section 1 are exercised by the test suite.
- `decisions.md` — historical record of the feature folders (`flashing-mines/`, `mine-detonation-storm/`) listed in section 1.
