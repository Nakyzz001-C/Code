import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2nd_test")

# Colors
BG = (30, 30, 30)
PLAYER_COLOR = (0, 200, 255)
BOX_COLOR = (255, 80, 80)
RED = (255, 0, 0)
WHITE = (240, 240, 240)


# Clock
clock = pygame.time.Clock()

# Square settings
square = pygame.Rect(0, 0, 0 , 0)
square_size = 50
square_x = WIDTH // 2
square_y = HEIGHT // 2
speed = 5
y_velocity = 0
gravity = 0.6
jump_strength = -20
on_ground = False

# Target square
box = pygame.Rect(200, 100, 40, 40)

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

    # Collision with ground
    if square_y + square_size >= ground_y:
        square_y = ground_y - square_size
        y_velocity = 0
        on_ground = True

    # Key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        square_x -= speed
    if keys[pygame.K_d]:
        square_x += speed
    if keys[pygame.K_w]:
        square_y -= speed
    if keys[pygame.K_s]:
        square_y += speed

    # Collision check
    colliding = square.colliderect(box)

    # Keep square on screen
    square_x = max(0, min(WIDTH - square_size, square_x))
    square_y = max(0, min(HEIGHT - square_size, square_y))

    # Drawing
    screen.fill((30, 30, 30))  
    
    # background
    pygame.draw.rect(
        screen,
        (0, 200, 255),
        (square_x, square_y, square_size, square_size)
    )

    pygame.draw.rect(
        screen,
        RED if colliding else PLAYER_COLOR,
        square
    )

    pygame.draw.rect(screen, RED, box)

     # Ground
    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))

    pygame.display.flip()
    clock.tick(60)
