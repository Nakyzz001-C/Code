import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2nd_test")
clock = pygame.time.Clock()

# Colors
BG = (30, 30, 30)
PLAYER_COLOR = (0, 200, 255)
BOX_COLOR = (255, 80, 80)
RED = (255, 0, 0)
WHITE = (240, 240, 240)

# Square (player) settings
square_size = 50
square_x = 50
square_y = 125
run_speed = 10
speed = 5
y_velocity = 0
gravity = 0.6
jump_strength = -20
on_ground = False

# Target box (platform)
box = pygame.Rect(200, 300, 120, 30)

# Ground
ground_y = HEIGHT - 50

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Jump
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False

    # Apply gravity
    y_velocity += gravity
    square_y += y_velocity

    # Create player rect (IMPORTANT: synced with position)
    player = pygame.Rect(square_x, square_y, square_size, square_size)

    # --- Collision with ground ---
    if player.bottom >= ground_y:
        square_y = ground_y - square_size
        y_velocity = 0
        on_ground = True

    # --- Collision with box (platform) ---
    if player.colliderect(box):
        # Landing on top of box
        if y_velocity > 0 and player.bottom <= box.top + 10:
            square_y = box.top - square_size
            y_velocity = 0
            on_ground = True

    # Movement (left/right only for platformer feel)
    keys = pygame.key.get_pressed() 
    if keys[pygame.K_a]: square_x -= run_speed 
    if keys[pygame.K_d]: square_x += run_speed 
    if keys[pygame.K_w]: square_y -= speed 
    if keys[pygame.K_s]: square_y += speed

    # Keep player on screen
    square_x = max(0, min(WIDTH - square_size, square_x))
    square_y = min(square_y, HEIGHT - square_size)

    # Update player rect again after movement
    player = pygame.Rect(square_x, square_y, square_size, square_size)

    # Drawing
    screen.fill(BG)

    # Player
    pygame.draw.rect(screen, PLAYER_COLOR, player)

    # Box (platform)
    pygame.draw.rect(screen, BOX_COLOR, box)

    # Ground
    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))

    pygame.display.flip()
    clock.tick(60)