def move (self, dep_ligne, dep_colonne) :
    """ Déplacement du joueur sur la grille

    Args:
        dep_ligne (int): Déplacement du joueur suivant les lignes 
        dep_colonne (int): Déplacement du joueur suivant les colonnes 
    """
    self.pas -= 1 
    self.ligne += dep_ligne
    self.colonne += dep_colonne