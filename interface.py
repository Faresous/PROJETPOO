# interface_blueprince
import os, sys
import pygame as pg
from enum import Enum
import random 
from doors import Rooms, DoorState, Orientation, Room

""" Grille Blue Prince """
ROWS, COLS = 9, 5
CELL, GAP, PAD = 64, 4, 40
BOARD_W = COLS * (CELL + GAP) + PAD * 2 - GAP
BOARD_H = ROWS * (CELL + GAP) + PAD * 2 - GAP

SIDEBAR_W = 520  # élargissement inventaire
W = BOARD_W + SIDEBAR_W
H = BOARD_H + 72
FPS = 60

""" taille de l'icone de chaque item (inventaire) """
INV_ICON = 24      # icônes objets permanents/consommables

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

# classe fille de Enum (heritage)
class UIState(Enum):
    """
    Énumération représentant les différents états de l'interface utilisateur du jeu BluePrince.

    Chaque valeur indique dans quelle phase ou écran se trouve actuellement le joueur :
    - MENU : affichage du menu principal (écran d'accueil).
    - PLAYING : jeu en cours (plateau et inventaire affichés).
    - OPTIONS : écran des paramètres (audio, commandes, etc.).
    - QUITTING : fermeture du jeu ou retour au bureau.

    Cette classe permet de gérer simplement la logique de navigation entre les différents écrans
    du jeu sans recourir à des variables booléennes multiples.
    """
    MENU     = 0
    PLAYING  = 1
    OPTIONS  = 2
    QUITTING = 3

# couleur pour le menu principal
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

def draw_main_menu(screen,
                   big,
                   font,
                   bg_img: pg.Surface | None,
                   focus_idx: int) -> list[pg.Rect]:

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
        dark.fill((0, 0, 0, 70))  # léger assombrissement
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
    # ombre
    sh = pg.Surface((rect.w, rect.h), pg.SRCALPHA)
    pg.draw.rect(sh, (0, 0, 0, 60), (0, 0, rect.w, rect.h), border_radius=rect.h // 2)
    screen.blit(sh, (rect.x, rect.y + 4))
    # capsule semi-transparente
    btn = pg.Surface((rect.w, rect.h), pg.SRCALPHA)
    pg.draw.rect(btn, (255, 255, 255, 240 if hovered else 220),
                 (0, 0, rect.w, rect.h), border_radius=rect.h // 2)
    # bord
    pg.draw.rect(btn, ACCENT if hovered else (220, 226, 231),
                 (0, 0, rect.w, rect.h), width=2, border_radius=rect.h // 2)
    screen.blit(btn, rect.topleft)


def run_main_menu(screen, 
                big,
                font,
                clock, 
                assets_dir):
    """
    Affiche et gère le menu principal du jeu.

    Cette fonction crée la boucle d'événements du menu d'accueil. 
    Elle affiche le fond, les boutons (Nouvelle partie, Charger, Options, Quitter),
    et gère la navigation via le clavier et la souris. 
    Lorsqu'une option est sélectionnée, elle renvoie l'état correspondant du jeu.

    Args:
        screen (pg.Surface): Surface principale de la fenêtre Pygame où le menu est affiché.
        big (pg.font.Font): Agrandir la police pour les titres.
        font (pg.font.Font): Police d'écriture de text.
        clock (pg.time.Clock): Horloge Pygame utilisée pour limiter la fréquence d'affichage (FPS).
        assets_dir (str): Chemin vers le dossier contenant les images a implementé.

    Returns:
        UIState: L'état sélectionné par le joueur :
            - UIState.PLAYING  → lancer une nouvelle partie
            - UIState.OPTIONS  → ouvrir le menu des options
            - UIState.QUITTING → quitter le jeu
            - UIState.MENU     → (valeur temporaire pour "Charger", non encore implémenté)
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
                    return act if isinstance(act, UIState) else UIState.MENU  # "LOAD" à brancher
            if event.type == pg.MOUSEMOTION:
                # survol souris met à jour le focus
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

def _run_options(screen: pg.Surface, font: pg.font.Font, big: pg.font.Font, clock: pg.time.Clock):
    """
    Affiche et gère la section "options" (3ème bouton dans le menu principal).

    Args:
        screen (pg.Surface): Surface principale de la fenêtre Pygame où le menu est affiché.
        big (pg.font.Font): Police utilisée pour les titres du menu.
        font (pg.font.Font): Police utilisée pour le texte des boutons.
        clock (pg.time.Clock): Horloge Pygame utilisée pour limiter la fréquence d'affichage (FPS).
        assets_dir (str): Chemin vers le dossier contenant les ressources graphiques du menu (fonds, images, etc.).

    Returns:
        UIState: L'état sélectionné par le joueur :
            - UIState.PLAYING  → lancer une nouvelle partie
            - UIState.OPTIONS  → ouvrir le menu des options
            - UIState.QUITTING → quitter le jeu
            - UIState.MENU     → (valeur temporaire pour "Charger", non encore implémenté)
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
        screen.fill((240, 244, 248))
        screen.blit(big.render("Options", True, TEXT_DARK), (40, 40))
        screen.blit(font.render("Je pense à implementer la langue, peut-être une jauge d'audio, luminosité...", True, MUTED), (40, 110))
        pg.display.flip()
        clock.tick(FPS)

def _start_new_game(inventory, rooms, cursor):
    """
    Initialise une nouvelle partie en réinitialisant l'inventaire, la grille des chambres et le curseur. 

    Args:
        inventory (dict): dictionnaire contenant l'inventaire initial du joueur (nom + quantité). 
        rooms (list[list[int]]): grille des chambres (0 = vide, 1 = chambre présente). 
        cursor (list[int]): position actuelle.  
    
    Returns:
        Renvoie l'état initialisé de l'inventaire, les chambres et la position actuelle pour une nouvelle partie. 
    """
    for r in range(ROWS):
        for c in range(COLS):
            rooms[r][c] = 0
    rooms[ENTRY_POS[0]][ENTRY_POS[1]] = 1
    rooms[ANTI_POS[0]][ANTI_POS[1]]   = 1
    cursor[0], cursor[1] = ENTRY_POS
    inventory.update({"pelle":0, "detecteur":0, "patte":0, "carte":0, "pas":70, "pièces":0, "gems":2, "clés":0, "dés":0})


def init_music():
    """ Music de fond du jeu BluePrince 
     
    Returns:
        Renvoie la musique de fond initialisée et jouée en boucle  
    """
    pg.mixer.init()
    pg.mixer.music.load(os.path.join(ASSETS, "blueprince.mp3"))
    pg.mixer.music.set_volume(1)
    pg.mixer.music.play(-1)

def grid_rect(r, c, x0=0, y0=0):
    """ Dimmensionnement du plateau du jeu 

    Args:
        r (int): le nombre de lignes 
        c (int): le nombres de colonnes 
        x0 (int): l'origine du nomrbes de lignes 
        y0 (int): l'origine du nombres de colonnes 
    
    Returns:
        Renvoie une grille de taille CELL x CELL 
    """
    x = x0 + PAD + c * (CELL + GAP)
    y = y0 + PAD + r * (CELL + GAP)
    return pg.Rect(x, y, CELL, CELL)


def pos_from_mouse(mx, my, x0=0, y0=0):
    """ Position actuel et Bords / limites du plateau de jeu

    Args:
        mx (int): Position du curseur en lignes 
        my (int): Position du curseur en colonnes 
        x0 (int): l'origine du nomrbes de lignes 
        y0 (int): l'origine du nombres de colonnes 
        
    Returns:
        Renvoie la position de la cellule actuel ou None si on est à l'exterieur  
    """
    # clics seulement dans la zone plateau
    if mx >= BOARD_W: 
        return None
    for r in range(ROWS):
        for c in range(COLS):
            if grid_rect(r, c, x0, y0).collidepoint(mx, my):
                return (r, c)
    return None

def load_png(name, size):
    """ Chargement des icons des objets 

    Args:
        name (str): Path de l'icon 
        size (int): Taille de redimensionnement souhaitée
        
    Returns:
        Renvoie l'image redimmensionnée et représentée en icon
    """
    path = os.path.join(ASSETS, name)
    surf = pg.image.load(path).convert_alpha()
    return pg.transform.smoothscale(surf, (size, size))


def draw_board(screen, rooms, font, cursor, img_entree, img_anti):
    """ Construire le plateau de jeu à gauche de l'écran

    Args:
        screen (pygame.surface): Fond ert formes des grilles   
        rooms (list(list(int))): Contient la list des pièces
        cursor (tuple[int,int]): coordonnées du curseur 
        img_entree(pygame.surface): L'image de la chambre d'entrée 
        img_anti(pygame.surface): L'image de l'antichambre 
        
    Returns:
        Retourne le plateau de jeu 
    """
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
    """ Affichage du nom de la chambre actuel

    Args:
        rooms (list(list(int))): Contient la list des pièces
        cursor (tuple[int,int]): coordonnées du curseur 
        
    Returns:
        Renvoie une chaine de caractère avce le nom de la chambre 
    """
    r, c = cursor
    if (r, c) == ENTRY_POS: return "Chambre d'entrée"
    if (r, c) == ANTI_POS:  return "Anti-chambre"
    if rooms[r][c] == 1:    return "Room"
    return "—"


def draw_sidebar(screen, font, big, inventory, room_label, icons):
    
    """ Construire l'inventaire à droite de l'écran 

    Args:
        screen (pygame.surface): Fond et formes des grilles  
        font (pygame.font): La police d'écriture 
        big (pygame.font.Font): Agrandir la police pour les titres
        inventory (dictionnary[str,str]): Dictionnaire contient l'inventaire du joueur 
        room_label (str): Etiquete de la chambre 
        icons (dictionnary[str,pygame.surface]): Icons et noms de chaque item 
           
    Returns:
        Renvoie l'affichage de l'inventaire 
    """
    x0 = BOARD_W
    screen.fill(BG1, pg.Rect(x0, 0, SIDEBAR_W, H))

    # Titre
    screen.blit(big.render("Inventory:", True, TEXT_DARK), (x0 + 24, 24))

    # Deux colonnes: permanents à gauche, consommables à droite
    colL_x = x0 + 24
    colR_x = x0 + SIDEBAR_W // 2 + 20
    name_dx_L = INV_ICON + 10
    name_dx_R = INV_ICON + 10
    val_dx  = 120

    # En-têtes colonnes
    screen.blit(font.render("Permanents", True, MUTED),   (colL_x, 56))
    screen.blit(font.render("Consommables", True, MUTED), (colR_x, 56))

    # Définition des groupes
    permanents   = [("pelle","Pelle"), ("detecteur de méteaux","Détecteur"), ("patte de lapin","Patte de lapin"), ("kit de crochetage","KC"),("marteau","Marteau")]
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
            yL += max(INV_ICON, 28) + 14

    # Colonne droite: consommables (toujours visibles, icônes plus petites)
    yR = 80
    for key, label in consommables:
        qty = inventory.get(key, 0)
        ico = icons.get(key)
        if ico: screen.blit(pg.transform.smoothscale(ico, (INV_ICON, INV_ICON)), (colR_x, yR + 4))
        screen.blit(font.render(label, True, TEXT_DARK), (colR_x + name_dx_R, yR + 6))
        screen.blit(big.render(str(qty), True, TEXT_DARK), (colR_x + val_dx, yR + 2))
        yR += max(INV_ICON, 28) + 14

    # Section pièce actuelle (une seule ligne)
    y_bottom = max(yL, yR) + 12
    screen.blit(big.render(room_label, True, TEXT_DARK), (x0 + 24, y_bottom))

    # Aide
    helpy = H - 56
    screen.blit(font.render("Clic: placer/retirer une pièce", True, MUTED), (x0 + 24, helpy))
    screen.blit(font.render("Flèches/ZQSD: curseur  |  Échap: quitter", True, MUTED), (x0 + 24, helpy + 22))


def opt_obj(name): 

    """ Générer l'icône pour chaque objet, qu'il soit permanent ou temporaire 

    Args:
    name (str) : le nom du fichier de l'objet (example: "shovel.png")
        
    Returns:
    Renvoie un objet image (pygame.Surface) redimmensionné ou None si l'objet n'existe pas.
    """

    p = os.path.join(ASSETS, name)
    return load_png(name, INV_ICON) if os.path.exists(p) else None


""" main (test) """
def main():
    state = UIState.MENU
    pg.init()
    init_music()
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

    """ Icone de chaque chambre/objet (wikipedia du jeu BluePrince) """
    # taille de l'icone des chambres
    icon = CELL - 8

    """ 
        Chargement des icones pour les chambres
        
     """

    # pour l'instant on a que la chambre d'entrée et l'anti-chambre donc apres il faudra implementer
    # une fonction pour généraliser toutes les chambres

    img_entree = None
    if os.path.exists(os.path.join(ASSETS)):
        img_entree = load_png("entree.webp", icon)

    img_anti = None
    if os.path.exists(os.path.join(ASSETS)):
        img_anti = load_png("antichambre.webp", icon)


    icons = {
        # permanents
        "pelle": opt_obj("shovel.png"),
        "detecteur de méteaux": opt_obj("metal-detector.png"),
        "patte de lapin": opt_obj("rabbit_foot.png"),
        "kit de crochetage": opt_obj("lockpick.png"),
        "marteau": opt_obj("hammer.png"),

        # consommables
        "pas": opt_obj("footstep.png"),
        "pièces": opt_obj("money.png"),
        "gems": opt_obj("diamond.png"),
        "clés": opt_obj("key.png"),
        "dés": opt_obj("dice.png"),
    }

    """
     Deroulement de l'inteface en fonction des touches enfoncer par le joueur sur son clavier
     
      """
     # --- boucle principale pilotée par l'état
    running = True
    while running:
        if state == UIState.MENU:
            choice = run_main_menu(screen, big, font, clock, ASSETS)
            if choice == UIState.QUITTING:
                break
            if choice == UIState.OPTIONS:
                _run_options(screen, font, big, clock)
                state = UIState.MENU
                continue
            if choice == UIState.PLAYING:
                _start_new_game(inventory, rooms, cursor)
                state = UIState.PLAYING
                continue

        if state == UIState.PLAYING:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    state = UIState.QUITTING
                elif e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE:
                        state = UIState.MENU
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

            # Rendu jeu
            draw_board(screen, rooms, font, tuple(cursor), img_entree, img_anti)
            room_label = current_room_name(tuple(cursor), rooms)
            draw_sidebar(screen, font, big, inventory, room_label, icons)
            pg.display.flip()
            clock.tick(FPS)

        if state == UIState.QUITTING:
            running = False

    pg.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
