# Code Context Pack

Verified code patterns, conventions, and critical paths across the Snake Game codebase.

## 1. Key Functions and Classes (verified from source)

### game_logic.py (shared, used by Pygame implementation and tests)

- check_wall_collision(head, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT) -> bool
  - Returns True if head x/y is outside [0, grid_width) x [0, grid_height).
- check_self_collision(head, body) -> bool
  - Returns True iff head is found in body[1:].
- get_next_head(head, direction) -> tuple
  - Computes (head_x + dir_x, head_y + dir_y). No bounds wrapping.
- calculate_new_score(current_score) -> int
  - Returns current_score + 1. (Trivial helper; centralised for testability.)
- is_valid_food_position(pos, snake_body) -> bool
  - Returns pos not in snake_body.
- is_valid_mine_position(candidate, snake_body, snake_direction, food_pos, mines) -> bool
  - Rejects candidates that are on snake body, within Manhattan distance 10 of any snake segment, on the snake projected forward path until it exits the grid, equal to the food position, or already in the mines list.
- spawn_mine(mines, snake_body, snake_direction, food_pos, score) -> None
  - Mutates the mines list in place. Target count is 1 + score // 5. Makes up to 1000 random attempts per mine; silently skips if a valid slot is not found.

### leaderboard.py - class HighScoreManager

Constructor: HighScoreManager(filepath="highscores.json"). filepath is stored as instance attribute.

Module constants: SCHEMA_VERSION = 2, VALID_NAME_MAX_LENGTH = 20.

Methods:
- _default_stats() -> dict
  - Returns {"food_eaten": 0, "mine_shrinks": 0, "invincibility_count": 0}.
- migrate_legacy_entries(entries) -> list
  - Each entry dict is merged with default stats; entry values take precedence (partial migration safe).
- _unwrap_scores(raw)
  - If raw is dict with scores key, returns raw["scores"]; if raw is list, returns migrate_legacy_entries(raw); else returns [].
- load_scores()
  - If file missing, returns []. Reads JSON. If JSON root is a list (legacy), migrates and immediately calls save_scores to persist v2 envelope (one-time upgrade). On JSONDecodeError or IOError returns [].
- save_scores(scores)
  - Writes {"schema_version": 2, "scores": scores} with indent=2. Returns True on success; False on IOError or OSError.
- validate_name(name)
  - Returns True iff 1 <= len(name) <= 20 AND name.isalnum().
- is_high_score(score)
  - True if fewer than 10 scores stored, else score > scores[-1]["score"].
- add_score(score, name, food_eaten=0, mine_shrinks=0, invincibility_count=0)
  - Raises ValueError if name fails validation. Uppercases name. Stamps date with datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"). Appends entry, sorts descending by score, truncates to top 10, persists. On save failure, returns the previously-loaded scores rather than the in-memory list (best-effort durability).
- get_leaderboard()
  - Returns load_scores() (top 10 sorted by score descending after sorting on insert).

### snake_game.py (Pygame) - principal classes

Class Snake:
- Attributes: body (list of (x, y) tuples, head at index 0), direction (UP/DOWN/LEFT/RIGHT), grow (bool), animation_frames=5, current_frame, prev_head, next_head, color_index.
- Methods: move (interpolates over animation_frames before committing the new head), change_direction (prevents direct reversal by comparing negated tuple), check_collision (wall + self check on next_head), eat_food (uses next_head equality), draw.

Class Food:
- Attributes: position. Method: respawn(snake_body) - random until is_valid_food_position is True.

Module-level state: storm phase machine (phase: "border_flash" | "warning" | "explosion" | "idle"), invincibility_active, invincibility_time_remaining, mine flash accumulator, etc. Updated each tick in the main loop with a dt computed from pygame.time.Clock.

### snake_game_tkinter.py - SnakeGame class

Single class SnakeGame owns the root window, the Canvas, the score label, and all game state (snake_body, snake_direction, food_pos, mines, mine_flash_state, storm_phase, storm_phase_start, invincibility_active, etc.).

Notable methods:
- reset_game(): re-initialises all gameplay state.
- on_key(event): direction change; rejects reversal.
- move_snake(): the per-tick update; calls draw at the end and schedules the next tick via root.after.
- format_leaderboard_message(entries) -> str: pure helper (no UI), tested by test_snake_game_tkinter_display.py. Returns a monospaced text block ranking score, name, date, food_eaten, mine_shrinks, invincibility_count.
- _show_leaderboard_window(): opens a Toplevel with a monospaced widget displaying format_leaderboard_message output.

Persistence: at game over the SnakeGame creates a HighScoreManager and calls is_high_score(score), then prompts for a name if qualified.

### snake_game_console.py - Snake class (reduced)

Snake class without animation interpolation; eat_food rotates color_index modulo len(SNAKE_COLORS). Movement uses modulo wrapping ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT) - this is the only implementation that wraps instead of colliding with walls.

Module-level: tick-based timing (WARNING_TICKS=3, EXPLOSION_TICKS=1, INVINCIBILITY_TICKS=100). The terminal is cleared each tick with os.system("cls" if os.name == "nt" else "clear").

Rules splash: `show_rules_screen()` is defined at line 211 and is invoked as the first statement of `main()` at line 228 (verified by line read). This is the **only** runtime where the rules splash is actually displayed at start-up — the Pygame and Tkinter implementations both define equivalent functions but never call them (see `risk.md` section 5b "snake_game.py rules splash defined but never drawn" and "snake_game_tkinter.py ships pause and rules screens that nothing invokes"). Note that the file is currently dead because of the indentation defect in `risk.md` section 5b ("snake_game_console.py does not even parse"); once that is fixed, this start-up splash is what the player will see first.

### snake_game.html (JavaScript)

All logic in a single inline script. Module-level constants for grid, colors, timings. State held in top-level let variables (snake, food, mines, score, gameLoop, etc.). Drawing dispatched to ctx.fillRect for each cell. Flash and storm phases use setTimeout to schedule transitions; the master tick uses setInterval(tick, gameSpeed).

## 2. Important Algorithms and Business Logic

### Mine spawning (game_logic.spawn_mine, plus inline equivalents in Tkinter/Console/HTML)

Target mine count = 1 + score // 5. New mines must satisfy is_valid_mine_position - in particular:
- Manhattan distance from every snake segment must exceed 10.
- The candidate must not lie on the snake projected forward path (the straight ray cast from head in current direction until it exits the grid).
- Must not coincide with food or an existing mine.
Up to 1000 random attempts per mine; if exhausted, the mine is silently skipped (the next call will retry). This is the documented constraint from flashing-mines/flashing-mines-plan.md and confirmed in source.

### Mine flashing

Pygame: real-time accumulator; toggles between MINE_COLOR_A (red) and MINE_COLOR_B (light grey) every MINE_FLASH_INTERVAL (0.2 s).
Tkinter: same 0.2 s period implemented through canvas item recolouring on each tick.
HTML: setInterval timed identically.
Console: no flash (static character M) - explicitly noted in code comments as a console limitation.

### Mine Detonation Storm (MDS-001) state machine

Trigger: total mine count on board >= STORM_TRIGGER_COUNT (10). All four implementations replicate the same logical machine.

Phases:
1. border_flash: window border alternates between STORM_BORDER_COLOR_A (red) and STORM_BORDER_COLOR_B (black) every STORM_BORDER_FLASH_INTERVAL (0.2 s) for an introductory beat.
2. warning: the next mine to detonate is highlighted with a flashing warning marker for WARNING_DURATION (3.0 s in Pygame; 3 ticks in Console).
3. explosion: a 3x3 blast zone centred on the mine renders for EXPLOSION_DURATION (1.0 s in Pygame; 1 tick in Console) using the EXPLOSION_COLORS palette.
4. Snake death within the blast zone (unless invincibility is active).
5. Bonus food spawns per detonation as described in mine-detonation-storm/user-story.md AC-7.
6. Storm ends when all mines have detonated; the cycle returns to idle.

### Invincibility Power-Up

Trigger: eating a super-food (special food that flashes on Pygame/Tkinter/HTML; static $ glyph on Console). When active for INVINCIBILITY_DURATION (10.0 s; 100 ticks on Console):
- Snake colour rendered as INVINCIBILITY_COLOR (yellow / (255,255,0)).
- Mine collisions are ignored.
- An audio cue plays via winsound (Tkinter), pygame.mixer (Pygame), or HTMLAudioElement (HTML). The Console implementation is silent.

**Pygame availability constraint (verified, undocumented before this audit):** in `snake_game.py` the only branch that sets `super_food_position` to a non-`None` value is lines 367-376 — inside the warning-to-explosion transition of the Mine Detonation Storm. There is no normal-play spawn path. Consequently the Invincibility Power-Up on the Pygame runtime can **only** become available during an MDS event (when `super_food_mine_counter == super_food_mine_index`). This is a behavioural divergence from the Tkinter and HTML runtimes, where the super-food has independent spawn pathways. See `dataflow.md` section 5 for the data-flow view.

### Leaderboard insert

Sort-then-truncate (leaderboard.add_score): list.append, sort by score descending, slice [:10]. Top 10 only. Date stored as UTC ISO-8601 with the trailing +00:00 replaced by Z.

## 3. Code Patterns and Conventions

- Snake-case function and variable names throughout Python files.
- ALL_CAPS module-level constants.
- Docstrings on every public function in game_logic.py and every public method in leaderboard.py.
- if __name__ == "__main__": guard at the bottom of every executable Python file.
- Inline comments in named sections for feature groupings (e.g. "# Mine Detonation Storm constants", "# Invincibility Power-Up constants").
- Raw-string literals (r"...") used for Windows absolute paths to avoid escape interpretation.
- ANSI escape sequences kept as named module constants in snake_game_console.py.
- HTML/JS uses camelCase for variables and lowercase const/let/function declarations.
- No type hints anywhere in the codebase.
- Forward references inside `main()`: `snake_game.py` line 311 calls `_stop_invincibility_music()` before its definition at line 562. Legal because Python resolves names at call time, not at function-definition time, but it surprises readers expecting top-down ordering. (Audit cross-ref: `decisions.md` ADR pattern note.)

## 4. Critical Code Paths and Workflows

### Cold start
1. Interpreter loads module-level constants and class definitions.
2. main / SnakeGame() constructor initialises display surface or root window.
3. Initial snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)] facing RIGHT; initial score = 0; mines list is empty.
4. First food spawned via is_valid_food_position loop.
5. Main loop begins.

### Per-tick path (the hot path)
input -> direction update -> snake.move -> wall check -> self check -> food check (with possible super-food / mine respawn) -> mine collision check -> storm state-machine tick -> render frame.

### Game over path
1. set running = False (Pygame) or stop scheduling root.after (Tkinter) or clearInterval (HTML).
2. Tkinter only: HighScoreManager.is_high_score(score); if True, prompt for name via tkinter.simpledialog; call add_score(score, name, food_eaten, mine_shrinks, invincibility_count); show leaderboard window.
3. Display GAME OVER text. Restart on Space (where supported).

## 5. Error Handling and Validation Patterns

- HighScoreManager.load_scores catches json.JSONDecodeError and IOError; returns empty list on failure.
- HighScoreManager.save_scores catches IOError and OSError; returns False on failure.
- HighScoreManager.add_score raises ValueError with a descriptive message when the name is invalid; the Tkinter caller is expected to validate the name before calling, but the layered defence remains.
- spawn_mine bounds the random search at 1000 attempts to avoid an infinite loop on a saturated grid; failure is silent by design.
- The Pygame implementation guards against direct direction reversal in Snake.change_direction by comparing the negated tuple against the current direction.
- No try/except in the per-tick render or input paths - errors propagate and crash the loop (intentional for visibility during development).
- No input sanitisation needed for keyboard input - direction events are restricted by event type filtering, not by content checks.

## 6. Performance-Critical Sections

- Per-tick rendering loop is the dominant cost in all implementations.
- Pygame uses pygame.time.Clock(60) and computes dt = clock.tick(60) / 1000 each frame; with sub-step animation (animation_frames = 5) the logical tick rate is approximately 12 moves per second.
- Console implementation re-renders the full screen each tick (os.system clear plus a print of every row). This dominates wall-clock time on the console runtime.
- HTML setInterval period is set by a let variable named gameSpeed (verified in source); tick logic is constant-time relative to snake length and mine count.
- Mine spawning random search is O(attempts) per mine; with the 1000 cap and small grids this is bounded.
- The Manhattan distance test in is_valid_mine_position is O(len(snake_body)) per candidate; combined with the up-to-1000 attempts this is the worst-case CPU spike on each food-eaten event.
- highscores.json is rewritten in full on every score insert; with at most 10 entries the I/O is trivial.

## 7. Notable Implementation Hazards Found in Source

- snake_game.py line 53: INVINCIBILITY_MUSIC_PATH is a hard-coded absolute Windows path under C:\Users\GrahamSaunders. Will fail on any other user account or operating system.
- snake_game_tkinter.py has the equivalent hard-coded audio path (used by winsound.PlaySound).
- pytest.bat hard-codes the absolute path to a specific user pytest.exe installation.
- README.md instructs cd C:\cursor\snake_game - this is inconsistent with the actual repository location and any other clone destination.
- verify_color.py asserts FOOD_COLOR == (100, 200, 255) in its messaging, but snake_game.py currently sets FOOD_COLOR = (255, 255, 255) (white). The script is therefore out of date relative to the source.
- test_food_color.py reads snake_game.py as text and uses a regex to assert the colour - any reformatting of that single line would break the test even if behaviour is unchanged.
- **snake_game.py line 49 / 551**: `SUPER_FOOD_COLOR_B` is defined; `SUPER_FOOD_COLOR_A` is referenced at line 551 inside `draw_super_food` but is **never defined**. First call with `flash_state` truthy raises `NameError`. See `risk.md` section 5b.
- **snake_game.py line 477**: `draw_pause_overlay(screen)` is called inside the `if paused and not game_over:` branch, but the function is **never defined** anywhere in the repository. See `risk.md` section 5b.
- **snake_game_console.py lines 287, 290-291**: indentation errors prevent the file from parsing. `snake.move()` is incorrectly inside the super-food-collision branch; `storm_phase_ticks -= 1` follows an `if not paused and storm_active:` header at the same indent level, producing `IndentationError`. See `risk.md` section 5b.
- **snake_game_tkinter.py lines 513, 521**: `toggle_pause` and `_draw_rules` are defined but have **no key binding** and **no caller** respectively. Pause and rules screen are unreachable from gameplay. `self.show_rules = True` at line 166 is dead state (no other read or write anywhere in the file; verified by `Grep`). See `risk.md` section 5b.
- **snake_game_tkinter.py lines 15 / 399**: `FOOD_COLOR = '#FF69B4'` (hot pink) directly contradicts the inline comment on line 399 (`# Draw food (ALWAYS YELLOW per .cursorrules)`). The `.cursorrules` file does not actually pin food colour to yellow; the comment is an inherited claim from an earlier revision.
- **snake_game.html lines 344, 386, 737**: `paused` and `showRules` are assigned without `let`, `const`, or `var`. Works in non-strict mode by auto-creating window globals; raises `ReferenceError` under strict mode. See `risk.md` section 5b.
- **snake_game.py line 208 (definition) / no call site**: `draw_rules_screen(screen)` is defined and the `show_rules = True` flag at line 268 swallows the first key press, but the draw block (lines 456-479) never invokes the function. The Pygame rules splash is unreachable. See `risk.md` section 5b.
- **snake_game.py lines 382-399**: the phase-2 → next-mine transition for the Mine Detonation Storm is nested inside the `for dy in range(-1, 2):` blast-cell iteration loop. The `if storm_queue: ... else: ...` block at lines 388-399 fires on each iteration of the inner loop rather than once per explosion frame, breaking the storm phase machine on the first explosion. Verified by line read; the indent of line 388 sits inside `for dy` rather than at the `elif storm_phase == 'explosion':` level. See `risk.md` section 5b.
- **`run_pygame_version.bat` line 2** echoes "Running Pygame version (snake_game.py) with light blue food..." while `snake_game.py` line 21 sets `FOOD_COLOR = (255, 255, 255)` (white). The launcher mis-describes the build; same root cause as `verify_color.py` drift.
- **`README.md` line 75** instructs `cd C:\cursor\snake_game` — this path does not match the actual repository location (`C:\snakegame\BA-Marlin-Test-Repo`). Lines 60-61 / 67-68 advertise a single-colour blue snake and yellow food, both contradicted by source.

## 8. Test Surface and Coverage Matrix (verified)

### 8.1 Test runner configuration

- `pytest.ini` contains a single section:

  ```
  [pytest]
  testpaths = tests
  ```

  Only the `tests/` folder is auto-collected by a bare `pytest` invocation.
- `pytest.bat` is a one-line wrapper that calls `C:\Users\GrahamSaunders\AppData\Local\Programs\Python\Python314\Scripts\pytest.exe`. Hard-coded to the original developer's machine; portable invocation is plain `pytest`.
- There is no `tox.ini`, no `setup.cfg`, no `pyproject.toml`, and no `Makefile` — pytest discovery and configuration are confined to `pytest.ini`.
- There is no CI workflow file anywhere in the repo (`.github/workflows/`, `.gitlab-ci.yml`, etc. all absent). Tests are run manually by the developer.

### 8.2 Pytest-collected suite (`tests/`)

- `tests/__init__.py` — Empty file; present only to mark the folder as a Python package.
- `tests/conftest.py` — Two module-level fixtures: `default_snake_body` returns `[(15, 15), (14, 15), (13, 15)]` (3-segment snake centred on a 30x30 grid); `empty_mines` returns `[]`. No autouse fixtures, no teardown.
- `tests/test_smoke.py` (10 tests, ~55 LOC) — Import-and-type smoke checks for `game_logic`: module import, `GRID_SIZE`/`GRID_WIDTH`/`GRID_HEIGHT`/`WINDOW_WIDTH`/`WINDOW_HEIGHT` are int, `SNAKE_COLORS` non-empty list, initial snake body is list of length-2 tuples, `is_valid_food_position((0,0), …) == True`, score default 0.
- `tests/test_game_logic.py` (~125 LOC) — Five groups of unit tests against pure helpers in `game_logic`: `check_wall_collision` (5), `check_self_collision` (3), `get_next_head` (4 directions), `calculate_new_score` (3), `is_valid_food_position` (3), `is_valid_mine_position` (3). Not covered in this file: `spawn_mine` itself, the projected-forward-path branch of `is_valid_mine_position`, duplicate-mine rejection, food coincidence rejection.

### 8.3 Root-level unittest suites (NOT collected by default)

These files live at the repo root, end with `if __name__ == '__main__': unittest.main()`, and are invoked one at a time via `python <file>`. They are **not** picked up by a bare `pytest` invocation because `testpaths = tests` excludes them.

- `test_leaderboard.py` (~690 LOC) — Three test classes against `leaderboard.HighScoreManager`:
  - `TestLeaderboard` — happy paths: load, save, add_score, sort order, top-10 cap, qualification check, migration of legacy bare-list to v2 envelope, ISO-8601 timestamp shape, idempotent re-load.
  - `TestLeaderboardStatsV2` — verifies `food_eaten`, `mine_shrinks`, `invincibility_count` default to 0, propagate when supplied, survive round-trip.
  - `TestNameLengthBoundary` — boundary cases on the 1–20 alphanumeric constraint: empty, 1-char, 20-char, 21-char, spaces, punctuation, unicode.
  - Coverage: 100% of public methods exercised; I/O failure branches (IOError, OSError, JSONDecodeError) exercised via tempdir fixtures.
- `test_snake_game_tkinter_display.py` (~200 LOC) — Imports `format_leaderboard_message` from `snake_game_tkinter`. Pure-helper region asserts the monospaced string layout against fixed example score lists; display-integration region uses `unittest.mock.patch` to stub `_show_leaderboard_window`. **Gap:** never instantiates Tkinter; no on-screen rendering is verified.
- `test_food_color.py` (~90 LOC) — Three tests, all working by re-reading `snake_game.py` as text and applying `re.search`: asserts the regex captures `(255, 255, 255)`, does not capture `(255, 255, 0)`, and the trailing comment contains "white" (case-insensitive). Fragility: the regex is anchored to a single physical line; any reformatting of that line breaks the test even when behaviour is correct.

### 8.4 Coverage matrix (verified, not inferred)

| Source module | Covered by | Untested surface |
|---|---|---|
| `game_logic.py` | `tests/test_game_logic.py`, `tests/test_smoke.py` | `spawn_mine` itself; projected-forward-path branch; duplicate-mine rejection branch |
| `leaderboard.py` | `test_leaderboard.py` (root-level unittest) | none for public surface |
| `snake_game.py` (Pygame) | `test_food_color.py` (regex over source text only) | every Pygame import, every class, every render function — the runtime code path is wholly unexercised by automated tests |
| `snake_game_tkinter.py` | `test_snake_game_tkinter_display.py` (`format_leaderboard_message` + mocked `_show_leaderboard_window`) | gameplay loop, drawing, key bindings, audio |
| `snake_game_console.py` | none | entirely untested; would not even import today due to the indentation defect documented in section 7 |
| `snake_game.html` | none | the JavaScript and Canvas pipeline have no unit tests; no Playwright/Cypress harness exists |

### 8.5 How to run the full battery

The repo has no aggregator. To exercise every test surface, the operator must run four commands in sequence:

```
pytest
python test_leaderboard.py
python test_snake_game_tkinter_display.py
python test_food_color.py
```

The first command covers `tests/`. Each of the next three exits with the unittest summary; combining them into a single non-zero exit signal requires either a shell wrapper or moving the files into `tests/`.

### 8.6 Recommended ordering for closing the coverage gap

1. Add an `import snake_game_console` smoke test to fail fast on syntactical regressions.
2. Add a Pygame draw-path smoke test (e.g. headless `SDL_VIDEODRIVER=dummy`) that exercises `draw_super_food` and the pause overlay.
3. Move `test_leaderboard.py`, `test_snake_game_tkinter_display.py`, `test_food_color.py` into `tests/` or widen `testpaths` so `pytest` collects them by default.
4. Replace `test_food_color.py`'s regex parse with a direct attribute import once the `pygame` dependency is reliably importable in CI.
5. Delete `verify_color.py` (the regex-based unittest already covers the same assertion correctly).

## 9. Cross-references

- `risk.md` section 5b — every hazard listed in section 7 is enumerated there with the verification method (grep / line read / `ast.parse` attempt) and the prioritised mitigation order.
- `risk.md` section 5c — explains why none of the section-7 hazards are caught by the current test suite.
- `architecture.md` — situates the patterns documented here in the overall four-runtime topology.

