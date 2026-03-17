import pygame
import random
import math
import sys
 
pygame.init()
 
# --- Skjerm ---
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival")
 
clock = pygame.time.Clock()
 
# --- Farger ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
 
# --- Spiller ---
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 8
player_hp = 100
player_max_hp = 100
coins = 0
 
# --- Fiender ---
enemies = []  # [x, y, hp, is_boss]
enemy_speed = 2
wave = 1
spawn_amount = 6
LAST_WAVE = 10   # <--- Wave stopper på 10
 
# --- Skudd ---
bullets = []  # [x, y, dx, dy]
bullet_speed = 10
damage = 20
shoot_cooldown = 0
shoot_delay = 150  # millisekunder mellom skudd
 
# --- Shop ---
shop_open = False
font = pygame.font.SysFont(None, 30)
 
# --- Meny / vanskelighet ---
difficulty = None
menu = True
 
 
def draw_menu():
    screen.fill((20, 20, 20))
 
    title = font.render("WAVE SURVIVAL", True, WHITE)
    screen.blit(title, (WIDTH // 2 - 120, 100))
 
    easy_btn = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)
    hard_btn = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
    imp_btn = pygame.Rect(WIDTH // 2 - 100, 400, 200, 50)
 
    pygame.draw.rect(screen, (50, 150, 50), easy_btn)
    pygame.draw.rect(screen, (150, 50, 50), hard_btn)
    pygame.draw.rect(screen, (150, 0, 150), imp_btn)
 
    screen.blit(font.render("EASY", True, WHITE), (WIDTH // 2 - 30, 215))
    screen.blit(font.render("HARD", True, WHITE), (WIDTH // 2 - 30, 315))
    screen.blit(font.render("IMPOSSIBLE", True, WHITE), (WIDTH // 2 - 60, 415))
 
    return easy_btn, hard_btn, imp_btn
 
 
def apply_difficulty(level):
    global enemy_speed, spawn_amount, player_hp, player_max_hp
 
    if level == "easy":
        enemy_speed = 1.5
        spawn_amount = 4
        player_hp = 150
        player_max_hp = 150
 
    elif level == "hard":
        enemy_speed = 2.8
        spawn_amount = 8
        player_hp = 100
        player_max_hp = 100
 
    elif level == "impossible":
        enemy_speed = 4.5       # Raskere fiender
        spawn_amount = 15       # Flere fiender
        player_hp = 60          # Mindre HP
        player_max_hp = 60
 
 
def spawn_wave():
    global enemies, spawn_amount, wave, difficulty
 
    # Vanlige fiender
    for i in range(spawn_amount):
        x = random.choice([0, WIDTH])
        y = random.randint(0, HEIGHT)
        enemies.append([x, y, 60, False])
 
    # Bosser
    if difficulty == "impossible":
        boss_count = min(3 + wave, 10)
        boss_hp = 300 + wave * 40
    else:
        boss_count = min(1 + wave // 2, 5)
        boss_hp = 200 + wave * 20
 
    for i in range(boss_count):
        x = random.choice([0, WIDTH])
        y = random.randint(0, HEIGHT)
        enemies.append([x, y, boss_hp, True])
 
    spawn_amount += 3
 
 
def draw_hp_bar():
    pygame.draw.rect(screen, RED, (20, 20, 200, 20))
    pygame.draw.rect(screen, GREEN, (20, 20, 200 * (player_hp / player_max_hp), 20))
 
 
def draw_shop():
    pygame.draw.rect(screen, BLACK, (200, 100, 500, 400))
    pygame.draw.rect(screen, WHITE, (200, 100, 500, 400), 4)
 
    title = font.render("SHOP", True, WHITE)
    hp_text = font.render("1: +20 HP (20 coins)", True, WHITE)
    dmg_text = font.render("2: +10 Damage (30 coins)", True, WHITE)
    spd_text = font.render("3: Speed +1 (40 coins)", True, WHITE)
    exit_text = font.render("Press ESC to exit", True, WHITE)
 
    screen.blit(title, (420, 120))
    screen.blit(hp_text, (250, 200))
    screen.blit(dmg_text, (250, 250))
    screen.blit(spd_text, (250, 300))
    screen.blit(exit_text, (250, 350))
 
 
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
 
 
running = True
victory = False
 
# --- STARTMENY LOOP ---
while menu:
    clock.tick(60)
    easy_btn, hard_btn, imp_btn = draw_menu()
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
 
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
 
            if easy_btn.collidepoint(mx, my):
                difficulty = "easy"
                apply_difficulty("easy")
                menu = False
 
            elif hard_btn.collidepoint(mx, my):
                difficulty = "hard"
                apply_difficulty("hard")
                menu = False
 
            elif imp_btn.collidepoint(mx, my):
                difficulty = "impossible"
                apply_difficulty("impossible")
                menu = False
 
    pygame.display.update()
 
# Start wave 1
spawn_wave()
 
# --- HOVEDSPILL LOOP ---
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
 
        if victory:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                menu = True
                victory = False
 
                # Reset alt
                player_pos = [WIDTH // 2, HEIGHT // 2]
                coins = 0
                enemies = []
                bullets = []
                wave = 1
                spawn_amount = 6
                shoot_cooldown = 0
 
                # Tilbake til meny
                while menu:
                    clock.tick(60)
                    easy_btn, hard_btn, imp_btn = draw_menu()
 
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
 
                        if e.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = pygame.mouse.get_pos()
 
                            if easy_btn.collidepoint(mx, my):
                                difficulty = "easy"
                                apply_difficulty("easy")
                                menu = False
 
                            elif hard_btn.collidepoint(mx, my):
                                difficulty = "hard"
                                apply_difficulty("hard")
                                menu = False
 
                            elif imp_btn.collidepoint(mx, my):
                                difficulty = "impossible"
                                apply_difficulty("impossible")
                                menu = False
 
                    pygame.display.update()
 
                spawn_wave()
            continue
 
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if shop_button.collidepoint(mx, my):
                shop_open = True
 
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
 
    if shop_open:
        draw_shop()
        pygame.display.update()
        continue
 
    if victory:
        win_text = font.render("DU VANT! Klarte wave 10! Trykk R for meny", True, YELLOW)
        screen.blit(win_text, (150, 280))
        pygame.display.update()
        continue
 
    # --- SKYTING MED COOLDOWN ---
    if not shop_open:
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
        screen.blit(font.render("DU DØDE! Trykk R for meny", True, WHITE), (250, 300))
        pygame.display.update()
 
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False; running = False
 
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    menu = True
                    waiting = False
 
                    # Reset alt
                    player_pos = [WIDTH // 2, HEIGHT // 2]
                    coins = 0
                    enemies = []
                    bullets = []
                    wave = 1
                    spawn_amount = 6
                    shoot_cooldown = 0
 
                    # Tilbake til meny
                    while menu:
                        clock.tick(60)
                        easy_btn, hard_btn, imp_btn = draw_menu()
 
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
 
                            if e.type == pygame.MOUSEBUTTONDOWN:
                                mx, my = pygame.mouse.get_pos()
 
                                if easy_btn.collidepoint(mx, my):
                                    difficulty = "easy"
                                    apply_difficulty("easy")
                                    menu = False
 
                                elif hard_btn.collidepoint(mx, my):
                                    difficulty = "hard"
                                    apply_difficulty("hard")
                                    menu = False
 
                                elif imp_btn.collidepoint(mx, my):
                                    difficulty = "impossible"
                                    apply_difficulty("impossible")
                                    menu = False
 
                        pygame.display.update()
 
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
 