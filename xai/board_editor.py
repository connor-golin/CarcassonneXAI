import json
import pygame
import sys
import os
import pickle
from typing import Dict, List, Tuple


sys.path.append(os.getcwd())

from pygameCarcassonneDir.pygameFunctions import diplayGameBoard, drawGrid, get_clicked_X, get_clicked_Y, meepleCoordinates, placeColourTile, printTilesLeft
from pygameCarcassonneDir.pygameLabel import Label
from pygameCarcassonneDir import pygameNextTile, pygameSettings
from Carcassonne_Game.Carcassonne import CarcassonneState
from Carcassonne_Game.Tile import Tile
from player.Player import HumanPlayer

# Load config file
with open('xai/config.json', 'r') as config_file:
    config = json.load(config_file)

# Config Types
NameMapping = Dict[str, str]
Players = List[str]
PlayerColors = Dict[str, Tuple[int, int, int]]

# Config Variables
name_mapping: NameMapping = config['name_mapping']
players: Players = config['players']
player_colors: PlayerColors = {k: tuple(v) for k, v in config['player_colors'].items()}
WHITE: Tuple[int, int, int] = tuple(config['WHITE'])
BLACK: Tuple[int, int, int] = tuple(config['BLACK'])
TILE_SIZE: int = config['TILE_SIZE']
TILES_PER_ROW: int = config['TILES_PER_ROW']
MARGIN: int = config['MARGIN']
Y_OFFSET: int = config['Y_OFFSET']

# Constants from pygameNextTile
FEATURE_DICT = pygameNextTile.FEATURE_DICT
MEEPLE_LOCATION_DICT_SCALED = pygameNextTile.MEEPLE_LOCATION_DICT_SCALED

# Constants from pygameSettings
FONT_MEEPLE_IMAGE = pygameSettings.FONT_MEEPLE_IMAGE
FONT_MEEPLE_MENU = pygameSettings.FONT_MEEPLE_MENU
MEEPLE_CHOICE_HIGHLIGHT = pygameSettings.MEEPLE_CHOICE_HIGHLIGHT
MEEPLE_LABEL_SHIFT_X = pygameSettings.MEEPLE_LABEL_SHIFT_X
MEEPLE_LABEL_SHIFT_Y = pygameSettings.MEEPLE_LABEL_SHIFT_Y
MEEPLE_LABEL_X = pygameSettings.MEEPLE_LABEL_X
MEEPLE_LABEL_Y = pygameSettings.MEEPLE_LABEL_Y
GRID = pygameSettings.GRID
MEEPLE_SIZE = pygameSettings.MEEPLE_SIZE

# Initialize Pygame
pygame.init()

def initialize_game():
    GRID_SIZE = 50
    GRID_BORDER = 0
    MENU_WIDTH = 200
    DisplayScreen = pygameSettings.displayScreen(GRID, GRID_SIZE, GRID_BORDER, MENU_WIDTH, MEEPLE_SIZE)
    GAME_DISPLAY = DisplayScreen.pygameDisplay
    pygame.display.set_caption("Carcassonne Board Editor")

    Carcassonne = CarcassonneState(HumanPlayer(), HumanPlayer())

    tile_images = load_tile_images()

    return DisplayScreen, GAME_DISPLAY, Carcassonne, tile_images


def load_tile_images():
    tile_images = {}
    for i in range(24):
        tile_images[i] = pygame.image.load(f"images/{i}.png")
        tile_images[i] = pygame.transform.scale(tile_images[i], (TILE_SIZE, TILE_SIZE))
    return tile_images


def draw_tile_selection(GAME_DISPLAY, tile_images, current_tile_index, Carcassonne):
    w, h = pygame.display.get_surface().get_size()
    total_tile_width = TILES_PER_ROW * TILE_SIZE + (TILES_PER_ROW - 1) * MARGIN
    start_x = w - total_tile_width - 2 * MARGIN

    for i in range(24):
        row = i // TILES_PER_ROW
        col = i % TILES_PER_ROW
        x = start_x + (MARGIN + col * (TILE_SIZE + MARGIN))
        y = Y_OFFSET + MARGIN + row * (TILE_SIZE + MARGIN)  # Added Y_OFFSET here
        GAME_DISPLAY.blit(tile_images[i], (x, y))

        if i == current_tile_index:
            pygame.draw.rect(
                GAME_DISPLAY,
                (255, 0, 0),
                (x - 2, y - 2, TILE_SIZE + 4, TILE_SIZE + 4),
                2,
            )

        count = Carcassonne.TileQuantities[i]
        font = pygame.font.Font(None, 24)
        text = font.render(str(count), True, BLACK)
        GAME_DISPLAY.blit(text, (x + TILE_SIZE - 20, y + TILE_SIZE - 20))


def draw_current_tile(
    GAME_DISPLAY,
    DisplayScreen,
    tile_images,
    current_tile_index,
    rotation,
):
    w, h = pygame.display.get_surface().get_size()
    total_tile_width = TILES_PER_ROW * TILE_SIZE + (TILES_PER_ROW - 1) * MARGIN
    start_x = w - total_tile_width - 2 * MARGIN

    rotated_image = pygame.transform.rotate(tile_images[current_tile_index], -rotation)
    rotated_image = pygame.transform.scale_by(rotated_image, 1.5)
    GAME_DISPLAY.blit(
        rotated_image,
        (  # bottom right of screen, up by 1.75x the size of the tile image
            (w + start_x) / 2 - rotated_image.get_width() / 2,
            h - 1.5 * rotated_image.get_height(),
        ),
    )
    font = pygame.font.Font(None, 30)
    text = font.render(f"Selected: Tile {current_tile_index}", True, BLACK)
    GAME_DISPLAY.blit(
        text,
        (  # top of the tile image defined above
            (w + start_x) / 2 - rotated_image.get_width() / 2 - text.get_width() / 4,
            h - 1.75 * rotated_image.get_height(),
        ),
    )


def possibleCoordinatesMeeples(Carcassonne, Meeple, rotation, tile_index):
    """
    Return a list of all playable coordinates for the current tile
    """
    availableMoves = Carcassonne.availableMoves(
        False, tile_index
    )  # False so it considers meeple info
    coordinates = []
    for move in availableMoves:
        MeepleInfo = move.MeepleInfo
        if MeepleInfo == Meeple:
            if move.Rotation == (rotation * 90):
                coordinates.append((move.X, move.Y))
    return coordinates


def get_clicked_tile(pos):
    x, y = pos
    w, h = pygame.display.get_surface().get_size()
    y_adjusted = y - Y_OFFSET

    # Calculate the total width of the tile selection area
    total_tile_width = TILES_PER_ROW * TILE_SIZE + (TILES_PER_ROW - 1) * MARGIN
    start_x = w - total_tile_width - 2 * MARGIN

    # Check if click is within tile selection area horizontally
    if x < start_x or x > start_x + total_tile_width:
        return None

    # Calculate column and row
    col = (x - start_x) // (TILE_SIZE + MARGIN)
    row = y_adjusted // (TILE_SIZE + MARGIN)

    # Calculate tile index
    index = row * TILES_PER_ROW + col

    # Ensure the index is within bounds
    if 0 <= index < 24:
        return index

    return None

def draw_current_player(GAME_DISPLAY, DisplayScreen, player):
    start_x = 0
    label_width = 200
    label_height = 30
    font = pygame.font.Font(None, 36)
    player_name = players[player]
    save_text = font.render(f"To Play: {player_name}", True, BLACK)

    to_play = pygame.draw.rect(
        GAME_DISPLAY,
        player_colors[player_name],
        (
            start_x,
            DisplayScreen.Window_Height - label_height,
            label_width,
            label_height,
        ),
    )

    GAME_DISPLAY.blit(
        save_text, (start_x + 20, DisplayScreen.Window_Height - label_height + 5)
    )

    return to_play

def draw_buttons(GAME_DISPLAY, DisplayScreen):
    w, h = pygame.display.get_surface().get_size()
    total_tile_width = TILES_PER_ROW * TILE_SIZE + (TILES_PER_ROW - 1) * MARGIN
    start_x = w - total_tile_width - 2 * MARGIN

    font = pygame.font.Font(None, 36)
    save_text = font.render("Save", True, BLACK)
    load_text = font.render("Load", True, BLACK)

    button_width = 80
    button_height = 30
    spacing = (
        w - start_x - 2 * button_width
    ) // 3  # Calculate spacing between buttons and the edges

    save_x = start_x + spacing
    load_x = save_x + button_width + spacing

    save_rect = pygame.draw.rect(
        GAME_DISPLAY,
        (200, 200, 200),
        (
            save_x,
            DisplayScreen.Window_Height - button_height,
            button_width,
            button_height,
        ),
    )
    load_rect = pygame.draw.rect(
        GAME_DISPLAY,
        (200, 200, 200),
        (
            load_x,
            DisplayScreen.Window_Height - button_height,
            button_width,
            button_height,
        ),
    )

    GAME_DISPLAY.blit(
        save_text, (save_x + 12, DisplayScreen.Window_Height - button_height + 5)
    )
    GAME_DISPLAY.blit(
        load_text, (load_x + 12, DisplayScreen.Window_Height - button_height + 5)
    )

    return save_rect, load_rect


def save_game_state(Carcassonne):
    with open("board_state.pkl", "wb") as f:
        pickle.dump(Carcassonne, f)


def load_game_state():
    try:
        with open("board_state.pkl", "rb") as f:
            Carcassonne = pickle.load(f)
        return Carcassonne
    except FileNotFoundError:
        print("No saved game state found.")
        return None


def possibleCoordinates(carcassonne, tile_index, rotation):
    """
    Return a list of all playable coordinates for the current tile
    """
    availableMoves = carcassonne.availableMoves(True, tile_index)

    coordinates = []

    for move in availableMoves:
        if move.Rotation == (rotation * 90):
            coordinates.append((move.X, move.Y))
    return coordinates


def highlightPossibleMoves(carcassonne, tile_index, rotation, DisplayScreen):
    """
    Highlight on the grid where the player can place the next tile
    """
    for X, Y in possibleCoordinates(carcassonne, tile_index, rotation):
        # all possible moves
        placeColourTile(X, Y, DisplayScreen, pygame.Color(0, 0, 255))


def addMeepleLocations(location_key, Location, NumberKey, numberSelected, tile):
    """
    Add meeples or meeple locations to tile
    """
    Feature = location_key[0]
    circleColour = WHITE
    background = None
    thickness = 2

    # change colour for selected meeple location
    if NumberKey == numberSelected:
        if NumberKey == 0:
            background = None
            Meeple = None
            thickness = 2
        else:
            background = MEEPLE_CHOICE_HIGHLIGHT
            circleColour = MEEPLE_CHOICE_HIGHLIGHT
            Meeple = location_key
            thickness = 0

    text = str(NumberKey)
    X, Y = meepleCoordinates(
        Location, Feature, MEEPLE_LOCATION_DICT_SCALED, tile.TileIndex
    )

    # image label
    meepleLabelImage = Label(text, font_size=FONT_MEEPLE_IMAGE, background=background)
    image = pygame.image.load(tile.image)
    pygame.draw.circle(image, circleColour, (X + 7, Y + 12), 16, thickness)
    image.blit(meepleLabelImage.text_surface, (X, Y))


def updateMeepleMenu(meepleLabel, location_key, Location, NumberKey, numberSelected):
    Feature = location_key[0]
    background = background0 = WHITE

    # change colour for selected meeple location
    if NumberKey == numberSelected:
        background = MEEPLE_CHOICE_HIGHLIGHT

    if numberSelected == 0:
        background0 = MEEPLE_CHOICE_HIGHLIGHT

    # each label has a "No Meeple Option"
    text = "0. No Meeple"
    meepleInfoLabel = Label(text, font_size=FONT_MEEPLE_MENU, background=background0)
    meepleLabel.blit(
        meepleInfoLabel.text_surface,
        (MEEPLE_LABEL_X, MEEPLE_LABEL_Y - MEEPLE_LABEL_SHIFT_Y),
    )

    # info label
    x = MEEPLE_LABEL_X
    y = MEEPLE_LABEL_Y

    # rows
    shiftY = MEEPLE_LABEL_SHIFT_Y * ((NumberKey - 1) % 4)
    y += shiftY

    # next column
    shiftX = 0 if NumberKey < 5 else MEEPLE_LABEL_SHIFT_X
    x += shiftX

    # create label
    text = str(NumberKey) + ". " + str(FEATURE_DICT[Feature])
    meepleInfoLabel = Label(text, font_size=FONT_MEEPLE_MENU, background=background)
    meepleLabel.blit(meepleInfoLabel.text_surface, (x, y))


def printMeepleLocations(tile):
    available = tile.AvailableMeepleLocs

    print("\nAvailable meeple locations:")
    for i in range(len(available)):
        # Cast shortname to long name i.e.: # C -> City
        feature_shortname = list(available.keys())[i][0]
        print(f"{i + 1} : {name_mapping.get(feature_shortname, feature_shortname)}")


def main():
    DisplayScreen, GAME_DISPLAY, Carcassonne, tile_images = initialize_game()

    # init tile
    current_tile_index = 16
    tile = Tile(current_tile_index)
    printMeepleLocations(tile)
    
    player = 0
    rotation = 0
    meeple = None
    running = True

    meepleRect = (0, 0, 300, 160)
    meepleLabel = pygame.Surface(pygame.Rect(meepleRect).size)
    meepleLabel.set_alpha(165)
    text = "0. No Meeple"
    meepleInfoLabel = Label(text, font_size=FONT_MEEPLE_MENU, background=WHITE)
    meepleLabel.blit(
        meepleInfoLabel.text_surface,
        (MEEPLE_LABEL_X, MEEPLE_LABEL_Y - MEEPLE_LABEL_SHIFT_Y),
    )

    while running:
        rotation = rotation % 4
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if save_rect.collidepoint(event.pos):
                    save_game_state(Carcassonne)
                    print("Game state saved.")
                elif load_rect.collidepoint(event.pos):
                    Carcassonne = load_game_state()
                    if Carcassonne:
                        print("Game state loaded.")
                    else:
                        print("Failed to load game state.")
                        main()
                else:
                    clicked_tile = get_clicked_tile(event.pos)
                    if clicked_tile is not None:
                        current_tile_index = clicked_tile
                        rotation = 0
                        meeple = None
                        tile = Tile(current_tile_index)
                        printMeepleLocations(tile)
                    else:
                        X, Y = get_clicked_X(
                            pygame.mouse.get_pos(), DisplayScreen
                        ), get_clicked_Y(pygame.mouse.get_pos(), DisplayScreen)

                        move_tuple = (current_tile_index, X, Y, rotation * 90, meeple)
                        count = Carcassonne.TileQuantities[current_tile_index]
                        if count <= 0:
                            print(
                                f"No tiles of index: '{current_tile_index}' remaining."
                            )
                            continue
                        if (X, Y) not in possibleCoordinatesMeeples(
                            Carcassonne, meeple, rotation, current_tile_index
                        ):
                            print("Meeple cannot be placed here!")
                            continue
                        if (X, Y) in possibleCoordinates(
                            Carcassonne, current_tile_index, rotation
                        ):
                            Carcassonne.move(move_tuple)
                            print(f"player: {player}")
                            player = 1 - player
                            print(f"after player: {player}")
                        else:
                            print("Invalid location pressed")
                            continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    rotation -= 1
                elif event.key == pygame.K_RIGHT:
                    rotation += 1
                elif event.key in [
                    pygame.K_0,
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                    pygame.K_5,
                    pygame.K_6,
                    pygame.K_7,
                    pygame.K_8,
                    pygame.K_9,
                ]:
                    meeple = int(pygame.key.name(event.key))  # cast to int
                    meeple = (
                        meeple - 1 if meeple != 0 else None
                    )  # make 0 == None for no meeple

                    if meeple and meeple >= len(tile.AvailableMeepleLocs):
                        print(
                            f"Meeple index {meeple + 1} is not available. Available range: 0-{len(tile.AvailableMeepleLocs)}"
                        )
                        continue

                    feature_shortname = list(tile.AvailableMeepleLocs.keys())[meeple][0]
                    print(
                        # Gets long name: i.e, M -> Monastery
                        f"Meeple location at index {meeple + 1} selected: {name_mapping.get(feature_shortname, feature_shortname)}" 
                    )

                    i = 1
                    for location_key in tile.AvailableMeepleLocs:
                        location_value = tile.AvailableMeepleLocs[location_key]

                        keys = list(tile.AvailableMeepleLocs.keys())

                        addMeepleLocations(
                            location_key, location_value, i, keys[meeple], tile
                        )
                        i += 1

                    meeple = keys[meeple]

        GAME_DISPLAY.fill(WHITE)

        
        drawGrid(DisplayScreen)
        diplayGameBoard(Carcassonne, DisplayScreen)
        draw_tile_selection(GAME_DISPLAY, tile_images, current_tile_index, Carcassonne)
        draw_current_tile(
            GAME_DISPLAY,
            DisplayScreen,
            tile_images,
            current_tile_index,
            rotation * 90 % 360,
        )
        save_rect, load_rect = draw_buttons(
            GAME_DISPLAY, DisplayScreen
        )  # Draw buttons once per frame
        printTilesLeft(Carcassonne, DisplayScreen)
        highlightPossibleMoves(Carcassonne, current_tile_index, rotation, DisplayScreen)
        # GAME_DISPLAY.blit(meepleLabel, (0, 0))
        draw_current_player(GAME_DISPLAY, DisplayScreen, player)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
