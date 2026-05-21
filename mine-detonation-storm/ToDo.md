# ToDo: Mine Detonation Storm
**Feature ID:** MDS-001  
**Feature Folder:** `mine-detonation-storm/`  
**Build Reference:** `mine-detonation-storm/Build.md`  
**Date:** 2026-03-06

**Legend:** `[ ]` pending · `[x]` complete · `[-]` in progress

---

## Pre-Implementation

- [x] Confirm Flashing Mines is functional — launch all 4 versions and verify mines appear, flash, and damage the snake
  - File: `snake_game.py`, `snake_game_tkinter.py`, `snake_game_console.py`, `snake_game.html`
  - Action: Launch each version, play until score > 5, confirm mines appear and flash
  - Verify: Mines visible and flashing in all 4 versions without errors

- [x] Back up all 4 game files
  - File: project root
  - Action: Run in PowerShell from `snake_game/` folder:
    ```powershell
    Copy-Item snake_game.py snake_game.py.bak-mds
    Copy-Item snake_game_tkinter.py snake_game_tkinter.py.bak-mds
    Copy-Item snake_game_console.py snake_game_console.py.bak-mds
    Copy-Item snake_game.html snake_game.html.bak-mds
    ```
  - Verify: 4 `.bak-mds` files exist in project root

---

## Phase 1 — Pygame (`snake_game.py`)

- [x] **1.1** Add MDS constants to `snake_game.py`
  - File: `snake_game.py`
  - Action: Insert the following block immediately after `MINE_FLASH_INTERVAL = 0.2` (line 26), before `# Snake color palette`:
    ```python
    # Mine Detonation Storm constants
    STORM_TRIGGER_COUNT = 10
    STORM_BORDER_COLOR_A = (255, 0, 0)
    STORM_BORDER_COLOR_B = (0, 0, 0)
    STORM_BORDER_FLASH_INTERVAL = 0.2
    WARNING_DURATION = 3.0
    WARNING_FLASH_INTERVAL = 0.2
    EXPLOSION_DURATION = 1.0
    EXPLOSION_COLORS = [
        (255, 0, 0),
        (255, 136, 0),
        (255, 255, 0),
        (255, 255, 255),
        (255, 68, 0),
    ]
    ```
  - Verify: Constants visible in file; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    ```

- [x] **1.2** Add `draw_storm_border()`, `draw_explosion_cells()`, `draw_warning_cell()`, `draw_bonus_foods()` to `snake_game.py`
  - File: `snake_game.py`
  - Action: Insert all four functions immediately after `draw_mines()` (after line 352), before `if __name__ == '__main__':`:
    ```python
    def draw_storm_border(screen, flash_state):
        color = STORM_BORDER_COLOR_A if flash_state else STORM_BORDER_COLOR_B
        pygame.draw.rect(screen, color, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 2)

    def draw_explosion_cells(screen, mine_pos):
        mx, my = mine_pos
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                cx, cy = mx + dx, my + dy
                if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                    color = random.choice(EXPLOSION_COLORS)
                    pygame.draw.rect(screen, color,
                                     (cx * GRID_SIZE, cy * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_warning_cell(screen, mine_pos, flash_state_index):
        mx, my = mine_pos
        color = EXPLOSION_COLORS[flash_state_index % len(EXPLOSION_COLORS)]
        pygame.draw.rect(screen, color, (mx * GRID_SIZE, my * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_bonus_foods(screen, bonus_foods):
        for bx, by in bonus_foods:
            center = (bx * GRID_SIZE + GRID_SIZE // 2, by * GRID_SIZE + GRID_SIZE // 2)
            pygame.draw.circle(screen, GREEN, center, GRID_SIZE // 2)
    ```
  - Verify: 4 new functions visible in file; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    ```

- [x] **1.3** Initialise storm state variables in `main()` in `snake_game.py`
  - File: `snake_game.py`
  - Action: In `main()`, immediately after `mine_flash_accumulator = 0.0`, insert:
    ```python
    storm_active = False
    storm_queue = []
    storm_phase = None
    storm_current_mine = None
    storm_phase_elapsed = 0.0
    storm_warning_flash_state = False
    storm_warning_flash_acc = 0.0
    storm_warning_flash_index = 0
    border_flash_state = False
    border_flash_acc = 0.0
    bonus_foods = []
    ```
  - Verify: All 11 variables present in `main()`; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    ```

- [x] **1.4** Add storm state reset to SPACE restart block in `snake_game.py`
  - File: `snake_game.py`
  - Action: Inside the `if event.key == pygame.K_SPACE:` restart block, immediately after `mine_flash_accumulator = 0.0`, insert:
    ```python
    storm_active = False
    storm_queue = []
    storm_phase = None
    storm_current_mine = None
    storm_phase_elapsed = 0.0
    storm_warning_flash_state = False
    storm_warning_flash_acc = 0.0
    storm_warning_flash_index = 0
    border_flash_state = False
    border_flash_acc = 0.0
    bonus_foods = []
    ```
  - Verify: Reset block contains all 11 storm variables; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    ```

- [x] **1.5** Replace `if not game_over:` logic block in `snake_game.py` with full storm logic
  - File: `snake_game.py`
  - Action: Replace the entire existing `if not game_over:` block (from `if not game_over:` through `if snake.check_collision(): game_over = True`) with the full replacement block from Build.md Step 1.5. The new block includes: `dt = clock.get_time() / 1000.0`, mine flash accumulator, storm border flash accumulator, storm warning flash accumulator, `storm_phase_elapsed` accumulator, warning→explosion transition, explosion Phase 2 kill check with blast_cells set, explosion→next-mine or end-storm transition, mine collision check, bonus food consumption check, food consumption check with storm trigger, wall/self collision check
  - Verify: Syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    ```

- [x] **1.6** Replace drawing pipeline in `snake_game.py`
  - File: `snake_game.py`
  - Action: Replace the existing drawing block (from `# Drawing` through `game_over_screen(screen, score)`) with the new pipeline from Build.md Step 1.6. New order: `draw_gradient_background`, `draw_grid`, `draw_storm_border` (if active), `draw_explosion_cells` (if Phase 2), `draw_warning_cell` (if Phase 1), `draw_mines`, `draw_bonus_foods`, `draw_food`, `draw_food_particles`, `draw_snake`, `draw_score`, `game_over_screen`
  - Verify: Syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    ```

- [x] **1.7** Final syntax validation and launch check for `snake_game.py`
  - File: `snake_game.py`
  - Action: Run syntax validation then launch:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    py snake_game.py
    ```
  - Verify: No output from syntax check; game window opens without errors; mines visible; snake moves

---

## Phase 2 — Tkinter (`snake_game_tkinter.py`)

- [x] **2.1** Add MDS constants to `snake_game_tkinter.py`
  - File: `snake_game_tkinter.py`
  - Action: Insert the following block immediately after `MINE_FLASH_INTERVAL = 200` (line 15), before `# Snake color palette`:
    ```python
    # Mine Detonation Storm constants
    STORM_TRIGGER_COUNT = 10
    STORM_BORDER_COLOR_A = '#FF0000'
    STORM_BORDER_COLOR_B = '#000000'
    STORM_BORDER_FLASH_INTERVAL = 200
    WARNING_DURATION_MS = 3000
    WARNING_FLASH_INTERVAL = 200
    EXPLOSION_DURATION_MS = 1000
    EXPLOSION_COLORS = [
        '#FF0000',
        '#FF8800',
        '#FFFF00',
        '#FFFFFF',
        '#FF4400',
    ]
    ```
  - Verify: Constants visible in file; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    ```

- [x] **2.2** Add storm state initialisation to `reset_game()` in `snake_game_tkinter.py`
  - File: `snake_game_tkinter.py`
  - Action: In `reset_game()`, immediately after the existing `self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)` line, insert:
    ```python
    self.storm_active = False
    self.storm_queue = []
    self.storm_phase = None
    self.storm_current_mine = None
    self.storm_phase_start_ms = 0
    self.storm_warning_flash_state = False
    self.bonus_foods = []
    if hasattr(self, '_border_flash_after_id'):
        self.root.after_cancel(self._border_flash_after_id)
    self._border_flash_after_id = None
    if hasattr(self, '_warning_flash_after_id'):
        self.root.after_cancel(self._warning_flash_after_id)
    self._warning_flash_after_id = None
    if hasattr(self, '_storm_phase_after_id'):
        self.root.after_cancel(self._storm_phase_after_id)
    self._storm_phase_after_id = None
    self.border_flash_state = False
    ```
  - Verify: Syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    ```

- [x] **2.3** Add `_start_storm()`, `_begin_warning_phase()`, `_begin_explosion_phase()`, `_advance_storm_phase()`, `_end_storm()`, `_toggle_border_flash()`, `_toggle_warning_flash()` methods to `SnakeGame`
  - File: `snake_game_tkinter.py`
  - Action: Insert all 7 methods after `_try_spawn_mine()`, before `def main():`. Use exact code from Build.md Step 2.3
  - Verify: All 7 method names present in file; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    ```

- [x] **2.4** Update food consumption block in `move_snake()` to add storm trigger in `snake_game_tkinter.py`
  - File: `snake_game_tkinter.py`
  - Action: In `move_snake()`, in the `if new_head == self.food:` block, add storm trigger immediately after `self._try_spawn_mine()`:
    ```python
    if not self.storm_active and len(self.mines) >= STORM_TRIGGER_COUNT:
        self._start_storm()
    ```
  - Verify: Syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    ```

- [x] **2.5** Replace mine collision block in `move_snake()` with Phase 2 kill check, bonus food, and mine collision in `snake_game_tkinter.py`
  - File: `snake_game_tkinter.py`
  - Action: Replace the existing mine collision block and `return False` at the end of `move_snake()` with the full block from Build.md Step 2.4 (corrected version): Phase 2 blast_cells kill check → `_end_storm()` + `return True`; bonus food consumption (`self.snake.append(self.snake[-1])`, score+1, colour cycle, `_try_spawn_mine()`); mine collision (shrink 3, score-3, return True if empty); `return False`
  - Verify: Syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    ```

- [x] **2.6** Add storm border, explosion cells, warning cell, and bonus foods to `draw()` in `snake_game_tkinter.py`
  - File: `snake_game_tkinter.py`
  - Action: In `draw()`, insert the storm border, explosion cells, and warning cell blocks immediately **before** the `# Draw mines` block. Insert the bonus foods block immediately **after** the mines block and **before** `# Draw snake`. Use exact code from Build.md Step 2.5
  - Verify: Syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    ```

- [x] **2.7** Final syntax validation and launch check for `snake_game_tkinter.py`
  - File: `snake_game_tkinter.py`
  - Action:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    py snake_game_tkinter.py
    ```
  - Verify: No output from syntax check; game window opens without errors; mines visible; snake moves

---

## Phase 3 — Console (`snake_game_console.py`)

- [x] **3.1** Add MDS constants to `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action: Insert the following block immediately after `MINE_COLOR = '\033[91m'` (line 24), before `# Directions`:
    ```python
    # Mine Detonation Storm constants
    STORM_TRIGGER_COUNT = 10
    CONSOLE_WARNING_CHAR = '!'
    CONSOLE_EXPLOSION_CHAR = '*'
    CONSOLE_STORM_LABEL = '*** DETONATION STORM ***'
    STORM_STORM_COLOR = '\033[91m'
    CONSOLE_WARN_COLOR = '\033[93m'
    WARNING_TICKS = 3
    EXPLOSION_TICKS = 1
    ```
  - Verify: Constants visible in file; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```

- [x] **3.2** Add storm state variables to `main()` in `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action: In `main()`, replace `mines = []` with:
    ```python
    mines = []
    storm_active = False
    storm_queue = []
    storm_phase = None
    storm_current_mine = None
    storm_phase_ticks = 0
    bonus_foods = []
    ```
  - Verify: All 7 variables present in `main()`; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```

- [x] **3.3** Update `draw_game()` signature in `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action: Replace the function signature `def draw_game(snake, food, mines, score):` with:
    ```python
    def draw_game(snake, food, mines, score, storm_active=False, storm_phase=None,
                  storm_current_mine=None, bonus_foods=None):
        if bonus_foods is None:
            bonus_foods = []
    ```
  - Verify: New signature present; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```

- [x] **3.4** Update mine/warning/explosion/bonus cell marking in `draw_game()` in `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action: Replace the `# Mark mine positions` block with the expanded block from Build.md Step 3.3 that includes: mine marking, warning cell marking (`CONSOLE_WARNING_CHAR` if Phase 1), explosion cells marking (`CONSOLE_EXPLOSION_CHAR` for 3×3 if Phase 2, clipped), bonus food marking (`'●'`)
  - Verify: New blocks present; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```

- [x] **3.5** Update cell rendering in `draw_game()` for warning and explosion chars in `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action: In the cell rendering section inside `draw_game()`, add `elif` branches for `CONSOLE_WARNING_CHAR` and `CONSOLE_EXPLOSION_CHAR` as per Build.md Step 3.3 (both render with `CONSOLE_WARN_COLOR`)
  - Verify: Two new `elif` branches present; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```

- [x] **3.6** Add storm label print to `draw_game()` in `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action: Before `print("Use WASD to move, Q to quit")` at the end of `draw_game()`, insert:
    ```python
    if storm_active:
        print(STORM_STORM_COLOR + CONSOLE_STORM_LABEL + RESET_COLOR)
    ```
  - Verify: Storm label block present; syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```

- [x] **3.7** Replace `while not game_over:` game loop body in `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action: Replace the entire `while not game_over:` loop body with the full replacement from Build.md Step 3.4. New loop includes: `draw_game()` call with storm args; food-eat handler with storm trigger and mine spawn; bonus food check with `snake.grow = True`; `snake.move()`; storm tick countdown with phase transitions (warning→explosion at `storm_phase_ticks <= 0`, explosion Phase 2 kill check, explosion→next-mine or end-storm); mine collision check; self-collision check; input handling; `time.sleep(0.1)`
  - Verify: Syntax check passes:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```

- [x] **3.8** Final syntax validation and launch check for `snake_game_console.py`
  - File: `snake_game_console.py`
  - Action:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    py snake_game_console.py
    ```
  - Verify: No output from syntax check; game launches in terminal; grid renders; snake moves with WASD

---

## Phase 4 — HTML/JS (`snake_game.html`)

- [x] **4.1** Add MDS constants to `snake_game.html`
  - File: `snake_game.html`
  - Action: In the `<script>` block, insert the following immediately after the `MINE_FLASH_INTERVAL = 200` line:
    ```javascript
    const STORM_TRIGGER_COUNT = 10;
    const STORM_BORDER_COLOR_A = '#FF0000';
    const STORM_BORDER_COLOR_B = '#000000';
    const STORM_BORDER_FLASH_INTERVAL = 200;
    const WARNING_DURATION_MS = 3000;
    const WARNING_FLASH_INTERVAL = 200;
    const EXPLOSION_DURATION_MS = 1000;
    const EXPLOSION_COLORS = ['#FF0000', '#FF8800', '#FFFF00', '#FFFFFF', '#FF4400'];
    ```
  - Verify: Constants visible in `<script>` block; file opens in browser without JS errors

- [x] **4.2** Add storm state variables to `snake_game.html`
  - File: `snake_game.html`
  - Action: In the `<script>` block, insert the following immediately after `let mineFlashTimer = null;`:
    ```javascript
    let stormActive = false;
    let stormQueue = [];
    let stormPhase = null;
    let stormCurrentMine = null;
    let stormPhaseTimer = null;
    let stormWarningFlashState = false;
    let stormWarningFlashTimer = null;
    let borderFlashState = false;
    let borderFlashTimer = null;
    let bonusFoods = [];
    ```
  - Verify: Variables visible in `<script>` block; file opens in browser without JS errors

- [x] **4.3** Add `startStorm()`, `beginWarningPhase()`, `beginExplosionPhase()`, `endStorm()` functions to `snake_game.html`
  - File: `snake_game.html`
  - Action: Insert all 4 functions immediately before the `init()` function using exact code from Build.md Step 4.3
  - Verify: All 4 function names present in `<script>` block; file opens in browser without JS errors

- [x] **4.4** Update `init()` in `snake_game.html` to reset storm state
  - File: `snake_game.html`
  - Action: In `init()`, immediately after the `mineFlashTimer = setInterval(...)` line, insert the storm state reset block from Build.md Step 4.4 (resets `stormActive`, `stormQueue`, `stormPhase`, `stormCurrentMine`, `bonusFoods`, `borderFlashState`, cancels all 3 storm timer IDs)
  - Verify: Storm reset block present in `init()`; file opens in browser without JS errors

- [x] **4.5** Update `endGame()` in `snake_game.html` to cancel storm timers
  - File: `snake_game.html`
  - Action: In `endGame()`, immediately after `if (mineFlashTimer) clearInterval(mineFlashTimer);`, insert:
    ```javascript
    if (borderFlashTimer) clearInterval(borderFlashTimer);
    borderFlashTimer = null;
    if (stormWarningFlashTimer) clearInterval(stormWarningFlashTimer);
    stormWarningFlashTimer = null;
    if (stormPhaseTimer) clearTimeout(stormPhaseTimer);
    stormPhaseTimer = null;
    ```
  - Verify: Storm timer cancellation present in `endGame()`; file opens in browser without JS errors

- [x] **4.6** Replace mine collision / food consumption block in `update()` in `snake_game.html`
  - File: `snake_game.html`
  - Action: Replace the existing block from `// Mine collision check` through the closing `}` of `snake.pop()` (the entire mine collision + `snake.unshift(head)` + food consumption section) with the full replacement from Build.md Step 4.6. New block includes: Phase 2 explosion kill check (before `unshift`), mine collision check (before `unshift`), `snake.unshift(head)`, bonus food check (grow: no pop), food check with storm trigger, else `snake.pop()`
  - Verify: `startStorm()` call present in `update()`; file opens in browser without JS errors

- [x] **4.7** Add storm border, explosion cells, warning cell, bonus foods to `draw()` in `snake_game.html`
  - File: `snake_game.html`
  - Action: In `draw()`, insert storm border, explosion cells, and warning cell blocks immediately **before** the `// Draw mines` comment. Insert bonus foods drawing **after** the mines `forEach` block and **before** `// Draw snake`. Use exact code from Build.md Step 4.7
  - Verify: All storm drawing blocks present in `draw()`; file opens in browser without JS errors

- [x] **4.8** Final launch and JS console check for `snake_game.html`
  - File: `snake_game.html`
  - Action: Open `snake_game.html` in a browser. Open developer console (F12). Play the game briefly
  - Verify: No JavaScript errors in console; game renders correctly; mines visible and flashing

---

## Phase 5 — Documentation

- [x] **5.1** Update `docs/architecture.md` — add Mine Detonation Storm subsection, component interaction diagram entries, and constants
  - File: `docs/architecture.md`
  - Action: Append the Mine Detonation Storm Component subsection (state variables, trigger, phases, kill condition), update the Component Interaction Diagram with storm phase tick and Phase 2 kill branches, add new MDS constants. Use exact content from Build.md Step 5.1
  - Verify: "Mine Detonation Storm Component" heading present in file; `STORM_TRIGGER_COUNT` present in constants section

- [x] **5.2** Update `docs/code.md` — append Mine Detonation Storm code patterns section
  - File: `docs/code.md`
  - Action: Append the full "Mine Detonation Storm — Code Patterns" section from Build.md Step 5.2, including: Storm Constants code block, Storm Trigger Pattern, Storm State Variables table, Phase Transition Logic code block, Explosion Blast Cells Pattern, Explosion Rendering Pattern, Timing Mechanisms table, Bonus Food Pattern
  - Verify: "Mine Detonation Storm — Code Patterns" heading present at end of file

- [x] **5.3** Update `docs/dataflow.md` — append Mine Detonation Storm data flows section
  - File: `docs/dataflow.md`
  - Action: Append the full "Mine Detonation Storm — Data Flows" section from Build.md Step 5.3, including: Storm Trigger Flow, Phase Transition Flow, Phase 2 Kill Flow, Bonus Food Spawn/Consume Flow, Storm End Flow
  - Verify: "Mine Detonation Storm — Data Flows" heading present at end of file

- [x] **5.4** Update `docs/decisions.md` — append ADR-MDS-001 through ADR-MDS-005
  - File: `docs/decisions.md`
  - Action: Append the full "Mine Detonation Storm Feature — Architectural Decisions" section from Build.md Step 5.4 with all 5 ADRs
  - Verify: "ADR-MDS-001" through "ADR-MDS-005" all present in file

- [x] **5.5** Update `docs/glossary.md` — append Mine Detonation Storm glossary entries
  - File: `docs/glossary.md`
  - Action: Append the full "Mine Detonation Storm — Glossary" section from Build.md Step 5.5 with all 8 terms: Mine Detonation Storm, Detonation Queue, Phase 1/Warning Phase, Phase 2/Explosion Phase, Blast Zone, Bonus Food, Storm Border, EXPLOSION_COLORS
  - Verify: "Mine Detonation Storm" and "Blast Zone" terms present in file

- [x] **5.6** Update `docs/risk.md` — append RISK-MDS-001 through RISK-MDS-004
  - File: `docs/risk.md`
  - Action: Append the full "Mine Detonation Storm — Risks" section from Build.md Step 5.6 with all 4 risk entries
  - Verify: "RISK-MDS-001" through "RISK-MDS-004" all present in file

- [x] **5.7** Update `docs/structure.md` — add `mine-detonation-storm/` folder to directory tree
  - File: `docs/structure.md`
  - Action: In the Complete Directory Tree section, immediately after the `flashing-mines/` block, insert the `mine-detonation-storm/` block from Build.md Step 5.7 listing all 4 feature folder files
  - Verify: `mine-detonation-storm/` entry with 4 sub-files present in directory tree

---

## Phase 6 — Verification

- [x] **6.1** Run final syntax validation on all 3 Python files
  - File: `snake_game.py`, `snake_game_tkinter.py`, `snake_game_console.py`
  - Action:
    ```powershell
    py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
    py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
    py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
    ```
  - Verify: All 3 commands produce no output

- [x] **6.2** Launch all 4 versions and confirm no startup errors
  - File: `snake_game.py`, `snake_game_tkinter.py`, `snake_game_console.py`, `snake_game.html`
  - Action: Launch each version:
    ```powershell
    py snake_game.py
    py snake_game_tkinter.py
    py snake_game_console.py
    ```
    Open `snake_game.html` in browser (F12 open)
  - Verify: All 4 launch without errors; browser console shows no JS errors

- [x] **6.3a** Manual test — SC-1 through SC-8 (storm trigger, border, sequence, visuals)
  - File: all 4 versions
  - Action: In each version, play to score 45+ (10 mines active). Test:
    - SC-1: Storm triggers when 10th mine appears after food eat
    - SC-2: No nested storm while one is active
    - SC-3: Red/black border flashes at 0.2s in Pygame/Tkinter/HTML
    - SC-4: `*** DETONATION STORM ***` in bright red shown in console
    - SC-5: Mines detonate in shuffled (random) order
    - SC-6: 3-second warning flash using explosion-palette colours before each explosion
    - SC-7: 1-second 3×3 flickering explosion area
    - SC-8: Only current warning mine uses explosion-palette; all others flash standard red/grey
  - Verify: All 8 behaviours confirmed in all 4 versions (or applicable platform variants)

- [x] **6.3b** Manual test — SC-9 through SC-13 (kill, bonus food)
  - File: all 4 versions
  - Action: In each version:
    - SC-9: Move head into active Phase 2 blast zone → confirm immediate game over
    - SC-10: Move head into Phase 1 warning cell → confirm no explosion kill
    - SC-11: Confirm one GREEN bonus food appears at mine centre at Phase 2 start
    - SC-12: Eat bonus food → confirm score+1 and snake growth
    - SC-13: Let storm end, confirm bonus foods remain on grid; eat them normally
  - Verify: All 5 behaviours confirmed in all applicable versions

- [x] **6.3c** Manual test — SC-14 through SC-18 (storm end, spawning during storm, restart)
  - File: all 4 versions
  - Action: In each version:
    - SC-14: Let all mines detonate → confirm storm ends, border flash stops
    - SC-15: Die in Phase 2 blast → confirm storm ends immediately
    - SC-16: Eat food during storm → confirm new mine spawns into `mines` only, not `storm_queue`
    - SC-17: Confirm no nested storm triggers during active storm
    - SC-18: Press SPACE mid-storm → confirm clean restart: no border flash, no timers firing, no bonus foods
  - Verify: All 5 behaviours confirmed in all applicable versions

- [x] **6.3d** Manual test — SC-19 through SC-22 (regression)
  - File: all 4 versions
  - Action:
    - SC-19–20: All 4 versions pass syntax check and launch
    - SC-21: Food is always GREEN; snake colour progression unchanged throughout storm
    - SC-22: Confirm all 7 `/docs` files updated (open each and verify new section present)
  - Verify: All regression criteria confirmed; no regressions to existing Flashing Mines feature

---

*ToDo.md — Mine Detonation Storm (MDS-001) — Generated 2026-03-06*
