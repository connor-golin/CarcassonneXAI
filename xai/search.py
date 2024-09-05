from collections import defaultdict
from Carcassonne_Game.Tile import Tile
from Carcassonne_Game.Tile_dict import CITY_OPENINGS_DICT
from pygameCarcassonneDir.pygameFunctions import get_city_tiles, rotate_point

BLOCKING_MULTIPLIER = 5

class MinimaxPlayer:
    def __init__(self, max_depth=3, max_moves_to_consider=5):
        self.max_depth = max_depth
        self.max_moves_to_consider = max_moves_to_consider

    def get_best_move(self, state):
        best_score, best_move, blocking_score = self.minimax(
            state, self.max_depth, float("-inf"), float("inf"), True
        )
        isBlocking = blocking_score > 0
        return best_score, best_move, isBlocking


    def minimax(self, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or state.isGameOver:
            eval_score, blocking_score = self.evaluate(state)
            return eval_score, None, blocking_score

        best_move = None
        moves = []

        # Generate and evaluate all possible moves
        for i, tile_count in enumerate(state.TileQuantities):
            if tile_count <= 0:
                continue
            current_tile_index = i
            for move in state.availableMoves(False, current_tile_index):
                move_eval, _ = self.evaluate_move(state, move)
                moves.append((move_eval, move))

        # Sort moves based on the evaluation scores
        moves.sort(reverse=maximizing_player, key=lambda x: x[0])
        # print(moves)

        # Limit the number of moves to consider
        moves = moves[: self.max_moves_to_consider]
        cumulative_blocking_score = 0  # Track blocking score cumulatively

        if maximizing_player:
            max_eval = float("-inf")
            for _, move in moves:
                new_state = state.CloneState()
                move_tuple = (
                    move.TileIndex,
                    move.X,
                    move.Y,
                    move.Rotation,
                    move.MeepleInfo,
                )
                new_state.move(move_tuple)
                eval, mv, blocking_score = self.minimax(new_state, depth - 1, alpha, beta, False)
                cumulative_blocking_score += blocking_score  # Accumulate blocking score
                if eval > max_eval:
                    max_eval = eval
                    best_move = move_tuple
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move, cumulative_blocking_score
        else:
            min_eval = float("inf")
            for _, move in moves:
                new_state = state.CloneState()
                move_tuple = (
                    move.TileIndex,
                    move.X,
                    move.Y,
                    move.Rotation,
                    move.MeepleInfo,
                )
                new_state.move(move_tuple)
                eval, mv, blocking_score = self.minimax(new_state, depth - 1, alpha, beta, True)
                cumulative_blocking_score += blocking_score  # Accumulate blocking score
                if eval < min_eval:
                    min_eval = eval
                    best_move = move_tuple
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move, cumulative_blocking_score


    def evaluate(self, state):
        player = state.playerSymbol
        opponent = 3 - player  # players are 1 and 2

        score_diff = state.Scores[player] - state.Scores[opponent]

        blocking_score = self.evaluate_blocking(state) * BLOCKING_MULTIPLIER

        evaluation_score = score_diff + blocking_score
        return evaluation_score, blocking_score

    def evaluate_blocking(self, state):
        blocking_score = 0
        player = state.playerSymbol
        opponent = 3 - player     

        for city_id, city in state.BoardCities.items():
            if not city.ClosedFlag:
                opponent_owns_city = city.Meeples[opponent - 1] > 0
                player_owns_city = city.Meeples[player - 1] > 0
                is_blocked = city.isBlocked(state) # TODO: Fix

                if opponent_owns_city and is_blocked:  # block opponent's city
                    blocking_score += city.Value
                elif player_owns_city and is_blocked:  # penalize blocking own city
                    blocking_score -= city.Value

        return blocking_score

    def evaluate_move(self, state, move):
        temp_state = state.CloneState()
        move_tuple = (move.TileIndex, move.X, move.Y, move.Rotation, move.MeepleInfo)
        temp_state.move(move_tuple)

        return self.evaluate(temp_state)

# TODO: Fix
# def isBlocked(state, x1, y1) -> bool:
#         opening_locations = city_openings(state)  # Get the openings for this city
#         print(f"Opening locations: {opening_locations}")
        
#         res = {}
#         for (x, y) in opening_locations:
#             res[(x, y)] = True

#         # Check each opening location
#         for (x, y) in opening_locations:
#             # Iterate through all tile types
#             for tile_index in range(0, 24):

#                 # Skip if no tiles of this type are left
#                 if state.TileQuantities[tile_index] <= 0:
#                     continue

#                 tile = Tile(tile_index)

#                 for rotation in range(4):  # Check all rotations
#                     # Get the surrounding spots for this tile
#                     SurroundingSpots = [(x-1, y), (x, y+1), (x+1, y), (x, y-1)]
                    
#                     fits, _ = state.doesTileFit(tile, rotation * 90, SurroundingSpots)
#                     if fits:
#                         res[(x, y)] = False
#                         return False  # If any tile fits, the city is not blocked
        
#         print(f"res: {res}")

#         # If no tile fits in any opening, the city is blocked
#         return True

# def city_openings(Carcassonne):
#     surroundings = []
#     board = Carcassonne.Board
#     city_index = 0

#     for (x, y), tile in Carcassonne.Board.items():
#         tile_index = tile.TileIndex
#         rotation = tile.Rotation // 90

#         if tile_index in CITY_OPENINGS_DICT:
#             # Iterate through all city openings lists for the tile
#             for city_openings in CITY_OPENINGS_DICT[tile_index]: # e.g. {0: [[0,1,2,3]], 1: ...}
#                 for city_opening in city_openings:

#                     # Determine the surrounding coordinates based on city openings
#                     if city_opening == 0:
#                         dx, dy = rotate_point(-1, 0, rotation)
#                     elif city_opening == 1:
#                         dx, dy = rotate_point(0, 1, rotation)
#                     elif city_opening == 2:
#                         dx, dy = rotate_point(1, 0, rotation)
#                     elif city_opening == 3:
#                         dx, dy = rotate_point(0, -1, rotation)
#                     else:
#                         continue

#                     # if its already in the surroundings, skip
#                     if (x + dx, y + dy) in get_city_tiles(Carcassonne).keys():
#                         continue

#                     if (x, y) in board.keys():
#                         tile = board[(x, y)]
#                         # surroundings[tile].append((x + dx, y + dy))
#                         surroundings.append((x + dx, y + dy))
#                         city_index += 1
#     return surroundings