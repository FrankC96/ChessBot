import pygame
from typing import Optional
from math import inf

from board import Board, Block
from piece import Move
from bot import minimax

if __name__ == "__main__":
    pygame.init()

    SCREEN = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT = SCREEN.get_size()

    SCREEN.fill([255, 255, 255])

    MAX_SEARCH_PLY = 1
    HUMAN_PLAYER = "b"
    BOT_PLAYER = "b" if HUMAN_PLAYER == "w" else "w"

    board = Board(MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT, HUMAN_PLAYER)

    clock = pygame.time.Clock()

    selected_block: Optional[Block] = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if board.current_player == HUMAN_PLAYER:
                    selected_block = board.find_by_pos_mouse(event.pos)
                    
                    if isinstance(selected_block, Block):
                        selected_block.select_block(board)

                if board.current_player == BOT_PLAYER:
                    score, best_piece, best_move, states_expl = minimax(
                        board, MAX_SEARCH_PLY, BOT_PLAYER
                    )

                    if score != abs(float(inf)) and isinstance(best_move, Move):
                        print("=" * 100)
                        print(
                            f"[{score}]\t->\t",
                            f"Chosen {best_piece} move from {best_move.start_pos} to {best_move.end_pos}",
                        )
                        print("=" * 100)
                        print(f"Explored {states_expl} states.")
                        if best_move:
                            x_start, y_start = best_move.start_pos
                            x_end, y_end = best_move.end_pos
                            start_block, end_block = (
                                board.blocks[x_start][y_start],
                                board.blocks[x_end][y_end],
                            )

                            board.move([start_block, end_block])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    board.load_prev_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = Board(MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT, HUMAN_PLAYER)

            if event.type == pygame.QUIT:
                running = False

        SCREEN.fill((255, 255, 255))

        board.update(SCREEN)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
