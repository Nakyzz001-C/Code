import pygame
import sys
 
pygame.init()
 
# --- KONFIG ---
WIDTH, HEIGHT = 960, 540
FPS = 60
 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE  = (80, 80, 255)
GREY  = (80, 80, 80)
 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Swordsfight")
clock = pygame.time.Clock()
 
# --- LYD (kan byttes ut med ekte filer) ---
# pygame.mixer.music.load("music.ogg")
# pygame.mixer.music.play(-1)
# sword_sound = pygame.mixer.Sound("sword.wav")
# shoot_sound = pygame.mixer.Sound("shoot.wav")
sword_sound = None
shoot_sound = None
 
# --- MAPS (enkle plattformer) ---
MAPS = {
    "arena": [
        pygame.Rect(0, HEIGHT - 40, WIDTH, 40),          # gulv
    ],
    "parkour": [
        pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
        pygame.Rect(200, HEIGHT - 150, 150, 20),
        pygame.Rect(500, HEIGHT - 230, 150, 20),
        pygame.Rect(750, HEIGHT - 310, 150, 20),
    ],
    "mid_hole": [
        pygame.Rect(0, HEIGHT - 40, WIDTH // 3, 40),
        pygame.Rect(2 * WIDTH // 3, HEIGHT - 40, WIDTH // 3, 40),
        pygame.Rect(WIDTH // 3 + 40, HEIGHT - 140, WIDTH // 3 - 80, 20),
    ],
}
 
CURRENT_MAP_NAME = "parkour"  # bytt mellom "arena", "parkour", "mid_hole"
PLATFORMS = MAPS[CURRENT_MAP_NAME]
 
GRAVITY = 0.6
JUMP_FORCE = -12
MOVE_SPEED = 5
BULLET_SPEED = 10
MELEE_RANGE = 45
MELEE_DAMAGE = 15
BULLET_DAMAGE = 10
MAX_HP = 100
 
ULTIMATE_CHARGE_PER_HIT = 15
ULTIMATE_MAX = 100
ULTIMATE_DURATION = 180  # frames (ca 3 sek på 60 FPS)
 
 
class Bullet:
    def __init__(self, x, y, direction, owner):
        self.rect = pygame.Rect(x, y, 10, 4)
        self.direction = direction
        self.owner = owner
        self.alive = True
 
    def update(self):
        self.rect.x += BULLET_SPEED * self.direction
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.alive = False
 
    def draw(self, surf):
        pygame.draw.rect(surf, BLUE, self.rect)
 
 
class Player:
    def __init__(self, x, y, controls, color):
        self.rect = pygame.Rect(x, y, 30, 60)
        self.color = color
        self.controls = controls
 
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing = 1  # 1 = høyre, -1 = venstre
 
        self.hp = MAX_HP
        self.alive = True
 
        self.melee_cooldown = 0
        self.shoot_cooldown = 0
 
        self.ultimate_charge = 0
        self.ultimate_active = False
        self.ultimate_timer = 0
 
    def handle_input(self, keys):
        if not self.alive:
            return
 
        self.vel_x = 0
        if keys[self.controls["left"]]:
            self.vel_x = -MOVE_SPEED
            self.facing = -1
        if keys[self.controls["right"]]:
            self.vel_x = MOVE_SPEED
            self.facing = 1
 
        if keys[self.controls["jump"]] and self.on_ground:
            self.vel_y = JUMP_FORCE
 
    def try_melee(self, keys, opponent):
        if not self.alive:
            return
        if self.melee_cooldown > 0:
            return
        if keys[self.controls["melee"]]:
            self.melee_cooldown = 20  # ca 0.3 sek
            # sword_sound and sword_sound.play()
            # enkel hitbox foran spilleren
            if self.facing == 1:
                hitbox = pygame.Rect(self.rect.right, self.rect.centery - 10, MELEE_RANGE, 20)
            else:
                hitbox = pygame.Rect(self.rect.left - MELEE_RANGE, self.rect.centery - 10, MELEE_RANGE, 20)
 
            if hitbox.colliderect(opponent.rect) and opponent.alive:
                opponent.take_damage(MELEE_DAMAGE)
                self.gain_ultimate(ULTIMATE_CHARGE_PER_HIT)
 
    def try_shoot(self, keys, bullets):
        if not self.alive:
            return
        if self.shoot_cooldown > 0:
            return
        if keys[self.controls["shoot"]]:
            self.shoot_cooldown = 25
            # shoot_sound and shoot_sound.play()
            if self.facing == 1:
                bx = self.rect.right + 5
            else:
                bx = self.rect.left - 15
            by = self.rect.centery
            bullets.append(Bullet(bx, by, self.facing, self))
 
    def try_ultimate(self, keys):
        if not self.alive:
            return
        if self.ultimate_active:
            return
        if self.ultimate_charge >= ULTIMATE_MAX and keys[self.controls["ultimate"]]:
            self.ultimate_active = True
            self.ultimate_timer = ULTIMATE_DURATION
            # her kan du legge til effekter/lyd
            # f.eks. skjermshake, glow, osv.
 
    def gain_ultimate(self, amount):
        self.ultimate_charge = min(ULTIMATE_MAX, self.ultimate_charge + amount)
 
    def take_damage(self, amount):
        if self.ultimate_active:
            amount *= 0.5  # ultimate gir litt damage-reduction
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
 
    def apply_physics(self):
        self.vel_y += GRAVITY
        self.rect.x += self.vel_x
        self.collide_horizontal()
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide_vertical()
 
    def collide_horizontal(self):
        for plat in PLATFORMS:
            if self.rect.colliderect(plat):
                if self.vel_x > 0:
                    self.rect.right = plat.left
                elif self.vel_x < 0:
                    self.rect.left = plat.right
 
    def collide_vertical(self):
        for plat in PLATFORMS:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y = 0
 
        # faller ut av banen = KO
        if self.rect.top > HEIGHT + 100:
            self.alive = False
            self.hp = 0
 
    def update_ultimate_state(self):
        if self.ultimate_active:
            self.ultimate_timer -= 1
            if self.ultimate_timer <= 0:
                self.ultimate_active = False
                self.ultimate_charge = 0
 
    def update(self):
        if self.melee_cooldown > 0:
            self.melee_cooldown -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.apply_physics()
        self.update_ultimate_state()
 
    def draw(self, surf):
        # glow når ultimate er aktiv
        if self.ultimate_active:
            glow_rect = self.rect.inflate(20, 20)
            pygame.draw.rect(surf, (255, 255, 100), glow_rect, 2)
 
        # kropp
        pygame.draw.rect(surf, self.color, self.rect, 2)
        # enkel stickman
        cx = self.rect.centerx
        cy = self.rect.top + 15
        pygame.draw.circle(surf, self.color, (cx, cy), 10)  # hode
        pygame.draw.line(surf, self.color, (cx, cy + 10), (cx, self.rect.bottom - 10), 3)  # kropp
        pygame.draw.line(surf, self.color, (cx, self.rect.bottom - 10), (cx - 10, self.rect.bottom + 10), 3)
        pygame.draw.line(surf, self.color, (cx, self.rect.bottom - 10), (cx + 10, self.rect.bottom + 10), 3)
 
        # sverd (bare en linje)
        sword_len = 25
        if self.facing == 1:
            pygame.draw.line(surf, WHITE, (cx + 10, cy + 10), (cx + 10 + sword_len, cy), 3)
        else:
            pygame.draw.line(surf, WHITE, (cx - 10, cy + 10), (cx - 10 - sword_len, cy), 3)
 
 
def draw_platforms(surf):
    for plat in PLATFORMS:
        pygame.draw.rect(surf, GREY, plat)
 
 
def draw_hp_bar(surf, player, x, y, w, h, name):
    ratio = player.hp / MAX_HP
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2)
    pygame.draw.rect(surf, RED, (x + 2, y + 2, (w - 4) * ratio, h - 4))
    font = pygame.font.SysFont(None, 20)
    text = font.render(f"{name}: {player.hp}", True, WHITE)
    surf.blit(text, (x + 5, y + 2))
 
 
def draw_ultimate_bar(surf, player, x, y, w, h):
    ratio = player.ultimate_charge / ULTIMATE_MAX
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 1)
    pygame.draw.rect(surf, BLUE, (x + 2, y + 2, (w - 4) * ratio, h - 4))
 
 
def main():
    player1 = Player(150, HEIGHT - 200, {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
        "melee": pygame.K_f,
        "shoot": pygame.K_g,
        "ultimate": pygame.K_h,
    }, GREEN)
 
    player2 = Player(WIDTH - 180, HEIGHT - 200, {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "melee": pygame.K_KP1,   # numpad 1
        "shoot": pygame.K_KP2,   # numpad 2
        "ultimate": pygame.K_KP3 # numpad 3
    }, RED)
 
    bullets = []
    winner = None
    font_big = pygame.font.SysFont(None, 60)
    font_small = pygame.font.SysFont(None, 28)
 
    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
        if winner is None:
            # input
            player1.handle_input(keys)
            player2.handle_input(keys)
 
            player1.try_melee(keys, player2)
            player2.try_melee(keys, player1)
 
            player1.try_shoot(keys, bullets)
            player2.try_shoot(keys, bullets)
 
            player1.try_ultimate(keys)
            player2.try_ultimate(keys)
 
            # oppdater spillere
            player1.update()
            player2.update()
 
            # oppdater kuler
            for b in bullets:
                b.update()
                if b.alive and b.rect.colliderect(player1.rect) and b.owner is not player1 and player1.alive:
                    player1.take_damage(BULLET_DAMAGE)
                    b.alive = False
                    b.owner.gain_ultimate(ULTIMATE_CHARGE_PER_HIT)
                if b.alive and b.rect.colliderect(player2.rect) and b.owner is not player2 and player2.alive:
                    player2.take_damage(BULLET_DAMAGE)
                    b.alive = False
                    b.owner.gain_ultimate(ULTIMATE_CHARGE_PER_HIT)
 
            bullets = [b for b in bullets if b.alive]
 
            # sjekk vinner
            if not player1.alive and player2.alive:
                winner = "Spiller 2 vant!"
            elif not player2.alive and player1.alive:
                winner = "Spiller 1 vant!"
            elif not player1.alive and not player2.alive:
                winner = "Uavgjort!"
 
        # --- RENDER ---
        screen.fill(BLACK)
        draw_platforms(screen)
 
        for b in bullets:
            b.draw(screen)
 
        player1.draw(screen)
        player2.draw(screen)
 
        draw_hp_bar(screen, player1, 20, 20, 250, 20, "P1")
        draw_hp_bar(screen, player2, WIDTH - 270, 20, 250, 20, "P2")
 
        draw_ultimate_bar(screen, player1, 20, 50, 250, 10)
        draw_ultimate_bar(screen, player2, WIDTH - 270, 50, 250, 10)
 
        if winner:
            text = font_big.render(winner, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
            info = font_small.render("Trykk R for å restarte, ESC for å avslutte", True, WHITE)
            screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 20))
 
            if keys[pygame.K_r]:
                return main()
            if keys[pygame.K_ESCAPE]:
                running = False
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()