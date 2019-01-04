# Chinese Checkers

* A game of two, three, four or six players. Here we look at the two-player game only.
* The board is a _n_ x _n_ hexagonal grid (for two players). We choose _n_ = 7 to keep things tractable, although it is normally 9.
* Each player's pieces are arranged in a triangle (of 6 pieces for _n_ = 7) at opposite ends of the board.
* The winner is the first player to move all their pieces to the opposite end of the board (i.e. where the other player's pieces started).
* A move consists of a single piece moving either one position in any direction, or a series of jumps over other pieces.
Each jump is over an immediately adjacent single piece (of any colour) to an empty position beyond.

## Random play

In many games the number of moves in the game is inherently limited, and while draws
can be more likely than not, wins are not vanishingly small. For example,
tic-tac-toe and othello are limited by the number of squares on the board. Chess has
rules that limit the number of moves in the game.

In Chinese checkers, a game between two players that choose moves at random will
never end (and it would result in a draw if there was a rule that limited the number of
moves in a game).

This is because there are _49 choose 6_ ways of arranging the pieces of one player
(white, say) on the board, and only one of them is a winning position. So the chance
of a game ending with random play is about 1 in 14 million.

Contrast this to chess, where in random play one player is likely to win over
[15% of the time](http://wismuth.com/chess/random-games.html). I was surprised the win
rate was this high.

A reasonable way of implementing random play in Chinese checkers therefore is to
favour moves that move in the forward direction (i.e. towards the end of the board
for that player). If this is done then most games end in a win. This is important
for training agents to play the game, where having some wins crop up by chance is
important for them to learn.

## Greedy play

A very simple strategy is to choose the move that minimizes the sum of
the distances of the player's pieces to the target position. This
is actually a pretty good strategy, however, it doesn't do any look ahead, so it can suffer
from not keeping pieces together. (Allowing pieces to jump over each other is a good idea
since it allows them to move to the target area faster.)

In practice, Greedy will always beat Random.

## Usage

Install Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```