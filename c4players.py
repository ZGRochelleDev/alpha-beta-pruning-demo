import random

class ConnectFourPlayer:
    def get_move(self):
        # Must return a value between 0 and 6 (inclusive), where 0 is the left-most column and 6 is the right-most column.
        raise NotImplementedError('Must be implemented by subclass')

    def is_automated(self):
        # AI players should return True, human players should return False
        return True

class ConnectFourHumanPlayer(ConnectFourPlayer):
    def __init__(self, model):
        self.model = model

    def is_automated(self):
        return False

    def get_move(self):
        valid_input = False
        valid_columns = self.model.get_valid_moves()

        while not valid_input:
            try:
                column = int(input('Enter column (1-7): '))
                if column < 1 or column > 7:
                    raise ValueError()
                else:
                    valid_input = True

                if valid_columns[column-1]:
                    return column-1
                else:
                    print('That column is full. Pick again.')
                    valid_input = False
            except ValueError:
                print('Invalid input.')

        # Should not get here
        return -1


class ConnectFourRandomPlayer(ConnectFourPlayer):
    def __init__(self, model):
        self.model = model

    def get_move(self):
        moves = self.model.get_valid_moves()
        m = random.randrange(7)
        while not moves[m]:
            m = random.randrange(7)
        return m

class ConnectFourAIPlayer(ConnectFourPlayer):
    def __init__(self, model):
        self.model = model
        self.player_num = None
        self.max_depth = 4


    def eval_enhanced_scorer(self, window):
        score = 0

        ## figure out which number is the opponent
        if self.player_num == 1:
            opponent = 2
        else:
            opponent = 1

        ## count how many AI pieces, opponent pieces, and empty spaces are in this group of 4
        my_count = window.count(self.player_num)
        opp_count = window.count(opponent)
        empty_count = window.count(-1)

        ## good patterns for the AI
        if my_count == 4:
            score += 100
        elif my_count == 3 and empty_count == 1:
            score += 12
        elif my_count == 2 and empty_count == 2:
            score += 5

        ## dangerous opponent patterns - the opponent is close to winning
        if opp_count == 4:
            score -= 100
        elif opp_count == 3 and empty_count == 1:
            score -= 15
        elif opp_count == 2 and empty_count == 2:
            score -= 5

        return score

    def eval(self, state):
    ## Source: https://boardgamegeek.com/thread/3321924/connect-four-probability-diagram-aka-strategy-guid
    ## Below, evaluate the utility of a non-terminal state.
    ## For each position on the board there is a specific number of "Connect 4" possibilities.
    ## For example, position A6 has exactly 3 possibilities. Mapping it out looks like this:
        #     A  B  C  D   E   F  G
        # 1:  3  4  5  7   5   4  3
        # 2:  4  6  8  10  8   6  4
        # 3:  5  8  11 13  11  8  5
        # 4:  5  8  11 13  11  8  5
        # 5:  4  6  8  10  8   6  4
        # 6:  3  4  5  7   5   4  3

        utility_map = [
            [3, 4, 5, 5, 4, 3],
            [4, 6, 8, 8, 6, 4],
            [5, 8, 11, 11, 8, 5],
            [7, 10, 13, 13, 10, 7],
            [5, 8, 11, 11, 8, 5],
            [4, 6, 8, 8, 6, 4],
            [3, 4, 5, 5, 4, 3]
        ]

        score = 0

        ## first, score each piece based on where it is on the board
        ## center positions are worth more than edge positions
        for x in range(7):
            for y in range(6):
                if state[x][y] == self.player_num:
                    score += utility_map[x][y]
                elif state[x][y] != -1:
                    score -= utility_map[x][y]

        ## below, check every possible Connect-4 on the board and give it a score ##

        # look at every horizontal group of 4
        for y in range(6):
            for x in range(4):
                window = [state[x][y], state[x+1][y], state[x+2][y], state[x+3][y]]
                score += self.eval_enhanced_scorer(window)

        # look at every vertical group of 4
        for x in range(7):
            for y in range(3):
                window = [state[x][y], state[x][y+1], state[x][y+2], state[x][y+3]]
                score += self.eval_enhanced_scorer(window)

        # look at every diagonal group of 4 going down-right
        for x in range(4):
            for y in range(3):
                window = [state[x][y], state[x+1][y+1], state[x+2][y+2], state[x+3][y+3]]
                score += self.eval_enhanced_scorer(window)

        # look at every diagonal group of 4 going down-left
        for x in range(3, 7):
            for y in range(3):
                window = [state[x][y], state[x-1][y+1], state[x-2][y+2], state[x-3][y+3]]
                score += self.eval_enhanced_scorer(window)

        return score

    def whose_turn(self, state):
        ones = 0
        twos = 0

        for column in state:
            for value in column:
                if value == 1:
                    ones += 1
                elif value == 2:
                    twos += 1

        if ones == twos:
            return 1
        else:
            return 2

    ## Note: I moved the non-terminal checking code to a seperate function called eval() to make it easier to read and modify. The terminal checking code is still in utility().
    def utility(self, state):
        ## check if someone has won
        for y in range(6):
            for x in range(7):
                if state[x][y] != -1:
                    if self.check_diagonal(state, x, y) or self.check_inline(state, x, y):
                        winner = state[x][y]

                        ## if terminal and the next turn is player 1:
                        ##   then player 2 just made the winning move
                        ## if the next turn is player 2:
                        ##   then player 1 just made the winning move
                        if winner == self.player_num:
                            return 1000
                        else:
                            return -1000

        ## draw
        return 0

    def max_value(self, state, alpha, beta, depth):
        if self.terminal_test(state):
            return self.utility(state)

        if depth >= self.max_depth:
            return self.eval(state)

        v = -float('inf')
        for a in self.actions(state):
            v = max(v, self.min_value(self.result(state, a), alpha, beta, depth+1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, state, alpha, beta, depth):
        if self.terminal_test(state):
            return self.utility(state)

        if depth >= self.max_depth:
            return self.eval(state)

        v = float('inf')
        for a in self.actions(state):
            v = min(v, self.max_value(self.result(state, a), alpha, beta, depth+1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def alpha_beta_search(self, state):
        # v = self.max_value(state, -float('inf'), float('inf'))

        # for a in self.actions(state):
        #     if self.min_value(self.result(state, a), -float('inf'), float('inf')) == v:
        #         return a

        alpha = -float('inf')
        beta = float('inf')
        best_value = -float('inf')
        best_move = None

        for a in self.actions(state):
            value = self.min_value(self.result(state, a), alpha, beta, 1)
            if value > best_value:
                best_value = value
                best_move = a
            alpha = max(alpha, best_value)

        return best_move

    def result(self, state, action):
        ## the chip for the player whose turn it is
        player_num = self.whose_turn(state)

        ## copy the 2D list
        newstate = [col[:] for col in state]

        ## drop new chip into the column at "action"
        ## start from the bottom and iterate upwards
        for row in range(5, -1, -1):
            if newstate[action][row] == -1:
                newstate[action][row] = player_num
                break
        return newstate

    def actions(self, state):
        moves = []
        for col in range(len(state)):
            if state[col][0] == -1:
                moves.append(col)
        return moves

    def check_diagonal(self, state, x, y):
        chip = state[x][y]
        if chip == -1:
            return False

        ## check right-diagonal
        if y + 3 <= 5 and x + 3 <= 6:
            if state[x][y] == chip and state[x+1][y+1] == chip and state[x+2][y+2] == chip and state[x+3][y+3] == chip:
                return True

        ## check left-diagonal
        if y + 3 <= 5 and x - 3 >= 0:
            if state[x][y] == chip and state[x-1][y+1] == chip and state[x-2][y+2] == chip and state[x-3][y+3] == chip:
                return True

        return False

    def check_inline(self, state, x, y):
        chip = state[x][y]
        if chip == -1:
            return False

        ## check 4 in a row
        if x + 3 <= 6:
            if state[x][y] == chip and state[x+1][y] == chip and state[x+2][y] == chip and state[x+3][y] == chip:
                return True

        ## check 4 in a column
        if y + 3 <= 5:
            if state[x][y] == chip and state[x][y+1] == chip and state[x][y+2] == chip and state[x][y+3] == chip:
                return True

        return False

    def get_move(self):
        state = self.model.get_grid()

        if self.player_num is None:
            self.player_num = self.model.get_turn()

        print("AI starting search...")
        move = self.alpha_beta_search(state)
        print("AI finished search. move =", move)
        return move

    def is_automated(self):
        # The AI player should return True, human players should return False
        return True

    def terminal_test(self, state):
        # return true if the game would terminate in this state
        # terminate means: if a player has won or if the game has reached a draw

        ## check for win
        for y in range(6):
            for x in range(7):
                if state[x][y] != -1:
                    diag = self.check_diagonal(state, x, y)
                    inline = self.check_inline(state, x, y)
                    if diag or inline:
                        return True

        ## check for draw
        if len(self.actions(state)) == 0:
            return True

        return False
