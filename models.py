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
<<<<<<< HEAD
        return true 
    else:
        return false 
=======
        return True 
    else:
        return False 
>>>>>>> 6db5ac0373ca66a3abf67a14031f5b85e497af9a
  
def resumer(self):
    #Renvoie les informations importantes de la piéce
    return{
        "nom": self.nom,
        "rarete": self.rarete,
        "cout": self.cout_gemmes,  #le cout d'entreé 
        "portes": dict(self.portes),  #copie l'etat des portes 
        "objets": len(self.objets_dans_la_piece)  #le nombre d'objet présents 
    }
<<<<<<< HEAD
    
=======
>>>>>>> 6db5ac0373ca66a3abf67a14031f5b85e497af9a
