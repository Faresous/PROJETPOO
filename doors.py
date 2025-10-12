import random
rng = random.Random(seed)          

ROWS = 9  # nb de lignes

def door_level_by_row(row, rows=ROWS, rng=random):
    if row == 0:
        return 0
    if row == rows - 1:
        return 2
    # progression pondérée
    x = row / (rows - 1)
    # poids linéaires simples
    w0 = max(0.0, 1.0 - 1.5*x)     # diminue
    w1 = 0.5 + 0.5*(1 - abs(2*x-1))# cloche au milieu
    w2 = 0.2 + 1.3*x               # augmente
    return rng.choices([0,1,2], weights=[w0,w1,w2], k=1)[0]

    def tirage_aléatoire_doors(row,rng=random):
        # North,Est,South,Ouest
        return {d: door_level_by_row(row, rng=rng) for d in ("N","E","S","O")}

# il restera à implementer les differentes biban (toutes la liste sur wikipedia) + les caractéristiques de chaque portes (effets speciaux ect..)
