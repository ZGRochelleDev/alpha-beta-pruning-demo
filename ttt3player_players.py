import copy


class TTT3PlayerHumanPlayer:
    def __init__(self, model, symbol):
        self.model = model
        self.symbol = symbol

    def is_automated(self):
        return False

    def get_move(self):
        valid_input = False
        valid_moves = self.model.get_valid_moves()

        while not valid_input:
            try:
                move = int(input('Enter move (1-16): '))
                if move < 1 or move > 16:
                    raise ValueError()
                else:
                    valid_input = True

                if move in valid_moves:
                    return move
                else:
                    print('That spot is full. Pick again.')
                    valid_input = False
            except ValueError:
                print('Invalid input.')

        # Should not get here
        return -1


class TTT3PlayerAIPlayer:
    def __init__(self, model, symbol):
        self.model = model
        self.symbol = symbol

    def is_automated(self):
        return True

    # Assume actions are numbered 1-16
    def result(self, state, action):
        newstate = copy.deepcopy(state)
        turn = self._get_turn(state)

        action -= 1 # Adjustment of 1
        col = action % 4
        row = action // 4
        newstate[row][col] = turn

        return newstate

    def actions(self, state):
        moves = []
        for row in range(4):
            for col in range(4):
                if state[row][col] is None:
                    moves.append(row*4 + col + 1)
        return moves

    def terminal_test(self, state):
        # Check for horizontal win
        for row in range(4):
            for startcol in range(2):
                if state[row][startcol] is not None and state[row][startcol] == state[row][startcol+1] and state[row][startcol] == state[row][startcol+2]:
                    return True
        # Check for vertical win
        for col in range(4):
            for startrow in range(2):
                if state[startrow][col] is not None and state[startrow][col] == state[startrow+1][col] and state[startrow][col] == state[startrow+2][col]:
                    return True
        # Check for diagonal \ win
        for startrow in range(2):
            for startcol in range(2):
                if state[startrow][startcol] is not None and state[startrow][startcol] == state[startrow+1][startcol+1] and state[startrow][startcol] == state[startrow+2][startcol+2]:
                    return True
        # Check for diagonal / win
        for startrow in range(2,4):
            for startcol in range(2):
                if state[startrow][startcol] is not None and state[startrow][startcol] == state[startrow-1][startcol+1] and state[startrow][startcol] == state[startrow-2][startcol+2]:
                    return True
        
        return self._is_draw(state)

    def utility(self, state):
        if self._get_winner(state) == self.symbol:
            return 1000
        elif self._get_winner(state) is not None:
            return -1000
        if self._is_draw(state):
            return 0

        return 0 # Should not happen

    def _is_draw(self, state):
        all_filled = True
        for row in range(4):
            for col in range(4):
                if state[row][col] is None:
                    all_filled = False
        return all_filled

    def _get_winner(self, state):
        # Check for horizontal win
        for row in range(4):
            for startcol in range(2):
                if state[row][startcol] is not None and state[row][startcol] == state[row][startcol+1] and state[row][startcol] == state[row][startcol+2]:
                    return state[row][startcol]
        # Check for vertical win
        for col in range(4):
            for startrow in range(2):
                if state[startrow][col] is not None and state[startrow][col] == state[startrow+1][col] and state[startrow][col] == state[startrow+2][col]:
                    return state[0][col]
        # Check for diagonal \ win
        for startrow in range(2):
            for startcol in range(2):
                if state[startrow][startcol] is not None and state[startrow][startcol] == state[startrow+1][startcol+1] and state[startrow][startcol] == state[startrow+2][startcol+2]:
                    return state[startrow][startcol]
        # Check for diagonal / win
        for startrow in range(2,4):
            for startcol in range(2):
                if state[startrow][startcol] is not None and state[startrow][startcol] == state[startrow-1][startcol+1] and state[startrow][startcol] == state[startrow-2][startcol+2]:
                    return state[startrow][startcol]

        return None # Uh-oh

    def _get_turn(self, state):
        empties = 0
        for row in range(4):
            for col in range(4):
                if state[row][col] is None:
                    empties += 1

        if empties % 3 == 1:
            return 'X'
        elif empties % 3 == 0:
            return 'O'
        else:
            return '+'

    ## below is minimax code adapted from pseudocode in Artificial Intelligence: A Modern Approach - by Russell and Norvig
    def symbol_index(self, symbol):
        ## convert each symbol into a position in a list, so we can compare the scores for the current player
        if symbol == 'X':
            return 0
        elif symbol == 'O':
            return 1
        else:
            return 2


    ## the utility function does not return a list like the ruberic states, but instead returns a single number for the current player. So, I didn't use it in the minimax code and replaced it with the eval function below.
    def eval(self, state):
        ## check if someone has won the game
        winner = self._get_winner(state)

        ## return a 3-number list
        ## each position in the list is the score for one player:
        ##   [X score, O score, + score]
        if winner == 'X':
            return [1000, -1000, -1000]
        elif winner == 'O':
            return [-1000, 1000, -1000]
        elif winner == '+':
            return [-1000, -1000, 1000]
        elif self._is_draw(state):
            ## call a draw if the board is full and no one has won
            return [0, 0, 0]

        ## if the state is not terminal, then give all three players a score of 0
        ## this way, the AI won't prefer one non-terminal state over another
        return [0, 0, 0]

    def max_value(self, state, depth):
        ## stop searching if the game is over of if we reached the depth cutoff
        if self.terminal_test(state):
            return self.eval(state)

        if depth >= 5:
            return self.eval(state)

        ## determine whose turn, then convert that symbol into the correct list index
        turn = self._get_turn(state)
        turn_i = self.symbol_index(turn)

        best_value = None

        ## try every possible move
        for a in self.actions(state):
            ## make the move, then increase the depth
            value = self.max_value(self.result(state, a), depth + 1)

            ## is this move better for the current player than the best seen so far?
            if best_value is None or value[turn_i] > best_value[turn_i]:
                best_value = value

        ## return the best score list found
        return best_value

    def get_move(self):
        state = self.model.get_grid()

        ## determine which score in the list belongs to this AI
        index = self.symbol_index(self.symbol)

        best_move = None
        best_value = None

        ## try every legal move
        for a in self.actions(state):
            ## look ahead at the result of making this move
            value = self.max_value(self.result(state, a), 1)

            ## choose the move that gives this AI the best score
            if best_value is None or value[index] > best_value[index]:
                best_value = value
                best_move = a

        ## return the best move
        return best_move
