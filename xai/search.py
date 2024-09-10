from collections import defaultdict

BLOCKING_MULTIPLIER = 5  # multiplier for blocking score

class MinimaxPlayer:
    def __init__(self, max_depth, max_moves_to_consider, state):
        # initialize player and opponent
        self.max_depth = max_depth
        self.max_moves_to_consider = max_moves_to_consider
        self.player = None
        self.opponent = None
        self.blocked_cities = set()

    def get_best_move(self, state):
        # set player and opponent symbols
        self.player = state.playerSymbol - 1
        self.opponent = state.playerSymbol % 2

        # get best move using minimax
        best_score, best_move, is_blocking = self.minimax(
            state, self.max_depth, float("-inf"), float("inf"), True
        )
        return best_score, best_move, is_blocking

    def minimax(self, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or state.isGameOver:
            # evaluate score and blocking
            eval_score, blocking_score = self.evaluate(state)
            return eval_score, None, blocking_score > 0

        best_move = None
        moves = []

        # generate and evaluate possible moves
        for i, tile_count in enumerate(state.TileQuantities):
            if tile_count <= 0:
                continue
            current_tile_index = i
            for move in state.availableMoves(False, current_tile_index):
                move_eval, _ = self.evaluate_move(state, move)
                moves.append((move_eval, move))

        # sort moves and limit to max_moves_to_consider
        moves.sort(reverse=maximizing_player, key=lambda x: x[0])
        moves = moves[:self.max_moves_to_consider]

        if maximizing_player:
            max_eval = float("-inf")
            is_blocking = False
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

                eval, mv, move_blocking = self.minimax(
                    new_state, depth - 1, alpha, beta, False
                )
                if eval > max_eval:
                    max_eval = eval
                    best_move = move_tuple
                    is_blocking = move_blocking
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move, is_blocking
        else:
            min_eval = float("inf")
            is_blocking = False
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

                eval, mv, move_blocking = self.minimax(
                    new_state, depth - 1, alpha, beta, True
                )
                if eval < min_eval:
                    min_eval = eval
                    best_move = move_tuple
                    is_blocking = move_blocking
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move, is_blocking

    def evaluate(self, state):
        # calculate score difference and blocking score
        score_diff = state.Scores[self.player] - state.Scores[self.opponent]
        blocking_score = self.evaluate_blocking(state) * BLOCKING_MULTIPLIER

        evaluation_score = score_diff + blocking_score
        return evaluation_score, blocking_score

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
