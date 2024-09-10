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