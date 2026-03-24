import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1800, 1200
screen_width = 1800
screen_height = 1200
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("1st EXP")
clock = pygame.time.Clock()

# Colors
WHITE = (240, 240, 240)
RED = (255, 0, 0)
DARK = (30, 30, 30)

# Square (player)
player_x = 25
player_y = HEIGHT // 2
size = 100
x = WIDTH // 2 - size // 2
y = HEIGHT - size - 50
y_velocity = 0
gravity = 0.6
jump_strength = -12 
on_ground = False
player_pos = [WIDTH // 2, HEIGHT // 2]

# Ground
ground_y = HEIGHT - 90

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Jump with SPACE
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False
        # Move player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_y > 0:
        player_y -= 5
    if keys[pygame.K_s] and player_y < HEIGHT - 40:
        player_y += 5

    # Apply gravity
    y_velocity += gravity
    y += y_velocity

    # Collision with ground
    if y + size >= ground_y:
        y = ground_y - size
        y_velocity = 0
        on_ground = True




    # Draw
    screen.fill(DARK)

    # Ground
    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))

    # Square
    pygame.draw.rect(screen, RED, (x, y, size, size))

    pygame.display.flip()
    clock.tick(60)
