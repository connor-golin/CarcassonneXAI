from collections import defaultdict
import json

# Load config file
with open("xai/config.json", "r") as config_file:
    config = json.load(config_file)

# Config Variables
BLOCKING_MULTIPLIER: int = config["BLOCKING_MULTIPLIER"]
MERGING_MULTIPLIER: int = config["MERGING_MULTIPLIER"]

class MinimaxPlayer:
    def __init__(self, max_depth, max_moves_to_consider, state):
        # initialize player and opponent
        self.max_depth = max_depth
        self.max_moves_to_consider = max_moves_to_consider
        self.player = None
        self.opponent = None
        self.blocked_cities = set()

        print(f"Minimax initialised with multiplers: Blocking: {BLOCKING_MULTIPLIER}, Merging: {MERGING_MULTIPLIER}")

    def get_best_move(self, state):
        # set player and opponent symbols
        self.player = state.playerSymbol - 1
        self.opponent = state.playerSymbol % 2

        print(f"Player: {self.player}, Opponent: {self.opponent}")

        # get best move using minimax
        best_score, best_move, is_blocking, is_merging = self.minimax(
            state, self.max_depth, float("-inf"), float("inf"), True
        )
        return best_score, best_move, is_blocking, is_merging

    def minimax(self, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or state.isGameOver:
            # evaluate score and blocking
            eval_score, blocking_score, merging_score = self.evaluate(state)
            return eval_score, None, blocking_score > 0, merging_score > 0

        best_move = None
        moves = []

        # generate and evaluate possible moves
        for i, tile_count in enumerate(state.TileQuantities):
            if tile_count <= 0:
                continue
            current_tile_index = i
            for move in state.availableMoves(False, current_tile_index):
                move_eval, _, _ = self.evaluate_move(state, move)
                moves.append((move_eval, move))

        # sort moves and limit to max_moves_to_consider
        moves.sort(reverse=maximizing_player, key=lambda x: x[0])
        moves = moves[:self.max_moves_to_consider]

        if maximizing_player:
            max_eval = float("-inf")
            is_blocking = False
            is_merging = False
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

                eval, mv, move_blocking, move_merging = self.minimax(
                    new_state, depth - 1, alpha, beta, False
                )
                if eval > max_eval:
                    max_eval = eval
                    best_move = move_tuple
                    is_blocking = move_blocking
                    is_merging = move_merging
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move, is_blocking, is_merging
        else:
            min_eval = float("inf")
            is_blocking = False
            is_merging = False
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

                eval, mv, move_blocking, move_merging = self.minimax(
                    new_state, depth - 1, alpha, beta, True
                )
                if eval < min_eval:
                    min_eval = eval
                    best_move = move_tuple
                    is_blocking = move_blocking
                    is_merging = move_merging
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move, is_blocking, is_merging

    def evaluate(self, state):
        # calculate score difference and blocking score
        score_diff = state.Scores[self.player] - state.Scores[self.opponent]
        blocking_score = self.evaluate_blocking(state) * BLOCKING_MULTIPLIER
        is_winning_farms, merging_score = self.evaluate_merging(state)

        if is_winning_farms:
            merging_score += 100

        total = score_diff + blocking_score + merging_score
        return total, blocking_score, merging_score

    def evaluate_merging(self, state):
        # Count meeples in fields for each player
        player_field_score = 0
        opponent_field_score = 0

        farmP1 = 3 * sum(
            [
                len([x for x in v.CityIndexes if state.BoardCities[x].ClosedFlag])
                for k, v in state.BoardFarms.items()
                if v.Pointer == v.ID
                and v.Meeples[0] >= v.Meeples[1]
                and v.Meeples[0] > 0
            ]
        )
        farmP2 = 3 * sum(
            [
                len([x for x in v.CityIndexes if state.BoardCities[x].ClosedFlag])
                for k, v in state.BoardFarms.items()
                if v.Pointer == v.ID
                and v.Meeples[1] >= v.Meeples[0]
                and v.Meeples[1] > 0
            ]
        )

        if self.player == 0:
            player_field_score += farmP1
            opponent_field_score += farmP2
        else:
            player_field_score += farmP2
            opponent_field_score += farmP1

        # Evaluate merging potential based on meeple difference
        field_score_difference = player_field_score - opponent_field_score

        is_winning_farms = field_score_difference > 0
        return abs(field_score_difference), is_winning_farms

    def evaluate_blocking(self, state):
        blocking_score = 0

        for city in state.BoardCities.values():
            # skip blocked or closed cities
            is_blocked = city.isBlocked(state)
            if city.ClosedFlag or city in self.blocked_cities or not is_blocked:
                continue

            # update blocked cities and score
            opponent_owns_city = city.Meeples[self.opponent] > 0
            player_owns_city = city.Meeples[self.player] > 0
            self.blocked_cities.add(city)

            if opponent_owns_city:  # reward blocking opponent
                blocking_score += city.Value
            elif player_owns_city:  # penalise blocking self
                blocking_score -= city.Value

        return blocking_score

    def evaluate_move(self, state, move):
        # evaluate move by simulating it
        temp_state = state.CloneState()
        move_tuple = (move.TileIndex, move.X, move.Y, move.Rotation, move.MeepleInfo)
        temp_state.move(move_tuple)

        return self.evaluate(temp_state)
