from chess_engine import make_move, undo_move, get_all_valid_moves, make_null_move, undo_null_move, HASH_LOG, Move
from random import randint
from math import fabs
import time
import pandas as pd
import os

push_move = make_move
retract_move = undo_move
get_valid_moves = get_all_valid_moves


# If when we score the board, positive values indicate white is winning
FABS = fabs
CHECK_MATE = 10_000
STALE_MATE = 0

current_script_path = os.path.abspath(__file__)
package_file_path = os.path.join(os.path.dirname(current_script_path), 'Opening_Data_Base', 'opening_moves.txt')

OPENING_LINES = package_file_path

## Taken from https://rustic-chess.org/front_matter/title.html, Marcel Vanthoor
MVV_LLA_TABLE = [
   [ 0,  0,  0,  0,  0,  0, 0],  # Victim K, 0's as it is checkmate already
   [50, 51, 52, 53, 54, 55, 0], # victim Q, attacker K, Q, R, B, N, P
   [40, 41, 42, 43, 44, 45, 0], # victim R, attacker K, Q, R, B, N, P
   [30, 31, 32, 33, 34, 35, 0], # victim B, attacker K, Q, R, B, N, P
   [20, 21, 22, 23, 24, 25, 0], # victim N, attacker K, Q, R, B, N, P
   [10, 11, 12, 13, 14, 15, 0], # victim P, attacker K, Q, R, B, N, P
   [ 0,  0,  0,  0,  0,  0, 0],  # No Victim
]


middle_game_pieces = {100: 82, 320: 337, 330: 365, 500: 477, 900: 1025,  1: 0} # adds to 4039
end_game_pieces = {100: 94, 320: 281, 330: 297, 500: 512,  900: 936,  1: 0}  # adds to 3868

PAWN_MG_white = ( 0,   0,   0,   0,   0,   0,  0,   0,
                 98, 134,  61,  95,  68, 126, 34, -11,
                 -6,   7,  26,  31,  65,  56, 25, -20,
                -14,  13,   6,  21,  23,  12, 17, -23,
                -27,  -2,  -5,  12,  17,   6, 10, -25,
                -26,  -4,  -4, -10,   3,   3, 33, -12,
                -35,  -1, -20, -23, -15,  24, 38, -22,
                  0,   0,   0,   0,   0,   0,  0,   0)

PAWN_EG_white = (  0,   0,   0,   0,   0,   0,   0,   0,
                    178, 173, 158, 134, 147, 132, 165, 187,
                     94, 100,  85,  67,  56,  53,  82,  84,
                     32,  24,  13,   5,  -2,   4,  17,  17,
                     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
                      4,   7,  -6,   1,   0,  -5,  -1,  -8,
                     13,   8,   8,  10,  13,   0,   2,  -7,
                      0,   0,   0,   0,   0,   0,   0,   0)

KNIGHT_MG_white = (-167, -89, -34, -49,  61, -97, -15, -107,
                 -73, -41,  72,  36,  23,  62,   7,  -17,
                 -47,  60,  37,  65,  84, 129,  73,   44,
                  -9,  17,  19,  53,  37,  69,  18,   22,
                 -13,   4,  16,  13,  28,  19,  21,   -8,
                 -23,  -9,  12,  10,  19,  17,  25,  -16,
                 -29, -53, -12,  -3,  -1,  18, -14,  -19,
                -105, -21, -58, -33, -17, -28, -19,  -23)

KNIGHT_EG_white = (-58, -38, -13, -28, -31, -27, -63, -99,
            -25,  -8, -25,  -2,  -9, -25, -24, -52,
            -24, -20,  10,   9,  -1,  -9, -19, -41,
            -17,   3,  22,  22,  22,  11,   8, -18,
            -18,  -6,  16,  25,  16,  17,   4, -18,
            -23,  -3,  -1,  15,  10,  -3, -20, -22,
            -42, -20, -10,  -5,  -2, -20, -23, -44,
            -29, -51, -23, -15, -22, -18, -50, -64)

BISHOP_MG_white = (-29,   4, -82, -37, -25, -42,   7,  -8,
                -26,  16, -18, -13,  30,  59,  18, -47,
                -16,  37,  43,  40,  35,  50,  37,  -2,
                 -4,   5,  19,  50,  37,  37,   7,  -2,
                 -6,  13,  13,  26,  34,  12,  10,   4,
                  0,  15,  15,  15,  14,  27,  18,  10,
                  4,  15,  16,   0,   7,  21,  33,   1,
                -33,  -3, -14, -21, -13, -12, -39, -21)

BISHOP_EG_white = (-14, -21, -11,  -8, -7,  -9, -17, -24,
                 -8,  -4,   7, -12, -3, -13,  -4, -14,
                  2,  -8,   0,  -1, -2,   6,   0,   4,
                 -3,   9,  12,   9, 14,  10,   3,   2,
                 -6,   3,  13,  19,  7,  10,  -3,  -9,
                -12,  -3,   8,  10, 13,   3,  -7, -15,
                -14, -18,  -7,  -1,  4,  -9, -15, -27,
                -23,  -9, -23,  -5, -9, -16,  -5, -17)

ROOK_MG_white = (     32,  42,  32,  51, 63,  9,  31,  43,
             27,  32,  58,  62, 80, 67,  26,  44,
             -5,  19,  26,  36, 17, 45,  61,  16,
            -24, -11,   7,  26, 24, 35,  -8, -20,
            -36, -26, -12,  -1,  9, -7,   6, -23,
            -45, -25, -16, -17,  3,  0,  -5, -33,
            -44, -16, -20,  -9, -1, 11,  -6, -71,
            -19, -13,   1,  17, 16,  7, -37, -26)

ROOK_EG_white = (13, 10, 18, 15, 12,  12,   8,   5,
                11, 13, 13, 11, -3,   3,   8,   3,
                 7,  7,  7,  5,  4,  -3,  -5,  -3,
                 4,  3, 13,  1,  2,   1,  -1,   2,
                 3,  5,  8,  4, -5,  -6,  -8, -11,
                -4,  0, -5, -1, -7, -12,  -8, -16,
                -6, -6,  0,  2, -9,  -9, -11,  -3,
                -9,  2,  3, -1, -5, -13,   4, -20)

QUEEN_MG_white = (    -28,   0,  29,  12,  59,  44,  43,  45,
            -24, -39,  -5,   1, -16,  57,  28,  54,
            -13, -17,   7,   8,  29,  56,  47,  57,
            -27, -27, -16, -16,  -1,  17,  -2,   1,
             -9, -26,  -9, -10,  -2,  -4,   3,  -3,
            -14,   2, -11,  -2,  -5,   2,  14,   5,
            -35,  -8,  11,   2,   8,  15,  -3,   1,
             -1, -18,  -9,  10, -15, -25, -31, -50)

QUEEN_EG_white = ( -9,  22,  22,  27,  27,  19,  10,  20,
            -17,  20,  32,  41,  58,  25,  30,   0,
            -20,   6,   9,  49,  47,  35,  19,   9,
              3,  22,  24,  45,  57,  40,  57,  36,
            -18,  28,  19,  47,  31,  34,  39,  23,
            -16, -27,  15,   6,   9,  17,  10,   5,
            -22, -23, -30, -16, -16, -23, -36, -32,
            -33, -28, -22, -43,  -5, -32, -20, -41)

KING_MG_white = (-65,  23,  16, -15, -56, -34,   2,  13,
             29,  -1, -20,  -7,  -8,  -4, -38, -29,
             -9,  24,   2, -16, -20,   6,  22, -22,
            -17, -20, -12, -27, -30, -25, -14, -36,
            -49,  -1, -27, -39, -46, -44, -33, -51,
            -14, -14, -22, -46, -44, -30, -15, -27,
              1,   7,  -8, -64, -43, -16,   9,   8,
            -15,  36,  12, -54,   8, -28,  24,  14)

KING_EG_white = (-74, -35, -18, -18, -11,  15,   4, -17,
            -12,  17,  14,  17,  17,  38,  23,  11,
             10,  17,  23,  15,  20,  45,  44,  13,
             -8,  22,  24,  27,  26,  33,  26,   3,
            -18,  -4,  21,  24,  27,  23,   9, -11,
            -19,  -3,  11,  21,  23,  16,   7,  -9,
            -27, -11,   4,  13,  14,   4,  -5, -17,
            -53, -34, -21, -11, -28, -14, -24, -43)


PAWN_MG_black = [-item for item in tuple(reversed(PAWN_MG_white))]
PAWN_EG_black = [-item for item in tuple(reversed(PAWN_EG_white))]

KNIGHT_MG_black = [-item for item in tuple(reversed(KNIGHT_MG_white))]
KNIGHT_EG_black = [-item for item in tuple(reversed(KNIGHT_EG_white))]

BISHOP_MG_black = [-item for item in tuple(reversed(BISHOP_MG_white))]
BISHOP_EG_black = [-item for item in tuple(reversed(BISHOP_EG_white))]

ROOK_MG_black = [-item for item in tuple(reversed(ROOK_MG_white))]
ROOK_EG_black = [-item for item in tuple(reversed(ROOK_EG_white))]

QUEEN_MG_black  = [-item for item in tuple(reversed(QUEEN_MG_white))]
QUEEN_EG_black  = [-item for item in tuple(reversed(QUEEN_EG_white))]

KING_MG_black = [-item for item in tuple(reversed(KING_MG_white))]
KING_EG_black = [-item for item in tuple(reversed(KING_EG_white))]


piece_sq_values = {100: (PAWN_MG_white,PAWN_EG_white), -100:(PAWN_MG_black, PAWN_EG_black),
                   320: (KNIGHT_MG_white,KNIGHT_EG_white), -320: (KNIGHT_MG_black, KNIGHT_EG_black),
                   330: (BISHOP_MG_white,BISHOP_EG_white), -330: (BISHOP_MG_black, BISHOP_EG_black),
                   500: (ROOK_MG_white,ROOK_EG_white), -500: (ROOK_MG_black, ROOK_EG_black),
                   900: (QUEEN_MG_white,QUEEN_EG_white), -900: (QUEEN_MG_black, QUEEN_EG_black),
                   1: (KING_MG_white,KING_EG_white) , -1: (KING_MG_black, KING_EG_black)}

NODES_SEARCHED = 0
TURN = 0
OUT_OF_BOOK = False


OPENING_DF = pd.read_csv(OPENING_LINES, delim_whitespace=True, header=None)


def find_random_move(moves):
    if moves != []:
        index = randint(0, len(moves) - 1)
        return moves[index]
    else:
        return None


def get_opening_book(board, moves, dict):
    global OPENING_DF, TURN, OUT_OF_BOOK


    try: # We look if the current position key is present in the data frame
        if len(dict['move_log']) > 0:
            # Increments turn by two if playing against a human
            if (not dict['white_to_move']) and (TURN % 2 ==0):
                TURN += 1

            previous_move = (dict['move_log'][-1]).get_pgn_notation(board)
            previous_move_2 = (dict['move_log'][-1]).get_pgn_notation(board, multiple_piece_flag=True)

            OPENING_1 = OPENING_DF.copy()

            OPENING_DF = OPENING_DF[OPENING_DF[:][TURN - 1] == previous_move].copy()

            if OPENING_DF.empty: OPENING_DF = OPENING_1[OPENING_1[:][TURN - 1] == previous_move_2]

            OPENING_DF = OPENING_DF.reset_index(drop=True)

            index = randint(0, len(OPENING_DF) - 1)
            move = OPENING_DF.loc[index, TURN]
            move = get_move_from_notation(board, moves, move)

           # return move

        else: # We choose a random move from the starting possibilities
            index = randint(0, len(OPENING_DF) - 1)
            move = OPENING_DF.loc[index, TURN]
            move = get_move_from_notation(board, moves, move)


        TURN += 1
        print('We found a book move which is: ', move.get_pgn_notation(board))
        return move

    except (KeyError, ValueError, AttributeError): # Means we are out of book, so we return to finding a move with negamax
        print('Out of book')
        OUT_OF_BOOK = True
        return None


ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}


def get_move_from_notation(board, moves, notation):
    if notation is None: return None
    if notation == 'O-O':
        end_col = 6
        for move in moves:
            if (move.end_ind % 8 == end_col) and move.castle_move:
                return move

    elif notation == 'O-O-O' :
        end_col = 2
        for move in moves:
            if (move.end_ind % 8 == end_col) and move.castle_move:
                return move


    end_square = files_to_cols[notation[-2]] + 8 * ranks_to_rows[notation[-1]]

    # Checks if there are multiple moves of the same type achieving the same square
    # So we flag them as multiple moves

    # FIX THIS
    all_possible_notations = [move.get_pgn_notation(board) for move in moves]
    for move in moves:
        move_notation = move.get_pgn_notation(board)

        if all_possible_notations.count(move_notation) > 1:
            move_not = move.get_pgn_notation(board, multiple_piece_flag=True)
        else:
            move_not = move.get_pgn_notation(board)

        if move_not == notation:
            return move

    print('Could not find a move for this notation: ', notation)
    return None


########################################################################################################################
#                                                  MOVE SEARCH FUNCTION                                                #
########################################################################################################################


### ALPHA BETA PRUNING IS NOT RETURNING THE RIGHT RESULTS, BACK TO SQUARE ONE, IT looks as if it is just assuming the
### opponent plays the worst possible moves instead of the best ones


# Engine does not go for the fastest mate
# Engine doesn't see stale mate and also doesnt see 3 move repetition (will fix the latter at a later point_
def iterative_deepening(moves, board, dict, time_constraints):
    best_move, DEPTH = None, 1
    start_time = time.time()

    turn_multiplier = 1 if dict['white_to_move'] else -1

    # First 9 turns moves can be done by opening book
    # Statistically probs only 3/4 turns actually done
    if (len(dict['move_log']) < 10) and not OUT_OF_BOOK:
        best_move = get_opening_book(board, moves, dict)


    if best_move is None:
        moves = move_ordering(moves)

        while True:
          #  print('searching at a depth of:', DEPTH)
            best_move = root_negamax(moves, board, dict, turn_multiplier, DEPTH)
            DEPTH += 1

            if (time.time() - start_time > time_constraints) or DEPTH == 15:
        #        print("Time limit exceeded. Stopping search.")
                break

            moves.remove(best_move)
            moves.insert(0, best_move)

    if best_move is None: return find_random_move(moves)

   # print(best_move.get_pgn_notation(board))

    return best_move


def root_negamax(moves, board, dict, turn_multiplier, DEPTH):
    global NODES_SEARCHED
    score = None
    max_score, best_move = -100_000, None
    alpha, beta = -CHECK_MATE, CHECK_MATE

    if moves == []:
        if dict['in_check']:
            return -CHECK_MATE
        else:
            return STALE_MATE

    for move in moves:
        push_move(board, move, dict)
        score = -negamax(board, dict, DEPTH - 1, -turn_multiplier, -beta, -alpha)
        retract_move(board, dict)
        #print(move.get_pgn_notation(board), 'score: (white)', score * turn_multiplier)

        if score > max_score:
            max_score, best_move = score, move

        if max_score > alpha:
            alpha = max_score

        if alpha >= beta:
           break

    if best_move is None:
        best_move = find_random_move(moves)

    print('Best move at depth: ', DEPTH, ' is: ', best_move.get_pgn_notation(board), 'eval_bar: (white)', score * turn_multiplier, 'SEARCHED: ', NODES_SEARCHED)
    NODES_SEARCHED = 0
    return best_move



EXTENSION = 5
def quiescence_search(board, dict, turn_multiplier, alpha, beta, extension):

    stand_pat = evaluate_board(board, dict, turn_multiplier) * turn_multiplier

    if stand_pat >= beta:
        return beta  # Fail-hard beta-cutoff

    if alpha < stand_pat:
        alpha = stand_pat  # New alpha

    if extension == 0:
        return alpha


    moves = get_valid_moves(board, dict)

    if moves == []:
        if dict['in_check']:
            return -CHECK_MATE
        else:
            return STALE_MATE



    captures = [move for move in moves if move.piece_captured != 0]
    move_ordering(captures) # Now sorting the captures

    for move in captures:

        push_move(board, move, dict)
        score = -quiescence_search(board, dict, -turn_multiplier, -beta, -alpha, extension - 1)
        retract_move(board, dict)

        if score >= beta:
            return beta  # Fail-hard beta-cutoff

        if score > alpha:
            alpha = score  # New alpha

    return alpha



def negamax(board, dict, depth, turn_multiplier, alpha, beta):
    if depth == 0:
        return quiescence_search(board, dict, turn_multiplier, alpha, beta, EXTENSION)


    best = -CHECK_MATE
    moves = move_ordering(get_valid_moves(board, dict))

    if moves == []:
        if dict['in_check']:
            return -CHECK_MATE
        else:
            return STALE_MATE

#  Removing null move pruning it seems to aggressive
 #   if depth > 3 and (not dict['in_check']):
 #       make_null_move(dict)
  #      null_move_score = -negamax(board, dict, depth - 3, -turn_multiplier, -beta, -beta+1)
 #       undo_null_move(dict)
 #       if null_move_score >= beta:
 #           return null_move_score  # Null move pruning

    for move in moves:
        make_move(board, move, dict)
        score = -negamax(board, dict, depth - 1, -turn_multiplier, -beta, -alpha)
        retract_move(board, dict)


        if score > best:
            best = score

        if score > alpha:
            alpha = score

        if alpha >= beta:
            break

    return best

########################################################################################################################
#                                                   EVALUATION FUNCTION                                                #
########################################################################################################################


### This is returns the same value wheter it is white or black perspective
def evaluate_board(board, dict, turn_multiplier):
    global NODES_SEARCHED
    ### COUNTING FOR 3 MOVE REPETITION:
    if len(HASH_LOG) > 7:
        counter = 0
        for index in range(len(HASH_LOG)-1, -1, -1):
            hash = HASH_LOG[index]

            if hash == (dict['ZOBRIST_HASH']):
                counter += 1

            if counter == 3:
                dict['stale_mate'] = True
                return STALE_MATE

    NODES_SEARCHED += 1

    enemy_score = 0
    for square in board:
            if square > 0 and (turn_multiplier == -1):  enemy_score += square
            elif square < 0 and (turn_multiplier == 1): enemy_score -= square

    enemy_score = 4000 if enemy_score > 4000 else enemy_score

    value = map(lambda square: interpolate_pesto_board(square[0], square[1], enemy_score), enumerate(board))
    eval_bar = sum(value)


    # This takes way too long
    if (eval_bar * turn_multiplier) > 300 and (enemy_score < 1500):
        side_winning = 1 if eval_bar > 0 else -1

        white_k = (dict['white_king_loc'] // 8, dict['white_king_loc'] % 8)
        black_k = (dict['black_king_loc'] // 8, dict['black_king_loc'] % 8)

        king_distance = ((white_k[0] - black_k[0]) ** 2 + (white_k[1] - black_k[1]) ** 2) ** 0.5

        if side_winning == 1:  # White is winning
            eval_bar -= king_distance * 25
        else:  # Black is winning
            eval_bar += king_distance * 25

        if side_winning == 1:
            row, col = (black_k[0] - 4), (black_k[1] - 4)
            distance = (row**2 + col**2) * 4 - 128

        else:
            row, col = (white_k[0] - 4), (white_k[1] - 4)
            distance = 128 - (row ** 2 + col ** 2)*4

        eval_bar += distance


    return eval_bar / 100


def interpolate_pesto_board(square_ind, piece, enemy_pieces_values):
    enemy_pieces_values = 800 if enemy_pieces_values < 800 else enemy_pieces_values
    if piece == 0:
        return 0

    side_multiplier = 1 if piece > 0 else -1
    abs_piece = piece * side_multiplier

    middle_game_value, end_game_value = piece_sq_values[piece][0][square_ind], piece_sq_values[piece][1][square_ind]

    difference = end_game_value - middle_game_value
    difference_piece_value = end_game_pieces[abs_piece] - middle_game_pieces[abs_piece]

    interpolation_percentage = (4000 - enemy_pieces_values) / 3200
    # Dividing by 3200 as to enter the endgame when 80% of the pieces are gone

    single_sq_evaluation = middle_game_value + interpolation_percentage * difference_piece_value
    single_piece_evaluation = middle_game_pieces[abs_piece] + interpolation_percentage * difference_piece_value

    return (single_piece_evaluation * side_multiplier) + single_sq_evaluation


########################################################################################################################
#                                               MOVER ORDERING FUNCTION                                                #
########################################################################################################################

## Aggressive move ordering to lead to great pruning is the way to really increase\
## the speed of the engine, focus on this until you cant anymore,

piece_indices = {1: 0, 900: 1, 500: 2, 330: 3, 320: 4, 100: 5, 0:6,
                -1: 0, -900: 1, -500: 2, -330: 3, -320: 4, -100: 5}

def move_ordering(moves):
    # The -1 ensures that all captures are looked at first before normal moves

    score = [MVV_LLA_TABLE[piece_indices[move.piece_captured]][piece_indices[move.piece_moved]]  for move in moves]
    combined = list(zip(moves, score))

    # Sort the combined list based on scores
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

    # Extract the sorted values
    moves = [item[0] for item in sorted_combined]

    #for tup in sorted_combined:
   #     if tup[1] != 0:
   #         print(tup[0].get_pgn_notation(board), tup[1])

    return moves