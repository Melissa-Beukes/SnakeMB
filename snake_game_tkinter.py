import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import winsound
import sys
from leaderboard import HighScoreManager

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
GAME_SPEED = 150  # milliseconds
FOOD_COLOR = '#FF69B4'  # Hot Pink (RGB 255, 105, 180)

# Mine colors and timing
MINE_COLOR_A = '#FF0000'
MINE_COLOR_B = '#C8C8C8'
MINE_FLASH_INTERVAL = 200   # milliseconds

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

# Snake color palette (bright colors visible on dark backgrounds)
SNAKE_COLORS = [
    '#0064FF',      # Bright Blue
    '#00FFFF',      # Cyan
    '#32FF32',      # Lime Green
    '#FFFF00',      # Yellow
    '#FFA500',      # Orange
    '#FF3232',      # Red
    '#FF00FF',      # Magenta
    '#FF69B4',      # Hot Pink
]

# Invincibility Power-Up constants
SUPER_FOOD_COLOR_A        = '#FFFF00'
SUPER_FOOD_COLOR_B        = '#000000'
SUPER_FOOD_FLASH_INTERVAL = 250
INVINCIBILITY_DURATION_MS = 10000
INVINCIBILITY_COLOR       = '#FFFF00'
INVINCIBILITY_MUSIC_PATH  = r"C:\Users\GrahamSaunders\Downloads\snake_game_v1.1.0\music\chiptune_triumphant.wav"
HUD_INVINCIBILITY_OFFSET  = 5 * GRID_SIZE

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


_EMPTY_LB_MESSAGE = "No high scores yet!\n\nBe the first to set a record!"
_LB_TITLE = "=== TOP 10 HIGH SCORES ==="
_LB_HEADER = (
    f"{'Rank':>4}  {'Name':<4} {'Score':>6}  {'Food':>5}  {'Mines':>5}  {'Inv':>4}\n"
)
_LB_DIVIDER = "-" * 44 + "\n"


def _format_row(rank, entry):
    """Render one leaderboard row from an entry dict.

    Legacy entries lacking stats keys render those columns as 0.
    """
    food = entry.get("food_eaten", 0)
    mines = entry.get("mine_shrinks", 0)
    inv = entry.get("invincibility_count", 0)
    return (
        f"{rank:>4}.  {entry['name']:<4} {entry['score']:>6}"
        f"  {food:>5}  {mines:>5}  {inv:>4}\n"
    )


def format_leaderboard_message(scores):
    """Return a human-readable leaderboard string for messagebox.showinfo.

    Pure function: no side effects, no GUI calls. Tolerates legacy
    entries lacking the stats keys by defaulting them to 0.
    """
    if not scores:
        return _EMPTY_LB_MESSAGE
    msg = _LB_TITLE + "\n" + _LB_HEADER + _LB_DIVIDER
    for i, entry in enumerate(scores, 1):
        msg += _format_row(i, entry)
    return msg


_LB_WINDOW_WIDTH = 540
_LB_WINDOW_HEIGHT = 420
_LB_FONT = ("Consolas", 14)


def _show_leaderboard_window(parent_root, message):
    """Show the leaderboard in a Toplevel with a monospace Text widget.

    Side-effecting GUI helper. Kept as a module-level function so tests
    can patch it directly via snake_game_tkinter._show_leaderboard_window.
    """
    top = tk.Toplevel(parent_root)
    top.title("Leaderboard")
    top.geometry(f"{_LB_WINDOW_WIDTH}x{_LB_WINDOW_HEIGHT}")
    top.resizable(False, False)
    top.transient(parent_root)
    try:
        top.grab_set()
    except tk.TclError:
        pass

    text = tk.Text(
        top,
        font=_LB_FONT,
        wrap="none",
        borderwidth=0,
        padx=12,
        pady=12,
    )
    text.insert("1.0", message)
    text.configure(state="disabled")
    text.pack(fill="both", expand=True)

    ok = tk.Button(top, text="OK", width=10, command=top.destroy)
    ok.pack(pady=(0, 12))
    ok.focus_set()
    top.bind("<Return>", lambda _e: top.destroy())
    top.bind("<Escape>", lambda _e: top.destroy())


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='#1a0030')
        self.canvas.pack()
        self.paused = False
        
        # Score label — positioned below canvas using pack geometry manager
        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 16), bg='#1a0030', fg='white')
        self.score_label.pack(fill='x', padx=10, pady=5)
        self.inv_label = tk.Label(root, text="", font=("Arial", 16), bg='#1a0030', fg='#FFFF00')
        self.inv_label.pack(fill='x', padx=10, pady=0)
        
        # Initialize leaderboard manager
        self.leaderboard = HighScoreManager()
        
        # Game state
        self.reset_game()
        
        # Rules screen state
        self.show_rules = True
        
        # Key bindings
        self.root.bind('<Up>', lambda e: self.change_direction(UP))
        self.root.bind('<Down>', lambda e: self.change_direction(DOWN))
        self.root.bind('<Left>', lambda e: self.change_direction(LEFT))
        self.root.bind('<Right>', lambda e: self.change_direction(RIGHT))
        self.root.bind('<space>', lambda e: self.restart_game() if self.game_over else None)
        self.root.bind('<Escape>', lambda e: self.root.quit())

        
        # Start game loop
        self.game_loop()
    
    def reset_game(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.color_index = 0  # Track current color
        self.paused = False
        self.score_label.config(text=f"Score: {self.score}")
        self.mines = []
        self.mine_flash_state = False
        if hasattr(self, '_flash_after_id'):
            self.root.after_cancel(self._flash_after_id)
        self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)
        # Storm state reset
        self.storm_active = False
        self.storm_queue = []
        self.storm_phase = None
        self.storm_current_mine = None
        self.storm_phase_start_ms = 0
        self.storm_warning_flash_state = False
        self.bonus_foods = []
        self.super_food_position = None
        self.super_food_flash_state = False
        self.super_food_mine_index = None
        self.super_food_mine_counter = 0
        self.invincibility_active = False
        self.invincibility_timer_remaining = 10
        if hasattr(self, '_super_food_flash_after_id') and self._super_food_flash_after_id:
            self.root.after_cancel(self._super_food_flash_after_id)
        self._super_food_flash_after_id = None
        if hasattr(self, '_inv_tick_after_id') and self._inv_tick_after_id:
            self.root.after_cancel(self._inv_tick_after_id)
        self._inv_tick_after_id = None
        if hasattr(self, '_inv_end_after_id') and self._inv_end_after_id:
            self.root.after_cancel(self._inv_end_after_id)
        self._inv_end_after_id = None
        self.inv_label.config(text="")
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass
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
        # Stats counters — reset on each new game
        self.food_eaten = 0
        self.mine_shrinks = 0
        self.invincibility_count = 0

    def generate_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos
    
    def change_direction(self, new_direction):
        # Prevent reversing direction
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.next_direction = new_direction
    
    def move_snake(self):
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            if not self.invincibility_active:
                return True
        
        # Check self collision
        if new_head in self.snake:
            if not self.invincibility_active:
                return True
        
        self.snake.insert(0, new_head)
        
        # Check food consumption
        if new_head == self.food:
            self.score += 1
            self.food_eaten += 1  # Track regular food consumed
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            self.score_label.config(text=f"Score: {self.score}")
            self.food = self.generate_food()
            self._try_spawn_mine()
            # Storm trigger
            if not self.storm_active and len(self.mines) >= STORM_TRIGGER_COUNT:
                self._start_storm()
        else:
            self.snake.pop()

        # Phase 2 explosion kill check
        if self.storm_active and self.storm_phase == 'explosion' and self.storm_current_mine:
            mx, my = self.storm_current_mine
            blast_cells = set()
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    cx, cy = mx + dx, my + dy
                    if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT:
                        blast_cells.add((cx, cy))
            for segment in self.snake:
                if segment in blast_cells:
                    if not self.invincibility_active:
                        self._end_storm()
                        return True

        # Bonus food consumption
        if new_head in self.bonus_foods:
            self.bonus_foods.remove(new_head)
            self.food_eaten += 1  # Track bonus food consumed
            self.snake.append(self.snake[-1])
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self._try_spawn_mine()

        # Super-Food collision
        if self.super_food_position is not None and new_head == self.super_food_position:
            self.super_food_position = None
            if hasattr(self, '_super_food_flash_after_id') and self._super_food_flash_after_id:
                self.root.after_cancel(self._super_food_flash_after_id)
            self._super_food_flash_after_id = None
            if not self.invincibility_active:
                self._activate_invincibility()

        # Mine collision check
        if new_head in self.mines:
            if not self.invincibility_active:
                self.mine_shrinks += 1  # Track mine shrink events
                self.mines.remove(new_head)
                shrink = min(3, len(self.snake))
                del self.snake[-shrink:]
                self.score = max(0, self.score - 3)
                self.score_label.config(text=f"Score: {self.score}")
                if len(self.snake) == 0:
                    return True

        return False
    
    def draw(self):
        self.canvas.delete('all')
        
        # Draw grid
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            self.canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill='#282828')
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill='#282828')

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

        # Draw mines
        mine_color = MINE_COLOR_A if self.mine_flash_state else MINE_COLOR_B
        for mx, my in self.mines:
            x1 = mx * GRID_SIZE
            y1 = my * GRID_SIZE
            self.canvas.create_rectangle(x1, y1, x1 + GRID_SIZE, y1 + GRID_SIZE,
                                          fill=mine_color, outline='')

        # Draw bonus foods (always GREEN)
        for bx, by in self.bonus_foods:
            x1 = bx * GRID_SIZE
            y1 = by * GRID_SIZE
            self.canvas.create_rectangle(x1, y1, x1 + GRID_SIZE, y1 + GRID_SIZE,
                                         fill='#00FF00', outline='#006400')

        # Draw Super-Food
        if self.super_food_position is not None:
            sf_color = SUPER_FOOD_COLOR_A if self.super_food_flash_state else SUPER_FOOD_COLOR_B
            sfx, sfy = self.super_food_position
            x1 = sfx * GRID_SIZE
            y1 = sfy * GRID_SIZE
            self.canvas.create_rectangle(x1, y1, x1 + GRID_SIZE, y1 + GRID_SIZE,
                                         fill=sf_color, outline='')

        # Draw snake with current color
        current_color = INVINCIBILITY_COLOR if self.invincibility_active else SNAKE_COLORS[self.color_index]
        for segment in self.snake:
            x1 = segment[0] * GRID_SIZE
            y1 = segment[1] * GRID_SIZE
            x2 = x1 + GRID_SIZE
            y2 = y1 + GRID_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=current_color, outline='')
        
        # Draw food (ALWAYS YELLOW per .cursorrules)
        x1 = self.food[0] * GRID_SIZE
        y1 = self.food[1] * GRID_SIZE
        x2 = x1 + GRID_SIZE
        y2 = y1 + GRID_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=FOOD_COLOR, outline='')
        
        # Draw game over screen
        if self.game_over:
            self.canvas.create_rectangle(100, 200, 500, 400, fill='black', outline='white', width=3)
            self.canvas.create_text(300, 250, text='Game Over!',
                                   font=('Arial', 36, 'bold'), fill='white')
            self.canvas.create_text(300, 300, text=f'Final Score: {self.score}',
                                   font=('Arial', 24), fill='white')
            self.canvas.create_text(300, 350, text='Press SPACE to restart or ESC to quit',
                                   font=('Arial', 14), fill='white')
        
        # Draw pause overlay
        if self.paused and not self.game_over:
            overlay_width = WINDOW_WIDTH - 100
            overlay_height = 200
            overlay_x = 50
            overlay_y = (WINDOW_HEIGHT - overlay_height) // 2
            
            # Semi-transparent background
            self.canvas.create_rectangle(overlay_x, overlay_y,
                                           overlay_x + overlay_width,
                                           overlay_y + overlay_height,
                                           fill='black', outline='white', width=3,
                                           stipple='gray50')
            
            # PAUSED text
            self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30,
                                    text='PAUSED', font=('Arial', 48, 'bold'),
                                    fill='white')
            
            # Instruction text
            self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30,
                                    text='Press P to Resume', font=('Arial', 24),
                                    fill='white')
    
    def game_loop(self):
        if not self.game_over:
            collision = self.move_snake()
            if collision:
                self.game_over = True
                # Handle game over (leaderboard check/display) on next frame
                # Using after() ensures UI is updated before showing dialogs
                self.root.after(100, self.handle_game_over)
        
        self.draw()
        self.root.after(GAME_SPEED, self.game_loop)
    
    def restart_game(self):
        self.reset_game()
    
    def prompt_for_name(self):
        """Prompt player for name (1-20 characters) with validation."""
        while True:
            name = simpledialog.askstring(
                "High Score!",
                "Enter your name (up to 20 characters, A-Z or 0-9):",
                parent=self.root
            )
            
            # Cancel button or dialog closed
            if name is None:
                return None
            
            # Validate name
            if self.leaderboard.validate_name(name):
                return name.upper()
            else:
                messagebox.showerror(
                    "Invalid Name",
                    "Name must be 1-20 alphanumeric characters (A-Z, 0-9).",
                    parent=self.root
                )
    
    def display_leaderboard(self):
        """Display leaderboard in a Toplevel with a monospace Text widget.

        A native messagebox renders with a proportional font, which makes
        the column-aligned formatter output drift. A Toplevel + Text in
        Consolas keeps the columns straight and lets us size the window.
        """
        message = format_leaderboard_message(
            self.leaderboard.get_leaderboard()
        )
        _show_leaderboard_window(self.root, message)
    
    def handle_game_over(self):
        """Handle game over logic including leaderboard check."""
        if self.leaderboard.is_high_score(self.score):
            name = self.prompt_for_name()
            if name:
                try:
                    self.leaderboard.add_score(
                        self.score, name,
                        food_eaten=self.food_eaten,
                        mine_shrinks=self.mine_shrinks,
                        invincibility_count=self.invincibility_count
                    )
                    messagebox.showinfo(
                        "Score Saved!",
                        f"Congratulations {name}!\nYour score of {self.score} has been added to the leaderboard!",
                        parent=self.root
                    )
                except ValueError as e:
                    messagebox.showerror("Error", str(e), parent=self.root)
        
        # Always display leaderboard after game over
        self.display_leaderboard()

    def toggle_pause(self):
        """Toggle pause state and manage overlay."""
        self.paused = not self.paused

    def _dismiss_rules(self, event=None):
        if self.show_rules:
            self.show_rules = False

    def _draw_rules(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(
            80, 120, WINDOW_WIDTH - 80, WINDOW_HEIGHT - 120,
            fill='black', outline='white', width=3
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, 175,
            text='Test1 Rules',
            font=('Arial', 32, 'bold'), fill='white'
        )
        rules_lines = [
            'Use the arrow keys to control the snake.',
            'Eat the green apples to grow and increase',
            'your score. Avoid hitting the walls or yourself.',
            'The game gets harder as you grow longer.',
        ]
        for i, line in enumerate(rules_lines):
            self.canvas.create_text(
                WINDOW_WIDTH // 2, 250 + i * 35,
                text=line,
                font=('Arial', 16), fill='#C8C8C8'
            )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, 430,
            text='Press any key or click to continue',
            font=('Arial', 13), fill='#969696'
        )

    def _toggle_mine_flash(self):
        self.mine_flash_state = not self.mine_flash_state
        self._flash_after_id = self.root.after(MINE_FLASH_INTERVAL, self._toggle_mine_flash)

    def _toggle_super_food_flash(self):
        if self.super_food_position is None:
            self._super_food_flash_after_id = None
            return
        self.super_food_flash_state = not self.super_food_flash_state
        self._super_food_flash_after_id = self.root.after(SUPER_FOOD_FLASH_INTERVAL, self._toggle_super_food_flash)

    def _activate_invincibility(self):
        self.invincibility_count += 1  # Track invincibility activations
        self.invincibility_active = True
        self.invincibility_timer_remaining = 10
        self.inv_label.config(text=f"INV: {self.invincibility_timer_remaining}")
        if hasattr(self, '_inv_tick_after_id') and self._inv_tick_after_id:
            self.root.after_cancel(self._inv_tick_after_id)
        self._inv_tick_after_id = self.root.after(1000, self._tick_invincibility)
        if hasattr(self, '_inv_end_after_id') and self._inv_end_after_id:
            self.root.after_cancel(self._inv_end_after_id)
        self._inv_end_after_id = self.root.after(INVINCIBILITY_DURATION_MS, self._end_invincibility)
        try:
            winsound.PlaySound(INVINCIBILITY_MUSIC_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        except Exception as e:
            print(f"WARNING: Could not play invincibility music: {e}", file=sys.stderr)

    def _tick_invincibility(self):
        if not self.invincibility_active:
            return
        self.invincibility_timer_remaining = max(0, self.invincibility_timer_remaining - 1)
        self.inv_label.config(text=f"INV: {self.invincibility_timer_remaining}")
        if self.invincibility_timer_remaining > 0:
            self._inv_tick_after_id = self.root.after(1000, self._tick_invincibility)

    def _end_invincibility(self):
        self.invincibility_active = False
        self.invincibility_timer_remaining = 0
        self.inv_label.config(text="")
        if hasattr(self, '_inv_tick_after_id') and self._inv_tick_after_id:
            self.root.after_cancel(self._inv_tick_after_id)
        self._inv_tick_after_id = None
        if hasattr(self, '_inv_end_after_id') and self._inv_end_after_id:
            self.root.after_cancel(self._inv_end_after_id)
        self._inv_end_after_id = None
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

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
            # silently skip if 1000 attempts exhausted

    def _start_storm(self):
        self.storm_active = True
        self.storm_queue = self.mines[:]
        random.shuffle(self.storm_queue)
        self.mines = []
        self.super_food_mine_index = random.randint(0, len(self.storm_queue) - 1)
        self.super_food_mine_counter = 0
        if self.super_food_position is not None:
            self.super_food_position = None
            if hasattr(self, '_super_food_flash_after_id') and self._super_food_flash_after_id:
                self.root.after_cancel(self._super_food_flash_after_id)
            self._super_food_flash_after_id = None
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
        if self.super_food_mine_index is not None and self.super_food_mine_counter == self.super_food_mine_index:
            self.super_food_position = self.storm_current_mine
            self.super_food_flash_state = True
            if hasattr(self, '_super_food_flash_after_id') and self._super_food_flash_after_id:
                self.root.after_cancel(self._super_food_flash_after_id)
            self._super_food_flash_after_id = self.root.after(SUPER_FOOD_FLASH_INTERVAL, self._toggle_super_food_flash)
        self.super_food_mine_counter += 1
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

def main():
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()

if __name__ == '__main__':
    main()



