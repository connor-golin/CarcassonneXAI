# file imports
from Carcassonne_Game.Tile_dict import CITY_OPENINGS_DICT, HAS_CITY
from pygameCarcassonneDir.pygameSettings import (
    MEEPLE_SIZE,
    WHITE,
    BROWN,
    RED,
    BLUE,
    DARK_GREEN,
    TILE_WIDTH
)

from pygameCarcassonneDir.pygameLabel import Label

# packages
import pygame
import math

X_DEPTH = 10
Y_DEPTH = 20
WIDTH = HEIGHT = TILE_WIDTH  # image scaled x2

XSHIFT = YSHIFT = MEEPLE_SIZE // 2

MEEPLE_LOCATION_DICT = {
    (0, 1): [X_DEPTH - XSHIFT, HEIGHT // 2 - YSHIFT],
    (0, 2): [WIDTH // 4 - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (1, 1): [WIDTH // 2 - XSHIFT, Y_DEPTH - YSHIFT],
    (1, 2): [WIDTH // 4 - XSHIFT, Y_DEPTH - YSHIFT],
    (2, 1): [WIDTH - X_DEPTH - XSHIFT, HEIGHT // 2 - YSHIFT],
    (2, 2): [3 * (WIDTH // 4) - XSHIFT, Y_DEPTH - YSHIFT],
    (3, 0): [3 * (WIDTH // 4) - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (3, 1): [WIDTH // 2 - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (3, 2): [WIDTH // 4 - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (0, 4): [WIDTH // 2 - XSHIFT, HEIGHT // 2 - YSHIFT],
    # exceptions
    0: [3 * (WIDTH // 4), Y_DEPTH - YSHIFT],
}

# pygame functions


def get_clicked_X(mouse_pos, displayScreen):
    Grid = displayScreen.Grid
    Grid_Size = displayScreen.Grid_Size
    Grid_border = displayScreen.Grid_border
    # column coordinate
    x = mouse_pos[0]
    max_X = math.floor(Grid[0] / 2)
    min_X = -max_X  # +displayScreen.Grid_border

    for i in range(min_X, max_X + 2):
        if Grid_border < x < ((i - min_X) * Grid_Size) + Grid_border:
            return i - 1
    return 1000


def get_clicked_Y(mouse_pos, displayScreen):
    Grid = displayScreen.Grid
    Grid_Size = displayScreen.Grid_Size
    Grid_border = displayScreen.Grid_border
    # row coordinate
    y = mouse_pos[1]
    max_Y = math.floor(Grid[1] / 2)  # + displayScreen.Grid_border
    min_Y = -max_Y  # + displayScreen.Grid_border

    for i in range(min_Y, max_Y + 2):
        if Grid_border < y < ((i - min_Y) * Grid_Size) + Grid_border:
            return -(i - 1)
    return 1000


def drawGrid(DisplayScreen):
    # display constants
    Grid_Window_Width = DisplayScreen.Grid_Window_Width
    Grid_Window_Height = DisplayScreen.Grid_Window_Height
    Grid_border = DisplayScreen.Grid_border
    Grid_Size = DisplayScreen.Grid_Size
    GAME_DISPLAY = DisplayScreen.pygameDisplay

    # add game mat
    gameMat = pygame.image.load("pygame_images/game_mat.png")
    gameMat = pygame.transform.scale(gameMat, (Grid_Window_Width, Grid_Window_Height))
    GAME_DISPLAY.blit(gameMat, (Grid_border, Grid_border))

    # for loop for each grid sqaure
    for x in range(0, Grid_Window_Width, Grid_Size):
        for y in range(0, Grid_Window_Height, Grid_Size):
            rect = pygame.Rect(x + Grid_border, y + Grid_border, Grid_Size, Grid_Size)
            pygame.draw.rect(GAME_DISPLAY, WHITE, rect, 1)


def placeColourTile(x, y, DisplayScreen, COLOUR):
    # display constants
    Grid_Window_Width = DisplayScreen.Grid_Window_Width
    Grid_Window_Height = DisplayScreen.Grid_Window_Height
    Grid_border = DisplayScreen.Grid_border
    Grid_Size = DisplayScreen.Grid_Size
    GAME_DISPLAY = DisplayScreen.pygameDisplay

    # reverse orientation
    y = y * -1

    X = (
        Grid_Size * math.floor(Grid_Window_Width / (Grid_Size * 2))
        + x * Grid_Size
        + Grid_border
    )
    Y = (
        Grid_Size * math.floor(Grid_Window_Height / (Grid_Size * 2))
        + y * Grid_Size
        + Grid_border
    )

    # draw rectangle
    rect = (X, Y, Grid_Size, Grid_Size)
    rect_surf = pygame.Surface(pygame.Rect(rect).size)
    rect_surf.set_alpha(150)
    pygame.draw.rect(rect_surf, COLOUR, rect_surf.get_rect())
    GAME_DISPLAY.blit(rect_surf, rect)


def placeTile(Tile, Rotation, x, y, DisplayScreen):
    # display constants
    Grid_Window_Width = DisplayScreen.Grid_Window_Width
    Grid_Window_Height = DisplayScreen.Grid_Window_Height
    Grid_Size = DisplayScreen.Grid_Size
    Grid_border = DisplayScreen.Grid_border
    Meeple_Size = DisplayScreen.Meeple_Size
    GAME_DISPLAY = DisplayScreen.pygameDisplay

    TileIndex = Tile.TileIndex
    # reverse orientation
    y = y * -1

    GAME_X = (
        Grid_Size * math.floor(Grid_Window_Width / (Grid_Size * 2))
        + x * Grid_Size
        + Grid_border
    )
    GAME_Y = (
        Grid_Size * math.floor(Grid_Window_Height / (Grid_Size * 2))
        + y * Grid_Size
        + Grid_border
    )

    # load image
    image = pygame.image.load("images/" + str(TileIndex) + ".png")

    # load meeple
    TileMeeple = Tile.Meeple
    if not (TileMeeple is None):
        Feature, Location = TileMeeple[0], TileMeeple[1]
        playerSymbol = TileMeeple[2]
        # meeple image
        meepleColour = "blue" if playerSymbol == 1 else "red"
        meepleImage = pygame.image.load("meeple_images/" + meepleColour + ".png")
        meepleImage = pygame.transform.scale(meepleImage, (Meeple_Size, Meeple_Size))
        X, Y = meepleCoordinates(Location, Feature, MEEPLE_LOCATION_DICT, TileIndex)
        image.blit(meepleImage, (X, Y))
    # add image
    image = pygame.transform.scale(image, (Grid_Size, Grid_Size))
    image = pygame.transform.rotate(image, Rotation)
    GAME_DISPLAY.blit(image, (GAME_X, GAME_Y))


def meepleCoordinates(Location, Feature, DICT, TileIndex):
    """
    Get meeple coordinates from Meeple Tile Location
    """
    coords = DICT[Location]

    # exceptions
    if TileIndex in [8, 9]:
        if Location == (0, 2):
            coords = DICT[(3, 0)]

    elif TileIndex == 14:
        if Location == (2, 1):
            coords = DICT[(3, 0)]

    elif TileIndex == 16:
        if Location == (0, 2):
            coords = DICT[0]

    elif TileIndex == 17:
        if Location == (2, 2):
            coords = DICT[(3, 0)]

    elif TileIndex in [18, 19]:
        if Location == (0, 2):
            coords = DICT[(2, 2)]
        if Location == (2, 2):
            coords = DICT[(3, 0)]

    elif TileIndex == 22:
        if Location == (0, 1):
            coords = DICT[(0, 4)]
        if Location == (0, 2):
            coords = DICT[(1, 1)]

    elif TileIndex == 23:
        if Location == (0, 2):
            coords = DICT[(1, 2)]
        if Location == (1, 2):
            coords = DICT[(2, 2)]
        if Location == (2, 2):
            coords = DICT[(3, 0)]

    X, Y = coords[0], coords[1]
    return X, Y


def diplayGameBoard(Carcassonne, displayScreen):
    """
    Display all current tiles on the game board
    """
    tiles = Carcassonne.Board  # stored in a dictionary
    tile_coorindates = list(tiles.keys())

    for X, Y in tile_coorindates:
        tile = tiles[X, Y]
        # reverse rotation
        rotation = 360 - tile.Rotation
        # place tile on board
        placeTile(tile, rotation, X, Y, displayScreen)


def playMove(
    NextTile, player, Carcassonne, TileIndex, isStartOfGame=False, ManualMove=None
):

    # check if there is a possible move
    if len(Carcassonne.availableMoves()) == 0:
        print("No Moves Available - Tile Discarded From Game")
        Carcassonne.move([None, TileIndex])
        return player  # turn not over

    # get move
    if player.isAIPlayer:
        selectedMove = player.chooseAction(Carcassonne)
    else:
        selectedMove = ManualMove

    # play move on board
    # print(f'(pygame) Selected Move: {selectedMove}')
    # print(f'(pygame) Selected Move[0]: {selectedMove[0]}')
    Carcassonne.move(selectedMove)
    # switch player
    if player == Carcassonne.p1:
        return Carcassonne.p2, selectedMove

    return Carcassonne.p1, selectedMove


def printTilesLeft(Carcassonne, displayScreen, *args):
    # attributes
    Grid_Window_Width = displayScreen.Total_Grid_Width
    Menu_Width = displayScreen.Menu_Width
    GAME_DISPLAY = displayScreen.pygameDisplay
    window_width, window_height = pygame.display.get_surface().get_size()

    # rectangular surface
    rect = (0, 0, Menu_Width, 40)
    label = pygame.Surface(pygame.Rect(rect).size)
    label.set_alpha(165)
    pygame.draw.rect(label, BROWN, label.get_rect(), 10)
    width = (label.get_rect().size)[0]
    height = (label.get_rect().size)[1]

    # number of tiles left
    tilesLeft = Carcassonne.TotalTiles
    text = "Tiles Left: " + str(tilesLeft)
    tilesLeftLabel = Label(text, font_size=25, background=None, foreground=WHITE)
    text_width = (tilesLeftLabel.text_surface.get_rect().size)[0]
    text_height = (tilesLeftLabel.text_surface.get_rect().size)[1]
    # attach to rectangle
    label.blit(
        tilesLeftLabel.text_surface,
        ((width - text_width) / 2, (height - text_height) / 2),
    )
    # attach rectangle to screen
    GAME_DISPLAY.blit(label, (window_width - Menu_Width, 0))


def rotate_point(x, y, rotation):
    """Rotate the point (x, y) by 90 degrees clockwise."""
    if rotation == 0:
        return x, y
    elif rotation == 1:
        return -y, x
    elif rotation == 2:
        return -x, -y
    elif rotation == 3:
        return y, -x
    else:
        return x, y


def get_city_tiles(Carcassonne):
    cities = {}
    for (x, y), tile in Carcassonne.Board.items():
        tile_index = tile.TileIndex
        if tile_index in HAS_CITY:
            cities[(x, y)] = tile

    return cities


def city_openings(Carcassonne):
    surroundings = []
    board = Carcassonne.Board
    city_index = 0

    for (x, y), tile in Carcassonne.Board.items():
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
                    if (x + dx, y + dy) in get_city_tiles(Carcassonne).keys():
                        continue

                    if (x, y) in board.keys():
                        tile = board[(x, y)]
                        surroundings.append((x + dx, y + dy))
                        city_index += 1
    return surroundings


def printScores(Carcassonne, displayScreen):
    # attributes
    Grid_Window_Width = displayScreen.Total_Grid_Width
    Grid_Window_Height = displayScreen.Total_Grid_Height
    Menu_Width = displayScreen.Menu_Width
    GAME_DISPLAY = displayScreen.pygameDisplay

    color1 = color2 = WHITE

    # highlight current player
    if Carcassonne.playerSymbol == 1:
        color1 = DARK_GREEN
    else:
        color2 = DARK_GREEN

    # latest scores
    scores = Carcassonne.Scores
    p1_score = scores[0]
    p2_score = scores[1]

    # names
    name_p1 = Carcassonne.p1.name
    name_p2 = Carcassonne.p2.name

    # meeple count
    meeples = Carcassonne.Meeples
    p1_meeples = meeples[0]
    p2_meeples = meeples[1]

    # score labels
    p1_Label = Label("Player 1:", font_size=30, background=None, foreground=color1)
    p2_Label = Label("Player 2:", font_size=30, background=None, foreground=color2)

    p1_Name_Label = Label(
        " Name: " + name_p1, font_size=25, background=None, foreground=WHITE
    )
    p2_Name_Label = Label(
        " Name: " + name_p2, font_size=25, background=None, foreground=WHITE
    )

    p1_Score_Label = Label(
        " Score: " + str(p1_score), font_size=25, background=None, foreground=WHITE
    )
    p2_Score_Label = Label(
        " Score: " + str(p2_score), font_size=25, background=None, foreground=WHITE
    )

    p1_Meeples_Label = Label(
        " Meeples: " + str(p1_meeples), font_size=25, background=None, foreground=WHITE
    )
    p2_Meeples_Label = Label(
        " Meeples: " + str(p2_meeples), font_size=25, background=None, foreground=WHITE
    )

    label1_x = [
        (p1_Label.text_surface.get_rect().size)[0],
        (p1_Name_Label.text_surface.get_rect().size)[0],
        (p1_Score_Label.text_surface.get_rect().size)[0],
        (p1_Meeples_Label.text_surface.get_rect().size)[0],
    ]
    label1_y = [
        (p1_Label.text_surface.get_rect().size)[1],
        (p1_Name_Label.text_surface.get_rect().size)[1],
        (p1_Score_Label.text_surface.get_rect().size)[1],
        (p1_Meeples_Label.text_surface.get_rect().size)[1],
    ]

    # dimension of text
    text_width1 = max(label1_x)
    text_width2 = max(label1_x)
    text_height = sum(label1_y) + 10 * 5

    # surfaces to add text to
    rect1 = (0, 0, text_width1 + 20, text_height)
    label1 = pygame.Surface(pygame.Rect(rect1).size)
    label1.set_alpha(165)
    pygame.draw.rect(label1, BLUE, label1.get_rect(), 10)

    rect2 = (0, 0, text_width2 + 20, text_height)
    label2 = pygame.Surface(pygame.Rect(rect2).size)
    label2.set_alpha(165)
    pygame.draw.rect(label2, RED, label2.get_rect(), 10)

    width = (label1.get_rect().size)[0]

    # attach to rectangle
    label1.blit(p1_Label.text_surface, ((width - text_width1) / 2, 13))
    label1.blit(p1_Name_Label.text_surface, ((width - text_width1) / 2, 40))
    label1.blit(p1_Score_Label.text_surface, ((width - text_width1) / 2, 65))
    label1.blit(p1_Meeples_Label.text_surface, ((width - text_width1) / 2, 90))

    label2.blit(p2_Label.text_surface, ((width - text_width2) / 2, 13))
    label2.blit(p2_Name_Label.text_surface, ((width - text_width2) / 2, 40))
    label2.blit(p2_Score_Label.text_surface, ((width - text_width2) / 2, 65))
    label2.blit(p2_Meeples_Label.text_surface, ((width - text_width2) / 2, 90))

    total_width = 2 * width

    GAME_DISPLAY.blit(
        label1,
        (Grid_Window_Width + (Menu_Width - total_width) / 2, Grid_Window_Height - 180),
    )
    GAME_DISPLAY.blit(
        label2,
        (
            Grid_Window_Width + width + (Menu_Width - total_width) / 2,
            Grid_Window_Height - 180,
        ),
    )
