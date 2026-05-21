# Glossary Context Pack

Verified terminology, constants, and identifiers used throughout the Snake Game codebase. Every entry references its source.

## 1. Domain Concepts

- Snake: ordered list of (x, y) grid cells. The cell at index 0 is the head. Moves one cell per logical tick along the current direction vector.
- Food: a single (x, y) grid cell occupied by the consumable. When the snake head lands on it, the snake grows by one segment, the score increases by 1, and a new food position is chosen via is_valid_food_position.
- Mine: a cell that hurts the snake on contact. Mines flash on Pygame/Tkinter/HTML but are static on Console (limitation). Mine collision shrinks the snake and decrements the score unless invincibility is active. Source: flashing-mines/Build.md, snake_game.py constants section, snake_game_console.py MINE_CHAR.
- Super food: a special food that grants invincibility when eaten. Visually flashes on Pygame/Tkinter/HTML; displayed as the dollar sign on Console (CONSOLE_SUPER_FOOD_CHAR = "$").
- Bonus food: food awarded by the Mine Detonation Storm pipeline after each detonation (acceptance criterion **AC-6** in `mine-detonation-storm/user-story.md`; AC-7 covers storm-end conditions). Must be GREEN (0, 255, 0) / `#00FF00` per AC-11. Spawns at the mine centre at the start of explosion Phase 2; persists after the storm ends; can spawn on a cell occupied by snake body.
- Invincibility: time-limited state during which the snake ignores mine collisions and is rendered yellow ((255, 255, 0)). Constants: INVINCIBILITY_DURATION 10.0 seconds (Pygame), INVINCIBILITY_TICKS 100 (Console).
- Mine Detonation Storm (MDS): scripted sequence of mine explosions triggered when the mine count reaches STORM_TRIGGER_COUNT (10). Phases: border_flash, warning, explosion, idle.
- Blast zone: 3x3 grid region centred on a detonating mine; lethal to the snake unless invincibility is active.
- Snake colour palette: 8-entry SNAKE_COLORS list in game_logic.py (Pygame/Tkinter), or ANSI-coded equivalents in snake_game_console.py. Index advances by 1 modulo 8 on every food eaten.

## 2. Code Identifiers and Constants

### Grid and window
- GRID_SIZE = 20 (game_logic.py): pixel size of one grid cell.
- WINDOW_WIDTH = 600 (game_logic.py).
- WINDOW_HEIGHT = 630 (game_logic.py).
- GRID_PIXEL_HEIGHT = 600 (game_logic.py).
- SCORE_BAR_HEIGHT = 30 (game_logic.py).
- GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE = 30 (game_logic.py).
- GRID_HEIGHT = GRID_PIXEL_HEIGHT // GRID_SIZE = 30 (game_logic.py).
- Console-only: GRID_WIDTH = 20, GRID_HEIGHT = 20 (snake_game_console.py).

### Directions
- UP = (0, -1), DOWN = (0, 1), LEFT = (-1, 0), RIGHT = (1, 0). Shared verbatim by game_logic.py and snake_game_console.py.

### Colours (Pygame snake_game.py)
- BLACK (0, 0, 0)
- WHITE (255, 255, 255)
- FOOD_COLOR (255, 255, 255) - white food, latest revision (line 21).
- DARK_BLUE (0, 0, 128) - background gradient.
- LIGHT_BLUE_SHINE (180, 230, 255) - food shine highlight.
- LIGHT_YELLOW (255, 255, 200) - super-food shine highlight.
- GREEN (0, 255, 0) - bonus foods only.
- SUPER_FOOD_COLOR_B (0, 0, 0) - super-food off-flash colour. `SUPER_FOOD_COLOR_A` is **referenced at line 551 but never defined** — this is a runtime `NameError` (see `risk.md` section 1.1).

### Food colour across implementations (cross-runtime discrepancy register)

The README claims food is "Yellow (always)". Reality, verified line by line:

| File | Line | Value | Visible colour |
|---|---|---|---|
| `snake_game.py` | 21 | `(255, 255, 255)` | white |
| `snake_game_tkinter.py` | 15 | `'#FF69B4'` | hot pink |
| `snake_game.html` | 119 | `'#FFFFFF'` | white |
| `snake_game_console.py` | (printed under `\033[97m`) | bright-white ANSI | white |

The Tkinter file additionally contains a comment on line 399 that reads `# Draw food (ALWAYS YELLOW per .cursorrules)` even though the constant is hot pink. This is documented in `risk.md` section 3.3.

### Snake colour across implementations (cross-runtime discrepancy register)

The README claims the snake is "Blue (always)". Reality: every implementation uses an 8-entry rotating palette that advances on each food eaten:

- `game_logic.py` defines `SNAKE_COLORS` as an 8-entry RGB list, used by `snake_game.py`.
- `snake_game_tkinter.py` defines its own 8-entry hex-string palette.
- `snake_game_console.py` defines an 8-entry ANSI colour-code palette.
- `snake_game.html` defines an 8-entry CSS-string palette.

No implementation hard-codes a single blue colour for the snake.

### Mine and storm colours
- MINE_COLOR_A (255, 0, 0) - bright red.
- MINE_COLOR_B (200, 200, 200) - light grey (Pygame default secondary).
- STORM_BORDER_COLOR_A (255, 0, 0).
- STORM_BORDER_COLOR_B (0, 0, 0).
- EXPLOSION_COLORS palette: red, orange, yellow, white, ember-orange.

### Timing
- MINE_FLASH_INTERVAL = 0.2 s (Pygame).
- STORM_BORDER_FLASH_INTERVAL = 0.2 s.
- WARNING_DURATION = 3.0 s; WARNING_FLASH_INTERVAL = 0.2 s.
- EXPLOSION_DURATION = 1.0 s.
- INVINCIBILITY_DURATION = 10.0 s (Pygame); INVINCIBILITY_TICKS = 100 (Console); SUPER_FOOD_FLASH_INTERVAL = 0.25 s.

### Storm triggers
- STORM_TRIGGER_COUNT = 10 (all four implementations).

### Console-specific
- MINE_CHAR = "M"; CONSOLE_WARNING_CHAR = "!"; CONSOLE_EXPLOSION_CHAR = "*".
- CONSOLE_STORM_LABEL = "*** DETONATION STORM ***".
- CONSOLE_INVINCIBLE_LABEL = "*** INVINCIBLE ***".
- WARNING_TICKS = 3; EXPLOSION_TICKS = 1.
- RESET_COLOR = ANSI escape "\033[0m".
- ANSI palette entries: bright blue, cyan, green, yellow, orange, red, magenta, pink (see snake_game_console.py).

### Leaderboard (leaderboard.py)
- SCHEMA_VERSION = 2.
- VALID_NAME_MAX_LENGTH = 20.
- Default filepath: "highscores.json".
- Default stats dict: {"food_eaten": 0, "mine_shrinks": 0, "invincibility_count": 0}.

## 3. Module / File Names

- game_logic.py: shared pure-function logic (Pygame plus tests).
- leaderboard.py: HighScoreManager class.
- snake_game.py: Pygame implementation entry point.
- snake_game_tkinter.py: Tkinter implementation entry point.
- snake_game_console.py: Console implementation entry point.
- snake_game.html: Browser implementation; self-contained HTML+CSS+JS.
- highscores.json: persistent leaderboard data file.
- pytest.ini: pytest configuration (testpaths=tests).
- pytest.bat / run_game.bat / run_pygame_version.bat / run_web_game.bat: Windows convenience launchers.
- music/chiptune_triumphant.wav: invincibility audio asset.

## 4. Test Files

- tests/test_game_logic.py: pytest suite covering game_logic.py.
- tests/test_smoke.py: pytest smoke/import test.
- tests/conftest.py: pytest fixtures (default_snake_body, empty_mines).
- tests/__init__.py: empty file (treats tests as a package).
- test_leaderboard.py: unittest suite for HighScoreManager (classes TestLeaderboard, TestLeaderboardStatsV2, TestNameLengthBoundary).
- test_snake_game_tkinter_display.py: unittest suite for format_leaderboard_message and the display flow (mocks _show_leaderboard_window).
- test_food_color.py: unittest suite that reads snake_game.py as text via re and asserts the FOOD_COLOR tuple.
- verify_color.py: standalone diagnostic script (not a test); imports snake_game and prints the resolved FOOD_COLOR value.

## 5. Feature Folder Artefacts

- flashing-mines/Build.md, flashing-mines-plan.md, ToDo.md, post-implementation-lessons-learned.md: design and build trail for the Flashing Mines feature.
- mine-detonation-storm/Plan.md, Build.md, ToDo.md, user-story.md, feature.json, run-log.md: design and build trail for MDS-001.
- user-story.md acceptance criteria identifiers used in this codebase: AC-1 through AC-11. AC-7 specifically defines the bonus-food-per-detonation rule.

## 6. Configuration Fields and Parameters

- HighScoreManager constructor argument filepath (defaults to highscores.json).
- HighScoreManager.add_score keyword arguments: score, name, food_eaten=0, mine_shrinks=0, invincibility_count=0.
- spawn_mine parameters: mines (mutated in place), snake_body, snake_direction, food_pos, score.
- is_valid_mine_position parameters: candidate, snake_body, snake_direction, food_pos, mines.

## 7. Error Codes and Exception Messages

- ValueError raised by HighScoreManager.add_score when validate_name fails. Message: "Invalid name '<name>': must be 1-20 alphanumeric characters".
- json.JSONDecodeError caught by load_scores; treated as empty leaderboard.
- IOError / OSError caught by save_scores; returns False to signal partial-failure.
- HTTP and GitHub API codes referenced in Auto-PR-Solution.md (operational tooling, not gameplay): 401 Bad credentials, 422 Unprocessable Entity, 404 Not Found.

## 8. Acronyms and Abbreviations

- ADR: Architectural Decision Record (decisions.md).
- AC-n: Acceptance Criterion n in a user story (e.g. AC-7 in mine-detonation-storm/user-story.md).
- MDS / MDS-001: Mine Detonation Storm; feature identifier used in feature.json and run-log.md.
- AAFM: name of the MCP-based PR-automation toolchain referenced in Auto-PR-Solution.md and .aafm-config.md (.aafm-config.md is documented in past notes but not present in the live working tree at the time of this Context Pack).
- PAT: Personal Access Token (GitHub) - context only, no PATs in the repo.
- HUD: Heads-Up Display (HUD_INVINCIBILITY_OFFSET = 5 * GRID_SIZE in snake_game.py).
- v2 envelope: the JSON shape {"schema_version": 2, "scores": [...]} used by the leaderboard file.

## 9. Cross-reference

- `risk.md` — every defect catalogued in this glossary's discrepancy registers (food colour, snake colour, `SUPER_FOOD_COLOR_A`) is enumerated with file:line citations and triage priority.
- `code.md` section 8 — explains exactly which of the terms above are covered by tests and which are not (the unreachable Tkinter `_draw_rules`, `toggle_pause`, and the entire Pygame draw path are untested).
- `decisions.md` — historical record of the user stories whose AC-n labels appear in section 5.
- `structure.md` — master inventory of every file consulted when writing this glossary.

## 9. Mine Detonation Storm Acceptance Criteria (MDS-001)

Acceptance criteria AC-1 through AC-11 from mine-detonation-storm/user-story.md,
reproduced for reference. All 11 were marked PASS at delivery (2026-03-06+).

- **AC-1** Trigger: active mine count reaches 10 on a food-eat event; only one storm
  at a time; re-triggers only after storm ends and threshold is reached again.
- **AC-2** Border flash: thin solid border alternating bright red and black at 0.2 s
  on all four sides. Console shows `*** DETONATION STORM ***` in bright red ANSI.
- **AC-3** Sequence: mines detonate in random order (shuffled once at storm start).
  Per mine: 3 s warning (Phase 1) + 1 s explosion (Phase 2).
- **AC-4** Visual: Phase 1 flashes the single mine cell with EXPLOSION_COLORS every
  0.2 s. Phase 2 fills a 3x3 area with the palette, each cell independently per frame.
  Console: `!` yellow for Phase 1; `*` yellow for Phase 2 (one tick).
- **AC-5** Kill condition: snake head in any Phase 2 cell ends the game unless
  invincibility is active. Phase 1 applies normal mine-hit damage (shrink 3, score -3).
- **AC-6** Bonus food: one green food (0,255,0 / #00FF00) spawns at the mine centre
  at Phase 2 start. Persists after storm; can spawn on snake body.
- **AC-7** Storm end: when detonation queue is empty and no phase is in progress, or
  immediately on snake death.
- **AC-8** New mines during storm are not appended to the active queue. Trigger is not
  re-evaluated while a storm is active.
- **AC-9** Restart clears all storm state: active flag, queue, phase, current mine,
  elapsed timers, flash accumulators, bonus_foods.
- **AC-10** Platform-native timing: Pygame uses dt accumulator; Tkinter uses root.after;
  HTML/JS uses setTimeout/setInterval; Console uses integer tick counters.
- **AC-11** Bonus food must be green; snake colour progression must not be affected.

Source: mine-detonation-storm/user-story.md; `decisions.md` ADR-024.
