# Build Guide: Flashing Mines

Feature Folder: `snake_game/flashing-mines/`

---

## Feature Overview

Add flashing mine obstacles to all four Snake Game versions (`snake_game.py`, `snake_game_tkinter.py`, `snake_game_console.py`, `snake_game.html`). Mines scale in count with score, spawn with validated placement, flash red/grey at 0.2 s intervals, and damage the snake on collision.

Addresses deliverables: D-1 (Mine entity), D-2 (Mine count scaling), D-3 (Mine spawn validation), D-4 (Mine persistence), D-5 (Mine collision), D-6 (Flash timing), D-7 (Documentation updates)

---

## File Structure

### Files to Modify

---

**File:** `snake_game/snake_game.py`
**Status:** MODIFY EXISTING
**Reference pattern:** Food class (lines 107–115), `draw_food` (lines 143–159), `main()` game loop (lines 190–251), `food_particles` global (line 254)
**Dependencies:** No new imports — uses existing `pygame`, `random`, `math`

**Changes Required:**

1. **Add constants** — after existing color block (~line 22):
```python
MINE_COLOR_A = (255, 0, 0)        # Bright red
MINE_COLOR_B = (200, 200, 200)    # Light grey
MINE_FLASH_INTERVAL = 0.2         # Seconds
```

2. **Add new function `spawn_mine()`** — add as a top-level function alongside `draw_food`, `draw_snake` etc.:
```python
def spawn_mine(mines, snake_body, snake_direction, food_pos, score):
    expected_count = 1 + score // 5
    mines_to_add = expected_count - len(mines)
    if mines_to_add <= 0:
        return
    for _ in range(mines_to_add):
        for attempts in range(1000):
            cx = random.randint(0, GRID_WIDTH - 1)
            cy = random.randint(0, GRID_HEIGHT - 1)
            candidate = (cx, cy)
            if candidate in snake_body:
                continue
            if any(abs(cx - sx) + abs(cy - sy) <= 10 for sx, sy in snake_body):
                continue
            hx, hy = snake_body[0]
            dx, dy = snake_direction
            path = set()
            px, py = hx + dx, hy + dy
            while 0 <= px < GRID_WIDTH and 0 <= py < GRID_HEIGHT:
                path.add((px, py))
                px += dx
                py += dy
            if candidate in path:
                continue
            if candidate == food_pos:
                continue
            if candidate in mines:
                continue
            mines.append(candidate)
            break
        # silently skip if 1000 attempts exhausted
```

3. **Add new function `draw_mines()`** — add alongside other draw functions:
```python
def draw_mines(screen, mines, flash_state):
    color = MINE_COLOR_A if flash_state else MINE_COLOR_B
    for mx, my in mines:
        pygame.draw.rect(screen, color, (mx * GRID_SIZE, my * GRID_SIZE, GRID_SIZE, GRID_SIZE))
```

4. **`main()` — initialise mine state** — after `score = 0` (line ~197):
```python
mines = []
mine_flash_state = False
mine_flash_accumulator = 0.0
```

5. **`main()` — restart block** — inside the `pygame.K_SPACE` handler (line ~210), add after `score = 0`:
```python
mines = []
mine_flash_state = False
mine_flash_accumulator = 0.0
```

6. **`main()` — update section** — after the `snake.eat_food()` block (line ~232), add:
```python
if snake.eat_food(food.position):
    score += 1
    food = Food(snake.body)
    create_food_particles(food.position)
    spawn_mine(mines, snake.body, snake.direction, food.position, score)   # ADD THIS LINE
```

7. **`main()` — update section** — add flash accumulator update and mine collision check. Insert after `snake.move()` and before `snake.check_collision()` (line ~228):
```python
# Flash timer
mine_flash_accumulator += clock.get_time() / 1000.0
if mine_flash_accumulator >= MINE_FLASH_INTERVAL:
    mine_flash_state = not mine_flash_state
    mine_flash_accumulator = 0.0

# Mine collision (check next_head, consistent with wall/self collision pattern)
if snake.next_head in mines:
    mines.remove(snake.next_head)
    shrink = min(3, len(snake.body))
    del snake.body[-shrink:]
    score = max(0, score - 3)
    if len(snake.body) == 0:
        game_over = True
```

8. **`main()` — render section** — add `draw_mines()` call after `draw_grid()` and before `draw_snake()` (line ~240–241):
```python
draw_grid(screen)
draw_mines(screen, mines, mine_flash_state)   # ADD THIS LINE
draw_snake(screen, snake)
```

---

**File:** `snake_game/snake_game_tkinter.py`
**Status:** MODIFY EXISTING
**Reference pattern:** `SnakeGame` class (lines 30–160); `reset_game()` (lines 58–66); `move_snake()` (lines 79–105); `draw()` (lines 107–141); `root.after(GAME_SPEED, self.game_loop)` (line 149)
**Dependencies:** No new imports

**Changes Required:**

1. **Add constants** — after existing color block (~line 22):
```python
MINE_COLOR_A = '#FF0000'
MINE_COLOR_B = '#C8C8C8'
MINE_FLASH_INTERVAL = 200   # milliseconds
```

2. **`reset_game()`** — add mine state reset and flash timer management (after `self.color_index = 0`, line ~65):
```python
self.mines = []
self.mine_flash_state = False
if hasattr(self, '_flash_after_id'):
    self.root.after_cancel(self._flash_after_id)
self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)
```

3. **Add new method `_toggle_mine_flash()`** — inside `SnakeGame` class:
```python
def _toggle_mine_flash(self):
    self.mine_flash_state = not self.mine_flash_state
    self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)
```

4. **Add new method `_try_spawn_mine()`** — inside `SnakeGame` class:
```python
def _try_spawn_mine(self):
    expected_count = 1 + self.score // 5
    mines_to_add = expected_count - len(self.mines)
    if mines_to_add <= 0:
        return
    for _ in range(mines_to_add):
        for attempts in range(1000):
            cx = random.randint(0, GRID_WIDTH - 1)
            cy = random.randint(0, GRID_HEIGHT - 1)
            candidate = (cx, cy)
            if candidate in self.snake:
                continue
            if any(abs(cx - sx) + abs(cy - sy) <= 10 for sx, sy in self.snake):
                continue
            hx, hy = self.snake[0]
            dx, dy = self.direction
            path = set()
            px, py = hx + dx, hy + dy
            while 0 <= px < GRID_WIDTH and 0 <= py < GRID_HEIGHT:
                path.add((px, py))
                px += dx
                py += dy
            if candidate in path:
                continue
            if candidate == self.food:
                continue
            if candidate in self.mines:
                continue
            self.mines.append(candidate)
            break
```

5. **`move_snake()`** — add mine spawn call after food consumption block (after `self.food = self.generate_food()`, line ~101):
```python
self._try_spawn_mine()
```

6. **`move_snake()`** — add mine collision check after food consumption block, before `return False` (line ~104):
```python
if new_head in self.mines:
    self.mines.remove(new_head)
    shrink = min(3, len(self.snake))
    del self.snake[-shrink:]
    self.score = max(0, self.score - 3)
    self.score_label.config(text=f"Score: {self.score}")
    if len(self.snake) == 0:
        return True   # triggers game_over = True in game_loop()
```

7. **`draw()`** — add mine drawing after grid lines, before snake (after the grid for-loops, before the snake for-loop, ~line 116):
```python
mine_color = MINE_COLOR_A if self.mine_flash_state else MINE_COLOR_B
for mx, my in self.mines:
    x1 = mx * GRID_SIZE
    y1 = my * GRID_SIZE
    self.canvas.create_rectangle(x1, y1, x1 + GRID_SIZE, y1 + GRID_SIZE,
                                  fill=mine_color, outline='')
```

---

**File:** `snake_game/snake_game_console.py`
**Status:** MODIFY EXISTING
**Reference pattern:** `Snake` class (lines 28–58); `Food` class (lines 61–68); `draw_game()` (lines 71–101); `main()` (lines 104–139)
**Dependencies:** No new imports

**Changes Required:**

1. **Add constants** — after existing ANSI color block (~line 20):
```python
MINE_CHAR = 'M'
MINE_COLOR = '\033[91m'   # Bright red ANSI — no flash (console limitation)
```

2. **Add new function `spawn_mine()`** — add as a top-level function (no flash timer needed):
```python
def spawn_mine(mines, snake_body, snake_direction, food_pos, score):
    expected_count = 1 + score // 5
    mines_to_add = expected_count - len(mines)
    if mines_to_add <= 0:
        return
    for _ in range(mines_to_add):
        for attempts in range(1000):
            cx = random.randint(0, GRID_WIDTH - 1)
            cy = random.randint(0, GRID_HEIGHT - 1)
            candidate = (cx, cy)
            if candidate in snake_body:
                continue
            if any(abs(cx - sx) + abs(cy - sy) <= 10 for sx, sy in snake_body):
                continue
            # Path projection uses modulo wrap (console uses wrapping movement)
            hx, hy = snake_body[0]
            dx, dy = snake_direction
            path = set()
            px = (hx + dx) % GRID_WIDTH
            py = (hy + dy) % GRID_HEIGHT
            visited = set()
            while (px, py) not in visited:
                visited.add((px, py))
                path.add((px, py))
                px = (px + dx) % GRID_WIDTH
                py = (py + dy) % GRID_HEIGHT
            if candidate in path:
                continue
            if candidate == food_pos:
                continue
            if candidate in mines:
                continue
            mines.append(candidate)
            break
```

3. **`draw_game()`** — mark mine cells in the grid array, after marking food (after `grid[food.position[1]][food.position[0]] = '●'`, ~line 80):
```python
for mx, my in mines:
    grid[my][mx] = MINE_CHAR
```

4. **`draw_game()`** — render 'M' cells in the print loop. Update the cell rendering block (inside the row/cell loop, ~line 88–98) to handle `MINE_CHAR`:
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

5. **`draw_game()` signature** — update to accept `mines`:
```python
def draw_game(snake, food, mines, score):
```

6. **`main()` — initialise mine state** — after `score = 0` (line ~108):
```python
mines = []
```

7. **`main()` — game loop** — update `draw_game()` call to pass `mines` (~line 111):
```python
draw_game(snake, food, mines, score)
```

8. **`main()` — game loop** — add mine spawn after food-eat block (after `food = Food(snake.body)`, ~line 115):
```python
spawn_mine(mines, snake.body, snake.direction, food.position, score)
```

9. **`main()` — game loop** — add mine collision check after `snake.move()` (~line 117):
```python
if snake.body[0] in mines:
    mines.remove(snake.body[0])
    shrink = min(3, len(snake.body))
    del snake.body[-shrink:]
    score = max(0, score - 3)
    if len(snake.body) == 0:
        game_over = True
```

---

**File:** `snake_game/snake_game.html`
**Status:** MODIFY EXISTING
**Reference pattern:** Global state (lines 144–151); `init()` (lines 154–167); `update()` (lines 182–214); `draw()` (lines 217–306); `endGame()` (lines 309–313)
**Dependencies:** No new dependencies

**Changes Required:**

1. **Add constants** — in the JS constants block, after existing color constants (~line 123):
```javascript
const MINE_COLOR_A = '#FF0000';
const MINE_COLOR_B = '#C8C8C8';
const MINE_FLASH_INTERVAL = 200; // milliseconds
```

2. **Add global state** — after `let colorIndex = 0` (~line 151):
```javascript
let mines = [];
let mineFlashState = false;
let mineFlashTimer = null;
```

3. **`init()`** — add mine reset and flash timer management (after `colorIndex = 0`, ~line 161):
```javascript
mines = [];
mineFlashState = false;
if (mineFlashTimer) clearInterval(mineFlashTimer);
mineFlashTimer = setInterval(() => { mineFlashState = !mineFlashState; }, MINE_FLASH_INTERVAL);
```

4. **`endGame()`** — clear flash timer (after `gameOver = true`, ~line 310):
```javascript
if (mineFlashTimer) clearInterval(mineFlashTimer);
```

5. **Add new function `trySpawnMine()`** — add alongside `generateFood()`:
```javascript
function trySpawnMine() {
    const expectedCount = 1 + Math.floor(score / 5);
    const minesToAdd = expectedCount - mines.length;
    if (minesToAdd <= 0) return;
    for (let m = 0; m < minesToAdd; m++) {
        let placed = false;
        for (let attempt = 0; attempt < 1000; attempt++) {
            const cx = Math.floor(Math.random() * GRID_WIDTH);
            const cy = Math.floor(Math.random() * GRID_HEIGHT);
            const tooClose = snake.some(s => Math.abs(cx - s.x) + Math.abs(cy - s.y) <= 10);
            if (tooClose) continue;
            const onSnake = snake.some(s => s.x === cx && s.y === cy);
            if (onSnake) continue;
            // Collision-course path check
            const path = [];
            let px = snake[0].x + direction.x;
            let py = snake[0].y + direction.y;
            while (px >= 0 && px < GRID_WIDTH && py >= 0 && py < GRID_HEIGHT) {
                path.push({x: px, y: py});
                px += direction.x;
                py += direction.y;
            }
            if (path.some(p => p.x === cx && p.y === cy)) continue;
            if (food.x === cx && food.y === cy) continue;
            if (mines.some(mi => mi.x === cx && mi.y === cy)) continue;
            mines.push({x: cx, y: cy});
            placed = true;
            break;
        }
        // silently skip if 1000 attempts exhausted
    }
}
```

6. **`update()`** — add mine spawn call after food consumption block (after `food = generateFood()`, ~line 209):
```javascript
trySpawnMine();
```

7. **`update()`** — add mine collision check after self-collision check (~line 198), before `snake.unshift(head)`:
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

8. **`draw()`** — add mine drawing after grid, before snake (~line 238, after the grid stroke loops):
```javascript
const mineColor = mineFlashState ? MINE_COLOR_A : MINE_COLOR_B;
mines.forEach(m => {
    ctx.fillStyle = mineColor;
    ctx.fillRect(m.x * GRID_SIZE + 1, m.y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2);
});
```

---

**File:** `snake_game/docs/architecture.md`
**Status:** MODIFY EXISTING
**Changes Required:**
- Add Mine as a new game entity/component under "Key Components and Relationships"
- Add mine state to Rendering Pipeline section (step between grid and snake)
- Update Component Interaction Diagram to show mine collision branch

**File:** `snake_game/docs/structure.md`
**Status:** MODIFY EXISTING
**Changes Required:**
- Add `spawn_mine()` and `draw_mines()` (Pygame), `_try_spawn_mine()` and `_toggle_mine_flash()` (Tkinter), `spawn_mine()` (Console), `trySpawnMine()` (HTML) to per-file function lists

**File:** `snake_game/docs/code.md`
**Status:** MODIFY EXISTING
**Changes Required:**
- Document `spawn_mine()` spawn logic, flash logic, and collision logic for each version

**File:** `snake_game/docs/dataflow.md`
**Status:** MODIFY EXISTING
**Changes Required:**
- Add Pipeline: Mine Collision Data Flow (head → mine check → remove mine → shrink → score adjust → game-over check)

**File:** `snake_game/docs/decisions.md`
**Status:** MODIFY EXISTING
**Changes Required:**
- Add ADR for mine placement algorithm (list-of-tuples over Mine class; 1000-attempt graceful skip)
- Add ADR for shrink-on-hit decision (3 segments / score -3 / game-over at 0)

**File:** `snake_game/docs/glossary.md`
**Status:** MODIFY EXISTING
**Changes Required:**
- Add definitions: Mine, Mine Collision, Flash Cycle, Safe Spawn Radius

**File:** `snake_game/docs/risk.md`
**Status:** MODIFY EXISTING
**Changes Required:**
- Add PERF risk: spawn failure edge case (1000 attempts on crowded grid)
- Add LOGIC risk: shrink-to-zero game over edge case

---

## Technical Specifications

### Data Schemas

**Python mine state (all Python versions):**
```python
mines: list[tuple[int, int]] = []     # grid coords e.g. [(5, 10), (12, 3)]
mine_flash_state: bool = False        # True = MINE_COLOR_A (red), False = MINE_COLOR_B (grey)
mine_flash_accumulator: float = 0.0  # Pygame only — seconds since last toggle
```

**JavaScript mine state:**
```javascript
mines: Array<{x: number, y: number}>  // e.g. [{x:5,y:10},{x:12,y:3}]
mineFlashState: boolean               // true = '#FF0000', false = '#C8C8C8'
mineFlashTimer: number | null         // setInterval ID
```

**New constants:**

| Constant | Pygame | Tkinter | Console | HTML/JS |
|----------|--------|---------|---------|---------|
| `MINE_COLOR_A` | `(255, 0, 0)` | `'#FF0000'` | N/A | `'#FF0000'` |
| `MINE_COLOR_B` | `(200, 200, 200)` | `'#C8C8C8'` | N/A | `'#C8C8C8'` |
| `MINE_FLASH_INTERVAL` | `0.2` (seconds) | `200` (ms) | N/A | `200` (ms) |
| `MINE_CHAR` | N/A | N/A | `'M'` | N/A |
| `MINE_COLOR` | N/A | N/A | `'\033[91m'` | N/A |

### Error Handling

| Scenario | Handling |
|----------|---------|
| No valid spawn in 1000 attempts | `break` / exit inner loop silently — no exception, no crash |
| `score - 3 < 0` | `score = max(0, score - 3)` / `score = Math.max(0, score - 3)` |
| Snake length reaches 0 after shrink | Set `game_over = True` / call `endGame()` immediately |
| Empty mines list during collision check | `in` operator (Python) / `.findIndex()` (JS) return falsy — no-op |

### Dependencies

**Existing — no changes to requirements.txt:**

| Version | Libraries |
|---------|-----------|
| Pygame | `pygame==2.5.2` (requirements.txt), `random`, `math` (stdlib) |
| Tkinter | `tkinter` (built-in), `random` (stdlib) |
| Console | `random`, `os`, `time` (stdlib) |
| HTML | Vanilla JS, Canvas 2D API (browser built-in) |

**New dependencies:** None.

### Integration Points

| # | File | Section / Location | What to add |
|---|------|--------------------|-------------|
| I-1 | `snake_game.py` | After color constants (~line 22) | 3 new `MINE_*` constants |
| I-2 | `snake_game.py` | After `draw_gradient_background` function | New `spawn_mine()` function |
| I-3 | `snake_game.py` | After `draw_food` function | New `draw_mines()` function |
| I-4 | `snake_game.py` | `main()` after `score = 0` (~line 197) | Mine state variables |
| I-5 | `snake_game.py` | `main()` SPACE restart handler (~line 210) | Reset mine state variables |
| I-6 | `snake_game.py` | `main()` after `create_food_particles()` call (~line 232) | `spawn_mine()` call |
| I-7 | `snake_game.py` | `main()` update section after `snake.move()` | Flash accumulator + mine collision block |
| I-8 | `snake_game.py` | `main()` render section after `draw_grid()` (~line 240) | `draw_mines()` call |
| I-9 | `snake_game_tkinter.py` | After color constants (~line 22) | 3 new `MINE_*` constants |
| I-10 | `snake_game_tkinter.py` | `SnakeGame` class — new methods | `_toggle_mine_flash()`, `_try_spawn_mine()` |
| I-11 | `snake_game_tkinter.py` | `reset_game()` after `self.color_index = 0` | Mine state + flash timer init |
| I-12 | `snake_game_tkinter.py` | `move_snake()` after `self.food = self.generate_food()` | `_try_spawn_mine()` call + mine collision block |
| I-13 | `snake_game_tkinter.py` | `draw()` after grid lines, before snake loop | Mine canvas drawing block |
| I-14 | `snake_game_console.py` | After ANSI constants (~line 20) | `MINE_CHAR`, `MINE_COLOR` |
| I-15 | `snake_game_console.py` | After `Food` class | New `spawn_mine()` function |
| I-16 | `snake_game_console.py` | `draw_game()` — signature and grid construction | Accept `mines` param; mark mine cells |
| I-17 | `snake_game_console.py` | `draw_game()` — cell render loop | MINE_CHAR render branch |
| I-18 | `snake_game_console.py` | `main()` after `score = 0` | `mines = []` |
| I-19 | `snake_game_console.py` | `main()` game loop — `draw_game()` call | Pass `mines` argument |
| I-20 | `snake_game_console.py` | `main()` after `food = Food(snake.body)` | `spawn_mine()` call |
| I-21 | `snake_game_console.py` | `main()` after `snake.move()` | Mine collision block |
| I-22 | `snake_game.html` | JS constants block after existing colors (~line 123) | 3 new `MINE_*` constants |
| I-23 | `snake_game.html` | Global state after `colorIndex` (~line 151) | `mines`, `mineFlashState`, `mineFlashTimer` |
| I-24 | `snake_game.html` | `init()` after `colorIndex = 0` (~line 161) | Mine reset + flash timer start |
| I-25 | `snake_game.html` | `endGame()` after `gameOver = true` | Flash timer clear |
| I-26 | `snake_game.html` | After `generateFood()` function | New `trySpawnMine()` function |
| I-27 | `snake_game.html` | `update()` after `food = generateFood()` (~line 209) | `trySpawnMine()` call |
| I-28 | `snake_game.html` | `update()` after self-collision check (~line 198) | Mine collision block |
| I-29 | `snake_game.html` | `draw()` after grid loops, before snake loop (~line 238) | Mine canvas drawing block |

---

## Implementation Flow

### Normal Gameplay Flow

```
1. Game init  → mines = [], flash timer starts
2. Player eats food → score += 1
3. spawn_mine() called:
     expected = 1 + floor(score / 5)
     while len(mines) < expected: validate and append candidate (max 1000 tries)
4. New food generated (existing logic, unaffected)
5. Flash timer fires every 0.2s → mine_flash_state toggles (all mines sync)
6. Render order each frame:
     background → grid → mines (flash colour) → snake → food → score
7. Snake moves to new head position
8. Mine collision check (head == any mine):
     → remove mine from list
     → shrink snake tail by min(3, len)
     → score = max(0, score - 3)
     → if len(snake) == 0: game_over = True
9. Existing wall + self-collision checks follow (unchanged)
```

### Mine Collision Flow

```
snake head lands on mine cell
    ├─→ mines.remove(mine_cell)
    ├─→ shrink = min(3, len(snake))
    ├─→ del snake[-shrink:]  /  snake.splice(len-shrink, shrink)
    ├─→ score = max(0, score - 3)
    ├─→ update score display
    └─→ len(snake) == 0?
          Yes → game_over = True
          No  → continue game
```

### Game Restart Flow

```
SPACE pressed (game_over state)
    ├─→ mines = []
    ├─→ mine_flash_state = False
    ├─→ cancel existing flash timer; start new flash timer
    └─→ existing snake / food / score reset (unchanged)
```

---

## Testing Requirements

No automated tests exist in this project. All testing is manual.

### Manual Test Procedure (run for each of the 4 versions)

| # | Step | Expected Result |
|---|------|----------------|
| T-1 | Launch game, eat 1 food | Exactly 1 mine appears on grid |
| T-2 | Continue eating until score = 5 | Exactly 2 mines appear |
| T-3 | Continue eating until score = 10 | Exactly 3 mines appear |
| T-4 | Observe mine position after spawning | Mine is not on snake body, not on food, not within 10 grid cells (Manhattan) of any snake segment |
| T-5 | Watch Pygame / Tkinter / HTML versions for ~1 second | Mine flashes red ↔ grey approx 5 times per second |
| T-6 | Run console version, eat food | 'M' character appears on grid (no flash) |
| T-7 | Navigate snake head into a mine | Mine disappears; snake is 3 segments shorter; score drops by 3 (min 0) |
| T-8 | Navigate snake (length ≤ 3) into a mine | Game Over triggered immediately |
| T-9 | Hit mine with score ≤ 3 | Score shows 0 (not negative) |
| T-10 | Game over → press SPACE | All mines cleared; mine count resets on next food eat |
| T-11 | Eat multiple foods rapidly | Old mines remain; only new mines added per food event |
| T-12 | Eat food; observe food respawn | Food still green; snake colour progression unaffected |

### Verification Commands

**Build Verification:**
```bash
python snake_game.py
python snake_game_tkinter.py
python snake_game_console.py
```
Open `snake_game.html` in browser → DevTools → Console → confirm zero JS errors.

**Manual Visual Verification:**
```
Pygame:   run → eat 1 food → mine appears → observe red/grey flash ~5×/sec
Tkinter:  run → eat 1 food → mine appears → observe red/grey flash ~5×/sec
HTML:     open in browser → eat 1 food → mine appears → DevTools Console clean
Console:  run → eat 1 food → 'M' character visible in grid border
```

---

## Implementation Success Criteria

All of the following must be satisfied before the feature is considered complete:

- [ ] SC-1: Mine appears on grid after first food eaten — all 4 versions
- [ ] SC-2: Mine count equals `1 + floor(score / 5)` at score 1, 5, 10, 15
- [ ] SC-3: Mine never spawns on snake body, within Manhattan-10, on collision-course path, on food, or on existing mine
- [ ] SC-4: No crash when 1000 spawn attempts exhausted (mine silently skipped)
- [ ] SC-5: Pygame, Tkinter, HTML mines flash at ≈0.2 s between red `#FF0000` and grey `#C8C8C8`
- [ ] SC-6: Console mines render as static `'M'` character in bright red ANSI
- [ ] SC-7: All mines flash in sync (same phase toggle)
- [ ] SC-8: Snake hitting mine → mine removed + snake 3 shorter + score −3 (min 0)
- [ ] SC-9: Snake hitting mine when length ≤ 3 → game-over in all 4 versions
- [ ] SC-10: Mines persist across food-eat events (not reset each food)
- [ ] SC-11: All mines cleared on game restart (SPACE)
- [ ] SC-12: Food remains green; snake color progression unaffected
- [ ] SC-13: All 4 versions launch without runtime errors after changes
- [ ] SC-14: `/docs` files updated (architecture, structure, code, dataflow, decisions, glossary, risk)

---

## Validation Checklist

- [x] Feature Folder path extracted from Implementation Plan: `snake_game/flashing-mines/`
- [x] All 4 modified files exist in workspace (verified during plan creation)
- [x] All 7 docs files exist: `docs/architecture.md`, `docs/structure.md`, `docs/code.md`, `docs/dataflow.md`, `docs/decisions.md`, `docs/glossary.md`, `docs/risk.md`
- [x] All pattern references point to actual file line numbers (verified against source)
- [x] No new packages required — all existing dependencies
- [x] Every deliverable (D-1 through D-7) has corresponding build instructions
- [x] All integration points numbered and specific (I-1 through I-29)
- [x] All verification commands are complete and executable
- [x] No rationale, alternatives, or rollback content included (kept in Plan.md only)

---

**Build.md:** `snake_game/flashing-mines/Build.md`
