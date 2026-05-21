# Build Guide: Mine Detonation Storm
**Feature ID:** MDS-001  
**Feature Folder:** `mine-detonation-storm/`  
**Plan Reference:** `mine-detonation-storm/Plan.md`  
**Date:** 2026-03-06

---

## Pre-Implementation Checklist

Before modifying any file:

- [ ] Confirm Flashing Mines feature is present and functional in all 4 versions
- [ ] Back up all 4 game files:

```powershell
Copy-Item snake_game.py snake_game.py.bak-mds
Copy-Item snake_game_tkinter.py snake_game_tkinter.py.bak-mds
Copy-Item snake_game_console.py snake_game_console.py.bak-mds
Copy-Item snake_game.html snake_game.html.bak-mds
```

---

## Phase 1 — Pygame (`snake_game.py`)

### Step 1.1 — Add new constants

Add the following block immediately after line 26 (`MINE_FLASH_INTERVAL = 0.2`), before the `# Snake color palette` comment:

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

### Step 1.2 — Add storm drawing functions

Add the following three functions immediately after `draw_mines()` (after line 352, before `if __name__ == '__main__':`):

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

### Step 1.3 — Initialise storm state in `main()`

In `main()`, locate the existing mine state initialisation block:
```python
    mines = []
    mine_flash_state = False
    mine_flash_accumulator = 0.0
```

Add the following **immediately after** those three lines:

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

### Step 1.4 — Add storm state to restart block

In `main()`, locate the restart block inside the `if event.key == pygame.K_SPACE:` branch:
```python
                        mines = []
                        mine_flash_state = False
                        mine_flash_accumulator = 0.0
```

Add the following **immediately after** those three lines, still inside the `if event.key == pygame.K_SPACE:` block:

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

### Step 1.5 — Replace the `if not game_over:` logic block

Locate the entire `if not game_over:` block in `main()`. It currently reads:

```python
        if not game_over:
            snake.move()

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
            
            # Check for food consumption
            if snake.eat_food(food.position):
                score += 1
                food = Food(snake.body)
                create_food_particles(food.position)
                spawn_mine(mines, snake.body, snake.direction, food.position, score)
            
            # Check for collision
            if snake.check_collision():
                game_over = True
```

Replace it entirely with:

```python
        if not game_over:
            snake.move()
            dt = clock.get_time() / 1000.0

            # Mine flash timer
            mine_flash_accumulator += dt
            if mine_flash_accumulator >= MINE_FLASH_INTERVAL:
                mine_flash_state = not mine_flash_state
                mine_flash_accumulator = 0.0

            # Storm timers
            if storm_active:
                # Border flash
                border_flash_acc += dt
                if border_flash_acc >= STORM_BORDER_FLASH_INTERVAL:
                    border_flash_state = not border_flash_state
                    border_flash_acc = 0.0

                # Warning flash (cycles through EXPLOSION_COLORS index)
                if storm_phase == 'warning':
                    storm_warning_flash_acc += dt
                    if storm_warning_flash_acc >= WARNING_FLASH_INTERVAL:
                        storm_warning_flash_index = (storm_warning_flash_index + 1) % len(EXPLOSION_COLORS)
                        storm_warning_flash_acc = 0.0

                # Phase elapsed
                storm_phase_elapsed += dt

                if storm_phase == 'warning' and storm_phase_elapsed >= WARNING_DURATION:
                    # Transition to explosion
                    storm_phase = 'explosion'
                    storm_phase_elapsed = 0.0
                    bonus_foods.append(storm_current_mine)

                elif storm_phase == 'explosion':
                    # Phase 2 kill check
                    mx, my = storm_current_mine
                    blast_cells = set()
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            cx, cy = mx + dx, my + dy
                            if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                                blast_cells.add((cx, cy))
                    if snake.next_head in blast_cells:
                        game_over = True
                        storm_active = False
                        storm_queue = []
                        storm_phase = None
                        storm_current_mine = None
                        storm_phase_elapsed = 0.0
                        border_flash_state = False
                        bonus_foods = []

                    elif storm_phase_elapsed >= EXPLOSION_DURATION:
                        if storm_queue:
                            storm_current_mine = storm_queue.pop(0)
                            storm_phase = 'warning'
                            storm_phase_elapsed = 0.0
                            storm_warning_flash_acc = 0.0
                            storm_warning_flash_index = 0
                        else:
                            storm_active = False
                            storm_phase = None
                            storm_current_mine = None
                            storm_phase_elapsed = 0.0
                            border_flash_state = False

            # Mine collision (check next_head)
            if snake.next_head in mines:
                mines.remove(snake.next_head)
                shrink = min(3, len(snake.body))
                del snake.body[-shrink:]
                score = max(0, score - 3)
                if len(snake.body) == 0:
                    game_over = True

            # Bonus food consumption
            if snake.next_head in bonus_foods:
                bonus_foods.remove(snake.next_head)
                snake.grow = True
                snake.color_index = (snake.color_index + 1) % len(SNAKE_COLORS)
                score += 1
                spawn_mine(mines, snake.body, snake.direction, food.position, score)

            # Check for food consumption
            if snake.eat_food(food.position):
                score += 1
                food = Food(snake.body)
                create_food_particles(food.position)
                spawn_mine(mines, snake.body, snake.direction, food.position, score)
                # Storm trigger
                if not storm_active and len(mines) >= STORM_TRIGGER_COUNT:
                    storm_active = True
                    storm_queue = mines[:]
                    random.shuffle(storm_queue)
                    mines.clear()
                    border_flash_state = False
                    border_flash_acc = 0.0
                    storm_current_mine = storm_queue.pop(0)
                    storm_phase = 'warning'
                    storm_phase_elapsed = 0.0
                    storm_warning_flash_acc = 0.0
                    storm_warning_flash_index = 0

            # Check for collision
            if snake.check_collision():
                game_over = True
```

### Step 1.6 — Replace the drawing pipeline

Locate the existing drawing block (currently lines 266–276):

```python
        # Drawing
        draw_gradient_background(screen)
        draw_grid(screen)
        draw_mines(screen, mines, mine_flash_state)
        draw_snake(screen, snake)
        draw_food(screen, food)
        draw_food_particles(screen)
        draw_score(screen, score)
        
        if game_over:
            game_over_screen(screen, score)
```

Replace it entirely with:

```python
        # Drawing
        draw_gradient_background(screen)
        draw_grid(screen)
        if storm_active:
            draw_storm_border(screen, border_flash_state)
        if storm_active and storm_phase == 'explosion' and storm_current_mine:
            draw_explosion_cells(screen, storm_current_mine)
        if storm_active and storm_phase == 'warning' and storm_current_mine:
            draw_warning_cell(screen, storm_current_mine, storm_warning_flash_index)
        draw_mines(screen, mines, mine_flash_state)
        draw_bonus_foods(screen, bonus_foods)
        draw_food(screen, food)
        draw_food_particles(screen)
        draw_snake(screen, snake)
        draw_score(screen, score)

        if game_over:
            game_over_screen(screen, score)
```

### Step 1.7 — Syntax validation

```powershell
py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
```

No output = success. Any output = error to fix before proceeding.

---

## Phase 2 — Tkinter (`snake_game_tkinter.py`)

### Step 2.1 — Add new constants

Add the following block immediately after line 15 (`MINE_FLASH_INTERVAL = 200`), before the `# Snake color palette` comment:

```python
# Mine Detonation Storm constants
STORM_TRIGGER_COUNT = 10
STORM_BORDER_COLOR_A = '#FF0000'
STORM_BORDER_COLOR_B = '#000000'
STORM_BORDER_FLASH_INTERVAL = 200   # milliseconds
WARNING_DURATION_MS = 3000          # milliseconds
WARNING_FLASH_INTERVAL = 200        # milliseconds
EXPLOSION_DURATION_MS = 1000        # milliseconds
EXPLOSION_COLORS = [
    '#FF0000',
    '#FF8800',
    '#FFFF00',
    '#FFFFFF',
    '#FF4400',
]
```

### Step 2.2 — Add storm state to `reset_game()`

In `reset_game()`, locate:
```python
        self.mines = []
        self.mine_flash_state = False
        if hasattr(self, '_flash_after_id'):
            self.root.after_cancel(self._flash_after_id)
        self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)
```

Add the following block **immediately after** those lines, still inside `reset_game()`:

```python
        # Storm state reset
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

### Step 2.3 — Add storm methods to `SnakeGame`

Add the following five methods to the `SnakeGame` class. Insert them **after** `_try_spawn_mine()` (at the end of the class body, before `def main():`):

```python
    def _start_storm(self):
        self.storm_active = True
        self.storm_queue = self.mines[:]
        random.shuffle(self.storm_queue)
        self.mines = []
        self.border_flash_state = False
        if hasattr(self, '_border_flash_after_id') and self._border_flash_after_id:
            self.root.after_cancel(self._border_flash_after_id)
        self._border_flash_after_id = self.root.after(
            STORM_BORDER_FLASH_INTERVAL, self._toggle_border_flash)
        self._begin_warning_phase()

    def _begin_warning_phase(self):
        if not self.storm_queue:
            self._end_storm()
            return
        self.storm_current_mine = self.storm_queue.pop(0)
        self.storm_phase = 'warning'
        self.storm_warning_flash_state = False
        if hasattr(self, '_warning_flash_after_id') and self._warning_flash_after_id:
            self.root.after_cancel(self._warning_flash_after_id)
        self._warning_flash_after_id = self.root.after(
            WARNING_FLASH_INTERVAL, self._toggle_warning_flash)
        if hasattr(self, '_storm_phase_after_id') and self._storm_phase_after_id:
            self.root.after_cancel(self._storm_phase_after_id)
        self._storm_phase_after_id = self.root.after(
            WARNING_DURATION_MS, self._begin_explosion_phase)

    def _begin_explosion_phase(self):
        self.storm_phase = 'explosion'
        self.bonus_foods.append(self.storm_current_mine)
        if hasattr(self, '_warning_flash_after_id') and self._warning_flash_after_id:
            self.root.after_cancel(self._warning_flash_after_id)
        self._warning_flash_after_id = None
        if hasattr(self, '_storm_phase_after_id') and self._storm_phase_after_id:
            self.root.after_cancel(self._storm_phase_after_id)
        self._storm_phase_after_id = self.root.after(
            EXPLOSION_DURATION_MS, self._advance_storm_phase)

    def _advance_storm_phase(self):
        if self.storm_queue:
            self._begin_warning_phase()
        else:
            self._end_storm()

    def _end_storm(self):
        self.storm_active = False
        self.storm_phase = None
        self.storm_current_mine = None
        self.border_flash_state = False
        if hasattr(self, '_border_flash_after_id') and self._border_flash_after_id:
            self.root.after_cancel(self._border_flash_after_id)
        self._border_flash_after_id = None
        if hasattr(self, '_warning_flash_after_id') and self._warning_flash_after_id:
            self.root.after_cancel(self._warning_flash_after_id)
        self._warning_flash_after_id = None
        if hasattr(self, '_storm_phase_after_id') and self._storm_phase_after_id:
            self.root.after_cancel(self._storm_phase_after_id)
        self._storm_phase_after_id = None
        self.storm_queue = []

    def _toggle_border_flash(self):
        if not self.storm_active:
            return
        self.border_flash_state = not self.border_flash_state
        self._border_flash_after_id = self.root.after(
            STORM_BORDER_FLASH_INTERVAL, self._toggle_border_flash)

    def _toggle_warning_flash(self):
        if self.storm_phase != 'warning':
            return
        self.storm_warning_flash_state = not self.storm_warning_flash_state
        self._warning_flash_after_id = self.root.after(
            WARNING_FLASH_INTERVAL, self._toggle_warning_flash)
```

### Step 2.4 — Update `move_snake()` — Phase 2 kill check, bonus food, and storm trigger

In `move_snake()`, locate the food consumption block:

```python
        # Check food consumption
        if new_head == self.food:
            self.score += 1
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            self.score_label.config(text=f"Score: {self.score}")
            self.food = self.generate_food()
            self._try_spawn_mine()
        else:
            self.snake.pop()
```

Replace it with:

```python
        # Check food consumption
        if new_head == self.food:
            self.score += 1
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            self.score_label.config(text=f"Score: {self.score}")
            self.food = self.generate_food()
            self._try_spawn_mine()
            # Storm trigger
            if not self.storm_active and len(self.mines) >= STORM_TRIGGER_COUNT:
                self._start_storm()
        else:
            self.snake.pop()
```

Then locate the mine collision check block:

```python
        # Mine collision check
        if new_head in self.mines:
            self.mines.remove(new_head)
            shrink = min(3, len(self.snake))
            del self.snake[-shrink:]
            self.score = max(0, self.score - 3)
            self.score_label.config(text=f"Score: {self.score}")
            if len(self.snake) == 0:
                return True
        
        return False
```

Replace it with:

```python
        # Phase 2 explosion kill check
        if self.storm_active and self.storm_phase == 'explosion' and self.storm_current_mine:
            mx, my = self.storm_current_mine
            blast_cells = set()
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    cx, cy = mx + dx, my + dy
                    if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                        blast_cells.add((cx, cy))
            if new_head in blast_cells:
                self._end_storm()
                return True

        # Bonus food consumption
        if new_head in self.bonus_foods:
            self.bonus_foods.remove(new_head)
            self.snake.insert(0, new_head)
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self._try_spawn_mine()

        # Mine collision check
        if new_head in self.mines:
            self.mines.remove(new_head)
            shrink = min(3, len(self.snake))
            del self.snake[-shrink:]
            self.score = max(0, self.score - 3)
            self.score_label.config(text=f"Score: {self.score}")
            if len(self.snake) == 0:
                return True

        return False
```

**Note on bonus food growth:** The bonus food insert above adds `new_head` to position 0 before the `self.snake.insert(0, new_head)` call earlier in `move_snake()`. To avoid double-insert, the bonus food block must consume it from `bonus_foods` before the normal tail-pop path. The existing `self.snake.insert(0, new_head)` on line 104 has already occurred by this point. So replace the bonus food block's `self.snake.insert(0, new_head)` with simply `self.snake.grow = True` — but since `SnakeGame` does not use a `grow` flag (it uses direct insert/pop), instead set the snake to not pop the tail this tick by re-inserting the head again:

Actually, since the Tkinter version uses direct list manipulation (not a `grow` flag), the correct bonus food growth approach is: do **not** pop the tail for this tick. Since `self.snake.pop()` is only called in the `else` branch of the food check (which already didn't fire because the bonus food isn't `self.food`), the tail has already been popped at this point.

**Correction — revised bonus food block for Tkinter:**

The tail pop happens at the end of the food check `else` branch. When `new_head == self.food` is false, `self.snake.pop()` removes the tail. The bonus food check happens **after** the tail has already been popped. To grow the snake one extra segment when bonus food is eaten, re-append the last element:

```python
        # Bonus food consumption
        if new_head in self.bonus_foods:
            self.bonus_foods.remove(new_head)
            self.snake.append(self.snake[-1])  # grow by 1
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self._try_spawn_mine()
```

Use this corrected version. The full revised `move_snake()` mine collision / bonus food / return section is:

```python
        # Phase 2 explosion kill check
        if self.storm_active and self.storm_phase == 'explosion' and self.storm_current_mine:
            mx, my = self.storm_current_mine
            blast_cells = set()
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    cx, cy = mx + dx, my + dy
                    if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                        blast_cells.add((cx, cy))
            if new_head in blast_cells:
                self._end_storm()
                return True

        # Bonus food consumption
        if new_head in self.bonus_foods:
            self.bonus_foods.remove(new_head)
            self.snake.append(self.snake[-1])
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self._try_spawn_mine()

        # Mine collision check
        if new_head in self.mines:
            self.mines.remove(new_head)
            shrink = min(3, len(self.snake))
            del self.snake[-shrink:]
            self.score = max(0, self.score - 3)
            self.score_label.config(text=f"Score: {self.score}")
            if len(self.snake) == 0:
                return True

        return False
```

### Step 2.5 — Update `draw()` — storm border, explosion cells, warning cell, bonus foods

In `draw()`, locate the mines drawing block:

```python
        # Draw mines
        mine_color = MINE_COLOR_A if self.mine_flash_state else MINE_COLOR_B
        for mx, my in self.mines:
            x1 = mx * GRID_SIZE
            y1 = my * GRID_SIZE
            self.canvas.create_rectangle(x1, y1, x1 + GRID_SIZE, y1 + GRID_SIZE,
                                          fill=mine_color, outline='')
```

Add the following **before** that mines block (after the grid drawing but before mines):

```python
        # Storm border
        if self.storm_active and self.border_flash_state:
            self.canvas.create_rectangle(1, 1, WINDOW_WIDTH - 1, WINDOW_HEIGHT - 1,
                                         outline=STORM_BORDER_COLOR_A, width=2, fill='')

        # Explosion cells (Phase 2)
        if self.storm_active and self.storm_phase == 'explosion' and self.storm_current_mine:
            mx, my = self.storm_current_mine
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    cx, cy = mx + dx, my + dy
                    if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                        color = random.choice(EXPLOSION_COLORS)
                        self.canvas.create_rectangle(
                            cx * GRID_SIZE, cy * GRID_SIZE,
                            cx * GRID_SIZE + GRID_SIZE, cy * GRID_SIZE + GRID_SIZE,
                            fill=color, outline='')

        # Warning cell (Phase 1)
        if self.storm_active and self.storm_phase == 'warning' and self.storm_current_mine:
            mx, my = self.storm_current_mine
            w_color = EXPLOSION_COLORS[0] if self.storm_warning_flash_state else EXPLOSION_COLORS[2]
            self.canvas.create_rectangle(
                mx * GRID_SIZE, my * GRID_SIZE,
                mx * GRID_SIZE + GRID_SIZE, my * GRID_SIZE + GRID_SIZE,
                fill=w_color, outline='')
```

Then add bonus foods drawing **after** the mines block and **before** the snake drawing:

```python
        # Draw bonus foods (always GREEN)
        for bx, by in self.bonus_foods:
            x1 = bx * GRID_SIZE
            y1 = by * GRID_SIZE
            self.canvas.create_rectangle(x1, y1, x1 + GRID_SIZE, y1 + GRID_SIZE,
                                         fill='#00FF00', outline='#006400')
```

### Step 2.6 — Syntax validation

```powershell
py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
```

No output = success.

---

## Phase 3 — Console (`snake_game_console.py`)

### Step 3.1 — Add new constants

Add the following block immediately after line 24 (`MINE_COLOR = '\033[91m'`), before `# Directions`:

```python
# Mine Detonation Storm constants
STORM_TRIGGER_COUNT = 10
CONSOLE_WARNING_CHAR = '!'
CONSOLE_EXPLOSION_CHAR = '*'
CONSOLE_STORM_LABEL = '*** DETONATION STORM ***'
STORM_STORM_COLOR = '\033[91m'    # Bright red ANSI for storm label
CONSOLE_WARN_COLOR = '\033[93m'   # Bright yellow ANSI for warning/explosion chars
WARNING_TICKS = 3
EXPLOSION_TICKS = 1
```

### Step 3.2 — Add storm state to `main()`

In `main()`, locate:
```python
    mines = []
```

Replace that line with:

```python
    mines = []
    storm_active = False
    storm_queue = []
    storm_phase = None
    storm_current_mine = None
    storm_phase_ticks = 0
    bonus_foods = []
```

### Step 3.3 — Update `draw_game()` signature and rendering

The current signature is:
```python
def draw_game(snake, food, mines, score):
```

Replace it with:
```python
def draw_game(snake, food, mines, score, storm_active=False, storm_phase=None,
              storm_current_mine=None, bonus_foods=None):
    if bonus_foods is None:
        bonus_foods = []
```

Then inside `draw_game()`, locate the grid marking section. The current mine marking is:
```python
    # Mark mine positions
    for mx, my in mines:
        grid[my][mx] = MINE_CHAR
```

Replace that block with:

```python
    # Mark mine positions
    for mx, my in mines:
        grid[my][mx] = MINE_CHAR

    # Mark warning cell (Phase 1)
    if storm_active and storm_phase == 'warning' and storm_current_mine:
        wx, wy = storm_current_mine
        grid[wy][wx] = CONSOLE_WARNING_CHAR

    # Mark explosion cells (Phase 2)
    if storm_active and storm_phase == 'explosion' and storm_current_mine:
        ex, ey = storm_current_mine
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                cx, cy = ex + dx, ey + dy
                if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                    grid[cy][cx] = CONSOLE_EXPLOSION_CHAR

    # Mark bonus foods
    for bx, by in bonus_foods:
        grid[by][bx] = '●'
```

Then in the cell rendering section inside `draw_game()`, locate:
```python
            elif cell == MINE_CHAR:
                line += MINE_COLOR + cell + RESET_COLOR
            else:
                line += cell
```

Replace it with:

```python
            elif cell == MINE_CHAR:
                line += MINE_COLOR + cell + RESET_COLOR
            elif cell == CONSOLE_WARNING_CHAR:
                line += CONSOLE_WARN_COLOR + cell + RESET_COLOR
            elif cell == CONSOLE_EXPLOSION_CHAR:
                line += CONSOLE_WARN_COLOR + cell + RESET_COLOR
            else:
                line += cell
```

Then locate the `print("Use WASD to move, Q to quit")` line at the end of `draw_game()`. Add the storm label print **before** that line:

```python
    if storm_active:
        print(STORM_STORM_COLOR + CONSOLE_STORM_LABEL + RESET_COLOR)
    print("Use WASD to move, Q to quit")
```

### Step 3.4 — Update `main()` game loop

Locate the `while not game_over:` loop. The current body is:

```python
    while not game_over:
        draw_game(snake, food, mines, score)
        
        if snake.eat_food(food.position):
            score += 1
            food = Food(snake.body)
            spawn_mine(mines, snake.body, snake.direction, food.position, score)

        snake.move()

        # Mine collision check
        if snake.body[0] in mines:
            mines.remove(snake.body[0])
            shrink = min(3, len(snake.body))
            del snake.body[-shrink:]
            score = max(0, score - 3)
            if len(snake.body) == 0:
                game_over = True

        if snake.check_collision():
            game_over = True

        # Get user input
        user_input = input().lower()
        if user_input == 'w':
            snake.change_direction(UP)
        elif user_input == 's':
            snake.change_direction(DOWN)
        elif user_input == 'a':
            snake.change_direction(LEFT)
        elif user_input == 'd':
            snake.change_direction(RIGHT)
        elif user_input == 'q':
            game_over = True

        time.sleep(0.1)  # Add a small delay to control game speed
```

Replace it entirely with:

```python
    while not game_over:
        draw_game(snake, food, mines, score,
                  storm_active=storm_active, storm_phase=storm_phase,
                  storm_current_mine=storm_current_mine, bonus_foods=bonus_foods)

        if snake.eat_food(food.position):
            score += 1
            food = Food(snake.body)
            spawn_mine(mines, snake.body, snake.direction, food.position, score)
            # Storm trigger
            if not storm_active and len(mines) >= STORM_TRIGGER_COUNT:
                storm_active = True
                storm_queue = mines[:]
                random.shuffle(storm_queue)
                mines = []
                storm_current_mine = storm_queue.pop(0)
                storm_phase = 'warning'
                storm_phase_ticks = WARNING_TICKS
        elif snake.body[0] in bonus_foods:
            bonus_foods.remove(snake.body[0])
            snake.grow = True
            snake.color_index = (snake.color_index + 1) % len(SNAKE_COLORS)
            score += 1
            spawn_mine(mines, snake.body, snake.direction, food.position, score)

        snake.move()

        # Storm phase tick countdown
        if storm_active:
            storm_phase_ticks -= 1
            if storm_phase == 'warning' and storm_phase_ticks <= 0:
                storm_phase = 'explosion'
                storm_phase_ticks = EXPLOSION_TICKS
                bonus_foods.append(storm_current_mine)
            elif storm_phase == 'explosion':
                # Phase 2 kill check
                ex, ey = storm_current_mine
                head = snake.body[0]
                blast_cells = set()
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        cx, cy = ex + dx, ey + dy
                        if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                            blast_cells.add((cx, cy))
                if head in blast_cells:
                    game_over = True
                    storm_active = False
                    storm_queue = []
                    storm_phase = None
                    storm_current_mine = None
                    bonus_foods = []
                elif storm_phase_ticks <= 0:
                    if storm_queue:
                        storm_current_mine = storm_queue.pop(0)
                        storm_phase = 'warning'
                        storm_phase_ticks = WARNING_TICKS
                    else:
                        storm_active = False
                        storm_phase = None
                        storm_current_mine = None

        # Mine collision check
        if snake.body[0] in mines:
            mines.remove(snake.body[0])
            shrink = min(3, len(snake.body))
            del snake.body[-shrink:]
            score = max(0, score - 3)
            if len(snake.body) == 0:
                game_over = True

        if snake.check_collision():
            game_over = True

        # Get user input
        user_input = input().lower()
        if user_input == 'w':
            snake.change_direction(UP)
        elif user_input == 's':
            snake.change_direction(DOWN)
        elif user_input == 'a':
            snake.change_direction(LEFT)
        elif user_input == 'd':
            snake.change_direction(RIGHT)
        elif user_input == 'q':
            game_over = True

        time.sleep(0.1)
```

### Step 3.5 — Syntax validation

```powershell
py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
```

No output = success.

---

## Phase 4 — HTML/JS (`snake_game.html`)

All edits are inside the `<script>` block.

### Step 4.1 — Add new constants

Locate the mine constants block:
```javascript
        // Mine colors and timing
        const MINE_COLOR_A = '#FF0000';
        const MINE_COLOR_B = '#C8C8C8';
        const MINE_FLASH_INTERVAL = 200; // milliseconds
```

Add the following **immediately after** that block:

```javascript
        // Mine Detonation Storm constants
        const STORM_TRIGGER_COUNT = 10;
        const STORM_BORDER_COLOR_A = '#FF0000';
        const STORM_BORDER_COLOR_B = '#000000';
        const STORM_BORDER_FLASH_INTERVAL = 200; // ms
        const WARNING_DURATION_MS = 3000;
        const WARNING_FLASH_INTERVAL = 200; // ms
        const EXPLOSION_DURATION_MS = 1000;
        const EXPLOSION_COLORS = ['#FF0000', '#FF8800', '#FFFF00', '#FFFFFF', '#FF4400'];
```

### Step 4.2 — Add storm state variables

Locate the mine state block:
```javascript
        // Mine state
        let mines = [];
        let mineFlashState = false;
        let mineFlashTimer = null;
```

Add the following **immediately after** that block:

```javascript
        // Storm state
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

### Step 4.3 — Add storm functions

Add the following four functions **immediately before** the `init()` function:

```javascript
        function startStorm() {
            stormActive = true;
            stormQueue = mines.map(m => ({x: m.x, y: m.y}));
            stormQueue.sort(() => Math.random() - 0.5);
            mines = [];
            borderFlashState = false;
            if (borderFlashTimer) clearInterval(borderFlashTimer);
            borderFlashTimer = setInterval(() => {
                borderFlashState = !borderFlashState;
            }, STORM_BORDER_FLASH_INTERVAL);
            beginWarningPhase();
        }

        function beginWarningPhase() {
            if (stormQueue.length === 0) { endStorm(); return; }
            stormCurrentMine = stormQueue.shift();
            stormPhase = 'warning';
            stormWarningFlashState = false;
            if (stormWarningFlashTimer) clearInterval(stormWarningFlashTimer);
            stormWarningFlashTimer = setInterval(() => {
                stormWarningFlashState = !stormWarningFlashState;
            }, WARNING_FLASH_INTERVAL);
            if (stormPhaseTimer) clearTimeout(stormPhaseTimer);
            stormPhaseTimer = setTimeout(beginExplosionPhase, WARNING_DURATION_MS);
        }

        function beginExplosionPhase() {
            stormPhase = 'explosion';
            bonusFoods.push({x: stormCurrentMine.x, y: stormCurrentMine.y});
            if (stormWarningFlashTimer) clearInterval(stormWarningFlashTimer);
            stormWarningFlashTimer = null;
            if (stormPhaseTimer) clearTimeout(stormPhaseTimer);
            stormPhaseTimer = setTimeout(() => {
                if (stormQueue.length > 0) {
                    beginWarningPhase();
                } else {
                    endStorm();
                }
            }, EXPLOSION_DURATION_MS);
        }

        function endStorm() {
            stormActive = false;
            stormPhase = null;
            stormCurrentMine = null;
            stormQueue = [];
            borderFlashState = false;
            if (borderFlashTimer) clearInterval(borderFlashTimer);
            borderFlashTimer = null;
            if (stormWarningFlashTimer) clearInterval(stormWarningFlashTimer);
            stormWarningFlashTimer = null;
            if (stormPhaseTimer) clearTimeout(stormPhaseTimer);
            stormPhaseTimer = null;
        }
```

### Step 4.4 — Update `init()` to reset storm state

In `init()`, locate the mine reset block:
```javascript
            // Mine reset and flash timer
            mines = [];
            mineFlashState = false;
            if (mineFlashTimer) clearInterval(mineFlashTimer);
            mineFlashTimer = setInterval(() => { mineFlashState = !mineFlashState; }, MINE_FLASH_INTERVAL);
```

Add the following **immediately after** that block, still inside `init()`:

```javascript
            // Storm state reset
            stormActive = false;
            stormQueue = [];
            stormPhase = null;
            stormCurrentMine = null;
            bonusFoods = [];
            borderFlashState = false;
            if (borderFlashTimer) clearInterval(borderFlashTimer);
            borderFlashTimer = null;
            if (stormWarningFlashTimer) clearInterval(stormWarningFlashTimer);
            stormWarningFlashTimer = null;
            if (stormPhaseTimer) clearTimeout(stormPhaseTimer);
            stormPhaseTimer = null;
```

### Step 4.5 — Update `endGame()` to cancel storm timers

In `endGame()`, locate:
```javascript
            if (mineFlashTimer) clearInterval(mineFlashTimer);
```

Add the following **immediately after** that line:

```javascript
            if (borderFlashTimer) clearInterval(borderFlashTimer);
            borderFlashTimer = null;
            if (stormWarningFlashTimer) clearInterval(stormWarningFlashTimer);
            stormWarningFlashTimer = null;
            if (stormPhaseTimer) clearTimeout(stormPhaseTimer);
            stormPhaseTimer = null;
```

### Step 4.6 — Update `update()` — Phase 2 kill check, bonus food, storm trigger

In `update()`, locate the mine collision check block:
```javascript
            // Mine collision check
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

            snake.unshift(head);

            // Check food consumption
            if (head.x === food.x && head.y === food.y) {
                score++;
                colorIndex = (colorIndex + 1) % SNAKE_COLORS.length;
                document.getElementById('score').textContent = score;
                food = generateFood();
                trySpawnMine();
            } else {
                snake.pop();
            }
```

Replace it entirely with:

```javascript
            // Phase 2 explosion kill check (before unshift, consistent with wall/self checks)
            if (stormActive && stormPhase === 'explosion' && stormCurrentMine) {
                const mx = stormCurrentMine.x;
                const my = stormCurrentMine.y;
                let inBlast = false;
                for (let dy = -1; dy <= 1; dy++) {
                    for (let dx = -1; dx <= 1; dx++) {
                        if (head.x === mx + dx && head.y === my + dy) {
                            inBlast = true;
                        }
                    }
                }
                if (inBlast) {
                    endStorm();
                    endGame();
                    return;
                }
            }

            // Mine collision check (before unshift, consistent with ordering)
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

            snake.unshift(head);

            // Bonus food consumption
            const bonusHitIndex = bonusFoods.findIndex(b => b.x === head.x && b.y === head.y);
            if (bonusHitIndex !== -1) {
                bonusFoods.splice(bonusHitIndex, 1);
                score++;
                colorIndex = (colorIndex + 1) % SNAKE_COLORS.length;
                document.getElementById('score').textContent = score;
                trySpawnMine();
                // grow: do not pop tail this tick
            } else if (head.x === food.x && head.y === food.y) {
                // Check food consumption
                score++;
                colorIndex = (colorIndex + 1) % SNAKE_COLORS.length;
                document.getElementById('score').textContent = score;
                food = generateFood();
                trySpawnMine();
                // Storm trigger
                if (!stormActive && mines.length >= STORM_TRIGGER_COUNT) {
                    startStorm();
                }
            } else {
                snake.pop();
            }
```

### Step 4.7 — Update `draw()` — storm border, explosion cells, warning cell, bonus foods

In `draw()`, locate the mines drawing block:
```javascript
            // Draw mines (after grid, before snake)
            const mineColor = mineFlashState ? MINE_COLOR_A : MINE_COLOR_B;
            mines.forEach(m => {
                ctx.fillStyle = mineColor;
                ctx.fillRect(m.x * GRID_SIZE + 1, m.y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2);
            });
```

Add the following **immediately before** that mines block:

```javascript
            // Storm border
            if (stormActive && borderFlashState) {
                ctx.strokeStyle = STORM_BORDER_COLOR_A;
                ctx.lineWidth = 3;
                ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);
            }

            // Explosion cells (Phase 2)
            if (stormActive && stormPhase === 'explosion' && stormCurrentMine) {
                const mx = stormCurrentMine.x;
                const my = stormCurrentMine.y;
                for (let dy = -1; dy <= 1; dy++) {
                    for (let dx = -1; dx <= 1; dx++) {
                        const cx = mx + dx;
                        const cy = my + dy;
                        if (cx >= 0 && cx < GRID_WIDTH && cy >= 0 && cy < GRID_HEIGHT) {
                            ctx.fillStyle = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLOSION_COLORS.length)];
                            ctx.fillRect(cx * GRID_SIZE, cy * GRID_SIZE, GRID_SIZE, GRID_SIZE);
                        }
                    }
                }
            }

            // Warning cell (Phase 1)
            if (stormActive && stormPhase === 'warning' && stormCurrentMine) {
                const wColor = stormWarningFlashState ? EXPLOSION_COLORS[0] : EXPLOSION_COLORS[2];
                ctx.fillStyle = wColor;
                ctx.fillRect(
                    stormCurrentMine.x * GRID_SIZE, stormCurrentMine.y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE);
            }
```

Then add bonus foods drawing **after** the mines block and **before** the snake drawing:

```javascript
            // Draw bonus foods (always GREEN)
            bonusFoods.forEach(b => {
                const bx = b.x * GRID_SIZE + GRID_SIZE / 2;
                const by = b.y * GRID_SIZE + GRID_SIZE / 2;
                const br = GRID_SIZE / 2 - 2;
                ctx.fillStyle = GREEN;
                ctx.beginPath();
                ctx.arc(bx, by, br, 0, 2 * Math.PI);
                ctx.fill();
            });
```

### Step 4.8 — Verify HTML opens without JS console errors

Open `snake_game.html` in a browser. Open the browser developer console (F12). Verify no errors appear on load or during gameplay.

---

## Phase 5 — Documentation Updates

Update all 7 files in `docs/`. Each file receives a new section appended or a new block inserted in the appropriate location.

### Step 5.1 — `docs/architecture.md`

Add the following subsection at the end of the **Key Components and Relationships** section (after the Mine Component subsection):

```markdown
#### Mine Detonation Storm Component
**Purpose:** Event system triggered when 10 mines are simultaneously active. Manages sequential mine detonation with warning phase, explosion phase, bonus food spawning, snake kill zone, and storm border flash.

**State (Python versions):**
- `storm_active` — `bool`; True while storm is running
- `storm_queue` — `list` of `(x,y)` tuples; remaining mines to detonate
- `storm_phase` — `str|None`; `'warning'` or `'explosion'`
- `storm_current_mine` — `tuple|None`; position of mine in active phase
- `storm_phase_elapsed` — `float`; seconds elapsed in current phase (Pygame) or phase tick countdown (Console)
- `storm_warning_flash_state` — `bool`; warning cell colour toggle
- `border_flash_state` — `bool`; border colour toggle
- `bonus_foods` — `list` of `(x,y)` tuples; bonus food positions

**State (JavaScript version):**
- `stormActive`, `stormQueue`, `stormPhase`, `stormCurrentMine`
- `stormPhaseTimer` (setTimeout ID), `stormWarningFlashTimer` (setInterval ID)
- `borderFlashTimer` (setInterval ID), `borderFlashState`, `bonusFoods`

**Trigger:** Mine count reaches `STORM_TRIGGER_COUNT` (10) on a food-eat event.

**Phases per mine:** Phase 1 WARNING (3s/3 ticks) → Phase 2 EXPLOSION (1s/1 tick).

**Kill condition:** Snake head in any Phase 2 3×3 blast cell → immediate game over.
```

Add the following to the Component Interaction Diagram, inside the game-loop flow after the mine collision branch:

```
    ├─→ Storm Phase Tick → [warning elapsed] → transition to explosion, spawn bonus food
    │                   → [explosion elapsed] → next mine warning OR end storm
    │
    ├─→ Phase 2 Kill Check → [head in blast cells] → game_over = True, end_storm()
    │
    ├─→ Bonus Food Check → [head on bonus food] → score+1, grow, cycle colour
```

Add to the Constants section:
```
- `STORM_TRIGGER_COUNT = 10`
- `STORM_BORDER_COLOR_A` — Bright red: `(255,0,0)` / `'#FF0000'`
- `STORM_BORDER_COLOR_B` — Black: `(0,0,0)` / `'#000000'`
- `STORM_BORDER_FLASH_INTERVAL` — `0.2s` / `200ms`
- `WARNING_DURATION` — `3.0s` / `3000ms`
- `EXPLOSION_DURATION` — `1.0s` / `1000ms`
- `EXPLOSION_COLORS` — 5-colour palette: red, orange, yellow, white, orange-red
```

### Step 5.2 — `docs/code.md`

Append the following section at the end of the file:

````markdown
---

## Mine Detonation Storm — Code Patterns

### Storm Constants (all versions)
```python
STORM_TRIGGER_COUNT = 10
STORM_BORDER_COLOR_A = (255, 0, 0)        # '#FF0000' in JS/Tkinter
STORM_BORDER_COLOR_B = (0, 0, 0)          # '#000000' in JS/Tkinter
STORM_BORDER_FLASH_INTERVAL = 0.2         # seconds (Pygame) | 200ms (Tkinter, HTML)
WARNING_DURATION = 3.0                     # seconds | 3000ms | 3 ticks (console)
EXPLOSION_DURATION = 1.0                   # seconds | 1000ms | 1 tick (console)
EXPLOSION_COLORS = [(255,0,0),(255,136,0),(255,255,0),(255,255,255),(255,68,0)]
```

### Storm Trigger Pattern
```python
# Evaluated after spawn_mine() call in food-eat handler:
if not storm_active and len(mines) >= STORM_TRIGGER_COUNT:
    start_storm()
```

### Storm State Variables (Python)
| Variable | Type | Purpose |
|----------|------|---------|
| `storm_active` | `bool` | True while storm is running |
| `storm_queue` | `list[tuple]` | Remaining mines to detonate |
| `storm_phase` | `str\|None` | `'warning'` or `'explosion'` |
| `storm_current_mine` | `tuple\|None` | Mine position in active phase |
| `storm_phase_elapsed` | `float` | Seconds in current phase (Pygame) |
| `border_flash_state` | `bool` | Border colour toggle |
| `bonus_foods` | `list[tuple]` | Bonus food positions |

### Phase Transition Logic (Pygame accumulator pattern)
```python
if storm_phase == 'warning' and storm_phase_elapsed >= WARNING_DURATION:
    storm_phase = 'explosion'
    storm_phase_elapsed = 0.0
    bonus_foods.append(storm_current_mine)
elif storm_phase == 'explosion' and storm_phase_elapsed >= EXPLOSION_DURATION:
    if storm_queue:
        storm_current_mine = storm_queue.pop(0)
        storm_phase = 'warning'
        storm_phase_elapsed = 0.0
    else:
        # end_storm()
        storm_active = False
        storm_phase = None
```

### Explosion Blast Cells Pattern
```python
mx, my = storm_current_mine
blast_cells = set()
for dy in range(-1, 2):
    for dx in range(-1, 2):
        cx, cy = mx + dx, my + dy
        if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
            blast_cells.add((cx, cy))
if snake.next_head in blast_cells:
    game_over = True
    end_storm()
```

### Explosion Rendering Pattern (Pygame)
```python
def draw_explosion_cells(screen, mine_pos):
    mx, my = mine_pos
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            cx, cy = mx + dx, my + dy
            if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                color = random.choice(EXPLOSION_COLORS)
                pygame.draw.rect(screen, color,
                                 (cx * GRID_SIZE, cy * GRID_SIZE, GRID_SIZE, GRID_SIZE))
```

### Timing Mechanisms (per platform)
| Version | Border Flash | Warning Flash | Phase Transition |
|---------|-------------|---------------|-----------------|
| Pygame | Accumulator | Accumulator | Accumulator |
| Tkinter | `root.after()` recursive | `root.after()` recursive | `root.after()` one-shot |
| HTML/JS | `setInterval()` | `setInterval()` | `setTimeout()` |
| Console | Not applicable | Not applicable | Tick countdown |

### Bonus Food Pattern
Bonus food items are stored in `bonus_foods` (list of `(x,y)` tuples). They are:
- Spawned at `storm_current_mine` position at Phase 2 start
- Rendered using `GREEN` colour only
- Consumed by standard head-collision check each tick
- On consume: `score += 1`, snake grows, `color_index` cycles
````

### Step 5.3 — `docs/dataflow.md`

Append the following section at the end of the file:

```markdown
---

## Mine Detonation Storm — Data Flows

### Storm Trigger Flow
```
food-eat event
  → spawn_mine() adds mine to mines list
  → len(mines) >= STORM_TRIGGER_COUNT and not storm_active
  → start_storm():
      storm_queue ← copy of mines, shuffled
      mines ← []
      storm_current_mine ← storm_queue.pop(0)
      storm_phase ← 'warning'
      start border flash timer
      start warning flash timer
```

### Phase Transition Flow
```
storm_phase == 'warning', elapsed >= 3s (or 3 ticks):
  → storm_phase ← 'explosion'
  → bonus_foods.append(storm_current_mine)
  → stop warning flash timer
  → start 1s explosion timer

storm_phase == 'explosion', elapsed >= 1s (or 1 tick):
  → if storm_queue not empty:
      storm_current_mine ← storm_queue.pop(0)
      storm_phase ← 'warning'
      restart warning flash timer
  → else:
      end_storm()
```

### Phase 2 Kill Flow
```
every game tick while storm_phase == 'explosion':
  compute blast_cells = 3x3 around storm_current_mine (clipped to grid)
  if snake.head in blast_cells:
    game_over = True
    end_storm()
```

### Bonus Food Spawn/Consume Flow
```
Phase 2 start:
  bonus_foods.append(storm_current_mine)

each game tick:
  if snake.head in bonus_foods:
    bonus_foods.remove(position)
    score += 1
    snake grows
    color_index cycles
    spawn_mine() called
```

### Storm End Flow
```
end_storm():
  storm_active ← False
  storm_phase ← None
  storm_current_mine ← None
  storm_queue ← []
  border_flash_state ← False
  cancel all storm timers (border, warning, phase)
```
```

### Step 5.4 — `docs/decisions.md`

Append the following ADRs at the end of the **Flashing Mines Feature — Implementation Decisions** section:

```markdown
---

## Mine Detonation Storm Feature — Architectural Decisions

### ADR-MDS-001: Storm Trigger Evaluated After spawn_mine() in Food-Eat Handler

**Status:** Implemented

**Decision:** The storm trigger check (`len(mines) >= STORM_TRIGGER_COUNT`) is evaluated immediately after `spawn_mine()` in the food-eat handler, not at any other point in the game loop.

**Rationale:** AC-1b specifies the trigger is evaluated "on each food-eat event that causes mine count to reach 10." Placing it after `spawn_mine()` ensures it fires at the correct moment.

---

### ADR-MDS-002: Phase Timing Mechanism Per Platform

**Status:** Implemented

**Decision:** Phase timing uses the same platform-native mechanism as the existing mine flash:
- Pygame: accumulator pattern with `clock.get_time()`
- Tkinter: one-shot `root.after()` for phase transitions; recursive `root.after()` for flash toggles
- HTML/JS: `setTimeout()` for phase transitions; `setInterval()` for flash toggles
- Console: integer tick countdown

**Rationale:** Consistent with ADR-FM-001. Each platform has one idiomatic timer approach.

---

### ADR-MDS-003: Console Tick Approximation

**Status:** Implemented

**Decision:** Console Phase 1 = 3 ticks, Phase 2 = 1 tick as approximation of 3s and 1s.

**Rationale:** The console game loop is blocking (`input()`-driven) with no real-time clock. Tick-based counting is the only feasible approach. AC-10 explicitly specifies this.

---

### ADR-MDS-004: Phase 2 Kill Check — Head Only

**Status:** Implemented

**Decision:** Only the snake head triggers game over when in a Phase 2 blast cell. Body segments are ignored.

**Rationale:** AC-5c explicitly states "Head only — body segments do NOT cause death."

---

### ADR-MDS-005: Bonus Food Placed Unconditionally at Mine Centre Cell

**Status:** Implemented

**Decision:** Bonus food is appended to `bonus_foods` at `storm_current_mine` position unconditionally at Phase 2 start, without checking if the cell is occupied by the snake body, another bonus food, or standard food.

**Rationale:** AC-6f: "Bonus food placed at centre cell even if occupied by snake body."
```

### Step 5.5 — `docs/glossary.md`

Append the following entries at the end of the file:

```markdown
---

## Mine Detonation Storm — Glossary

**Mine Detonation Storm:** An event triggered when 10 or more mines are simultaneously active. All mines are detonated sequentially with warning and explosion phases.

**Detonation Queue (`storm_queue`):** A shuffled list of mine positions created at storm start. Mines are popped from the queue one by one to enter the detonation sequence.

**Phase 1 / Warning Phase:** The 3-second (3-tick in console) pre-explosion phase for each mine. The mine cell flashes using EXPLOSION_COLORS. No blast area active. Snake cannot be killed by explosion during this phase.

**Phase 2 / Explosion Phase:** The 1-second (1-tick in console) explosion phase. A 3×3 blast zone is active. Snake head in blast zone → immediate game over. Bonus food spawns at mine centre at Phase 2 start.

**Blast Zone:** The 3×3 grid area centred on the detonating mine, clipped to grid boundaries. Active during Phase 2 only.

**Bonus Food:** A GREEN food item spawned at the mine's centre cell at Phase 2 start. Consumed by standard mechanics (score+1, grow, colour cycle). Persists after storm ends.

**Storm Border:** A flashing red/black border drawn around the inner edge of the game window during a Mine Detonation Storm. Console equivalent: `*** DETONATION STORM ***` label in bright red ANSI.

**EXPLOSION_COLORS:** The 5-colour palette used for warning flash and explosion rendering: bright red `(255,0,0)`, orange `(255,136,0)`, yellow `(255,255,0)`, white `(255,255,255)`, bright orange-red `(255,68,0)`.
```

### Step 5.6 — `docs/risk.md`

Append the following entries at the end of the file:

```markdown
---

## Mine Detonation Storm — Risks

### RISK-MDS-001: Tkinter Timer Accumulation on Long Storm

**Risk:** With 10+ mines, a storm can last 40+ seconds. If the player restarts mid-storm without cancelling timers, multiple `_toggle_border_flash`, `_toggle_warning_flash`, and `_advance_storm_phase` callbacks may fire on stale state.

**Mitigation:** `reset_game()` cancels all three timer IDs using `hasattr` guards before clearing state. `_toggle_border_flash()` and `_toggle_warning_flash()` check `storm_active` / `storm_phase` before rescheduling.

**Severity:** Medium | **Probability:** Low (only on rapid restart)

---

### RISK-MDS-002: HTML Timer Orphan on Tab Switch or Rapid Restart

**Risk:** If the browser tab is hidden during a storm and `setTimeout`/`setInterval` callbacks fire after `init()` resets state, orphaned callbacks may corrupt `stormPhase` or `bonusFoods`.

**Mitigation:** `init()` cancels all storm timer IDs before resetting state. `endGame()` also cancels all storm timers. Phase transition functions (`beginWarningPhase`, `beginExplosionPhase`) always cancel their predecessor timer before setting a new one.

**Severity:** Low | **Probability:** Low

---

### RISK-MDS-003: Console Tick Approximation Inaccuracy

**Risk:** The console Phase 1 duration is approximated as 3 ticks (~0.3s at 10 FPS), not 3 real seconds. Players may find the warning phase very short.

**Mitigation:** AC-10 explicitly specifies tick-based timing for the console version. This is accepted behaviour.

**Severity:** Low | **Probability:** Certain (by design)

---

### RISK-MDS-004: Bonus Food List Growth During Long Storm

**Risk:** If the player avoids eating bonus foods throughout a 10-mine storm, the `bonus_foods` list will contain up to 10 items simultaneously. This is expected but creates a temporarily cluttered grid.

**Mitigation:** Bonus foods are removed on consumption. They persist after the storm ends and are consumed by normal mechanics. This is accepted per AC-6b and AC-6e.

**Severity:** Low | **Probability:** Low
```

### Step 5.7 — `docs/structure.md`

In `docs/structure.md`, locate the `flashing-mines/` entry in the Complete Directory Tree:

```
├── flashing-mines/                    # Feature folder: Flashing Mines
│   ├── flashing-mines-plan.md         # Implementation plan (P41)
│   ├── Build.md                       # Build guide (P42)
│   ├── ToDo.md                        # Task checklist — all 62 tasks marked complete
│   └── post-implementation-lessons-learned.md  # Lessons learned; feature completed 2026-03-05
```

Add the following **immediately after** that block:

```
├── mine-detonation-storm/             # Feature folder: Mine Detonation Storm
│   ├── Plan.md                        # Implementation plan (P41)
│   ├── Build.md                       # Build guide (P42) — this file
│   ├── ToDo.md                        # Task checklist (P43)
│   └── post-implementation-lessons-learned.md  # Lessons learned (P44)
```

---

## Phase 6 — Verification

### Step 6.1 — Syntax validation (all Python files)

```powershell
py -c "import ast; ast.parse(open('snake_game.py', encoding='utf-8').read())"
py -c "import ast; ast.parse(open('snake_game_tkinter.py', encoding='utf-8').read())"
py -c "import ast; ast.parse(open('snake_game_console.py', encoding='utf-8').read())"
```

All three commands must produce no output.

### Step 6.2 — Launch verification (all versions)

```powershell
py snake_game.py
```
```powershell
py snake_game_tkinter.py
```
```powershell
py snake_game_console.py
```

Open `snake_game.html` in a browser. Verify no JavaScript console errors (F12).

### Step 6.3 — Manual test procedure (all versions)

Test each version against all success criteria. Perform the following steps in each version:

**SC-1 / AC-1:** Play until score 45+ (10 mines appear). Confirm storm triggers.  
**SC-2 / AC-1c:** Confirm no nested storm while one is active.  
**SC-3 / AC-2a–b:** Confirm red/black border flashes during storm (Pygame, Tkinter, HTML).  
**SC-4 / AC-2f:** Confirm `*** DETONATION STORM ***` in bright red appears (Console).  
**SC-5 / AC-3a:** Confirm mines detonate in shuffled (random) order.  
**SC-6 / AC-3b Phase 1:** Confirm 3-second (3-tick) warning flash using explosion colours.  
**SC-7 / AC-3b Phase 2:** Confirm 1-second (1-tick) 3×3 flickering explosion area.  
**SC-8 / AC-3f:** Confirm only the current warning mine uses explosion-palette; others flash red/grey.  
**SC-9 / AC-5a:** Move snake head into active Phase 2 blast zone — confirm immediate game over.  
**SC-10 / AC-5b:** Move snake into Phase 1 warning cell — confirm no explosion kill.  
**SC-11 / AC-6a–c:** Confirm one GREEN bonus food appears at mine centre at Phase 2 start.  
**SC-12 / AC-6d:** Eat a bonus food — confirm score+1 and snake growth.  
**SC-13 / AC-6e:** Let storm end, confirm bonus foods remain; eat them.  
**SC-14 / AC-7a:** Let all mines detonate — confirm storm ends, border flash stops.  
**SC-15 / AC-7b:** Die in Phase 2 blast — confirm storm ends immediately.  
**SC-16 / AC-8a–b:** Eat food during storm — confirm new mine spawns into `mines`, not `storm_queue`.  
**SC-17 / AC-8c:** Confirm no nested storm during active storm.  
**SC-18 / AC-9:** Press SPACE mid-storm — confirm clean restart, no timers firing, no bonus foods remaining.  
**SC-19–20:** All 4 versions pass syntax check and launch without errors.  
**SC-21:** Confirm food always GREEN, snake colour progression unchanged.  
**SC-22:** Confirm all 7 `/docs` files updated.

---

*Build.md — Mine Detonation Storm (MDS-001) — Generated 2026-03-06*
