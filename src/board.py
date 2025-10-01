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

        self.poss_move: bool = False
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
        blocks = flatten_list(board.blocks)

        # Reset the click cycle buffer to initial position
        self.block_clicked = cycle([True, False])

        # Reset the board
        for block in blocks:
            block.clicked = False
            block.poss_move = False

        self.clicked = next(self.block_clicked)
        board.clicked_blocks.append(self)

        if len(board.clicked_blocks) == 1 and self.piece:
            """
            Enter here when you have made the first selection on the
            board and only if that selection is a block with a piece.
            As a first selection you can't select an empty block.
            The flow is:
                Click()
                    -> Show selected block
                    -> Show poss. moves
            """

            av_moves = self.piece.calculate_moves(board)
            for mv in av_moves:
                x, y = mv.end_pos
                board.blocks[x][y].poss_move = True

        elif len(board.clicked_blocks) == 2:
            """
            Enter here only when you have selected the second block.
            The flow is:
                Click()
                    -> Assuming the first selection was a piece. (which we ensure it is)
                    -> Calculate the poss. moves of the starting piece (start_pos)
                    -> Move to the second selection by the user (end_pos)
                    -> Reset the board (?)
                    -> Clear the clicked blocks cache
            """
            # On board change, store the board
            board.serialize()

            start, end = board.clicked_blocks
            if start.piece:
                if board.clicked_blocks[-1] == self:
                    # FIXME: There is a bug here, in the case of not appending a click
                    # (else clause) it think's that you re-pressed the same block.
                    for block in blocks:
                        block.clicked = False
                        block.poss_move = False
                moves = start.piece.calculate_moves(board)
                for mv in moves:
                    if mv.end_pos == end.pos:
                        board.move(board.clicked_blocks)
                        for block in blocks:
                            block.clicked = False
                            block.poss_move = False

            if start != end:
                board.current_player = next(board.players)

            board.clicked_blocks.clear()

        else:
            """
            We need to append a click to the cache for the logic to be checked.
            If all the logic fails then just do nothing, clear the cache.
            """

            # Reset the click state buffer, only for visual
            # no need to append to clicked_blocks, because
            # it's not a valid selection.
            self.clicked = next(self.block_clicked)

            board.clicked_blocks.clear()

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
    def __init__(self, screen: pygame.Surface, player: str):
        assert player in ["w", "b"], f"Player can be eiter white ('w') or black ('b')"

        self.screen = screen

        # Get screen widht, height borders
        self.s_width, self.s_height = self.screen.get_size()
        self.block_factory = BlockFactory()
        self.piece_factory = PieceFactory((self.s_width, self.s_height))
        self.move_factory = MoveFactory()

        self.players: List[str] = cycle(["b", "w"])
        self.current_player = player

        # A buffer to track all clicked blocks in the board
        self.clicked_blocks = deque([], maxlen=2)
        self.block_to_exec_move: Optional[Block] = None
        self.board_states: List[str] = []

        # Variable to track how many times we perform an undo, or step ahead
        self.board_hist_mov: int = 0

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

        self.serialize()

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
            # Are there 2 pieces in the board with the same position?
            # print([p.ind_pos for p in self.pieces].count((3, 5)))
            for piece in self.pieces:
                x, y = piece.ind_pos
                if (x, y) == pos:
                    return piece
        else:
            return found_block

    def clear_selections(self):
        self.clicked_blocks = deque([], maxlen=2)

    def move(self, blocks):
        """This ASSUMES that blocks are already of length 2"""
        piece = blocks[0].piece

        if piece:
            av_moves = [p.end_pos for p in piece.calculate_moves(self)]

            if blocks[1].pos in av_moves:
                # Remove the captured piece
                if blocks[0].piece and blocks[1].piece:
                    print(f"Removing block {blocks[1].piece}")
                    self.pieces.remove(blocks[1].piece)

                blocks[1].piece = blocks[0].piece
                blocks[1].piece.name = blocks[0].piece.name
                blocks[1].piece.team = blocks[0].piece.team
                blocks[1].piece.ind_pos = blocks[1].pos
                blocks[1].piece.img_path = blocks[0].piece.img_path
                blocks[0].piece = None

            self.clear_selections()

    def update(self):
        max_width, _ = self.screen.get_size()

        pygame.font.init()
        font = pygame.font.Font(None, 36)

        curr_player_text = font.render(
            f"Current player {self.current_player}", True, (0, 0, 0)
        )

        if len(self.clicked_blocks) > 1:
            self.move(self.clicked_blocks)

        # Iterate all board blocks and draw them
        for i in range(8):
            for j in range(8):
                self.blocks[i][j].draw(self.screen)

        board_width_bounds = self.blocks[7][7].pg_rect.right

        # Draw information about the game
        # description container
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            pygame.Rect(
                board_width_bounds + 30, 25, max_width - (board_width_bounds + 40), 600
            ),
            5,
        )

        self.screen.blit(curr_player_text, (board_width_bounds + 50, 100))

    def serialize(self):
        """
        This is a string representation of the board.
        The standard FEN notation won't be used, because
        of my modified board logic. There are no castling
        rights, promotion, en passant. So instead a simple
        loop will be used for all pieces like assuming
        white Rook at position (0, 0) followed by a white
        knight in (1, 0) at the board only becomes:
            -> WR00WK10 K for king, k for knight, same for bishop
        And at the end of the string, we have the player t
        hat plays next.
        """

        board_state: str = ""
        for piece in self.pieces:
            board_state += piece.team[0].capitalize()
            name = piece.name
            if name == "knight" or name == "bishop":
                board_state += name[0]
            else:
                board_state += name[0].capitalize()

            board_state += str(piece.ind_pos[0])
            board_state += str(piece.ind_pos[1])

        self.board_states.append(board_state)

    def load_prev_state(self):
        """
        We need to convert the serialized string,
        to the Piece format.
        """

        blocks = flatten_list(self.blocks)

        self.board_hist_mov += 1

        if self.board_hist_mov >= len(self.board_states):
            self.board_hist_mov = len(self.board_states)

        # Remove all pieces from the board
        self.pieces = []
        for block in blocks:
            block.piece = None

        state = self.board_states[-self.board_hist_mov]

        # To avoid any excess iterations,
        # we know in "state", we represent each piece every 4 characters.

        for i in range(len(state) // 4):
            # Get piece saved representation
            piece_repr = state[i * 4 : (i * 4) + 4]

            team = piece_repr[0].lower()

            name: Optional[str] = None
            match piece_repr[1]:
                # Get the name
                case "K":
                    name = "king"
                case "Q":
                    name = "queen"
                case "R":
                    name = "rook"
                case "b":
                    name = "bishop"
                case "k":
                    name = "knight"
                case "P":
                    name = "pawn"

            pos = (int(piece_repr[2]), int(piece_repr[3]))

            # Create saved piece
            self.pieces.append(self.piece_factory(name, pos, team))

            # Assign pieces to the correct block
            for piece in self.pieces:
                # Get the position of each piece, and access
                # its corresponding block.
                x, y = piece.ind_pos

                self.blocks[x][y].piece = piece

        else:
            print("No previous stored states in board.")
