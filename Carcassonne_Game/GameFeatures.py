"""
Create objects for each of the features in the game:
    - Monastery
    - Cities
    - Farms
    - Roads
"""

from Carcassonne_Game import Carcassonne
from Carcassonne_Game.Tile import Tile
from Carcassonne_Game.Tile_dict import CITY_OPENINGS_DICT
from pygameCarcassonneDir.pygameFunctions import rotate_point


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
    def __init__(
        self, ID=None, Value=None, Openings=None, Meeples=[0, 0], all_coordinates=[]
    ):
        if ID is not None:
            self.ID = ID
            self.Pointer = ID
            self.Openings = Openings
            self.Value = Value
            self.Meeples = Meeples
            self.ClosedFlag = False
            self.isBlocked = False
            self.tiles = []

    def CloneCity(self):
        Clone = City()
        Clone.ID = self.ID
        Clone.Pointer = self.Pointer
        Clone.Openings = self.Openings
        Clone.Value = self.Value
        Clone.Meeples = [x for x in self.Meeples]
        Clone.ClosedFlag = self.ClosedFlag
        Clone.isBlocked = self.isBlocked
        Clone.openings_coordinates = [x for x in self.openings_coordinates]
        return Clone

    def Update(self, OpeningsChange=0, ValueAdded=0, MeeplesAdded=[0, 0]):
        self.Openings += OpeningsChange
        self.Value += ValueAdded
        self.Meeples[1] += MeeplesAdded[1]
        self.Meeples[0] += MeeplesAdded[0]

    def AddCoordinate(self, tile):
        if tile not in self.tiles:
            self.tiles.append(tile)

    def isBlocked(self, state: Carcassonne) -> bool:
        if self.Openings <= 0:
            return True

        for x, y in self.all_coordinates:

            print(f"Checking city opening at {x, y}")

            for tile_index in range(0, 24):
                tile = Tile(tile_index)

                for rotation in tile.AvailableRotations:
                    SurroundingSpots = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
                    fits, _ = state.doesTileFit(tile, rotation, SurroundingSpots)
                    if fits:
                        print(f"Tile {tile_index} fits at {x, y}")
                        return False

        self.isBlocked = True
        return True

    def get_occupied_coordinates(self):
        return [tile.coordinates for tile in self.tiles]

    def getOpenings(self, state):
        surroundings = []

        for tile in self.tiles:
            x, y = tile.coordinates
            tile_index = tile.TileIndex
            rotation = tile.Rotation // 90

            if tile_index in CITY_OPENINGS_DICT:
                # Iterate through all city openings lists for the tile
                for city_openings in CITY_OPENINGS_DICT[tile_index]:
                    for city_opening in city_openings:
                        # Determine the surrounding coordinates based on city openings
                        if city_opening == 0:
                            dx, dy = rotate_point(-1, 0, rotation)
                        elif city_opening == 1:
                            dx, dy = rotate_point(0, 1, rotation)
                        elif city_opening == 2:
                            dx, dy = rotate_point(1, 0, rotation)
                        elif city_opening == 3:
                            dx, dy = rotate_point(0, -1, rotation)
                        else:
                            continue

                        # if its already in the surroundings, skip
                        if (
                            x + dx,
                            y + dy,
                        ) in self.get_occupied_coordinates():  # x,y : tile
                            continue

                        if (x, y) in state.Board.keys():
                            tile = state.Board[(x, y)]
                            surroundings.append((x + dx, y + dy))
        return surroundings

    def __repr__(self):
        return f"""ID={self.ID}, Pointer={self.Pointer}, Value={self.Value}, Openings={self.Openings}, Meeples=Player1: {self.Meeples[0]}, Player2: {self.Meeples[1]}, Closed={self.ClosedFlag}, Blocked={self.isBlocked}, tiles={self.tiles}"""


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
