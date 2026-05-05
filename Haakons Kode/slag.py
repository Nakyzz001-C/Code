import pygame
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 600, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Square Punch With Hand")
clock = pygame.time.Clock()

# Colors
BG = (30, 30, 30)
BODY_COLOR = (0, 200, 255)
HAND_COLOR = (0, 150, 200)

# Sizes
body_size = 50
hand_width = 20
hand_height = 10

# Positions
body_x = 150
body_y = HEIGHT // 2 - body_size // 2

# Punch variables
punching = False
hand_offset = 0
hand_speed = 6
max_reach = 35

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not punching:
                punching = True

    # Punch animation
    if punching:
        hand_offset += hand_speed

        if hand_offset >= max_reach:
            hand_speed = -hand_speed

        if hand_offset <= 0:
            hand_offset = 0
            hand_speed = abs(hand_speed)
            punching = False

    # Draw
    screen.fill(BG)

    # Body
    pygame.draw.rect(
        screen,
        BODY_COLOR,
        (body_x, body_y, body_size, body_size)
    )

    # Hand (punching part)
    hand_x = body_x + body_size // 2 + hand_offset
    hand_y = body_y + body_size // 2 - hand_height // 2

    pygame.draw.rect(
        screen,
        HAND_COLOR,
        (hand_x, hand_y, hand_width, hand_height)
    )

    pygame.display.flip()
    clock.tick(60)
