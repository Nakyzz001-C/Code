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


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (0,0,0), [x,y,width,height])
    pygame.display.flip()

