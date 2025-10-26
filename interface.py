# interface_blueprince_sidebar.py
import os, sys
import pygame as pg

# --- Grille Blue Prince
ROWS, COLS = 9, 5
CELL, GAP, PAD = 64, 4, 40
BOARD_W = COLS * (CELL + GAP) + PAD * 2 - GAP
BOARD_H = ROWS * (CELL + GAP) + PAD * 2 - GAP

SIDEBAR_W = 520  # élargissement inventaire
W = BOARD_W + SIDEBAR_W
H = BOARD_H + 72
FPS = 60

""" taille de l'icone de chaque item (inventaire) """
INV_ICON_PERM = 24      # icônes permanents
INV_ICON_CONS = 20      # icônes consommables plus petites
# Couleurs
BG1        = (255, 255, 255)   # fond global blanc pour l'inventaire
BG2        = (0, 0, 0)         # fond noir pour le plateau de jeux
TEXT_DARK = (30, 30, 30)
MUTED     = (120, 120, 120)
CURSOR    = (120, 185, 255)
ROOM_COL  = (70, 160, 120)

""" Position des chambres fixe (entrée + anti-chambre) """
ENTRY_POS = (ROWS - 1, COLS // 2)   # bas milieu
ANTI_POS  = (0,         COLS // 2)  # haut milieu

""" Icon de chaque chambre ou objet """
BASE_DIR = os.path.dirname(__file__)
ASSETS   = os.path.join(BASE_DIR, "assets")

def grid_rect(r, c, x0=0, y0=0):
    x = x0 + PAD + c * (CELL + GAP)
    y = y0 + PAD + r * (CELL + GAP)
    return pg.Rect(x, y, CELL, CELL)

""" Cette fonction nous divulgue notre position """
def pos_from_mouse(mx, my, x0=0, y0=0):
    # clics seulement dans la zone plateau
    if mx >= BOARD_W: 
        return None
    for r in range(ROWS):
        for c in range(COLS):
            if grid_rect(r, c, x0, y0).collidepoint(mx, my):
                return (r, c)
    return None

""" télécharger les icones de l'inventaire """
def load_png(name, size):
    path = os.path.join(ASSETS, name)
    surf = pg.image.load(path).convert_alpha()
    return pg.transform.smoothscale(surf, (size, size))

""" télécharger les images des chambres"""
def load_img(name, size):
    path = os.path.join(ASSETS, name)
    try:
        surf = pg.image.load(path).convert_alpha()
        return pg.transform.smoothscale(surf, (size, size))
    except Exception:
        return None

    return None

""" Cette fonction nous permet de constituer notre plateau de jeux, qui se trouve à gauche de l'écran"""
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

""" Divulguer le nom de la chambre en fonction de ou se trouve mon curseur"""
def current_room_name(cursor, rooms):
    r, c = cursor
    if (r, c) == ENTRY_POS: return "Chambre d'entée"
    if (r, c) == ANTI_POS:  return "Anti-chambre"
    if rooms[r][c] == 1:    return "Room"
    return "—"

""" Cette fonction nous permet de constituer notre inventaire, qui se trouve à droite de l'écran"""
def draw_sidebar(screen, font, big, inventory, room_label, icons):
    x0 = BOARD_W
    screen.fill(BG1, pg.Rect(x0, 0, SIDEBAR_W, H))

    # Titre
    screen.blit(big.render("Inventory:", True, TEXT_DARK), (x0 + 24, 24))

    # Deux colonnes: permanents à gauche, consommables à droite
    colL_x = x0 + 24
    colR_x = x0 + SIDEBAR_W // 2 + 20
    name_dx_L = INV_ICON_PERM + 10
    name_dx_R = INV_ICON_CONS + 10
    val_dx  = 120

    # En-têtes colonnes
    screen.blit(font.render("Permanents", True, MUTED),   (colL_x, 56))
    screen.blit(font.render("Consommables", True, MUTED), (colR_x, 56))

    # Définition des groupes
    permanents   = [("pelle","Pelle"), ("detecteur","Détecteur"), ("patte","Patte de lapin"), ("carte","Carte")]
    consommables = [("pas","Pas"), ("pièces","Pièces"), ("gems","Gems"), ("clés","Clés"), ("dés","Dés")]

    # Colonne gauche: permanents (afficher seulement si obtenus)
    yL = 80
    for key, label in permanents:
        qty = inventory.get(key, 0)
        if qty > 0:  # afficher seulement si possédé
            ico = icons.get(key)
            if ico: screen.blit(ico, (colL_x, yL))
            screen.blit(font.render(label, True, TEXT_DARK), (colL_x + name_dx_L, yL + 6))
            screen.blit(big.render(str(qty), True, TEXT_DARK), (colL_x + val_dx, yL + 2))
            yL += max(INV_ICON_PERM, 28) + 14

    # Colonne droite: consommables (toujours visibles, icônes plus petites)
    yR = 80
    for key, label in consommables:
        qty = inventory.get(key, 0)
        ico = icons.get(key)
        if ico: screen.blit(pg.transform.smoothscale(ico, (INV_ICON_CONS, INV_ICON_CONS)), (colR_x, yR + 4))
        screen.blit(font.render(label, True, TEXT_DARK), (colR_x + name_dx_R, yR + 6))
        screen.blit(big.render(str(qty), True, TEXT_DARK), (colR_x + val_dx, yR + 2))
        yR += max(INV_ICON_CONS, 28) + 14

    # Section pièce actuelle (une seule ligne)
    y_bottom = max(yL, yR) + 12
    screen.blit(big.render(room_label, True, TEXT_DARK), (x0 + 24, y_bottom))

    # Aide
    helpy = H - 56
    screen.blit(font.render("Clic: placer/retirer une pièce", True, MUTED), (x0 + 24, helpy))
    screen.blit(font.render("Flèches/ZQSD: curseur  |  Échap: quitter", True, MUTED), (x0 + 24, helpy + 22))


""" main (test) """
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

    """ Inventaire initiale """
    inventory = {
        # permanents
        "pelle":0, "detecteur":0, "patte":0, "carte":0,
        # consommables
        "pas":70, "pièces":0, "gems":2, "clés":0, "dés":0
    }

    """ Image de chaque chambre (wikipedia du jeu BluePrince) """
    """ taille de l'icone de chaque chambre """
    icon = CELL - 8

    """ chargement des chambres """
    img_entree = None
    for nm in ("entree.png", "entree.png.webp"):
        if os.path.exists(os.path.join(ASSETS, nm)):
            img_entree = load_png(nm, icon); break
    img_anti = None
    for nm in ("antichambre.png", "antichambre.png.webp"):
        if os.path.exists(os.path.join(ASSETS, nm)):
            img_anti = load_png(nm, icon); break

    """ chargement des icones """
    def opt(name): 
        p = os.path.join(ASSETS, name)
        return load_png(name, INV_ICON_PERM) if os.path.exists(p) else None

    icons = {
        # permanents
        "pelle": opt("shovel.png"),
        "detecteur": opt("metal_detector.png"),
        "patte": opt("rabbit_foot.png"),
        "carte": opt("map.png"),
        # consommables
        "pas": opt("footstep.png"),
        "pièces": opt("money.png"),
        "gems": opt("diamond.png"),
        "clés": opt("key.png"),
        "dés": opt("dice.png"),
    }

    """ Deroulement de l'inteface en fonction des touches enfoncer par le joueur sur son clavier """
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
        draw_sidebar(screen, font, big, inventory, room_label, icons)

        pg.display.flip()
        clock.tick(FPS)

    pg.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
