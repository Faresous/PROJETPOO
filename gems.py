def gems (self, nb_gems) :
    """Ajout de gems :

    Arguments :
        nb_gems (int): Nombre de gems à ajouter 

    Returns :
        Retourne True si l'ajout a bien été fait False sinon 
    """
    if self.gems >= nb_gems : 
        self.gems -= nb_gems
        return True
    return False 