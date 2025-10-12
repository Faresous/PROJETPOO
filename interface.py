import pygame as pg



# --- Constantes grille Blue Prince

ROWS, COLS = 9, 5          # 9 x 5

CELL     = 64              # taille case

GAP      = 4               # marge entre cases

PAD      = 40              # marge extérieure

W        = COLS * (CELL + GAP) + PAD * 2 - GAP

H        = ROWS * (CELL + GAP) + PAD * 2 - GAP

FPS      = 60



# Couleurs

BG        = (20, 22, 26)

GRID      = (210, 210, 210)

CURSOR    = (120, 185, 255)

ROOM_COL  = (70, 160, 120)

ENTRY_COL = (90, 200, 255)

ANTI_COL  = (255, 160, 90)

TEXT      = (235, 235, 235)

GHOST     = (80, 85, 95)



# Positions Blue Prince demandées

ENTRY_POS = (ROWS - 1, COLS // 2)  # Entrée: bas milieu -> (8, 2) pour 9x5

ANTI_POS  = (0, COLS // 2)         # Antichambre: haut milieu -> (0, 2)



def grid_rect(r, c):

    x = PAD + c * (CELL + GAP)

    y = PAD + r * (CELL + GAP)

    return pg.Rect(x, y, CELL, CELL)



def draw_grid(screen, rooms, cursor, font):

    screen.fill(BG)



    # Titre discret

    title = font.render("Blue Prince — Grille 9×5", True, TEXT)

    screen.blit(title, (PAD, 8))



    # Dessin cases

    for r in range(ROWS):

        for c in range(COLS):

            rect = grid_rect(r, c)



            # Remplissage pièce

            if rooms[r][c] == 1:

                pg.draw.rect(screen, ROOM_COL, rect, border_radius=8)



            # Entrée et Antichambre

            if (r, c) == ENTRY_POS:

                pg.draw.rect(screen, ENTRY_COL, rect, border_radius=10)

                e_txt = font.render("E", True, BG)

                screen.blit(e_txt, (rect.centerx - e_txt.get_width()//2,

                                    rect.centery - e_txt.get_height()//2))

            if (r, c) == ANTI_POS:

                pg.draw.rect(screen, ANTI_COL, rect, border_radius=10)

                a_txt = font.render("A", True, BG)

                screen.blit(a_txt, (rect.centerx - a_txt.get_width()//2,

                                    rect.centery - a_txt.get_height()//2))



            # Bordure case

            pg.draw.rect(screen, GRID, rect, width=1, border_radius=8)



    # Curseur

    cr = grid_rect(*cursor)

    pg.draw.rect(screen, CURSOR, cr, width=3, border_radius=10)



    # Légende

    legends = [

        "Clic: placer/retirer une pièce",

        "Flèches: déplacer le curseur",

        "Entrée/Espace: placer | Suppr/Backspace: retirer",

        "Échap: quitter",

    ]

    y = H - PAD + 6

    for line in legends:

        t = font.render(line, True, GHOST)

        screen.blit(t, (PAD, y))

        y += t.get_height() + 2



def pos_from_mouse(mx, my):

    # renvoie (r, c) ou None si hors grille

    for r in range(ROWS):

        for c in range(COLS):

            if grid_rect(r, c).collidepoint(mx, my):

                return (r, c)

    return None



def main():

    pg.init()

    screen = pg.display.set_mode((W, H + 72))  # bandeau d’aide

    pg.display.set_caption("Blue Prince — Grille")

    clock = pg.time.Clock()

    font = pg.font.SysFont(None, 28)



    # État simple: matrice de pièces (0=vide, 1=pièce)

    rooms = [[0 for _ in range(COLS)] for _ in range(ROWS)]



    # Verrouille E et A comme tuiles présentes

    rooms[ENTRY_POS[0]][ENTRY_POS[1]] = 1

    rooms[ANTI_POS[0]][ANTI_POS[1]]   = 1



    cursor = [ENTRY_POS[0], ENTRY_POS[1]]

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

                        rooms[r][c] ^= 1  # toggle



        draw_grid(screen, rooms, tuple(cursor), font)

        pg.display.flip()

        clock.tick(FPS)



    pg.quit()



if __name__ == "__main__":

    main()