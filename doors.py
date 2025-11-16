from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import Dict, Optional, Any, Tuple, List

# =========================================================
# Constantes et RNG
# =========================================================

ROWS_DEFAULT = 9
rng_default = random.Random()

# =========================================================
# Énumérations de base
# =========================================================

class Orientation(str, Enum):
    """Orientations cardinales utilisables par les portes."""
    N = "N"  # Nord
    E = "E"  # Est
    S = "S"  # Sud
    O = "O"  # Ouest

class RoomColor(Enum):
    YELLOW = "YELLOW"  # magasins
    GREEN  = "GREEN"   # jardins: gemmes, creusage, permanents
    VIOLET = "VIOLET"  # chambres: regain de pas
    ORANGE = "ORANGE"  # couloirs: beaucoup de portes
    RED    = "RED"     # pénalités: peu de portes, malus
    BLUE   = "BLUE"    # commun, effets variés


class Rarity(IntEnum):
    """Rareté des portes sur une échelle ordinale."""
    COMMON = 0
    RARE = 1
    EPIC = 2


class DoorState(str, Enum):
    """États possibles d'une porte."""
    UNLOCKED = "UNLOCKED"
    LOCKED = "LOCKED"
    DOUBLE_LOCKED = "DOUBLE_LOCKED"


class RoomShape(Enum):
    """Topologie géométrique d'une salle(différentes formes de salles)."""
    FOUR_WAY = auto()   # 4 portes (N, E, S, O)
    T_SHAPE = auto()    # 3 portes (N, E, S)
    L_SHAPE = auto()    # 2 portes adjacentes (N, E)
    STRAIGHT = auto()   # 2 portes opposées (N, S)
    DEAD_END = auto()   # 1 porte (N)
    SPECIAL = auto()    # cas irréguliers


# ==========================================================
# Données élémentaires - jouabilité des portes et des salles
# ==========================================================

@dataclass
class Door:
    """
    Représentation d'une porte et de son état de verrouillage.
    Invariant: state ∈ {UNLOCKED, LOCKED, DOUBLE_LOCKED}.
    """
    rarity: Rarity
    state: DoorState

    def open(self, resources: dict) -> bool:
        """
        Ouvre la porte en appliquant la règle:
          - UNLOCKED (niv 0): gratuit.
          - LOCKED   (niv 1): coûte 1 clé, OU gratuit si lockpick=True.
          - DOUBLE_LOCKED (niv 2): coûte 1 clé; le lockpick ne fonctionne pas.

        Args:
            resources: dict muté en place, ex:
                {
                    "keys": int,        # nombre de clés disponibles
                    "lockpick": bool,   # kit de crochetage disponible ?
                }

        Returns:
            bool: True si ouverture effectuée, False sinon.
        """

        if self.state == DoorState.UNLOCKED:
            return True

        keys = int(resources.get("keys", 0))
        lockpick = bool(resources.get("kit de crochetage", False))

        if self.state == DoorState.LOCKED:
            if lockpick:
                self.state = DoorState.UNLOCKED
                return True
            if keys > 0:
                resources["keys"] = keys - 1
                self.state = DoorState.UNLOCKED
                return True
            return False

        if self.state == DoorState.DOUBLE_LOCKED:
            if keys > 0:
                resources["keys"] = keys - 1
                self.state = DoorState.UNLOCKED
                return True
            return False

        return False


@dataclass(frozen=True)
class RoomSpec:
    """
    Décrit les caractéristiques fixes: identité, forme, coût, comportement des portes.
    """
    key: str
    name: str
    desc: str
    shape: RoomShape
    color: RoomColor
    icon: Optional[str] = None
    tags: Tuple[str, ...] = ()
    rarity_label: Optional[str] = None
    cost_gems: Optional[int] = None
    door_behavior: Optional[str] = None
    exits: Optional[int] = None


@dataclass
class Room:
    """
    Salle concrète instanciée depuis un RoomSpec, avec ses portes et effets.
    """
    spec: RoomSpec
    rotation: int = 0
    doors: Dict[Orientation, Door] = field(default_factory=dict)
    loot: Tuple[str, ...] = ()
    effects: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict:

        """
        Résumé sérialisable pour affichage, debug ou sauvegarde JSON.
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

    # Logique d’entrée et cas spéciaux (Vestibule, Rotunda)
    def on_enter(self, rng: Optional[random.Random] = None) -> None:
        """
        Applique la logique d'entrée lorsque la salle est visitée.
        - VESTIBULE: garantit 4 portes, 1 LOCKED et 3 UNLOCKED, enregistre la direction verrouillée.
        - ROTUNDA: active exactement deux portes au hasard, stockées dans effects['active_doors'].
        """
        if rng is None:
            rng = random.Random()

        # Dans Room.on_enter, cas VESTIBULE
        if self.spec.key == "VESTIBULE":
        # garantit 4 portes présentes
            for d in (Orientation.N, Orientation.E, Orientation.S, Orientation.O):
                self.doors.setdefault(d, Door(rarity=Rarity.COMMON, state=DoorState.UNLOCKED))
            locked_dir = (rng or random.Random()).choice(list(self.doors.keys()))
            for d, door in self.doors.items():
                door.state = DoorState.LOCKED if d == locked_dir else DoorState.UNLOCKED
            self.effects["vestibule_locked"] = locked_dir.value

        if self.spec.key == "ROTUNDA":
            if self.doors:
                active = rng.sample(list(self.doors.keys()), k=min(2, len(self.doors)))
                self.effects["active_doors"] = [d.value for d in active]

    def rotate_rotunda(self) -> None:
        """
        Fait pivoter les deux portes actives d'une ROTUNDA d'un cran horaire.
        Ordre des directions: [N, E, S, O].
        """
        if self.spec.key != "ROTUNDA":
            return
        active = self.effects.get("active_doors")
        if not active:
            return
        dirs = [Orientation.N, Orientation.E, Orientation.S, Orientation.O]
        pair = [Orientation(x) for x in active]
        start_idx = (dirs.index(pair[0]) + 1) % 4
        new_pair = (dirs[start_idx], dirs[(start_idx + 2) % 4])
        self.effects["active_doors"] = [new_pair[0].value, new_pair[1].value]
    
    
    def apply_color_effects(room: Room, rng: Optional[random.Random] = None) -> None:
        """
        Applique automatiquement les effets associés à la couleur d'une pièce.

        Rôle :
            Cette fonction complète les effets dynamiques d'une salle en fonction
            de sa couleur définie dans RoomSpec.color. Chaque couleur représente
            une catégorie de pièce du manoir Blue Prince, et détermine les bonus,
            malus ou comportements spéciaux lors de l'entrée dans la salle.

        Détail des effets appliqués :
            - 🟡 YELLOW (Magasin) :
                Crée un espace d'échange d'objets où l'or peut être échangé contre des clés.
                L'effet "shop" est activé avec des taux définis dans room.effects["shop"].
            - 🟢 GREEN (Jardin) :
                Génère aléatoirement des gemmes ou un emplacement de creusage ("dig_spot").
                L'effet "garden" contient les ressources disponibles.
            - 🟣 VIOLET (Chambre) :
                Active un effet de repos augmentant les pas disponibles ("regain_steps").
            - 🟠 ORANGE (Couloir) :
                Indique que la salle privilégie les connexions multiples ("prefer_many_doors").
            - 🔴 RED (Pièce piégée) :
                Applique un malus (par exemple une perte de pas) dans "penalty".
            - 🔵 BLUE (Pièce commune) :
                Salle standard sans effet particulier, mais marquée "misc" pour cohérence.

        Args:
            room (Room): Instance de la salle courante dont les effets seront mis à jour.
            rng (Optional[random.Random]): Générateur pseudo-aléatoire à utiliser
                pour les effets variables (par exemple génération de gemmes).
                Si None, un générateur local est instancié.

        Effets de bord:
            Modifie le dictionnaire room.effects en place selon la couleur de la pièce.

        Returns:
            None
        """
        rng = rng or random.Random()
        c = room.spec.color
        if c == RoomColor.YELLOW:
            room.effects["shop"] = {"rates": {"gold_to_key": 1}, "enabled": True}
        elif c == RoomColor.GREEN:
            room.effects["garden"] = {"gems_spawn": rng.choice([0, 1, 2]), "dig_spot": True}
        elif c == RoomColor.VIOLET:
            room.effects["regain_steps"] = 1
        elif c == RoomColor.ORANGE:
            room.effects.setdefault("corridor_hint", "prefer_many_doors")
        elif c == RoomColor.RED:
            room.effects["penalty"] = {"steps_minus": 1}
        elif c == RoomColor.BLUE:
            room.effects.setdefault("misc", True)


# =========================================================
# Classe mère 1 : Doors — toutes les méthodes liées aux portes
# =========================================================

class Doors:
    """
    Espace de nom pour la logique portes:
      - profil de rareté par ligne
      - état par défaut selon rareté
      - orientations actives d"une forme
      - génération des portes d"une salle
      - tirage aléatoire de raretés par orientation
    """
    ROTATION_MAP = {
        Orientation.N: Orientation.E,
        Orientation.E: Orientation.S,
        Orientation.S: Orientation.O,
        Orientation.O: Orientation.N,
    }
    
    @staticmethod
    def rotate_orientation(dir: Orientation, rotation: int) -> Orientation:
        """Fait pivoter une orientation de N degrés (multiples de 90)."""
        if rotation == 0:
            return dir
        if rotation == 90:
            return Doors.ROTATION_MAP[dir]
        if rotation == 180:
            return Doors.ROTATION_MAP[Doors.ROTATION_MAP[dir]]
        if rotation == 270:
            return Doors.ROTATION_MAP[Doors.ROTATION_MAP[Doors.ROTATION_MAP[dir]]]
        return dir
    
    @staticmethod
    def shape_orientations(shape: RoomShape, rotation: int) -> Tuple[Orientation, ...]:
        """
        Renvoie les orientations actives pour une forme ET une rotation données.
        Les formes de base sont (par convention) orientées au Nord.
        """
        base_dirs = []
        if shape == RoomShape.FOUR_WAY:
            base_dirs = [Orientation.S, Orientation.O, Orientation.N, Orientation.E]
        elif shape == RoomShape.T_SHAPE:
            base_dirs = [Orientation.S, Orientation.O, Orientation.E] # T "couché"
        elif shape == RoomShape.L_SHAPE:
            base_dirs = [Orientation.S, Orientation.O]
        elif shape == RoomShape.STRAIGHT:
            base_dirs = [Orientation.S, Orientation.N]
        elif shape == RoomShape.DEAD_END:
            base_dirs = [Orientation.S] # Toujours vers le "haut" par défaut
        
        # Applique la rotation demandée à chaque porte de base
        rotated_dirs = [Doors.rotate_orientation(d, rotation) for d in base_dirs]
        return tuple(rotated_dirs)
    
    
    @staticmethod
    def level_by_row(row: int, rows: int = ROWS_DEFAULT, rng: random.Random = rng_default) -> int:
        """
        Niveau de difficulté en fonction de la ligne.
        0: commun, 1: rare, 2: épique.
        """
        if row == 0:
            return 0
        if row == rows - 1:
            return 2
        x = row / (rows - 1)
        w0 = max(0.0, 1.0 - 1.5 * x)         # décroît
        w1 = 0.5 + 0.5 * (1 - abs(2 * x - 1))# cloche centrale
        w2 = 0.2 + 1.3 * x                   # croît
        return rng.choices([0, 1, 2], weights=[w0, w1, w2], k=1)[0]

    @staticmethod
    def default_state_from_rarity(r: Rarity) -> DoorState:
        """Map rareté → état par défaut."""
        return {
            Rarity.COMMON: DoorState.UNLOCKED,
            Rarity.RARE: DoorState.LOCKED,
            Rarity.EPIC: DoorState.DOUBLE_LOCKED,
        }[r]

    @staticmethod
    def make_for_shape(shape: RoomShape, row: int, rotation: int, rng: Optional[random.Random]) -> Dict[Orientation, Door]:
        """
        Génère les portes d'une salle suivant sa forme, 
        sa rotation, et sa rareté (rangée).
        """
        # 1. Calcule les directions des portes APRES rotation
        dirs = Doors.shape_orientations(shape, rotation)
        rng = rng or random.Random()
        out: Dict[Orientation, Door] = {}
        
        for d in dirs:
            # 2. Détermine le niveau de difficulté
            level = Doors.level_by_row(row, rng=rng)
            rarity = Rarity(level)
            
            # 3. Détermine l'état de verrouillage
            state = Doors.default_state_from_rarity(rarity)
            
            # 4. Crée la porte
            out[d] = Door(rarity=rarity, state=state)
            
        return out


# =========================================================
# Classe mère 2 : Rooms — base de données et usines de salles
# =========================================================

class Rooms:
    """
    Espace de nom pour la logique salles:
      - base de données ROOMS_DB
      - instanciation de Room (portes + effets d'entrée)
      - catalogage utilitaire des 41 portes pour test/équilibrage
    """

        # ---------- Base de données intégrée ----------
    ROOMS_DB: Dict[str, RoomSpec] = {
        # 001–012
        "FOUNDATION": RoomSpec(key="FOUNDATION", name="Foundation",
            desc="Pièce permanente avec accès au sous-sol.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","permanent"), rarity_label="Rare", cost_gems=0),

        "ENTRANCE_HALL": RoomSpec(key="ENTRANCE_HALL", name="Entrance Hall",
            desc="Point de départ quotidien. Trois portes.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("permanent","blueprint"), rarity_label="N/A", cost_gems=0),

        "SPARE_ROOM": RoomSpec(key="SPARE_ROOM", name="Spare Room",
            desc="Salle neutre pouvant être améliorée.", shape=RoomShape.STRAIGHT,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Common"),

        "ROTUNDA": RoomSpec(key="ROTUNDA", name="Rotunda",
            desc="Salle rotative. Deux portes actives à la fois.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","mechanical"), rarity_label="Common", cost_gems=3),

        "PARLOR": RoomSpec(key="PARLOR", name="Parlor",
            desc="Puzzle du salon.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","puzzle"), rarity_label="Common"),

        "BILLIARD_ROOM": RoomSpec(key="BILLIARD_ROOM", name="Billiard Room",
            desc="Puzzle de fléchettes.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","puzzle"), rarity_label="Common"),

        "GALLERY": RoomSpec(key="GALLERY", name="Gallery",
            desc="Galerie, liée à Room 8.", shape=RoomShape.STRAIGHT,
            color=RoomColor.BLUE, tags=("blueprint","puzzle"), rarity_label="Common"),

        "ROOM_8": RoomSpec(key="ROOM_8", name="Room 8",
            desc="Pièce verrouillée par la clé Room 8.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","puzzle"), rarity_label="Rare"),

        "CLOSET": RoomSpec(key="CLOSET", name="Closet",
            desc="Cul-de-sac avec objets.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Commonplace"),

        "WALKIN_CLOSET": RoomSpec(key="WALKIN_CLOSET", name="Walk-in Closet",
            desc="Variante du closet.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Commonplace"),

        "ATTIC": RoomSpec(key="ATTIC", name="Attic",
            desc="Grenier, dead-end avec 8 objets.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Rare", cost_gems=3),

        "STOREROOM": RoomSpec(key="STOREROOM", name="Storeroom",
            desc="Dead-end: 1 gemme, 1 clé, 1 pièce.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Common"),

        # 013–024
        "NOOK": RoomSpec(key="NOOK", name="Nook",
            desc="Contient toujours 1 clé.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Commonplace"),

        "GARAGE": RoomSpec(key="GARAGE", name="Garage",
            desc="Dead-end. Trois clés au mur.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Unusual", cost_gems=1),

        "MUSIC_ROOM": RoomSpec(key="MUSIC_ROOM", name="Music Room",
            desc="Feuilles de musique, 1 clé spéciale.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard", cost_gems=2),

        "LOCKER_ROOM": RoomSpec(key="LOCKER_ROOM", name="Locker Room",
            desc="Diffuse des clés dans le manoir.", shape=RoomShape.STRAIGHT,
            color=RoomColor.BLUE, tags=("blueprint","spread","mechanical"), rarity_label="Rare", cost_gems=1),

        "DEN": RoomSpec(key="DEN", name="Den",
            desc="Toujours 1 gemme. Portes en T.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Commonplace"),

        "WINE_CELLAR": RoomSpec(key="WINE_CELLAR", name="Wine Cellar",
            desc="Toujours 3 gemmes. Dead-end.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Commonplace"),

        "TROPHY_ROOM": RoomSpec(key="TROPHY_ROOM", name="Trophy Room",
            desc="Musée des trophées. 8 gemmes.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard", cost_gems=5),

        "BALLROOM": RoomSpec(key="BALLROOM", name="Ballroom",
            desc="À l’entrée, fixe les gemmes à 2.", shape=RoomShape.STRAIGHT,
            color=RoomColor.BLUE, tags=("blueprint","entry"), rarity_label="Unusual", cost_gems=2),

        "PANTRY": RoomSpec(key="PANTRY", name="Pantry",
            desc="Fruit aléatoire et 4 pièces.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Commonplace"),

        "RUMPUS_ROOM": RoomSpec(key="RUMPUS_ROOM", name="Rumpus Room",
            desc="Automate diseur de bonne aventure. 8 pièces.", shape=RoomShape.STRAIGHT,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard", cost_gems=1),

        "VAULT": RoomSpec(key="VAULT", name="Vault",
            desc="Dead-end: 40 pièces. Coffres numérotés.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Rare", cost_gems=3),

        "OFFICE": RoomSpec(key="OFFICE", name="Office",
            desc="Terminal: paie, email, diffusion de pièces.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","spread","terminal"), rarity_label="Standard", cost_gems=2),

        # 025–036
        "DRAWING_ROOM": RoomSpec(key="DRAWING_ROOM", name="Drawing Room",
            desc="Un reroll gratuit lors du draft. T-shape.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "STUDY": RoomSpec(key="STUDY", name="Study",
            desc="Rerolls payants jusqu’à 8 fois.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "LIBRARY": RoomSpec(key="LIBRARY", name="Library",
            desc="Découvre des plans moins communs. L-shape.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "CHAMBER_OF_MIRRORS": RoomSpec(key="CHAMBER_OF_MIRRORS", name="Chamber of Mirrors",
            desc="Autorise un second exemplaire de salles. Récompense permanente.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","puzzle"), rarity_label="Unusual"),

        "THE_POOL": RoomSpec(key="THE_POOL", name="The Pool",
            desc="Ajoute Locker Room, Sauna, Pump Room au pool du jour.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "DRAFTING_STUDIO": RoomSpec(key="DRAFTING_STUDIO", name="Drafting Studio",
            desc="Ajoute définitivement un floorplan au pool.", shape=RoomShape.STRAIGHT,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "UTILITY_CLOSET": RoomSpec(key="UTILITY_CLOSET", name="Utility Closet",
            desc="Tableau électrique. Dead-end.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","mechanical","dead_end"), rarity_label="Standard"),

        "BOILER_ROOM": RoomSpec(key="BOILER_ROOM", name="Boiler Room",
            desc="Salle mécanique. Alimente en énergie.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","mechanical"), rarity_label="Standard"),

        "PUMP_ROOM": RoomSpec(key="PUMP_ROOM", name="Pump Room",
            desc="Salle mécanique. Modifie niveaux d’eau. L-shape.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","mechanical"), rarity_label="Standard"),

        "SECURITY": RoomSpec(key="SECURITY", name="Security",
            desc="Terminal sécurité. Paramètre portes électroniques. L-shape.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","mechanical","terminal"), rarity_label="Standard"),

        "WORKSHOP": RoomSpec(key="WORKSHOP", name="Workshop",
            desc="Combine des objets en outils hybrides.", shape=RoomShape.STRAIGHT,
            color=RoomColor.BLUE, tags=("blueprint","mechanical"), rarity_label="Standard"),

        "LABORATORY": RoomSpec(key="LABORATORY", name="Laboratory",
            desc="Expériences; déblocages permanents. L-shape.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","mechanical","terminal"), rarity_label="Standard"),

        # 037–046
        "SAUNA": RoomSpec(key="SAUNA", name="Sauna",
            desc="Demain: +20 pas. Dead-end.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Standard"),

        "COAT_CHECK": RoomSpec(key="COAT_CHECK", name="Coat Check",
            desc="Dépose un objet pour le récupérer un autre jour. Dead-end.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Standard"),

        "MAIL_ROOM": RoomSpec(key="MAIL_ROOM", name="Mail Room",
            desc="Lettre livrée le lendemain. Dead-end.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Standard"),

        "FREEZER": RoomSpec(key="FREEZER", name="Freezer",
            desc="Fige comptes jusqu’au lendemain. Dead-end.", shape=RoomShape.DEAD_END,
            color=RoomColor.BLUE, tags=("blueprint","dead_end"), rarity_label="Standard"),

        "DINING_ROOM": RoomSpec(key="DINING_ROOM", name="Dining Room",
            desc="À rang 8: consommer le plat pour +20/30 pas.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "OBSERVATORY": RoomSpec(key="OBSERVATORY", name="Observatory",
            desc="+1 étoile permanente; constellations.", shape=RoomShape.L_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "CONFERENCE_ROOM": RoomSpec(key="CONFERENCE_ROOM", name="Conference Room",
            desc="Centralise les objets diffusés par d’autres salles. T-shape.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint",), rarity_label="Standard"),

        "AQUARIUM": RoomSpec(key="AQUARIUM", name="Aquarium",
            desc="Compte comme tous les types.", shape=RoomShape.T_SHAPE,
            color=RoomColor.BLUE, tags=("blueprint","hallway"), rarity_label="Unusual", cost_gems=1),

        "ANTECHAMBER": RoomSpec(key="ANTECHAMBER", name="Antechamber",
            desc="Cible visible; portes scellées à rouvrir chaque jour.", shape=RoomShape.FOUR_WAY,
            color=RoomColor.BLUE, tags=("goal-adjacent",), rarity_label="N/A"),
            
        "ROOM_46": RoomSpec(key="ROOM_46", name="Room 46",
            desc="Objectif du jeu. Couronne royale.", shape=RoomShape.SPECIAL,
            color=RoomColor.BLUE, tags=("goal",), rarity_label="Rumored"),
    }



    # ---------- Usines / Générateurs ----------
    @staticmethod
    def generate_room(spec_key: str, row: int,rotation: int = 0, rng: Optional[random.Random] = None) -> Room:
        """
        Instancie une Room depuis sa RoomSpec, génère ses portes et applique la logique dentrée.
        """
        rng = rng or random.Random()
        spec = Rooms.ROOMS_DB[spec_key]
        doors = Doors.make_for_shape(spec.shape, row, rotation, rng)
        room = Room(spec=spec, rotation=rotation,doors=doors, effects={})
        room.on_enter(rng)
        return room