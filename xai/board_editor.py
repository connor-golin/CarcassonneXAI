import random
import pygame
import sys
import os
import pickle
import pygame_menu

sys.path.append(os.getcwd())

from pygameCarcassonneDir.pygameFunctions import (
    diplayGameBoard,
    drawGrid,
    get_clicked_X,
    get_clicked_Y,
    meepleCoordinates,
    placeColourTile,
    printTilesLeft,
)
from pygameCarcassonneDir.pygameLabel import Label
from pygameCarcassonneDir import pygameNextTile, pygameSettings
from Carcassonne_Game.Carcassonne import CarcassonneState
from Carcassonne_Game.Tile import Tile
from player.Player import HumanPlayer
from xai.search import MinimaxPlayer
from load_config import *  # import all config.json variables

# Initialize Pygame
pygame.init()


def startMenu():
    pygame.init()
    surface = pygame.display.set_mode((600, 400))

    def city_blocking():
        main(board_state="board_states/city_blocking.pkl")

    def field_merging():
        main(board_state="board_states/field_merging.pkl")

    def new_game():
        main(board_state=None)

    menu = pygame_menu.Menu(
        "Select a scenario", 600, 400, theme=pygame_menu.themes.THEME_DARK
    )
    menu.add.button("New Game", new_game)
    menu.add.button("City Blocking", city_blocking)
    menu.add.button("Field Merging", field_merging)
    menu.add.button("Quit", pygame_menu.events.EXIT)
    menu.mainloop(surface)


def initialize_game():
    DisplayScreen = pygameSettings.displayScreen(
        GRID, GRID_SIZE, GRID_BORDER, MENU_WIDTH, MEEPLE_SIZE
    )
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
    w, _ = pygame.display.get_surface().get_size()

    # Calculate the dynamic X_PADDING to perfectly fit tiles within MENU_WIDTH
    available_width = (
        MENU_WIDTH - 4 * X_PADDING
    )  # Space within the menu minus the left and right padding
    total_tile_width = (
        TILES_PER_ROW * EDITOR_TILE_SIZE
    )  # Total width occupied by tiles without padding
    dynamic_x_padding = (available_width - total_tile_width) / (TILES_PER_ROW - 1)

    # Start x position for the first column of tiles
    starting_x = w - MENU_WIDTH + 2 * X_PADDING
    starting_y = Y_PADDING + 50

    for i in range(24):
        row = i // TILES_PER_ROW
        col = i % TILES_PER_ROW

        # Calculate x and y positions based on padding
        x = starting_x + col * (EDITOR_TILE_SIZE + dynamic_x_padding)
        y = starting_y + row * (EDITOR_TILE_SIZE + Y_PADDING)

        # Draw the tile
        tile_image = pygame.transform.smoothscale(
            tile_images[i], (EDITOR_TILE_SIZE, EDITOR_TILE_SIZE)
        )
        GAME_DISPLAY.blit(tile_image, (x, y))

        # Highlight the current tile with a red border
        if i == current_tile_index:
            pygame.draw.rect(
                GAME_DISPLAY,
                (255, 0, 0),
                (x, y, EDITOR_TILE_SIZE, EDITOR_TILE_SIZE),
                2,
            )

        # Display the tile count
        count = Carcassonne.TileQuantities[i]
        font = pygame.font.SysFont("timesnewroman", 18)
        font.set_bold(True)
        text = font.render(str(count), True, BLACK)
        GAME_DISPLAY.blit(text, (x + EDITOR_TILE_SIZE - 12, y + EDITOR_TILE_SIZE - 20))


def get_clicked_tile(pos):
    x, y = pos
    w, _ = pygame.display.get_surface().get_size()

    available_width = MENU_WIDTH - 4 * X_PADDING
    total_tile_width = TILES_PER_ROW * EDITOR_TILE_SIZE
    dynamic_x_padding = (available_width - total_tile_width) / (TILES_PER_ROW - 1)

    # Start x position for the first column of tiles
    starting_x = w - MENU_WIDTH + 2 * X_PADDING
    starting_y = Y_PADDING + 50

    for i in range(24):
        row = i // TILES_PER_ROW
        col = i % TILES_PER_ROW

        # Calculate x and y positions based on dynamic padding
        tile_x = starting_x + col * (EDITOR_TILE_SIZE + dynamic_x_padding)
        tile_y = starting_y + row * (EDITOR_TILE_SIZE + Y_PADDING)

        # Check if the click is within this tile's boundaries
        if (
            tile_x <= x < tile_x + EDITOR_TILE_SIZE
            and tile_y <= y < tile_y + EDITOR_TILE_SIZE
        ):
            return i

    return None


def draw_current_tile(
    GAME_DISPLAY,
    tile_images,
    current_tile_index,
    rotation,
):
    w, h = pygame.display.get_surface().get_size()
    starting_x = w - MENU_WIDTH / 2

    rotated_image = pygame.transform.rotate(tile_images[current_tile_index], -rotation)
    rotated_image = pygame.transform.smoothscale(
        rotated_image, (TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE)
    )
    GAME_DISPLAY.blit(
        rotated_image,
        (
            starting_x - 0.5 * TILE_PREVIEW_SIZE,
            h - 2 * rotated_image.get_height(),
        ),
    )
    font = pygame.font.Font(None, 30)
    text = font.render(f"Selected: Tile {current_tile_index}", True, BLACK)
    GAME_DISPLAY.blit(
        text,
        (  # top of the tile image defined above
            starting_x - 0.5 * text.get_width(),
            h - 2.3 * rotated_image.get_height(),
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


def draw_current_player(GAME_DISPLAY, player):

    # font settings for player turn label
    font = pygame.font.SysFont("timesnewroman", 36)
    font.set_bold(True)
    player_name = players[player]  # Red or Blue
    to_play_label = font.render(f"To Play: {player_name}", True, BLACK)

    # set text background to correspond to their colour
    pygame.draw.rect(
        GAME_DISPLAY,
        colours[player_name.upper()],
        (
            0,
            0,
            to_play_label.get_width() + 10,
            to_play_label.get_height() + 10,
        ),
    )
    GAME_DISPLAY.blit(to_play_label, (5, 5))


def draw_buttons(GAME_DISPLAY):
    window_width, window_height = pygame.display.get_surface().get_size()
    starting_x = window_width - MENU_WIDTH / 2

    # initialise save/load text
    font = pygame.font.Font(None, 36)
    save_text = font.render("Save", True, BLACK)
    load_text = font.render("Load", True, BLACK)
    # get text width/heights
    save_text_width = save_text.get_width()
    load_text_width = load_text.get_width()
    text_height = save_text.get_height()
    X_PADDING = 10

    save_rect = pygame.draw.rect(
        GAME_DISPLAY,
        (200, 200, 200),
        (
            window_width - MENU_WIDTH + X_PADDING,
            window_height - 2.5 * text_height - 5,
            MENU_WIDTH - 2 * X_PADDING,
            text_height,
        ),
    )
    load_rect = pygame.draw.rect(
        GAME_DISPLAY,
        (200, 200, 200),
        (
            window_width - MENU_WIDTH + X_PADDING,
            window_height - 1.5 * text_height,
            MENU_WIDTH - 2 * X_PADDING,
            text_height,
        ),
    )

    GAME_DISPLAY.blit(
        save_text,
        (starting_x - 0.5 * save_text_width - 5, window_height - 2.5 * text_height - 5),
    )
    GAME_DISPLAY.blit(
        load_text,
        (starting_x - 0.5 * load_text_width - 5, window_height - 1.5 * text_height),
    )

    return save_rect, load_rect


def draw_AI_move(GAME_DISPLAY, DisplayScreen):
    start_x = 0
    label_width = 200
    label_height = 30
    font = pygame.font.Font(None, 36)
    save_text = font.render(f"Play AI Move", True, BLACK)

    to_play = pygame.draw.rect(
        GAME_DISPLAY,
        (100, 100, 100),
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


def save_game_state(Carcassonne):
    rand = random.randint(1, 9999999)
    with open(f"board_states/board_state_{rand}.pkl", "wb") as f:
        pickle.dump(Carcassonne, f)


def load_game_state(path):
    if not path:
        print("Load file not found")
        startMenu()
    try:
        with open(path, "rb") as f:
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


def playRandomMove(Carcassonne, player):
    available_moves = Carcassonne.availableMoves(False)  # Get available moves

    if not available_moves:
        print("No available moves.")
        return

    move = random.choice(available_moves)  # Choose a random move
    Carcassonne.move(
        (move.TileIndex, move.X, move.Y, move.Rotation, move.MeepleInfo)
    )  # Play the move

    print(f"Random move played by player {player}: {move}")


def main(board_state):
    DisplayScreen, GAME_DISPLAY, Carcassonne, tile_images = initialize_game()

    # init tile
    current_tile_index = 16
    tile = Tile(current_tile_index)
    printMeepleLocations(tile)

    if board_state:
        Carcassonne = load_game_state(board_state)

    player = Carcassonne.playerSymbol - 1
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

    # init minimax player
    minimax_player = MinimaxPlayer(
        max_depth=3, max_moves_to_consider=10, state=Carcassonne
    )

    while running:
        rotation = rotation % 4
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # save state
                if save_rect.collidepoint(event.pos):
                    save_game_state(Carcassonne)
                    print("Game state saved.")
                # load state
                elif load_rect.collidepoint(event.pos):
                    Carcassonne = load_game_state(None)
                    if Carcassonne:
                        print("Game state loaded.")
                    else:
                        print("Failed to load game state.")
                        mainloop()

                elif ai_search.collidepoint(event.pos):
                    print(f"Searching for best move...")

                    # [[City, Road, Monastery, City(Incomplete), Road(Incomplete), Monastery(Incomplete), Farms]]
                    print(f"Live Scores: {Carcassonne.Scores[2:]}")
                    print(
                        f"Field score for player 0 (Blue): {Carcassonne.FeatureScores[0][6]}"
                    )
                    print(
                        f"Field score for player 1 (Red): {Carcassonne.FeatureScores[1][6]}"
                    )

                    eval, move, isBlocking, isMerging = minimax_player.get_best_move(
                        Carcassonne
                    )
                    blocks = "Blocks" if isBlocking else "Does not block"
                    merged = "Merges" if isMerging else "Does not merge"
                    print(
                        f"""Move with a best score of {eval} was {move}. 
                        Tactics:
                            The move: {blocks} a city.
                            The move: {merged} a field."""
                    )
                    Carcassonne.move(move)

                    print(f"SCORES AFTER:")
                    print(f"Scores: {Carcassonne.Scores}")
                    print(
                        f"Field score for player 0 (Blue): {Carcassonne.FeatureScores[0]}"
                    )
                    print(
                        f"Field score for player 1 (Red): {Carcassonne.FeatureScores[1]}"
                    )

                    player = 1 - player
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

                        print(f"Scores: {Carcassonne.Scores}")

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
                            player = 1 - player
                            print(f"player: {player}")
                        else:
                            print("Invalid location pressed")
                            continue
            elif event.type == pygame.KEYDOWN:
                numberOfRotations = len(tile.AvailableRotations) - 1
                if rotation < 0 or (rotation + 1 > numberOfRotations):
                    print(f"This tile cannot rotate this way!")
                    rotation = 0
                    break

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

        # playRandomMove(Carcassonne, player)

        drawGrid(DisplayScreen)
        diplayGameBoard(Carcassonne, DisplayScreen)
        draw_tile_selection(GAME_DISPLAY, tile_images, current_tile_index, Carcassonne)
        draw_current_tile(
            GAME_DISPLAY,
            tile_images,
            current_tile_index,
            rotation * 90 % 360,
        )
        draw_current_player(GAME_DISPLAY, player)
        save_rect, load_rect = draw_buttons(GAME_DISPLAY)
        printTilesLeft(Carcassonne, DisplayScreen)
        highlightPossibleMoves(Carcassonne, current_tile_index, rotation, DisplayScreen)
        ai_search = draw_AI_move(GAME_DISPLAY, DisplayScreen)
        pygame.display.flip()

        if Carcassonne.isGameOver:
            print(
                f"Winner: Player {players[Carcassonne.winner - 1]}, Scores:  Blue: {Carcassonne.Scores[0]} - Red: {Carcassonne.Scores[1]}"
            )

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    startMenu()
