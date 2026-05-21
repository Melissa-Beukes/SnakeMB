# Plan: Mine Detonation Storm
**Feature ID:** MDS-001  
**Feature Folder:** `mine-detonation-storm/`  
**Depends On:** Flashing Mines feature — must be present and functional in all 4 versions  
**Date:** 2026-03-06  
**Status:** DRAFT — Awaiting Human Review and Approval

---

## 1. Overview

Implement the Mine Detonation Storm event across all 4 independent game versions (`snake_game.py`, `snake_game_tkinter.py`, `snake_game_console.py`, `snake_game.html`): when 10 or more active mines are simultaneously on the grid, trigger a dramatic storm sequence featuring a flashing red/black window border, sequential mine detonations with a 3-second explosion-palette warning flash (Phase 1) and a 1-second 3×3 kill-zone explosion (Phase 2), bonus GREEN food spawned at each detonation, and immediate game-over if the snake head enters any Phase 2 blast cell — as specified in user story MDS-001.

---

## 2. Technical Approach

### 2.1 Foundational Patterns (from existing codebase)

This feature builds directly on the Flashing Mines feature (completed 2026-03-05) and the established patterns documented in `docs/architecture.md`, `docs/code.md`, and `docs/decisions.md`:

| Pattern | Source | Applied Here |
|---------|--------|--------------|
| Module-level UPPERCASE constants | `docs/code.md` Pattern 1 | New MDS constants added at file top |
| Plain list for mine state | ADR-FM-002 | `storm_queue` as plain list of `(x,y)` tuples; `bonus_foods` as plain list |
| Boolean flag-based state | `docs/code.md` Pattern 3 | `storm_active`, `border_flash_state`, `storm_warning_flash_state` |
| Accumulator timing (Pygame) | ADR-FM-001 | `storm_phase_elapsed`, `border_flash_acc`, `storm_warning_flash_acc` |
| `root.after()` scheduling (Tkinter) | ADR-FM-001 | Border flash and warning flash via recursive `root.after()` |
| `setInterval`/`setTimeout` (HTML) | ADR-FM-001 | `borderFlashTimer` (setInterval), `stormWarningFlashTimer` (setInterval), `stormPhaseTimer` (setTimeout) |
| Tick-based timing (Console) | ADR-FM-001, ADR-FM-003 | Phase 1 = 3 ticks, Phase 2 = 1 tick |
| Immediate-mode rendering | `docs/decisions.md` Pattern 2 | Storm border, explosion cells, warning cell drawn every frame |
| `hasattr` guard on timer cancel | IMP-FM-D3 | All new Tkinter `after` IDs cancelled with `hasattr` guard in `reset_game()` |
| Standalone per-file | ADR-007 | No shared code; each version modified independently |
| Food always GREEN | `.cursorrules` Rule 2 | Bonus food: `(0,255,0)` / `#00FF00` — never changes |
| Snake colour unchanged | `.cursorrules` Rule 2 | `color_index` logic untouched |
| Pygame collision uses `next_head` | ADR-FM-004 / IMP-FM-D1 | Phase 2 kill check uses `snake.next_head` in Pygame |
| HTML collision before `unshift` | IMP-FM-D4 | Phase 2 kill check placed before `snake.unshift(head)` |
| Console path projection visited guard | IMP-FM-D2 / C1 | Not directly applicable here, but noted for spawn continuity |

### 2.2 New Constants (all versions)

Added at module top alongside existing mine constants:

```
STORM_TRIGGER_COUNT      = 10
STORM_BORDER_COLOR_A     = (255,0,0)      # '#FF0000' in JS
STORM_BORDER_COLOR_B     = (0,0,0)        # '#000000' in JS
STORM_BORDER_FLASH_INTERVAL = 0.2         # seconds / 200ms
WARNING_DURATION         = 3.0            # seconds / 3000ms
WARNING_FLASH_INTERVAL   = 0.2            # seconds / 200ms
EXPLOSION_DURATION       = 1.0            # seconds / 1000ms
EXPLOSION_COLORS         = [(255,0,0),(255,136,0),(255,255,0),(255,255,255),(255,68,0)]
CONSOLE_WARNING_CHAR     = '!'
CONSOLE_EXPLOSION_CHAR   = '*'
CONSOLE_STORM_LABEL      = '*** DETONATION STORM ***'
```

### 2.3 New State Variables

**Python versions (Pygame, Tkinter, Console):**

| Variable | Type | Initial Value | Description |
|----------|------|---------------|-------------|
| `storm_active` | `bool` | `False` | Storm is in progress |
| `storm_queue` | `list` | `[]` | Remaining mine positions to detonate (shuffled at storm start) |
| `storm_phase` | `str\|None` | `None` | `'warning'` or `'explosion'` |
| `storm_current_mine` | `tuple\|None` | `None` | Mine position currently in warning or explosion phase |
| `storm_phase_elapsed` | `float` | `0.0` | Seconds elapsed in current phase (Pygame/Tkinter) |
| `storm_warning_flash_state` | `bool` | `False` | Current warning flash colour index toggle |
| `storm_warning_flash_acc` | `float` | `0.0` | Accumulator for warning flash timing (Pygame only) |
| `border_flash_state` | `bool` | `False` | Current border colour toggle |
| `border_flash_acc` | `float` | `0.0` | Accumulator for border flash timing (Pygame only) |
| `bonus_foods` | `list` | `[]` | List of `(x,y)` positions for bonus food items |

**JavaScript version:**

| Variable | Type | Initial | Description |
|----------|------|---------|-------------|
| `stormActive` | `bool` | `false` | Storm in progress |
| `stormQueue` | `array` | `[]` | Remaining `{x,y}` mine objects to detonate |
| `stormPhase` | `string\|null` | `null` | `'warning'` or `'explosion'` |
| `stormCurrentMine` | `object\|null` | `null` | Mine position in active phase |
| `stormPhaseTimer` | `timeout ID\|null` | `null` | setTimeout ID for phase transition |
| `stormWarningFlashState` | `bool` | `false` | Warning flash colour toggle |
| `stormWarningFlashTimer` | `interval ID\|null` | `null` | setInterval ID for warning flash |
| `borderFlashState` | `bool` | `false` | Border colour toggle |
| `borderFlashTimer` | `interval ID\|null` | `null` | setInterval ID for border flash |
| `bonusFoods` | `array` | `[]` | `{x,y}` positions of bonus food |

### 2.4 Storm Logic (all versions)

**Trigger check** — evaluated in the food-eat handler (after mine spawn), when `not storm_active`:
```
if len(mines) >= STORM_TRIGGER_COUNT and not storm_active:
    start_storm()
```

**`start_storm()`:**
1. Set `storm_active = True`
2. Shuffle a copy of `mines` into `storm_queue`; remove all mines in the queue from `mines`
3. Start border flash timer
4. Pop first mine from `storm_queue` → set as `storm_current_mine`, set `storm_phase = 'warning'`, reset `storm_phase_elapsed = 0`
5. Start warning flash timer

**Phase transitions (per game tick / accumulator):**
- `storm_phase == 'warning'` and `elapsed >= WARNING_DURATION`:
  → transition to `'explosion'`: reset `elapsed = 0`, spawn bonus food at `storm_current_mine`, start explosion timer
- `storm_phase == 'explosion'` and `elapsed >= EXPLOSION_DURATION`:
  → if `storm_queue` not empty: pop next mine → set `storm_phase = 'warning'`, reset timers/elapsed
  → if `storm_queue` empty: `end_storm()`

**`end_storm()`:**
1. `storm_active = False`, `storm_phase = None`, `storm_current_mine = None`, `storm_phase_elapsed = 0`
2. Cancel all storm timers (border flash, warning flash, phase timers)
3. Clear `storm_queue`
4. `border_flash_state = False`, `storm_warning_flash_state = False`

**Phase 2 kill check** — evaluated every game tick during `storm_phase == 'explosion'`:
- Compute 3×3 blast cells centred on `storm_current_mine` (clipped to grid bounds)
- If `snake.next_head` (Pygame) / `head` (HTML, before `unshift`) / `snake[0]` (Tkinter, Console) in blast cells → `game_over = True`, `end_storm()`

**Bonus food consumption** — bonus foods in `bonus_foods` are checked against the snake head each tick alongside standard food. On hit: `score += 1`, snake grows, `color_index` cycles, remove from `bonus_foods`. Bonus foods drawn using `GREEN` colour only.

**Mine spawning during storm** — `spawn_mine()` / `_try_spawn_mine()` / `trySpawnMine()` continues operating; new mines go into `mines` list only, never into `storm_queue`. Trigger check blocked while `storm_active`.

### 2.5 Rendering Order (all graphical versions)

Per user story Technical Notes:
1. Background
2. Grid
3. **Storm border** (if `storm_active` and `border_flash_state`)
4. **Explosion cells** (if `storm_phase == 'explosion'` — random colour from `EXPLOSION_COLORS` per cell per frame)
5. **Warning mine cell** (if `storm_phase == 'warning'` — flash colour from `EXPLOSION_COLORS`)
6. Remaining mines (standard red/grey flash — `mine_flash_state`)
7. **Bonus foods** (GREEN)
8. Standard food (GREEN)
9. Snake
10. Score/UI
11. Game over overlay

### 2.6 Console Version Specifics

The console version is tick-based (no real-time timers). Timing is approximated:
- Phase 1 (WARNING): 3 game ticks — render the warning mine cell as `CONSOLE_WARNING_CHAR` (`'!'`) in bright yellow ANSI
- Phase 2 (EXPLOSION): 1 game tick — render the 3×3 area as `CONSOLE_EXPLOSION_CHAR` (`'*'`) in bright yellow ANSI
- Border flash: display `CONSOLE_STORM_LABEL` (`'*** DETONATION STORM ***'`) in bright red ANSI at top of grid display
- State variables `storm_phase_ticks_remaining` (int) replaces float elapsed for console

### 2.7 Implementation Sequence

Phases are executed in this order to isolate and validate each platform before proceeding to documentation:

1. **Pygame** (`snake_game.py`) — accumulator-based timing, `next_head` kill check
2. **Tkinter** (`snake_game_tkinter.py`) — `root.after()` scheduling, method-based state in `SnakeGame`
3. **Console** (`snake_game_console.py`) — tick-based, no timers, `encoding='utf-8'`
4. **HTML/JS** (`snake_game.html`) — `setInterval`/`setTimeout`, kill check before `unshift`
5. **Documentation** — all 7 `/docs` files updated
6. **Regression** — syntax validation + manual testing all 4 versions

---

## 3. Files Affected

### Game Files (MODIFY)

| File | Path | Action | Changes |
|------|------|--------|---------|
| Pygame version | `snake_game.py` | MODIFY | Add MDS constants; add `start_storm()`, `end_storm()`, `draw_storm_border()`, `draw_explosion_cells()`, `draw_warning_cell()`, `draw_bonus_foods()` functions; add storm state in `main()`; add restart reset; add border/warning flash accumulators; add phase transition logic in game loop; add Phase 2 kill check; add storm trigger after food-eat/mine-spawn; add bonus food consumption; update rendering pipeline |
| Tkinter version | `snake_game_tkinter.py` | MODIFY | Add MDS constants; add `_start_storm()`, `_end_storm()`, `_toggle_border_flash()`, `_toggle_warning_flash()`, `_advance_storm_phase()` methods to `SnakeGame`; add storm state in `reset_game()`; add `hasattr` guards in `reset_game()` for all new timer IDs; add Phase 2 kill check in `move_snake()`; add storm trigger after spawn call; add bonus food consumption in `move_snake()`; update `draw()` with storm border, explosion cells, warning cell, bonus foods |
| Console version | `snake_game_console.py` | MODIFY | Add MDS constants; add `start_storm()`, `end_storm()` functions; add storm state in `main()`; add tick-countdown variables; add phase transition logic in game loop; add Phase 2 kill check; add storm trigger after spawn call; add bonus food consumption; update `draw_game()` to show storm label, warning char, explosion chars, bonus food |
| HTML/JS version | `snake_game.html` | MODIFY | Add MDS constants; add global storm state variables; add `startStorm()`, `endStorm()`, `advanceStormPhase()` functions; update `init()` to clear all storm timers; update `endGame()` to cancel storm timers; add Phase 2 kill check in `update()` before `snake.unshift(head)`; add storm trigger after mine spawn; add bonus food consumption in `update()`; update `draw()` with storm border, explosion cells, warning cell, bonus foods |

### Feature Folder Files (CREATE)

| File | Path | Action |
|------|------|--------|
| Implementation Plan | `mine-detonation-storm/Plan.md` | CREATE (this file) |
| Build Guide | `mine-detonation-storm/Build.md` | CREATE (P42) |
| Task Checklist | `mine-detonation-storm/ToDo.md` | CREATE (P43) |
| Lessons Learned | `mine-detonation-storm/post-implementation-lessons-learned.md` | CREATE (P44) |

### Documentation Files (MODIFY)

| File | Path | Action | Changes |
|------|------|--------|---------|
| Architecture | `docs/architecture.md` | MODIFY | Add Mine Detonation Storm subsection; update Component Interaction Diagram with storm branches; add new MDS constants |
| Code Patterns | `docs/code.md` | MODIFY | Add Mine Detonation Storm section: new constants, storm state variables, phase transition logic, explosion rendering pattern, bonus food pattern |
| Data Flow | `docs/dataflow.md` | MODIFY | Add storm trigger flow, phase transition flow, explosion kill flow, bonus food spawn/consume flow |
| Decisions | `docs/decisions.md` | MODIFY | Add ADR-MDS-001 through ADR-MDS-005 (storm trigger placement, phase timing mechanism per platform, console tick approximation, explosion kill head-only, bonus food forced placement) |
| Glossary | `docs/glossary.md` | MODIFY | Add: Mine Detonation Storm, Detonation Queue, Phase 1 / Warning Phase, Phase 2 / Explosion Phase, Blast Zone, Bonus Food, Storm Border |
| Risk | `docs/risk.md` | MODIFY | Add RISK-MDS-001 through RISK-MDS-004 (Tkinter timer accumulation on long storm, HTML timer orphan if tab switched, console tick approximation inaccuracy, bonus food list unbounded growth) |
| Structure | `docs/structure.md` | MODIFY | Add `mine-detonation-storm/` folder and its 4 files to the directory tree |

---

## 4. Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| `pygame==2.5.2` | External library | Already exists (`requirements.txt`) | Used in `snake_game.py` — no change |
| `tkinter` | Built-in Python | Already exists | Used in `snake_game_tkinter.py` — no change |
| `random` (stdlib) | Built-in Python | Already exists | Used for `random.shuffle()` on storm queue and `random.choice()` for explosion colours |
| `os`, `time` (stdlib) | Built-in Python | Already exists | Used in console version — no change |
| HTML5 Canvas / Vanilla JS | Browser API | Already exists | Used in `snake_game.html` — no change |
| Flashing Mines feature | Prior feature | Already exists (completed 2026-03-05) | Storm builds on `mines` list, `mine_flash_state`, `mine_flash_accumulator`/timer — must be present |

**No new external dependencies are introduced.**

---

## 5. Assumptions

All assumptions are stated explicitly here. None are hidden.

| # | Assumption | Basis |
|---|------------|-------|
| A-1 | The Flashing Mines feature is fully implemented and passing in all 4 versions before implementation begins. | User story: "Depends On: Flashing Mines feature — must be present and functional in all 4 versions" |
| A-2 | The storm trigger is checked immediately after the mine-spawn step in the food-eat handler (not at any other point in the game loop). | AC-1b: "Evaluated on each food-eat event that causes mine count to reach 10." |
| A-3 | At storm start, all 10 mines currently in `mines` are moved into `storm_queue` and removed from `mines`. Mines spawned after storm start remain in `mines` only and are not added to the queue. | AC-3d and AC-8b |
| A-4 | The bonus food at Phase 2 start is placed unconditionally at the mine's centre cell, even if the snake body occupies that cell. It is NOT validated against `bonus_foods`, `food`, or `mines`. | AC-6f: "placed at centre cell even if occupied by snake body" |
| A-5 | Multiple bonus food items may coexist simultaneously on the grid (one per detonation). The `bonus_foods` list may grow to the total number of detonated mines before any are consumed. | AC-6b |
| A-6 | Bonus food is consumed by the standard food-eat mechanic: head touches position → score+1, grow, colour cycle. The snake eating bonus food triggers a mine spawn (via existing `spawn_mine()` call in the food-eat handler). | AC-6d; food-eat event flow from `docs/architecture.md` Component Interaction Diagram |
| A-7 | Phase 2 kill check uses only the snake head — body segments do NOT trigger game over. | AC-5c |
| A-8 | During Phase 1, normal mine collision rules apply to `storm_current_mine` (since it has been removed from `mines` at Phase 1 start, there is no mine collision by the standard path — this is a no-collision state during warning). The user story states "normal mine collision rules apply (shrink 3, score -3)" for Phase 1, but since the mine is removed from `mines`, no collision will occur. The warning cell is a visual effect only during Phase 1. | AC-3b Phase 1: "Mine removed from active mines list at Phase 1 start. Snake NOT killed — normal mine collision rules apply." The removal from `mines` means the existing mine-collision check will not fire. No special Phase 1 snake-kill logic is needed. |
| A-9 | The storm border is drawn as a single-pixel-wide rect along the inner edge of the 600×600 window (Pygame/Tkinter/HTML). No game entity rendering overlaps the border (the border is 1px, game cells are 20px). | AC-2a, AC-2c |
| A-10 | For the console version, "3 ticks" for Phase 1 and "1 tick" for Phase 2 are reasonable approximations of 3s and 1s at the ~10 FPS console game loop. Exact real-time accuracy is not required for the console version. | AC-10: "Console: tick-based (3 ticks Phase 1, 1 tick Phase 2)" |
| A-11 | Explosion cells in Phase 2 flicker independently — each of the (up to) 9 cells picks a random colour from `EXPLOSION_COLORS` every render frame. For Pygame (60 FPS) this creates rapid flickering. For Tkinter/HTML (~6.67 FPS) it creates slower flickering. This is acceptable per the user story. | AC-4 Phase 2 |
| A-12 | The `storm_phase_timer` (HTML) and `_advance_storm_phase` (Tkinter) approach uses `setTimeout` / `root.after()` for phase transitions (3000ms warning, 1000ms explosion). This is consistent with how Tkinter flash timers and HTML mine flash timers are already implemented. | AC-10; ADR-FM-001 |
| A-13 | For Pygame, phase transitions are managed by accumulators in the main game loop (same pattern as `mine_flash_accumulator`). No `threading` or `pygame.time.set_timer` is introduced. | ADR-FM-001 |
| A-14 | On game restart, ALL storm state must be reset before `mines = []` is set, so no dangling timers reference destroyed state. | AC-9; IMP-FM-D3 pattern |
| A-15 | The storm does not affect or interfere with the existing `mine_flash_accumulator` / `mine_flash_state` logic for non-queued mines. Remaining mines continue to flash red/grey normally during the storm. | AC-3f |
| A-16 | The `py` command (not `python`) is used for all syntax validation on this Windows system. | Feature constraint 6; L3 from flashing-mines lessons |
| A-17 | `snake_game_console.py` must be opened with `encoding='utf-8'` for any AST parse or file read operation. | Feature constraint 8; L2 from flashing-mines lessons |
| A-18 | PowerShell command separator is `;` not `&&`. | Feature constraint 7; L1 from flashing-mines lessons |

---

## 6. Test Strategy

### 6.1 Approach

Manual testing only — no automated tests (per `.cursorrules` Rule 10 and project definition of done). All verification is performed through:
1. Python AST syntax validation (`py -c "import ast; ast.parse(open('FILE', encoding='utf-8').read())"`)
2. Visual launch check (game opens without errors)
3. Manual gameplay testing per version

Test documentation will be recorded in `mine-detonation-storm/Build.md` (step-by-step build instructions and test procedure) and `mine-detonation-storm/post-implementation-lessons-learned.md` (outcomes and deviations).

### 6.2 Syntax Validation (all Python versions)

Run after each Python file modification, before proceeding to the next version:

```powershell
py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
```

### 6.3 Manual Test Procedures Per Version

Each version is tested after implementation. The test procedure covers all acceptance criteria.

#### Pygame (`snake_game.py`)
1. Launch: `py snake_game.py` — verify no errors
2. Play until score reaches ~45+ (10 mines triggered: mine count = 1 + floor(score/5) = 10 at score=45)
3. **AC-1**: Verify storm triggers exactly when 10th mine appears (after food eat at score=45)
4. **AC-2**: Verify red/black flashing border appears around window at 0.2s interval
5. **AC-3**: Verify mines detonate one by one; each mine's cell flashes explosion palette for ~3s before explosion
6. **AC-4**: Verify 3×3 cells flicker with explosion colours during Phase 2
7. **AC-5**: Manoeuvre snake head into an active 3×3 explosion area — verify immediate game over
8. **AC-5**: Manoeuvre snake into Phase 1 warning cell — verify no explosion kill (normal mine rules: mine removed from `mines` so no collision)
9. **AC-6**: Verify GREEN bonus food appears at mine's centre cell at Phase 2 start; eat it — verify score+1 and snake growth
10. **AC-7**: Verify storm ends after all mines detonated (border flash stops)
11. **AC-8**: Eat food during storm — verify new mines spawn normally and do NOT trigger a nested storm
12. **AC-9**: Press SPACE to restart mid-storm — verify all storm state cleared, game resumes cleanly
13. Verify food remains GREEN, snake colour progression unchanged

#### Tkinter (`snake_game_tkinter.py`)
1. Launch: `py snake_game_tkinter.py` — verify no errors
2. Repeat tests 2–13 from Pygame procedure above
3. Verify no timer leaks: restart multiple times — verify no accelerating flash speeds or duplicate timers
4. Verify `hasattr` guards prevent `AttributeError` on first `reset_game()` call

#### Console (`snake_game_console.py`)
1. Launch: `py snake_game_console.py` — verify no errors
2. Play to trigger storm
3. **AC-2f**: Verify `*** DETONATION STORM ***` appears in bright red ANSI at top of display
4. **AC-4 Phase 1**: Verify `!` in bright yellow for warning mine cell for 3 ticks
5. **AC-4 Phase 2**: Verify `*` in bright yellow for explosion cells for 1 tick
6. **AC-5**: Verify game over when snake head in explosion cell during tick
7. **AC-6**: Verify bonus food `●` appears GREEN at mine position
8. **AC-9**: Enter 'r' or restart — verify clean state

#### HTML/JS (`snake_game.html`)
1. Open in browser — verify no console errors
2. Repeat tests 2–13 from Pygame procedure
3. Verify no orphaned `setInterval`/`setTimeout` IDs after restart (check browser console)
4. Verify Phase 2 kill check fires before `snake.unshift(head)` (behavioural: snake dies correctly when entering blast zone)

### 6.4 Regression Tests (all versions after completion)

After all 4 versions and documentation are complete, run a final regression pass:
- Verify existing Flashing Mines behaviour unchanged (mines still flash red/grey, mine hit still shrinks 3, score -3)
- Verify food remains GREEN in all versions
- Verify snake colour progression unchanged in all versions
- Verify all 4 versions launch without errors
- Verify all 7 `/docs` files have been updated

---

## 7. Success Criteria

All criteria must be met before the feature is considered done. Criteria map directly to the Definition of Done and Acceptance Criteria (AC-1 through AC-11).

| SC | Criterion | Maps To |
|----|-----------|---------|
| SC-1 | Storm triggers when `len(mines) >= 10` on a food-eat event, in all 4 versions | AC-1a, AC-1b |
| SC-2 | Storm does not trigger again while `storm_active == True` | AC-1c, AC-1d |
| SC-3 | Flashing red/black border visible during storm in Pygame, Tkinter, HTML at 0.2s interval | AC-2a, AC-2b |
| SC-4 | `*** DETONATION STORM ***` in bright red ANSI visible in console during storm | AC-2f |
| SC-5 | Mines detonate one by one in random (shuffled) order | AC-3a, AC-3d |
| SC-6 | Each mine shows 3-second (3-tick console) warning flash using EXPLOSION_COLORS palette before explosion | AC-3b Phase 1, AC-4 Phase 1 |
| SC-7 | Each mine shows 1-second (1-tick console) 3×3 explosion area with flickering explosion colours | AC-3b Phase 2, AC-4 Phase 2 |
| SC-8 | Only the current warning mine flashes explosion-palette; all other mines flash standard red/grey | AC-3f |
| SC-9 | Snake head entering any Phase 2 3×3 cell causes immediate game over | AC-5a, AC-5d |
| SC-10 | Snake entering Phase 1 warning cell does NOT cause explosion death (mine already removed from `mines`) | AC-5b |
| SC-11 | One GREEN bonus food spawns at mine's centre cell at Phase 2 start for each detonation | AC-6a, AC-6c |
| SC-12 | Bonus food is consumed by standard mechanics (score+1, grow, colour cycle) | AC-6d |
| SC-13 | Bonus food persists after storm ends; consumed normally | AC-6e |
| SC-14 | Storm ends when detonation queue is exhausted; border flash stops | AC-7a, AC-7e |
| SC-15 | Storm ends immediately on Phase 2 snake death | AC-7b |
| SC-16 | Mine spawning continues normally during storm; new mines not added to queue | AC-8a, AC-8b |
| SC-17 | No nested storm triggered during active storm | AC-8c |
| SC-18 | SPACE/restart clears all storm state: `storm_active=False`, queue empty, `storm_phase=None`, `storm_current_mine=None`, all timers cancelled, `bonus_foods=[]` | AC-9 |
| SC-19 | All 4 versions pass Python AST syntax validation or browser console shows no errors | Definition of Done |
| SC-20 | All 4 versions launch without runtime errors | Definition of Done |
| SC-21 | Manual gameplay testing PASSED — confirmed by user | Definition of Done |
| SC-22 | All 7 `/docs` files updated (architecture, code, dataflow, decisions, glossary, risk, structure) | Definition of Done |

---

## 8. Rollback Strategy

### 8.1 Approach

Manual file restore — consistent with the project's established rollback approach (no version control; manual backup).

### 8.2 Pre-Implementation Backup

Before modifying any game file, create timestamped backups of all 4 game files:

```powershell
Copy-Item snake_game.py snake_game.py.bak-mds
Copy-Item snake_game_tkinter.py snake_game_tkinter.py.bak-mds
Copy-Item snake_game_console.py snake_game_console.py.bak-mds
Copy-Item snake_game.html snake_game.html.bak-mds
```

### 8.3 Per-Version Rollback

If any version fails syntax validation or introduces a runtime error that cannot be quickly resolved:
1. Restore from backup: e.g. `Copy-Item snake_game.py.bak-mds snake_game.py`
2. Investigate the failure in isolation before re-attempting
3. Do not proceed to the next version until the current version passes

### 8.4 Full Rollback

If the feature must be fully reverted after partial implementation:
1. Restore all 4 game files from `.bak-mds` backups
2. Restore all 7 `/docs` files from their pre-implementation content (back up docs before modifying)
3. Delete `mine-detonation-storm/Build.md`, `mine-detonation-storm/ToDo.md`, `mine-detonation-storm/post-implementation-lessons-learned.md` (preserve `Plan.md` as record)
4. Verify all 4 versions launch and Flashing Mines feature still operates correctly

### 8.5 Documentation Rollback

Before modifying any doc file, record the current last-modified state. If docs are partially updated and rollback is triggered, restore each doc file from its pre-modification state individually.

---

*Plan.md — Mine Detonation Storm (MDS-001) — Generated 2026-03-06*
