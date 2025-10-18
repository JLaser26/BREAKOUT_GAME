import pygame
from sys import exit as e
import random
import os
import json

pygame.init()

WIDTH, HEIGHT = 800, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (100, 255, 100)

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

COLORS = [random_color() for i in range(200)]

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BREAKOUT GAME")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

PROGRESS_FILE = "progress.json"

# ============================================================
# Utility: Load and Save Progress
# ============================================================
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            return data.get("max_level", 1)
    return 1

def save_progress(max_level):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"max_level": max_level}, f)

# ============================================================
# Ball Class
# ============================================================
class Ball:
    def __init__(self, sledge_rect, speed=3):
        self.radius = 7
        self.reset(sledge_rect, speed)
    
    def reset(self, sledge_rect, speed):
        """Place ball on top of sledge, not moving until launch."""
        self.ball_pos = [sledge_rect.centerx, sledge_rect.top - self.radius]
        self.ball_speed = [0, 0]
        self.launched = False
        self.base_speed = speed

    def draw(self):
        pygame.draw.circle(window, WHITE, (int(self.ball_pos[0]), int(self.ball_pos[1])), self.radius)

    def move(self, sledge_rect, bricks):
        global score

        if not self.launched:
            self.ball_pos[0] = sledge_rect.centerx
            self.ball_pos[1] = sledge_rect.top - self.radius
            return

        # Move ball
        self.ball_pos[0] += self.ball_speed[0]
        self.ball_pos[1] += self.ball_speed[1]

        # Bounce off walls
        if self.ball_pos[0] - self.radius <= 0 or self.ball_pos[0] + self.radius >= WIDTH:
            self.ball_speed[0] = -self.ball_speed[0]
        if self.ball_pos[1] - self.radius <= 0:
            self.ball_speed[1] = -self.ball_speed[1]

        ball_rect = pygame.Rect(self.ball_pos[0] - self.radius, self.ball_pos[1] - self.radius, self.radius * 2, self.radius * 2)

        # Bounce on sledge
        if ball_rect.colliderect(sledge_rect):
            self.ball_pos[1] = sledge_rect.top - self.radius
            self.ball_speed[1] = -self.ball_speed[1]
            hit_pos = (self.ball_pos[0] - sledge_rect.x) / sledge_rect.width
            self.ball_speed[0] = (hit_pos - 0.5) * 10

        # Hit bricks
        for brick in bricks[:]:
            if ball_rect.colliderect(brick.rect):
                self.ball_speed[1] = -self.ball_speed[1]
                bricks.remove(brick)
                score += 10
                break

        # Fall below
        if self.ball_pos[1] - self.radius > HEIGHT:
            game_over_screen("Game Over! Press R to Restart or ESC to Quit")

# ============================================================
# Sledge Class
# ============================================================
class Sledge:
    def __init__(self):
        self.width = 100
        self.height = 10
        self.speed = 6
        self.sledge_rect = pygame.Rect(WIDTH / 2 - self.width / 2, HEIGHT - 50, self.width, self.height)

    def draw(self):
        pygame.draw.rect(window, WHITE, self.sledge_rect)

    def move(self, keys):
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.sledge_rect.right < WIDTH:
            self.sledge_rect.x += self.speed
        elif (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.sledge_rect.left > 0:
            self.sledge_rect.x -= self.speed

# ============================================================
# Brick Class
# ============================================================
class Brick:
    def __init__(self, x, y, color):
        self.width = 75
        self.height = 25
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color

    def draw(self):
        pygame.draw.rect(window, self.color, self.rect)

# ============================================================
# Helper Functions
# ============================================================
def create_bricks(rows, cols):
    bricks = []
    offset_x, offset_y = 60, 50
    gap = 10
    for row in range(rows):
        for col in range(cols):
            x = offset_x + col * (75 + gap)
            y = offset_y + row * (25 + gap)
            color = random.choice(COLORS)
            bricks.append(Brick(x, y, color))
    return bricks

def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    window.blit(score_text, (20, 10))
    window.blit(level_text, (WIDTH - 150, 10))

def game_over_screen(message):
    while True:
        window.fill(BLACK)
        msg = font.render(message, True, WHITE)
        window.blit(msg, (WIDTH/2 - msg.get_width()/2, HEIGHT/2 - 20))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                e()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    level_select_menu()
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    e()

def next_level_screen():
    global level, max_unlocked
    level += 1
    max_unlocked = max(max_unlocked, level)
    save_progress(max_unlocked)
    msg = font.render(f"Level {level}", True, WHITE)
    sub_msg = font.render("Press SPACE to Continue", True, WHITE)

    while True:
        window.fill(BLACK)
        window.blit(msg, (WIDTH/2 - msg.get_width()/2, HEIGHT/2 - 40))
        window.blit(sub_msg, (WIDTH/2 - sub_msg.get_width()/2, HEIGHT/2 + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                e()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

def level_select_menu():
    global level, score, bricks, ball, player
    selected = 1
    while True:
        window.fill(BLACK)
        title = font.render("Select Level", True, WHITE)
        window.blit(title, (WIDTH/2 - title.get_width()/2, 150))

        for i in range(1, max_unlocked + 1):
            color = GREEN if i == selected else WHITE
            text = font.render(f"Level {i}", True, color)
            window.blit(text, (WIDTH/2 - text.get_width()/2, 220 + (i - 1) * 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                e()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = max(1, selected - 1)
                elif event.key == pygame.K_DOWN:
                    selected = min(max_unlocked, selected + 1)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    level = selected
                    score = 0
                    player = Sledge()
                    ball = Ball(player.sledge_rect, 3 + level)
                    bricks = create_bricks(4 + level, 8)
                    return
                elif event.key == pygame.K_ESCAPE:
                    main_menu()

def start_level(lvl):
    """Setup a specific level"""
    global level, score, bricks, ball, player
    level = lvl
    score = 0
    player = Sledge()
    ball = Ball(player.sledge_rect, 3 + level)
    bricks = create_bricks(4 + level, 8)

def main_menu():
    selected = 0
    options = ["Resume Last Level", "Level Select", "Quit"]

    while True:
        window.fill(BLACK)
        title = font.render("BREAKOUT GAME", True, WHITE)
        window.blit(title, (WIDTH/2 - title.get_width()/2, 200))

        for i, option in enumerate(options):
            color = GREEN if i == selected else WHITE
            text = font.render(option, True, color)
            window.blit(text, (WIDTH/2 - text.get_width()/2, 300 + i * 60))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                e()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if selected == 0:  # Resume
                        start_level(max_unlocked)
                        return
                    elif selected == 1:  # Level select
                        level_select_menu()
                        return
                    elif selected == 2:  # Quit
                        pygame.quit()
                        e()

# ============================================================
# Initialization
# ============================================================
max_unlocked = load_progress()
main_menu()

score = 0
running = True

# ============================================================
# Main Game Loop
# ============================================================
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            e()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not ball.launched:
                ball.launched = True
                x_angle = random.uniform(-1.5, 1.5)
                ball.ball_speed = [x_angle, -ball.base_speed]

    player.move(keys)
    ball.move(player.sledge_rect, bricks)

    window.fill(BLACK)
    player.draw()
    ball.draw()
    for brick in bricks:
        brick.draw()
    draw_score()

    # Win condition
    if not bricks:
        ball_speed = min(10, 3 + level)
        rows = min(8, 4 + level)
        next_level_screen()
        bricks = create_bricks(rows, 8)
        player = Sledge()
        ball = Ball(player.sledge_rect, ball_speed)

    pygame.display.update()
    clock.tick(90)
