from abc import ABC, abstractmethod

class objet(ABC):
    """
    Classe abstraite qui définit le plan de base pour les objets du jeu.
    
    Args:
        nom (str): Le nom de l'objet
        description (str): La description de l'objet
        joueur: Le joueur qui utilise l'objet
    """
    def __init__(self, nom: str, description: str):
        self.nom = nom
        self.description = description
    
    @abstractmethod
    def utiliser(self, joueur):
        pass

# OBJETS PERMANENTS :

class objetpermanent(objet):
    def __init__(self,nom : str, description : str):
        super().__init__(nom, description)

    def utiliser(self, joueur):
        print(f"L'objet {self.nom} est un objet permanent")

class Pelle(objetpermanent):
    """
    Permet de creuser pour trouver des objets
    """
    def __init__(self):
        super().__init__(
            nom="Pelle",
            description="Permet de creuser"
        )
        
class Marteau(objetpermanent):
    """
    Permet de briser les cadenas des coffres, permettant de les ouvrir
    sans depenser de cle.
    """
    def __init__(self):
        super().__init__(
            nom="Marteau",
            description="Permet de briser les cadenas"
        )

# OBJETS CONSOMMABLES :

class objetconsommable(objet):
    """
    Objet qui disparaît après utilisation.
    
    Args:
        valeur (int): La valeur ou quantité de l'objet
    """
    
    def __init__(self,nom: str, description: str, valeur: int):
        super().__init__(nom, description)
        self.valeur=valeur
    
    
    def utiliser(self, joueur):
        """
        Utilise l'objet consommable. 
        """       
        print(f"Le joueur utilise L'objet {self.nom}")
        
        
    def epuise(self):
        """
        Vérifie si l'objet est épuisé.
        """
        return self.valeur <= 0
