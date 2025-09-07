from __future__ import annotations

from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board


class Piece:
    """
    This is the base class for all pieces.

    A piece will have a name as "pawn", a position in the board as (0, 4)
    a color as "w" for white and "b" for black and the symbol as a unicode character.

    Attributes
    ----------
    name    : str
        Name of the piece ("pawn")
    pos     : Tuple[int, int]
        Current position of the piece on the board (1, 2)
    color   : str
        Color of the piece ("w")
    symbol  : str
        Unicode symbol of the piece "\u2654"
    """

    def __init__(
        self, name: str, pos: Tuple[int, int], color: str, symbol: str
    ) -> None:
        """
        Initialize a Piece instance.

        Parameters
        ----------
        name    : str
            Name of the piece ("pawn").
        pos     : Tuple[int, int]
            Current position of the piece on the board (1, 2).
        color   : str
            Color of the piece ("w").
        symbol  : str
            Unicode symbol of the piece "\u2654".
        """

        self.name: str = name
        self.pos: Tuple[int, int] = pos
        self.color: str = color
        self.symbol: str = symbol

        self.move_factory = MoveFactory()

    def __str__(self) -> str:
        """
        Method to describe a piece in human-readable form.

        Returns
        -------
        str
            String representation of the piece.
        """
        return f"Piece {self.name} in team {self.color} with pos {self.pos}"

    def move(self, board: Board, move: "Move") -> None:
        """
        Method to execute a Move in a Board object.

        Parameters
        ----------
        board   : Board
            Board object to which the Move will be executed.
        move    : Move
            Move object to be executed.

        Returns
        -------
        None
        """
        end_pos = move.end_pos

        assert 0 <= end_pos[0] < 8, f"Wrong move provided {self} to {end_pos}"
        assert 0 <= end_pos[1] < 8, f"Wrong move provided {self} to {end_pos}"

        # Starting Tuple[int, int] set to empty
        x_st, y_st = self.pos
        board.board[x_st][y_st] = "\u2022"

        # Check if the resulting Tuple[int, int] is occupied by another piece
        # Set the other piece to empty
        unknown_piece: Optional[Piece] = board.find_by_pos(end_pos)
        if unknown_piece:
            if unknown_piece.name == "king":
                board.game_over = True

            board.captured_pieces.append(unknown_piece)
            board.pieces.remove(unknown_piece)

            x, y = end_pos
            self.pos = (x, y)
        else:
            x, y = end_pos
            self.pos = (x, y)

    # def can_move(self, pos: Tuple[int, int], state: List[Tuple[int, int]]) -> bool:
    #     """
    #     Method to check if a piece can be moved to the given position by the current board state.
    #     By "can move" we check whether the desired position is held by another piece or not.

    #     Parameters
    #     ----------
    #     pos     : Tuple[int, int]
    #         A tuple of int describing the position we want to move the piece to.
    #     state   : List[Tuple[int, int]]
    #         A list of tuples holding the positions of all the pieces on the board.

    #     Returns
    #     -------
    #     bool
    #         True if the piece can be moved to the given position.
    #     """
    #     can_move = False
    #     if pos not in state:
    #         self.available_moves.append(pos)
    #         can_move = True

    #     return can_move

    def _check_position_bounds(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Method to validate a Piece's position and ensure that it's inside the 8x8 grid.
        The difference with the `can_move` method is that this will check only if the
        desired position is inside the 8x8 grid whereas `can_move` checks if the desired
        position is held by another piece.

        Parameters
        ----------
        pos     : Tuple[int, int]
            The position we are interested in.

        Returns
        -------
        Optional[Tuple[int, int]]
            If desired position is inside the 8x8 grid, then we return the position
            else we return None.

        """
        in_bounds = pos
        if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
            in_bounds = None

        return in_bounds

    def calculate_moves(self, board) -> List["Move"]:
        """
        Method to calculate all possible moves for a piece.

        Parameters
        ----------
        board   : Board
            A Board object.

        Returns
        -------
        List[Tuple[int, int]]
            A list of all possible moves for a given piece.
        """
        self.available_moves: List[Move] = []
        curr_player = self.color

        match self.name:
            case "king":
                start_pos = self.pos
                # directions=[forward, backward, left, right, forward diagonal right, forward diagonal left, backward diagonal right, backward diagonal left]
                directions = [
                    (1, 0),
                    (-1, 0),
                    (0, -1),
                    (0, 1),
                    (1, 1),
                    (1, -1),
                    (-1, 1),
                    (-1, -1),
                ]
                for dir in directions:
                    end_pos = self._check_position_bounds(
                        (start_pos[0] + dir[0], start_pos[1] + dir[1])
                    )

                    if not end_pos:
                        continue

                    unknown_piece = board.find_by_pos(end_pos)
                    # There are 3 states a board cell can be in.
                    # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                    if end_pos and unknown_piece and self.color != unknown_piece.color:
                        # Cell is occupied by enemy team, capture is registered as a valid move
                        self.available_moves.append(
                            self.move_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=10000.0,
                                is_capture=True,
                                captured_piece=unknown_piece,
                            )
                        )

                    elif not unknown_piece:
                        # Cell is unoccupied, move
                        self.available_moves.append(
                            self.move_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=1000.0,
                                is_capture=False,
                                captured_piece=None,
                            )
                        )
                    if end_pos and unknown_piece and self.color == unknown_piece.color:
                        # Cell occupied by same team, check next move
                        continue

            case "queen":
                start_pos = self.pos

                # directions=[forward, backward, left, right, left_forward, right_forward, left_backward, right_backward]
                directions = [
                    (1, 0),
                    (-1, 0),
                    (0, -1),
                    (0, 1),
                    (1, -1),
                    (1, 1),
                    (-1, -1),
                    (-1, 1),
                ]
                for dir in directions:
                    for i in range(8):
                        end_pos = self._check_position_bounds(
                            (start_pos[0] + i * dir[0], start_pos[1] + i * dir[1])
                        )

                        if not end_pos:
                            continue

                        unknown_piece = board.find_by_pos(end_pos)
                        # There are 3 states a board cell can be in.
                        # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                        if (
                            end_pos
                            and unknown_piece
                            and self.color != unknown_piece.color
                        ):
                            # Cell is occupied by enemy team, capture is registered as a valid move
                            self.available_moves.append(
                                self.move_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=600.0,
                                    is_capture=True,
                                    captured_piece=unknown_piece,
                                )
                            )
                            break

                        elif not unknown_piece:
                            # Cell is unoccupied, move
                            self.available_moves.append(
                                self.move_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=300.0,
                                    is_capture=False,
                                    captured_piece=None,
                                )
                            )
                        if (
                            end_pos
                            and unknown_piece
                            and self.color == unknown_piece.color
                        ):
                            # Cell occupied by same team, check next move
                            break

            case "rook":
                start_pos = self.pos

                # directions=[forward, backward, left, right]
                directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]
                for dir in directions:
                    for i in range(8):
                        end_pos = self._check_position_bounds(
                            (start_pos[0] + i * dir[0], start_pos[1] + i * dir[1])
                        )

                        if not end_pos:
                            continue

                        unknown_piece = board.find_by_pos(end_pos)
                        # There are 3 states a board cell can be in.
                        # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                        if (
                            end_pos
                            and unknown_piece
                            and self.color != unknown_piece.color
                        ):
                            # Cell is occupied by enemy team, capture is registered as a valid move
                            self.available_moves.append(
                                self.move_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=200.0,
                                    is_capture=True,
                                    captured_piece=unknown_piece,
                                )
                            )
                            break

                        elif not unknown_piece:
                            # Cell is unoccupied, move
                            self.available_moves.append(
                                self.move_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=100.0,
                                    is_capture=False,
                                    captured_piece=None,
                                )
                            )

                        if (
                            end_pos
                            and unknown_piece
                            and self.color == unknown_piece.color
                        ):
                            # Cell occupied by same team, check next move
                            break

            case "bishop":
                start_pos = self.pos

                # directions=[left_forward, right_forward, left_backward, right_backward]
                directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
                for dir in directions:
                    for i in range(8):
                        end_pos = self._check_position_bounds(
                            (start_pos[0] + i * dir[0], start_pos[1] + i * dir[1])
                        )

                        if not end_pos:
                            continue

                        unknown_piece = board.find_by_pos(end_pos)
                        # There are 3 states a board cell can be in.
                        # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                        if (
                            end_pos
                            and unknown_piece
                            and self.color != unknown_piece.color
                        ):
                            # Cell is occupied by enemy team, capture is registered as a valid move
                            self.available_moves.append(
                                self.move_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=100.0,
                                    is_capture=True,
                                    captured_piece=unknown_piece,
                                )
                            )
                            break

                        elif not unknown_piece:
                            # Cell is unoccupied, move
                            self.available_moves.append(
                                self.move_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=50.0,
                                    is_capture=False,
                                    captured_piece=None,
                                )
                            )

                        if (
                            end_pos
                            and unknown_piece
                            and self.color == unknown_piece.color
                        ):
                            # Cell occupied by same team, check next move
                            break

            case "knight":
                start_pos = self.pos

                directions = [
                    (1, 2),
                    (1, -2),
                    (-1, 2),
                    (-1, -2),
                    (2, 1),
                    (2, -1),
                    (-2, 1),
                    (-2, -1),
                ]
                for dir in directions:
                    end_pos = self._check_position_bounds(
                        (start_pos[0] + dir[0], start_pos[1] + dir[1])
                    )

                    if not end_pos:
                        continue

                    unknown_piece = board.find_by_pos(end_pos)
                    # There are 3 states a board cell can be in.
                    # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                    if end_pos and unknown_piece and self.color != unknown_piece.color:
                        # Cell is occupied by enemy team, capture is registered as a valid move
                        self.available_moves.append(
                            self.move_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=100.0,
                                is_capture=True,
                                captured_piece=unknown_piece,
                            )
                        )

                    elif not unknown_piece:
                        # Cell is unoccupied, move
                        self.available_moves.append(
                            self.move_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=0.0,
                                is_capture=False,
                                captured_piece=None,
                            )
                        )

                    if end_pos and unknown_piece and self.color == unknown_piece.color:
                        # Cell occupied by same team, check next move
                        continue

            case "pawn":
                start_pos = self.pos
                home_pos = 2 if start_pos[0] == 1 or start_pos[0] == 6 else 1
                pawn_dir = 1 if curr_player == "w" else -1

                # directions=[forward, forward_right, forward_left]
                directions = [(pawn_dir * home_pos, 0), (pawn_dir, 1), (pawn_dir, -1)]
                for dir in directions:
                    end_pos = self._check_position_bounds(
                        (start_pos[0] + dir[0], start_pos[1] + dir[1])
                    )

                    if not end_pos:
                        continue

                    # REMINDME: Put condition for reaching final rank and promoting

                    unknown_piece = board.find_by_pos(end_pos)
                    # There are 3 states a board cell can be in.
                    # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                    if (
                        end_pos
                        and unknown_piece
                        and self.color != unknown_piece.color
                        and dir != (pawn_dir * home_pos, 0)
                    ):
                        # Cell is occupied by enemy team, capture is registered as a valid move
                        self.available_moves.append(
                            self.move_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=20.0,
                                is_capture=True,
                                captured_piece=unknown_piece,
                            )
                        )

                    elif not unknown_piece and dir == (pawn_dir * home_pos, 0):
                        # Since the first move examined is the +2 forward
                        # We need to also examing the +1 forward if there is any pawn and not hover above it
                        inter_piece = board.find_by_pos(
                            (end_pos[0] - pawn_dir, end_pos[1])
                        )
                        if inter_piece:
                            break
                        else:
                            # Cell is unoccupied, move
                            self.available_moves.append(
                                self.move_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=0.0,
                                    is_capture=False,
                                    captured_piece=None,
                                )
                            )
                        if home_pos == 2:
                            # FIXME:
                            if not inter_piece:
                                self.available_moves.append(
                                    self.move_factory(
                                        piece=self,
                                        start_pos=start_pos,
                                        end_pos=(end_pos[0] - pawn_dir, end_pos[1]),
                                        score=0.0,
                                        is_capture=False,
                                        captured_piece=None,
                                    )
                                )

                    if end_pos and unknown_piece and self.color == unknown_piece.color:
                        # Cell occupied by same team, check next move
                        break

        return list(set(self.available_moves))


class PieceFactory:
    """
    Factory class for creating Piece objects.

    """

    def __call__(
        self, name: str, pos: Tuple[int, int], color: str, symbol: str
    ) -> Piece:
        """
        Valid way to generate a Piece object.

        Parameters
        ----------
        name    : str
            Name of the piece ("pawn")
        pos     : Tuple[int, int]
            Current position of the piece on the board (1, 2)
        color   : str
            Color of the piece ("w")
        symbol  : str
            Unicode symbol of the piece "\u2654"

        Returns
        -------
        Piece
            A Piece object.
        """
        self.piece = Piece(name=name, pos=pos, color=color, symbol=symbol)

        assert 0 <= pos[0] < 8, f"Piece position for x axis is out of bounds"
        assert 0 <= pos[1] < 8, f"Piece position for y axis is out of bounds"

        return self.piece


class Move:
    """
    Move base class.

    piece : Piece
        The piece making the move.
    start_pos : Tuple[int, int]
        Starting position of the move.
    end_pos : Tuple[int, int]
        Ending position of the move.
    score : float
        Heuristic score associated with the move.
    is_capture : bool
        Whether the move captures an opponent's piece.
    captured_piece : Piece, optional
        The captured piece, if any.
    """

    def __init__(
        self,
        piece: Piece,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        score: float,
        is_capture: bool,
        captured_piece: Optional[Piece] = None,
    ):

        self.piece = piece
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.score = score
        self.is_capture = is_capture
        self.captured_piece = captured_piece

    def __lt__(self, other: "Move"):
        """
        Compare Moves based on their score.

        Parameters
        ----------
        other   : Move

        Returns
        -------

        """

        return self.score < other.score

    def __str__(self):
        """
        Method to represent a Move in human-readable form.

        Returns
        -------
        str
        """
        p_name = self.piece.name[0]
        p_team = self.piece.color
        s_pos = "".join([str(x) for x in self.start_pos])
        e_pos = "".join([str(x) for x in self.end_pos])
        i_capt = "T" if self.is_capture else "F"
        p_capt = "w" if self.piece.color == "b" else "b"

        return "".join([p_name, p_team, s_pos, e_pos, i_capt, p_capt])


class MoveFactory:
    """
    Factory class for creating Move objects.

    """

    def __call__(
        self,
        piece: Piece,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        score: float,
        is_capture: bool,
        captured_piece: Optional[Piece] = None,
    ):
        """
        piece : Piece
            The piece making the move.
        start_pos : Tuple[int, int]
            Starting position of the move.
        end_pos : Tuple[int, int]
            Ending position of the move.
        score : float
            Heuristic score associated with the move.
        is_capture : bool
            Whether the move captures an opponent's piece.
        captured_piece : Piece, optional
            The captured piece, if any.

        Returns
        -------
        Move
            A Move object.
        """
        self.move = Move(
            piece=piece,
            start_pos=start_pos,
            end_pos=end_pos,
            score=score,
            is_capture=is_capture,
            captured_piece=captured_piece,
        )

        assert 0 <= start_pos[0] < 8, f"Piece position for x axis is out of bounds"
        assert 0 <= start_pos[1] < 8, f"Piece position for y axis is out of bounds"

        assert 0 <= end_pos[0] < 8, f"Piece position for x axis is out of bounds"
        assert 0 <= end_pos[1] < 8, f"Piece position for y axis is out of bounds"

        return self.move
