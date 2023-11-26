# Handling user input and displaying the current GameState object
import pygame as p
import chess_engine
import timeit
import numpy as np
import cProfile
import pstats

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH / DIMENSION
MAX_FPS = 10 # Basically dictates how many buttons you can press per sec, related to animations
IMAGES = {}


'''Square conversion dictionaries'''
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

dict = {-100: 'bP', 100: 'wP', -500: 'bR', 500: 'wR', -300: 'bB', 300: 'wB',
        -293: 'bN', 293: 'wN', -900: 'bQ', 900: 'wQ', -1: 'bK', 1: 'wK'}

avg_move_time, avg_num_moves = [], []


'''Handle user input, and graphics'''
def main():

    highlight_sq = []
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))

    board = chess_engine.board
    dict = chess_engine.general_dict

    valid_moves = chess_engine.get_all_valid_moves(board, dict)

    move_made = False  # Flag for when we want to generate this function

    load_images()  # Does this once at the start as it is expensive computation
    running = True
    sq_selected = ()  # keep track of last input from user
    player_clicks = []  # keep track of player clicks, list of two tuples

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # Note if you add extra panels note to keep track of those
                col = int(location[0] // SQ_SIZE)
                row = int(location[1] // SQ_SIZE)

                if sq_selected == (8 * row + col):
                    sq_selected = ()  # Deselects if player clicks twice
                    player_clicks, highlight_sq = [], []

                else:
                    sq_selected = (8 * row + col)
                    player_clicks.append(sq_selected)  # Append both first and second clicks

                if len(player_clicks) == 1:
                    current_sq = get_single_move_notation(player_clicks[0])
                    highlight_sq.append(current_sq)


                    for move in valid_moves:

                        notation = move.get_chess_notation(chess_engine.board)

                        if notation[1:3] == get_single_move_notation(player_clicks[0]):
                            highlight_sq.append(notation[-2:])

                if len(player_clicks) == 2:
                    highlight_sq = []
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], board)

                    if move in valid_moves:
                        board, dict = chess_engine.make_move(board, move, dict)
                        move_made = True

                    sq_selected = ()
                    player_clicks = []

                '''Key press handler'''

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Do not allow for undo moves for now
                    board, dict = chess_engine.undo_move(board, dict)
                    move_made = True

                elif e.key == p.K_r:  # To make random moves
                    ind = np.random.randint(len(valid_moves))
                    rnd_move = valid_moves[ind]
                    board, dict = chess_engine.make_move(board, rnd_move, dict)
                    move_made = True

        if move_made:

            start = timeit.default_timer()
            valid_moves = chess_engine.get_all_valid_moves(board, dict)  # Note this will need to be valid moves only in the future
            time = timeit.default_timer() - start

            avg_move_time.append(time)
            avg_num_moves.append(len(valid_moves))
            print(f"Calculated {len(valid_moves)} moves in:", time)

            move_made = False

        draw_game_state(screen, board, highlight_sq)
        clock.tick(MAX_FPS)
        p.display.flip()


''' Responsible for all the graphics '''
def load_images():
    path = '/Users/federicosaitta/PycharmProjects/Chess/Images/'
    pieces = ['wP', 'bP', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wQ', 'bQ', 'wK', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(path + piece + '.png'), (SQ_SIZE, SQ_SIZE))


def draw_game_state(screen, board, highlight_sq_list):  # Drawing is done once per frame
    draw_board(screen)
    if len(highlight_sq_list) > 1:
        draw_highlights(screen, highlight_sq_list)
    draw_pieces(screen, board)


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

            piece = board[8 * r + c]
            if piece != 0:
                screen.blit(IMAGES[dict[piece]], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def get_single_move_notation(move):
    c = move % 8
    r = move // 8
    return cols_to_files[c] + rows_to_ranks[r]

if __name__ == '__main__':
    with cProfile.Profile() as profile:
        main()
        print(f'Moves per sec: {(1 / np.average(avg_move_time)) * np.average(avg_num_moves)}')

    #results = pstats.Stats(profile)
    #results.sort_stats(pstats.SortKey.TIME)
    #results.print_stats()