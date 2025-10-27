import random
rng = random.Random()          

ROWS = 9  # nb de lignes

def door_level_by_row(row, rows=ROWS, rng=random):

    """ niveau de difficulté de chaque porte en fonction de la ligne 

    Args:
        row (int): indice de la ligne courante (entre 0 et rows-1)  
        rows (int): nombre total de lignes (par défaut à 9)
        rng (random.Random): générateur de nombres aléatoires (import du module random)
        
    Returns:
         Renvoie un entier qui représente le niveau de difficulté de la porte (0: commun, 1: rare, 2: épique)
    """

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

            """ tirage aléatoire des choix des portes en fonction de l'orientation qu'on veut prendre 
        N : North
        E : Est
        S : South
        O : Ouest
    Args:
        row (int): indice de la ligne courante (entre 0 et rows-1)  
        rng (random.Random): générateur de nombres aléatoires (import du module random)
        
    Returns:
        Renvoie un dictionnaire avec pour caractères les orientations et pour valeur la rareté de la porte

    """""
        return {d: door_level_by_row(row, rng=rng) for d in ("N","E","S","O")}

 """
    Remarque de la part de chems : 
     En ce qui concerne la grande classe Doors, avant de faire la partie qui concerne l'héritage et les réunir tous dans la 
     même classe, il faudra rajouter une fonction qui permet d'ouvrir la porte en fonction de si la porte est 
     déverouillée, verrouillée ou verouillée à double tour. 
     Je pense aussi qu'il faudra rajouter une fonction qui permet de résumer tous les caractéristiques de 
     chaque chambre, mais je pense que ce sera dans une autre classe qu'on nommera "Room" ou "Chambre". 
     """
