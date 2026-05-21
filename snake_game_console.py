import random
import os
import time

# Constants
GRID_WIDTH = 20
GRID_HEIGHT = 20

# ANSI color codes for console (bright colors visible on dark backgrounds)
SNAKE_COLORS = [
    '\033[94m',   # Bright Blue
    '\033[96m',   # Bright Cyan
    '\033[92m',   # Bright Green
    '\033[93m',   # Bright Yellow
    '\033[38;5;208m',  # Orange
    '\033[91m',   # Bright Red
    '\033[95m',   # Bright Magenta
    '\033[38;5;213m',  # Pink
]
RESET_COLOR = '\033[0m'

# Mine display (no flash — console limitation; static character)
MINE_CHAR = 'M'
MINE_COLOR = '\033[91m'   # Bright red ANSI

# Mine Detonation Storm constants
STORM_TRIGGER_COUNT = 10
CONSOLE_WARNING_CHAR = '!'
CONSOLE_EXPLOSION_CHAR = '*'
CONSOLE_STORM_LABEL = '*** DETONATION STORM ***'
STORM_STORM_COLOR = '\033[91m'
CONSOLE_WARN_COLOR = '\033[93m'
WARNING_TICKS = 3
EXPLOSION_TICKS = 1

# Invincibility Power-Up constants
INVINCIBILITY_TICKS        = 100
INVINCIBILITY_COLOR_CODE   = '\033[93m'
CONSOLE_SUPER_FOOD_CHAR    = '$'
CONSOLE_INVINCIBLE_LABEL   = '*** INVINCIBLE ***'

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.color_index = 0  # Track current color

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        
        self.body.insert(0, new_head)
        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def check_collision(self):
        return self.body[0] in self.body[1:]

    def eat_food(self, food_pos):
        if self.body[0] == food_pos:
            self.grow = True
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            return True
        return False

class Food:
    def __init__(self, snake_body):
        self.position = self.generate_position(snake_body)

    def generate_position(self, snake_body):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_body:
                return pos

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
        # silently skip if 1000 attempts exhausted

def draw_game(snake, food, mines, score, storm_active=False, storm_phase=None,
              storm_current_mine=None, bonus_foods=None,
              super_food_position=None, invincibility_active=False,
              invincibility_ticks_remaining=0, paused=False):
    if bonus_foods is None:
        bonus_foods = []
    os.system('cls' if os.name == 'nt' else 'clear')
    grid = [[' ' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    # Mark snake positions
    for segment in snake.body:
        grid[segment[1]][segment[0]] = '█'

    # Mark food position
    grid[food.position[1]][food.position[0]] = '●'

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

    # Mark Super-Food position
    if super_food_position is not None:
        sfx, sfy = super_food_position
        grid[sfy][sfx] = CONSOLE_SUPER_FOOD_CHAR

    # Get current snake color
    current_color = SNAKE_COLORS[snake.color_index]

    print('┌' + '─' * GRID_WIDTH + '┐')
    for y, row in enumerate(grid):
        line = '│'
        for x, cell in enumerate(row):
            if cell == '█':
                seg_color = INVINCIBILITY_COLOR_CODE if invincibility_active else current_color
                line += seg_color + cell + RESET_COLOR
            elif cell == '●':
                line += '\033[97m' + cell + RESET_COLOR
            elif cell == MINE_CHAR:
                line += MINE_COLOR + cell + RESET_COLOR
            elif cell == CONSOLE_WARNING_CHAR:
                line += CONSOLE_WARN_COLOR + cell + RESET_COLOR
            elif cell == CONSOLE_EXPLOSION_CHAR:
                line += CONSOLE_WARN_COLOR + cell + RESET_COLOR
            elif cell == CONSOLE_SUPER_FOOD_CHAR:
                line += INVINCIBILITY_COLOR_CODE + cell + RESET_COLOR
            else:
                line += cell
        line += '│'
        print(line)
    print('└' + '─' * GRID_WIDTH + '┘')
    print()
    if invincibility_active:
        secs = invincibility_ticks_remaining // 10
        inv_hud = f"      INV: {secs}  {INVINCIBILITY_COLOR_CODE}{CONSOLE_INVINCIBLE_LABEL}{RESET_COLOR}"
    else:
        inv_hud = ""
    print(f"Score: {score}{inv_hud}")
    if storm_active:
        print(STORM_STORM_COLOR + CONSOLE_STORM_LABEL + RESET_COLOR)
    if paused:
        print()
        print("*** PAUSED ***")
        print("Press P to Resume")
        print()
    print("Use WASD to move, Q to quit")

def show_rules_screen():
    print('┌' + '─' * 38 + '┐')
    print('│' + ' ' * 38 + '│')
    print('│' + '         Test1 Rules              '.center(38) + '│')
    print('│' + ' ' * 38 + '│')
    print('│' + ' Use arrow keys to control snake. '.center(38) + '│')
    print('│' + ' Eat green apples to grow & score.'.center(38) + '│')
    print('│' + ' Avoid walls and your own body.   '.center(38) + '│')
    print('│' + ' Game gets harder as you grow.    '.center(38) + '│')
    print('│' + ' ' * 38 + '│')
    print('│' + ' Press Enter to continue...       '.center(38) + '│')
    print('│' + ' ' * 38 + '│')
    print('└' + '─' * 38 + '┘')
    input()


def main():
    show_rules_screen()
    snake = Snake()
    food = Food(snake.body)
    score = 0
    game_over = False
    mines = []
    storm_active = False
    storm_queue = []
    storm_phase = None
    storm_current_mine = None
    storm_phase_ticks = 0
    bonus_foods = []
    super_food_position = None
    super_food_mine_index = None
    super_food_mine_counter = 0
    invincibility_active = False
    invincibility_ticks_remaining = 0
    paused = False

    while not game_over:
        draw_game(snake, food, mines, score,
                  storm_active=storm_active, storm_phase=storm_phase,
                  storm_current_mine=storm_current_mine, bonus_foods=bonus_foods,
                  super_food_position=super_food_position,
                  invincibility_active=invincibility_active,
                  invincibility_ticks_remaining=invincibility_ticks_remaining, paused=paused)

        if not paused:
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
                    super_food_mine_index = random.randint(0, len(storm_queue) - 1)
                    super_food_mine_counter = 0
                    if super_food_position is not None:
                        super_food_position = None
                    storm_current_mine = storm_queue.pop(0)
                    storm_phase = 'warning'
                    storm_phase_ticks = WARNING_TICKS
            elif snake.body[0] in bonus_foods:
                bonus_foods.remove(snake.body[0])
                snake.grow = True
                snake.color_index = (snake.color_index + 1) % len(SNAKE_COLORS)
                score += 1
                spawn_mine(mines, snake.body, snake.direction, food.position, score)

                # Super-Food collision
                if super_food_position is not None and snake.body[0] == super_food_position:
                    super_food_position = None
                    if not invincibility_active:
                        invincibility_active = True
                        invincibility_ticks_remaining = INVINCIBILITY_TICKS
    
                snake.move()
    
            # Storm phase tick countdown
            if not paused and storm_active:
            storm_phase_ticks -= 1
            if storm_phase == 'warning' and storm_phase_ticks <= 0:
                storm_phase = 'explosion'
                storm_phase_ticks = EXPLOSION_TICKS
                if super_food_mine_index is not None and super_food_mine_counter == super_food_mine_index:
                    super_food_position = storm_current_mine
                super_food_mine_counter += 1
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
                for segment in snake.body:
                    if segment in blast_cells:
                        if not invincibility_active:
                            game_over = True
                            storm_active = False
                            storm_queue = []
                            storm_phase = None
                            storm_current_mine = None
                            bonus_foods = []
                            break
                if storm_phase_ticks <= 0:
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
            if not invincibility_active:
                mines.remove(snake.body[0])
                shrink = min(3, len(snake.body))
                del snake.body[-shrink:]
                score = max(0, score - 3)
                if len(snake.body) == 0:
                    game_over = True

        if snake.check_collision():
            if not invincibility_active:
                game_over = True

        # Invincibility tick countdown
        if not paused and invincibility_active:
            invincibility_ticks_remaining -= 1
            if invincibility_ticks_remaining <= 0:
                invincibility_active = False
                invincibility_ticks_remaining = 0

        # Get user input
        user_input = input().lower()
        if user_input == 'p':
            paused = not paused
            continue
        elif user_input == 'w':
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

    print(f"Game Over! Final Score: {score}")

if __name__ == '__main__':
    main()