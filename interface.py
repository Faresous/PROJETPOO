# interface_blueprince_sidebar.py
import os, sys
import pygame as pg

# --- Grille Blue Prince
ROWS, COLS = 9, 5
CELL, GAP, PAD = 64, 4, 40
BOARD_W = COLS * (CELL + GAP) + PAD * 2 - GAP
BOARD_H = ROWS * (CELL + GAP) + PAD * 2 - GAP

SIDEBAR_W = 340
W = BOARD_W + SIDEBAR_W
H = BOARD_H + 72
FPS = 60

# Couleurs
BG1        = (255, 255, 255)   # fond global blanc pour l'inventaire
BG2        = (0, 0, 0)         # fond noir pour le plateau de jeux
TEXT_DARK = (30, 30, 30)
MUTED     = (120, 120, 120)
CURSOR    = (120, 185, 255)
ROOM_COL  = (70, 160, 120)

# Positions fixes
ENTRY_POS = (ROWS - 1, COLS // 2)   # bas milieu
ANTI_POS  = (0,         COLS // 2)  # haut milieu

# Dossiers
BASE_DIR = os.path.dirname(__file__)
ASSETS   = os.path.join(BASE_DIR, "assets")

def grid_rect(r, c, x0=0, y0=0):
    x = x0 + PAD + c * (CELL + GAP)
    y = y0 + PAD + r * (CELL + GAP)
    return pg.Rect(x, y, CELL, CELL)

def pos_from_mouse(mx, my, x0=0, y0=0):
    # clics seulement dans la zone plateau
    if mx >= BOARD_W: 
        return None
    for r in range(ROWS):
        for c in range(COLS):
            if grid_rect(r, c, x0, y0).collidepoint(mx, my):
                return (r, c)
    return None

def load_img(name, size):
    path = os.path.join(ASSETS, name)
    try:
        surf = pg.image.load(path).convert_alpha()
        return pg.transform.smoothscale(surf, (size, size))
    except Exception:
        return None

def draw_board(screen, rooms, cursor, font, img_entree, img_anti):
    # zone plateau = gauche
    screen.fill(BG2, pg.Rect(0, 0, BOARD_W, H))

    for r in range(ROWS):
        for c in range(COLS):
            rect = grid_rect(r, c)

            if (r, c) == ENTRY_POS:
                if img_entree:
                    screen.blit(img_entree, img_entree.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (90, 200, 255), rect, border_radius=10)
                continue

            if (r, c) == ANTI_POS:
                if img_anti:
                    screen.blit(img_anti, img_anti.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (255, 160, 90), rect, border_radius=10)
                continue

            if rooms[r][c] == 1:
                pg.draw.rect(screen, ROOM_COL, rect, border_radius=8)

    # curseur
    cr = grid_rect(*cursor)
    pg.draw.rect(screen, CURSOR, cr, width=2, border_radius=10)

def current_room_name(cursor, rooms):
    r, c = cursor
    if (r, c) == ENTRY_POS: return "Chambre d'entée"
    if (r, c) == ANTI_POS:  return "Anti-chambre"
    if rooms[r][c] == 1:    return "Room"
    return "—"

def draw_sidebar(screen, font, big, inventory, room_label):
    # zone sidebar = droite
    x0 = BOARD_W
    screen.fill(BG1, pg.Rect(x0, 0, SIDEBAR_W, H))

    # Titre
    title = big.render("Inventory:", True, TEXT_DARK)
    screen.blit(title, (x0 + 24, 24))

    # Lignes inventaire (texte + emoji)
    lines = [
        (f"{inventory.get('gold',0)}", " 🕯"),
        (f"{inventory.get('rations',0)}", " 🍞"),
        (f"{inventory.get('gems',0)}", " 💎"),
        (f"{inventory.get('keys',0)}", " 🔑"),
        (f"{inventory.get('relics',0)}", " ⚙"),
    ]
    y = 24
    for val, ico in lines:
        y += 36
        t = big.render(val, True, TEXT_DARK)
        screen.blit(t, (x0 + SIDEBAR_W - 80, y))
        t2 = big.render(ico, True, TEXT_DARK)
        screen.blit(t2, (x0 + SIDEBAR_W - 48, y))

    # Espace
    y += 48
    label = big.render(room_label, True, TEXT_DARK)
    screen.blit(big.render("", True, TEXT_DARK), (x0+24, y))  # noop
    header = big.render(" ", True, TEXT_DARK)

    # Titre de la pièce
    hdr = big.render(room_label, True, TEXT_DARK)
    screen.blit(hdr, (x0 + 24, y + 12))

    # Aide
    helpy = H - 56
    h1 = font.render("Clic: placer/retirer une pièce", True, MUTED)
    h2 = font.render("Flèches/ZQSD: curseur  |  Échap: quitter", True, MUTED)
    screen.blit(h1, (x0 + 24, helpy))
    screen.blit(h2, (x0 + 24, helpy + 22))

def main():
    pg.init()
    screen = pg.display.set_mode((W, H))
    pg.display.set_caption("Blue Prince — Jeux + Inventaire")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 24)
    big  = pg.font.SysFont(None, 28)

    # État
    rooms = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    rooms[ENTRY_POS[0]][ENTRY_POS[1]] = 1
    rooms[ANTI_POS[0]][ANTI_POS[1]]   = 1
    cursor = [ENTRY_POS[0], ENTRY_POS[1]]

    # Inventaire minimal démo
    inventory = {"gold":70, "rations":0, "gems":2, "keys":0, "relics":0}

    # Images
    icon = CELL - 8
    img_entree = load_img("entree.png", icon) or load_img("entree.png.webp", icon)
    img_anti   = load_img("antichambre.png", icon) or load_img("antichambre.png.webp", icon)

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

        # Dessin
        draw_board(screen, rooms, tuple(cursor), big, img_entree, img_anti)
        room_label = current_room_name(tuple(cursor), rooms)
        draw_sidebar(screen, font, big, inventory, room_label)

        pg.display.flip()
        clock.tick(FPS)

    pg.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
