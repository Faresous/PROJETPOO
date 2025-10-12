# interface_squelette.py
import os
import sys
import pygame as pg

# --- Constantes Blue Prince
ROWS, COLS = 9, 5 # lignes/colomnes
CELL = 64
GAP  = 4
PAD  = 40
W = COLS * (CELL + GAP) + PAD * 2 - GAP
H = ROWS * (CELL + GAP) + PAD * 2 - GAP
FPS = 60

# Couleurs
BG        = (255, 255, 255) #BackGround si on voulait noir on aurai pu faire bg = (0,0,0)
GRID      = (210, 210, 210)
CURSOR    = (120, 185, 255)
ROOM_COL  = (70, 160, 120)
TEXT      = (235, 235, 235)
GHOST     = (120, 125, 135)

# Positions fixes demandées
ENTRY_POS = (ROWS - 1, COLS // 2)  # bas milieu -> (8,2)
ANTI_POS  = (0,         COLS // 2) # haut milieu -> (0,2)

# Dossiers
BASE_DIR = os.path.dirname(__file__)
ASSETS   = os.path.join(BASE_DIR, "assets")

def grid_rect(r, c):
    x = PAD + c * (CELL + GAP)
    y = PAD + r * (CELL + GAP)
    return pg.Rect(x, y, CELL, CELL)

def pos_from_mouse(mx, my):
    for r in range(ROWS):
        for c in range(COLS):
            if grid_rect(r, c).collidepoint(mx, my):
                return (r, c)
    return None

def load_img(name, size): #insertion des images pour différentes pièces 
    """Charge et redimensionne. Retourne None si fichier absent."""
    path = os.path.join(ASSETS, name)
    try:
        surf = pg.image.load(path).convert_alpha()
        return pg.transform.smoothscale(surf, (size, size))
    except Exception:
        return None

def draw_grid(screen, rooms, cursor, font, img_entree, img_anti):
    screen.fill(BG)

    title = font.render("Blue Prince — Grille 9×5", True, (30, 30, 30))
    screen.blit(title, (PAD, 8))

    for r in range(ROWS):
        for c in range(COLS):
            rect = grid_rect(r, c)

            # Entrée
            if (r, c) == ENTRY_POS:
                if img_entree:
                    screen.blit(img_entree, img_entree.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (90, 200, 255), rect, border_radius=10)
                continue

            # Antichambre
            if (r, c) == ANTI_POS:
                if img_anti:
                    screen.blit(img_anti, img_anti.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (255, 160, 90), rect, border_radius=10)
                continue

            # Autres pièces seulement si occupées
            if rooms[r][c] == 1:
                pg.draw.rect(screen, ROOM_COL, rect, border_radius=8)
                # option: petit liseré
                pg.draw.rect(screen, (200, 200, 200), rect, width=1, border_radius=8)

    # affichage de la position actuelle
    cr = grid_rect(*cursor)
    pg.draw.rect(screen, (180, 200, 255), cr, width=2, border_radius=10)

    # help
    legends = [
        "Clic: placer/retirer une pièce",
        "Flèches/ZQSD: curseur  |  Échap: quitter",
    ]
    y = H - PAD + 6
    for line in legends:
        t = font.render(line, True, (120, 120, 120))
        screen.blit(t, (PAD, y))
        y += t.get_height() + 2


def main():
    pg.init()
    screen = pg.display.set_mode((W, H + 72))  # bandeau bas
    pg.display.set_caption("Blue Prince — Interface de départ")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 28)

    # État de la grille
    rooms = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    rooms[ENTRY_POS[0]][ENTRY_POS[1]] = 1
    rooms[ANTI_POS[0]][ANTI_POS[1]]   = 1
    cursor = [ENTRY_POS[0], ENTRY_POS[1]]

    # Images
    icon_size = CELL - 8
    img_entree = load_img("entree.png.webp", icon_size) #pièce d'entrée (debut de jeu)
    img_anti   = load_img("antichambre.png.webp", icon_size) #anti-chambre (fin de jeu)

    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    running = False
                elif e.key in (pg.K_UP, pg.K_z):
                    cursor[0] = max(0, cursor[0] - 1)
                elif e.key in (pg.K_DOWN, pg.K_s):
                    cursor[0] = min(ROWS - 1, cursor[0] + 1)
                elif e.key in (pg.K_LEFT, pg.K_q):
                    cursor[1] = max(0, cursor[1] - 1)
                elif e.key in (pg.K_RIGHT, pg.K_d):
                    cursor[1] = min(COLS - 1, cursor[1] + 1)
                elif e.key in (pg.K_RETURN, pg.K_SPACE):
                    r, c = cursor
                    if (r, c) not in (ENTRY_POS, ANTI_POS):
                        rooms[r][c] = 1
                elif e.key in (pg.K_DELETE, pg.K_BACKSPACE):
                    r, c = cursor
                    if (r, c) not in (ENTRY_POS, ANTI_POS):
                        rooms[r][c] = 0
            elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                hit = pos_from_mouse(*e.pos)
                if hit:
                    r, c = hit
                    if (r, c) not in (ENTRY_POS, ANTI_POS):
                        rooms[r][c] ^= 1

        draw_grid(screen, rooms, tuple(cursor), font, img_entree, img_anti)
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())