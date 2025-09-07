import unittest

from src.piece import *
from src.board import *


class TestObjectCreation(unittest.TestCase):

    def test_create_piece(self):
        # Piece creation
        piece = Piece("king", (0, 4), "w", "\u2654")
        self.assertIsInstance(piece, Piece, msg="This is not a piece")

    def test_create_factory(self):
        # Piece factory creation
        piece_fac = PieceFactory()
        self.assertIsInstance(piece_fac, PieceFactory)

    def test_piece_position_bnds(self):
        piece_factory = PieceFactory()
        # Edge case for the x position of the piece to be < 0
        with self.assertRaises(AssertionError):
            piece_factory("pawn", (-1, 0), "w", "\u2654")
        # Edge case for the x position of the piece to be > 8
        with self.assertRaises(AssertionError):
            piece_factory("pawn", (10, 0), "w", "\u2654")
        # Edge case for the y position of the piece to be < 0
        with self.assertRaises(AssertionError):
            piece_factory("pawn", (0, -1), "w", "\u2654")
        # Edge case for the y position of the piece to be > 8
        with self.assertRaises(AssertionError):
            piece_factory("pawn", (0, 10), "w", "\u2654")

    def test_piece_move(self):
        piece_factory = PieceFactory()
        move_factory = MoveFactory()

        # Assuming the correct position of a white knight,
        # so we also need to generate a board object
        piece = piece_factory("knight", (0, 1), "w", "\u2654")
        board = Board("w")

        # Trying to move outside the board, generate the move
        with self.assertRaises(AssertionError):
            move = move_factory(piece, (0, 1), (-1, 1), -float("inf"), False, None)
            piece.move(board, move)  # FIXME: This is not tested
            # How can we test a faulty Move for the move method
            # if it we cannot even generate this?


if __name__ == "__main__":
    unittest.main()
