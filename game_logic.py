import random

# Grid constants
GRID_SIZE = 20
WINDOW_WIDTH = 600
SCORE_BAR_HEIGHT = 30
GRID_PIXEL_HEIGHT = 600
WINDOW_HEIGHT = 630
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = GRID_PIXEL_HEIGHT // GRID_SIZE

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Snake color palette
SNAKE_COLORS = [
    (0, 100, 255),
    (0, 255, 255),
    (50, 255, 50),
    (255, 255, 0),
    (255, 165, 0),
    (255, 50, 50),
    (255, 0, 255),
    (255, 105, 180),
]


def check_wall_collision(head, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT):
    """Returns True if head position is outside grid bounds."""
    head_x, head_y = head
    if head_x < 0 or head_x >= grid_width or head_y < 0 or head_y >= grid_height:
        return True
    return False


def check_self_collision(head, body):
    """Returns True if head is present in body[1:] (self-collision)."""
    if head in body[1:]:
        return True
    return False


def get_next_head(head, direction):
    """Returns the next head position tuple given current head and direction."""
    head_x, head_y = head
    dir_x, dir_y = direction
    return (head_x + dir_x, head_y + dir_y)


def calculate_new_score(current_score):
    """Returns current_score + 1."""
    return current_score + 1


def is_valid_food_position(pos, snake_body):
    """Returns True if pos is not occupied by the snake body."""
    return pos not in snake_body


def is_valid_mine_position(candidate, snake_body, snake_direction, food_pos, mines):
    """
    Returns True if candidate passes all mine placement checks:
    - Not in snake_body
    - Not within Manhattan distance 10 of any snake segment
    - Not on the snake's projected forward path
    - Not equal to food_pos
    - Not already in mines
    """
    cx, cy = candidate
    if candidate in snake_body:
        return False
    if any(abs(cx - sx) + abs(cy - sy) <= 10 for sx, sy in snake_body):
        return False
    hx, hy = snake_body[0]
    dx, dy = snake_direction
    path = set()
    px, py = hx + dx, hy + dy
    while 0 <= px < GRID_WIDTH and 0 <= py < GRID_HEIGHT:
        path.add((px, py))
        px += dx
        py += dy
    if candidate in path:
        return False
    if candidate == food_pos:
        return False
    if candidate in mines:
        return False
    return True


def spawn_mine(mines, snake_body, snake_direction, food_pos, score):
    """
    Adds mines to the mines list up to the expected count (1 + score // 5).
    Mutates the mines list in place.
    Makes up to 1000 attempts per mine; silently skips if exhausted.
    """
    expected_count = 1 + score // 5
    mines_to_add = expected_count - len(mines)
    if mines_to_add <= 0:
        return
    for _ in range(mines_to_add):
        for attempts in range(1000):
            cx = random.randint(0, GRID_WIDTH - 1)
            cy = random.randint(0, GRID_HEIGHT - 1)
            candidate = (cx, cy)
            if is_valid_mine_position(candidate, snake_body, snake_direction, food_pos, mines):
                mines.append(candidate)
                break
