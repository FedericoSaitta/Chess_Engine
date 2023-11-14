# Handling user input and displaying the current GameState object
import timeit

import numpy as np
import pygame as p

from Files import chess_engine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH / DIMENSION
MAX_FPS = 15  # comes into play when animating images
IMAGES = {}

'Conversions constants'
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

avg_move_time = []
avg_num_moves = []


# Handle user input and update graphics
def main():  # Standard game loop for a game
    global highlight_sq  # Will fix this as no variable should be global ig
    highlight_sq = []

    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = chess_engine.GameState()

    starttime = timeit.default_timer()
    valid_moves = gs.get_all_valid_moves()  # Note this will need to be valid moves only in the future
    print("The time difference is :", timeit.default_timer() - starttime)

    move_made = False  # Flag for when we want to generate this function

    load_images()  # important to do this only once (expensive process)

    running = True
    sq_selected = ()  # keep track of last input from user
    player_clicks = []  # keep track of player clicks, two tuples

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:  # Change this to add dragging pieces
                location = p.mouse.get_pos()  # Note if you add extra panels note to keep track of those
                col = int(location[0] // SQ_SIZE)
                row = int(location[1] // SQ_SIZE)

                if sq_selected == (row, col):
                    sq_selected = ()  # deselects if player clicks twice
                    player_clicks = []
                    highlight_sq = []

                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)  # Append both first and second clicks

                if len(player_clicks) == 1:
                    current_sq = get_single_move_notation(player_clicks[0])
                    highlight_sq.append(current_sq)

                    for move in valid_moves:
                        notation = move.get_chess_notation(gs.board)
                        if notation[1:3] == get_single_move_notation(player_clicks[0]):
                            highlight_sq.append(notation[-2:])

                if len(player_clicks) == 2:
                    highlight_sq = []
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], gs.board)

                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True

                    sq_selected = ()
                    player_clicks = []

            # Key press handler

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Do not allow for undo moves for now
                    gs.undo_move()
                    move_made = True

                if e.key == p.K_LEFT:  # Use these to go through previous moves
                    pass

                elif e.key == p.K_RIGHT:
                    pass

                elif e.key == p.K_r:  # To make random moves
                    ind = np.random.randint(len(valid_moves))
                    rnd_move = valid_moves[ind]
                    gs.make_move(rnd_move)
                    move_made = True

        if move_made:
            #    print(f'White to play: {gs.white_to_move}')

            starttime = timeit.default_timer()
            valid_moves = gs.get_all_valid_moves()  # Note this will need to be valid moves only in the future
            time = timeit.default_timer() - starttime

            avg_move_time.append(time)
            avg_num_moves.append(len(valid_moves))

            print(f"Calculated {len(valid_moves)} moves in:", timeit.default_timer() - starttime)


            move_made = False

        draw_game_state(screen, gs, highlight_sq)
        clock.tick(MAX_FPS)
        p.display.flip()


''' Responsible for all the graphics '''


def load_images():
    path = '/Users/federicosaitta/PycharmProjects/Chess/Images/'
    pieces = ['wP', 'bP', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wQ', 'bQ', 'wK', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(path + piece + '.png'), (SQ_SIZE, SQ_SIZE))


def draw_game_state(screen, gs, highlight_sq_list):  # Drawing is done once per frame
    draw_board(screen)
    if len(highlight_sq_list) > 1:
        draw_highlights(screen, highlight_sq_list)
    draw_pieces(screen, gs.board)


def draw_board(screen):  # Draws the squares on the board
    colors = [p.Color((238, 238, 210)), p.Color((118, 160, 86))]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_highlights(screen, highlight_sq_list):
    color_red = (255, 50, 50)
    color_yellow = (255, 255, 51)

    if highlight_sq_list != []:
        for index, end_pos in enumerate(highlight_sq_list):
            end_row = ranks_to_rows[end_pos[1]]
            end_col = files_to_cols[end_pos[0]]

            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(128)
            s.fill(color_red) if index != 0 else s.fill(color_yellow)
            screen.blit(s, (end_col * SQ_SIZE, end_row * SQ_SIZE))


def draw_pieces(screen, board):  # Draws the pieces, need to draw them after the board
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def get_single_move_notation(move):
    return cols_to_files[move[1]] + rows_to_ranks[move[0]]


if __name__ == '__main__':
    main()
    print(f'Avg move gen time: {np.average(avg_move_time)}')
    print(f'Avg valid moves per turn: {np.average(avg_num_moves)}')
