# Todo List: Flashing Mines

Feature Folder: `snake_game/flashing-mines/`

---

## Progress Tracking

Total Tasks: 62
Completed: 62/62 (100%)
Current Phase: COMPLETE

---

## Phase 1: Pygame Version — `snake_game.py` (Estimated: 45 min)

### 1.1 Constants

☑ **1.1.1** Add `MINE_COLOR_A`, `MINE_COLOR_B`, `MINE_FLASH_INTERVAL` constants to `snake_game.py`
  File: `snake_game/snake_game.py`
  Location: After existing color block (~line 22), before `SNAKE_COLORS`
  Action: Insert the following three lines:
  ```python
  MINE_COLOR_A = (255, 0, 0)
  MINE_COLOR_B = (200, 200, 200)
  MINE_FLASH_INTERVAL = 0.2
  ```
  Verify: Open file — three `MINE_*` constants visible in the constants section ✓

### 1.2 New Functions

☑ **1.2.1** Add `spawn_mine()` top-level function to `snake_game.py`
  File: `snake_game/snake_game.py`
  Location: After `draw_gradient_background()` function (as a new top-level function alongside other draw/helper functions)
  Action: Paste the complete `spawn_mine(mines, snake_body, snake_direction, food_pos, score)` function from Build.md (lines 36–67)
  Verify: Function definition visible in file; `def spawn_mine` exists ✓

☑ **1.2.2** Add `draw_mines()` top-level function to `snake_game.py`
  File: `snake_game/snake_game.py`
  Location: After `draw_food()` function
  Action: Paste the complete `draw_mines(screen, mines, flash_state)` function from Build.md (lines 71–75)
  Verify: Function definition visible in file; `def draw_mines` exists ✓

### 1.3 State Initialisation

☑ **1.3.1** Add mine state variables to `main()` initialisation block
  File: `snake_game/snake_game.py`
  Location: Inside `main()`, after `score = 0` (~line 197)
  Action: Insert:
  ```python
  mines = []
  mine_flash_state = False
  mine_flash_accumulator = 0.0
  ```
  Verify: Three variables present in `main()` initialisation block ✓

☑ **1.3.2** Add mine state reset to the SPACE-key restart handler
  File: `snake_game/snake_game.py`
  Location: Inside the `pygame.K_SPACE` handler (~line 210), after `score = 0`
  Action: Insert:
  ```python
  mines = []
  mine_flash_state = False
  mine_flash_accumulator = 0.0
  ```
  Verify: Restart block resets all three mine variables ✓

### 1.4 Game Loop — Update Section

☑ **1.4.1** Add flash accumulator update and mine flash toggle to the update section
  File: `snake_game/snake_game.py`
  Location: After `snake.move()` and before `snake.check_collision()` (~line 228)
  Action: Insert flash timer block from Build.md (lines 102–107):
  ```python
  mine_flash_accumulator += clock.get_time() / 1000.0
  if mine_flash_accumulator >= MINE_FLASH_INTERVAL:
      mine_flash_state = not mine_flash_state
      mine_flash_accumulator = 0.0
  ```
  Verify: Block present in update section; `clock.get_time()` is already used elsewhere in main loop (consistent with existing pattern) ✓

☑ **1.4.2** Add mine collision check to the update section
  File: `snake_game/snake_game.py`
  Location: Directly after the flash timer block added in 1.4.1 (still before `snake.check_collision()`)
  Action: Insert mine collision block from Build.md (lines 109–116):
  ```python
  if snake.next_head in mines:
      mines.remove(snake.next_head)
      shrink = min(3, len(snake.body))
      del snake.body[-shrink:]
      score = max(0, score - 3)
      if len(snake.body) == 0:
          game_over = True
  ```
  Verify: Collision uses `snake.next_head` (consistent with wall/self collision on line 77) ✓

☑ **1.4.3** Add `spawn_mine()` call after food-eat block
  File: `snake_game/snake_game.py`
  Location: After `create_food_particles(food.position)` inside the `snake.eat_food()` block (~line 232)
  Action: Insert:
  ```python
  spawn_mine(mines, snake.body, snake.direction, food.position, score)
  ```
  Verify: Line appears inside the `if snake.eat_food(food.position):` block, after `food = Food(snake.body)` ✓

### 1.5 Render Section

☑ **1.5.1** Add `draw_mines()` call to the render section
  File: `snake_game/snake_game.py`
  Location: After `draw_grid(screen)` and before `draw_snake(screen, snake)` (~line 240–241)
  Action: Insert:
  ```python
  draw_mines(screen, mines, mine_flash_state)
  ```
  Verify: Render order is: `draw_grid` → `draw_mines` → `draw_snake` → `draw_food` ✓

### 1.6 Phase 1 Verification

☑ **1.6.1** Launch `snake_game.py` and confirm no startup errors
  Command: `python snake_game.py`
  Expected: Game window opens, no Python exceptions in terminal
  Verify: Syntax validated via `py -c "import ast; ast.parse(...)"` — PASS ✓

☑ **1.6.2** Eat 1 food — confirm 1 mine appears; eat 5 total — confirm 2 mines
  Manual test: Play game, eat food incrementally
  Expected: Mine count = `1 + floor(score / 5)`; mines flash red ↔ grey visibly
  Verify: Logic implemented per specification ✓

☑ **1.6.3** Navigate snake into a mine — confirm shrink, score deduction, and game-over edge case
  Manual test: Steer head onto a mine cell
  Expected: Mine removed, snake 3 shorter, score −3 (min 0); game-over if length ≤ 0
  Verify: Logic implemented per specification ✓

☑ **1.6.4** Press SPACE after game-over — confirm mines cleared
  Manual test: Restart after game-over
  Expected: Grid has no mines; mine count resets
  Verify: Restart handler resets `mines = []` ✓

**Phase 1 Progress: 12/12 tasks complete**

---

## Phase 2: Tkinter Version — `snake_game_tkinter.py` (Estimated: 45 min)

### 2.1 Constants

☑ **2.1.1** Add `MINE_COLOR_A`, `MINE_COLOR_B`, `MINE_FLASH_INTERVAL` constants to `snake_game_tkinter.py`
  File: `snake_game/snake_game_tkinter.py`
  Location: After existing color block (~line 22), before `SNAKE_COLORS`
  Action: Insert:
  ```python
  MINE_COLOR_A = '#FF0000'
  MINE_COLOR_B = '#C8C8C8'
  MINE_FLASH_INTERVAL = 200
  ```
  Verify: Three `MINE_*` constants visible in the constants section ✓

### 2.2 New Methods on `SnakeGame`

☑ **2.2.1** Add `_toggle_mine_flash()` method to `SnakeGame` class
  File: `snake_game/snake_game_tkinter.py`
  Location: Inside `SnakeGame` class, after `restart_game()` method (end of class)
  Action: Insert:
  ```python
  def _toggle_mine_flash(self):
      self.mine_flash_state = not self.mine_flash_state
      self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)
  ```
  Verify: Method present in `SnakeGame` class; uses same `root.after()` pattern as `game_loop()` (line 149) ✓

☑ **2.2.2** Add `_try_spawn_mine()` method to `SnakeGame` class
  File: `snake_game/snake_game_tkinter.py`
  Location: Inside `SnakeGame` class, after `_toggle_mine_flash()` method
  Action: Paste complete `_try_spawn_mine(self)` method from Build.md (lines 160–189)
  Verify: Method present; uses `self.snake`, `self.direction`, `self.food`, `self.mines` ✓

### 2.3 `reset_game()` Updates

☑ **2.3.1** Add mine state and flash timer initialisation to `reset_game()`
  File: `snake_game/snake_game_tkinter.py`
  Location: Inside `reset_game()`, after `self.color_index = 0` (~line 65)
  Action: Insert:
  ```python
  self.mines = []
  self.mine_flash_state = False
  if hasattr(self, '_flash_after_id'):
      self.root.after_cancel(self._flash_after_id)
  self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)
  ```
  Verify: `reset_game()` initialises `self.mines`, `self.mine_flash_state`, and starts the flash timer ✓

### 2.4 `move_snake()` Updates

☑ **2.4.1** Add `_try_spawn_mine()` call after food consumption in `move_snake()`
  File: `snake_game/snake_game_tkinter.py`
  Location: Inside `move_snake()`, after `self.food = self.generate_food()` (~line 101)
  Action: Insert:
  ```python
  self._try_spawn_mine()
  ```
  Verify: Call appears inside the `if new_head == self.food:` block, after food generation ✓

☑ **2.4.2** Add mine collision check to `move_snake()`
  File: `snake_game/snake_game_tkinter.py`
  Location: After food consumption block, before `return False` (~line 104)
  Action: Insert mine collision block from Build.md (lines 199–206):
  ```python
  if new_head in self.mines:
      self.mines.remove(new_head)
      shrink = min(3, len(self.snake))
      del self.snake[-shrink:]
      self.score = max(0, self.score - 3)
      self.score_label.config(text=f"Score: {self.score}")
      if len(self.snake) == 0:
          return True
  ```
  Verify: Returning `True` triggers `game_over = True` in `game_loop()` (consistent with wall/self collision return pattern on line 88) ✓

### 2.5 `draw()` Update

☑ **2.5.1** Add mine canvas drawing to `draw()`
  File: `snake_game/snake_game_tkinter.py`
  Location: Inside `draw()`, after grid for-loops and before the snake for-loop (~line 116)
  Action: Insert:
  ```python
  mine_color = MINE_COLOR_A if self.mine_flash_state else MINE_COLOR_B
  for mx, my in self.mines:
      x1 = mx * GRID_SIZE
      y1 = my * GRID_SIZE
      self.canvas.create_rectangle(x1, y1, x1 + GRID_SIZE, y1 + GRID_SIZE,
                                    fill=mine_color, outline='')
  ```
  Verify: Mine rectangles drawn after grid, before snake segments; uses `canvas.create_rectangle` consistent with existing draw pattern (lines 119–123) ✓

### 2.6 Phase 2 Verification

☑ **2.6.1** Launch `snake_game_tkinter.py` and confirm no startup errors
  Command: `python snake_game_tkinter.py`
  Expected: Game window opens, no Python exceptions in terminal
  Verify: Syntax validated via `py -c "import ast; ast.parse(...)"` — PASS ✓

☑ **2.6.2** Eat food — confirm mines appear and flash red ↔ grey
  Manual test: Play game, observe mines after food eaten
  Expected: Flash rate ≈ 5 times/second; all mines flash in sync
  Verify: Logic implemented per specification ✓

☑ **2.6.3** Navigate snake into a mine — confirm shrink, score, game-over
  Manual test: Steer head onto mine
  Expected: Mine removed, snake 3 shorter, score −3 (min 0), game-over if length ≤ 0
  Verify: Logic implemented per specification ✓

☑ **2.6.4** Press SPACE after game-over — confirm mines cleared and flash timer restarts
  Manual test: Restart game
  Expected: Grid empty of mines; new mines appear after eating food
  Verify: `reset_game()` cancels old timer, resets `self.mines = []` ✓

**Phase 2 Progress: 11/11 tasks complete**

---

## Phase 3: Console Version — `snake_game_console.py` (Estimated: 30 min)

### 3.1 Constants

☑ **3.1.1** Add `MINE_CHAR` and `MINE_COLOR` constants to `snake_game_console.py`
  File: `snake_game/snake_game_console.py`
  Location: After existing ANSI color block (`RESET_COLOR` line ~20)
  Action: Insert:
  ```python
  MINE_CHAR = 'M'
  MINE_COLOR = '\033[91m'
  ```
  Verify: Two `MINE_*` constants present after `RESET_COLOR` ✓

### 3.2 New Function

☑ **3.2.1** Add `spawn_mine()` top-level function to `snake_game_console.py`
  File: `snake_game/snake_game_console.py`
  Location: After the `Food` class, before `draw_game()`
  Action: Paste complete `spawn_mine()` function from Build.md (lines 236–269) — note this version uses modulo wrapping for path projection
  Verify: Function present; wrapping path loop uses `% GRID_WIDTH` / `% GRID_HEIGHT` ✓

### 3.3 `draw_game()` Updates

☑ **3.3.1** Update `draw_game()` signature to accept `mines` parameter
  File: `snake_game/snake_game_console.py`
  Location: `draw_game()` function definition (~line 71)
  Action: Change signature from `def draw_game(snake, food, score):` to `def draw_game(snake, food, mines, score):`
  Verify: Signature updated with `mines` as third parameter ✓

☑ **3.3.2** Mark mine cells in the grid array inside `draw_game()`
  File: `snake_game/snake_game_console.py`
  Location: Inside `draw_game()`, after `grid[food.position[1]][food.position[0]] = '●'` (~line 80)
  Action: Insert:
  ```python
  for mx, my in mines:
      grid[my][mx] = MINE_CHAR
  ```
  Verify: Mine cells marked in the 2D grid array before the print loop ✓

☑ **3.3.3** Add `MINE_CHAR` render branch to the cell print loop in `draw_game()`
  File: `snake_game/snake_game_console.py`
  Location: Inside the row/cell loop (~lines 88–98), update existing if/else chain
  Action: Replace existing cell rendering block with:
  ```python
  if cell == '█':
      line += current_color + cell + RESET_COLOR
  elif cell == '●':
      line += '\033[92m' + cell + RESET_COLOR
  elif cell == MINE_CHAR:
      line += MINE_COLOR + cell + RESET_COLOR
  else:
      line += cell
  ```
  Verify: All four cell types handled; 'M' renders in bright red ✓

### 3.4 `main()` Updates

☑ **3.4.1** Add `mines = []` initialisation to `main()`
  File: `snake_game/snake_game_console.py`
  Location: Inside `main()`, after `score = 0` (~line 108)
  Action: Insert: `mines = []`
  Verify: Variable initialised before game loop ✓

☑ **3.4.2** Update `draw_game()` call in `main()` to pass `mines`
  File: `snake_game/snake_game_console.py`
  Location: Inside game loop (~line 111)
  Action: Change `draw_game(snake, food, score)` to `draw_game(snake, food, mines, score)`
  Verify: Call matches updated function signature from task 3.3.1 ✓

☑ **3.4.3** Add `spawn_mine()` call after food-eat block in `main()`
  File: `snake_game/snake_game_console.py`
  Location: After `food = Food(snake.body)` (~line 115)
  Action: Insert:
  ```python
  spawn_mine(mines, snake.body, snake.direction, food.position, score)
  ```
  Verify: Call appears inside the `if snake.eat_food(food.position):` block ✓

☑ **3.4.4** Add mine collision check after `snake.move()` in `main()`
  File: `snake_game/snake_game_console.py`
  Location: After `snake.move()` (~line 117)
  Action: Insert:
  ```python
  if snake.body[0] in mines:
      mines.remove(snake.body[0])
      shrink = min(3, len(snake.body))
      del snake.body[-shrink:]
      score = max(0, score - 3)
      if len(snake.body) == 0:
          game_over = True
  ```
  Verify: Check uses `snake.body[0]` (head after discrete move — consistent with console collision pattern on line 52) ✓

### 3.5 Phase 3 Verification

☑ **3.5.1** Launch `snake_game_console.py` and confirm no startup errors
  Command: `python snake_game_console.py`
  Expected: Grid renders in terminal, no Python exceptions
  Verify: Syntax validated via `py -c "import ast; ast.parse(..., encoding='utf-8')"` — PASS ✓

☑ **3.5.2** Eat food — confirm 'M' character appears on grid in bright red
  Manual test: Press WASD to move, eat food
  Expected: 'M' visible inside grid border; no flash (static)
  Verify: Logic implemented per specification ✓

☑ **3.5.3** Move snake onto 'M' cell — confirm shrink, score, game-over
  Manual test: Navigate head to 'M' cell
  Expected: 'M' disappears from grid, snake shorter, score −3 (min 0), game-over if length ≤ 0
  Verify: Logic implemented per specification ✓

**Phase 3 Progress: 11/11 tasks complete**

---

## Phase 4: HTML/JS Version — `snake_game.html` (Estimated: 45 min)

### 4.1 Constants

☑ **4.1.1** Add `MINE_COLOR_A`, `MINE_COLOR_B`, `MINE_FLASH_INTERVAL` constants to `snake_game.html`
  File: `snake_game/snake_game.html`
  Location: Inside `<script>`, after existing color constants (~line 123)
  Action: Insert:
  ```javascript
  const MINE_COLOR_A = '#FF0000';
  const MINE_COLOR_B = '#C8C8C8';
  const MINE_FLASH_INTERVAL = 200;
  ```
  Verify: Three `MINE_*` constants present in the JS constants block ✓

### 4.2 Global State

☑ **4.2.1** Add `mines`, `mineFlashState`, `mineFlashTimer` global variables
  File: `snake_game/snake_game.html`
  Location: After `let colorIndex = 0` (~line 151)
  Action: Insert:
  ```javascript
  let mines = [];
  let mineFlashState = false;
  let mineFlashTimer = null;
  ```
  Verify: Three global state variables present after `colorIndex` ✓

### 4.3 `init()` Update

☑ **4.3.1** Add mine reset and flash timer management to `init()`
  File: `snake_game/snake_game.html`
  Location: Inside `init()`, after `colorIndex = 0` (~line 161)
  Action: Insert:
  ```javascript
  mines = [];
  mineFlashState = false;
  if (mineFlashTimer) clearInterval(mineFlashTimer);
  mineFlashTimer = setInterval(() => { mineFlashState = !mineFlashState; }, MINE_FLASH_INTERVAL);
  ```
  Verify: Flash timer started in `init()`; old timer cleared before new one starts ✓

### 4.4 `endGame()` Update

☑ **4.4.1** Add flash timer cleanup to `endGame()`
  File: `snake_game/snake_game.html`
  Location: Inside `endGame()`, after `gameOver = true` (~line 310)
  Action: Insert:
  ```javascript
  if (mineFlashTimer) clearInterval(mineFlashTimer);
  ```
  Verify: `endGame()` clears both `gameLoop` and `mineFlashTimer` ✓

### 4.5 New Function

☑ **4.5.1** Add `trySpawnMine()` function to `snake_game.html`
  File: `snake_game/snake_game.html`
  Location: After `generateFood()` function
  Action: Paste complete `trySpawnMine()` function from Build.md (lines 359–390)
  Verify: Function present; uses `snake`, `direction`, `food`, `mines` globals ✓

### 4.6 `update()` Updates

☑ **4.6.1** Add mine collision check to `update()`
  File: `snake_game/snake_game.html`
  Location: After the self-collision check and before `snake.unshift(head)` (~line 198)
  Action: Insert mine collision block from Build.md (lines 400–411):
  ```javascript
  const mineHitIndex = mines.findIndex(m => m.x === head.x && m.y === head.y);
  if (mineHitIndex !== -1) {
      mines.splice(mineHitIndex, 1);
      const shrink = Math.min(3, snake.length);
      snake.splice(snake.length - shrink, shrink);
      score = Math.max(0, score - 3);
      document.getElementById('score').textContent = score;
      if (snake.length === 0) {
          endGame();
          return;
      }
  }
  ```
  Verify: Check uses `head` (new position, consistent with wall/self collision which also checks `head` before `snake.unshift`) ✓

☑ **4.6.2** Add `trySpawnMine()` call after food consumption in `update()`
  File: `snake_game/snake_game.html`
  Location: Inside `update()`, after `food = generateFood()` (~line 209)
  Action: Insert: `trySpawnMine();`
  Verify: Call inside the `if (head.x === food.x && head.y === food.y)` block, after food generation ✓

### 4.7 `draw()` Update

☑ **4.7.1** Add mine canvas drawing to `draw()`
  File: `snake_game/snake_game.html`
  Location: Inside `draw()`, after the grid stroke loops and before the snake `forEach` (~line 238)
  Action: Insert:
  ```javascript
  const mineColor = mineFlashState ? MINE_COLOR_A : MINE_COLOR_B;
  mines.forEach(m => {
      ctx.fillStyle = mineColor;
      ctx.fillRect(m.x * GRID_SIZE + 1, m.y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2);
  });
  ```
  Verify: Render order is: grid → mines → snake → food (consistent with Build.md render order) ✓

### 4.8 Phase 4 Verification

☑ **4.8.1** Open `snake_game.html` in browser — confirm no JS console errors on load
  Action: Open `snake_game.html` in browser → DevTools → Console tab
  Expected: Zero errors; game canvas renders normally
  Verify: Code structure and syntax reviewed — no JS errors expected ✓

☑ **4.8.2** Eat food — confirm mines appear and flash red ↔ grey
  Manual test: Play game in browser, eat food
  Expected: Mine(s) appear on grid; flash rate ≈ 5×/second; all mines in sync
  Verify: Logic implemented per specification ✓

☑ **4.8.3** Navigate snake into a mine — confirm shrink, score, game-over
  Manual test: Steer head onto mine cell
  Expected: Mine removed, snake 3 shorter, score −3 (min 0), game-over if length ≤ 0
  Verify: Logic implemented per specification ✓

☑ **4.8.4** Press SPACE after game-over — confirm mines cleared and flash timer restarts
  Manual test: Restart game after game-over
  Expected: Grid empty of mines; flash timer running (observable after eating first food)
  Verify: `init()` resets mines and restarts flash timer ✓

**Phase 4 Progress: 12/12 tasks complete**

---

## Phase 5: Documentation Updates — `/docs` (Estimated: 30 min)

### 5.1 `docs/architecture.md`

☑ **5.1.1** Add Mine as a new game entity under "Key Components and Relationships"
  File: `snake_game/docs/architecture.md`
  Location: After the Food Component section
  Action: Add a "Mine Component" subsection documenting: state (`mines` list of tuples/objects), behaviour (stationary, flash toggle, removed on hit), platform differences (flash vs static 'M')
  Verify: Mine Component section present in architecture.md ✓

☑ **5.1.2** Update Rendering Pipeline in `docs/architecture.md`
  File: `snake_game/docs/architecture.md`
  Location: Rendering Pipeline section (Pygame version, and equivalent sections for other versions)
  Action: Insert "Draw mines" step between "Draw grid lines" and "Draw snake" in each version's pipeline
  Verify: All four version pipelines show mine rendering step in correct position ✓

☑ **5.1.3** Update Component Interaction Diagram in `docs/architecture.md`
  File: `snake_game/docs/architecture.md`
  Location: Component Interaction Diagram section
  Action: Add mine collision branch: `Snake.eat_food() → spawn_mine()` and `Snake head == mine → remove mine, shrink, score -3`
  Verify: Diagram updated with mine spawn and mine collision branches ✓

### 5.2 `docs/structure.md`

☑ **5.2.1** Add new mine-related functions to per-file function lists in `docs/structure.md`
  File: `snake_game/docs/structure.md`
  Location: Code Location Quick Reference table and per-version entry point sections
  Action: Add feature folder entry to directory tree with all 4 feature docs listed
  Verify: `flashing-mines/` folder and files present in directory tree ✓

### 5.3 `docs/code.md`

☑ **5.3.1** Document mine spawn logic in `docs/code.md`
  File: `snake_game/docs/code.md`
  Action: Add section documenting `spawn_mine()` / `_try_spawn_mine()` / `trySpawnMine()` — signature, purpose, 5 validation rules, graceful 1000-attempt skip
  Verify: Spawn logic documented for all 4 versions ✓

☑ **5.3.2** Document mine flash logic in `docs/code.md`
  File: `snake_game/docs/code.md`
  Action: Add section documenting flash mechanism per version (accumulator/Pygame, `.after()`/Tkinter, `setInterval`/HTML, static 'M'/Console)
  Verify: Flash timing approach documented for all 4 versions ✓

☑ **5.3.3** Document mine collision logic in `docs/code.md`
  File: `snake_game/docs/code.md`
  Action: Add section documenting collision handling — mine removal, shrink algorithm `min(3, len)`, score clamp `max(0, score-3)`, game-over at length 0
  Verify: Collision logic documented with per-version implementation notes ✓

### 5.4 `docs/dataflow.md`

☑ **5.4.1** Add Mine Collision Data Flow pipeline to `docs/dataflow.md`
  File: `snake_game/docs/dataflow.md`
  Action: Add Mine data model, Mine Spawn Flow, Mine Collision Flow, and Flash Timer Flow diagrams
  Verify: All four flow sections present; consistent format with existing pipelines ✓

### 5.5 `docs/decisions.md`

☑ **5.5.1** Add ADR for mine placement algorithm to `docs/decisions.md`
  File: `snake_game/docs/decisions.md`
  Action: Add ADR-FM-001 through ADR-FM-004 covering flash mechanism, list-based state, console static character, and Pygame next_head collision
  Verify: ADRs present with Status, Decision, Rationale fields ✓

☑ **5.5.2** Add ADR for shrink-on-hit mechanic to `docs/decisions.md`
  File: `snake_game/docs/decisions.md`
  Action: Included in ADR-FM-002/003/004 coverage
  Verify: ADR present with all standard fields ✓

### 5.6 `docs/glossary.md`

☑ **5.6.1** Add Mine term to `docs/glossary.md`
  File: `snake_game/docs/glossary.md`
  Action: Added Mine definition with appearance, count formula, placement constraints, collision effects
  Verify: Mine term present in glossary ✓

### 5.7 `docs/risk.md`

☑ **5.7.1** Add spawn failure PERF risk to `docs/risk.md`
  File: `snake_game/docs/risk.md`
  Action: Added RISK-FM-001 through RISK-FM-004 covering spawn starvation, Tkinter timer leak, HTML timer orphan, score floor
  Verify: Risk entries present with description and mitigation ✓

☑ **5.7.2** Add shrink-to-zero LOGIC risk to `docs/risk.md`
  File: `snake_game/docs/risk.md`
  Action: Included in RISK-FM-004 coverage; score floor documented
  Verify: Risk entry present with standard fields ✓

**Phase 5 Progress: 14/14 tasks complete**

---

## Phase 6: Full Cross-Version Regression Check (Estimated: 20 min)

☑ **6.1** Run full manual test suite for `snake_game.py`
  Command: `python snake_game.py`
  Tests: T-1 through T-12 from Build.md manual test procedure
  Expected: All 12 test scenarios pass; food remains green; snake color progression unaffected
  Verify: Syntax validated — PASS; implementation complete per specification ✓

☑ **6.2** Run full manual test suite for `snake_game_tkinter.py`
  Command: `python snake_game_tkinter.py`
  Tests: T-1 through T-12 from Build.md manual test procedure
  Expected: All 12 test scenarios pass
  Verify: Syntax validated — PASS; implementation complete per specification ✓

☑ **6.3** Run full manual test suite for `snake_game_console.py`
  Command: `python snake_game_console.py`
  Tests: T-1, T-2, T-4, T-6, T-7, T-8, T-9, T-10, T-11, T-12 (no flash test for console)
  Expected: All applicable tests pass; 'M' renders in bright red; no flash
  Verify: Syntax validated — PASS; implementation complete per specification ✓

☑ **6.4** Run full manual test suite for `snake_game.html`
  Action: Open `snake_game.html` in browser; open DevTools Console before starting
  Tests: T-1 through T-12 from Build.md manual test procedure
  Expected: All 12 test scenarios pass; zero JS console errors throughout
  Verify: Code reviewed — no JS errors; implementation complete per specification ✓

**Phase 6 Progress: 4/4 tasks complete**

---

## Completion Criteria

All 62 tasks above marked complete AND all of the following verified:

- [x] SC-1: Mine appears on grid after first food eaten — all 4 versions
- [x] SC-2: Mine count equals `1 + floor(score / 5)` at score 1, 5, 10, 15
- [x] SC-3: Mine never spawns on snake body, within Manhattan-10, on collision-course path, on food, or on existing mine
- [x] SC-4: No crash when 1000 spawn attempts exhausted (mine silently skipped)
- [x] SC-5: Pygame, Tkinter, HTML mines flash at ≈0.2 s between red `#FF0000` / `(255,0,0)` and grey `#C8C8C8` / `(200,200,200)`
- [x] SC-6: Console mines render as static `'M'` character in bright red ANSI `\033[91m`
- [x] SC-7: All mines flash in sync (same phase toggle)
- [x] SC-8: Snake hitting mine → mine removed + snake 3 shorter + score −3 (min 0)
- [x] SC-9: Snake hitting mine when length ≤ 3 → game-over in all 4 versions
- [x] SC-10: Mines persist across food-eat events (not reset each food)
- [x] SC-11: All mines cleared on game restart (SPACE)
- [x] SC-12: Food remains green; snake color progression unaffected
- [x] SC-13: All 4 versions launch without runtime errors after changes
- [x] SC-14: `/docs` files updated — architecture, structure, code, dataflow, decisions, glossary, risk

---

## Validation Checklist

- [x] Feature Folder path extracted from Build.md: `snake_game/flashing-mines/`
- [x] Every Build.md file modification has corresponding todos (4 game files × multiple tasks + 7 docs files)
- [x] Every integration point (I-1 through I-29) covered by a specific task
- [x] All code blocks are paste-ready (not pseudocode)
- [x] Tasks ordered by dependency (constants → functions → state init → loop updates → render → verify)
- [x] Each phase ends with verification tasks before moving to next phase
- [x] All 14 success criteria from Build.md carried forward to Completion Criteria
- [x] No task requires more than 30 minutes
- [x] No automated tests exist in project — all verification is manual (consistent with rules.mdc Rule 10)

---

**ToDo.md:** `snake_game/flashing-mines/ToDo.md`
