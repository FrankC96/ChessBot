import pygame

from board import Board


if __name__ == "__main__":
    with open("./board_states.txt", "r") as states_file:
        boards_history = states_file.read()

    boards_history = boards_history.split("\n")

    pygame.init()

    SCREEN = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT = SCREEN.get_size()

    SCREEN.fill([255, 255, 255])

    HUMAN_PLAYER = "b"
    BOT_PLAYER = "b" if HUMAN_PLAYER == "w" else "w"

    BOARD = Board(MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT, HUMAN_PLAYER)

    clock = pygame.time.Clock()

    time_idx = 0
    state = boards_history[time_idx]
    BOARD.load_prev_state(state)

    i = 0
    while boards_history[0][i] == boards_history[1][i]:
        i += 1
        if i == len(boards_history[0]):
            print("States are identical!")
            break

    running = True
    while running:
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # Go backwards in time, if initial board is reached cap time_idx = 0
                    time_idx -= 1

                    if time_idx < 1:
                        time_idx = 0

                    print(f"Current timeframe [{time_idx}/{len(boards_history)}]")
                    state = boards_history[time_idx]
                    BOARD.load_prev_state(state)

                elif event.key == pygame.K_RIGHT:
                    # Go forwards in time, if max board states reach cap at len(board_states) - 1
                    time_idx += 1

                    if time_idx > len(boards_history) - 1:
                        time_idx = len(boards_history) - 1

                    print(f"Current timeframe [{time_idx}/{len(boards_history)}]")
                    state = boards_history[time_idx]
                    BOARD.load_prev_state(state)

                elif event.key == pygame.K_r:
                    # Board reset
                    time_idx = 0

                    print(f"Current timeframe [{time_idx}/{len(boards_history)}]")
                    state = boards_history[time_idx]
                    BOARD.load_prev_state(state)

            if event.type == pygame.QUIT:
                running = False

        SCREEN.fill((255, 255, 255))

        BOARD.update(SCREEN)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
