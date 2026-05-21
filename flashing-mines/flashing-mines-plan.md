# Flashing Mines — Implementation Plan

**Feature Folder:** `snake_game/flashing-mines/`
**Implementation Plan File:** `snake_game/flashing-mines/flashing-mines-plan.md`

---

## SETUP

**Change Overview:** Add flashing mine obstacles to all four Snake Game versions that scale in number with the player's score and damage the snake on collision.

**Repository to be touched:** `snake_game/` (root — all four game files)

**User Story:** `snake_game/User_Story_flashing-mines.txt`

**Support Documentation:** None provided by user.

---

## PRE-ANALYSIS CHECKLIST

- [x] Workspace scanned for relevant code patterns
- [x] Dependencies and tech stack identified
- [x] User story parsed for deliverables
- [x] Existing test patterns identified
- [x] Configuration files analysed (.cursorrules, rules.mdc, docs/)
- [x] Any ambiguities or gaps documented

**Gaps / Ambiguities identified:**

| # | Gap | Source | Resolution |
|---|-----|--------|------------|
| G-1 | Console version uses blocking `input()` — 0.2s flash toggle cannot run on a separate timer | docs/architecture.md, snake_game_console.py:123 | User story AC-6 states: "if the console version cannot flash, render mines as a static 'M' character." Accepted — static 'M' for console. |
| G-2 | Pygame uses interpolated animation frames; collision is checked against `snake.next_head`, not `snake.body[0]` | snake_game.py:77 | Mine collision must be checked against `next_head` in the Pygame version, consistent with existing food and wall collision patterns. |
| G-3 | Console version wraps at edges (no wall collision, modulo movement) | snake_game_console.py:38 | The "collision course" path projection must account for wrapping — cells ahead are calculated with modulo. |
| G-4 | No automated tests exist in the project | docs/risk.md (DEBT-002), docs/decisions.md | Testing is manual only, consistent with rules.mdc Rule 10. |

---

## IMPLEMENTATION REQUIREMENTS

### Technical Requirements

| # | Requirement | Source |
|---|-------------|--------|
| TR-1 | All four versions must be modified independently — no shared modules | docs/decisions.md ADR-007, rules.mdc Rule 3 |
| TR-2 | Mine state stored as `list` of `(x, y)` tuples (Python) / array of `{x, y}` objects (JS) | User_Story AC-Technical Notes |
| TR-3 | Flash state is a single shared boolean — all mines flash in sync | User_Story AC-Technical Notes |
| TR-4 | Mine count formula: `number_of_mines = 1 + floor(score / 5)` | User_Story AC-2 |
| TR-5 | New mine spawned only on food-eat event; existing mines remain | User_Story AC-2 |
| TR-6 | Spawn validation: not on snake body, not within 10 Manhattan-distance of any body segment, not on collision-course path, not on food, not on existing mine; max 1000 attempts then skip | User_Story AC-3 |
| TR-7 | Mine collision: remove mine, shrink snake by 3 from tail, reduce score by 3 (min 0), game over if length ≤ 0 | User_Story AC-5 |
| TR-8 | Flash cycle: 0.2 s interval, toggling between MINE_COLOR_A (255,0,0) and MINE_COLOR_B (200,200,200) | User_Story AC-1 |
| TR-9 | Mines drawn after grid/background and before the snake in every render pass | User_Story AC-Technical Notes |
| TR-10 | Color constants MINE_COLOR_A, MINE_COLOR_B, MINE_FLASH_INTERVAL added at module level | User_Story AC-Technical Notes |
| TR-11 | No new external dependencies introduced | docs/structure.md, requirements.txt |

### Error Handling

| # | Scenario | Handling |
|---|----------|---------|
| EH-1 | No valid mine spawn position found within 1000 attempts | Skip mine spawn silently — do not crash (User_Story AC-3 last bullet) |
| EH-2 | Snake length drops to 0 or below after mine collision shrink | Trigger game-over immediately (User_Story AC-5d) |
| EH-3 | Score would go negative after mine penalty | Clamp to 0 — `score = max(0, score - 3)` (User_Story AC-5c) |

### Testing

Manual testing only (consistent with rules.mdc Rule 10 — no automated tests exist).

### Test Requirements

| # | Test | Versions |
|---|------|---------|
| T-1 | Mine appears on grid after eating first food | All 4 |
| T-2 | Mine count scales: score 0→4 = 1 mine, 5→9 = 2 mines | All 4 |
| T-3 | Mine flashes between red and grey at ≈0.2 s | Pygame, Tkinter, HTML |
| T-4 | Console mine renders as 'M' (static) | Console |
| T-5 | Mine does not spawn on snake body | All 4 |
| T-6 | Mine does not spawn within 10 Manhattan-distance of snake | All 4 |
| T-7 | Mine does not spawn on food cell | All 4 |
| T-8 | Mine does not spawn on existing mine cell | All 4 |
| T-9 | Snake hitting mine: mine removed, snake shrinks by 3, score -3 (min 0) | All 4 |
| T-10 | Snake hitting mine when length ≤ 3: game over | All 4 |
| T-11 | Mines cleared and reset on game restart | All 4 |
| T-12 | Mines do not interact with food (food spawning unaffected) | All 4 |

### Build Verification

| # | Step | Command |
|---|------|---------|
| BV-1 | Pygame version runs without error | `python snake_game.py` |
| BV-2 | Tkinter version runs without error | `python snake_game_tkinter.py` |
| BV-3 | Console version runs without error | `python snake_game_console.py` |
| BV-4 | HTML version loads in browser without console errors | Open `snake_game.html` in browser, check DevTools Console |

---

## CONSTRAINTS

- All findings based on facts from workspace analysis only — no invented code.
- Each game file is standalone; no imports between versions (docs/decisions.md ADR-007).
- Food MUST remain `(0, 255, 0)` / `#00FF00` / `'green'` — rules.mdc Rule 2.
- Snake color progression system must not be affected — rules.mdc Rule 2.
- New constants must follow existing UPPERCASE module-level convention — rules.mdc Rule 5.
- Documentation in `/docs` must be updated as part of completion (rules.mdc Rule 9).
- No automated tests — manual testing only (rules.mdc Rule 10, docs/decisions.md DEBT-002).

---

## DELIVERABLES

Sourced exclusively from `User_Story_flashing-mines.txt`.

| # | Deliverable | Traced to AC |
|---|-------------|-------------|
| D-1 | Mine entity — each mine occupies 1 grid cell; displayed as flashing red/grey square (or static 'M' in console) | AC-1 |
| D-2 | Mine count scaling — `number_of_mines = 1 + floor(score / 5)`; one new mine added per food-eat | AC-2 |
| D-3 | Mine spawn validation — respects 6 spawn rules; fails gracefully after 1000 attempts | AC-3 |
| D-4 | Mine persistence — mines remain stationary until snake hits them or game ends | AC-4 |
| D-5 | Mine collision — mine removed + snake shrinks 3 + score -3 (min 0) + game-over if length ≤ 0 | AC-5 |
| D-6 | Flash timing — platform-appropriate timer per version (accumulator/Pygame, .after()/Tkinter, setInterval()/HTML, static/console) | AC-6 |
| D-7 | Documentation updates — `/docs` files updated per rules.mdc Rule 9 and user story doc requirements | User_Story "Documentation Updates Required" |

---

## IMPLEMENTATION SOLUTION DESIGN

---

### 1. Architecture Decision

**Pattern/Approach:** Extend the existing immediate-mode game loop in each version by adding a `mines` state variable, a `mine_flash_state` boolean, and a flash timer. On each food-eat event, attempt to spawn a new mine using the validated placement logic. On each frame, check mine collision against the snake head. In the render pass, draw mines after the background/grid and before the snake.

**Reference Implementation:**
- Mine state modelled on `food.position` pattern — `(x, y)` tuple storage (docs/dataflow.md Food Entity Data Model)
- Flash timer modelled on Pygame's existing `pygame.time.get_ticks()` usage for food pulse (snake_game.py:158)
- Collision check modelled on existing food collision pattern (snake_game.py:89–93, snake_game_tkinter.py:97, snake_game_console.py:54–58, snake_game.html:205–209)
- Spawn validation loop modelled on `Food.generate_position()` while-loop with occupancy check (snake_game.py:111–115)

**Rationale:** Maintains consistency with existing patterns; no new architectural layers needed; isolated to each standalone file per ADR-007.

**Alternative Considered:** A separate `Mine` class — not chosen because the existing food entity uses no class in Tkinter/HTML/Console versions and adding a class for mines only in some versions would be inconsistent. A `list` of tuples/objects is sufficient and consistent with the food pattern.

---

### 2. File Structure Design

#### File 1 — `snake_game.py`

**File Path:** `snake_game/snake_game.py`
**Status:** MODIFY EXISTING
**Purpose:** Add mine state, flash timer, spawn logic, collision, and rendering to the Pygame version.
**Reference Pattern:** Existing Food class (lines 107–115), draw_food (lines 143–159), main game loop (lines 190–251), food_particles global (line 254).
**Dependencies:** No new imports; uses existing `pygame`, `random`, `math`.

**Sections to add/modify:**

| Location | Change |
|----------|--------|
| After existing color constants (line ~22) | Add `MINE_COLOR_A = (255, 0, 0)`, `MINE_COLOR_B = (200, 200, 200)`, `MINE_FLASH_INTERVAL = 0.2` |
| `main()` — after `score = 0` init | Add `mines = []`, `mine_flash_state = False`, `mine_flash_accumulator = 0.0` |
| `main()` — game loop, after `snake.eat_food()` block | Call `spawn_mine(mines, snake.body, food.position, score)` |
| `main()` — game loop, update section | Add mine collision check; if `snake.next_head in mines`: remove mine, shrink snake, adjust score, check game-over |
| `main()` — game loop, update section | Update `mine_flash_accumulator` using `clock.get_time() / 1000.0`; toggle `mine_flash_state` when accumulator ≥ 0.2 |
| `main()` — render section, after `draw_grid`, before `draw_snake` | Call `draw_mines(screen, mines, mine_flash_state)` |
| `main()` — restart block (space pressed) | Reset `mines = []`, `mine_flash_state = False`, `mine_flash_accumulator = 0.0` |
| New function `spawn_mine(mines, snake_body, food_pos, score)` | Returns nothing; appends valid mine position to `mines` list or skips after 1000 attempts |
| New function `draw_mines(screen, mines, flash_state)` | Draws each mine as a filled `GRID_SIZE × GRID_SIZE` rect using `MINE_COLOR_A` or `MINE_COLOR_B` based on `flash_state` |

**Snake shrink logic (mine collision in Pygame):**
- `snake.body` shrink: remove last 3 elements with `del snake.body[-3:]` (or fewer if not enough segments — check length first)
- Because Pygame uses `next_head`-based collision, this is caught at the same point as wall/self collision
- Score: `score = max(0, score - 3)`
- Game-over if `len(snake.body) <= 0` after shrink

---

#### File 2 — `snake_game_tkinter.py`

**File Path:** `snake_game/snake_game_tkinter.py`
**Status:** MODIFY EXISTING
**Purpose:** Add mine state, `.after()` flash timer, spawn logic, collision, and canvas rendering to the Tkinter version.
**Reference Pattern:** `SnakeGame` class (lines 30–160); `reset_game()` (lines 58–66); `move_snake()` (lines 79–105); `draw()` (lines 107–141); `game_loop()` (lines 142–149); `root.after(GAME_SPEED, self.game_loop)` (line 149).
**Dependencies:** No new imports.

**Sections to add/modify:**

| Location | Change |
|----------|--------|
| After existing color constants (line ~22) | Add `MINE_COLOR_A = '#FF0000'`, `MINE_COLOR_B = '#C8C8C8'`, `MINE_FLASH_INTERVAL = 200` (ms) |
| `reset_game()` | Add `self.mines = []`, `self.mine_flash_state = False` |
| `reset_game()` | Cancel any pending flash timer: `if hasattr(self, '_flash_after_id'): self.root.after_cancel(self._flash_after_id)` |
| `reset_game()` | Start flash timer: `self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)` |
| New method `_toggle_mine_flash(self)` | Toggle `self.mine_flash_state`; reschedule: `self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)` |
| `move_snake()` — after food consumption block | Call `self._try_spawn_mine()` |
| `move_snake()` — collision section (after food check, before `return False`) | Check if `new_head in self.mines`; if so: remove mine, shrink snake, adjust score, update label, check game-over |
| `draw()` — after grid, before snake | Draw each mine as `canvas.create_rectangle` using current flash colour |
| New method `_try_spawn_mine(self)` | Spawn validation; appends to `self.mines` or skips |
| `generate_food()` | No change needed — mine-exclusion handled in `_try_spawn_mine` |

**Snake shrink (Tkinter):**
- `self.snake` is a plain list; remove last 3: `del self.snake[-3:]`
- Score: `self.score = max(0, self.score - 3)` + update label
- Game-over if `len(self.snake) == 0`

---

#### File 3 — `snake_game_console.py`

**File Path:** `snake_game/snake_game_console.py`
**Status:** MODIFY EXISTING
**Purpose:** Add static mine rendering (character 'M'), spawn logic, and collision to the console version. No flashing (AC-6 fallback).
**Reference Pattern:** `Snake` class (lines 28–58); `Food` class (lines 61–68); `draw_game()` (lines 71–101); `main()` (lines 104–139).
**Dependencies:** No new imports.

**Sections to add/modify:**

| Location | Change |
|----------|--------|
| After existing color constants (line ~20) | Add `MINE_CHAR = 'M'`, `MINE_COLOR = '\033[91m'` (bright red ANSI) |
| `main()` — after `score = 0` | Add `mines = []` |
| `main()` — game loop, after food-eat block | Call `spawn_mine(mines, snake.body, food.position, score)` |
| `main()` — game loop, after `snake.move()` | Check if `snake.body[0] in mines`; if so: remove mine, shrink, adjust score, check game-over |
| `draw_game()` — grid construction | Mark mine cells: `grid[mine[1]][mine[0]] = MINE_CHAR` |
| `draw_game()` — rendering loop | Render 'M' cells with `MINE_COLOR` ANSI code + `RESET_COLOR` |
| `main()` — restart (after game over, if the user re-runs) | `mines = []` on restart (game re-initialises from top of loop on re-run, so this is covered by the existing `main()` scope) |
| New function `spawn_mine(mines, snake_body, food_pos, score)` | Same validation logic as other versions |

**Snake shrink (Console):**
- `snake.body` is a list; `del snake.body[-3:]`
- Score: `score = max(0, score - 3)`
- Game-over if `len(snake.body) == 0`

**Note on collision-course check (console):** The console version uses wrapping movement `(head_x + dir_x) % GRID_WIDTH`. The forbidden-path cells must be computed using modulo wrapping to be consistent with how the snake actually moves.

---

#### File 4 — `snake_game.html`

**File Path:** `snake_game/snake_game.html`
**Status:** MODIFY EXISTING
**Purpose:** Add mine state, `setInterval()` flash timer, spawn logic, collision, and canvas rendering to the HTML/JS version.
**Reference Pattern:** Global state vars (lines 144–151); `init()` (lines 154–167); `generateFood()` (lines 170–178); `update()` (lines 182–214); `draw()` (lines 217–306); `endGame()` (lines 309–313).
**Dependencies:** No new dependencies.

**Sections to add/modify:**

| Location | Change |
|----------|--------|
| After existing color constants (line ~123) | Add `const MINE_COLOR_A = '#FF0000'`, `const MINE_COLOR_B = '#C8C8C8'`, `const MINE_FLASH_INTERVAL = 200` |
| Global state section (after `colorIndex`) | Add `let mines = []`, `let mineFlashState = false`, `let mineFlashTimer = null` |
| `init()` | Reset `mines = []`, `mineFlashState = false`; clear old timer `if (mineFlashTimer) clearInterval(mineFlashTimer)`; start new `mineFlashTimer = setInterval(() => { mineFlashState = !mineFlashState; }, MINE_FLASH_INTERVAL)` |
| `endGame()` | Clear flash timer: `if (mineFlashTimer) clearInterval(mineFlashTimer)` |
| `update()` — after food consumption block | Call `trySpawnMine()` |
| `update()` — collision checks section (after self-collision check) | Check `mines.some(m => m.x === head.x && m.y === head.y)`; if so: remove mine, shrink snake, adjust score, update DOM, check game-over |
| `draw()` — after grid, before snake | Iterate `mines` array, draw each as `ctx.fillRect` using current flash colour |
| New function `trySpawnMine()` | Spawn validation; pushes valid `{x, y}` to `mines` or skips |
| `generateFood()` | No change needed — mine exclusion handled in `trySpawnMine` |

**Snake shrink (JavaScript):**
- `snake.splice(snake.length - 3, 3)` (remove last 3 elements)
- Score: `score = Math.max(0, score - 3)` + update DOM
- Game-over if `snake.length === 0`

---

### 3. Technical Specifications

#### Data Structures

**Python versions — mine state:**
```python
mines: list[tuple[int, int]] = []          # e.g. [(5, 10), (12, 3)]
mine_flash_state: bool = False             # True = MINE_COLOR_A (red), False = MINE_COLOR_B (grey)
mine_flash_accumulator: float = 0.0       # Pygame only — seconds accumulated since last toggle
```

**JavaScript — mine state:**
```javascript
mines: Array<{x: number, y: number}>      // e.g. [{x:5, y:10}, {x:12, y:3}]
mineFlashState: boolean                    // true = MINE_COLOR_A, false = MINE_COLOR_B
mineFlashTimer: number | null              // setInterval ID
```

**New constants (all versions):**

| Constant | Python | JavaScript |
|----------|--------|-----------|
| `MINE_COLOR_A` | `(255, 0, 0)` | `'#FF0000'` |
| `MINE_COLOR_B` | `(200, 200, 200)` | `'#C8C8C8'` |
| `MINE_FLASH_INTERVAL` | `0.2` (s, Pygame) / `200` (ms, Tkinter) | `200` (ms) |

---

#### Mine Spawn Validation Algorithm (all versions)

```
Input: mines, snake_body, food_pos, score

expected_count = 1 + floor(score / 5)
mines_to_add = expected_count - len(mines)
if mines_to_add <= 0: return

for each mine to add:
    attempts = 0
    while attempts < 1000:
        candidate = random grid cell
        
        # Rule 1: not on any snake body segment
        if candidate in snake_body: retry
        
        # Rule 2: Manhattan distance > 10 from every body segment
        for segment in snake_body:
            if |candidate.x - segment.x| + |candidate.y - segment.y| <= 10: retry
        
        # Rule 3: not on collision-course path
        # Starting from snake head, step in current direction until wall (or wrap for console)
        path_cell = snake_head
        while path_cell in grid:
            if candidate == path_cell: retry
            path_cell = next cell in direction
        
        # Rule 4: not on food cell
        if candidate == food_pos: retry
        
        # Rule 5: not on existing mine
        if candidate in mines: retry
        
        # Valid
        mines.append(candidate)
        break
        
        attempts += 1
    
    # if attempts == 1000: skip silently (AC-3)
```

---

#### Mine Collision Algorithm (all versions)

```
# Triggered when snake head moves onto a mine cell

mine_hit = cell that matches snake head position

1. Remove mine_hit from mines list
2. Shrink snake: remove last min(3, len(snake)-1) tail segments
   → If len(snake) - 3 <= 0: game_over = True; return
   → Else: del snake[-3:]
3. score = max(0, score - 3)
4. Update score display
```

---

#### Flash Timing per Version

| Version | Mechanism | Source |
|---------|-----------|--------|
| Pygame | `mine_flash_accumulator += clock.get_time() / 1000.0`; toggle when `>= 0.2`, reset to `0.0` | User_Story AC-6, docs/architecture.md Pygame frame rate |
| Tkinter | `root.after(200, _toggle_mine_flash)` recursive scheduling | User_Story AC-6, snake_game_tkinter.py:149 pattern |
| HTML | `setInterval(() => { mineFlashState = !mineFlashState }, 200)` | User_Story AC-6, snake_game.html:166 pattern |
| Console | Static 'M' — no flash | User_Story AC-6 fallback, docs/architecture.md console limitations |

---

#### Error Handling

| Scenario | Handling | Reference |
|----------|----------|---------|
| No valid mine spawn in 1000 attempts | `break` out of loop silently — no crash | User_Story AC-3 |
| Score - 3 < 0 | `score = max(0, score - 3)` | User_Story AC-5c |
| Snake length ≤ 0 after shrink | `game_over = True` immediately | User_Story AC-5d |
| Mines list empty when checking collision | No-op — `if snake_head in mines` is False | Python `in` / JS `.some()` handle empty collections |

---

#### Dependencies

**Existing dependencies used:**

| Version | Dependency | Confirmed in |
|---------|-----------|-------------|
| Pygame | `pygame` 2.5.2, `random`, `math` | requirements.txt, snake_game.py:1–4 |
| Tkinter | `tkinter`, `random` | snake_game_tkinter.py:1–2 |
| Console | `random`, `os`, `time` | snake_game_console.py:1–3 |
| HTML | Vanilla JS, Canvas 2D API | snake_game.html |

**New dependencies:** None.

---

#### Integration Points

**Integration 1 — snake_game.py**
- File: `snake_game/snake_game.py`
- Change: Add 3 constants after line 22 (existing color block); add `mines`, `mine_flash_state`, `mine_flash_accumulator` to `main()` state; add `spawn_mine()` call in food-eat block (line ~232); add mine collision check in update section; add flash accumulator update using `clock.get_time()`; add `draw_mines()` call in render section (after `draw_grid`, before `draw_snake`, line ~240); reset mines on restart (line ~210).
- Reason: Pygame version is standalone; all changes localised to this file.

**Integration 2 — snake_game_tkinter.py**
- File: `snake_game/snake_game_tkinter.py`
- Change: Add 3 constants after line 22; add `self.mines`, `self.mine_flash_state` to `reset_game()`; add `_toggle_mine_flash()` method; add `_try_spawn_mine()` method; add mine collision in `move_snake()`; add mine drawing in `draw()`; cancel/restart flash timer in `reset_game()`.
- Reason: Tkinter version is standalone; all changes localised to this file.

**Integration 3 — snake_game_console.py**
- File: `snake_game/snake_game_console.py`
- Change: Add `MINE_CHAR`, `MINE_COLOR` after line 20; add `mines = []` to `main()`; add `spawn_mine()` call after food-eat; add mine collision check after `snake.move()`; add mine rendering in `draw_game()`.
- Reason: Console version is standalone; all changes localised to this file.

**Integration 4 — snake_game.html**
- File: `snake_game/snake_game.html`
- Change: Add 3 constants in JS constants block; add `mines`, `mineFlashState`, `mineFlashTimer` globals; update `init()` to reset mines and manage flash timer; update `endGame()` to clear flash timer; add `trySpawnMine()` call in `update()`; add mine collision check in `update()`; add mine drawing in `draw()`.
- Reason: HTML version is standalone; all changes localised to this file.

**Integration 5 — Documentation**
- Files: `snake_game/docs/architecture.md`, `docs/structure.md`, `docs/code.md`, `docs/dataflow.md`, `docs/decisions.md`, `docs/glossary.md`, `docs/risk.md`
- Change: Update per user story "Documentation Updates Required" section and rules.mdc Rule 9.
- Reason: Features are only "done" if both code and docs are updated (rules.mdc).

---

### 4. Implementation Flow

#### Normal Gameplay Flow (with mines)

```
1. Game initialises → mines = [], flash timer starts
2. Player eats food
3. score += 1
4. expected_mines = 1 + floor(score / 5)
5. If len(mines) < expected_mines → run spawn_mine()
   a. Generate random candidate cell
   b. Validate against 5 rules (body, Manhattan-10, path, food, existing mines)
   c. If valid: append to mines; else retry up to 1000 times then skip
6. New food generated (existing logic — unaffected by mines)
7. Flash timer fires every 0.2s → mine_flash_state toggles (all mines in sync)
8. Render frame:
   a. Background / gradient
   b. Grid
   c. Mines (red or grey based on mine_flash_state)  ← NEW
   d. Snake
   e. Food
   f. Score
9. Snake moves to new head position
10. Mine collision check:
    a. If new head == any mine position:
       - Remove that mine from list
       - Shrink snake by 3 tail segments
       - score = max(0, score - 3)
       - Update score display
       - If len(snake) <= 0: game_over = True
11. Existing wall / self-collision check continues as before
12. Loop repeats
```

#### Mine Collision Flow (shrink + game-over branch)

```
Snake head → mine cell
    │
    ├─→ Remove mine from mines list
    │
    ├─→ shrink_amount = min(3, len(snake) - 1)
    │      (preserve at least head — game-over handled separately)
    │
    ├─→ del snake[-shrink_amount:]  (or splice in JS)
    │
    ├─→ score = max(0, score - 3)
    │
    └─→ len(snake) == 0 ?
          Yes → game_over = True
          No  → continue game
```

#### Game Restart Flow

```
Player presses SPACE (game over state)
    │
    ├─→ mines = []           (clear all mines)
    ├─→ mine_flash_state = False
    ├─→ Reset flash timer    (cancel + restart)
    └─→ Existing snake/food/score reset continues
```

---

### 5. Testing Strategy

#### Unit Testing Approach

No automated tests exist in the project (docs/decisions.md DEBT-002, rules.mdc Rule 10). Manual testing per the test requirements table above.

**Test Reference Pattern:** None — no existing test files found in workspace.

#### Manual Testing Procedure

**For each of the 4 versions:**

1. Launch the game.
2. Eat 1 food → confirm exactly 1 mine appears.
3. Eat 4 more (total 5) → confirm exactly 2 mines appear.
4. Verify mines are not on the snake body or food cell.
5. In Pygame/Tkinter/HTML: confirm mines visually flash red ↔ grey approximately every 0.2s.
6. In Console: confirm mines render as 'M'.
7. Navigate snake head into a mine:
   - Confirm mine disappears.
   - Confirm snake is 3 segments shorter.
   - Confirm score decreased by 3 (or clamped at 0).
8. Engineer a scenario where snake is ≤ 3 segments and hits a mine → confirm game-over.
9. After game-over, press SPACE → confirm mines are cleared.
10. Play until a restart to confirm mine count resets.

#### Verification Commands

**Build Verification:**
```
python snake_game.py
python snake_game_tkinter.py
python snake_game_console.py
```
Open `snake_game.html` in browser — check DevTools → Console for errors.

**Manual Visual Verification:**
- Pygame: Run → eat food → observe mine flashes at ~5 per second.
- Tkinter: Run → same check.
- HTML: Run in browser → DevTools → Console — no JS errors.
- Console: Run → eat food → 'M' character appears in grid.

---

## IMPLEMENTATION SUCCESS CRITERIA

| # | Criterion | Traced to |
|---|-----------|---------|
| SC-1 | Mine appears on grid after first food eaten in all 4 versions | D-1, D-2 |
| SC-2 | Mine count equals `1 + floor(score / 5)` at all score values tested | D-2 |
| SC-3 | Mine never spawns on snake body, within 10 Manhattan distance, on collision-course path, on food, or on existing mine | D-3 |
| SC-4 | Mine spawn gracefully skips after 1000 failed attempts (no crash) | D-3 |
| SC-5 | Pygame, Tkinter, HTML mines visually flash at ≈0.2s interval between red and grey | D-6 |
| SC-6 | Console mines render as static 'M' character | D-6 |
| SC-7 | All mines flash in synchronisation (same phase) | D-6 |
| SC-8 | Snake hitting a mine: mine removed, snake 3 shorter, score -3 (min 0) | D-5 |
| SC-9 | Snake hitting mine when length ≤ 3 triggers game-over | D-5 |
| SC-10 | Mines persist across multiple food-eat events (not reset each time) | D-4 |
| SC-11 | All mines cleared on game restart | D-4 |
| SC-12 | Food remains green; snake color progression unaffected | Constraint |
| SC-13 | All 4 game versions launch without errors after implementation | BV-1–4 |
| SC-14 | `/docs` files updated per rules.mdc Rule 9 | D-7 |

---

## ROLLBACK STRATEGY

**Risk Level:** Low

**Rationale:** Changes are additive (new state variables, new functions, new render calls) and isolated to 4 standalone files. No database, no external services, no shared modules. Failure modes are visual/gameplay only and do not corrupt persistent state (none exists).

**Rollback Approach:** Code Revert (manual `git revert` or restore files from backup).

**Rollback Triggers:**
- Any game version fails to launch after implementation.
- Mine collision causes unexpected crash or freeze.
- Flash timer causes UI thread issues in Tkinter.
- Score or snake body corruption detected.

**Rollback Steps:**
1. Restore original `snake_game.py`, `snake_game_tkinter.py`, `snake_game_console.py`, `snake_game.html` from version control or backup.
2. Verify each version launches correctly (`python snake_game.py`, etc.).
3. Confirm food/snake/score behaviour is unchanged.
4. Revert any updated `/docs` files if code was reverted.

**Rollback Verification:** Each of the 4 game files launches and basic gameplay (move, eat food, game over, restart) functions correctly with no mine-related code present.

**Rollback Testing:** No — risk is low and rollback is a straightforward file restore.

---

## TRACEABILITY

| User Story AC | Deliverable | Implementation Section |
|---------------|------------|----------------------|
| AC-1 (Appearance) | D-1 | File Structure Design — draw_mines / canvas mine drawing |
| AC-2 (Mine Count) | D-2 | spawn_mine algorithm — `expected_count = 1 + floor(score/5)` |
| AC-3 (Spawn Rules) | D-3 | Mine Spawn Validation Algorithm |
| AC-4 (Mine Behaviour) | D-4 | Game state — mines persist in list until hit or game over |
| AC-5 (Collision) | D-5 | Mine Collision Algorithm |
| AC-6 (Flash Timing) | D-6 | Flash Timing per Version table |
| Doc Requirements | D-7 | Integration Point 5 — Documentation |

---

## IMPORTANT REMINDERS

- Do not execute this plan — it is for review only.
- All findings are based on facts from workspace analysis. No hidden functionality assumed.
- No automated tests exist; manual testing only.
- `/docs` updates are mandatory on implementation (rules.mdc Rule 9).
- All 4 game files are standalone — no code sharing between them (ADR-007).
- Food color `(0,255,0)` / `#00FF00` must not change (rules.mdc Rule 2).
- Snake color progression must not be affected (rules.mdc Rule 2).

---

## VALIDATION CHECKLIST

- [x] All deliverables are traceable to user story acceptance criteria
- [x] All solution components reference existing workspace patterns (food pattern, collision pattern, game loop pattern)
- [x] All file paths follow workspace conventions (root-level game files, docs/ for documentation)
- [x] All dependencies are verified — no new packages required; all existing (requirements.txt, stdlib)
- [x] All integration points are specific (file, location, change)
- [x] No existing test files found — manual testing documented; gap flagged (G-4)
- [x] Four gaps documented and resolved (G-1 through G-4)
- [x] Solution design is complete enough for P42 (Build.md extraction)

---

**Implementation Plan:** `snake_game/flashing-mines/flashing-mines-plan.md`
**Feature Folder:** `snake_game/flashing-mines/`
