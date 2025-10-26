def add_item(self, item,quantite):
    """ Ajoute un objet à l'inventaire

    Args:
        item (): nom de l'attribut à ajouter
        quantite(int): quantité à ajouter

    Returns:
        True si l'ajout a bien été fait, False sinon
    """

    items = {'shovel', 'hammer', 'lockpick', 'metal_detector', 'rabbit_foot'}
    
    if not isinstance(quantite, int) or quantite < 0:
        return False

    # Objets permanents 
    if item in items :
        if hasattr(self, items):
            self.permanent_items.add(item)
            print(f"{self.item} a été ajouté ")
            return True
        return False
    
    # Objets consommables
    if hasattr(self, item):
        if isinstance(getattr(self, item), int):
            setattr(self, item, getattr(self, item) + quantite)
            print(f"Le joueur a ramassé {quantite} {item} !")      
            return True
        return False