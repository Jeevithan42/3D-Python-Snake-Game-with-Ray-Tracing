import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 800
BLOCK_SIZE = 20
FPS_BASE = 12

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 40, 40)
GREEN = (40, 230, 40)
DARK_GREEN = (0, 160, 0)
GREY = (169, 169, 169)
DARK_GREY = (50, 50, 50)
WALL_COLOR = (120, 120, 130)

# Theme Backgrounds
BG_COLOR = (30, 30, 40) # Dark modern theme

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Snake: RTX ON")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("impact", 72)
font_large = pygame.font.SysFont("impact", 48)
font_medium = pygame.font.SysFont("trebuchet ms", 32, bold=True)
font_small = pygame.font.SysFont("trebuchet ms", 24, bold=True)

# Game Variables
highscore = 0
score = 0
level = 1
game_state = "menu"

modes = ["Classic Mode", "Wrap-Around Mode", "Maze Mode"]
selected_mode_idx = 0
current_mode = "Classic Mode"

snake = [(WIDTH // 2, HEIGHT // 2)]
dx, dy = 0, 0
food = (0, 0)
obstacles = []

def spawn_food():
    while True:
        x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        if y < 40: # keep off score area
            continue
        if (x, y) not in snake and (x, y) not in obstacles:
            return (x, y)

def spawn_obstacle():
    while True:
        x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        if y < 40:
            continue
        # Don't spawn too close to head
        head_x, head_y = snake[0]
        if abs(x - head_x) < 100 and abs(y - head_y) < 100:
            continue
            
        if (x, y) not in snake and (x, y) != food and (x, y) not in obstacles:
            obstacles.append((x, y))
            break

def reset_game(mode):
    global snake, dx, dy, score, level, food, current_mode, obstacles
    current_mode = mode
    snake = [(WIDTH // 2, HEIGHT // 2)]
    dx, dy = 0, 0
    score = 0
    level = 1
    obstacles = []
    
    if current_mode == "Maze Mode":
        for _ in range(5):
            spawn_obstacle()
            
    food = spawn_food()

food = spawn_food()

def draw_text(text, font, color, x, y, shadow=True):
    if shadow:
        surf_shadow = font.render(text, True, BLACK)
        rect_shadow = surf_shadow.get_rect()
        rect_shadow.center = (x + 3, y + 3)
        screen.blit(surf_shadow, rect_shadow)
        
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    rect.center = (x, y)
    screen.blit(surface, rect)

def draw_block(screen, color, x, y, size, is_head=False):
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 1)
    if is_head:
        eye_color = WHITE
        eye_pupil = BLACK
        eye_offset = 5
        eye_size = 4
        pupil_size = 2

# Transparent Grid
grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for x in range(0, WIDTH, BLOCK_SIZE):
    pygame.draw.line(grid_surface, (255, 255, 255, 10), (x, 0), (x, HEIGHT))
for y in range(0, HEIGHT, BLOCK_SIZE):
    pygame.draw.line(grid_surface, (255, 255, 255, 10), (0, y), (WIDTH, y))

running = True
while running:
    moved_this_frame = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_mode_idx = (selected_mode_idx - 1) % len(modes)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_mode_idx = (selected_mode_idx + 1) % len(modes)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    reset_game(modes[selected_mode_idx])
                    game_state = "playing"
            elif game_state == "playing" and not moved_this_frame:
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and dy == 0:
                    dx, dy = 0, -BLOCK_SIZE
                    moved_this_frame = True
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and dy == 0:
                    dx, dy = 0, BLOCK_SIZE
                    moved_this_frame = True
                elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and dx == 0:
                    dx, dy = -BLOCK_SIZE, 0
                    moved_this_frame = True
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and dx == 0:
                    dx, dy = BLOCK_SIZE, 0
                    moved_this_frame = True

    if game_state == "menu":
        screen.fill(BG_COLOR)
        screen.blit(grid_surface, (0,0))
        
        draw_text("SNAKE: RTX ON", font_title, GREEN, WIDTH // 2, HEIGHT // 2 - 150)
        
        if score == 0 and highscore > 0:
            draw_text("GAME OVER", font_large, RED, WIDTH // 2, HEIGHT // 2 - 60)
            
        draw_text(f"High Score: {highscore}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 10)
        
        for i, mode in enumerate(modes):
            color = GREEN if i == selected_mode_idx else GREY
            prefix = ">> " if i == selected_mode_idx else "   "
            suffix = " <<" if i == selected_mode_idx else "   "
            draw_text(prefix + mode + suffix, font_medium, color, WIDTH // 2, HEIGHT // 2 + 80 + i * 40)
            
        pygame.display.flip()
        clock.tick(15)
        continue

    # --- Game Logic ---
    if game_state == "playing":
        if dx != 0 or dy != 0:
            head_x, head_y = snake[0]
            new_head = (head_x + dx, head_y + dy)

            # Border collision
            if current_mode == "Wrap-Around Mode":
                if new_head[0] < 0:
                    new_head = (WIDTH - BLOCK_SIZE, new_head[1])
                elif new_head[0] >= WIDTH:
                    new_head = (0, new_head[1])
                elif new_head[1] < 0:
                    new_head = (new_head[0], HEIGHT - BLOCK_SIZE)
                elif new_head[1] >= HEIGHT:
                    new_head = (new_head[0], 0)
            else:
                if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
                    pygame.time.wait(1000)
                    game_state = "menu"
                    continue
                
            # Self Collision
            if new_head in snake:
                pygame.time.wait(1000)
                game_state = "menu"
                continue
                
            # Obstacle Collision
            if new_head in obstacles:
                pygame.time.wait(1000)
                game_state = "menu"
                continue
                
            snake.insert(0, new_head)

            # Food Collision
            if new_head == food:
                score += 10
                if score > highscore:
                    highscore = score
                    
                if score % 50 == 0 and score > 0:
                    level += 1
                    
                if current_mode == "Maze Mode" and score % 30 == 0:
                    spawn_obstacle()
                    spawn_obstacle()
                    
                food = spawn_food()
            else:
                snake.pop()

    # --- Rendering ---
    screen.fill(BG_COLOR)
    screen.blit(grid_surface, (0,0))
    
    render_queue = []
    
    # Food
    render_queue.append({'type': 'food', 'x': food[0], 'y': food[1], 'color': RED, 'is_head': False})
    
    # Obstacles
    for obs in obstacles:
        render_queue.append({'type': 'obstacle', 'x': obs[0], 'y': obs[1], 'color': WALL_COLOR, 'is_head': False})
    
    # Snake
    for i, segment in enumerate(snake):
        is_h = (i == 0)
        col = GREEN if is_h else DARK_GREEN
        render_queue.append({'type': 'snake', 'x': segment[0], 'y': segment[1], 'color': col, 'is_head': is_h})
    
    # Simple rendering (no 3D sorting or shadows)
    for item in render_queue:
        draw_block(screen, item['color'], item['x'], item['y'], BLOCK_SIZE, item['is_head'])
    
    # --- Main Draw Pass ---
    for item in render_queue:
        draw_block(screen, item['color'], item['x'], item['y'], BLOCK_SIZE, item['is_head'])
        
        # Add special glowing light effect to food
        if item['type'] == 'food':
            # Glow aura
            glow = pygame.Surface((BLOCK_SIZE*4, BLOCK_SIZE*4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 50, 50, 40), (BLOCK_SIZE*2, BLOCK_SIZE*2), BLOCK_SIZE*2)
            pygame.draw.circle(glow, (255, 100, 100, 80), (BLOCK_SIZE*2, BLOCK_SIZE*2), BLOCK_SIZE)
            screen.blit(glow, (item['x'] - BLOCK_SIZE*1.5, item['y'] - BLOCK_SIZE*1.5))
            
            pygame.draw.rect(screen, WHITE, (item['x']+4, item['y']+4, 6, 6), border_radius=2)

    # Draw Score UI
    score_text = f"Mode: {current_mode}   Score: {score}   High Score: {highscore}   Level: {level}"
    draw_text(score_text, font_small, WHITE, WIDTH // 2, 20)

    pygame.display.flip()
    
    if current_mode == "Classic Mode":
        current_fps = FPS_BASE + (level - 1) * 2
    else:
        current_fps = FPS_BASE + (level - 1)
        
    clock.tick(current_fps)

pygame.quit()
sys.exit()
