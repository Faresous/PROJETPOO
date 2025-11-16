# =====================================================
#  interfacepy – Interface graphique du jeu BluePrince
# =====================================================

import os
import sys
import pygame as pg
import random
from enum import Enum
from doors import Rooms, Doors, Orientation, Room
from joueur import joueur

# ======================
#  CONSTANTES GÉNÉRALES
# ======================

ROWS, COLS = 9, 5
CELL, GAP, PAD = 64, 4, 40
BOARD_W = COLS * (CELL + GAP) + PAD * 2 - GAP
BOARD_H = ROWS * (CELL + GAP) + PAD * 2 - GAP
SIDEBAR_W = 520
W = BOARD_W + SIDEBAR_W
H = BOARD_H + 72
FPS = 60

INV_ICON = 24

BG1   = (255,255,255)
BG2   = (0,0,0)
TEXT_DARK = (30,30,30)
MUTED     = (120,120,120)
ROOM_COL  = (70,160,120)
WHITE     = (255,255,255)

ENTRY_POS = (ROWS - 1, COLS // 2)
ANTI_POS  = (0,         COLS // 2)

BASE_DIR = os.path.dirname(__file__)
ASSETS   = os.path.join(BASE_DIR, "assets")

# ============================================================
#  AJOUT : dictionnaire global contenant les images des salles
# ============================================================
ROOM_IMAGES = {}

def load_room_images():
    """
    Charge les images des salles (.webp ou .png) selon Rooms.ROOMS_DB.
    """
    for key in Rooms.ROOMS_DB.keys():

        img = None
        # On teste .webp puis .png
        for ext in ("webp", "png"):
            filename = f"{key}.{ext}"
            path = os.path.join(ASSETS, filename)
            if os.path.exists(path):
                img = load_png(filename, CELL - 8)
                break

        ROOM_IMAGES[key] = img


# ============================================================
#  ÉTATS DE L’INTERFACE
# ============================================================

class UIState(Enum):
    """
    États possibles de l’interface BluePrince.

    - MENU : menu principal.
    - PLAYING : partie en cours (déplacement via portes).
    - DRAFT : écran de sélection de 3 salles.
    - OPTIONS : paramètres.
    - QUITTING : sortie du jeu.
    - GAME_OVER : plus de pas.
    """
    MENU     = 0
    PLAYING  = 1
    DRAFT    = 2
    OPTIONS  = 3
    QUITTING = 4
    GAME_OVER = 5

# ===============
#  MENU PRINCIPAL 
# ===============

WHITE = (255, 255, 255)
ACCENT = (28, 160, 110)
ACCENT_DARK = (20, 120, 85)

def _button_rects(center_x, start_y, w = 360, h = 56, gap = 16):
    """ Création des boutons du menu principal en forme de rectangle  """
    rects = []
    y = start_y
    for _ in range(4):
        rects.append(pg.Rect(center_x - w//2, y, w, h))
        y += h + gap
    return rects

def draw_main_menu(screen, big, font, bg_img, focus_idx):
    """ Dessine le menu principal avec les boutons  """
    screen.fill(BG1)
    if bg_img:
        bg = pg.transform.smoothscale(bg_img, (screen.get_width(), screen.get_height()))
        screen.blit(bg, (0, 0))
        dark = pg.Surface(screen.get_size(), pg.SRCALPHA)
        dark.fill((0, 0, 0, 70))
        screen.blit(dark, (0, 0))

    cx = screen.get_width() // 2
    title = big.render("BluePrince", True, TEXT_DARK)
    subtitle = font.render("Choisissez une action", True, MUTED)
    screen.blit(title, title.get_rect(center=(cx, 140)))
    screen.blit(subtitle, subtitle.get_rect(center=(cx, 190)))

    rects = _button_rects(center_x=cx, start_y=260)
    labels = ["Nouvelle partie", "Charger", "Options", "Quitter"]

    mx, my = pg.mouse.get_pos()
    for i, (r, label) in enumerate(zip(rects, labels)):
        hovered = r.collidepoint(mx, my) or (i == focus_idx)
        draw_pill_button(screen, r, hovered)
        txt = font.render(label, True, ACCENT_DARK if hovered else TEXT_DARK)
        screen.blit(txt, txt.get_rect(center=r.center))

    return rects


def draw_pill_button(screen, rect, hovered):
    """
    Dessine un bouton de type "bulle" (bordure arrondie).
    """
    sh = pg.Surface((rect.w, rect.h), pg.SRCALPHA)
    pg.draw.rect(sh, (0, 0, 0, 60), (0, 0, rect.w, rect.h), border_radius=rect.h // 2)
    screen.blit(sh, (rect.x, rect.y + 4))

    btn = pg.Surface((rect.w, rect.h), pg.SRCALPHA)
    pg.draw.rect(btn, (255, 255, 255, 240 if hovered else 220),
                 (0, 0, rect.w, rect.h), border_radius=rect.h // 2)

    pg.draw.rect(btn, ACCENT if hovered else (220, 226, 231),
                 (0, 0, rect.w, rect.h), width=2, border_radius=rect.h // 2)
    screen.blit(btn, rect.topleft)


def run_main_menu(screen, big, font, clock, assets_dir):
    """
    Affiche et gère le menu principal du jeu.
    """
    bg_img = None
    for nm in ("BG_blueprince.webp", "BG_blueprince.png", "BG_blueprince.jpg"):
        p = os.path.join(assets_dir, nm)
        if os.path.exists(p):
            bg_img = pg.image.load(p).convert()
            break

    labels = ["Nouvelle partie", "Charger", "Options", "Quitter"]
    actions = [UIState.PLAYING, "LOAD", UIState.OPTIONS, UIState.QUITTING]
    focus_idx = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return UIState.QUITTING

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return UIState.QUITTING
                elif event.key in (pg.K_UP, pg.K_z):
                    focus_idx = (focus_idx - 1) % len(labels)
                elif event.key in (pg.K_DOWN, pg.K_s):
                    focus_idx = (focus_idx + 1) % len(labels)
                elif event.key in (pg.K_RETURN, pg.K_SPACE):
                    act = actions[focus_idx]
                    return act if isinstance(act, UIState) else UIState.MENU

            if event.type == pg.MOUSEMOTION:
                rects = _button_rects(center_x=screen.get_width() // 2, start_y=260)
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        focus_idx = i
                        break

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                rects = _button_rects(center_x=screen.get_width() // 2, start_y=260)
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        act = actions[i]
                        return act if isinstance(act, UIState) else UIState.MENU

        draw_main_menu(screen, big, font, bg_img, focus_idx)
        pg.display.flip()
        clock.tick(FPS)


def _run_options(screen, font, big, clock):
    """
    Affiche et gère la section "options".
    """
    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                running = False
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                running = False

        screen.fill((240,244,248))
        screen.blit(big.render("Options", True, TEXT_DARK), (40,40))
        screen.blit(font.render("Paramètres à implémenter...", True, MUTED), (40,110))
        pg.display.flip()
        clock.tick(FPS)

# ==================
#  MUSIQUE + IMAGES
# ==================

def init_music():
    """ Music de fond du jeu BluePrince """
    pg.mixer.init()
    pg.mixer.music.load(os.path.join(ASSETS,"blueprince.mp3"))
    pg.mixer.music.set_volume(1)
    pg.mixer.music.play(-1)

def load_png(name, size):
    """ Chargement des icons des objets """
    path = os.path.join(ASSETS, name)
    surf = pg.image.load(path).convert_alpha()
    return pg.transform.smoothscale(surf, (size, size))

def opt_obj(name):
    """ Générer l'icône pour chaque objet. """
    p = os.path.join(ASSETS, name)
    return load_png(name, INV_ICON) if os.path.exists(p) else None

# ====================
#  TIRAGE DE 3 SALLES
# ====================

def get_opposite_dir(dir: Orientation):
    """Retourne l'orientation opposée"""
    if dir == Orientation.N: return Orientation.S
    if dir == Orientation.S: return Orientation.N
    if dir == Orientation.E: return Orientation.O
    if dir == Orientation.O: return Orientation.E
    return None

def draft_three_rooms(row: int, entrance_direction: Orientation , pioche: list):
    """ Tire trois salles compatibles avec la rareté. """
    
    needed_door = get_opposite_dir(entrance_direction)
    
    valid_options = []
    for spec in pioche:
        if spec.key in {"ROOM_46", "ANTECHAMBER"}:
            continue
            
        # On teste les 4 rotations
        for rotation in [0, 90, 180, 270]:
            # Calcule les portes pour cette rotation
            room_doors = Doors.shape_orientations(spec.shape, rotation)
            
            if needed_door in room_doors:
                valid_options.append( (spec, rotation) )
                break
            
    lvl = Doors.level_by_row(row)
    if lvl == 0:
        rare_ok = ("Common","Commonplace","Standard",None)
    elif lvl == 1:
        rare_ok = ("Unusual","Rare","Standard")
    else:
        rare_ok = ("Rumored","Epic","Very Rare","Rare")
    
    pool = valid_options
    if len(pool) < 3:
        return random.choices(pool, k=3)
    else:
        return random.sample(pool, 3)

def reroll_draft(row: int, player: joueur, draft_list,pioche: list, entrance_dir: Orientation):
    """ Reroll du draft si joueur possède un dé. """
    if player.des <= 0:
        return draft_list, False
    player.des -= 1
    return draft_three_rooms(row, entrance_dir, pioche), True

def apply_room_loot(player: joueur, room: Room):
    """ Applique effets immédiats : gemmes, pas, malus. """
    eff = room.effects

    if "regain_steps" in eff:
        g = eff["regain_steps"]
        player.pas += g
        return f"You gain {g} step(s)."

    if "garden" in eff:
        g = eff["garden"]["gems_spawn"]
        if g > 0:
            player.gemmes += g
            return f"You gain {g} gem(s)."

    if "penalty" in eff:
        s = eff["penalty"]["steps_minus"]
        player.pas -= s
        return f"You lose {s} step(s)."

    return None

def room_has_opening(spec, orientation):
    """Retourne True si la salle possède une porte dans l'orientation demandée."""
    dirs = Doors.shape_orientations(spec.shape)
    return orientation in dirs

def allowed_room_positions(spec, new_r, new_c):
    """Filtre géographique : vérifie que la salle peut exister à la position."""
    dirs = Doors.shape_orientations(spec.shape)

    # bord du haut → pas de porte Nord
    if new_r == 0 and Orientation.N in dirs:
        return False

    # bord du bas
    if new_r == ROWS - 1 and Orientation.S in dirs:
        return False

    # bord gauche
    if new_c == 0 and Orientation.O in dirs:
        return False

    # bord droit
    if new_c == COLS - 1 and Orientation.E in dirs:
        return False

    return True

ROTATION_ORDER = [Orientation.N, Orientation.E, Orientation.S, Orientation.O]
def rotate_shape_to_fit(spec, entrance_dir):
    """
    Retourne une nouvelle RoomSpec avec rotation effectuée
    pour que la porte 'entrance_dir' devienne accessible.
    """
    needed = entrance_dir

    for rot in range(4):
        dirs = Doors.shape_orientations(spec.shape)
        if needed in dirs:
            return spec, rot
        spec = spec.rotate_90()  # ta classe RoomSpec le permet déjà

    # si aucune rotation ne marche → salle impossible
    return None, None

def compute_valid_specs(row, col, entrance_dir):
    """
    Filtre complet : rareté + compatibilité géographique + rotation auto
    """
    specs = list(Rooms.ROOMS_DB.values())
    rng = random.Random()
    rng.seed()

    valid = []

    for spec in specs:

        # 1) La salle doit posséder l'ouverture du côté par lequel on entre
        if not room_has_opening(spec, Orientation.opposite(entrance_dir)):
            continue

        # 2) Géométrie : interdictions selon la position dans le manoir
        if not allowed_room_positions(spec, row, col):
            continue

        # 3) Tester rotations possibles
        rotated, rot = rotate_shape_to_fit(spec, entrance_dir)
        if rotated is None:
            continue

        valid.append(rotated)

    return valid


# =======================
#  TRIANGLE DIRECTIONNEL
# =======================

def draw_direction_hint(screen, rect, direction: Orientation):
    """
    Dessine un triangle blanc propre sur le bord de la salle pour indiquer
    la direction sélectionnée par le joueur.
    """
    SIZE = 6

    if direction == Orientation.N:
        pts = [(rect.centerx, rect.top + 5),
               (rect.centerx - SIZE, rect.top + 25),
               (rect.centerx + SIZE, rect.top + 25)]

    elif direction == Orientation.S:
        pts = [(rect.centerx, rect.bottom - 5),
               (rect.centerx - SIZE, rect.bottom - 25),
               (rect.centerx + SIZE, rect.bottom - 25)]

    elif direction == Orientation.E:
        pts = [(rect.right - 5, rect.centery),
               (rect.right - 25, rect.centery - SIZE),
               (rect.right - 25, rect.centery + SIZE)]

    elif direction == Orientation.O:
        pts = [(rect.left + 5, rect.centery),
               (rect.left + 25, rect.centery - SIZE),
               (rect.left + 25, rect.centery + SIZE)]

    pg.draw.polygon(screen, (255,255,255), pts)
    pg.draw.polygon(screen, (0,0,0), pts, width=2)

# ============================================================
#  DESSIN DE LA GRILLE — MODIFIÉ (images de salles ajoutées)
# ============================================================

def grid_rect(r, c):
    """ Dimmensionnement du plateau du jeu """
    x = PAD + c * (CELL + GAP)
    y = PAD + r * (CELL + GAP)
    return pg.Rect(x, y, CELL, CELL)

def draw_board(screen, room_grid, player: joueur, img_entree, img_anti, active_direction):
    """ Construire le plateau de jeu à gauche de l'écran  """
    screen.fill(BG2, pg.Rect(0,0,BOARD_W,H))

    for r in range(ROWS):
        for c in range(COLS):
            rect = grid_rect(r,c)
            room = room_grid[r][c]

            # entrée
            if (r,c) == ENTRY_POS:
                if img_entree:
                    screen.blit(img_entree, img_entree.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (90,200,255), rect, border_radius=10)

            # anti-chambre
            elif (r,c) == ANTI_POS:
                if img_anti:
                    screen.blit(img_anti, img_anti.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (255,160,90), rect, border_radius=10)

            else:
                if room:
                    # AJOUT : afficher l'image de la salle si disponible
                    img = ROOM_IMAGES.get(room.spec.key)
                    if img:
                        rotation = room.rotation
                        rotated_img = pg.transform.rotate(img, -rotation)
                        screen.blit(rotated_img, rotated_img.get_rect(center=rect.center))
                    else:
                        pg.draw.rect(screen, ROOM_COL, rect, border_radius=8)

            # salle active
            if (r,c) == (player.ligne, player.colonne):
                pg.draw.rect(screen, WHITE, rect, width=3, border_radius=10)
                if active_direction:
                    draw_direction_hint(screen, rect, active_direction)

# ======================
#  SIDEBAR / INVENTAIRE 
# ======================

def draw_sidebar(screen, font, big, player: joueur, current_room_name, icons, last_message, step_flash, step_flash_time):
    """ Construire l'inventaire à droite de l'écran  """
    x0 = BOARD_W
    screen.fill(BG1, pg.Rect(x0,0,SIDEBAR_W,H))

    screen.blit(big.render("Inventory:", True, TEXT_DARK), (x0+24,24))

    inventory = {
        "pas": player.pas,
        "pièces": player.orr,
        "gems": player.gemmes,
        "clés": player.cles,
        "dés": player.des,
        "pelle": 1 if "Pelle" in player.objet_permanents else 0,
        "detecteur de méteaux": 1 if "Detecteur de méteaux" in player.objet_permanents else 0,
        "patte de lapin": 1 if "Patte de lapin" in player.objet_permanents else 0,
        "kit de crochetage": 1 if "Kit de crochetage" in player.objet_permanents else 0,
        "marteau": 1 if "Marteau" in player.objet_permanents else 0,
    }

    permanents = [
        ("pelle","Pelle"), ("detecteur de méteaux","Détecteur"),
        ("patte de lapin","Patte de lapin"), ("kit de crochetage","KC"),
        ("marteau","Marteau")
    ]

    conso = [
        ("pas","Pas"), ("pièces","Pièces"),
        ("gems","Gems"), ("clés","Clés"), ("dés","Dés")
    ]

    colL = x0+24
    colR = x0+SIDEBAR_W//2+20
    dx = INV_ICON + 10
    valdx = 120

    screen.blit(font.render("Permanents", True, MUTED), (colL,56))
    screen.blit(font.render("Consommables", True, MUTED), (colR,56))

    yL = 80
    for key,label in permanents:
        if inventory[key] > 0:
            ico = icons.get(key)
            if ico: screen.blit(ico, (colL,yL))
            screen.blit(font.render(label,True,TEXT_DARK),(colL+dx,yL+6))
            screen.blit(big.render(str(inventory[key]),True,TEXT_DARK),(colL+valdx,yL+2))
            yL += INV_ICON + 24

    yR = 80
    for key,label in conso:
        ico = icons.get(key)
        if ico: screen.blit(pg.transform.smoothscale(ico,(INV_ICON,INV_ICON)),(colR,yR+4))
        screen.blit(font.render(label,True,TEXT_DARK),(colR+dx,yR+6))
        screen.blit(big.render(str(inventory[key]),True,TEXT_DARK),(colR+valdx,yR+2))
        yR += INV_ICON + 24

    yb = max(yL,yR) + 12
    screen.blit(big.render(current_room_name, True, TEXT_DARK),(x0+24,yb))

    if step_flash and step_flash_time > 0:
        color = (0,180,0) if step_flash.startswith("+") else (220,40,40)
        screen.blit(big.render(step_flash, True, color), (x0+24, yb+40))

    if last_message:
        screen.blit(font.render(last_message, True, (0,0,0)), (x0+24, H-40))

# =======
#  DRAFT
# =======

def draw_draft(screen, font, big, draft_list, focus_idx):
    """ Affiche les 3 salles à sélectionner. """
    x0 = BOARD_W
    screen.fill((240,240,240), pg.Rect(x0,0,SIDEBAR_W,H))

    title = big.render("Choose a room to draft", True, TEXT_DARK)
    screen.blit(title, (x0+80,40))

    xs = [x0+90, x0+220, x0+350]   # positions horizontales des 3 rooms
    img_size = 80                # taille des images des salles

    for i, (spec, rotation) in enumerate(draft_list):

        # IMAGE DE LA SALLE
        img = ROOM_IMAGES.get(spec.key)
        if img:
            # redimensionner proprement
            room_img = pg.transform.smoothscale(img, (img_size, img_size))
            rotated_img = pg.transform.rotate(room_img, -rotation)
            screen.blit(rotated_img, rotated_img.get_rect(center=(xs[i], 170)))
        else:
            # fallback sans image
            pg.draw.rect(screen, (200,200,200),
                         pg.Rect(xs[i]-img_size//2, 170-img_size//2, img_size, img_size))

        # NOM EN DESSOUS DE L’IMAGE
        col = (0,120,255) if i==focus_idx else TEXT_DARK
        txt = font.render(spec.name, True, col)
        screen.blit(txt, txt.get_rect(center=(xs[i], 270)))

        # CADRE BLEU SI SÉLECTIONNÉ
        if i == focus_idx:
            rect = pg.Rect(xs[i]-img_size//2, 170-img_size//2, img_size, img_size)
            pg.draw.rect(screen, (0,120,255), rect, width=3, border_radius=8)

    rr = big.render("Redraw (R)", True, (60,60,60))
    screen.blit(rr, rr.get_rect(center=(x0 + SIDEBAR_W//2, 340)))


# ===========
#  GAME OVER
# ===========

def draw_game_over(screen, font, big):
    """
    Affiche l'écran Game Over lorsque le joueur n'a plus de pas.
    """
    screen.fill((0,0,0))
    txt = big.render("NO STEPS LEFT", True, (255,60,60))
    sub = font.render("GAME OVER — Press SPACE to return to menu", True, (220,220,220))
    screen.blit(txt, txt.get_rect(center=(W//2, H//2 - 20)))
    screen.blit(sub, sub.get_rect(center=(W//2, H//2 + 20)))

# ======
#  MAIN
# ======

def main():
    """ main (test) """

    pg.init()
    init_music()
    screen = pg.display.set_mode((W,H))
    pg.display.set_caption("Blue Prince — Jeux + Inventaire")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None,24)
    big  = pg.font.SysFont(None,28)

    # AJOUT : chargement images des salles
    load_room_images()

    icon = CELL - 8
    img_entree = load_png("entree.webp", icon) if os.path.exists(ASSETS) else None
    img_anti   = load_png("antichambre.webp", icon) if os.path.exists(ASSETS) else None

    icons = {
        "pelle": opt_obj("shovel.png"),
        "detecteur de méteaux": opt_obj("metal-detector.png"),
        "patte de lapin": opt_obj("rabbit_foot.png"),
        "kit de crochetage": opt_obj("lockpick.png"),
        "marteau": opt_obj("hammer.png"),
        "pas": opt_obj("footstep.png"),
        "pièces": opt_obj("money.png"),
        "gems": opt_obj("diamond.png"),
        "clés": opt_obj("key.png"),
        "dés": opt_obj("dice.png"),
    }

    player = joueur(ENTRY_POS[0], ENTRY_POS[1])

    room_grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    room_grid[ENTRY_POS[0]][ENTRY_POS[1]] = Rooms.generate_room("ENTRANCE_HALL", row=ENTRY_POS[0],rotation=180)
    room_grid[ANTI_POS[0]][ANTI_POS[1]]   = Rooms.generate_room("ANTECHAMBER",   row=0)

    # PIOCHE 
    pioche = list(Rooms.ROOMS_DB.values())
    pioche = [spec for spec in pioche if spec.key not in {"ENTRANCE_HALL", "ANTECHAMBER", "ROOM_46"}]
    
    state = UIState.MENU
    active_direction = None
    last_message = None
    draft_list = None
    focus_idx = 0
    entrance_direction_for_draft = None
    
    step_flash = None
    step_flash_time = 0

    running = True
    while running:

        # ------------ GAME OVER ----------------
        if state == UIState.GAME_OVER:
            draw_game_over(screen, font, big)
            pg.display.flip()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    return 0
                if e.type == pg.KEYDOWN and e.key in (pg.K_SPACE, pg.K_RETURN):
                    state = UIState.MENU
                    continue

            clock.tick(FPS)
            continue

        # ------------ MENU ----------------
        if state == UIState.MENU:
            choice = run_main_menu(screen, big, font, clock, ASSETS)
            if choice == UIState.PLAYING:
                state = UIState.PLAYING
                continue
            if choice == UIState.OPTIONS:
                _run_options(screen, font, big, clock)
                state = UIState.MENU
                continue
            if choice == UIState.QUITTING:
                break

        # ------------ PLAYING ----------------
        if state == UIState.PLAYING:

            if step_flash_time > 0:
                step_flash_time -= 1 / FPS
            else:
                step_flash = None

            for e in pg.event.get():

                if e.type == pg.QUIT:
                    state = UIState.QUITTING

                elif e.type == pg.KEYDOWN:

                    if e.key == pg.K_ESCAPE:
                        state = UIState.MENU

                    elif e.key in (pg.K_z, pg.K_UP):
                        active_direction = Orientation.N
                    elif e.key in (pg.K_s, pg.K_DOWN):
                        active_direction = Orientation.S
                    elif e.key in (pg.K_q, pg.K_LEFT):
                        active_direction = Orientation.O
                    elif e.key in (pg.K_d, pg.K_RIGHT):
                        active_direction = Orientation.E

                    elif e.key in (pg.K_SPACE, pg.K_RETURN) and active_direction:

                        r, c = player.ligne, player.colonne
                        room = room_grid[r][c]
                        dir  = active_direction
                        
                        if room is None:
                            last_message = "No room here."
                            active_direction = None
                            continue
                        
                        # bords
                        if (dir==Orientation.N and r==0) \
                        or (dir==Orientation.S and r==ROWS-1) \
                        or (dir==Orientation.E and c==COLS-1) \
                        or (dir==Orientation.O and c==0):
                            last_message = "You cannot exit the manor."
                            active_direction = None
                            continue

                        door = room.doors.get(dir)
                        if door is None:
                            last_message = "No door in this direction."
                            active_direction = None
                            continue

                        resources = {
                            "keys": player.cles,
                            "kit de crochetage": ("Kit de crochetage" in player.objet_permanents)
                        }

                        ok = door.open(resources)
                        player.cles = resources["keys"]

                        if not ok:
                            last_message = "The door is locked."
                            active_direction = None
                            continue

                        dep_ligne, dep_colonne = 0, 0
                        
                        if dir == Orientation.N: dep_ligne = -1 
                        if dir == Orientation.S: dep_ligne = 1
                        if dir == Orientation.E: dep_colonne = 1
                        if dir == Orientation.O: dep_colonne = -1
         
                        # perte de 1 pas
                        try:
                            player.move(dep_ligne, dep_colonne)
                            step_flash = "-1"
                            step_flash_time = 1.0
                            
                        except ValueError:
                            last_message = "Plus de pas !"
                            state = UIState.GAME_OVER
                            active_direction = None
                            continue
                        
                        if player.pas <= 0:
                            state = UIState.GAME_OVER
                            continue

                        # nouvelle salle
                        if room_grid[player.ligne][player.colonne] is None:
                            entrance_direction_for_draft = active_direction
                            draft_list = draft_three_rooms(player.ligne, entrance_direction_for_draft, pioche)
                            focus_idx = 0
                            active_direction = None
                            state = UIState.DRAFT
                            continue

                        # salle connuet
                        msg = apply_room_loot(player, room_grid[player.ligne][player.colonne])

                        if msg and msg.startswith("You gain"):
                            gain = int(msg.split()[2])
                            step_flash = f"+{gain}"
                            step_flash_time = 1.0

                        last_message = msg
                        active_direction = None
            
            if room_grid[player.ligne][player.colonne] is None:
                pg.display.flip()
                clock.tick(FPS)
                continue

            draw_board(screen, room_grid, player, img_entree, img_anti, active_direction)
            
            current_room = room_grid[player.ligne][player.colonne]
            name = current_room.spec.name if current_room else "Unknown room"

            draw_sidebar(screen, font, big, player, name, icons, last_message, step_flash, step_flash_time)
            pg.display.flip()
            clock.tick(FPS)
  
        # ------------ DRAFT ----------------
        if state == UIState.DRAFT:

            for e in pg.event.get():

                if e.type == pg.QUIT:
                    state = UIState.QUITTING

                elif e.type == pg.KEYDOWN:

                    if e.key == pg.K_ESCAPE:
                        state = UIState.PLAYING

                    elif e.key in (pg.K_LEFT, pg.K_q):
                        focus_idx = max(0, focus_idx - 1)
                    elif e.key in (pg.K_RIGHT, pg.K_d):
                        focus_idx = min(2, focus_idx + 1)

                    elif e.key == pg.K_r:
                        draft_list, _ = reroll_draft(player.ligne, player, draft_list, pioche, entrance_direction_for_draft)    
                    elif e.key in (pg.K_SPACE, pg.K_RETURN):
                        spec, rotation = draft_list[focus_idx]
                        cost = spec.cost_gems or 0
                        
                        if not player.utiliser_gems(cost):
                            last_message = "Pas assez de gems!"
                            continue
                        
                        if spec in pioche:
                            pioche.remove(spec)
                        
                        room = Rooms.generate_room(spec.key, row=player.ligne, rotation=rotation)
                        room_grid[player.ligne][player.colonne] = room
                        last_message = f"Le joueur a depense {cost} gemmes !"
                        
                        msg = apply_room_loot(player, room)
                        if msg and msg.startswith("You gain"):
                            gain = int(msg.split()[2])
                            step_flash = f"+{gain}"
                            step_flash_time = 1.0

                        last_message = msg
                        state = UIState.PLAYING

            draw_board(screen, room_grid, player, img_entree, img_anti, None)
            draw_draft(screen, font, big, draft_list, focus_idx)
            pg.display.flip()
            clock.tick(FPS)

        if state == UIState.QUITTING:
            running = False

    pg.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
