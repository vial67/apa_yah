"""
Game "Pac-Man Tosca" — replika tampilan dari screenshot
=========================================================
- Background tosca/teal
- Dinding berbentuk SILANG (+) seperti stik es krim
- 1 hantu biru di kiri, 2 hantu hijau (army) di kanan
- Pac-Man kuning di kanan bawah, bisa digerakkan pemain
- Pac-Man harus mengambil semua "koin" tanpa nabrak hantu / dinding

Instalasi:
    pip install pygame

Jalankan:
    python pacman_cross_game.py

Kontrol: Panah (Arrow Keys) atau WASD
Tekan R untuk main ulang setelah menang / kalah
"""

import pygame
import math
import random
import sys

pygame.init()

# ================= KONFIGURASI LAYAR =================
WIDTH, HEIGHT = 820, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pygame window")
clock = pygame.time.Clock()
FPS = 60

# ================= WARNA (meniru screenshot) =================
TEAL_BG = (117, 209, 214)          # background tosca
STICK_COLOR = (238, 238, 232)      # warna stik es krim (putih gading)
STICK_SHADE = (205, 205, 198)      # garis bayangan di stik
BLUE_GHOST = (46, 74, 214)
GREEN_GHOST = (109, 130, 92)       # hijau army
GHOST_EYE_BG = (30, 30, 30)
GHOST_PUPIL = (200, 20, 20)
YELLOW = (255, 213, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COIN_COLOR = (255, 230, 120)

font = pygame.font.SysFont("arial", 26, bold=True)
big_font = pygame.font.SysFont("arial", 46, bold=True)

# ================= DINDING BENTUK SILANG (+) =================
# Meniru posisi di gambar: satu stik horizontal panjang + satu stik vertikal panjang
CROSS_CENTER = (430, 470)
H_STICK = pygame.Rect(0, 0, 340, 38)   # horizontal
V_STICK = pygame.Rect(0, 0, 38, 340)   # vertical
H_STICK.center = CROSS_CENTER
V_STICK.center = CROSS_CENTER

WALL_RECTS = [H_STICK, V_STICK]


def draw_stick(surface, rect):
    """Gambar satu 'stik es krim' dengan sudut membulat + garis tekstur."""
    pygame.draw.rect(surface, STICK_COLOR, rect, border_radius=14)
    pygame.draw.rect(surface, STICK_SHADE, rect, width=2, border_radius=14)
    # garis tekstur kayu (horizontal kalau stick lebih lebar dari tinggi)
    if rect.width > rect.height:
        for i in range(3):
            y = rect.top + rect.height * (i + 1) / 4
            pygame.draw.line(surface, STICK_SHADE, (rect.left + 10, y), (rect.right - 10, y), 1)
    else:
        for i in range(3):
            x = rect.left + rect.width * (i + 1) / 4
            pygame.draw.line(surface, STICK_SHADE, (x, rect.top + 10), (x, rect.bottom - 10), 1)


def draw_walls(surface):
    for r in WALL_RECTS:
        draw_stick(surface, r)


def rect_blocks(cx, cy, radius):
    """Cek apakah lingkaran (cx, cy, radius) menabrak salah satu dinding."""
    for r in WALL_RECTS:
        closest_x = max(r.left, min(cx, r.right))
        closest_y = max(r.top, min(cy, r.bottom))
        dist = math.hypot(cx - closest_x, cy - closest_y)
        if dist < radius:
            return True
    return False


# ================= GHOST =================
class Ghost:
    def __init__(self, x, y, body_color, speed=1.6):
        self.x, self.y = x, y
        self.radius = 34
        self.color = body_color
        self.speed = speed
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.change_timer = random.randint(30, 90)

    def update(self):
        self.change_timer -= 1
        if self.change_timer <= 0 or random.random() < 0.01:
            self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.change_timer = random.randint(40, 100)

        nx = self.x + self.dir[0] * self.speed
        ny = self.y + self.dir[1] * self.speed

        # pantul dari tepi layar
        if nx < 40 or nx > WIDTH - 40:
            self.dir = (-self.dir[0], self.dir[1])
            nx = self.x + self.dir[0] * self.speed
        if ny < 100 or ny > HEIGHT - 40:
            self.dir = (self.dir[0], -self.dir[1])
            ny = self.y + self.dir[1] * self.speed

        # pantul dari dinding
        if rect_blocks(nx, ny, self.radius):
            self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        else:
            self.x, self.y = nx, ny

    def draw(self, surface):
        r = self.radius
        cx, cy = int(self.x), int(self.y)

        # badan (setengah lingkaran atas + gerigi bawah)
        body_rect = pygame.Rect(cx - r, cy - r, r * 2, int(r * 1.6))
        pygame.draw.ellipse(surface, self.color, body_rect)
        pygame.draw.rect(surface, self.color, (cx - r, cy, r * 2, int(r * 0.7)))

        # gerigi bawah (ombak)
        wave_y = cy + int(r * 0.7)
        n_waves = 4
        seg = (r * 2) / n_waves
        points = [(cx - r, wave_y)]
        for i in range(n_waves):
            x0 = cx - r + seg * i
            xm = x0 + seg / 2
            x1 = x0 + seg
            points.append((xm, wave_y + 10))
            points.append((x1, wave_y))
        points.append((cx + r, cy))
        points.append((cx - r, cy))
        pygame.draw.polygon(surface, self.color, points)

        # mata
        eye_r = int(r * 0.32)
        for dx in (-1, 1):
            ex = cx + dx * int(r * 0.4)
            ey = cy - int(r * 0.15)
            pygame.draw.circle(surface, WHITE, (ex, ey), eye_r)
            pygame.draw.circle(surface, GHOST_PUPIL, (ex, ey), int(eye_r * 0.55))
            pygame.draw.circle(surface, BLACK, (ex, ey), int(eye_r * 0.2))

        # "headset"/antena kecil biar mirip gambar (opsional dekorasi)
        pygame.draw.line(surface, (40, 40, 40), (cx, cy - r), (cx, cy - r - 10), 3)


# ================= PAC-MAN =================
class PacMan:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 32
        self.speed = 4
        self.mouth_angle = 35
        self.mouth_dir = 1
        self.facing = 0  # derajat: 0=kanan,90=atas,180=kiri,270=bawah

    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            self.facing = 180
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            self.facing = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            self.facing = 90
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            self.facing = 270

        nx = self.x + dx * self.speed
        ny = self.y + dy * self.speed
        nx = max(self.radius, min(WIDTH - self.radius, nx))
        ny = max(100 + self.radius, min(HEIGHT - self.radius, ny))

        if not rect_blocks(nx, self.y, self.radius):
            self.x = nx
        if not rect_blocks(self.x, ny, self.radius):
            self.y = ny

        if dx != 0 or dy != 0:
            self.mouth_angle += self.mouth_dir * 4
            if self.mouth_angle > 40 or self.mouth_angle < 5:
                self.mouth_dir *= -1

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = self.radius
        a1 = math.radians(self.facing + self.mouth_angle)
        a2 = math.radians(self.facing - self.mouth_angle)
        p1 = (cx, cy)
        p2 = (cx + r * math.cos(a1), cy - r * math.sin(a1))
        p3 = (cx + r * math.cos(a2), cy - r * math.sin(a2))
        pygame.draw.circle(surface, YELLOW, (cx, cy), r)
        pygame.draw.polygon(surface, TEAL_BG, [p1, p2, p3])
        # mata kecil pacman
        eye_angle = math.radians(self.facing + 90)
        ex = cx + (r * 0.4) * math.cos(eye_angle)
        ey = cy - (r * 0.4) * math.sin(eye_angle) - r * 0.35
        pygame.draw.circle(surface, BLACK, (int(ex), int(ey)), 3)


# ================= KOIN (pengganti dot) =================
def make_coins():
    coins = []
    for gx in range(80, WIDTH - 80, 70):
        for gy in range(120, HEIGHT - 60, 70):
            cx, cy = gx, gy
            if rect_blocks(cx, cy, 25):
                continue
            coins.append([cx, cy])
    return coins


# ================= SETUP OBJEK (posisi meniru screenshot) =================
pacman = PacMan(WIDTH - 90, HEIGHT - 90)          # kanan bawah
ghosts = [
    Ghost(90, 410, BLUE_GHOST, speed=1.8),         # hantu biru, kiri
    Ghost(680, 380, GREEN_GHOST, speed=1.4),       # hantu hijau atas-kanan
    Ghost(680, 470, GREEN_GHOST, speed=1.4),       # hantu hijau bawah-kanan
]
coins = make_coins()
score = 0
lives = 3
game_over = False
win = False


def reset_game():
    global pacman, ghosts, coins, score, lives, game_over, win
    pacman = PacMan(WIDTH - 90, HEIGHT - 90)
    ghosts = [
        Ghost(90, 410, BLUE_GHOST, speed=1.8),
        Ghost(680, 380, GREEN_GHOST, speed=1.4),
        Ghost(680, 470, GREEN_GHOST, speed=1.4),
    ]
    coins = make_coins()
    score = 0
    lives = 3
    game_over = False
    win = False


def draw_hud(surface):
    pygame.draw.rect(surface, (20, 20, 20), (0, 0, WIDTH, 60))
    surface.blit(font.render(f"Skor: {score}", True, WHITE), (15, 16))
    surface.blit(font.render(f"Nyawa: {lives}", True, WHITE), (WIDTH - 150, 16))


# ================= GAME LOOP =================
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game_over or win):
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over and not win:
        pacman.update(keys)
        for g in ghosts:
            g.update()

        # ambil koin
        for c in coins[:]:
            if math.hypot(pacman.x - c[0], pacman.y - c[1]) < pacman.radius:
                coins.remove(c)
                score += 10

        if not coins:
            win = True

        # tabrakan dengan hantu
        for g in ghosts:
            if math.hypot(pacman.x - g.x, pacman.y - g.y) < pacman.radius + g.radius - 10:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    pacman.x, pacman.y = WIDTH - 90, HEIGHT - 90
                break

    # ================= GAMBAR =================
    screen.fill(TEAL_BG)
    draw_walls(screen)

    for c in coins:
        pygame.draw.circle(screen, COIN_COLOR, (int(c[0]), int(c[1])), 6)
        pygame.draw.circle(screen, (180, 150, 40), (int(c[0]), int(c[1])), 6, 1)

    for g in ghosts:
        g.draw(screen)
    pacman.draw(screen)

    draw_hud(screen)

    if game_over:
        t = big_font.render("GAME OVER", True, (220, 30, 30))
        s = font.render("Tekan R untuk main lagi", True, WHITE)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 30))
    elif win:
        t = big_font.render("KAMU MENANG!", True, (20, 160, 60))
        s = font.render("Tekan R untuk main lagi", True, WHITE)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
