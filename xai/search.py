import json

# Load config file
with open("xai/config.json", "r") as config_file:
    config = json.load(config_file)

# Config Variables
BLOCKING_MULTIPLIER: int = config["BLOCKING_MULTIPLIER"]
MERGING_MULTIPLIER: int = config["MERGING_MULTIPLIER"]

class MinimaxPlayer:
    def __init__(self, max_depth, max_moves_to_consider):
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
            state, state, self.max_depth, float("-inf"), float("inf"), True
        )
        return best_score, best_move, is_blocking, is_merging

    def minimax(self, state_before_move, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or state.isGameOver:
            eval_score, blocking_score, merging_score = self.evaluate(state_before_move, state)
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
                    state, new_state, depth - 1, alpha, beta, False
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
                    state, new_state, depth - 1, alpha, beta, True
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

    def evaluate(self, state_before_move, state_after_move):
        # Calculate score difference and blocking score
        score_diff = state_after_move.Scores[self.player] - state_after_move.Scores[self.opponent]
        blocking_score = self.evaluate_blocking(state_after_move) * BLOCKING_MULTIPLIER
        merging_score = self.evaluate_merging(state_before_move, state_after_move) * MERGING_MULTIPLIER

        total = score_diff + blocking_score + merging_score
        return total, blocking_score, merging_score

    def evaluate_merging(self, state_before_move, state_after_move):
        merging_score = 0

        # IDs : owner in the before state
        field_owners_before = self.get_field_owners(state_before_move)
        # IDs : owner in the after state
        field_owners_after = self.get_field_owners(state_after_move)

        # Compare field ownerships to detect changes
        for field_id, owner_after in field_owners_after.items():
            owner_before = field_owners_before.get(field_id)
            if owner_before and owner_before != owner_after:
                # Ownership has changed
                if (owner_before == 'opponent' and owner_after == 'player') or (owner_before == 'opponent' and owner_after == 'tie'):
                    # We have gained control over a field
                    field = state_after_move.BoardFarms[field_id]
                    field_value = 3 * len([
                        x for x in field.CityIndexes
                        if state_after_move.BoardCities[x].ClosedFlag
                    ])
                    merging_score += field_value
                elif owner_before == 'player' and owner_after == 'opponent':
                    # We have lost control over a field
                    field = state_after_move.BoardFarms[field_id]
                    field_value = 3 * len([
                        x for x in field.CityIndexes
                        if state_after_move.BoardCities[x].ClosedFlag
                    ])
                    merging_score -= field_value

        return merging_score

    def get_field_owners(self, state):
        field_owners = {}
        for field_id, field in state.BoardFarms.items():
            # Resolve farm pointers
            while field.Pointer != field.ID:
                field = state.BoardFarms[field.Pointer]
            player_meeples = field.Meeples[self.player]
            opponent_meeples = field.Meeples[self.opponent]
            if player_meeples > opponent_meeples:
                field_owners[field_id] = 'player'
            elif opponent_meeples > player_meeples:
                field_owners[field_id] = 'opponent'
            else:
                field_owners[field_id] = 'tie'
        return field_owners

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

    def evaluate_move(self, state_before_move, move):
        # Simulate the move
        temp_state = state_before_move.CloneState()
        move_tuple = (move.TileIndex, move.X, move.Y, move.Rotation, move.MeepleInfo)
        temp_state.move(move_tuple)

        # Pass both states to the evaluate function
        return self.evaluate(state_before_move, temp_state)
