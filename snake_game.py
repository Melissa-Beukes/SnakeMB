import pygame
import random
import sys
import math
from game_logic import (
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    GRID_PIXEL_HEIGHT, SCORE_BAR_HEIGHT,
    UP, DOWN, LEFT, RIGHT,
    SNAKE_COLORS,
    check_wall_collision, check_self_collision, get_next_head,
    calculate_new_score, is_valid_food_position, is_valid_mine_position,
    spawn_mine,
)

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FOOD_COLOR = (255, 255, 255)   # Food color (white)
DARK_BLUE = (80, 0, 120)  # For gradient background (purple)
LIGHT_BLUE_SHINE = (180, 230, 255)  # For food shine effect (lighter blue)
LIGHT_YELLOW = (255, 255, 200)  # For super food shine effect (unused by regular food)
GREEN = (0, 255, 0)     # Bonus foods only

# Mine colors and timing
MINE_COLOR_A = (255, 0, 0)        # Bright red
MINE_COLOR_B = (200, 200, 200)    # Light grey
MINE_FLASH_INTERVAL = 0.2         # Seconds

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

# Invincibility Power-Up constants
SUPER_FOOD_COLOR_B        = (0, 0, 0)
SUPER_FOOD_FLASH_INTERVAL = 0.25
INVINCIBILITY_DURATION    = 10.0
INVINCIBILITY_COLOR       = (255, 255, 0)
INVINCIBILITY_MUSIC_PATH  = r"C:\Users\GrahamSaunders\Downloads\snake_game_v1.1.0\music\chiptune_triumphant.wav"
HUD_INVINCIBILITY_OFFSET  = 5 * GRID_SIZE

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.animation_frames = 5
        self.current_frame = 0
        self.prev_head = self.body[0]
        self.next_head = self.body[0]
        self.color_index = 0  # Track current color
    
    def move(self):
        if self.current_frame == 0:
            head_x, head_y = self.body[0]
            dir_x, dir_y = self.direction
            self.next_head = (head_x + dir_x, head_y + dir_y)
            self.prev_head = self.body[0]
        
        self.current_frame += 1
        
        if self.current_frame >= self.animation_frames:
            self.body.insert(0, self.next_head)
            
            if not self.grow:
                self.body.pop()
            else:
                self.grow = False
            
            self.current_frame = 0
    
    def change_direction(self, new_direction):
        # Prevent reversing direction
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def check_collision(self):
        head_x, head_y = self.next_head
        
        # Check wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        
        # Check self collision
        if self.next_head in self.body[1:]:
            return True
        
        return False
    
    def eat_food(self, food_pos):
        if self.next_head == food_pos:
            self.grow = True
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            return True
        return False

    def get_interpolated_body(self):
        if self.current_frame == 0:
            return self.body
        
        t = self.current_frame / self.animation_frames
        interpolated_head = (
            self.prev_head[0] + (self.next_head[0] - self.prev_head[0]) * t,
            self.prev_head[1] + (self.next_head[1] - self.prev_head[1]) * t
        )
        return [interpolated_head] + self.body[:-1]

class Food:
    def __init__(self, snake_body):
        self.position = self.generate_position(snake_body)
    
    def generate_position(self, snake_body):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_body:
                return pos

def draw_grid(screen):
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, GRID_PIXEL_HEIGHT))
    for y in range(0, GRID_PIXEL_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WINDOW_WIDTH, y))

def draw_snake(screen, snake, invincibility_active=False):
    current_color = INVINCIBILITY_COLOR if invincibility_active else SNAKE_COLORS[snake.color_index]
    interpolated_body = snake.get_interpolated_body()
    for i, segment in enumerate(interpolated_body):
        x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
        
        # Draw rounded rectangle for each segment
        pygame.draw.rect(screen, current_color, (x, y, GRID_SIZE, GRID_SIZE), border_radius=GRID_SIZE // 4)
        
        # Draw eyes on the head
        if i == 0:
            eye_radius = GRID_SIZE // 8
            left_eye = (x + GRID_SIZE // 4, y + GRID_SIZE // 4)
            right_eye = (x + 3 * GRID_SIZE // 4, y + GRID_SIZE // 4)
            pygame.draw.circle(screen, WHITE, left_eye, eye_radius)
            pygame.draw.circle(screen, WHITE, right_eye, eye_radius)
            pygame.draw.circle(screen, BLACK, left_eye, eye_radius // 2)
            pygame.draw.circle(screen, BLACK, right_eye, eye_radius // 2)

def draw_food(screen, food):
    # Food is WHITE (255, 255, 255)
    x, y = food.position[0] * GRID_SIZE, food.position[1] * GRID_SIZE
    center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
    radius = GRID_SIZE // 2

    # Draw the main circular food (solid white, no shine overlay)
    pygame.draw.circle(screen, FOOD_COLOR, center, radius)

    # Add pulsating outline effect (thin white ring)
    pulse = math.sin(pygame.time.get_ticks() * 0.01) * 2 + 2
    pygame.draw.circle(screen, WHITE, center, pulse, 1)

def draw_score(screen, score, invincibility_active=False, invincibility_timer_remaining=0.0):
    pygame.draw.rect(screen, (26, 26, 26),
                     (0, GRID_PIXEL_HEIGHT, WINDOW_WIDTH, SCORE_BAR_HEIGHT))
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    text_y = GRID_PIXEL_HEIGHT + (SCORE_BAR_HEIGHT - score_text.get_height()) // 2
    screen.blit(score_text, (10, text_y))
    if invincibility_active:
        secs = math.ceil(invincibility_timer_remaining)
        inv_text = font.render(f"INV: {secs}", True, INVINCIBILITY_COLOR)
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (10, text_y)
        screen.blit(inv_text, (score_text_rect.right + HUD_INVINCIBILITY_OFFSET, text_y))

def game_over_screen(screen, score):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, GRID_PIXEL_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, 48)
    game_over_text = font.render('Game Over!', True, WHITE)
    score_text = font.render(f'Final Score: {score}', True, WHITE)
    restart_text = font.render('Press SPACE to restart or ESC to quit', True, WHITE)
    
    game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, GRID_PIXEL_HEIGHT // 2 - 60))
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, GRID_PIXEL_HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, GRID_PIXEL_HEIGHT // 2 + 60))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)

    # Add a pulsating effect to the "Game Over!" text
    pulse = math.sin(pygame.time.get_ticks() * 0.005) * 10 + 20
    pygame.draw.rect(screen, WHITE, game_over_rect.inflate(pulse, pulse), 2)

def draw_rules_screen(screen):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    screen.blit(overlay, (0, 0))

    font_title  = pygame.font.SysFont('Arial', 42, bold=True)
    font_body   = pygame.font.SysFont('Arial', 22)
    font_prompt = pygame.font.SysFont('Arial', 16)

    title_surf = font_title.render('Test1 Rules', True, (255, 255, 255))
    screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 160)))

    rules_lines = [
        'Use the arrow keys to control the snake.',
        'Eat the green apples to grow and increase your score.',
        'Avoid hitting the walls or yourself.',
        'The game gets harder as you grow longer.',
    ]
    for i, line in enumerate(rules_lines):
        surf = font_body.render(line, True, (200, 200, 200))
        screen.blit(surf, surf.get_rect(center=(WINDOW_WIDTH // 2, 260 + i * 40)))

    prompt_surf = font_prompt.render('Press any key or click to continue', True, (150, 150, 150))
    screen.blit(prompt_surf, prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, 500)))

    pygame.display.flip()


def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()
    
    snake = Snake()
    food = Food(snake.body)
    score = 0
    game_over = False
    paused = False
    mines = []
    mine_flash_state = False
    mine_flash_accumulator = 0.0
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
    super_food_position = None
    super_food_flash_state = False
    super_food_flash_acc = 0.0
    super_food_mine_index = None
    super_food_mine_counter = 0
    invincibility_active = False
    invincibility_timer_remaining = 0.0
    invincibility_music_channel = None
    show_rules = True
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if show_rules:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    show_rules = False
                continue

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        # Restart game
                        snake = Snake()
                        food = Food(snake.body)
                        score = 0
                        game_over = False
                        paused = False
                        mines = []
                        mine_flash_state = False
                        mine_flash_accumulator = 0.0
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
                        super_food_position = None
                        super_food_flash_state = False
                        super_food_flash_acc = 0.0
                        super_food_mine_index = None
                        super_food_mine_counter = 0
                        invincibility_active = False
                        invincibility_timer_remaining = 0.0
                        _stop_invincibility_music()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)

            snake.move()
            dt = clock.get_time() / 1000.0

            # Mine flash timer
            mine_flash_accumulator += dt
            if mine_flash_accumulator >= MINE_FLASH_INTERVAL:
                mine_flash_state = not mine_flash_state
                mine_flash_accumulator = 0.0

            # Super-Food flash timer
            if super_food_position is not None:
                super_food_flash_acc += dt
                if super_food_flash_acc >= SUPER_FOOD_FLASH_INTERVAL:
                    super_food_flash_state = not super_food_flash_state
                    super_food_flash_acc -= SUPER_FOOD_FLASH_INTERVAL

            # Invincibility timer countdown
            if invincibility_active:
                invincibility_timer_remaining -= dt
                if invincibility_timer_remaining <= 0:
                    invincibility_active = False
                    invincibility_timer_remaining = 0.0
                    _stop_invincibility_music()

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
                    if super_food_mine_index is not None and super_food_mine_counter == super_food_mine_index:
                        super_food_position = storm_current_mine
                        super_food_flash_state = True
                        super_food_flash_acc = 0.0
                    super_food_mine_counter += 1
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
                if not invincibility_active:
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

            # Super-Food collision
            if super_food_position is not None and snake.next_head == super_food_position:
                super_food_position = None
                if not invincibility_active:
                    invincibility_active = True
                    invincibility_timer_remaining = INVINCIBILITY_DURATION
                    _start_invincibility_music()

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
                    super_food_mine_index = random.randint(0, len(storm_queue) - 1)
                    super_food_mine_counter = 0
                    if super_food_position is not None:
                        super_food_position = None
                    border_flash_state = False
                    border_flash_acc = 0.0
                    storm_current_mine = storm_queue.pop(0)
                    storm_phase = 'warning'
                    storm_phase_elapsed = 0.0
                    storm_warning_flash_acc = 0.0
                    storm_warning_flash_index = 0

            # Check for collision
            if snake.check_collision():
                if not invincibility_active:
                    game_over = True
        
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
        draw_super_food(screen, super_food_position, super_food_flash_state)
        draw_snake(screen, snake, invincibility_active)
        draw_score(screen, score, invincibility_active, invincibility_timer_remaining)

        if game_over:
            game_over_screen(screen, score)
        
        if paused and not game_over:
            draw_pause_overlay(screen)
        
        pygame.display.flip()
        clock.tick(60)

# Add these new functions at the end of the file
food_particles = []

def create_food_particles(position):
    global food_particles
    num_particles = 10
    for _ in range(num_particles):
        particle = {
            'pos': [position[0] * GRID_SIZE + GRID_SIZE // 2, position[1] * GRID_SIZE + GRID_SIZE // 2],
            'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
            'ttl': 30,  # Time to live (in frames)
        }
        food_particles.append(particle)

def draw_food_particles(screen):
    global food_particles
    new_particles = []
    for particle in food_particles:
        particle['pos'][0] += particle['vel'][0]
        particle['pos'][1] += particle['vel'][1]
        particle['ttl'] -= 1
        if particle['ttl'] > 0:
            alpha = int(255 * (particle['ttl'] / 30))
            color = (*FOOD_COLOR[:3], alpha)
            pygame.draw.circle(screen, color, (int(particle['pos'][0]), int(particle['pos'][1])), 2)
            new_particles.append(particle)
    food_particles = new_particles

BG_TOP = (20, 0, 40)  # Dark purple for top of background gradient

def draw_gradient_background(screen):
    for y in range(GRID_PIXEL_HEIGHT):
        r = int((y / GRID_PIXEL_HEIGHT) * (DARK_BLUE[0] - BG_TOP[0]) + BG_TOP[0])
        g = int((y / GRID_PIXEL_HEIGHT) * (DARK_BLUE[1] - BG_TOP[1]) + BG_TOP[1])
        b = int((y / GRID_PIXEL_HEIGHT) * (DARK_BLUE[2] - BG_TOP[2]) + BG_TOP[2])
        color = (r, g, b)
        pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))


def draw_mines(screen, mines, flash_state):
    color = MINE_COLOR_A if flash_state else MINE_COLOR_B
    for mx, my in mines:
        pygame.draw.rect(screen, color, (mx * GRID_SIZE, my * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_storm_border(screen, flash_state):
    color = STORM_BORDER_COLOR_A if flash_state else STORM_BORDER_COLOR_B
    pygame.draw.rect(screen, color, (0, 0, WINDOW_WIDTH, GRID_PIXEL_HEIGHT), 2)

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

def draw_super_food(screen, pos, flash_state):
    if pos is None:
        return
    color = SUPER_FOOD_COLOR_A if flash_state else SUPER_FOOD_COLOR_B
    sx, sy = pos
    pygame.draw.rect(screen, color, (sx * GRID_SIZE, sy * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def _start_invincibility_music():
    try:
        pygame.mixer.music.load(INVINCIBILITY_MUSIC_PATH)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"WARNING: Could not load invincibility music: {e}", file=sys.stderr)

def _stop_invincibility_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

if __name__ == '__main__':
    main()

# Add this at the end of the file
pygame.quit()


