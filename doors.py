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
    FOUR_WAY = auto()   # N, E, S, O
    T_SHAPE = auto()    # par convention ouvert vers le Nord: N, E, O
    L_SHAPE = auto()    # adjacentes: N, E
    STRAIGHT = auto()   # opposées: N, S
    DEAD_END = auto()   # cul-de-sac: S
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

    def open(self, inventory: set[str]) -> bool:
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
    def shape_orientations(shape: RoomShape) -> Tuple[Orientation, ...]:
        """Renvoie les orientations actives associées à une forme de salle."""
        if shape == RoomShape.FOUR_WAY:
            return (Orientation.N, Orientation.E, Orientation.S, Orientation.O)
        if shape == RoomShape.T_SHAPE:
            return (Orientation.N, Orientation.E, Orientation.O)
        if shape == RoomShape.L_SHAPE:
            return (Orientation.N, Orientation.E)
        if shape == RoomShape.STRAIGHT:
            return (Orientation.N, Orientation.S)
        if shape == RoomShape.DEAD_END:
            return (Orientation.S,)
        return tuple()  # SPECIAL

    @staticmethod
    def make_for_shape(shape: RoomShape, row: int, rng: Optional[random.Random]) -> Dict[Orientation, Door]:
        """
        Génère les portes d'une salle suivant sa forme et sa raretée.
        """
        dirs = Doors.shape_orientations(shape)
        rng = rng or random.Random()
        out: Dict[Orientation, Door] = {}
        for d in dirs:
            r = Rarity(Doors.level_by_row(row, rng=rng))
            out[d] = Door(rarity=r, state=Doors.default_state_from_rarity(r))
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
    #  Zone neutre, point d’accès
    "FOUNDATION": RoomSpec(
        key="FOUNDATION", name="The Foundation",
        desc="Accès au sous-sol via clé de Basement.",
        shape=RoomShape.STRAIGHT, color=RoomColor.BLUE,
        tags=("blueprint",),
        rarity_label="N/A", cost_gems=0,
        door_behavior="Basement via clé dédiée.",
    ),

    #  Grande salle d’entrée
    "ENTRANCE_HALL": RoomSpec(
        key="ENTRANCE_HALL", name="Entrance Hall",
        desc="Salle de départ, trois portes en avant.",
        shape=RoomShape.T_SHAPE, color=RoomColor.ORANGE,
        tags=("permanent", "blueprint"),
        rarity_label="N/A", cost_gems=0,
    ),

    #  Chambre standard
    "SPARE_ROOM": RoomSpec(
        key="SPARE_ROOM", name="Spare Room",
        desc="Peut offrir l’upgrade Spare Foyer.",
        shape=RoomShape.L_SHAPE, color=RoomColor.VIOLET,
        tags=("blueprint",),
        rarity_label="Standard", cost_gems=0,
    ),

    #  Salle mécanique rotative
    "ROTUNDA": RoomSpec(
        key="ROTUNDA", name="Rotunda",
        desc="Salle circulaire qui fait tourner l’accès aux portes.",
        shape=RoomShape.FOUR_WAY, color=RoomColor.BLUE,
        tags=("blueprint", "mechanical"),
        rarity_label="Rare", cost_gems=3,
        door_behavior="Deux portes accessibles à la fois.",
    ),

    #  Salon / pièce à vivre
    "PARLOR": RoomSpec(
        key="PARLOR", name="Parlor",
        desc="Salle de détente, effets de repos.",
        shape=RoomShape.L_SHAPE, color=RoomColor.VIOLET,
        tags=("blueprint",),
        rarity_label="Standard", cost_gems=0,
    ),

    #  Salle de jeu
    "BILLIARD_ROOM": RoomSpec(
        key="BILLIARD_ROOM", name="Billiard Room",
        desc="Chambre avec effets de regain.",
        shape=RoomShape.STRAIGHT, color=RoomColor.VIOLET,
        tags=("blueprint",),
        rarity_label="Standard", cost_gems=0,
    ),

    #  Galerie d’art
    "GALLERY": RoomSpec(
        key="GALLERY", name="Gallery",
        desc="Salle d’exposition, effets de repos.",
        shape=RoomShape.STRAIGHT, color=RoomColor.VIOLET,
        tags=("blueprint",),
        rarity_label="Standard", cost_gems=0,
    ),

    #  Petit local commun
    "CLOSET": RoomSpec(
        key="CLOSET", name="Closet",
        desc="Dead End contenant des objets communs.",
        shape=RoomShape.DEAD_END, color=RoomColor.BLUE,
        tags=("blueprint", "dead_end"),
        rarity_label="Commonplace", cost_gems=0,
        door_behavior="Cul-de-sac.",
    ),

    #  Variante du précédent
    "WALKIN_CLOSET": RoomSpec(
        key="WALKIN_CLOSET", name="Walk-in Closet",
        desc="Variante du closet, commune.",
        shape=RoomShape.DEAD_END, color=RoomColor.BLUE,
        tags=("blueprint", "dead_end"),
        rarity_label="Commonplace", cost_gems=0,
    ),

    #  Couloir classique
    "HALLWAY": RoomSpec(
        key="HALLWAY", name="Hallway",
        desc="Couloir simple reliant deux pièces.",
        shape=RoomShape.STRAIGHT, color=RoomColor.ORANGE,
        tags=("hallway", "commonplace"),
        rarity_label="Commonplace", cost_gems=0,
    ),

    #  Magasin / foyer d’échange
    "FOYER": RoomSpec(
        key="FOYER", name="Foyer",
        desc="Permet d’échanger des ressources et déverrouille des couloirs.",
        shape=RoomShape.T_SHAPE, color=RoomColor.YELLOW,
        tags=("hallway",),
        rarity_label="Standard", cost_gems=0,
        door_behavior="Effet global sur Hallways.",
    ),

    #  Vestibule : porte aléatoirement verrouillée
    "VESTIBULE": RoomSpec(
        key="VESTIBULE", name="Vestibule",
        desc="À l’entrée: 1 porte LOCKED, 3 UNLOCKED.",
        shape=RoomShape.FOUR_WAY, color=RoomColor.ORANGE,
        tags=("hallway",),
        rarity_label="Standard", cost_gems=0,
        door_behavior="Verrouillage aléatoire d’une porte.",
    ),

    #  Grand hall
    "GREAT_HALL": RoomSpec(
        key="GREAT_HALL", name="Great Hall",
        desc="Grand couloir principal.",
        shape=RoomShape.FOUR_WAY, color=RoomColor.ORANGE,
        tags=("hallway",),
        rarity_label="Standard", cost_gems=0,
    ),

    #  Aquarium-jardin
    "AQUARIUM": RoomSpec(
        key="AQUARIUM", name="Aquarium",
        desc="Salle lumineuse comptant comme jardin intérieur.",
        shape=RoomShape.T_SHAPE, color=RoomColor.GREEN,
        tags=("blueprint", "hallway"),
        rarity_label="Unusual", cost_gems=1,
        door_behavior="Compté comme Hallway et profite du FOYER.",
    ),

    #  Passage secret : effet piégeant
    "SECRET_PASSAGE": RoomSpec(
        key="SECRET_PASSAGE", name="Secret Passage",
        desc="Faux cul-de-sac avec effet imprévisible (piège).",
        shape=RoomShape.DEAD_END, color=RoomColor.RED,
        tags=("blueprint", "dead_end"),
        rarity_label="Unusual", cost_gems=1,
    ),

    #  Garage neutre
    "GARAGE": RoomSpec(
        key="GARAGE", name="Garage",
        desc="Dead End. Clés près de l’entrée.",
        shape=RoomShape.DEAD_END, color=RoomColor.BLUE,
        tags=("blueprint", "dead_end"),
        rarity_label="Standard", cost_gems=0,
    ),

    #  Salle au trésor
    "VAULT": RoomSpec(
        key="VAULT", name="Vault",
        desc="Dead End avec or et gemmes à récupérer.",
        shape=RoomShape.DEAD_END, color=RoomColor.GREEN,
        tags=("blueprint", "dead_end"),
        rarity_label="Unusual", cost_gems=2,
    ),

    #  Salle de contrôle
    "SECURITY": RoomSpec(
        key="SECURITY", name="Security",
        desc="Contrôle des portes mécaniques de sécurité.",
        shape=RoomShape.L_SHAPE, color=RoomColor.BLUE,
        tags=("blueprint", "mechanical"),
        rarity_label="Unusual", cost_gems=2,
    ),

    #  Entretien / maintenance
    "UTILITY_CLOSET": RoomSpec(
        key="UTILITY_CLOSET", name="Utility Closet",
        desc="Coupe-circuits du manoir.",
        shape=RoomShape.DEAD_END, color=RoomColor.BLUE,
        tags=("blueprint",),
        rarity_label="Standard", cost_gems=0,
    ),

    #  Sanctuaire final (rare, mystique)
    "INNER_SANCTUM": RoomSpec(
        key="INNER_SANCTUM", name="Inner Sanctum",
        desc="Grande salle à 8 portes via Sanctum Keys.",
        shape=RoomShape.SPECIAL, color=RoomColor.VIOLET,
        tags=("special",),
        rarity_label="Rare", exits=8,
    ),
}


    # ---------- Usines / Générateurs ----------
    @staticmethod
    def generate_room(spec_key: str, row: int, rng: Optional[random.Random] = None) -> Room:
        """
        Instancie une Room depuis sa RoomSpec, génère ses portes et applique la logique d’entrée.
        """
        rng = rng or random.Random()
        spec = Rooms.ROOMS_DB[spec_key]
        doors = Doors.make_for_shape(spec.shape, row, rng)
        room = Room(spec=spec, doors=doors, effects={})
        room.on_enter(rng)
        return room