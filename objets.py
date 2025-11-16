from abc import ABC, abstractmethod
import random

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
        if self.valeur <= 0:
            return f"{self.nom} est déjà mangé."
        reward = self.valeur
        
        if joueur.add_item("pas", self.valeur):
            self.valeur = 0
            return f"Vous mangez {self.nom} et regagnez +{reward} pas!"
            
    
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
        
class objets_interactifs(objet):
    """
    Classe pour les objets avec lesquels le joueur peut interagir
    """
    def __init__(self, nom: str, description: str):
        super().__init__(nom, description)
        self.deja_utilise = False # Pour savoir si l'objet a déjà été utilisé
        
    @abstractmethod
    def utiliser(self, joueur):
        pass
    
    
class endroits_ou_creuser(objets_interactifs):
    """
    Un endroit où le joueur peut creuser en utilisant une pelle
    """
    def __init__(self):
        super().__init__(
            nom="Endroit à creuser",
            description="Endroit ou creuser nécessite une pelle contiennent différents objets consommables")

    def utiliser(self, joueur):
        
        if self.deja_utilise:
            return "Vous avez déjà creusé"

        if "Pelle" in joueur.objet_permanents:
            
            resultat = random.randint(1, 6) 
            self.deja_utilise = True
            
            if resultat == 1:
                joueur.add_item("orr", 15) 
                return "Vous déterrez 15 pièces d'or !"
            
            elif resultat == 2:
                joueur.add_item("cles", 1)   
                return "Vous déterrez 1 cle !"
                 
            elif resultat == 3:
                joueur.add_item("pas", 5) 
                return "Vous déterrez 5 pas !"
                
            elif resultat == 4:
                joueur.add_item("gemmes", 1) 
                return "Vous déterrez 1 gemme !"
                
            elif resultat == 5:
                joueur.add_item("des", 1) 
                return "Vous déterrez 1 de !"
                
            else: 
                return "... mais vous ne trouvez rien :("
        
        else:
            return "Vous avez besoin d'une pelle pour creuser !"
        
        
class coffre(objets_interactifs):
    """
    Peut être ouvert avec un marteau ou une clé et donne des objets consommables
    """
    def __init__(self):
        super().__init__(
            nom="Coffre",
            description="Un coffre verrouillé qui s'ouvre avec un marteau ou une clé."
        )

    def utiliser(self, joueur):
        if self.deja_utilise:
            return  "Le coffre est déjà ouvert" 
        
        # On vérifie si le joueur a un Marteau
        
        if "Marteau" in joueur.objet_permanents:
            self.deja_utilise = True
            resultat = random.randint(1, 4)
            
            if resultat == 1:
                joueur.add_item("orr", 25)
                return "Vous utilisez le marteau et trouvez 25 pièces d'or !" 
                
            elif resultat == 2:
                joueur.add_item("pas", 10) 
                return "Vous utilisez le marteau et trouvez 10 pas !"
                
            elif resultat == 3:
                joueur.add_item("gemmes", 1)
                return "Vous utilisez le marteau et trouvez 1 gemme !"
                 
            else:
                joueur.add_item("des", 2)
                return "Vous utilisez le marteau et trouvez 2 dés !"
            
        # On vérifie si le joueur a une cle        
        if joueur.cles > 0:
            
            self.deja_utilise = True
            joueur.cles -= 1    # On consomme une clé
            
            resultat = random.randint(1, 4)
            
            if resultat == 1:
                joueur.add_item("orr", 25) 
                return "Vous utilisez une clé et trouvez 25 pièces d'or !"
                
            elif resultat == 2:
                joueur.add_item("pas", 10) 
                return "Vous utilisez une clé et trouvez 10 pas !"
                
            elif resultat == 3:
                joueur.add_item("gemmes", 1)
                return "Vous utilisez une clé et trouvez 1 gemme !"
                 
            else:
                joueur.add_item("des", 2)
                return "Vous utilisez une clé et trouvez 2 dés !"

        print("Le coffre est verrouillé il vous faut une clé ou un marteau.")
        
class casier(objets_interactifs) :
    """
    Un casier qui s'ouvre avec une clé et qui donne des objets consommables ou rien
    """
    
    def __init__(self):
        super().__init__(
            nom="Casier",
            description="Un casier qui s'ouvre avec une clé.")
    
    def utiliser(self, joueur):
        if self.deja_utilise:
            return "Le casier est déja ouvert"
        
        # On vérifie si le joueur a une Clé
        if joueur.cles > 0: 
            joueur.cles -= 1 # On consomme la clé
            self.deja_utilise = True

            resultat = random.randint(1, 6) 
            
            if resultat == 1:
                joueur.add_item("orr", 5)
                return "Vous ouvrez le casier et trouvez 5 pièces d'or !" 
                
            elif resultat == 2:
                joueur.add_item("des", 1)
                return "Vous ouvrez le casier et trouvez 1 dé !" 
                
            elif resultat == 3:
                joueur.add_item("cles", 1)
                return "Vous ouvrez le casier et retrouvez 1 clé !" 
                
            elif resultat == 4:
                joueur.add_item("pas", 10) 
                return "Vous ouvrez le casier et trouvez 10 pas !" 
                
            elif resultat == 5:
                joueur.add_item("gemmes", 1)
                return "Vous ouvrez le casier et trouvez 1 gemme !" 
                
            else:
                return "Le casier est vide :(" 

        return "Ce casier nécessite une clé pour ouvrir" 