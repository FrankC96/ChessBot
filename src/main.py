import pygame
from typing import Optional

from board import Board, Block


if __name__ == "__main__":
    pygame.init()

    SCREEN = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    SCREEN.fill([255, 255, 255])

    START_PLAYER = "w"
    CURRENT_PLAYER = START_PLAYER

    BOARD = Board(SCREEN)

    clock = pygame.time.Clock()

    selected_block: Optional[Block] = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                selected_block = BOARD.find_by_pos(event.pos)

                selected_block.select_block(BOARD)
                print(selected_block)

            if event.type == pygame.QUIT:
                running = False

        SCREEN.fill((150, 150, 150))

        BOARD.update()

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
