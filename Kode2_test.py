import pygame
import random
import math
import sys
 
pygame.init()
 
# --- Skjerm ---
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival - Impossible Mode")
 
clock = pygame.time.Clock()
 
# --- Farger ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
 
# --- Spiller ---
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5
player_hp = 60
player_max_hp = 60
coins = 0
 
# --- Fiender ---
enemies = []  # [x, y, hp, is_boss]
enemy_speed = 4.5
wave = 1
spawn_amount = 15
LAST_WAVE = 10
 
# --- Skudd ---
bullets = []
bullet_speed = 10
damage = 20
shoot_cooldown = 0
shoot_delay = 150
 
# --- Shop ---
shop_open = False
font = pygame.font.SysFont(None, 30)
 
 
# ---------------------------------------------------------
#   FIENDER SPACER (ikke tett sammen)
# ---------------------------------------------------------
def spawn_enemy_with_spacing(hp, is_boss):
    MIN_DIST = 80 if not is_boss else 150
 
    while True:
        x = random.choice([0, WIDTH])
        y = random.randint(0, HEIGHT)
 
        too_close = False
        for e in enemies:
            if math.hypot(x - e[0], y - e[1]) < MIN_DIST:
                too_close = True
                break
 
        if not too_close:
            enemies.append([x, y, hp, is_boss])
            return
 
 
# ---------------------------------------------------------
#   WAVE-SPAWN
# ---------------------------------------------------------
def spawn_wave():
    global enemies, spawn_amount, wave
 
    # Vanlige fiender
    for i in range(spawn_amount):
        spawn_enemy_with_spacing(60, False)
 
    # Bosser (Impossible = mange)
    boss_count = min(3 + wave, 10)
    boss_hp = 300 + wave * 40
 
    for i in range(boss_count):
        spawn_enemy_with_spacing(boss_hp, True)
 
    spawn_amount += 4
 
 
# ---------------------------------------------------------
#   HUD / SHOP
# ---------------------------------------------------------
def draw_hp_bar():
    pygame.draw.rect(screen, RED, (20, 20, 200, 20))
    pygame.draw.rect(screen, GREEN, (20, 20, 200 * (player_hp / player_max_hp), 20))
 
 
def draw_shop():
    pygame.draw.rect(screen, BLACK, (200, 100, 500, 400))
    pygame.draw.rect(screen, WHITE, (200, 100, 500, 400), 4)
 
    screen.blit(font.render("SHOP", True, WHITE), (420, 120))
    screen.blit(font.render("1: +20 HP (20 coins)", True, WHITE), (250, 200))
    screen.blit(font.render("2: +10 Damage (30 coins)", True, WHITE), (250, 250))
    screen.blit(font.render("3: Speed +1 (40 coins)", True, WHITE), (250, 300))
    screen.blit(font.render("Press ESC to exit", True, WHITE), (250, 350))
 
 
# ---------------------------------------------------------
#   FIENDE-LOGIKK
# ---------------------------------------------------------
def enemy_follow_player(enemy):
    ex, ey, hp, is_boss = enemy
    dx = player_pos[0] - ex
    dy = player_pos[1] - ey
    dist = math.hypot(dx, dy)
    if dist != 0:
        speed = enemy_speed + (1.5 if is_boss else 0)
        ex += speed * dx / dist
        ey += speed * dy / dist
    return [ex, ey, hp, is_boss]
 
 
# ---------------------------------------------------------
#   START SPILL
# ---------------------------------------------------------
spawn_wave()
running = True
victory = False
 
# ---------------------------------------------------------
#   HOVEDSPILL LOOP
# ---------------------------------------------------------
while running:
    dt = clock.tick(60)
    shoot_cooldown -= dt
    screen.fill((30, 30, 30))
 
    shop_button = pygame.Rect(20, 120, 160, 40)
 
    keys = pygame.key.get_pressed()
    if not shop_open and not victory:
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
 
        # --- Victory ---
        if victory:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Restart Impossible mode
                player_pos = [WIDTH // 2, HEIGHT // 2]
                player_hp = 60
                coins = 0
                enemies = []
                bullets = []
                wave = 1
                spawn_amount = 15
                shoot_cooldown = 0
                victory = False
                spawn_wave()
            continue
 
        # --- Shop-knapp ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if shop_button.collidepoint(mx, my):
                shop_open = True
 
        # --- Shop kjøp ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: shop_open = True
            if event.key == pygame.K_ESCAPE: shop_open = False
 
            if shop_open:
                if event.key == pygame.K_1 and coins >= 20:
                    player_hp = min(player_max_hp, player_hp + 20); coins -= 20
                if event.key == pygame.K_2 and coins >= 30:
                    damage += 10; coins -= 30
                if event.key == pygame.K_3 and coins >= 40:
                    player_speed += 1; coins -= 40
 
    # --- Shop visning ---
    if shop_open:
        draw_shop()
        pygame.display.update()
        continue
 
    # --- Victory ---
    if victory:
        screen.blit(font.render("DU VANT! Klarte wave 10! Trykk R for restart", True, YELLOW), (150, 280))
        pygame.display.update()
        continue
 
    # --- Skyting med cooldown ---
    if pygame.mouse.get_pressed()[0] and shoot_cooldown <= 0:
        mx, my = pygame.mouse.get_pos()
        dx = mx - player_pos[0]
        dy = my - player_pos[1]
        dist = math.hypot(dx, dy)
        if dist != 0:
            bullets.append([player_pos[0], player_pos[1], dx / dist, dy / dist])
            shoot_cooldown = shoot_delay
 
    # --- Oppdater skudd ---
    for b in bullets:
        b[0] += b[2] * bullet_speed
        b[1] += b[3] * bullet_speed
 
    # --- Kollisjon skudd-fiende ---
    for b in bullets[:]:
        for e in enemies[:]:
            ex, ey, ehp, is_boss = e
            radius = 25 if is_boss else 15
            if math.hypot(b[0] - ex, b[1] - ey) < radius:
                ehp -= damage
                bullets.remove(b)
                if ehp <= 0:
                    enemies.remove(e)
                    coins += 20 if is_boss else 5
                else:
                    e[2] = ehp
                break
 
    # --- Oppdater fiender ---
    for i in range(len(enemies)):
        enemies[i] = enemy_follow_player(enemies[i])
 
    # --- Kollisjon fiende-spiller ---
    for e in enemies:
        ex, ey, ehp, is_boss = e
        if math.hypot(ex - player_pos[0], ey - player_pos[1]) < (30 if is_boss else 20):
            player_hp -= 1.0 if is_boss else 0.5
 
    # --- Tegning ---
    pygame.draw.circle(screen, WHITE, (int(player_pos[0]), int(player_pos[1])), 20)
 
    for e in enemies:
        ex, ey, ehp, is_boss = e
        pygame.draw.circle(screen, YELLOW if is_boss else RED, (int(ex), int(ey)), 25 if is_boss else 15)
 
    for b in bullets:
        pygame.draw.circle(screen, GREEN, (int(b[0]), int(b[1])), 5)
 
    draw_hp_bar()
 
    screen.blit(font.render(f"Coins: {coins}", True, WHITE), (20, 50))
    screen.blit(font.render(f"Wave: {wave}", True, WHITE), (20, 80))
 
    pygame.draw.rect(screen, (50, 50, 50), shop_button)
    pygame.draw.rect(screen, WHITE, shop_button, 3)
    screen.blit(font.render("OPEN SHOP (E)", True, WHITE), (25, 130))
 
    # --- Død ---
    if player_hp <= 0:
        screen.blit(font.render("DU DØDE! Trykk R for restart", True, WHITE), (250, 300))
        pygame.display.update()
 
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False; running = False
 
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Restart Impossible mode
                    player_pos = [WIDTH // 2, HEIGHT // 2]
                    player_hp = 60
                    coins = 0
                    enemies = []
                    bullets = []
                    wave = 1
                    spawn_amount = 15
                    shoot_cooldown = 0
                    waiting = False
                    spawn_wave()
 
    # --- Wave ferdig ---
    if len(enemies) == 0 and not victory:
        if wave >= LAST_WAVE:
            victory = True
        else:
            wave += 1
            spawn_wave()
 
    pygame.display.update()
 
pygame.quit()