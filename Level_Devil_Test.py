import pygame
import random
import sys

pygame.init()

#  WINDOW 
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Level Devil Clone")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

#  COLORS 
BG = (30, 30, 30)
PLAYER_COLOR = (0, 200, 205)
COIN_COLOR = (255, 215, 0)
SPIKE_COLOR = (255, 50, 50)

# PLAYER 
player = pygame.Rect(100, 400, 40, 40)
vel_y = 0
gravity = 0.5
jump_power = -15
on_ground = False

#  GAME DATA 
platforms = []
coins = []
spikes = []

camera_x = 0
death_count = 0
coins_collected = 0

# SETTINGS 
SPAWN_DISTANCE = 600
DELETE_DISTANCE = 300
difficulty = 1

button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)

#  FUNCTIONS 

def reset_player():
    global vel_y
    player.x = 100
    player.y = 300
    vel_y = 0


def generate_platform(x):
    y = random.randint(300, 550)

    r = random.random()
    if r < 0.6:
        plat_type = "normal"
    elif r < 0.8:
        plat_type = "moving"
    else:
        plat_type = "fake"

    return {
        "rect": pygame.Rect(x, y, random.randint(100, 180), 20),
        "type": plat_type,
        "dir": random.choice([-1, 1]),
        "speed": random.randint(2, 4),
        "falling": False,
        "start_x": x  #  for moving platforms to know their original position
    }


def generate_coin(plat_rect):
    return pygame.Rect(
        plat_rect.x + plat_rect.width // 2,
        plat_rect.y - 30,
        20, 20
    )


def generate_spike(plat_rect):
    return pygame.Rect(
        plat_rect.x + random.randint(0, plat_rect.width - 40),
        plat_rect.y - 40,
        40, 40
    )


def restart_game():
    global platforms, coins, spikes, last_platform_x, difficulty

    coins.clear()
    spikes.clear()
    platforms.clear()

    # SAFE START
    for i in range(3):
        platforms.append({
            "rect": pygame.Rect(i * 180, 500, 150, 20),
            "type": "normal",
            "dir": 0,
            "speed": 0,
            "falling": False,
            "start_x": i * 180
        })

    for i in range(3, 5):
        platforms.append(generate_platform(i * 200))

    last_platform_x = platforms[-1]["rect"].x
    difficulty = 1
    reset_player()


# INITIAL SETUP
restart_game()

#  GAME LOOP 
while True:
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # MOVEMENT 
    if keys[pygame.K_a]:
        player.x -= 5
    if keys[pygame.K_d]:
        player.x += 5
    if keys[pygame.K_SPACE] and on_ground:
        vel_y = jump_power

    #  GRAVITY 
    vel_y += gravity
    player.y += vel_y
    on_ground = False

    #  COLLISION 
    for plat in platforms:
        rect = plat["rect"]

        if player.colliderect(rect) and vel_y > 0:
            player.bottom = rect.top
            vel_y = 0
            on_ground = True

            if plat["type"] == "fake":
                plat["falling"] = True

            if plat["type"] == "moving":
                player.x += plat["dir"] * plat["speed"]

    #  CAMERA 
    camera_x = player.x - 200

    # GENERATION
    while last_platform_x < player.x + SPAWN_DISTANCE:
        gap = random.randint(120, 220)
        new_x = last_platform_x + gap

        new_plat = generate_platform(new_x)
        platforms.append(new_plat)
        last_platform_x = new_plat["rect"].x

        difficulty += 0.02

        if random.random() < 0.7:
            coins.append(generate_coin(new_plat["rect"]))

        if random.random() < min(0.3 + difficulty * 0.01, 0.7):
            spikes.append(generate_spike(new_plat["rect"]))

    #  CLEAN 
    platforms = [p for p in platforms if p["rect"].x > player.x - DELETE_DISTANCE]
    coins = [c for c in coins if c.x > player.x - DELETE_DISTANCE]
    spikes = [s for s in spikes if s.x > player.x - DELETE_DISTANCE]

    #  PLATFORM BEHAVIOR
    for plat in platforms:
        rect = plat["rect"]

        if plat["type"] == "moving":
            rect.x += plat["dir"] * plat["speed"]

            #  FIXED MOVEMENT RANGE
            if abs(rect.x - plat["start_x"]) > 100:
                plat["dir"] *= -1

        if plat["type"] == "fake" and plat["falling"]:
            rect.y += 8

    #  COINS 
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            coins_collected += 1

    #  DEATH 
    died = False
    for spike in spikes:
        if player.colliderect(spike):
            died = True

    if player.y > HEIGHT:
        died = True

    if died:
        death_count += 1

        waiting = True
        while waiting:
            screen.fill(BG)

            text = font.render("YOU DIED", True, (255, 0, 0))
            screen.blit(text, (WIDTH//2 - 120, HEIGHT//2 - 50))

            pygame.draw.rect(screen, (100, 200, 100), button_rect)
            btn_text = font.render("RESTART", True, (0, 0, 0))
            screen.blit(btn_text, (button_rect.x + 20, button_rect.y + 10))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        restart_game()
                        waiting = False

    #  DRAW 
    pygame.draw.rect(screen, PLAYER_COLOR,
                     (player.x - camera_x, player.y, 40, 40))

    for plat in platforms:
        rect = plat["rect"]

        if plat["type"] == "normal":
            color = (200, 200, 200)
        elif plat["type"] == "moving":
            color = (200, 200, 200)
        else:
            color = (200, 200, 200)

        pygame.draw.rect(screen, color,
                         (rect.x - camera_x, rect.y, rect.width, rect.height))

    for coin in coins:
        pygame.draw.rect(screen, COIN_COLOR,
                         (coin.x - camera_x, coin.y, 20, 20))

    for spike in spikes:
        pygame.draw.rect(screen, SPIKE_COLOR,
                         (spike.x - camera_x, spike.y, 30, 30))

    death_text = font.render(f"Deaths: {death_count}", True, (255, 255, 255))
    coin_text = font.render(f"Coins: {coins_collected}", True, (255, 255, 0))

    screen.blit(death_text, (10, 10))
    screen.blit(coin_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)