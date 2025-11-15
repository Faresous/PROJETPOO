# =====================================================
#  interface.py – Interface graphique du jeu BluePrince
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
    """ Création des boutons du menu principal en forme de rectangle  

    Args:
        center_x (int): coordonnée du centre du rectangle par rapport à x 
        start_y (int): hauteur du rectangle de chaque bouton (sa coordonnée y) 
        w (int): la largeur du rectangle 
        h (int): la hauteur du rectangle
        gap (int): l'espace entre chaque bouton

    Returns:
        Renvoie une liste qui crée le rectangle correspondant à chaque bouton 
    """
    rects = []
    y = start_y
    for _ in range(4):
        rects.append(pg.Rect(center_x - w//2, y, w, h))
        y += h + gap
    return rects

def draw_main_menu(screen, big, font, bg_img, focus_idx):
    """ Dessine le menu principal avec les boutons  

    Args:
        screen (pg.Surface): écran de jeu
        big (pg.font.Font): agrandir la police pour les titres 
        font (pg.font.Font): la police d'écriture  
        bg_img (pg.Surface): écran de fond
        focus_idx (int): index du bouton de la position actuelle

    Returns:
        Renvoie l'affichage du menu principal avec une liste de rectangles correspondant à chaque bouton 
    """
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

    Args:
        screen (pg.Surface): Surface principale sur laquelle le bouton est affiché.
        rect (pg.Rect): Rectangle définissant la position et la taille du bouton.
        hovered (bool): Indique si le bouton est survolé par la souris (active un effet visuel plus lumineux au niveau des bordures).

    Returns:
        Dessine directement sur la surface du bouton donnée.
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

    Cette fonction crée la boucle d'événements du menu d'accueil. 
    Elle affiche le fond, les boutons (Nouvelle partie, Charger, Options, Quitter),
    et gère la navigation via le clavier et la souris. 
    Lorsqu'une option est sélectionnée, elle renvoie l'état correspondant du jeu.

    Returns:
        UIState: l'état du jeu choisi dans le menu.
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
    Affiche et gère la section "options" (3ème bouton dans le menu principal).
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

def draft_three_rooms(row: int):
    """ Tire trois salles compatibles avec la rareté. """
    specs = list(Rooms.ROOMS_DB.values())
    out = []

    for _ in range(3):
        lvl = Doors.level_by_row(row)

        if lvl == 0:
            rare_ok = ("Common","Commonplace","Standard",None)
        elif lvl == 1:
            rare_ok = ("Unusual","Rare","Standard")
        else:
            rare_ok = ("Rumored","Epic","Very Rare","Rare")

        pool = [s for s in specs if s.rarity_label in rare_ok]
        out.append(random.choice(pool))

    return out

def reroll_draft(row: int, player: joueur, draft_list):
    """ Reroll du draft si joueur possède un dé. """
    if player.des <= 0:
        return draft_list, False
    player.des -= 1
    return draft_three_rooms(row), True

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

# =======================
#  TRIANGLE DIRECTIONNEL
# =======================

def draw_direction_hint(screen, rect, direction: Orientation):
    """
    Dessine un triangle blanc propre sur le bord de la salle pour indiquer
    la direction sélectionnée par le joueur.
    """
    SIZE = 20

    if direction == Orientation.N:
        pts = [
            (rect.centerx, rect.top + 5),
            (rect.centerx - SIZE, rect.top + 25),
            (rect.centerx + SIZE, rect.top + 25)
        ]

    elif direction == Orientation.S:
        pts = [
            (rect.centerx, rect.bottom - 5),
            (rect.centerx - SIZE, rect.bottom - 25),
            (rect.centerx + SIZE, rect.bottom - 25)
        ]

    elif direction == Orientation.E:
        pts = [
            (rect.right - 5, rect.centery),
            (rect.right - 25, rect.centery - SIZE),
            (rect.right - 25, rect.centery + SIZE)
        ]

    elif direction == Orientation.O:
        pts = [
            (rect.left + 5, rect.centery),
            (rect.left + 25, rect.centery - SIZE),
            (rect.left + 25, rect.centery + SIZE)
        ]

    pg.draw.polygon(screen, (255,255,255), pts)
    pg.draw.polygon(screen, (0,0,0), pts, width=2)

# ============================================================
#  DESSIN DE LA GRILLE
# ============================================================

def grid_rect(r, c):
    """ Dimmensionnement du plateau du jeu """
    x = PAD + c * (CELL + GAP)
    y = PAD + r * (CELL + GAP)
    return pg.Rect(x, y, CELL, CELL)

def draw_board(screen, room_grid, player: joueur, img_entree, img_anti, active_direction):
    """ Construire le plateau de jeu à gauche de l'écran 

    Args:
        screen (pygame.surface): Fond ert formes des grilles   
        room_grid (list[list[Room|None]]): Grille contenant les salles explorées
        player (joueur): position actuelle du joueur
        img_entree: image de l’entrée
        img_anti: image de l’anti-chambre
        active_direction (Orientation|None): direction sélectionnée pour déplacement
    """
    screen.fill(BG2, pg.Rect(0,0,BOARD_W,H))

    for r in range(ROWS):
        for c in range(COLS):
            rect = grid_rect(r,c)
            room = room_grid[r][c]

            if (r,c) == ENTRY_POS:
                if img_entree:
                    screen.blit(img_entree, img_entree.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (90,200,255), rect, border_radius=10)

            elif (r,c) == ANTI_POS:
                if img_anti:
                    screen.blit(img_anti, img_anti.get_rect(center=rect.center))
                else:
                    pg.draw.rect(screen, (255,160,90), rect, border_radius=10)

            else:
                if room:
                    pg.draw.rect(screen, ROOM_COL, rect, border_radius=8)

            if (r,c) == (player.ligne, player.colonne):
                pg.draw.rect(screen, WHITE, rect, width=3, border_radius=10)

                if active_direction:
                    draw_direction_hint(screen, rect, active_direction)
# ======================
#  SIDEBAR / INVENTAIRE 
# ======================

def draw_sidebar(screen, font, big, player: joueur, current_room_name, icons, last_message, step_flash, step_flash_time):
    """ Construire l'inventaire à droite de l'écran 

    Args:
        screen (pygame.surface): Fond et formes des grilles  
        font (pygame.font): La police d'écriture 
        big (pygame.font.Font): Agrandir la police pour les titres
        player (joueur): instance contenant l’inventaire et ressources
        current_room_name (str): nom de la salle actuelle
        icons (dict[str,Surface]): icônes disponibles
        last_message (str): message (loot, erreur...)
        step_flash (str): texte +1 / -1 à afficher
        step_flash_time (float): temps restant
    """
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

    xs = [x0+60, x0+200, x0+340]

    for i,spec in enumerate(draft_list):
        col = (0,120,255) if i==focus_idx else TEXT_DARK
        txt = font.render(spec.name, True, col)
        screen.blit(txt, txt.get_rect(center=(xs[i], 180)))

    rr = big.render("Redraw (R)", True, (60,60,60))
    screen.blit(rr, rr.get_rect(center=(x0 + SIDEBAR_W//2, 300)))

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
    room_grid[ENTRY_POS[0]][ENTRY_POS[1]] = Rooms.generate_room("ENTRANCE_HALL", row=ENTRY_POS[0])
    room_grid[ANTI_POS[0]][ANTI_POS[1]]   = Rooms.generate_room("ANTECHAMBER",   row=0)

    state = UIState.MENU
    active_direction = None
    last_message = None
    draft_list = None
    focus_idx = 0

    step_flash = None
    step_flash_time = 0

    running = True
    while running:

        # GAME OVER
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

        # MENU
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

        # PLAYING
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

                        new_r, new_c = r, c
                        if dir == Orientation.N: new_r -= 1
                        if dir == Orientation.S: new_r += 1
                        if dir == Orientation.E: new_c += 1
                        if dir == Orientation.O: new_c -= 1

                        # perte de 1 pas
                        player.pas -= 1
                        step_flash = "-1"
                        step_flash_time = 1.0

                        if player.pas <= 0:
                            state = UIState.GAME_OVER
                            continue

                        # Nouvelle salle ?
                        if room_grid[new_r][new_c] is None:
                            player.ligne, player.colonne = new_r, new_c
                            draft_list = draft_three_rooms(new_r)
                            focus_idx = 0
                            active_direction = None
                            state = UIState.DRAFT
                            continue

                        # Salle connue
                        player.ligne, player.colonne = new_r, new_c
                        msg = apply_room_loot(player, room_grid[new_r][new_c])

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

        # DRAFT
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
                        draft_list, _ = reroll_draft(player.ligne, player, draft_list)

                    elif e.key in (pg.K_SPACE, pg.K_RETURN):
                        spec = draft_list[focus_idx]
                        room = Rooms.generate_room(spec.key, row=player.ligne)
                        room_grid[player.ligne][player.colonne] = room

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
