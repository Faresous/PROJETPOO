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
# classe pour les pieces du manoire 
class piece:
  #represnete une seule piece dans le manoire contient toute les caracteristique 
  def __init__(self,nom,rarete,cout_gemmes,description,chemin_image):
      #mes attribut
      self.nom=nom
      self.rarete=rarete     # un chiffre par exemple de 0 a 3 (3 tres rare )
      self.cout_gemmes=cout_gemmes
      self.description=description   # pour decrire l'effet spéciale de la piece 
      self.chemin_image=chemin_image   # le lien vers l'image a afficher 
    # une liste qui contiendra les objet trouver dans cette piece
      self.objets_dans_la_piece=[]
      #un dictionnaire pour les portes (nord: 0 et sud=1 par exemple ) 0=deverouiller 1= verouiller 2= double tour 
      self.portes={}

def resumer(self):
    #Renvoie les informations importantes de la piéce
    return{
        "nom": self.nom,
        "rarete": self.rarete,
        "cout": self.cout_gemmes,  #le cout d'entreé 
        "portes": dict(self.portes),  #copie l'etat des portes 
        "objets": len(self.objets_dans_la_piece)  #le nombre d'objet présents 
    }
    
def entrer(self,joueur):

    #tente de faire entrer le joueur dans la piéce si le joueur a assez de gammes ou pas 
    if joueur.gemmes >= self.cout_gemmes:  #assez de gemmes pour payer le cout
        joueur.gemmes-=self.cout_gemmes     #debite le cout en gemmes sur le joueur 
        return True 
    else:
        return False 
  