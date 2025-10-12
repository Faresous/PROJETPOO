def add_item(self, item,quantite):
    if hasattr(self, item):
        setattr(self, item, getattr(self, item) + quantite)
        print(f"Le joueur a ramassé {quantite} {item} !")
        