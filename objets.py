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

