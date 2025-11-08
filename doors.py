from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import Dict, Optional, Any, Set, Tuple, List
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
  
class Orientation(str, Enum):
    """orientations cardinales utilisables par les portes 
       Membres: 
            N: Nord 
            E: est
            S: sud 
            o: ouest
            Remarque: concue pour une grille 2d en repere écran ou l'axe 
            augments vers le bas """
    N = "N"
    E = "E"
    S = "S"
    O = "O"
class Rarity(IntEnum):
    """Rareter typeé des portes 
    Niveaux: commmon (0): porte commune, occurance eleveé 
              RARE(1): Porte rare, occurance moyenne
              EPIC(2): Porte épique , occurance faible 
              usage: échelle ordinale pour la génération, l'equilibrage et l'affichage
              """
    COMMON =0 
    RARE = 1
    EPIC = 2
class DoorState(str, Enum):
    """Etat possible d'une porte 
       Membre :
       UNLOCKED: Porte déverrouillée
       LOCKED : verouiller 
       DOUBLE_LOUCKED: Porte doublement verouilleé 
       """
    UNLOCKED = "UNLOCKED"
    LOCKED = "LOCKED"
    DOUBLE_LOCKED = "DOUBLE_LOCKED"
class RoomShape(Enum):
    """Topologie de la salle 
        Membres:FOUR_WAY: quatre portes(N,E,S,O)
                T_SHAPE: trois portes en T 
                L_shape: deux portes adjacentes 
                STRAIGHT: deux portes opposées 
                DEAD_END: Une seule porte 
                SPECIAL: Cas irréguliers ou spécifiques 
                """
    FOUR_WAY = auto()
    T_SHAPE =  auto()
    L_SHAPE =  auto()
    STRAIGHT = auto()
    DEAD_END = auto()
    SPECIAL =  auto()

def default_state_from_rarity(r: Rarity) -> DoorState:
    """convertit une rareter en état par défaut de porte 
       Args:
       r (Rarity): Rareté (COMMON, RARE, EPIC).
       Returns:
       DoorState: état initial associé a la rareté
       """
    return{
        Rarity.COMMON: DoorState.UNLOCKED,
        Rarity.RARE: DoorState.LOCKED,
        Rarity.EPIC: DoorState.DOUBLE_LOCKED,

    }[r]
def shape_Orientations(shape: RoomShape)-> Tuple [Orientation, ...]:
    """
    Renvoie les orientations actives associées a une forme de salle 
    Args: 
        shape(RoomShape): type de salle (FOUR_WAY, T_SHAPE, L_SHAPE, STRAIGHT, DEAD_END, SPECIAL)
    Returns:
          Tuple[Orientation,..]: Tuple des orientations présentes
           convention d'ordre : (N,E,S,O) quand applicable
            pour special, renvoie un tuple vide 
    Details:
        - FOUR_WAY  → (N, E, S, O)
        - T_SHAPE   → (N, E, O)    # T ouvert vers le nord par convention
        - L_SHAPE   → (N, E)       # deux portes adjacentes
        - STRAIGHT  → (N, S)       # deux portes opposées
        - DEAD_END  → (S,)         # cul-de-sac orienté sud par convention
        - SPECIAL   → ()           # cas irrégulier géré ailleurs
        """
    if shape == RoomShape.FOUR_WAY:
        return (Orientation.N,Orientation.E,Orientation.S, Orientation.O)
    if shape == RoomShape.T_SHAPE:
        return (Orientation.N,Orientation.E, Orientation.O)
    if shape == RoomShape.L_SHAPE:
        return (Orientation.N,Orientation.E)
    if shape == RoomShape.STRAIGHT:
        return (Orientation.N,Orientation.S)
    if shape == RoomShape.DEAD_END:
        return (Orientation.S)
    return tuple() #SPECIAL

@dataclass
class Door:
    """Representation d'une porte et son etat de verrouillage 

       Args:
        rarity(Rarity) : Rareté de la porte 
        state(DoorState): etat initial de la porte 
       Returns:
        Door: instance initialisée respectant l'invariant.
       Invariant:
        state->{UNLOCKED, LOCKED, DOUBLE_LOCKED}
     """
    rarity: Rarity
    state: DoorState
    def open(self, inventory: set[str])-> bool:
        """ouvre la porte selon la cle disponible et met la porte unlocked apres
            Args:
            inventory set[str]: ensemble des clés détenues 
            Returns:
             bool: True si l'ouverture aboutit, false sinon """
        if self.state == DoorState.UNLOCKED:
            return True
        if self.state == DoorState.LOCKED:
            if "key" in inventory or f"key_{int(self.rarity)}" in inventory:
                self.state = DoorState.UNLOCKED
                return True
            return False 
        if self.state == DoorState.DOUBLE_LOCKED:
            if "master_key" in inventory and f"key_{int(self.rarity)}" in inventory:
                self.state = DoorState.UNLOCKED
                return True
            return False
        return False
    
@dataclass(frozen=True)
class RoomSpec:
     """Spécification statique d'un type de salle.

    Rôle:
        Décrit les caractéristiques fixes une salle (identité, forme, coût, comportement des portes).

    Args:
        key (str): Identifiant unique de la salle.
        name (str): Nom affiché.
        desc (str): Description textuelle.
        shape (RoomShape): Topologie géométrique (FOUR_WAY, L_SHAPE, etc.).
        icon (Optional[str]): Icône ou image associée.
        tags (Tuple[str, ...]): Étiquettes de catégorisation (ex. 'magique', 'piège').
        rarity_label (Optional[str]): Indication de rareté textuelle.
        cost_gems (Optional[int]): Coût d'accès en gemmes.
        door_behavior (Optional[str]): Comportement particulier des portes.
        exits (Optional[int]): Nombre de sorties pour les salles SPECIAL.

    Returns:
        RoomSpec: Instance immuable contenant la description complète d'une salle.
    """
     Key: str
     name: str
     desc: str
     shape: str
     icon: RoomShape
     icon: Optional [str]=None 
     tags: Tuple[str, ...] = ()
     rarity_label: Optional [str]= None
     cost_gems: Optional [int]=None
     door_behavior: Optional [str]= None
     exits: Optional [int]= None


@dataclass
class Room:
    """Représente une salle concrète issue d un modèle statique, avec ses portes,
    son contenu et ses effets temporaires.

    Args:
        spec (RoomSpec): Référence à la spécification statique de la salle.
        doors (Dict[Orientation, Door]): Dictionnaire orientation → porte.
        loot (Tuple[str, ...]): Objets ou ressources trouvables.
        effects (Dict[str, Any]): États/effets actifs (ex. 'active_doors').

    Returns:
        Room: Instance initialisée avec ses composants dynamiques.
    """
    spec: RoomSpec
    doors: Dict[Orientation, Door] = field(default_factory=dict)
    loot: Tuple[str, ...] = ()
    effects: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict:
        """Génère un résumé sérialisable (affichage, debug, sauvegarde JSON).

        Returns:
            dict: Infos générales, forme, tags, état des portes, effets actifs.
        """
        return {
            "key": self.spec.key,
            "name": self.spec.name,
            "desc": self.spec.desc,
            "shape": self.spec.shape.name,
            "tags": list(self.spec.tags),
            "doors": {
                d.value: {"rarity": int(dr.rarity), "state": dr.state.value}
                for d, dr in self.doors.items()
            },
            "effects": self.effects,
        }
    def on_enter(self, rng: Optional[random.Random] = None) -> None:
        """Applique la logique d entrée lorsque la salle est visitée.

        Rôle:
            Initialise ou met à jour l état des portes et des effets spéciaux
            en fonction du type de salle.

        Cas particuliers:
            - VESTIBULE :
                • Garantit 4 portes présentes.
                • Verrouille exactement une porte au hasard, déverrouille les autres.
                • Enregistre la direction verrouillée dans effects['vestibule_locked'].
            - ROTUNDA :
                • Active exactement deux portes (ou moins si indisponibles) choisies au hasard.
                • Enregistre les directions actives dans effects['active_doors'].

        Effets de bord:
            - Peut créer des portes manquantes (pour VESTIBULE) avec état LOCKED par défaut.
            - Modifie létat des portes existantes (UNLOCKED/LOCKED).
            - Met à jour le dictionnaire self.effects.

        Args:
            rng (Optional[random.Random]): Générateur pseudo-aléatoire à utiliser.
                Si None, une instance locale est créée.

        Returns:
            None
        """
        if rng is None:
            rng = random.Random()
        if self.spec.key == "VESTIBULE":
            if len(self.doors) < 4:
                for d in (Orientation.N, Orientation.E, Orientation.S, Orientation.O):
                    self.doors.setdefault(d, Door(rarity=Rarity.COMMON, state=DoorState.LOCKED))
            all_dirs = list(self.doors.keys())
            if all_dirs:
                locked_dir = rng.choice(all_dirs)
                for d, door in self.doors.items():
                    door.state = DoorState.LOCKED if d == locked_dir else DoorState.UNLOCKED
                self.effects["vestibule_locked"] = locked_dir.value
        if self.spec.key == "ROTUNDA":
            active = rng.sample(list(self.doors.keys()), k=min(2, len(self.doors)))
            self.effects["active_doors"] = [d.value for d in active]
    
    def rotate_rotunda(self) -> None:
        """
    Fait pivoter les deux portes actives d'une salle de type ROTUNDA.

    Rôle:
        - Vérifie que la salle correspond bien à une ROTUNDA.
        - Récupère les deux portes actuellement actives depuis effects['active_doors'].
        - Fait tourner cette paire d'une position dans le sens horaire
          selon l'ordre [N, E, S, O].
        - Met à jour effects['active_doors'] avec les nouvelles directions actives.

    Args:
        self (Room): instance de la salle courante.

    Returns:
        None: la méthode agit par effet de bord sur self.effects.
    """
        
        if self.spec.key != "ROTUNDA":
            return
        dirs = [Orientation.N, Orientation.E, Orientation.S, Orientation.O]
        active = self.effects.get("active_doors")
        if not active:
            return
        pair = [Orientation(x) for x in active]
        start_idx = (dirs.index(pair[0]) + 1) % 4
        new_pair = (dirs[start_idx], dirs[(start_idx + 2) % 4])
        self.effects["active_doors"] = [new_pair[0].value, new_pair[1].value]

