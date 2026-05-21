# Architecture Context Pack

System architecture overview for the Snake Game codebase.

## 1. System Architecture Overview

This is a single-repository, multi-implementation game project. Four independent game implementations target three runtimes:

- Pygame (snake_game.py) - desktop, hardware-accelerated 2D
- Tkinter (snake_game_tkinter.py) - desktop, stdlib GUI
- Console (snake_game_console.py) - terminal text mode
- HTML/JavaScript (snake_game.html) - browser, Canvas 2D

The Pygame implementation is the only one that imports the shared module game_logic.py. The other three implementations re-implement the equivalent logic inline. There is no shared object hierarchy across runtimes.

### Dominant Design Patterns (verified)

- Module-level constants for all tuning parameters (grid, colors, timing, durations).
- One Snake class per implementation, encapsulating body list, direction tuple, grow flag, and color index.
- One Food class only in the Pygame implementation; other implementations use a bare position tuple.
- Single main loop per runtime that interleaves input handling, state update, collision resolution, and rendering.
- Tick-driven timing on console (integer counters); wall-clock seconds on Pygame; root.after callbacks on Tkinter; setInterval / setTimeout on HTML.
- Pure-function helpers in game_logic.py with no side effects beyond the documented in-place mutation of the mines list in spawn_mine.

## 2. Key Components and Their Relationships

### Runtime layer (4 entry points)

snake_game.py (Pygame): imports game_logic; uses pygame for window, input, sound, blit operations.
snake_game_tkinter.py: stdlib tkinter Canvas, key bindings on root window, root.after for scheduling, winsound for audio (Windows-only).
snake_game_console.py: stdlib only; os.system("cls" / "clear") plus ANSI escape sequences; blocking input() for direction commands.
snake_game.html: vanilla JavaScript + HTML5 Canvas; setInterval drives the game tick; setTimeout drives flash phase transitions.

### Logic layer (1 module, shared by Pygame only)

game_logic.py exposes pure functions plus constants:
- Constants: GRID_SIZE=20, GRID_WIDTH=30, GRID_HEIGHT=30, WINDOW_WIDTH=600, GRID_PIXEL_HEIGHT=600, WINDOW_HEIGHT=630, SCORE_BAR_HEIGHT=30
- Direction vectors: UP, DOWN, LEFT, RIGHT
- SNAKE_COLORS: 8-entry RGB palette
- Functions: check_wall_collision, check_self_collision, get_next_head, calculate_new_score, is_valid_food_position, is_valid_mine_position, spawn_mine

Note that the console implementation has its own constants GRID_WIDTH=20, GRID_HEIGHT=20 (different grid size from the Pygame/Tkinter/HTML 30x30 grid).

### Persistence layer (1 module)

leaderboard.py defines HighScoreManager, used only by snake_game_tkinter.py at present. It persists top-10 scores to highscores.json using a v2 envelope { schema_version: 2, scores: [...] } and auto-migrates legacy bare-list files on first load.

### Test layer

- pytest tests in tests/ - configured by pytest.ini (testpaths=tests).
- Root-level unittest suites: test_leaderboard.py, test_snake_game_tkinter_display.py, test_food_color.py (not auto-collected by pytest unless invoked directly).
- verify_color.py is a standalone diagnostic script, not a test.

## 3. Data Flow and System Boundaries

### Inbound boundaries
- Keyboard input via pygame.event (Pygame), tkinter bind (Tkinter), input() (Console), addEventListener "keydown" (HTML).
- File reads: highscores.json (leaderboard), C:\Users\GrahamSaunders\Downloads\snake_game_v1.1.0\music\chiptune_triumphant.wav (Pygame invincibility music - hard-coded absolute path), music\chiptune_triumphant.wav (HTML - relative path).

### Outbound boundaries
- Screen rendering (Pygame surface blits, Tkinter Canvas items, ANSI stdout, Canvas2D fillRect).
- File writes: highscores.json (write-through on every add_score).
- Audio playback: winsound.PlaySound (Tkinter), pygame.mixer (Pygame), HTMLAudioElement.play (HTML). Console has no audio.

### Internal flow per tick (uniform across implementations)
1. Process queued input - update next direction (reject reverse).
2. Move snake head one cell along direction; pop tail unless grow flag set.
3. Check wall collision (Pygame, Tkinter, HTML); console wraps via modulo.
4. Check self collision.
5. Check food collision - increment score, set grow, spawn new food, possibly spawn super-food (score gate), possibly spawn mines via spawn_mine.
6. Check mine collision - if invincible, ignore; otherwise shrink snake and decrement score (Flashing Mines feature).
7. Update Mine Detonation Storm phase machine if active (warning -> explosion -> next mine, or border-flash -> end).
8. Render frame.

## 4. Technology Stack and Dependencies

Declared dependencies (requirements.txt):
- pygame==2.5.2
- pytest (unpinned)

Runtime dependencies discovered in source:
- Python stdlib: random, os, sys, math, time, json, datetime, tkinter, winsound, unittest, re
- Browser stdlib: HTML5 Canvas 2D, Web Audio (HTMLAudioElement)

No build system. No package manifest. No CI configuration. No Dockerfile.

Convenience launchers (Windows batch):
- run_game.bat -> py snake_game_tkinter.py
- run_pygame_version.bat -> py snake_game.py
- run_web_game.bat -> start snake_game.html
- pytest.bat -> hard-coded path C:\Users\GrahamSaunders\AppData\Local\Programs\Python\Python314\Scripts\pytest.exe

## 5. Scalability and Performance Considerations (Verified)

- Grid is fixed at compile-time per implementation (30x30 for Pygame/Tkinter/HTML; 20x20 for Console). No dynamic resize.
- Snake body is a Python list; head insert + tail pop is O(1) amortized. Self-collision check is O(n) over body length.
- Mine spawning attempts up to 1000 random candidates per mine; silently skips if exhausted (see spawn_mine in game_logic.py). This bounds CPU per spawn but can silently under-spawn on dense grids.
- Mine count target: 1 + score // 5 (game_logic.spawn_mine).
- Pygame snake animation uses sub-step interpolation: 5 frames per logical move (Snake.animation_frames = 5).
- Console implementation re-clears the entire terminal each tick via os.system - this is the dominant cost in that runtime and limits practical tick rate.
- Mine Detonation Storm trigger is total mine count >= 10 (STORM_TRIGGER_COUNT, all four implementations).
- Storm explosions occupy a 3x3 blast zone per mine; with N mines on screen this is O(N) blast cells.

## 6. Integration Patterns and External Services

- No network calls anywhere in the codebase.
- No external API consumption.
- No telemetry / analytics.
- No authentication.
- The only external resources are:
  - highscores.json - local filesystem JSON file (read/write).
  - music/chiptune_triumphant.wav - local audio asset (read-only).

The codebase is fully offline and self-contained at runtime. The only operational "integration" documented in the repo is the Auto-PR-Solution.md note about the AAFM MCP server interaction with the GitHub REST API for the developer tooling pipeline - that is not part of the shipped game.

## 7. Architectural Integrity Risks (round-2 enrichment)

The four-runtime topology described in section 1 assumes feature parity across implementations. Round-2 audit found that this assumption no longer holds for several constants and code paths. The discrepancies do not change the architecture but they degrade its guarantees:

- The Console implementation does not parse (`risk.md` section 5b). The architectural claim "four runtimes" is currently true on paper only; in practice the Console runtime is offline.
- The Pygame super-food draw path raises `NameError` on first activation (`risk.md` section 5b). The architectural claim that the Invincibility Power-Up is implemented in all four runtimes is true at the code level but false at the execution level.
- The Tkinter implementation diverges from the others on food colour (hot pink vs white) and ships unreachable pause and rules-splash UI (`risk.md` section 5b).
- The HTML implementation relies on non-strict-mode global auto-creation for `paused` and `showRules` (`risk.md` section 5b). The architecture survives only because the file is loaded as a classic script; a future migration to `type="module"` would break it.
- The Pygame rules splash (`draw_rules_screen`, line 208) is defined and the `show_rules` flag at line 268 silently consumes the first keypress, but the splash is never rendered (`risk.md` section 5b). Combined with the Tkinter `_draw_rules` defect (section 3.2), this means the rules splash is reachable on only one of the four runtimes — the Console runtime — and even there only after the Console parse defect is fixed. The architectural claim "four runtimes share UX" is therefore false for the start-up screen.
- The Pygame Mine Detonation Storm phase machine is mis-nested at `snake_game.py` lines 388-399; the warning-to-explosion transition fires inside the inner blast-cell iteration loop rather than once per explosion frame (`risk.md` section 5b). The architectural claim that the four runtimes implement the same MDS state machine is true at the constant level but degraded at the execution level on the Pygame runtime.

These are captured here so any architectural revision (for example, ADR-001's "future consideration: extract a render-agnostic core") starts from an accurate picture of the current state. See `risk.md` for the full register and `risk.md` section 5b for the prioritised mitigation order.

## 8. Cross-references

- `risk.md` — register of all parity-breaking defects called out in section 7 above.
- `code.md` — function-level detail on every component named in section 2.
- `dataflow.md` — per-tick and per-feature data flow detail used to derive section 3.
- `decisions.md` — historical decision trail (Flashing Mines, Mine Detonation Storm) showing how the current architecture was reached.
- `decisions.md` — the ADR set that codifies the architectural choices summarised in section 1.

## 9. Canonical Rendering Order (all runtimes)

The following draw order is enforced in all four implementations (later layers
paint over earlier ones). Verified against the draw blocks in every runtime.

1. Background.
2. Grid.
3. Storm border (if storm_active) -- red/black flash at 0.2 s.
4. Phase 2 explosion cells (3x3 blast zone, EXPLOSION_COLORS palette, each cell
   independently each render frame).
5. Phase 1 warning mine cell (flashing single cell).
6. Remaining standard mines (red/grey flash at 0.2 s).
7. Bonus foods (green, spawned per detonation).
8. Standard food.
9. Snake.
10. Score and UI.
11. Game over overlay.

Source: mine-detonation-storm/user-story.md AC-4; `decisions.md` ADR-024.

## 10. Rules Splash Cross-Runtime Matrix

Each runtime defines a start-up rules/how-to-play splash. Only two of the four
actually display it at runtime.

| Runtime | Function defined? | Called at start-up? | Evidence |
|---|---|---|---|
| Pygame (`snake_game.py`) | Yes -- `draw_rules_screen` at line 208 | **No** | `show_rules = True` flag (line 268) dismisses on first keypress (lines 276-279) but the draw block (lines 456-479) never calls the function. See `risk.md` section 5b. |
| Tkinter (`snake_game_tkinter.py`) | Yes -- `_draw_rules` at line 521 | **No** | `self.show_rules = True` (line 166) is never read; `_draw_rules` has zero callers. See `risk.md` section 5b. |
| Console (`snake_game_console.py`) | Yes -- `show_rules_screen()` at line 211 | **Yes** | Invoked as first statement of `main()` at line 228. Currently unreachable due to parse error (see `risk.md` section 5b), but the call wiring is correct. |
| HTML (`snake_game.html`) | Yes -- rules-overlay rendering branch | **Yes** | Controlled by `showRules` global (undeclared; see `risk.md` section 5b); the branch is reached in non-strict mode. |

Pygame and Tkinter are regressions: the splash code exists but is unreachable.
Console has correct wiring but is currently dead behind a parse error.
