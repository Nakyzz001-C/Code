import pygame
import sys
import random

pygame.init()

#WINDOW
WIDTH, HEIGHT = 1200, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()

#COLORS
BG = (30, 30, 30)
PLAYER_COLOR = (0, 200, 255)
PLATFORM_COLOR = (255, 80, 80)
COIN_COLOR = (255, 215, 0)
WHITE = (240, 240, 240)

# CROUCHING
normal_height = 50
crouch_height = 30
is_crouching = False

#PLAYER
square_size = 50
square_x = 50
square_y = 100
speed = 5
run_speed = 7
y_velocity = 0
gravity = 0.6
jump_strength = -15
on_ground = False

#PLATFORMS
# Each platform is a rectangle: x, y, width, height
ground = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)

# Ground
ground_y = HEIGHT - 90

platforms = [
    pygame.Rect(600, 200, 170, 20),
    pygame.Rect(400, 300, 150, 20),
    pygame.Rect(400, random.randint(100, 200), 150, 20),
    pygame.Rect(random.randint(200, 700), random.randint(220, 500), 150, 20),
    pygame.Rect(random.randint(100, 500), random.randint(120, 500), random.randint(100, 200), 20),
    pygame.Rect(650, 200, 150, 20)
]

coins = []
coin_timers = []  # stores when coins should respawn
COIN_SIZE = 20
RESPAWN_TIME = 10000 
MAX_COINS = 5

score = 0
font = pygame.font.SysFont(None, 36)

def spawn_coin():
    platform = random.choice(platforms)  # pick random platform
    
    x = random.randint(platform.left, platform.right - COIN_SIZE)
    y = platform.top - COIN_SIZE  # place on top of platform

    return pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)

for _ in range(3):  # start with 3 coins
    coins.append(spawn_coin())
#GAME LOOP 
while True:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Jump when pressing SPACE
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False

    # MOVEMENT
    keys = pygame.key.get_pressed() 
    if keys[pygame.K_a]: square_x -= run_speed 
    if keys[pygame.K_d]: square_x += run_speed 

    # GRAVITY
    y_velocity += gravity
    square_y += y_velocity

    # Create player rectangle (IMPORTANT)
    player = pygame.Rect(square_x, square_y, square_size, square_size)

    # Assume player is NOT on ground until proven otherwise
    on_ground = True

    # PLATFORM COLLISION 
    for platform in [ground] + platforms:
        if player.colliderect(platform):
            # Falling = land on top
            if y_velocity > 0 and player.bottom <= platform.top + 10:
                square_y = platform.top - square_size
                y_velocity = 0
                on_ground = True

            # Jumping = hit underside
            elif y_velocity < 0 and player.top >= platform.bottom - 10:
                square_y = platform.bottom
                y_velocity = 0
        # Collision with ground
    if square_y + square_size >= ground_y:
        square_y = ground_y - square_size
        y_velocity = 0
        on_ground = True


    # Update player rect again after position fixes
    player = pygame.Rect(square_x, square_y, square_size, square_size)

    current_time = pygame.time.get_ticks()

    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1
        
        # set respawn timer
        coin_timers.append(current_time + RESPAWN_TIME)

    for timer in coin_timers[:]:
        if current_time >= timer:
            if len(coins) < MAX_COINS:
                coins.append(spawn_coin())
            coin_timers.remove(timer)

    if len(coins) + len(coin_timers) < MAX_COINS:
        coin_timers.append(current_time + RESPAWN_TIME)

    # KEEP PLAYER ON SCREEN
    square_x = max(0, min(WIDTH - square_size, square_x))

    # DRAWING 
    screen.fill(BG)

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, platform)

    # Draw coins
    for coin in coins:
        pygame.draw.rect(screen, COIN_COLOR, coin)

    pygame.draw.rect(screen, WHITE, ground)

    # Draw player
    pygame.draw.rect(screen, PLAYER_COLOR, player)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

        # Ground
    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))

    pygame.display.flip()
    clock.tick(60)