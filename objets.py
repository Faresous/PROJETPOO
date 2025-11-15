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
            print("Vous avez déjà creusé")
            return False

        if "Pelle" in joueur.objet_permanents:
            print("Vous avez utilisez la Pelle pour déterrer quelque chose !")
            
            resultat = random.randint(1, 6) 
            
            if resultat == 1:
                print("Vous déterrez 15 pièces d'or !")
                joueur.add_item("orr", 15) 
            
            elif resultat == 2:
                print("Vous déterrez 1 cle !")
                joueur.add_item("cles", 1)   
                 
            elif resultat == 3:
                print("Vous déterrez 5 pas !")
                joueur.add_item("pas", 5) 
                
            elif resultat == 4:
                print("Vous déterrez 1 gemme !")
                joueur.add_item("gemmes", 1) 
                
            elif resultat == 5:
                print("Vous déterrez 1 de !")
                joueur.add_item("des", 1) 
                
            else: 
                print("... mais vous ne trouvez rien :(")
                
                
            self.deja_utilise = True
            return True
        
        else:
            print("Vous avez besoin d'une pelle pour creuser !")
            return False
        
        
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
            print("Le coffre est déjà ouvert")
            return False
        
        # On vérifie si le joueur a un Marteau
        
        if "Marteau" in joueur.objet_permanents:
            print("Vous utilisez le marteau pour ouvrir le coffre")
            
            resultat = random.randint(1, 4)
            
            if resultat == 1:
                print("Vous trouvez 25 pièces d'or !")
                joueur.add_item("orr", 25) 
                
            elif resultat == 2:
                print("Vous trouvez 10 pas !")
                joueur.add_item("pas", 10) 
                
            elif resultat == 3:
                print("Vous trouvez 1 gemmes !")
                joueur.add_item("gemmes", 1)
                 
            else:
                print("Vous trouvez 2 dés !")
                joueur.add_item("des", 2)
                
            self.deja_utilise = True
            return True
            
        # On vérifie si le joueur a une cle        
        if joueur.cles > 0:
            print("Vous utilisez une clé pour ouvrir le coffre")
            joueur.cles -= 1    # On consomme une clé
            
            resultat = random.randint(1, 4)
            
            if resultat == 1:
                print("Vous trouvez 25 pièces d'or !")
                joueur.add_item("orr", 25) 
                
            elif resultat == 2:
                print("Vous trouvez 10 pas !")
                joueur.add_item("pas", 10) 
                
            elif resultat == 3:
                print("Vous trouvez 1 gemmes !")
                joueur.add_item("gemmes", 1)
                 
            else:
                print("Vous trouvez 2 dés !")
                joueur.add_item("des", 2)
            self.deja_utilise = True
            return True

        print("Le coffre est verrouillé il vous faut une clé ou un marteau.")
        return False
    
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
            print("Le casier est déja ouvert")
            return False
        
        # On vérifie si le joueur a une Clé
        if joueur.cles > 0: 
            
            print("Vous utilisez une clé pour ouvrir le casier")
            
            joueur.cles -= 1 # On consomme la clé
            
            resultat = random.randint(1, 4)
            
            if resultat == 1:
                print("Vous trouvez 5 pièces d'or !")
                joueur.add_item("orr", 5)
                
            elif resultat == 2:
                print("Vous trouvez 1 dé !")
                joueur.add_item("des", 1)
                
            elif resultat == 3:
                print("Vous retrouvez 1 clé !")
                joueur.add_item("cles", 1)
                
            elif resultat == 4:
                print("Vous trouvez 10 pas !")
                joueur.add_item("pas", 10) 
                
            elif resultat == 5:
                print("Vous trouvez 1 gemmes !")
                joueur.add_item("gemmes", 1)
                
            else:
                print("Le casier est vide :(")
                
            self.deja_utilise = True
            return True

        print("Ce casier nécessite une clé pour l'ouvrir")
        return False