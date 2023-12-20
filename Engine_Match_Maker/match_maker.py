
from Engine_1.move_generator import get_all_valid_moves, make_move, undo_move, board, general_dict
from Engine_1.move_finder import iterative_deepening
#from Engine_2 import

STARTING_BOARD = board.copy()
STARTING_DICT = general_dict.copy()
THINKING_TIME = 0.03



while True:
    white_moves = get_all_valid_moves(board, general_dict)
    if white_moves == []: break
    white_move = iterative_deepening(white_moves, board, general_dict, THINKING_TIME)
    make_move(board, white_move, general_dict)
    black_moves = get_all_valid_moves(board, general_dict)
    if black_moves == []: break
    black_move = iterative_deepening(black_moves, board, general_dict, THINKING_TIME)
    make_move(board, black_move, general_dict)


def print_pgn(old_move_log):
    move_notation = []
    print(len(old_move_log) / 2)
    for index in range(len(old_move_log)):
        move_made = old_move_log[index]
        print(move_made.promotion, move_made.get_pgn_notation(STARTING_BOARD))
        valid_moves = get_all_valid_moves(STARTING_BOARD, STARTING_DICT)
        check_flag, multiple_piece_flag = None, None

        if True:
            if move_made in valid_moves:
                valid_moves.remove(move_made)
            for move in valid_moves:
                if move.end_ind == move_made.end_ind:
                    if move.piece_moved == move_made.piece_moved:
                        multiple_piece_flag = True


        notation = move_made.get_pgn_notation(STARTING_BOARD, multiple_piece_flag)
        make_move(STARTING_BOARD, move_made, STARTING_DICT)
        move_notation.append(notation)

    turn = 0
    for index in range(len(move_notation)):
        turn = index//2 + 1
        if index % 2 == 0:
            move_notation[index] = str(turn) + '. ' + move_notation[index]

    print(' '.join(move_notation))


print_pgn(general_dict['move_log'])