import copy
import pygame
from itertools import cycle
from collections import deque

from typing import Tuple, List, Dict, Optional, Union
from piece import Piece, PieceFactory, Move, MoveFactory


def flatten_list(list_: List):
    flattened_list = []
    for row in list_:
        flattened_list.extend(row)

    return flattened_list


class Block:

    def __init__(
        self,
        pos: Tuple[int, int],
        piece: Optional[str],
        color: Tuple[int, int],
        block_size: int,
        clicked: Optional[bool] = False,
        clicked_color: Optional[Tuple[int, int, int]] = (200, 0, 0),
    ):
        self.pos = pos
        self.piece = piece
        self.color = color
        self.block_size = block_size
        self.clicked = clicked
        self.clicked_color = clicked_color

        self.poss_move: Optional[bool] = None
        self.block_clicked: List[bool] = cycle([True, False])
        self.block_p_move: List[bool] = cycle([True, False])

        # Rect(left, top, width, height) -> Rect
        self.pg_rect = pygame.Rect(
            self.pos[0] * block_size // 2,
            self.pos[1] * block_size // 2,
            block_size // 2,
            block_size // 2,
        )

    def __repr__(self):
        return f"Block at {self.pos}, occupied {self.piece}"

    def select_block(self, board):
        poss_move_toggle: bool = False
        blocks = flatten_list(board.blocks)
        for block in blocks:
            if block.clicked:
                block.clicked = False

            if block.poss_move:
                poss_move_toggle = True
                block.poss_move = False

        if self.piece:
            print("I am in")
            av_moves = self.piece.calculate_moves(board)
            for mv in av_moves:
                x, y = mv.end_pos

                if poss_move_toggle:
                    pass
                else:
                    board.blocks[x][y].poss_move = True

            self.clicked = next(self.block_clicked)
        board.clicked_blocks.append(self)

    def draw(self, screen: pygame.Surface):
        # Draw the background color of the block
        if self.clicked:
            pygame.draw.rect(screen, self.clicked_color, self.pg_rect)
        else:
            pygame.draw.rect(screen, self.color, self.pg_rect)

        if self.poss_move:
            pygame.draw.rect(screen, (155, 204, 255), self.pg_rect)

        if self.piece:
            self.pg_img = pygame.image.load(self.piece.img_path)

            screen.blit(
                self.pg_img,
                (
                    self.pg_rect.center[0] - self.pg_img.get_width() // 2,
                    self.pg_rect.center[1] - self.pg_img.get_width() // 2,
                ),
            )


class BlockFactory:
    def __call__(
        self, pos: Tuple[int, int], piece: str, color: Tuple[int, int], block_size: int
    ):
        return Block(pos, piece, color, block_size)


class Board:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # Get screen widht, height borders
        self.s_width, self.s_height = self.screen.get_size()
        self.block_factory = BlockFactory()
        self.piece_factory = PieceFactory((self.s_width, self.s_height))
        self.move_factory = MoveFactory()

        # A buffer to track all clicked blocks in the board
        self.clicked_blocks = deque([], maxlen=2)
        self.block_to_exec_move: Optional[Block] = None

        # Hardcoded positions for all pieces.
        init_positions = {
            "king": [(0, 3), (7, 4)],
            "queen": [(0, 4), (7, 3)],
            "rook": [(0, 0), (0, 7), (7, 0), (7, 7)],
            "bishop": [(0, 2), (0, 5), (7, 2), (7, 5)],
            "knight": [(0, 1), (0, 6), (7, 1), (7, 6)],
            "pawn": [(i, j) for i in [1, 6] for j in range(8)],
        }

        # Create 64 Block objects
        self.blocks = []
        for i in range(8):
            row_blocks = []
            for j in range(8):
                block_color = (255, 255, 255) if (i + j) % 2 == 0 else (0, 100, 0)
                row_blocks.append(
                    self.block_factory(
                        pos=(i, j),
                        piece=None,
                        color=block_color,
                        block_size=self.s_width // 7,
                    )
                )
            self.blocks.append(row_blocks)

        # Create the board pieces
        self.pieces = []
        for name, pos in init_positions.items():
            i = 0
            for p in pos:
                x, y = p

                if i < len(pos) // 2:
                    temp_team = "w"
                else:
                    temp_team = "b"

                self.pieces.append(self.piece_factory(name, (y, x), temp_team))
                self.blocks[y][x].piece = self.pieces[-1]
                i += 1

    def find_by_pos(
        self, pos: Tuple[int, int], return_piece: Optional[bool] = None
    ) -> Optional[Piece]:
        """
        Method for finding a Piece object in the board by it's position.

        Iterate through all of board pieces and match their position with the given position.
        Checking for the team of the piece is unnecessary since we choose by position on the board.

        Parameters
        ----------
        pos     : Tuple[int]
            The posiiton we wish to investigate in the board.
        return_piece : bool
            A selector for returning the whole block or the piece on the requested block.

        Returns
        -------
        Union[bool, Piece]
            The piece found or False.
        """
        found_block: Optional[Block] = None
        blocks = flatten_list(self.blocks)

        for block in blocks:
            if block.pg_rect.collidepoint(pos):
                found_block = block

        if return_piece:
            for piece in self.pieces:
                x, y = piece.ind_pos
                if (x, y) == pos:
                    return piece
        else:
            return found_block

    def clear_selections(self):
        self.clicked_blocks = deque([], maxlen=2)

    def move(self, blocks):
        piece = blocks[0].piece

        if piece:
            av_moves = [p.end_pos for p in piece.calculate_moves(self)]

            if blocks[1].pos in av_moves:
                blocks[1].piece = blocks[0].piece
                blocks[1].piece.ind_pos = blocks[1].pos
                blocks[1].piece.img_path = blocks[1].piece.img_path
                blocks[0].piece = None

                # print([b.pos for b in self.clicked_blocks])
                self.clear_selections()

    def update(self):
        if len(self.clicked_blocks) > 1:
            self.move(self.clicked_blocks)

        # Iterate all board blocks and draw them
        for i in range(8):
            for j in range(8):
                self.blocks[i][j].draw(self.screen)
