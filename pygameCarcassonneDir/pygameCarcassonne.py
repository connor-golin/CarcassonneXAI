import sys
import os
import pygame
import pygame_menu

# add 'Carcassonne' directory to sys.path
sys.path.append(os.path.join(os.getcwd()))
print(sys.path)
print(os.getcwd())

# import local scripts
from player.Player import HumanPlayer, RandomPlayer
from player.MCTS_Player import MCTSPlayer
from player.MCTS_RAVE_Player import MCTS_RAVEPlayer
from player.MCTS_ES_Player import MCTS_ES_Player
from player.Star1_Player import Star1
from player.Star2_5_Player import Star2_5

from Carcassonne_Game.Carcassonne import CarcassonneState
from Carcassonne_Game.Tile import Tile

from pygameCarcassonneDir.pygameNextTile import nextTile
from pygameCarcassonneDir.pygameFunctions import (
    playMove,
    drawGrid,
    diplayGameBoard,
    printScores,
    printTilesLeft,
)

from pygameCarcassonneDir.pygameSettings import (
    BLACK,
    WHITE,
    GRID,
    GRID_SIZE,
    GRID_BORDER,
    MENU_WIDTH,
)
from pygameCarcassonneDir.pygameSettings import MEEPLE_SIZE
from pygameCarcassonneDir.pygameSettings import displayScreen

# Number Keys
NumKeys = [
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
]

# list of player available to choose from
PLAYERS = [
    ("Human", HumanPlayer()),
    ("Random", RandomPlayer()),
    ("MCTS", MCTSPlayer(isTimeLimited=False, timeLimit=5)),
    ("RAVE", MCTS_RAVEPlayer(isTimeLimited=True, timeLimit=5)),
]

PLAYER1 = [HumanPlayer()]
PLAYER2 = [RandomPlayer()]

AI_MOVE_EVENT = pygame.USEREVENT + 1
AI_DELAY = 1000  # ms


# start menu
def startMenu():
    pygame.init()
    surface = pygame.display.set_mode((600, 400))

    def selectPlayer1(value, player):
        PLAYER1[0] = player

    def selectPlayer2(value, player):
        PLAYER2[0] = player

    def start_the_game():
        p1 = PLAYER1[0]
        p2 = PLAYER2[0]
        PlayGame(p1, p2)

    menu = pygame_menu.Menu("Welcome", 600, 400, theme=pygame_menu.themes.THEME_BLUE)
    menu.add.selector("Player 1 :", PLAYERS, onchange=selectPlayer1)
    menu.add.selector("Player 2 :", PLAYERS, onchange=selectPlayer2)
    menu.add.button("Play", start_the_game)
    menu.add.button("Quit", pygame_menu.events.EXIT)
    menu.mainloop(surface)


def FinalMenu(Carcassonne):
    FS = Carcassonne.FeatureScores
    Scores = Carcassonne.Scores
    pygame.init()
    surface = pygame.display.set_mode((600, 800))
    winnerText = (
        "Draw"
        if Carcassonne.winner == 0
        else "Player " + str(Carcassonne.winner) + " Wins!"
    )

    def nothingButton():
        pass

    def restart_the_game():
        startMenu()

    menu = pygame_menu.Menu(
        title="Welcome", width=600, height=800, theme=pygame_menu.themes.THEME_BLUE
    )
    menu.add.button(winnerText, nothingButton)
    menu.add.button(f'Player 1{" " * 20}Player 2', nothingButton)
    menu.add.button(f'{Scores[2]}{"Total":^40}{Scores[3]}', nothingButton)
    menu.add.button(
        f'{FS[0][0] + FS[0][3]}{"City":^37}{FS[1][0] + FS[1][3]}', nothingButton
    )
    menu.add.button(
        f'{FS[0][1] + FS[0][4]}{"Road":^37}{FS[1][1] + FS[1][4]}', nothingButton
    )
    menu.add.button(
        f'{FS[0][2] + FS[0][5]}{"Monastery":^33}{FS[1][2] + FS[1][5]}', nothingButton
    )
    menu.add.button(f'{FS[0][6]}{"Farm":^37}{FS[1][6]}', nothingButton)
    menu.add.button("Play Again", restart_the_game)
    menu.add.button("Quit", pygame_menu.events.EXIT)
    menu.mainloop(surface)

# main game loop
def PlayGame(p1, p2):
    global GAME_DISPLAY, CLOCK
    pygame.init()
    CLOCK = pygame.time.Clock()
    DisplayScreen = displayScreen(GRID, GRID_SIZE, GRID_BORDER, MENU_WIDTH, MEEPLE_SIZE)
    GAME_DISPLAY = DisplayScreen.pygameDisplay
    pygame.display.set_caption("Carcassonne")
    background = pygame.image.load("pygame_images/table.jpg")
    background = pygame.transform.scale(
        background, (DisplayScreen.Window_Width, DisplayScreen.Window_Height)
    )
    title = pygame.image.load("pygame_images/game_title.png")
    title = pygame.transform.scale(title, (274, 70))
    background.blit(title, (40, 7))
    Carcassonne = CarcassonneState(p1, p2)
    NT = nextTile(Carcassonne, DisplayScreen)
    NT.moveLabel = pygame.Surface((DisplayScreen.Window_Width, 50))
    done = False
    player = Carcassonne.p1
    isGameOver = False
    isStartOfGame = isStartOfTurn = hasSomethingNew = True
    selectedMove = [16, 0, 0, 0, None]
    rotation = 0
    newRotation = False
    numberSelected = 0

    if player.isAIPlayer:
        pygame.time.set_timer(AI_MOVE_EVENT, AI_DELAY)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not isGameOver:
                if player.isAIPlayer:
                    if event.type == AI_MOVE_EVENT:
                        player, selectedMove = playMove(
                            NT,
                            player,
                            Carcassonne,
                            NT.nextTileIndex,
                            isStartOfGame,
                            ManualMove=None,
                        )
                        NT = nextTile(Carcassonne, DisplayScreen)
                        NT.moveLabel = pygame.Surface((DisplayScreen.Window_Width, 50))
                        isStartOfTurn = True
                        hasSomethingNew = True
                        isStartOfGame = False
                        isGameOver = Carcassonne.isGameOver
                        if isGameOver:
                            pygame.time.set_timer(AI_MOVE_EVENT, 0)
                        else:
                            pygame.time.wait(AI_DELAY)
                            break
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            rotation = -1
                            newRotation = True
                        elif event.key == pygame.K_RIGHT:
                            rotation = 1
                            newRotation = True
                        if event.key in NumKeys:
                            numberStr = pygame.key.name(event.key)
                            numberSelected = int(numberStr)
                            if numberSelected == 0:
                                NT.Meeple = None
                            hasSomethingNew = True
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        X, Y = NT.evaluate_click(pygame.mouse.get_pos(), DisplayScreen)

                        if (X, Y) in NT.possibleCoordsMeeples:
                            rotation = 90 * NT.Rotated
                            ManualMove = (NT.nextTileIndex, X, Y, rotation, NT.Meeple)
                            player, selectedMove = playMove(
                                NT,
                                player,
                                Carcassonne,
                                NT.nextTileIndex,
                                isStartOfGame,
                                ManualMove,
                            )
                            NT = nextTile(Carcassonne, DisplayScreen)
                            NT.moveLabel = pygame.Surface(
                                (DisplayScreen.Window_Width, 50)
                            )
                            isStartOfTurn = True
                            hasSomethingNew = True
                            isStartOfGame = False
                            pygame.time.set_timer(AI_MOVE_EVENT, 1)
                        elif (X, Y) in list(NT.Carcassonne.Board.keys()):
                            print("check")
                            text = NT.displayTextClickedTile(X, Y)
                            print(text)
                        else:
                            print(f"Position invalid: X: {X}, Y:{Y}")
                    isGameOver = Carcassonne.isGameOver
                    if isGameOver:
                        isStartOfTurn = False
                        hasSomethingNew = False

        GAME_DISPLAY.blit(background, (0, 0))
        drawGrid(DisplayScreen)
        if hasSomethingNew:
            if player.name == "Human":
                NT.resetImage()
                i = 1
                for location_key in NT.Tile.AvailableMeepleLocs:
                    location_value = NT.Tile.AvailableMeepleLocs[location_key]

                    NT.addMeepleLocations(
                        location_key,
                        location_value,
                        i,
                        numberSelected,
                        NT.nextTileIndex,
                    )
                    NT.updateMeepleMenu(location_key, location_value, i, numberSelected)
                    i += 1
                NT.rotate(NT.Rotated, newRotation)
            else: 
                if not isGameOver:
                    NT.resetImage()
                    NT.pressSpaceInstruction()

        if isStartOfTurn:
            NT.updateMoveLabel(Carcassonne, selectedMove, isStartOfGame)

        printScores(Carcassonne, DisplayScreen)
        printTilesLeft(Carcassonne, DisplayScreen)

        if not isGameOver:
            NT.showNextTile(DisplayScreen, rotation, newRotation)
            NT.showInfos(DisplayScreen)
            NT.highlightPossibleMoves(DisplayScreen)

        newRotation = False
        numberSelected = 0

        diplayGameBoard(Carcassonne, DisplayScreen)
        pygame.display.flip()

        isStartOfTurn = False
        hasSomethingNew = False

        CLOCK.tick(60)

        if isGameOver:
            print(
                f"Winner: Player {Carcassonne.winner}, Scores:  P1: {Carcassonne.Scores[0]} - P2: {Carcassonne.Scores[1]}"
            )
            FinalMenu(Carcassonne)


if __name__ == "__main__":
    startMenu()
