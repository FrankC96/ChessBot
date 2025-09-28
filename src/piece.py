from __future__ import annotations
import copy
from pathlib import Path

from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board


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
        p_team = self.piece.team
        s_pos = "".join([str(x) for x in self.start_pos])
        e_pos = "".join([str(x) for x in self.end_pos])
        i_capt = "T" if self.is_capture else "F"
        p_capt = "w" if self.piece.team == "b" else "b"

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
        score: Optional[float] = None,
        is_capture: Optional[bool] = None,
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


class Piece:

    def __init__(self, name: str, ind_pos: Tuple[int, int], team: str):
        """
        This is a class only representing a Piece object.
        A piece object can be created with no restrictions,
        if created directly by calling Piece().

        Args:
            name (str): [king, queen, bishop, knight, rook, pawn]
            ind_pos (Tuple[int, int]): Any 2D position given by the user, with coordinates in an 8x8 board
            team (str): [w, b]
        """

        self.name = name
        self.ind_pos = ind_pos
        self.team = team

        self.img_path = Path(f"chess_symbols/{team}_{name}.svg")
        assert self.img_path.exists(), f"The provided image file is not found."

        self.m_factory = MoveFactory()

    def __repr__(self):
        return f"Piece {self.name} - {self.team} at position {self.ind_pos}"

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

        match self.name:
            case "king":
                start_pos = self.ind_pos
                # directions=[forward, backward, left, right, forward diagonal right, forward diagonal left, backward diagonal right, backward diagonal left]
                directions = [
                    (0, -1),
                    (0, 1),
                    (-1, 0),
                    (1, 0),
                    (1, 1),
                    (1, -1),
                    (1, 1),
                    (-1, -1),
                ]
                for dir in directions:
                    end_pos = self._check_position_bounds(
                        (start_pos[0] + dir[0], start_pos[1] + dir[1])
                    )

                    if not end_pos:
                        continue

                    unknown_piece = board.find_by_pos(end_pos, return_piece=True)

                    # There are 3 states a board cell can be in.
                    # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                    if end_pos and unknown_piece and self.team != unknown_piece.team:

                        # Cell is occupied by enemy team, capture is registered as a valid move
                        self.available_moves.append(
                            self.m_factory(
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
                            self.m_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=1000.0,
                                is_capture=False,
                                captured_piece=None,
                            )
                        )
                    if end_pos and unknown_piece and self.team == unknown_piece.team:
                        # Cell occupied by same team, check next move
                        continue

            case "queen":
                start_pos = self.ind_pos

                # directions=[forward, backward, left, right, left_forward, right_forward, left_backward, right_backward]
                directions = [
                    (0, 1),
                    (0, -1),
                    (-1, 0),
                    (1, 0),
                    (-1, -1),
                    (1, 1),
                    (-1, 1),
                    (1, -1),
                ]
                for dir in directions:
                    for i in range(1, 8):
                        end_pos = self._check_position_bounds(
                            (start_pos[0] + i * dir[0], start_pos[1] + i * dir[1])
                        )

                        if not end_pos:
                            continue

                        unknown_piece = board.find_by_pos(end_pos, return_piece=True)
                        # There are 3 states a board cell can be in.
                        # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                        if (
                            end_pos
                            and unknown_piece
                            and self.team != unknown_piece.team
                        ):
                            # Cell is occupied by enemy team, capture is registered as a valid move
                            self.available_moves.append(
                                self.m_factory(
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
                                self.m_factory(
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
                            and self.team == unknown_piece.team
                        ):
                            # Cell occupied by same team, check next move
                            break

            case "rook":
                start_pos = self.ind_pos

                # directions=[forward, backward, left, right]
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                for dir in directions:
                    for i in range(1, 8):
                        end_pos = self._check_position_bounds(
                            (start_pos[0] + i * dir[0], start_pos[1] + i * dir[1])
                        )

                        if not end_pos:
                            continue

                        unknown_piece = board.find_by_pos(end_pos, return_piece=True)
                        # There are 3 states a board cell can be in.
                        # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                        if (
                            end_pos
                            and unknown_piece
                            and self.team != unknown_piece.team
                        ):
                            # Cell is occupied by enemy team, capture is registered as a valid move
                            self.available_moves.append(
                                self.m_factory(
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
                                self.m_factory(
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
                            and self.team == unknown_piece.team
                        ):
                            # Cell occupied by same team, check next move
                            break

            case "bishop":
                start_pos = self.ind_pos

                # directions=[left_forward, right_forward, left_backward, right_backward]
                directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
                for dir in directions:
                    for i in range(1, 8):
                        end_pos = self._check_position_bounds(
                            (start_pos[0] + i * dir[0], start_pos[1] + i * dir[1])
                        )

                        if not end_pos:
                            continue

                        unknown_piece = board.find_by_pos(end_pos, return_piece=True)
                        # There are 3 states a board cell can be in.
                        # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                        if (
                            end_pos
                            and unknown_piece
                            and self.team != unknown_piece.team
                        ):
                            # Cell is occupied by enemy team, capture is registered as a valid move
                            self.available_moves.append(
                                self.m_factory(
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
                                self.m_factory(
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
                            and self.team == unknown_piece.team
                        ):
                            # Cell occupied by same team, check next move
                            break

            case "knight":
                start_pos = self.ind_pos

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

                    unknown_piece = board.find_by_pos(end_pos, return_piece=True)
                    # There are 3 states a board cell can be in.
                    # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                    if end_pos and unknown_piece and self.team != unknown_piece.team:
                        # Cell is occupied by enemy team, capture is registered as a valid move
                        self.available_moves.append(
                            self.m_factory(
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
                            self.m_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=0.0,
                                is_capture=False,
                                captured_piece=None,
                            )
                        )

                    if end_pos and unknown_piece and self.team == unknown_piece.team:
                        # Cell occupied by same team, check next move
                        continue

            case "pawn":
                start_pos = self.ind_pos

                home_pos = (
                    2
                    if (start_pos[1] == 1 and self.team == "w")
                    or (start_pos[1] == 6 and self.team == "b")
                    else 1
                )
                pawn_dir = 1 if self.team == "w" else -1

                # directions=[forward, forward_right, forward_left]
                directions = [(0, pawn_dir), (1, pawn_dir), (-1, pawn_dir)]
                if home_pos == 2:
                    directions.append((0, pawn_dir * 2))

                for dir in directions:
                    end_pos = self._check_position_bounds(
                        (start_pos[0] + dir[0], start_pos[1] + dir[1])
                    )

                    if not end_pos:
                        continue

                    # REMINDME: Put condition for reaching final rank and promoting
                    unknown_piece = board.find_by_pos(end_pos, return_piece=True)
                    # There are 3 states a board cell can be in.
                    # 1. empty  2. Occupied by same team    3. Occupied by enemy team
                    if (
                        end_pos
                        and unknown_piece
                        and self.team != unknown_piece.team
                        and (dir != (0, pawn_dir * 1) or dir != (0, pawn_dir * 2))
                    ):
                        # Cell is occupied by enemy team, capture is registered as a valid move
                        self.available_moves.append(
                            self.m_factory(
                                piece=self,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                score=20.0,
                                is_capture=True,
                                captured_piece=unknown_piece,
                            )
                        )

                    elif not unknown_piece and (
                        dir == (0, pawn_dir * 1) or dir == (0, pawn_dir * 2)
                    ):

                        inter_piece = board.find_by_pos(
                            (end_pos[0], end_pos[1] * pawn_dir), return_piece=True
                        )
                        if inter_piece:
                            if self.team == "w" and home_pos == 2:
                                print(
                                    f"Found piece {inter_piece.name} {inter_piece.team} at {inter_piece.ind_pos}"
                                )
                            # For the 2 step move originating from home,
                            # check if there is a piece 1 step ahead before moving.
                            continue
                        else:
                            # Cell is unoccupied, move
                            self.available_moves.append(
                                self.m_factory(
                                    piece=self,
                                    start_pos=start_pos,
                                    end_pos=end_pos,
                                    score=0.0,
                                    is_capture=False,
                                    captured_piece=None,
                                )
                            )

                    if end_pos and unknown_piece and self.team == unknown_piece.team:
                        # Cell occupied by same team, check next move
                        continue

        return list(set(self.available_moves))


class PieceFactory:
    def __init__(self, board_bounds: Tuple[int, int]):
        self.b_bounds = board_bounds
        self.pxl_offset = self.b_bounds[1] // 7

    def __call__(self, name: str, ind_pos: Tuple[int, int], team: str):
        true_pos = (ind_pos[0] * self.pxl_offset, ind_pos[1] * self.pxl_offset)

        assert (
            0 <= true_pos[0] <= self.b_bounds[1]
        ), f"Trying to place piece outside the max screen width {true_pos[0], self.b_bounds[1]}"
        assert (
            0 <= true_pos[1] <= self.b_bounds[0]
        ), f"Trying to place piece outside the max screen height {true_pos[1], self.b_bounds[0]}"
        return Piece(name, ind_pos, team)
