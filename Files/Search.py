'''
This file is responsible for:
- Searching for the best move in the game tree with an iterative deepening approach
- Ordering moves by: Hash Move > 2 Killer Moves > MVV/LLA Sorted Moves > The Remaining Moves

Notes:
- Negamax with alpha beta allows to prune not so promising branches, ultimately the speed of the engine is determined
  by how many branches we explore to arrive at the best move, good move ordering is the most important factor.
- Quiescence search instead is needed to avoid 'Horizon Effect', this is key to an accurate evaluation of the board.

Resources:
- Horizon effect: https://www.chessprogramming.org/Horizon_Effect
- MVV/LLA Table, Killer Moves: https://rustic-chess.org/front_matter/title.html
- Negamax: https://en.wikipedia.org/wiki/Negamax
- Quiescence Search: https://www.dailychess.com/rival/programming/quiescence.php # This has a lot of good tips


Possible improvements:
- Try one or three Killer move approach
- Creating special generators for the quiescence search
- Applying History heuristics (note that your move ordering function isn't called that much so it is important that it is
  good
- Applying principal variation search

Failed improvements:
- Null Move pruning, I believe it is because my engine does not search to great depths
'''

from Board_state import make_move, undo_move, make_null_move, undo_null_move, Move
from Move_Generator import get_all_valid_moves, is_not_in_check
from random import randint
from math import fabs
from Evaluation import evaluate_board

from time import time # Needed to limit the Engine's thinking time

# My engine does not have null move pruning because after testing for quite a bit, it really doesn't improve performance
# it even makes it slightly worse. I hope im implementing right, but I think for shallow searching engines like mine
# null move pruning really doesn't do much.


# Renaming imports as variables in script leads to 10-15 % performance gain
FABS = fabs
push_move = make_move
retract_move = undo_move
get_valid_moves = get_all_valid_moves
Move = Move


MVV_LLA_TABLE = [
    [0, 0, 0, 0, 0, 0, 0],        # Victim K, 0's as it is checkmate already
    [50, 51, 52, 53, 54, 55, 0],  # victim Q, attacker K, Q, R, B, N, P
    [40, 41, 42, 43, 44, 45, 0],  # victim R, attacker K, Q, R, B, N, P
    [30, 31, 32, 33, 34, 35, 0],  # victim B, attacker K, Q, R, B, N, P
    [20, 21, 22, 23, 24, 25, 0],  # victim N, attacker K, Q, R, B, N, P
    [10, 11, 12, 13, 14, 15, 0],  # victim P, attacker K, Q, R, B, N, P
    [0, 0, 0, 0, 0, 0, 0]]        # No Victim


NODES_SEARCHED = 0
OPENING_DF, OUT_OF_BOOK = None, False
OPENING_REPERTOIRE_FILE = '/Users/federicosaitta/PycharmProjects/Chess/Files/Opening_repertoire.txt'

CHECK_MATE = 10_000
STALE_MATE = 0


# A table where the row represents the ply depth, note that killer moves are ordered after MVV/LLA moves.
# Killer moves are only updated in the negamax search, not the quiescence one as by definition killer moves are
# 'quiet' moves, and not captures or checks.
KILLER_MOVES_TABLE = [[None] * 2 for _ in range(20)]



# Methods to read and index the opening repertoire matrix, pandas is avoided to minimize size of executable file
def initialize_opening_repertoire(file_name):
    # Initializes the opening repertoire matrix, this is done when the first call to the search function is made,
    # it is not done at startup to minimize UCI executable start up time.
    return read_csv_to_matrix(open(file_name, 'r'))


def read_csv_to_matrix(file_obj):
    # Reads the data, removes the extra spaces at the end of the line, it splits each line into a subsequent list
    # using space as a delimeter.
    data_matrix = []
    for line in file_obj:
        line = line.strip('\n')
        line = line.split(' ')
        line.remove('')

        data_matrix.append(line)

    return data_matrix


def index_matrix(matrix, row_index, column):
    # Indexes a matrix, returns all the rows which have the same row_index found at the specified column index
    for i in range(len(matrix) -1, -1, -1):
        if matrix[i][column] != row_index:
            matrix.remove(matrix[i])


# Sometimes it starts looking at opening book moves even though it shouldn't
'''There is a problem with the opening book
   Please re-check this as im not sure if it working 100%
 '''
# Make sure that you make it turn off when the startpos is not the basic start position
def get_opening_book(board, moves, dict):
    global OPENING_DF, OUT_OF_BOOK

    if OPENING_DF is None: OPENING_DF = initialize_opening_repertoire(OPENING_REPERTOIRE_FILE)

    try:  # We look if the current position key is present in the data frame
        turn = len(dict['move_log'])
        if turn > 0:

            previous_move = (dict['move_log'][-1]).get_pgn_notation()
            previous_move_2 = (dict['move_log'][-1]).get_pgn_notation(multiple_piece_flag=True)

            OPENING_1 = OPENING_DF.copy()
            index_matrix(OPENING_DF, previous_move, turn-1)

            if OPENING_DF == []:
                index_matrix(OPENING_1, previous_move_2, turn-1)
                OPENING_DF = OPENING_1


            index = randint(0, len(OPENING_DF) - 1)
            move = OPENING_DF[index][TURN]
            move = get_move_from_notation(board, moves, move)


        else:  # We choose a random move from the starting possibilities
               # This only happens at start of the game from the start position so column = 0
            index = randint(0, len(OPENING_DF) - 1)
            move = OPENING_DF[index][0]
            move = get_move_from_notation(board, moves, move)

        TURN += 1
        return move

    except (KeyError, ValueError, AttributeError) as e :
        # Means we are out of book, so we return to finding a move with negamax
        OUT_OF_BOOK = True
        return None


ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}


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

    # Checks if there are multiple moves of the same type achieving the same square
    # So we flag them as multiple moves

    all_possible_notations = [move.get_pgn_notation() for move in moves]
    for move in moves:
        move_notation = move.get_pgn_notation()

        if all_possible_notations.count(move_notation) > 1:
            move_not = move.get_pgn_notation(multiple_piece_flag=True)
        else:
            move_not = move.get_pgn_notation()

        if move_not == notation:
            return move

    return None


########################################################################################################################
#                                                  MOVE SEARCH FUNCTION                                                #
########################################################################################################################

# Method needed because if our engine is completely loosing, no move is assigned to best_move so we choose at random
# from the available moves. In the future, we should aim to select the move that delays checkmate the most, hoping that
# our opponent misses mate. (Eg stockfish sacrificing lots of pieces when completely loosing)
def find_random_move(moves):
    if moves != []:
        index = randint(0, len(moves) - 1)
        return moves[index]


def iterative_deepening(moves, board, dict, time_constraints, debug_info=False):
    global NODES_SEARCHED
    best_move, DEPTH = None, 1
    turn_multiplier = 1 if dict['white_to_move'] else -1

    if (len(dict['move_log']) < 10) and (not OUT_OF_BOOK):
        best_move = get_opening_book(board, moves, dict)

    start_time = time()

    if best_move is None: # Means that we couldn't find an opening move
        moves = move_ordering(moves, 0) # Ply is 0 at the root

        while True:
        #    for index, list in enumerate(KILLER_MOVES_TABLE):
     #           if list != [None, None]:
     #               print(f'{index}: {list[0].get_pgn_notation()}, {list[1].get_pgn_notation()}')

            NODES_SEARCHED = 0
            best_move, best_score = negamax_root(moves, board, dict, turn_multiplier, DEPTH)

            if debug_info:
                if best_move is not None:
                    print('At depth: ', DEPTH, ' Best Move: ', best_move.get_pgn_notation(),
                          ' score: ', best_score * turn_multiplier, ' Searched: ', NODES_SEARCHED,
                          ' in: ', time() - start_time)


            # If we find a checkmate, we go for that branch and stop searching, this ensures we go for the fastest mate.

            # Try and remove the brackets and test it a bit
            if FABS(best_score) == CHECK_MATE: break

            if (time() - start_time > time_constraints): break

            ## Look for maybe faster way?? remove is quite heavy, not hugely but noticeably
            if best_move is not None:
                moves.remove(best_move)
                moves.insert(0, best_move)

            DEPTH += 1

    shift_killer_table() # Every time the turn changes we shift the killer move table upwards by 1
    if best_move is None: return find_random_move(moves)

    return best_move


def negamax_root(moves, board, dict, turn_multiplier, max_depth):
    best_score, best_move = -CHECK_MATE, None
    alpha, beta = -CHECK_MATE, CHECK_MATE

    # Note that the first set of parent moves have already been ordered
    for parent_move in moves:
    #    print('Parent move: ', move.get_pgn_notation(board))
        make_move(board, parent_move, dict)
        score = -negamax(board, dict, -turn_multiplier, max_depth - 1, -beta, -alpha, max_depth)
        retract_move(board, dict)

   #     print('Move: ', move.get_pgn_notation(board), ' score: ', score * turn_multiplier)

        if score > best_score:
            best_score, best_move = score, parent_move

        if best_score > alpha: alpha = best_score

        if alpha >= beta:
            ply = 0 # Ply is 0 by definition as we are in the root of negamax
            update_killer_moves_table(parent_move, ply)
            break

    return best_move, best_score

# This extension limit is really just to limit searching positions where perpetual checks are present,
# once proper Zobrist hashing is in place, no extension limit should be in place. (It is extremely unlikely to misjudge
# a position due to this limit)
EXTENSION = 20
def negamax(board, dict, turn_multiplier, depth, alpha, beta, max_depth):
    if depth == 0:
        return quiesce_search(board, dict, turn_multiplier, EXTENSION, alpha, beta)


    best = -CHECK_MATE
    moves = get_valid_moves(board, dict)
    parent_moves = move_ordering(moves, max_depth - depth)  # Ordering moves by MVV/LLA for more pruning

    # Done this way as I detect check or stalemate after all the moves have been retrieved
    # The checkmate is negated because if dict['check_mate'] == True that means we are in checkmate
    if dict['stale_mate']: return STALE_MATE
    if dict['check_mate']: return -CHECK_MATE

    for child in parent_moves:
  #      print('child move: ', child.get_pgn_notation(board))
        push_move(board, child, dict)
        score = -negamax(board, dict, -turn_multiplier, depth - 1, -beta, -alpha, max_depth)
        retract_move(board, dict)

        if score > best:
            best = score

        if score > alpha: alpha = score
        if alpha >= beta:
            # We have a beta-cut off so we store the move as a killer move
            ply = max_depth - depth
            update_killer_moves_table(child, ply)
            break

    return best


def quiesce_search(board, dict, turn_multiplier, extension, alpha, beta):
    global NODES_SEARCHED
    if extension == 0:
        NODES_SEARCHED += 1
        eval = evaluate_board(board) * turn_multiplier
        return eval

    # Best move in a position can only result in an evaluation as good or better than stand_pat (null move principle)
    # so stand_pat is used as the lower bound

    NODES_SEARCHED += 1
    stand_pat = evaluate_board(board) * turn_multiplier


    if stand_pat >= beta: return beta  # Fail-hard beta-cutoff
    if alpha < stand_pat: alpha = stand_pat  # New alpha


    child_moves = get_valid_moves(board, dict)
    child_moves = move_ordering(child_moves)

    if dict['stale_mate']: return STALE_MATE
    elif dict['check_mate']: return -CHECK_MATE

    # I should also be looking at checks not just captures, should be using special method to just be able to yield
    # these kind of moves efficiently
    for move in child_moves:
        if move.piece_captured != 0 or move.en_passant:

            make_move(board, move, dict)
            score = -quiesce_search(board, dict, -turn_multiplier, extension - 1, -beta, -alpha)
            retract_move(board, dict)

            if score > stand_pat: stand_pat = score
            if score >= beta: return beta  # Fail-hard beta-cutoff
            if score > alpha: alpha = score  # New alpha

            return stand_pat

    # No search extensions were made as the position is quiet, so stand_pat is returned
    return stand_pat



########################################################################################################################
#                                               MOVER ORDERING FUNCTION                                                #
########################################################################################################################

## Aggressive move ordering to lead to great pruning is the way to really increase\
## the speed of the engine, focus on this until you cant anymore,

piece_indices = {1: 0, 900: 1, 500: 2, 330: 3, 320: 4, 100: 5, 0: 6,
                 -1: 0, -900: 1, -500: 2, -330: 3, -320: 4, -100: 5}

# You should also check_collisions against the best_move already present in the position
def update_killer_moves_table(move, ply):
    # I should also see if the move doesn't result in check
    if move.piece_captured == 0: # Looking for quiet moves only
        if move not in KILLER_MOVES_TABLE[ply]:
            KILLER_MOVES_TABLE[ply][1] = KILLER_MOVES_TABLE[ply][0]
            KILLER_MOVES_TABLE[ply][0] = move

def shift_killer_table():
    KILLER_MOVES_TABLE.pop(0)
    KILLER_MOVES_TABLE.append([None, None])



# Using -1 ply for quiescence search only, should be reframed back to normal once special generator is made for that search
def move_ordering(moves, ply=-1):
    # The -1 ensures that all captures are looked at first before normal moves

    # Promotions dont seem to be really changing the speed a lot, maybe even slowing down
    # As these matter only in the endgame
  #  promotions = []
 #   for move in moves:
 #       if move.promotion:
 #           moves.remove(move)
   #         promotions.append(move)

    # This is because different objects are created
    for move in KILLER_MOVES_TABLE[ply]:
        if move is not None:
            for diff_move in moves:
                if diff_move == move:
                    diff_move.killer_move = True

        # Check if there are collisions happening

#    we give killer moves a score of 1, meaning that they are ranked above quiet moves, but below 'bad captures'
    score = [MVV_LLA_TABLE[piece_indices[move.piece_captured]][piece_indices[move.piece_moved]] if not move.killer_move
             else 1 for move in moves]

    combined = list(zip(moves, score))

    # Sort the combined list based on scores
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

    # Extract the sorted values
    moves = [tup[0] for tup in sorted_combined]
   # promotions.extend(moves)

 #   print(f'last pass at depth: {ply}')
#    for tup in sorted_combined:
   #     print(tup[0].get_pgn_notation(), tup[1])

    return moves