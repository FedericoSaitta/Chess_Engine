# Handling user input and displaying the current GameState object
import pygame as p
import Board_state
from Search import find_random_move, iterative_deepening
from Move_Generator import get_all_valid_moves
import timeit
import time as t
from random import randint
import pstats
from collections import Counter
import cProfile


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH / DIMENSION
MAX_FPS = 10 # Basically dictates how many buttons you can press per sec, related to animations
IMAGES = {}
THINKING_MAX_TIME = 1 # Seconds (last iteration)



FEN  = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

'''Square conversion dictionaries'''
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

dict = {-100: 'bP', 100: 'wP', -500: 'bR', 500: 'wR', -330: 'bB', 330: 'wB',
        -320: 'bN', 320: 'wN', -900: 'bQ', 900: 'wQ', -1: 'bK', 1: 'wK'}


'''Handle user input, and graphics'''
def main():
    highlight_sq = []
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))

    dict, board = Board_state.generate_from_FEN(FEN)

    valid_moves = get_all_valid_moves(board, dict)
    move_made = False  # Flag for when we want to generate this function

    load_images()  # Does this once at the start as it is expensive computation
    running = True
    sq_selected = ()  # keep track of last input from user
    player_clicks = []  # keep track of player clicks, list of two tuples
    game_over = False

    player_one = True # If a human is playing white it will be true
    player_two = False # If a human is playing black it will be true
    draw_game_state(screen, board, highlight_sq)
    p.display.flip()

    while running:
        is_human_turn = (dict['white_to_move'] and player_one) or (not dict['white_to_move'] and player_two)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and is_human_turn:
                    location = p.mouse.get_pos()
                    col = int(location[0] // SQ_SIZE)
                    row = int(location[1] // SQ_SIZE)

                    if sq_selected == (8 * row + col):
                        sq_selected = ()              # Deselects if player clicks twice
                        player_clicks, highlight_sq = [], []

                    else:
                        sq_selected = (8 * row + col)
                        player_clicks.append(sq_selected)  # Append both first and second clicks

                    if len(player_clicks) == 1:
                        current_sq = get_single_move_notation(player_clicks[0])
                        highlight_sq.append(current_sq)

                        for move in valid_moves:
                            row, col = move.start_ind // 8, move.start_ind % 8
                            if (row, col) == get_single_move_notation(player_clicks[0]):
                                highlight_sq.append((move.end_ind // 8, move.end_ind % 8))


                    if len(player_clicks) == 2:
                        highlight_sq = []
                        move = Board_state.Move(player_clicks[0], player_clicks[1], board)

                        for engine_move in valid_moves:
                            if move == engine_move:
                                if engine_move.promotion:
                                    index = int(input('Promotion piece, type the index: [Q, R, B, N] \n'))
                                    piece = (['Q: 900', 'R: 500', 'B: 330', 'N: 320'][index])[-3:]
                                    if dict['white_to_move']: piece = int(piece)
                                    else: piece = - int(piece)
                                    move.prom_piece, move.promotion = piece, True
                                    Board_state.make_move(board, move, dict)
                                else:
                                    Board_state.make_move(board, engine_move, dict)
                                move_made = True
                                break

                        sq_selected = ()
                        player_clicks = []

            #'''Key press handler'''
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undoes twice so player can redo a move against an engine
                    Board_state.undo_move(board, dict)
                    Board_state.undo_move(board, dict)
                    move_made = True
                    game_over = False


        if not is_human_turn and not game_over:
            computer_move = iterative_deepening(valid_moves, board, dict, THINKING_MAX_TIME)
         #   t.sleep(1)
            Board_state.make_move(board, computer_move, dict)
            move_made = True

        if move_made and not game_over:
            valid_moves = get_all_valid_moves(board, dict)  # Note this will need to be valid moves only in the future

            move_made = False

            if valid_moves == []:
                game_over = True
                print('Game is Over')

        draw_game_state(screen, board, highlight_sq)
        clock.tick(MAX_FPS)
        p.display.flip()


########################################################################################################################
#                                                 GRAPHICS FUNCTIONS                                                   #
########################################################################################################################

def load_images():
    path = '/Users/federicosaitta/PycharmProjects/Chess/Images/'
    pieces = ['wP', 'bP', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wQ', 'bQ', 'wK', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(path + piece + '.png'), (SQ_SIZE, SQ_SIZE))


def draw_game_state(screen, board, highlight_sq_list):  # Drawing is done once per frame
    draw_board(screen)
    if len(highlight_sq_list) > 0:
        draw_highlights(screen, highlight_sq_list)
    draw_pieces(screen, board)


def draw_board(screen):  # Draws the squares on the board
    colors = [p.Color((238, 238, 210)), p.Color((118, 160, 86))]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''Fix the bug that if multiple pieces can land on the same '''
def draw_highlights(screen, highlight_sq_list):
    color_red = (255, 50, 50)
    color_yellow = (255, 255, 51)

    highlight_sq_list = list(dict.fromkeys(highlight_sq_list))
    # Removes duplicates from the list and preserves the order, this is done not to over-colour one square if
    # multiple pieces can jump to the same square

    for index, end_pos in enumerate(highlight_sq_list):

        end_row, end_col =  end_pos
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
    r, c = move // 8, move % 8
    return (r, c)

if __name__ == '__main__':

    with (cProfile.Profile() as profile):

        main()

        profiler_stats = pstats.Stats(profile)
     #   specific_file = ('Search.py')
        profiler_stats.strip_dirs().sort_stats('cumulative') # .print_stats(specific_file)


