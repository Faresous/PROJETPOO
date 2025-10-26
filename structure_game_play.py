from abc import ABC, abstractmethod

#_______________________le plan
class objet(ABC):
    #le plan de basse pour n'importe quelle objet dans le jeu 
    def __init__(self, nom, description):
        self.nom=nom
        self.description= description

    # la regle chaque objet enfants doit avoir une méthode utiliser 
    @abstractmethod
    def utiliser(self, joueur):
        pass
#____________________________________
# classes enfants (les objets concrets)
class objetpermanent(objet):
    #un objet que le joueur garde pour toujour elle herite de la classe objet 
    def __init__(self,nom,description):
        #on appelle le constructeur objet pour qu'il gere le nom et la description 
        super().__init__(nom, description)

    def utiliser(self, joueur):
        #on respecte les regles meme si l'action est simple 
        print(f"L'objet {self.nom} est un objet permanent")

class objetconsommable(objet):
    # un objet qui disparait aprés usage elle herite aussi de la classe objet 
    def __init__(self,nom,description,valeur=1):
        super().__init__(nom, description)
        # attribut spécifique aux consommable : leur "valuer" ou "quantité"
        self.valeur=valeur
    
    def utiliser(self, joueur):
        #la logique de consomation sera gérée par fares 
        # la méthode doit exister 
        print(f"le joueur utilise L'objet {self.nom}")


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


# classe pour les joeurs 
class joueur:
    def __init__(self,ligne_depart,colonne_depart):
        # tes attribut 
        #position dde joeur dans la grille 
        self.ligne=ligne_depart
        self.colonne=colonne_depart
        #consomable
        self.pas=70
        self.orr=0
        self.gemmes=2
        self.cles=0
        self.des=0
        #objets permanants que le joueur trouvera 
        self.objet_permanents=[]


       