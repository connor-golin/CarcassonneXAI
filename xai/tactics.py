import os
import sys
from typing import List

from dataclasses import dataclass
from typing import List, Dict, Optional

sys.path.append(os.path.join(os.getcwd()))

from Carcassonne_Game.Tile_dict import HAS_CITY, HAS_NOT_FARM, HAS_ROAD

@dataclass
class CarcassonneTactic:
    name: str
    description: str
    applicable_scenarios: List[str]
    expected_outcome: str
    difficulty: int  # 1-5, where 1 is easiest and 5 is most difficult
    tile_types: List[int]  # List of tile indices this tactic applies to
    tile_placement: Dict[str, str]  # e.g., {'position': 'north', 'rotation': '90'}
    meeple_placement: Optional[Dict[str, str]]  # e.g., {'position': 'city', 'type': 'knight'}
    counter_strategies: List[str]  # List of strategies that can counter this tactic

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "applicable_scenarios": self.applicable_scenarios,
            "expected_outcome": self.expected_outcome,
            "difficulty": self.difficulty,
            "tile_types": self.tile_types,
            "tile_placement": self.tile_placement,
            "meeple_placement": self.meeple_placement,
            "counter_strategies": self.counter_strategies
        }

    def __str__(self):
        return str(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

def create_carcassonne_tactics() -> List[CarcassonneTactic]:
    tactics = []

    # Road Tactics
    tactics.append(CarcassonneTactic(
        name="Field Division",
        description="Use road pieces to separate two fields, potentially limiting opponents' farm scoring.",
        applicable_scenarios=["Mid-game", "Large shared farm"],
        expected_outcome="Reduce opponent's potential farm points, secure smaller farms",
        difficulty=3,
        tile_types=HAS_ROAD,
        tile_placement={"position": "between_farms", "rotation": "align_road"},
        meeple_placement=None,
        counter_strategies=["Farm Equalising"]
    ))

    tactics.append(CarcassonneTactic(
        name="City Blocking",
        description="Use road pieces to make it difficult for opponents to complete their cities.",
        applicable_scenarios=["Opponent building large city", "Late mid-game"],
        expected_outcome="Force opponent to use specific tiles, potentially leaving city incomplete",
        difficulty=4,
        tile_types=[tile for tile in HAS_ROAD if tile not in HAS_CITY],
        tile_placement={"position": "adjacent_to_opponent_city", "rotation": "road_towards_city"},
        meeple_placement=None,
        counter_strategies=["City completion with road", "Abandoning the city"]
    ))

    # Farm Tactics
    tactics.append(CarcassonneTactic(
        name="Farm Equalising",
        description="Join your small farm to a larger opponent-controlled farm to share points.",
        applicable_scenarios=["Late game", "Opponent has large valuable farm"],
        expected_outcome="Reduce point difference, secure shared farm points",
        difficulty=2,
        tile_types=[tile for tile in range(24) if tile not in HAS_NOT_FARM],
        tile_placement={"position": "adjacent_to_large_farm", "rotation": "align_farm"},
        meeple_placement={"position": "farm", "type": "farmer"},
        counter_strategies=["Field Division"]
    ))

    tactics.append(CarcassonneTactic(
        name="Farm Stealing",
        description="Merge your field with opponent's field when you have a meeple advantage.",
        applicable_scenarios=["Mid to late game", "You have more available meeples"],
        expected_outcome="Gain control of a large farm, potentially earning significant points",
        difficulty=4,
        tile_types=[tile for tile in range(24) if tile not in HAS_NOT_FARM],
        tile_placement={"position": "between_farms", "rotation": "connect_farms"},
        meeple_placement={"position": "farm", "type": "farmer"},
        counter_strategies=["Field Division", "Meeple Conservation"]
    ))

    # Piggybacking Tactic
    tactics.append(CarcassonneTactic(
        name="Piggybacking",
        description="Place 'meepled' tiles in areas your opponent wishes to expand into, such as near monasteries or valuable farms.",
        applicable_scenarios=["Opponent building valuable feature", "Mid-game"],
        expected_outcome="Gain points from opponent's work, force opponent to change strategy",
        difficulty=3,
        tile_types=range(24),  # Can potentially use any tile for this
        tile_placement={"position": "adjacent_to_opponent_feature", "rotation": "maximize_benefit"},
        meeple_placement={"position": "optimal", "type": "appropriate"},
        counter_strategies=["Feature abandonment", "Blocking"]
    ))

    return tactics

def main():
    # Create the tactics database
    tactics_database = create_carcassonne_tactics()
    for tactic in tactics_database:
        print(str(tactic) + "\n")

if __name__ == "__main__":
    main()