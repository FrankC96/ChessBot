from math import inf


def minimax(
    board,
    depth,
    player,
    total_explored_states: int = 0,
    a=-float("inf"),
    b=float("inf"),
    writer=None,
):
    """
    A simple implementation of the minimax function with alpha-beta pruning.
    """
    total_explored_states += 1

    if writer is None:
        writer = open("./board_states.txt", "w", encoding="utf-8")
        close_writer = True
    else:
        close_writer = False

    if depth == 0 or board.game_over:
        if board.game_over:
            if board.winner == board.human_player:
                score = float(-inf)
            elif board.winner == board.bot_player:
                score = float(inf)
        else:
            score = board.score_board(player)

        if close_writer:
            writer.close()

        return score, None, None, total_explored_states

    if player == board.bot_player:
        max_score = float(-inf)
        best_piece = None
        best_move = None
        for piece in board.get_pieces_for_player(player):
            moves = piece.calculate_moves(board)
            sorted_moves = sorted(moves, key=lambda x: x.score, reverse=True)
            for move in sorted_moves:
                new_board = board.clone()

                x_start, y_start = piece.ind_pos
                x_end, y_end = move.end_pos

                print(
                    f"{total_explored_states}\t[{max_score}]\t->\t",
                    f"Exploring {new_board.blocks[x_start][y_start].piece} move from {move.start_pos} to {move.end_pos}",
                )

                new_board.move(
                    [new_board.blocks[x_start][y_start], new_board.blocks[x_end][y_end]]
                )
                writer.write(new_board.serialize(store=False) + "\n")

                score, _, _, total_explored_states = minimax(
                    new_board,
                    depth - 1,
                    new_board.current_player,
                    total_explored_states,
                    a,
                    b,
                    writer,
                )

                if score > max_score:
                    max_score = score
                    best_piece = piece
                    best_move = move

                a = max(a, max_score)
                if a >= b:
                    break

        return (max_score, best_piece, best_move, total_explored_states)
    else:
        min_score = float(inf)
        best_piece = None
        best_move = None
        for piece in board.get_pieces_for_player(player):
            moves = piece.calculate_moves(board)
            sorted_moves = sorted(moves, key=lambda x: x.score, reverse=True)
            for move in sorted_moves:
                new_board = board.clone()

                x_start, y_start = piece.ind_pos
                x_end, y_end = move.end_pos

                print(
                    f"{total_explored_states}\t[{min_score}]\t->\t",
                    f"Exploring {new_board.blocks[x_start][y_start].piece} move from {move.start_pos} to {move.end_pos}",
                )

                new_board.move(
                    [new_board.blocks[x_start][y_start], new_board.blocks[x_end][y_end]]
                )
                writer.write(new_board.serialize(store=False) + "\n")

                score, _, _, total_explored_states = minimax(
                    new_board,
                    depth - 1,
                    new_board.current_player,
                    total_explored_states,
                    a,
                    b,
                    writer,
                )

                if score < min_score:
                    min_score = score
                    best_piece = piece
                    best_move = move

                b = min(b, min_score)
                if b <= a:
                    break

        return (min_score, best_piece, best_move, total_explored_states)
