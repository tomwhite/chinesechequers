import random

from chinesechequers import *
from play import *


def test_hex():
    h1 = Hex(1, 2)
    h2 = Hex(1, 2)
    assert h1 is h2

def test_neighbor_pairs():
    assert Hex(2, 2).neighbor_pairs() == [
        (Hex(1, 2), Hex(0, 2)),
        (Hex(1, 3), Hex(0, 4)),
        (Hex(2, 1), Hex(2, 0)),
        (Hex(2, 3), Hex(2, 4)),
        (Hex(3, 1), Hex(4, 0)),
        (Hex(3, 2), Hex(4, 2))
    ]


def test_board_str():
    assert str(Board.start(7)).strip() == """
○ ○ ○ · · · · 
 ○ ○ · · · · · 
  ○ · · · · · · 
   · · · · · · · 
    · · · · · · ● 
     · · · · · ● ● 
      · · · · ● ● ● 
""".strip()


def test_on_board():
    board = Board.start(7)
    assert board.on_board(Hex(0, 0))
    assert board.on_board(Hex(0, 1))
    assert board.on_board(Hex(6, 6))
    assert not board.on_board(Hex(-1, 0))
    assert not board.on_board(Hex(7, 0))
    assert not board.on_board(Hex(400, 10))


def test_piece_at():
    board = Board.start(7)
    assert board.piece_at(Hex(0, 0))
    assert board.piece_at(Hex(1, 0))
    assert board.piece_at(Hex(6, 6))
    assert board.piece_at(Hex(6, 5))
    assert not board.piece_at(Hex(0, 4))
    assert not board.piece_at(Hex(-1, 0))
    assert not board.piece_at(Hex(4, 0))
    assert not board.piece_at(Hex(400, 10))


def test_generate_moves():
    board = Board.start(7)
    # corner piece can't move
    assert len(list(board.generate_moves(Hex(0, 0)))) == 0
    # piece on leading edge can move in two directions
    assert [m.end for m in board.generate_moves(Hex(0, 2))] == [Hex(0, 3), Hex(1, 2)]
    # piece on second diagonal can jump in two directions
    assert [m.end for m in board.generate_moves(Hex(0, 1))] == [Hex(0, 3), Hex(2, 1)]


def test_generate_moves_double_jump():
    # test case where there are multiple, branching jumps
    board = Board.start(7).move(Move(Hex(2, 0), Hex(3, 0))).move(Move(Hex(1, 1), Hex(2, 1)))
    assert [m.end for m in board.generate_moves(Hex(0, 0))] == [Hex(2, 0), Hex(2, 2), Hex(4, 0)]


def test_generate_boards():
    board = Board.start(7)
    assert len(list(board.generate_boards(white=True))) == 10


def test_winning_position():
    board = Board.start(7)
    assert not board.white_has_won()
    assert not board.black_has_won()
    board = Board(board.black_pieces, board.white_pieces, board.size, board.white_win, board.black_win)
    assert board.white_has_won()
    assert board.black_has_won()


def test_random_vs_greedy():
    random.seed(42)
    player1 = Random(white=True)
    player2 = Greedy(white=False)
    player1_wins, player2_wins, draws, shortest_game = play_series(player1, player2, games=10)
    assert player1_wins == 0
    assert player2_wins == 9
    assert draws == 1
    assert shortest_game == 24


def test_minimax_vs_greedy():
    player1 = Minimax(white=True)
    player2 = Greedy(white=False)
    player1_wins, player2_wins, draws, shortest_game = play_series(player1, player2, games=1)
    assert player1_wins == 1
    assert player2_wins == 0
    assert draws == 0
    assert shortest_game == 24


def test_greedy_vs_minimax():
    player1 = Greedy(white=True)
    player2 = Minimax(white=False)
    player1_wins, player2_wins, draws, shortest_game = play_series(player1, player2, games=1)
    assert player1_wins == 0
    assert player2_wins == 1
    assert draws == 0
    assert shortest_game == 23


def test_alphabeta_vs_greedy():
    player1 = AlphaBeta(white=True)
    player2 = Greedy(white=False)
    player1_wins, player2_wins, draws, shortest_game = play_series(player1, player2, games=1)
    assert player1_wins == 1
    assert player2_wins == 0
    assert draws == 0
    assert shortest_game == 24


def test_greedy_vs_alphabeta():
    player1 = Greedy(white=True)
    player2 = AlphaBeta(white=False)
    player1_wins, player2_wins, draws, shortest_game = play_series(player1, player2, games=1)
    assert player1_wins == 0
    assert player2_wins == 1
    assert draws == 0
    assert shortest_game == 23
