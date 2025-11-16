from objets import Pelle, Marteau, Kit_de_crochetage, Detecteur_de_metaux, Patte_de_lapin

class joueur:
    def __init__(self,ligne_depart,colonne_depart):
        # Position du joueur dans la grille 
        
        self.ligne = ligne_depart
        self.colonne = colonne_depart
        
        # Objets Consomables
        self.pas = 70
        self.orr = 0
        self.gemmes = 100
        self.cles = 100
        self.des = 0
        
        # Objets permanants que le joueur trouvera 
        self.objet_permanents={}

    def move (self, dep_ligne, dep_colonne) :
        """ Déplacement du joueur sur la grille
        Args:
            dep_ligne (int): Déplacement du joueur suivant les lignes 
            dep_colonne (int): Déplacement du joueur suivant les colonnes 
        """
        if self.pas > 0 :
            self.pas -= 1 
            self.ligne += dep_ligne
            self.colonne += dep_colonne
            return True
        
        raise ValueError("L'attribut pas doit être positif ")
    
    def utiliser_gems (self, nb_gems) :
        """ Utiliser et dépenser des gems. Renvoie True si réussi
        Args:
            nb_gems : Nombre de gems à dépenser
         Returns :
            Retourne True si l'ajout a bien été fait False sinon 
        """
        
        if self.gemmes >= nb_gems : 
            self.gemmes -= nb_gems
            print(f"Le joueur a depense {nb_gems} gemmes !")  
            return True
        print(f"Pas assez de gemmes !")  
        return False
    
    def add_item(self, item, quantite):
        """ Ajoute un objet à l'inventaire du joueur

        Args:
            item (str): Nom de l'attribut à ajouter
            quantite(int): quantité à ajouter
        Returns:
            True si l'ajout a bien été fait, False sinon
        """
        
        items = {'Pelle', 'Marteau', 'Kit de crochetage', 'Detecteur de meteaux', 'Patte de lapin'}
        
        # Si la quatité est pas un entier ou si elle est négative : ERREUR !!
        if not isinstance(quantite, int) :
            raise TypeError ("L'attribut quantité doit être un entier")    
        if quantite < 0 :
            raise ValueError("L'attribut quantité doit être positif ")
        
        # Objets permanants
        if item in items :
            if item not in self.objet_permanents:
                if item == 'Pelle':
                    self.objet_permanents[item] = Pelle()
                    
                elif item == 'Marteau':
                    self.objet_permanents[item] = Marteau()
                    
                elif item == 'Kit de crochetage':
                    self.objet_permanents[item] = Kit_de_crochetage()
                    
                elif item == 'Detecteur de meteaux':
                    self.objet_permanents[item] = Detecteur_de_metaux()
                    
                elif item == 'Patte de lapin':
                    self.objet_permanents[item] = Patte_de_lapin()
                    
                print(f"{item} a été ajouté aux objets permanents.")
                
            else:
                print(f"Vous possédez déjà {item}.")
            return True
        
        # Objets consommables
        # REMARQUE : 'item_name' doit être le nom exact de l'attribut (ex: "pas", "orr", "gemmes")
        if hasattr(self, item):
            if isinstance(getattr(self, item), int):
                setattr(self, item, getattr(self, item) + quantite)
                print(f"Le joueur a ramassé {quantite} {item} !")      
                return True
            return False
        
    def synchroniser_inventaire(self, inventaire : dict):
        # Met a jour l'inventaire affiché dans la barre latérale a partir des valeurs réelles du joueur
        inventaire["pas"]=self.pas #copie le nombre de pas du joueur vers l'UI
        inventaire["piéces"]=self.orr
        inventaire["gems"]=self.gemmes
        inventaire["clés"]=self.cles
        inventaire["dés"]=self.des   
        
        inventaire["pelle"] = 1 if "Pelle" in self.objet_permanents else 0
        inventaire["marteau"] = 1 if "Marteau" in self.objet_permanents else 0
        inventaire["kit de crochetage"] = 1 if "Kit de crochetage" in self.objet_permanents else 0
        inventaire["detecteur de meteaux"] = 1 if "Detecteur de meteaux" in self.objet_permanents else 0
        inventaire["patte de lapin"] = 1 if "Patte de lapin" in self.objet_permanents else 0
        
    def utiliser_objet(self, objet):
        """
        Méthode pour que le joueur utilise un objet de l'inventaire
        """
        return objet.utiliser(self)
