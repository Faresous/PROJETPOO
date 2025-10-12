def gems (self, nb_gems) :
    if self.gems >= nb_gems : 
        self.gems -= nb_gems
        return True
    return False 