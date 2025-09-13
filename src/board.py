import copy
import streamlit as st

from typing import List, Tuple, Optional
from piece import Piece, PieceFactory


class Board:
    """
    A class representing an 8x8 chess board.

    The board tracks all pieces, captured pieces, and game state. It also
    provides methods for visualization, querying, evaluation, and cloning.

    Attributes
    ----------
    st_status_placeholder :
        Streamlit placeholder for status information.
    st_board_placeholder :
        Streamlit placeholder for the rendered chessboard.
    pawn_factory : PieceFactory
        Factory for creating `Piece` objects.
    pieces : List[Piece]
        Active pieces on the board.
    captured_pieces: List[Piece]
        Captured pieces in a board state.
    game_over : bool
        Flag indicating if the game is over.
    transposition_table : dict
        FIXME: Cache for storing evaluated board states.
    board : List[List[str]]
        8x8 grid representing the chessboard state using piece symbols.
    """

    def __init__(self, max_player: str):
        """
        Initialize a Board object.

        Parameters
        ----------
        max_player: str
            The team the maximizing player is in mainly for scoring the board.
        """
        self.max_player = max_player
        self.captured_pieces: List[Piece] = []

        self.__acc_names = ["king", "queen", "rook", "bishop", "knight", "pawn"]
        self.__acc_colors = ["b", "w"]

        white_pieces = {
            "king": "\u2654",
            "queen": "\u2655",
            "rook": "\u2656",
            "bishop": "\u2657",
            "knight": "\u2658",
            "pawn": "\u2659",
        }

        black_pieces = {
            "king": "\u265a",
            "queen": "\u265b",
            "rook": "\u265c",
            "bishop": "\u265d",
            "knight": "\u265e",
            "pawn": "\u265f",
        }

        self.st_status_placeholder = st.empty()
        self.st_board_placeholder = st.empty()

        self.pawn_factory: PieceFactory = PieceFactory()
        self.pieces: List[Piece] = []

        self.game_over: bool = False

        # Hardcoded positions for all pieces.
        king_positions = [(0, 3), (7, 4)]
        queen_positions = [(0, 4), (7, 3)]
        rook_positions = [(0, 0), (0, 7), (7, 0), (7, 7)]
        bishop_positions = [(0, 2), (0, 5), (7, 2), (7, 5)]
        knight_positions = [(0, 1), (0, 6), (7, 1), (7, 6)]
        pawn_positions = [(i, j) for i in [1, 6] for j in range(8)]

        pieces_positions: List[List[Tuple[int, int]]] = [
            king_positions,
            queen_positions,
            rook_positions,
            bishop_positions,
            knight_positions,
            pawn_positions,
        ]

        # A dict holding information of the position of all pieces like
        # "king": [(0, 3), (7, 4)] we don't need to seperate any piece yet
        # into teams
        __pieces_pos_map = {
            p_name: p_pos for p_name, p_pos in zip(self.__acc_names, pieces_positions)
        }

        self.board = [["\u2022" for _ in range(8)] for _ in range(8)]

        # Generate pieces
        for p_name, p_pos in list(__pieces_pos_map.items()):
            # For all pieces on the board
            for p_idx, piece_pos in enumerate(p_pos):
                if p_idx < len(p_pos) // 2:
                    # Generate the first 16 pieces as whites
                    self.pieces.append(
                        self.pawn_factory(
                            name=p_name,
                            pos=piece_pos,
                            color="w",
                            symbol=white_pieces[p_name],
                        )
                    )
                else:
                    # And the rest as black
                    self.pieces.append(
                        self.pawn_factory(
                            name=p_name,
                            pos=piece_pos,
                            color="b",
                            symbol=black_pieces[p_name],
                        )
                    )

        # Assign each piece to the board
        for piece in self.pieces:
            x, y = piece.pos

            # FIXME: redundant syntax
            # normally `_check_position_bounds` with a desired move to investigate, not the piece's position
            if piece._check_position_bounds((x, y)):
                self.board[x][y] = piece.symbol

    def has_king(self, player: str) -> bool:
        """
        Method to check if the specific player has a king in the board.
        In chess, you can't capture a king, we allow it here for convenience.

        Parameters
        ----------
        player: str
            The team the player is in.

        Returns
        -------
        bool
        """
        assert player in self.__acc_colors, f"Incorrect player, you provided {player}"

        king = [
            piece
            for piece in self.pieces
            if piece.name == "king" and piece.color == player
        ]

        if len(king) == 1:  # Assuming there is only 1 king per player
            return True
        else:
            return False

    def show(
        self,
        player: Optional[str] = None,
        score: Optional[float] = None,
        time: Optional[float] = None,
    ):
        """
        Method to visualize the board and all it's pieces at any given point.

        Parameters
        ----------
        player  : str
            The team the player is in.

        score   : float
            The current score of the board.
        time    : float
            Time of search.

        Returns
        -------
        None
        """

        # Assign each piece to the board
        for piece in self.pieces:
            x, y = piece.pos

            # FIXME: redundant syntax
            # normally `_check_position_bounds` with a desired move to investigate, not the piece's position
            if piece._check_position_bounds((x, y)):
                self.board[x][y] = piece.symbol

        # How many white pieces are currently on the board?
        white_pieces = len(
            [
                piece
                for piece in self.pieces
                if piece.color == "w" and piece.symbol != "\u2022"
            ]
        )

        # How many black pieces are currently on the board?
        black_pieces = len(
            [
                piece
                for piece in self.pieces
                if piece.color == "b" and piece.symbol != "\u2022"
            ]
        )

        # A placeholder for streamlit to update the text in the same are on the page
        # and not append the next text info after the previous one.
        self.st_status_placeholder.markdown(
            f" \u2659 {white_pieces} | \u265f {black_pieces} | Player {player} | Score {score} | Time elapsed {time}"
        )
        # chatGPT:
        html = "<table style='font-size:24px; font-family:Arial; border-collapse: collapse;'>"
        for row in self.board:
            html += "<tr>"
            for cell in row:
                html += f"<td style='width:30px; height:30px; text-align:center;'>{cell}</td>"
            html += "</tr>"
        html += "</table>"

        # A streamlit placeholder for the board.
        self.st_board_placeholder.markdown(html, unsafe_allow_html=True)

    def find_by_pos(self, pos: Tuple[int, int]) -> Optional[Piece]:
        """
        Method for finding a Piece object in the board by it's position.

        Iterate through all of board pieces and match their position with the given position.
        Checking for the team of the piece is unnecessary since we choose by position on the board.

        Parameters
        ----------
        pos     : Tuple[int]
            The posiiton we wish to investigate in the board.
        Returns
        -------
        Union[bool, Piece]
            The piece found or False.
        """

        found_piece = None
        for piece in self.pieces:
            if piece.pos == pos:
                return piece

        return None

    def get_pieces_for_player(self, player: str) -> List[Piece]:
        """
        Method to return all the pieces a player currently has on the board.

        Parameters
        ----------
        player  : str
            The team the player is in.

        Returns
        -------
        List[Piece]
            A list of all the pieces a player has.
        """
        return [piece for piece in self.pieces if piece.color == player]

    def count_pieces(self, player: str) -> int:
        """
        Method to count the number of pieces that a player has.

        Parameters
        ----------
        player    : str
            The team the player is in.

        Returns
        -------
        int
            The number of pieces for the given player.
        """

        return len(self.get_pieces_for_player(player))

    def score_board(self, player: str) -> float:
        """
        Method to evaluate the current state of the board.
        Each piece is given a weight value. The current implementation
        sums all the pieces values each player posses and also the
        number of all possible moves for each player.

        Parameters
        ----------
        player  : str
            The maximizing player.
        Returns
        -------
        float
            The actual score minimax sees.
        """
        assert (
            player in self.__acc_colors
        ), f"Valid players are 'w' and 'b', you provided {player}"

        PIECE_VALUES = {
            "king": 1000,
            "queen": 9,
            "rook": 5,
            "bishop": 3,
            "knight": 3,
            "pawn": 1,
        }
        player_score: int = 0
        opponent_score: int = 0
        player_valid_moves: int = 0
        opponent_valid_moves: int = 0

        for piece in self.pieces:
            value: float = PIECE_VALUES.get(piece.name, 0)

            if piece.color == self.max_player:
                player_score += value
                player_valid_moves += len(piece.calculate_moves(self))
            else:
                opponent_score += value
                opponent_valid_moves += len(piece.calculate_moves(self))

        # The neutral point is 0.0 which is the starting score.
        # If player_score > opponent_score we have a positive score and a negative likewise.
        # The same applies for the valid_moves
        return (player_score - opponent_score) + (
            player_valid_moves - opponent_valid_moves
        )

    def clone(self) -> "Board":
        """
        Method to clone the board.

        Returns
        -------
        Board
            A deepcopy of the current board.
        """

        return copy.deepcopy(self)
