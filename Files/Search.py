from Board_state import make_move, undo_move, make_null_move, undo_null_move, Move
from Move_Generator import get_all_valid_moves
from random import randint
from math import fabs
from Evaluation import evaluate_board

from time import time # Needed to limit the Engine's thinking time

# Renaming imports as variables in script gains 10-15 % performance gain
FABS = fabs
push_move = make_move
retract_move = undo_move
get_valid_moves = get_all_valid_moves
Move = Move

## Taken from https://rustic-chess.org/front_matter/title.html, Marcel Vanthoor
MVV_LLA_TABLE = [
    [0, 0, 0, 0, 0, 0, 0],        # Victim K, 0's as it is checkmate already
    [50, 51, 52, 53, 54, 55, 0],  # victim Q, attacker K, Q, R, B, N, P
    [40, 41, 42, 43, 44, 45, 0],  # victim R, attacker K, Q, R, B, N, P
    [30, 31, 32, 33, 34, 35, 0],  # victim B, attacker K, Q, R, B, N, P
    [20, 21, 22, 23, 24, 25, 0],  # victim N, attacker K, Q, R, B, N, P
    [10, 11, 12, 13, 14, 15, 0],  # victim P, attacker K, Q, R, B, N, P
    [0, 0, 0, 0, 0, 0, 0]]        # No Victim


NODES_SEARCHED, TURN = 0, 0
OPENING_DF, OUT_OF_BOOK = None, False
OPENING_REPERTOIRE_FILE = '/Users/federicosaitta/PycharmProjects/Chess/Files/Opening_repertoire.txt'

CHECK_MATE = 10_000
STALE_MATE = 0


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
    # Traverses the list backwards to avoid index collisions when removing rows
        if matrix[i][column] != row_index:
            # Looks at each element in a specific column in a matrix, if it doesn't match we remove said row
            matrix.remove(matrix[i])


def get_opening_book(board, moves, dict):
    global OPENING_DF, TURN, OUT_OF_BOOK

    if OPENING_DF is None: OPENING_DF = initialize_opening_repertoire(OPENING_REPERTOIRE_FILE)

    try:  # We look if the current position key is present in the data frame
        if len(dict['move_log']) > 0:

            if (not dict['white_to_move']) and (TURN % 2 == 0): TURN += 1
            # Increments the Turn variable if engine plays against a human

            previous_move = (dict['move_log'][-1]).get_pgn_notation(board)
            previous_move_2 = (dict['move_log'][-1]).get_pgn_notation(board, multiple_piece_flag=True)

            OPENING_1 = OPENING_DF.copy()
            index_matrix(OPENING_DF, previous_move, TURN-1)

            if OPENING_DF == []:
                index_matrix(OPENING_1, previous_move_2, TURN-1)
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
        print(e)
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
def find_random_move(moves):
    if moves != []:
        index = randint(0, len(moves) - 1)
        return moves[index]
    else:
        return None


def iterative_deepening(moves, board, dict, time_constraints):
    global NODES_SEARCHED
    best_move, DEPTH = None, 1
    turn_multiplier = 1 if dict['white_to_move'] else -1

    if (len(dict['move_log']) < 10) and not OUT_OF_BOOK:
        best_move = get_opening_book(board, moves, dict)

    start_time = time()

    if best_move is None:
        moves = move_ordering(moves)

        while True:
            NODES_SEARCHED = 0
            best_move, best_score = negamax_root(moves, board, dict, turn_multiplier, DEPTH)

            if best_score == CHECK_MATE: break

            if (time() - start_time > time_constraints) or DEPTH == 15:
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
    alpha, beta = -CHECK_MATE, CHECK_MATE

    # Note with alpha beta pruning some moves will have the same evaluation but that is because they are
    # moves whose nodes have been pruned.

    for move in moves:
    #    print('Parent move: ', move.get_pgn_notation(board))
        # One is subtracted by the depth as we are looking at parent moves already
        make_move(board, move, dict)
        score = -negamax(board, dict, -turn_multiplier, depth - 1, -beta, -alpha)
        retract_move(board, dict)

        print('Move: ', move.get_pgn_notation(board), ' score: ', score * turn_multiplier)

        if score > best_score:
            best_score = score
            best_move = move

        if best_score > alpha: alpha = best_score
        if alpha >= beta: break

    if best_move is not None:
        print('At depth: ', depth, ' Best Move: ', best_move.get_pgn_notation(board),
              ' score: ', best_score * turn_multiplier, ' Searched: ', NODES_SEARCHED)

    return best_move, best_score

# This extension limit is really just to limit searching positions where perpetual checks are present,
# once proper Zobrist hashing is in place, no extension limit should be in place. (It is extremely unlikely to misjudge
# a position due to this limit)
EXTENSION = 6
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
    if dict['check_mate']: return -CHECK_MATE * turn_multiplier


    # The theory is that if your opponent could make two consecutive moves and not
    # improve his position, you must have an overwhelming advantage

    # Note that this will activate for searches at depth 3
 ######  # This does not work as you are only able to detect check on the next turn, it is probably a good idea to fix that

    # Try this one proper in check condition is in place
#    if depth > 2 and (not dict['in_check']):

        # Beta window is + 1.5
 #       make_null_move(dict)
 #       null_move_score = -negamax(board, dict, -turn_multiplier, depth - 2, -beta, -beta+1)
 #       undo_null_move(dict)

 #       if null_move_score >= beta:
  #          return null_move_score  # Null move pruning

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
