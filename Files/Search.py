from Board_state import make_move, undo_move, make_null_move, undo_null_move, Move
from Move_Generator import get_all_valid_moves
from random import randint
from math import fabs
from Evaluation import evaluate_board

import time
from pandas import read_csv
import os
import numpy as np

push_move = make_move
retract_move = undo_move
get_valid_moves = get_all_valid_moves

# If when we score the board, positive values indicate white is winning
FABS = fabs
CHECK_MATE = 9_999
STALE_MATE = 0

current_script_path = os.path.abspath(__file__)
package_file_path = os.path.join(os.path.dirname(current_script_path), 'Opening_repertoire.txt')

OPENING_LINES = package_file_path

## Taken from https://rustic-chess.org/front_matter/title.html, Marcel Vanthoor
MVV_LLA_TABLE = [
    [0, 0, 0, 0, 0, 0, 0],  # Victim K, 0's as it is checkmate already
    [50, 51, 52, 53, 54, 55, 0],  # victim Q, attacker K, Q, R, B, N, P
    [40, 41, 42, 43, 44, 45, 0],  # victim R, attacker K, Q, R, B, N, P
    [30, 31, 32, 33, 34, 35, 0],  # victim B, attacker K, Q, R, B, N, P
    [20, 21, 22, 23, 24, 25, 0],  # victim N, attacker K, Q, R, B, N, P
    [10, 11, 12, 13, 14, 15, 0],  # victim P, attacker K, Q, R, B, N, P
    [0, 0, 0, 0, 0, 0, 0],  # No Victim
]

NODES_SEARCHED = 0
TURN = 0
OUT_OF_BOOK = False


OPENING_DF = None

def find_random_move(moves):
    if moves != []:
        index = randint(0, len(moves) - 1)
        return moves[index]
    else:
        return None


def get_opening_book(board, moves, dict):
    global OPENING_DF, TURN, OUT_OF_BOOK

    if OPENING_DF is None:
        OPENING_DF = read_csv(OPENING_LINES, delim_whitespace=True, header=None)

    try:  # We look if the current position key is present in the data frame
        if len(dict['move_log']) > 0:
            # Increments turn by two if playing against a human
            if (not dict['white_to_move']) and (TURN % 2 == 0):
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

        else:  # We choose a random move from the starting possibilities
            index = randint(0, len(OPENING_DF) - 1)
            move = OPENING_DF.loc[index, TURN]
            move = get_move_from_notation(board, moves, move)

        TURN += 1
     #   print('We found a book move which is: ', move.get_pgn_notation(board))
        return move

    except (
    KeyError, ValueError, AttributeError):  # Means we are out of book, so we return to finding a move with negamax
    #    print('Out of book')
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

    elif notation == 'O-O-O':
        end_col = 2
        for move in moves:
            if (move.end_ind % 8 == end_col) and move.castle_move:
                return move

    end_square = files_to_cols[notation[-2]] + 8 * ranks_to_rows[notation[-1]]

    # Checks if there are multiple moves of the same type achieving the same square
    # So we flag them as multiple moves

    all_possible_notations = [move.get_pgn_notation(board) for move in moves]
    for move in moves:
        move_notation = move.get_pgn_notation(board)

        if all_possible_notations.count(move_notation) > 1:
            move_not = move.get_pgn_notation(board, multiple_piece_flag=True)
        else:
            move_not = move.get_pgn_notation(board)

        if move_not == notation:
            return move

   # print('Could not find a move for this notation: ', notation)
    return None


########################################################################################################################
#                                                  MOVE SEARCH FUNCTION                                                #
########################################################################################################################


# Note that pypy doesn't seem that much faster than normal python, it does speed up with heavier computation but maybe
# Cython is best, or rewriting some functions could also help quite a bit


# Alpha beta is now slow because of the fact tht quiet moves are not ordered at all
def iterative_deepening(moves, board, dict, time_constraints):
    global NODES_SEARCHED
    best_move, DEPTH = None, 1
    turn_multiplier = 1 if dict['white_to_move'] else -1

    if (len(dict['move_log']) < 10) and not OUT_OF_BOOK:
        pass
      #  best_move = get_opening_book(board, moves, dict)

    start_time = time.time()

    if best_move is None:
        moves = move_ordering(moves)

        while True:
            NODES_SEARCHED = 0
            print('searching at a depth of:', DEPTH)
            best_move = negamax_root(moves, board, dict, turn_multiplier, DEPTH)

            if (time.time() - start_time > time_constraints) or DEPTH == 15:
                break  # We have exceeded the time frame for a single search so we stop looking deeper

            if best_move is not None:
                # Of course when the engine found a forced mate, it gives up. This could be fixed in the future but for
                # now if a checkmate sequence is found then we simply make random moves

                # Move ordering by best move from previous search
                moves.remove(best_move)
                moves.insert(0, best_move)

            DEPTH += 1

    if best_move is None: return find_random_move(moves)

    return best_move


# Make sure the same are returned both with alpha and beta pruning and without
def negamax_root(moves, board, dict, turn_multiplier, depth):
    # The first set of parent moves have already been ordered
    best_score, best_move = -CHECK_MATE, None
    alpha, beta = -10_000, 10_000

    # Note with alpha beta pruning some moves will have the same evaluation but that is because they are
    # Moves whose nodes have been pruned.

    for move in moves:
    #    print('Parent move: ', move.get_pgn_notation(board))
        # One is subtracted by the depth as we are looking at parent moves already
        make_move(board, move, dict)
        score = -negamax(board, dict, -turn_multiplier, depth - 1, -beta, -alpha)
        retract_move(board, dict)

     #   print('Move: ', move.get_pgn_notation(board), ' score: ', score * turn_multiplier)

        if score > best_score:
            best_score = score
            best_move = move

        if best_score > alpha: alpha = best_score
        if alpha >= beta: break

#    print('Explored: ', NODES_SEARCHED, 'Best Move is: ', best_move.get_pgn_notation(board), ' score: ',
     #      best_score * turn_multiplier)

    return best_move


# Also could create a way to see exactly what line the engine is thinking
EXTENSION = 5
def negamax(board, dict, turn_multiplier, depth, alpha, beta):

    if depth == 0:
        score = quiesce_search(board, dict, turn_multiplier, EXTENSION, alpha, beta)
        return score

    best = -CHECK_MATE
    moves = get_valid_moves(board, dict)
    parent_moves = move_ordering(moves)  # Ordering moves by MVV/LLA for more pruning

    # Done this way as I detect check or stalemate after all the moves have been retrieved
    # This fails if only depth 1 is considered, assuming we always look further it is sound.
    if dict['stale_mate']: return STALE_MATE
    if dict['check_mate']: return CHECK_MATE * turn_multiplier


    # The theory is that if your opponent could make two consecutive moves and not
    # improve his position, you must have an overwhelming advantage

    # Note that this will activate for searches at depth 3
    if depth > 2 and (not dict['in_check']):

        # Beta window is + 1.5
        make_null_move(dict)
        null_move_score = -negamax(board, dict, -turn_multiplier, depth - 2, -beta, -beta+1)
        undo_null_move(dict)

        if null_move_score >= beta:
            return null_move_score  # Null move pruning

    for child in parent_moves:
  #      print('child move: ', child.get_pgn_notation(board))
        push_move(board, child, dict)
        score = -negamax(board, dict, -turn_multiplier, depth - 1, -beta, -alpha)
        retract_move(board, dict)

        if score > best:
            best = score

        if score > alpha: alpha = score
        if alpha >= beta: break

    return best


def quiesce_search(board, dict, turn_multiplier, extension, alpha, beta):
    global NODES_SEARCHED

    if extension == 0:
        NODES_SEARCHED += 1
        return evaluate_board(board, dict, turn_multiplier) * turn_multiplier

    # Best move in a position can only result in an evaluation as good or better than stand_pat (null move principle)
    # so stand_pat is used as the lower bound
    NODES_SEARCHED += 1
    stand_pat = evaluate_board(board, dict, turn_multiplier) * turn_multiplier

    if stand_pat >= beta: return beta  # Fail-hard beta-cutoff
    if alpha < stand_pat: alpha = stand_pat  # New alpha


    # Should be made fast to check for any captures available
    best_score = stand_pat
    child_moves = get_valid_moves(board, dict)
    child_moves = move_ordering(child_moves)

    if dict['stale_mate']: return STALE_MATE
    elif dict['check_mate']: return -CHECK_MATE * turn_multiplier

    # I should also be looking at checks not just captures, should be using special method to just be able to yield
    # these kind of moves efficiently
    for move in child_moves:
        if move.piece_captured != 0 or move.en_passant:

            make_move(board, move, dict)
            score = -quiesce_search(board, dict, -turn_multiplier, extension - 1, -beta, -alpha)
            retract_move(board, dict)

            if score > best_score: best_score = score
            if score >= beta: return beta  # Fail-hard beta-cutoff
            if score > alpha: alpha = score  # New alpha

            return best_score

    # No search extensions were made as the position is quiet, so stand_pat is returned
    return stand_pat



########################################################################################################################
#                                               MOVER ORDERING FUNCTION                                                #
########################################################################################################################

## Aggressive move ordering to lead to great pruning is the way to really increase\
## the speed of the engine, focus on this until you cant anymore,

piece_indices = {1: 0, 900: 1, 500: 2, 330: 3, 320: 4, 100: 5, 0: 6,
                 -1: 0, -900: 1, -500: 2, -330: 3, -320: 4, -100: 5}


def move_ordering(moves):
    # The -1 ensures that all captures are looked at first before normal moves

    # Promotions dont seem to be really chaning the speed a lot, maybe even slowing down
    # As these matter only in the endgame
  #  promotions = []
 #   for move in moves:
 #       if move.promotion:
  #          moves.remove(move)
   #         promotions.append(move)

    score = [MVV_LLA_TABLE[piece_indices[move.piece_captured]][piece_indices[move.piece_moved]] for move in moves]
    combined = list(zip(moves, score))

    # Sort the combined list based on scores
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

    # Extract the sorted values
    moves = [tup[0] for tup in sorted_combined]
   # promotions.extend(moves)

    # for tup in sorted_combined:
    #     if tup[1] != 0:
    #         print(tup[0].get_pgn_notation(board), tup[1])

    return moves


#### Extra code I might need for inspiration for new stuff
'''### This is returns the same value wheter it is white or black perspective
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

'''
