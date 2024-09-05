"""
Create objects for each of the features in the game:
    - Monastery
    - Cities
    - Farms
    - Roads
"""

from Carcassonne_Game import Carcassonne
from Carcassonne_Game.Tile import Tile
from pygameCarcassonneDir.pygameFunctions import city_openings


class Monastery:
    def __init__(self, ID=None, Owner=None):
        if ID is not None:
            self.ID = ID
            self.Owner = Owner
            self.Value = 1

    def CloneMonastery(self):
        Clone = Monastery()
        Clone.ID = self.ID
        Clone.Owner = self.Owner
        Clone.Value = self.Value
        return Clone

    def __repr__(self):
        String = (
            "Monastery ID"
            + str(self.ID)
            + "Value"
            + str(self.Value)
            + "Owner"
            + str(self.Owner)
        )
        return String


class City:
    def __init__(self, ID=None, Value=None, Openings=None, Meeples=[0, 0]):
        if ID is not None:
            self.ID = ID
            self.Pointer = ID
            self.Openings = Openings
            self.Value = Value
            self.Meeples = Meeples
            self.ClosedFlag = False

    def CloneCity(self):
        Clone = City()
        Clone.ID = self.ID
        Clone.Pointer = self.Pointer
        Clone.Openings = self.Openings
        Clone.Value = self.Value
        Clone.Meeples = [x for x in self.Meeples]
        Clone.ClosedFlag = self.ClosedFlag
        return Clone

    def Update(self, OpeningsChange=0, ValueAdded=0, MeeplesAdded=[0, 0]):
        self.Openings += OpeningsChange
        self.Value += ValueAdded
        self.Meeples[1] += MeeplesAdded[1]
        self.Meeples[0] += MeeplesAdded[0]

    def isBlocked(self, state: Carcassonne) -> bool:
        opening_locations = city_openings(state)[self.ID]  # Get the openings for this city

        # Closed cities have no openings
        if self.Openings <= 0:
            return True
        
        # Check each opening location
        for (x, y) in opening_locations:
            # Iterate through all tile types
            for tile_index in range(0, 24):

                # Skip if no tiles of this type are left
                if state.TileQuantities[tile_index] <= 0:
                    continue

                tile = Tile(tile_index)

                for rotation in range(4):  # Check all rotations
                    # Get the surrounding spots for this tile
                    SurroundingSpots = [(x-1, y), (x, y+1), (x+1, y), (x, y-1)]
                    
                    fits, _ = state.doesTileFit(tile, rotation * 90, SurroundingSpots)
                    if fits:
                        return False  # If any tile fits, the city is not blocked

        # If no tile fits in any opening, the city is blocked
        return True

    def __repr__(self):
        return f"""ID={self.ID}, Pointer={self.Pointer}, Value={self.Value}, Openings={self.Openings}, Meeples=Player1: {self.Meeples[0]}, Player2: {self.Meeples[1]}, Closed={self.ClosedFlag}
"""


class Farm:
    def __init__(self, ID=None, Meeples=[0, 0]):
        if ID is not None:
            self.ID = ID
            self.Pointer = ID
            self.CityIndexes = set()
            self.Meeples = Meeples

    def CloneFarm(self):
        Clone = Farm()
        Clone.ID = self.ID
        Clone.Pointer = self.Pointer
        Clone.CityIndexes = set([x for x in self.CityIndexes])
        Clone.Meeples = [x for x in self.Meeples]
        return Clone

    def Update(self, NewCityIndexes=[], MeeplesAdded=[0, 0]):
        for CityIndex in NewCityIndexes:
            self.CityIndexes.add(CityIndex)
        self.Meeples[1] += MeeplesAdded[1]
        self.Meeples[0] += MeeplesAdded[0]

    def __repr__(self):
        String = (
            "Farm ID"
            + str(self.ID)
            + "Ptr"
            + str(self.Pointer)
            + "CI"
            + str(self.CityIndexes)
            + "Mps"
            + str(self.Meeples[0])
            + ","
            + str(self.Meeples[1])
        )
        return String


class Road:
    def __init__(self, ID=None, Value=None, Openings=None, Meeples=[0, 0]):
        if ID is not None:
            self.ID = ID
            self.Pointer = ID
            self.Openings = Openings
            self.Value = Value
            self.Meeples = Meeples

    def CloneRoad(self):
        Clone = Road()
        Clone.ID = self.ID
        Clone.Pointer = self.Pointer
        Clone.Openings = self.Openings
        Clone.Value = self.Value
        Clone.Meeples = [x for x in self.Meeples]
        return Clone

    def Update(self, OpeningsChange=0, ValueAdded=0, MeeplesAdded=[0, 0]):
        self.Openings += OpeningsChange
        self.Value += ValueAdded
        self.Meeples[1] += MeeplesAdded[1]
        self.Meeples[0] += MeeplesAdded[0]

    def __repr__(self):
        String = (
            "Road ID"
            + str(self.ID)
            + "Ptr"
            + str(self.Pointer)
            + "V"
            + str(self.Value)
            + "Ops"
            + str(self.Openings)
            + "Mps"
            + str(self.Meeples[0])
            + ","
            + str(self.Meeples[1])
        )
        return String
