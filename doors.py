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
        Ouvre la porte selon les clés disponibles puis place l'état à UNLOCKED.
        Règle de décision:
          - UNLOCKED → True
          - LOCKED → True si "key" ou "key_{rarity}"
          - DOUBLE_LOCKED → True si "master_key" ET "key_{rarity}"
        """
        if self.state == DoorState.UNLOCKED:
            return True

        need = f"key_{int(self.rarity)}"
        if self.state == DoorState.LOCKED:
            if "key" in inventory or need in inventory:
                self.state = DoorState.UNLOCKED
                return True
            return False

        if self.state == DoorState.DOUBLE_LOCKED:
            if "master_key" in inventory and need in inventory:
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

        if self.spec.key == "VESTIBULE":
            # S'assure d’avoir 4 portes
            for d in (Orientation.N, Orientation.E, Orientation.S, Orientation.O):
                self.doors.setdefault(d, Door(rarity=Rarity.COMMON, state=DoorState.LOCKED))
            all_dirs = list(self.doors.keys())
            if all_dirs:
                locked_dir = rng.choice(all_dirs)
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
        "FOUNDATION": RoomSpec(
            key="FOUNDATION", name="The Foundation",
            desc="Accès au sous-sol via clé de Basement.",
            shape=RoomShape.STRAIGHT, tags=("blueprint",),
            rarity_label="N/A", cost_gems=0,
            door_behavior="Basement via clé dédiée.",
        ),
        "ENTRANCE_HALL": RoomSpec(
            key="ENTRANCE_HALL", name="Entrance Hall",
            desc="Salle de départ, trois portes en avant.",
            shape=RoomShape.T_SHAPE, tags=("permanent", "blueprint"),
            rarity_label="N/A", cost_gems=0,
        ),
        "SPARE_ROOM": RoomSpec(
            key="SPARE_ROOM", name="Spare Room",
            desc="Peut offrir l’upgrade Spare Foyer.",
            shape=RoomShape.L_SHAPE, tags=("blueprint",),
            rarity_label="Standard", cost_gems=0,
        ),
        "ROTUNDA": RoomSpec(
            key="ROTUNDA", name="Rotunda",
            desc="Salle circulaire qui fait tourner l’accès aux portes.",
            shape=RoomShape.FOUR_WAY, tags=("blueprint", "mechanical"),
            rarity_label="Rare", cost_gems=3,
            door_behavior="Deux portes accessibles à la fois.",
        ),
        "PARLOR": RoomSpec(
            key="PARLOR", name="Parlor",
            desc="Salle standard.",
            shape=RoomShape.L_SHAPE, tags=("blueprint",),
            rarity_label="Standard", cost_gems=0,
        ),
        "BILLIARD_ROOM": RoomSpec(
            key="BILLIARD_ROOM", name="Billiard Room",
            desc="Salle standard.",
            shape=RoomShape.STRAIGHT, tags=("blueprint",),
            rarity_label="Standard", cost_gems=0,
        ),
        "GALLERY": RoomSpec(
            key="GALLERY", name="Gallery",
            desc="Salle standard.",
            shape=RoomShape.STRAIGHT, tags=("blueprint",),
            rarity_label="Standard", cost_gems=0,
        ),
        "CLOSET": RoomSpec(
            key="CLOSET", name="Closet",
            desc="Cul-de-sac contenant des items.",
            shape=RoomShape.DEAD_END, tags=("blueprint", "dead_end"),
            rarity_label="Commonplace", cost_gems=0,
            door_behavior="Cul-de-sac.",
        ),
        "WALKIN_CLOSET": RoomSpec(
            key="WALKIN_CLOSET", name="Walk-in Closet",
            desc="Variante closet.",
            shape=RoomShape.DEAD_END, tags=("blueprint", "dead_end"),
            rarity_label="Commonplace", cost_gems=0,
        ),
        "HALLWAY": RoomSpec(
            key="HALLWAY", name="Hallway",
            desc="Couloir simple.",
            shape=RoomShape.STRAIGHT, tags=("hallway", "commonplace"),
            rarity_label="Commonplace", cost_gems=0,
        ),
        "FOYER": RoomSpec(
            key="FOYER", name="Foyer",
            desc="Déverrouille les portes des Hallways.",
            shape=RoomShape.T_SHAPE, tags=("hallway",),
            rarity_label="Standard", cost_gems=0,
            door_behavior="Effet global sur Hallways.",
        ),
        "VESTIBULE": RoomSpec(
            key="VESTIBULE", name="Vestibule",
            desc="À l’entrée: 1 porte LOCKED, 3 UNLOCKED.",
            shape=RoomShape.FOUR_WAY, tags=("hallway",),
            rarity_label="Standard", cost_gems=0,
            door_behavior="Verrouillage aléatoire d’une porte.",
        ),
        "GREAT_HALL": RoomSpec(
            key="GREAT_HALL", name="Great Hall",
            desc="Grand couloir.",
            shape=RoomShape.FOUR_WAY, tags=("hallway",),
            rarity_label="Standard", cost_gems=0,
        ),
        "AQUARIUM": RoomSpec(
            key="AQUARIUM", name="Aquarium",
            desc="Compte comme plusieurs types.",
            shape=RoomShape.T_SHAPE, tags=("blueprint", "hallway"),
            rarity_label="Unusual", cost_gems=1,
            door_behavior="En tant que Hallway, profite du FOYER.",
        ),
        "SECRET_PASSAGE": RoomSpec(
            key="SECRET_PASSAGE", name="Secret Passage",
            desc="Faux Dead End avec choix de couleur.",
            shape=RoomShape.DEAD_END, tags=("blueprint", "dead_end"),
            rarity_label="Unusual", cost_gems=1,
        ),
        "GARAGE": RoomSpec(
            key="GARAGE", name="Garage",
            desc="Dead End. Clés près de l’entrée.",
            shape=RoomShape.DEAD_END, tags=("blueprint", "dead_end"),
            rarity_label="Standard", cost_gems=0,
        ),
        "VAULT": RoomSpec(
            key="VAULT", name="Vault",
            desc="Dead End avec or.",
            shape=RoomShape.DEAD_END, tags=("blueprint", "dead_end"),
            rarity_label="Unusual", cost_gems=2,
        ),
        "SECURITY": RoomSpec(
            key="SECURITY", name="Security",
            desc="Contrôle des Security Doors.",
            shape=RoomShape.L_SHAPE, tags=("blueprint", "mechanical"),
            rarity_label="Unusual", cost_gems=2,
        ),
        "UTILITY_CLOSET": RoomSpec(
            key="UTILITY_CLOSET", name="Utility Closet",
            desc="Coupe-circuits.",
            shape=RoomShape.DEAD_END, tags=("blueprint",),
            rarity_label="Standard", cost_gems=0,
        ),
        "INNER_SANCTUM": RoomSpec(
            key="INNER_SANCTUM", name="Inner Sanctum",
            desc="Zone à 8 portes via Sanctum Keys.",
            shape=RoomShape.SPECIAL, tags=("special",),
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