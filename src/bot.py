def minimax(board, depth, player, a=-float("inf"), b=float("inf")):
    """
    A simple implementation of the minimax function with alpha-beta pruning.
    """
    if depth == 0 or board.game_over:
        score = board.score_board(player)
        return score, None, None

    if player == "w":
        max_score = -float("inf")
        best_piece = None
        best_move = None
        for piece in board.get_pieces_for_player(player):
            moves = piece.calculate_moves(board)
            sorted_moves = sorted(moves, key=lambda x: x.score, reverse=True)
            for move in sorted_moves:
                new_board = board.clone()
                new_piece = new_board.find_by_pos(piece.ind_pos, return_piece=False)
                x, y = move.end_pos
                new_board.move([new_piece, board.blocks[x][y]])
                score, _, _ = minimax(new_board, depth - 1, "b", a, b)

                if score > max_score:
                    max_score = score
                    best_piece = piece
                    best_move = move

                a = max(a, max_score)
                if a >= b:
                    break

        return (max_score, best_piece, best_move)
    else:
        min_score = float("inf")
        best_piece = None
        best_move = None
        for piece in board.get_pieces_for_player(player):
            moves = piece.calculate_moves(board)
            sorted_moves = sorted(moves, key=lambda x: x.score, reverse=True)
            for move in sorted_moves:
                new_board = board.clone()
                new_piece = new_board.find_by_pos(piece.ind_pos, return_piece=False)
                x, y = move.end_pos
                new_board.move([new_piece, board.blocks[x][y]])
                score, _, _ = minimax(new_board, depth - 1, "w", a, b)

                if score < min_score:
                    min_score = score
                    best_piece = piece
                    best_move = move

                b = min(b, min_score)
                if b <= a:
                    break

        return (min_score, best_piece, best_move)
