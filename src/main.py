import pygame
from typing import Optional

from board import Board, Block
from bot import minimax

if __name__ == "__main__":
    pygame.init()

    SCREEN = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT = SCREEN.get_size()

    SCREEN.fill([255, 255, 255])

    HUMAN_PLAYER = "w"
    BOT_PLAYER = "b" if HUMAN_PLAYER == "w" else "w"

    BOARD = Board(MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT, HUMAN_PLAYER)

    clock = pygame.time.Clock()

    selected_block: Optional[Block] = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BOARD.current_player == HUMAN_PLAYER:
                    selected_block = BOARD.find_by_pos(event.pos)

                    selected_block.select_block(BOARD)

                    # yes this is weird, but after a move is executed
                    # the clicked_blocks cache becomes 0.
                    # Since, we have already clicked a block, we know
                    # that the next time the cache is 0, the human
                    # player has performed a move.

                    if (
                        len(BOARD.clicked_blocks) == 0
                        and BOARD.current_player == BOT_PLAYER
                    ):
                        _, _, best_move = minimax(BOARD, 1, BOT_PLAYER)

                        x_start, y_start = best_move.start_pos
                        x_end, y_end = best_move.end_pos
                        start_block, end_block = (
                            BOARD.blocks[x_start][y_start],
                            BOARD.blocks[x_end][y_end],
                        )

                        BOARD.move([start_block, end_block])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    BOARD.load_prev_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    BOARD = Board(MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT, HUMAN_PLAYER)

            if event.type == pygame.QUIT:
                running = False

        SCREEN.fill((255, 255, 255))

        BOARD.update(SCREEN)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
