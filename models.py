import doors
def synchroniser_inventaire(self, inventaire : dict):
    #met a jour l'inventaire affiché dans la barre latérale a partir des valeurs réelles du joueur
    inventaire["pas"]=self.pas #copie le nombre de pas du joueur vers l'UI
    inventaire["piéces"]=self.orr
    inventaire["gems"]=self.gemmes
    inventaire["clés"]=self.cles
    inventaire["dés"]=self.des
def entrer(self,joueur):

    #tente de faire entrer le joueur dans la piéce si le joueur a assez de gammes ou pas 
    if joueur.gemmes >= self.cout_gemmes:  #assez de gemmes pour payer le cout
        joueur.gemmes-=self.cout_gemmes     #debite le cout en gemmes sur le joueur 
        return true 
    else:
        return false 
  
def resumer(self):
    #Renvoie les informations importantes de la piéce
    return{
        "nom": self.nom,
        "rarete": self.rarete,
        "cout": self.cout_gemmes,  #le cout d'entreé 
        "portes": dict(self.portes),  #copie l'etat des portes 
        "objets": len(self.objets_dans_la_piece)  #le nombre d'objet présents 
    }
def generer_portes(self, ligne):
    #generer automatiquement les portes de la pieces en fonction de la ligne 
    self.portes={
         "nord": doors.door_level_by_row(ligne),  #calcule l'etat de la porte nord selon la ligne 
         "sud": doors.door_level_by_row(ligne),
         "est": doors.door_level_by_row(ligne),
         "ouest": doors.door_level_by_row(ligne),

    }

