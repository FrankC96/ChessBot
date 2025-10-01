import pygame
from typing import Optional

from board import Board, Block
from bot import minimax

if __name__ == "__main__":
    pygame.init()

    SCREEN = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    SCREEN.fill([255, 255, 255])

    HUMAN_PLAYER = "w"
    BOT_PLAYER = "b"

    BOARD = Board(SCREEN, HUMAN_PLAYER)

    clock = pygame.time.Clock()

    selected_block: Optional[Block] = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if HUMAN_PLAYER == BOARD.current_player:
                    selected_block = BOARD.find_by_pos(event.pos)

                    selected_block.select_block(BOARD)
                else:
                    pass
                    # best_move = minimax(BOARD, 2, BOT_PLAYER)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    BOARD.load_prev_state()

            if event.type == pygame.QUIT:
                running = False

        SCREEN.fill((255, 255, 255))

        BOARD.update()

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
