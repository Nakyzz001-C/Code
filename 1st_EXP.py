import pygame
import sys

pygame.init()


screen_width = 1800
screen_height = 1200
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("1st EXP")

#Firkant settings
height = 100
width = 100
x = screen_width //2
y = screen_height //2

y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False

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
    y += y_velocity

    # Collision with ground
    if y + x >= ground_y:
        y = ground_y - size
        y_velocity = 0
        on_ground = True

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (0,0,0), [x,y,width,height])
    pygame.display.flip()

