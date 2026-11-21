import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kawaii Bunny & Clover Meadow Simulator")
clock = pygame.time.Clock()

# Couleurs (Thème Prairie Nocturne & Pastel Doux)
BG_COLOR = (16, 20, 34)
MEADOW_DARK = (26, 46, 40)
MEADOW_LIGHT = (38, 66, 54)
CLOVER_GREEN = (92, 205, 128)
CLOVER_LIGHT = (155, 240, 175)
BUNNY_BODY = (245, 240, 250)
BUNNY_EAR_INNER = (255, 175, 205)
BUNNY_NOSE = (255, 130, 175)
TEXT_COLOR = (244, 246, 255)
GRAY = (132, 142, 168)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

class Clover:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.scale = 0.2
        self.target_scale = random.uniform(0.85, 1.2)
        self.sway = random.uniform(0, math.pi * 2)

    def update(self):
        self.sway += 0.05
        if self.scale < self.target_scale:
            self.scale = min(self.target_scale, self.scale + 0.03)

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        bend = int(math.sin(self.sway) * 2)
        r = max(3, int(5 * self.scale))

        # Petite tige
        pygame.draw.line(surface, CLOVER_GREEN, (ix, iy + 6), (ix + bend, iy - 2), 2)

        # Trois petites feuilles en trèfle
        top_y = iy - 4 + bend
        pygame.draw.circle(surface, CLOVER_GREEN, (ix + bend, top_y - r // 2), r)
        pygame.draw.circle(surface, CLOVER_LIGHT, (ix - r + bend, top_y + r // 2), r)
        pygame.draw.circle(surface, CLOVER_GREEN, (ix + r + bend, top_y + r // 2), r)

class Bunny:
    def __init__(self, x, y, color=(245, 240, 250)):
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.color = color
        self.facing_right = True
        self.hop_phase = 0.0
        self.is_hopping = False
        self.wait_timer = random.randint(35, 95)

    def pick_target(self, meadow_top, meadow_bottom):
        self.target_x = random.uniform(90, WIDTH - 90)
        self.target_y = random.uniform(meadow_top + 20, meadow_bottom - 12)

    def update(self, clovers, meadow_top, meadow_bottom):
        target_clover = None
        if clovers:
            target_clover = min(clovers, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))
            self.target_x, self.target_y = target_clover.x, target_clover.y
        else:
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                self.wait_timer = random.randint(50, 120)
                self.pick_target(meadow_top, meadow_bottom)

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 6:
            self.facing_right = dx >= 0
            speed = 1.65
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            self.is_hopping = True
            self.hop_phase += 0.24
        else:
            self.is_hopping = False
            self.hop_phase = 0.0

        # Cueillir / grignoter le trèfle atteint
        if target_clover and dist < 14:
            clovers.remove(target_clover)
            self.pick_target(meadow_top, meadow_bottom)

    def draw(self, surface):
        hop_height = abs(math.sin(self.hop_phase)) * 10 if self.is_hopping else 0
        cx = int(self.x)
        cy = int(self.y - hop_height)
        d = 1 if self.facing_right else -1

        # Ombre portée au sol
        shadow_w = max(10, int(26 - hop_height * 0.6))
        pygame.draw.ellipse(surface, (16, 28, 25), (cx - shadow_w // 2, int(self.y) + 6, shadow_w, 7))

        # Queue pompon
        pygame.draw.circle(surface, self.color, (cx - d * 15, cy + 2), 5)

        # Corps arrondi
        pygame.draw.ellipse(surface, self.color, (cx - 14, cy - 8, 28, 18))

        # Tête
        head_x = cx + d * 10
        head_y = cy - 9
        pygame.draw.circle(surface, self.color, (head_x, head_y), 9)

        # Deux longues oreilles
        ear_tilt = int(math.sin(self.hop_phase) * 2) if self.is_hopping else 0
        for offset in (-3, 3):
            ex = head_x + d * offset
            pygame.draw.ellipse(surface, self.color, (ex - 3, head_y - 18 + ear_tilt, 6, 13))
            pygame.draw.ellipse(surface, BUNNY_EAR_INNER, (ex - 1, head_y - 15 + ear_tilt, 2, 8))

        # Œil et petit nez rose
        pygame.draw.circle(surface, (28, 30, 42), (head_x + d * 4, head_y - 1), 2)
        pygame.draw.circle(surface, BUNNY_NOSE, (head_x + d * 8, head_y + 1), 2)

BUNNY_PALETTES = [
    (245, 240, 250),  # Blanc crème
    (255, 215, 230),  # Rose pastel
    (220, 205, 190),  # Beige doux
    (215, 225, 248)   # Bleu lavande pâle
]

meadow_top = HEIGHT - 185
meadow_bottom = HEIGHT - 30

bunnies = [Bunny(WIDTH // 2, HEIGHT - 105, BUNNY_PALETTES[0])]
clovers = [
    Clover(random.uniform(90, WIDTH - 90), random.uniform(meadow_top + 20, meadow_bottom - 12))
    for _ in range(10)
]
fireflies = [
    [random.uniform(30, WIDTH - 30), random.uniform(80, meadow_top - 10), random.uniform(0, math.pi * 2)]
    for _ in range(18)
]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mouse_pos[1] > 80:
                cy = max(meadow_top + 15, min(meadow_bottom - 10, mouse_pos[1]))
                clovers.append(Clover(mouse_pos[0], cy))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                if len(bunnies) < 6:
                    col = BUNNY_PALETTES[len(bunnies) % len(BUNNY_PALETTES)]
                    bx = random.uniform(100, WIDTH - 100)
                    by = random.uniform(meadow_top + 20, meadow_bottom - 12)
                    bunnies.append(Bunny(bx, by, col))
            elif event.key == pygame.K_r:
                bunnies = [Bunny(WIDTH // 2, HEIGHT - 105, BUNNY_PALETTES[0])]
                clovers = []

    # Mise à jour des trèfles
    for clover in clovers:
        clover.update()

    # Mise à jour des lapins
    for bunny in bunnies:
        bunny.update(clovers, meadow_top, meadow_bottom)

    # Mise à jour des petites lueurs flottantes dans le ciel
    for fly in fireflies:
        fly[2] += 0.04
        fly[0] = (fly[0] + math.cos(fly[2] * 0.7) * 0.4) % WIDTH
        fly[1] += math.sin(fly[2]) * 0.35
        fly[1] = max(80, min(meadow_top - 10, fly[1]))

    # --- RENDU GRAPHIQUE ---
    screen.fill(BG_COLOR)

    # Petites lueurs douces dans le ciel
    for fly in fireflies:
        glow = int(140 + math.sin(fly[2] * 2) * 90)
        pygame.draw.circle(screen, (glow, 245, 165), (int(fly[0]), int(fly[1])), 2)

    # Prairie en deux couches douces
    pygame.draw.rect(screen, MEADOW_DARK, (0, meadow_top, WIDTH, HEIGHT - meadow_top))
    pygame.draw.rect(screen, MEADOW_LIGHT, (0, meadow_top + 45, WIDTH, HEIGHT - meadow_top - 45))
    pygame.draw.line(screen, (72, 115, 92), (0, meadow_top), (WIDTH, meadow_top), 2)

    # Trèfles dans la prairie
    for clover in clovers:
        clover.draw(screen)

    # Lapins mignons
    for bunny in bunnies:
        bunny.draw(screen)

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("KAWAII BUNNY MEADOW — PRAIRIE & TRÈFLES", True, TEXT_COLOR)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Lapins : {len(bunnies)} | Trèfles : {len(clovers)}", True, CLOVER_LIGHT)
    screen.blit(stats_txt, (40, 42))

    inst_txt = font_small.render("CLIC GAUCHE : Faire pousser un trèfle | B : Ajouter un lapin | R : Reset", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 40, 42))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()