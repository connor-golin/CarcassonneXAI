# Load config file
import json
from typing import Dict, List, Tuple
from pygameCarcassonneDir import pygameNextTile

with open("xai/config.json", "r") as config_file:
    config = json.load(config_file)

# Config Types
NameMapping = Dict[str, str]
Players = List[str]
PlayerColors = Dict[str, Tuple[int, int, int]]

# Config Variables
name_mapping: NameMapping = config["name_mapping"]
players: Players = config["players"]  # index 0: Blue, index 1: Red
colours: Dict[str, Tuple[int, int, int]] = {k: tuple(v) for k, v in config["colours"].items()}
WHITE = colours["WHITE"]
BLACK = colours["BLACK"]
CYAN = colours['CYAN']
GREY = colours['GREY']
TILE_SIZE: int = config["TILE_SIZE"]

# Constants for pygameNextTile and pygameSettings
FEATURE_DICT = pygameNextTile.FEATURE_DICT
MEEPLE_LOCATION_DICT_SCALED = pygameNextTile.MEEPLE_LOCATION_DICT_SCALED
FONT_MEEPLE_IMAGE = config["font_sizes"]["FONT_MEEPLE_IMAGE"]
FONT_MEEPLE_MENU = config["font_sizes"]["FONT_MEEPLE_MENU"]
MEEPLE_CHOICE_HIGHLIGHT = tuple(config["meeple"]["MEEPLE_CHOICE_HIGHLIGHT"])
MEEPLE_LABEL_SHIFT_X = config["meeple"]["MEEPLE_LABEL_SHIFT_X"]
MEEPLE_LABEL_SHIFT_Y = config["meeple"]["MEEPLE_LABEL_SHIFT_Y"]
MEEPLE_LABEL_X = config["meeple"]["MEEPLE_LABEL_X"]
MEEPLE_LABEL_Y = config["meeple"]["MEEPLE_LABEL_Y"]
GRID = tuple(config["game_grid"]["GRID"])
MEEPLE_SIZE = config["meeple"]["MEEPLE_SIZE"]

# Grid and window size
GRID_SIZE = config["game_grid"]["GRID_SIZE"]
GRID_BORDER = config["game_grid"]["GRID_BORDER"]
GRID_WINDOW_WIDTH = config["game_grid"]["GRID_WINDOW_WIDTH"]
GRID_WINDOW_HEIGHT = config["game_grid"]["GRID_WINDOW_HEIGHT"]
WINDOW_WIDTH = config["window"]["WINDOW_WIDTH"]
WINDOW_HEIGHT = config["window"]["WINDOW_HEIGHT"]
MENU_WIDTH = config["window"]["MENU_WIDTH"]

# editor UI settings
EDITOR_SETTINGS = config["editor_settings"]
EDITOR_TILE_SIZE: int = EDITOR_SETTINGS['EDITOR_TILE_SIZE']
TILE_PREVIEW_SIZE: int = EDITOR_SETTINGS['TILE_PREVIEW_SIZE']
TILES_PER_ROW: int = EDITOR_SETTINGS['TILES_PER_ROW']
X_PADDING: int = EDITOR_SETTINGS['X_PADDING']
Y_PADDING: int = EDITOR_SETTINGS['Y_PADDING']
