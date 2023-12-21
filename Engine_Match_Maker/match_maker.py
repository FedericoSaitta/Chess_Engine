
from Engine_1_OLD.move_generator import get_all_valid_moves, make_move, undo_move, board, general_dict
from Engine_1_OLD.move_finder import iterative_deepening
from Engine_2_NEW.move2_generator import get_all_valid_moves as get_all_valid_moves2
from Engine_2_NEW.move2finder import  iterative_deepening as iterative_deepening2
#from Engine_2_NEW import

STARTING_BOARD  = [  # Switching to a 1D board representation    # Left right is +/- 1 and up and down is +/- 8
    -500, -320, -330, -900, -1, -330, 0 , -500,  #  0  to 7
    -100, -100, -100, 0 , -100, -100 , -100, -100,  # 8 to 15
      0 ,  0  ,  0  , 0   ,  0  , -320,  0  ,   0 ,  # 16 to 23
      0 ,  0  , 0   , -100  ,  0  ,  0  ,  0  ,  0  ,  # 24 to 31
      0 ,  0  ,100  , 100 ,  0  ,  0  ,  0  ,  0  ,  # 32 to 39
      0 ,   0 ,   0 ,  0  ,  0  ,  0  ,  0  ,  0  ,  # 40 to 47
     100,  100,  0  ,  0  , 100  ,  100,  100,  100,  # 48 to 55
     500,  320,  330,  900,    1,  330,  320  ,  500]  # 56 to 63

board = STARTING_BOARD.copy()


STARTING_DICT = general_dict.copy()
THINKING_TIME =  2 # Seconds


while True:
    white_moves = get_all_valid_moves2(board, general_dict)

    if white_moves == []: break

    white_move = iterative_deepening2(white_moves, board, general_dict, THINKING_TIME)
    make_move(board, white_move, general_dict)

    black_moves = get_all_valid_moves(board, general_dict)

    if black_moves == []: break

    black_move = iterative_deepening(black_moves, board, general_dict, THINKING_TIME)
    make_move(board, black_move, general_dict)

'''There is still something wrong with the printing of the notation
but only in the notation, the engines print out the moves well'''

'''Random king moves (not castles are being made)'''

'''Sometimes it discards clearly good moves for ones that are not so much, probs due to evaluation 
function'''

def print_pgn(old_move_log):
    move_notation = []
    print(len(old_move_log) / 2)
    for index in range(len(old_move_log)):
        move_made = old_move_log[index]

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

    for index in range(len(move_notation)):
        turn = index//2 + 3
        if index % 2 == 0 :
            move_notation[index] = str(turn) + '. ' + move_notation[index]

    print(' '.join(move_notation))


print_pgn(general_dict['move_log'])