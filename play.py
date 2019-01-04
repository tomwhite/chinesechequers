from chinesechequers import *
import itertools
import random
import time

from blessed import Terminal


class Random:
    def __init__(self, white):
        self.white = white

    def set_white(self, white):
        self.white = white

    def play(self, board):
        # restrict to forward (or sideways) moves
        if self.white:
            moves = [move for move in board.generate_all_moves(self.white) if move.direction() >= 0]
        else:
            moves = [move for move in board.generate_all_moves(self.white) if move.direction() <= 0]
        move = random.choice(moves)
        return move

    def __str__(self):
        return "Random"

class Greedy:
    def __init__(self, white, randomize=False):
        self.white = white
        self.randomize = randomize

    def set_white(self, white):
        self.white = white

    def play(self, board):
        # choose move that minimizes sum of distances to target corner
        moves = list(board.generate_all_moves(self.white))
        if self.randomize:
            random.shuffle(moves)
        move = min(moves, key=lambda move: self._get_cost(board, move))
        return move

    def _get_cost(self, board, move):
        target = Hex(board.size - 1, board.size - 1) if self.white else Hex(0, 0)
        new_board = board.move(move)
        cost = 0
        for piece in new_board.white_pieces if self.white else new_board.black_pieces:
            cost += piece.distance(target)
        return cost

    def __str__(self):
        return "Greedy"

class Minimax:
    def __init__(self, white, depth=2, randomize=False):
        self.white = white
        self.depth = depth
        self.randomize = randomize

    def set_white(self, white):
        self.white = white

    def play(self, board):
        move, value = self._minimax(board, self.depth, True)
        return move

    def _minimax(self, board, depth, maximizing_player):
        """See https://en.wikipedia.org/wiki/Minimax#Pseudocode"""
        if depth == 0 or board.white_has_won() or board.black_has_won():
            return None, self._get_heuristic_value(board)
        if maximizing_player:
            value = float("-inf")
            best = (None, value)
            for move in self._generate_moves(board, self.white):
                mm = self._minimax(board.move(move), depth - 1, False)
                if mm[1] > best[1]:
                    best = (move, mm[1])
            return best
        else:
            value = float("inf")
            best = (None, value)
            for move in self._generate_moves(board, not self.white):
                mm = self._minimax(board.move(move), depth - 1, True)
                if mm[1] < best[1]:
                    best = (move, mm[1])
            return best

    def _generate_moves(self, board, white):
        moves = list(board.generate_all_moves(white=white))
        if self.randomize:
            random.shuffle(moves)
        return moves

    def _get_heuristic_value(self, board):
        value = 0

        white_target = Hex(board.size - 1, board.size - 1)
        for piece in board.white_pieces:
            value -= piece.distance(white_target)

        black_target = Hex(0, 0)
        for piece in board.black_pieces:
            value += piece.distance(black_target)

        return value if self.white else -value

    def __str__(self):
        return "Minimax({})".format(self.depth)


class AlphaBeta(Minimax):
    def __init__(self, white, depth=2):
        super().__init__(white, depth)

    def play(self, board):
        move, value = self._alphabeta(board, self.depth, float("-inf"), float("+inf"), True)
        return move

    def _alphabeta(self, board, depth, alpha, beta, maximizing_player):
        """See https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning#Pseudocode"""
        if depth == 0 or board.white_has_won() or board.black_has_won():
            return board, self._get_heuristic_value(board)
        if maximizing_player:
            value = float("-inf")
            best = (None, value)
            for move in board.generate_all_moves(white=self.white):
                mm = self._alphabeta(board.move(move), depth - 1, alpha, beta, False)
                if mm[1] > best[1]:
                    best = (move, mm[1])
                alpha = max(alpha, mm[1])
                if alpha >= beta:
                    break
            return best
        else:
            value = float("inf")
            best = (None, value)
            for move in board.generate_all_moves(white=not self.white):
                mm = self._alphabeta(board.move(move), depth - 1, alpha, beta, True)
                if mm[1] < best[1]:
                    best = (move, mm[1])
                beta = min(beta, mm[1])
                if alpha >= beta:
                    break
            return best

    def __str__(self):
        return "AlphaBeta({})".format(self.depth)


class Human:
    def __init__(self, white, term):
        self.white = white
        self.term = term
        self.x = 0
        self.y = 0

    @property
    def hex(self):
        return Hex((self.x - self.y) // 2, self.y)

    def move(self, dx, dy, board, start):
        if self.hex != start:
            self.clear_char(board)
        self.x += dx
        self.y += dy
        self.reverse_char(board)

    def get_char_at(self, board):
        hex = self.hex
        if hex in board.white_pieces:
            return board.WHITE
        elif hex in board.black_pieces:
            return board.BLACK
        else:
            return board.EMPTY

    def clear_char(self, board):
        print(self.term.move(self.y + 1, self.x) + self.get_char_at(board))

    def reverse_char(self, board):
        print(self.term.move(self.y + 1, self.x) + self.term.reverse(self.get_char_at(board)))

    def play(self, board):
        legal_moves = list(board.generate_all_moves(self.white))
        legal_starts = [move.start for move in legal_moves]
        start = None
        move = None
        print(self.term.move(board.size + 1, 0) + "Choose move start         ")
        self.reverse_char(board)
        with self.term.cbreak():
            val = ''
            while val.lower() != 'q':
                val = self.term.inkey()
                if val.code == self.term.KEY_LEFT and self.hex.q > 0:
                    self.move(-2, 0, board, start)
                elif val.code == self.term.KEY_RIGHT and self.hex.q < board.size - 1:
                    self.move(2, 0, board, start)
                elif val.code == self.term.KEY_UP and self.hex.r > 0:
                    self.move(-1, -1, board, start)
                elif val.code == self.term.KEY_DOWN and self.hex.r < board.size - 1:
                    self.move(1, 1, board, start)
                elif val.code == self.term.KEY_ENTER:
                    if start is None:
                        start = self.hex
                        if start in legal_starts:
                            print(self.term.move(board.size + 1, 0) + "Choose move end           ")
                        else:
                            print(self.term.move(board.size + 1, 0) + "Not a valid move start    ")
                            start = None
                    else:
                        move = Move(start, self.hex)
                        if move in legal_moves:
                            print(self.term.move(board.size + 1, 0) + "                          ")
                            break
                        else:
                            print(self.term.move(board.size + 1, 0) + "Not a valid move end      ")
                            move = None
        return move

    def __str__(self):
        return "Human"


def play_interactive(player1, player2, size=7, term=None):
    assert player1.white
    assert not player2.white

    board = Board.start(size=size)
    num_white_moves = 0
    num_black_moves = 0

    with term.fullscreen(), term.hidden_cursor():
        print(term.move(0, 0) + "{} (W) - {} (B)".format(player1, player2))
        print(term.move(1, 0) + str(board))
        while True:
            if not isinstance(player1, Human) and not isinstance(player2, Human):
                with term.cbreak(): # wait for key press
                    inp = term.inkey()
            move = player1.play(board)
            board = board.move(move)
            if not isinstance(player1, Human):
                animate_move(term, board, move)
            print(term.move(1, 0) + str(board))
            num_white_moves += 1
            if board.white_has_won():
                print("White won after {} moves".format(num_white_moves))
                break
            move = player2.play(board)
            board = board.move(move)
            if not isinstance(player2, Human):
                animate_move(term, board, move)
            term.clear()
            print(term.move(1, 0) + str(board))
            num_black_moves += 1
            if board.black_has_won():
                print("Black won after {} moves".format(num_black_moves))
                break
        with term.cbreak(): # wait for key press
            inp = term.inkey()


def animate_move(term, board, move):
    x, y = hex_to_cartesian(move.start)
    print(term.move(y + 1, x) + term.reverse(board.WHITE))
    time.sleep(1)
    print(term.move(y + 1, x) + board.EMPTY)
    if move.jump_path is None:
        x, y = hex_to_cartesian(move.end)
        print(term.move(y + 1, x) + term.reverse(board.WHITE))
        time.sleep(0.5)
    else:
        for position in move.jump_path:
            x, y = hex_to_cartesian(position)
            print(term.move(y + 1, x) + term.reverse(board.WHITE))
            time.sleep(0.5)
            print(term.move(y + 1, x) + board.EMPTY)


def hex_to_cartesian(hex):
    return hex.q * 2 + hex.r, hex.r


def play_series(player1, player2, size=7, games=1):
    assert player1.white
    assert not player2.white

    player1_wins = 0
    player2_wins = 0
    draws = 0
    shortest_game = 100
    for _ in range(games):
        board = Board.start(size=size)
        num_moves = 0
        while True:
            move = player1.play(board)
            board = board.move(move)
            if board.white_has_won():
                player1_wins += 1
                break
            move = player2.play(board)
            board = board.move(move)
            if board.black_has_won():
                player2_wins += 1
                break
            if num_moves >= 100:
                draws += 1
                break
            num_moves += 1
        if num_moves < shortest_game:
            shortest_game = num_moves
        print('.', end='', flush=True)
    return player1_wins, player2_wins, draws, shortest_game


def play_round_robin(players, size=7, games=1):
    all_results = {}
    for player1, player2 in itertools.combinations(players, 2):
        print(player1, player2)
        player1.white = True
        player2.white = False
        result1 = play_series(player1, player2, size, games)
        player1.white = False
        player2.white = True
        result2 = play_series(player2, player1, size, games)
        all_results[(player1, player2)] = (result1[0] + result2[1], result1[1] + result2[0], result1[2] + result2[2], min(result1[3], result2[3]))
    print()
    for k, v in all_results.items():
        player1 = k[0]
        player2 = k[1]
        print("{} - {}, {}, {}, {}, {}".format(player1, player2, v[0], v[1], v[2], v[3]))

if __name__ == '__main__':
    term = Terminal()
    player1 = Greedy(white=True)
    #player2 = Minimax(white=False)
    player2 = Human(white=False, term=term)
    play_interactive(player1, player2, term=term)
    #print(play_series(AlphaBeta(white=True, depth=4), AlphaBeta(white=False, depth=3), 7, 1))
    #play_round_robin([Random(white=True), Greedy(white=True, randomize=True), Minimax(white=True, depth=2, randomize=True), AlphaBeta(white=True, depth=3)], games=10)

    # following gets into a loop (odd!)
    #play_interactive(AlphaBeta(white=True, depth=4), AlphaBeta(white=False, depth=3), term=term)
