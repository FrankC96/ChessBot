import time
from itertools import cycle

from board import Board
from bot import minimax

if __name__ == "__main__":
    board = Board("w")  # the maximizing player

    PLAYERS = cycle(["w", "b"])

    for _ in range(200):
        curr_player = next(PLAYERS)

        start_time = time.time()
        score, piece, move = minimax(board, 3, curr_player)
        end_time = time.time()

        if piece:
            piece.move(board, move)
        else:
            print(f"Player {curr_player} lost!")
            break
        board.show(curr_player, score, end_time - start_time)
