import pygame
import random
import time
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1800, 1090
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Aim Trainer")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
FLASH_HIT_COLOR = (255, 255, 255, 150)  # semi-transparent white
FLASH_MISS_COLOR = (255, 0, 0, 150)     # semi-transparent red

# Target properties
TARGET_RADIUS = 38

# Font for text
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

# Clock for FPS control
clock = pygame.time.Clock()

# Game variables
score = 0
shots_fired = 0
hits = 0
target_lifetime = 2  # seconds
mode = None  # None means menu is active
session_time = 45  # seconds
session_start_time = None
flash_color = None
flash_start_time = 0
flash_duration = 0.2  # seconds

# Target class
class Target:
    def __init__(self, x, y, radius=TARGET_RADIUS, speed=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed  # pixels per frame
        self.direction = random.choice([-1, 1])
        self.spawn_time = time.time()
        self.hit = False

    def draw(self, surface):
        color = GREEN if self.hit else RED
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        if mode == "tracking" and not self.hit:
            # Move target horizontally back and forth
            self.x += self.speed * self.direction
            if self.x < self.radius or self.x > WIDTH - self.radius:
                self.direction *= -1

    def is_expired(self):
        return time.time() - self.spawn_time > target_lifetime

    def check_hit(self, pos):
        if not self.hit:
            dist = ((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5
            if dist <= self.radius:
                self.hit = True
                return True
        return False

# Spawn a new target
def spawn_target():
    x = random.randint(TARGET_RADIUS, WIDTH - TARGET_RADIUS)
    y = random.randint(TARGET_RADIUS, HEIGHT - TARGET_RADIUS)
    speed = 3 if mode == "tracking" else 0
    return Target(x, y, speed=speed)

# Draw crosshair at mouse position
def draw_crosshair(surface, pos):
    pygame.draw.line(surface, WHITE, (pos[0] - 10, pos[1]), (pos[0] + 10, pos[1]), 2)
    pygame.draw.line(surface, WHITE, (pos[0], pos[1] - 10), (pos[0], pos[1] + 10), 2)

# Display score, accuracy, and timer
def draw_stats(surface, score, hits, shots, time_left):
    accuracy = (hits / shots * 100) if shots > 0 else 0
    score_text = font.render(f"Score: {score}", True, WHITE)
    accuracy_text = font.render(f"Accuracy: {accuracy:.1f}%", True, WHITE)
    timer_text = font.render(f"Time Left: {int(time_left)}s", True, WHITE)
    surface.blit(score_text, (10, 10))
    surface.blit(accuracy_text, (10, 50))
    surface.blit(timer_text, (WIDTH - 180, 10))

# Draw flash effect (semi-transparent overlay)
def draw_flash(surface, color):
    flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    flash_surface.fill(color)
    surface.blit(flash_surface, (0, 0))

# Draw menu screen
def draw_menu(surface, selected_index):
    surface.fill(BLACK)
    title = large_font.render("2D Aim Trainer", True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    options = ["Flick Mode", "Tracking Mode", "Quit"]
    for i, option in enumerate(options):
        color = GREEN if i == selected_index else WHITE
        text = font.render(option, True, color)
        surface.blit(text, (WIDTH//2 - text.get_width()//2, 250 + i * 50))

    instructions = font.render("Use UP/DOWN to select, ENTER to confirm", True, WHITE)
    surface.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 100))

# Draw summary screen
def draw_summary(surface, score, hits, shots):
    surface.fill(BLACK)
    accuracy = (hits / shots * 100) if shots > 0 else 0
    summary_title = large_font.render("Session Summary", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    accuracy_text = font.render(f"Accuracy: {accuracy:.1f}%", True, WHITE)
    restart_text = font.render("Press ENTER to return to menu", True, WHITE)

    surface.blit(summary_title, (WIDTH//2 - summary_title.get_width()//2, 150))
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 250))
    surface.blit(accuracy_text, (WIDTH//2 - accuracy_text.get_width()//2, 300))
    surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 400))

def main():
    global score, shots_fired, hits, mode, session_start_time, flash_color, flash_start_time

    running = True
    target = None
    flash_color = None
    flash_start_time = 0
    flash_duration = 0.2
    selected_menu_index = 0
    in_summary = False

    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if mode is None:
                # Show mouse cursor in menu
                pygame.mouse.set_visible(True)

                # Menu navigation
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_menu_index = (selected_menu_index - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        selected_menu_index = (selected_menu_index + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if selected_menu_index == 0:
                            mode = "flick"
                        elif selected_menu_index == 1:
                            mode = "tracking"
                        elif selected_menu_index == 2:
                            running = False
                        if mode:
                            # Reset game variables for new session
                            score = 0
                            shots_fired = 0
                            hits = 0
                            session_start_time = current_time
                            target = spawn_target()
                            in_summary = False

            elif in_summary:
                # Show mouse cursor in summary
                pygame.mouse.set_visible(True)

                # Summary screen input
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    mode = None
                    in_summary = False

            else:
                # Hide mouse cursor during gameplay
                pygame.mouse.set_visible(False)

                # Game input
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    shots_fired += 1
                    if target and target.check_hit(mouse_pos):
                        hits += 1
                        score += 10
                        flash_color = FLASH_HIT_COLOR
                        flash_start_time = current_time
                    else:
                        flash_color = FLASH_MISS_COLOR
                        flash_start_time = current_time

        # Game logic and drawing
        if mode and not in_summary:
            # Update target
            if target:
                target.update()
                target.draw(screen)

                # Respawn target if hit or expired
                if target.hit or target.is_expired():
                    target = spawn_target()

            # Draw crosshair
            draw_crosshair(screen, mouse_pos)

            # Timer
            time_left = session_time - (current_time - session_start_time)
            if time_left <= 0:
                # Show summary
                in_summary = True
                mode = None

            # Draw stats and timer
            draw_stats(screen, score, hits, shots_fired, max(0, time_left))

        elif mode is None and not in_summary:
            # Draw menu
            draw_menu(screen, selected_menu_index)

        elif in_summary:
            # Draw summary screen
            draw_summary(screen, score, hits, shots_fired)

        # Draw flash effect if active
        if flash_color and (current_time - flash_start_time) < flash_duration:
            draw_flash(screen, flash_color)
        else:
            flash_color = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
