import math


class Hex:
    """A location on the board."""

    dict = {} # cache instances for efficiency

    @classmethod
    def __get(cls, q, r):
        return cls.dict.get((q, r))

    def __new__(cls, q, r):
        o = cls.__get(q, r)
        if o:
            return o
        h = super(Hex, cls).__new__(cls)
        h.q = q
        h.r = r
        h.hash = hash((q, r))
        h.pairs = None
        cls.dict[(q, r)] = h
        return h

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.q == other.q and self.r == other.r
        return False

    def __hash__(self):
        return self.hash

    def __repr__(self):
        return "({}, {})".format(self.q, self.r)

    def __str__(self):
        return self.__repr__()

    def neighbor_pairs(self):
        """Return all the immediate neighbors (and their neighbors in the same direction) of hex"""
        if self.pairs is None: # cache since this is called a lot
            pairs = []
            for q in (-1, 0, 1):
                r1 = max(-1, -q - 1)
                r2 = min(1, -q + 1)
                for r in range(r1, r2 + 1):
                    if q == 0 and r == 0:
                        continue
                    pairs.append((Hex(q + self.q, r + self.r), Hex(2 * q + self.q, 2 * r + self.r)))
            self.pairs = pairs
        return self.pairs

    def distance(self, other):
        """Return 'euclidean' distance to another Hex"""
        return math.sqrt((other.q - self.q) * (other.q - self.q) + (other.r - self.r) * (other.r - self.r))


class Move:
    """A move from one location to another."""

    def __init__(self, start, end, jump_path=None):
        self.start = start
        self.end = end
        self.jump_path = jump_path

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.start == other.start and self.end == other.end
        return False

    def __hash__(self):
        return hash((self.start, self.end))

    def __repr__(self):
        return "{}->{}".format(self.start, self.end)

    def direction(self):
        """
        Return a number whose sign indicates the direction of the move on the board.
        Positive is forwards, negative is backwards, zero is sideways.
        """
        return self.end.q - self.start.q + self.end.r - self.start.r

    def __str__(self):
        return "{}{} {}{}".format(self.start.q, self.start.r, self.end.q, self.end.r)


class Board:
    """A board containing the pieces of both players."""

    EMPTY = '\u00B7'
    BLACK = '\u25CF'
    WHITE = '\u25CB'

    @classmethod
    def start(cls, size=7):
        """Create a starting board of the given size (length of one side)"""
        piece_rows = int(size / 2)
        white_pieces = [Hex(q, r) for q in range(piece_rows) for r in range(piece_rows) if q + r < piece_rows]
        black_pieces = [Hex(size - 1 - q, size - 1 - r) for q in range(piece_rows) for r in range(piece_rows) if q + r < piece_rows]
        # the goal is for white to get to black's start position and vice versa
        white_win = frozenset(black_pieces)
        black_win = frozenset(white_pieces)
        return cls(white_pieces, black_pieces, size, white_win, black_win)

    def __init__(self, white_pieces, black_pieces, size, white_win, black_win):
        """Create a board with the given white and black pieces of the given size"""
        # TODO: assert pieces and size are consistent
        self.white_pieces = frozenset(white_pieces)
        self.black_pieces = frozenset(black_pieces)
        self.size = size
        self.white_win = white_win
        self.black_win = black_win
        assert len(self.white_pieces & self.black_pieces) == 0
        assert len(self.white_pieces) == len(self.white_win)
        assert len(self.black_pieces) == len(self.black_win)

    def white_has_won(self):
        return self.white_pieces == self.white_win

    def black_has_won(self):
        return self.black_pieces == self.black_win

    def on_board(self, hex):
        """Return true if the given location is on the board"""
        return 0 <= hex.q < self.size and 0 <= hex.r < self.size

    def piece_at(self, hex):
        """Return true if there is a piece at the given location on the board"""
        return hex in self.white_pieces or hex in self.black_pieces

    def generate_moves(self, piece):
        # go through all the immediate neighbors
        for neighbor, _ in piece.neighbor_pairs():
            # return neighbor only if it is on the board and empty (since the piece could move there)
            if self.on_board(neighbor) and not self.piece_at(neighbor):
                yield Move(piece, neighbor)
        # then go through all the jump paths
        for move in self._generate_all_jump_moves(piece):
            yield move

    def _generate_all_jump_moves(self, piece):
        """Return all the positions that are multiple jumps for the given piece"""
        jump_paths = []
        new = [(piece, jump) for jump in self._generate_single_jumps(piece)]
        jump_paths.extend(new)
        while True:
            new = self._extend_jump_paths(new)
            if len(new) == 0:
                break
            jump_paths.extend(new)
        # and return unique jump moves (along with a jump path for rendering)
        jumps_dict = {jump_path[-1]:jump_path for jump_path in jump_paths}
        for jump, jump_path in jumps_dict.items():
            yield Move(piece, jump, jump_path)

    def _generate_single_jumps(self, piece):
        """Return all the positions that are single jumps for the given piece"""
        for neighbor1, neighbor2 in piece.neighbor_pairs():
            # return neighbor2 only if neighbor1 has a piece, and neighbor2 is on the board and is a piece
            if self.piece_at(neighbor1) and self.on_board(neighbor2) and not self.piece_at(neighbor2):
                yield neighbor2

    def _extend_jump_paths(self, jump_paths):
        # extend paths where possible and return only the ones that have been extended
        new = []
        for jump_path in jump_paths:
            last = jump_path[-1]
            for next in self._generate_single_jumps(last):
                if next not in jump_path: # avoid circles
                    new.append(jump_path + (next,)) # extend the path
        return new

    def generate_all_moves(self, white):
        """Return all the valid moves from this board"""
        for start in self.white_pieces if white else self.black_pieces:
            for move in self.generate_moves(start):
                yield move

    def move(self, move):
        """Apply the given move to the current board and return the resulting board"""
        start = move.start
        end = move.end
        assert end not in self.white_pieces and end not in self.black_pieces
        if start in self.white_pieces:
            new_white_pieces = self.white_pieces - set((start,)) | set((end,))
            new_black_pieces = self.black_pieces
        elif start in self.black_pieces:
            new_white_pieces = self.white_pieces
            new_black_pieces = self.black_pieces - set((start,)) | set((end,))
        else:
            raise Exception("No such piece " + start)
        return Board(new_white_pieces, new_black_pieces, self.size, self.white_win, self.black_win)

    def generate_boards(self, white):
        """Return all the boards one move away from this board"""
        for move in self.generate_all_moves(white):
            yield self.move(move)

    def __str__(self):
        """Return a printable representation of this board"""
        str = ""
        for r in range(self.size):
            str = str + " " * r
            for q in range(self.size):
                if Hex(q, r) in self.white_pieces:
                    pos = self.WHITE
                elif Hex(q, r) in self.black_pieces:
                    pos = self.BLACK
                else:
                    pos = self.EMPTY
                str = str + pos + " "
            str = str + "\n"
        return str
