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

class Kit_de_crochetage(objetpermanent):
    """
    Permet d ouvrir certaines portes, sans depenser de cle
    """
    def __init__(self):
        super().__init__(
            nom="Kit de crochetage",
            description="Ouvre les portes verrouillées"
        )
        
class Detecteur_de_metaux(objetpermanent):
    """
    Augmente la chance de trouver des cles et des pieces
    """
    def __init__(self):
        super().__init__(
            nom="Detecteur de metaux",
            description="Augmente les chances de trouver des clés et pièces"
        )
        
class Patte_de_lapin(objetpermanent):
    """
    Augmente la chance de trouver tous les objets
    """
    def __init__(self):
        super().__init__(
            nom="Patte de lapin",
            description="Augmente les chances de trouver des objets"
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

class objets_insolites(objet) :
    """
    Autres objets qui redonnent des pas
    
    Args:
        valeur (int): La valeur ou quantité de l'objet
    """
    def __init__(self,nom: str, description: str, valeur: int):
        super().__init__(nom, description)
        self.valeur = valeur
        
    def utiliser(self, joueur):
        if joueur.add_item("pas", self.valeur):
            print(f"{joueur} a mangé {self.nom} et regagne + {self.valeur} pas!")
            self.valeur = 0
            return True
        return False
    
class Pomme(objets_insolites):
    """Redonne 2 pas"""
    def __init__(self):
        super().__init__(
            nom="Pomme",
            description="Redonne 2 pas",
            valeur=2)
     
class Banane(objets_insolites):
    """Redonne 3 pas"""
    def __init__(self):
        super().__init__(
            nom="Banane",
            description="Redonne 3 pas",
            valeur=3) 
        
class Gateau(objets_insolites):
    """Redonne 10 pas"""
    def __init__(self):
        super().__init__(
            nom="Gateau",
            description="Redonne 10 pas",
            valeur=10)    
        
class Sandwich(objets_insolites):
    """Redonne 15 pas"""
    def __init__(self):
        super().__init__(
            nom="Sandwich",
            description="Redonne 15 pas",
            valeur=15)    
        
class Repas(objets_insolites):
    """Redonne 25 pas"""
    def __init__(self):
        super().__init__(
            nom="Repas",
            description="Redonne 25 pas",
            valeur=25)  