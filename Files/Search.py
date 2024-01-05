'''
This file is responsible for:
- Searching for the best move in the game tree with an iterative deepening approach
- Ordering moves by: Hash Move > 2 Killer Moves > MVV/LLA Sorted Moves > The Remaining Moves

Notes:
- In a chess engine the Search module is where the greatest improvements and mistakes can be made, tuning to allow for
  the most amount of pruning while retaining accuracy should be the programmer's no.1 task.
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
from Opening_book import get_opening_book


from time import time # Needed to limit the Engine's thinking time


# Renaming imports as variables in script leads to 10-15 % performance gain
FABS = fabs
push_move = make_move
retract_move = undo_move
get_valid_moves = get_all_valid_moves
Move = Move
get_opening_book = get_opening_book


MVV_LLA_TABLE = [
    [0, 0, 0, 0, 0, 0, 0],        # Victim K, 0's as it is checkmate already
    [50, 51, 52, 53, 54, 55, 0],  # victim Q, attacker K, Q, R, B, N, P
    [40, 41, 42, 43, 44, 45, 0],  # victim R, attacker K, Q, R, B, N, P
    [30, 31, 32, 33, 34, 35, 0],  # victim B, attacker K, Q, R, B, N, P
    [20, 21, 22, 23, 24, 25, 0],  # victim N, attacker K, Q, R, B, N, P
    [10, 11, 12, 13, 14, 15, 0],  # victim P, attacker K, Q, R, B, N, P
    [0, 0, 0, 0, 0, 0, 0]]        # No Victim


NODES_SEARCHED = 0
OUT_OF_BOOK = False


CHECK_MATE = 10_000
STALE_MATE = 0


# A table where the row represents the ply depth, note that killer moves are ordered after MVV/LLA moves.
# Killer moves are only updated in the negamax search, not the quiescence one as by definition killer moves are
# 'quiet' moves, and not captures or checks.
KILLER_MOVES_TABLE = [[None] * 2 for _ in range(20)]


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


'''Problem it is that it doesnt try and avoid checkmate, this is probs due to scores confliciting or not being assigned'''
def iterative_deepening(moves, board, dict, time_constraints, debug_info=True):
    global NODES_SEARCHED, OUT_OF_BOOK

    best_move, DEPTH = None, 1
    turn_multiplier = 1 if dict['white_to_move'] else -1
    hash_move = None

    if (len(dict['move_log']) < 10) and (not OUT_OF_BOOK):
        if ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq') in dict['starting_FEN']:
            best_move = get_opening_book(board, moves, dict)
            if best_move is None:
                OUT_OF_BOOK = True
                if debug_info: print('Out of Opening Book')

    start_time = time()

    if best_move is None: # Means that we couldn't find an opening move
        moves = move_ordering(moves, hash_move, ply=0) # Ply is 0 at the root

        while True:

            NODES_SEARCHED = 0
            best_move, best_score = negamax_root(moves, board, dict, turn_multiplier, DEPTH)

            if debug_info:
                if best_move is not None:
                    print('At depth: ', DEPTH, ' Best Move: ', best_move.get_pgn_notation(),
                          ' score: ', best_score * turn_multiplier, ' Searched: ', NODES_SEARCHED,
                          ' in: ', time() - start_time, 'SPEED: ', NODES_SEARCHED / (time() - start_time))

            # If we find a checkmate, we go for that branch and stop searching, this ensures we go for the fastest mate.

            # Try and remove the brackets and test it a bit
            if FABS(best_score) == CHECK_MATE: break

            if (time() - start_time > time_constraints): break

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
    parent_moves = move_ordering(moves, ply= max_depth - depth)  # Ordering moves by MVV/LLA for more pruning

    # Done this way as I detect check or stalemate after all the moves have been retrieved
    # The checkmate is negated because if dict['check_mate'] == True that means we are in checkmate
    if dict['stale_mate']: return STALE_MATE
    if dict['check_mate']: return -CHECK_MATE

    for child in parent_moves:
  #      print('child move: ', child.get_pgn_notation(board))
        push_move(board, child, dict)
        score = -negamax(board, dict, -turn_multiplier, depth - 1, -beta, -alpha, max_depth)
        retract_move(board, dict)

        if score > best: best = score
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
    if (move.piece_captured == 0) and (not move.en_passant): # Looking for quiet moves only
        if move not in KILLER_MOVES_TABLE[ply]:
            KILLER_MOVES_TABLE[ply][1] = KILLER_MOVES_TABLE[ply][0]
            KILLER_MOVES_TABLE[ply][0] = move

def shift_killer_table():
    KILLER_MOVES_TABLE.pop(0)
    KILLER_MOVES_TABLE.append([None, None])


# Using -1 ply for quiescence search only, should be reframed back to normal once special generator is made for that search

# Move ordering should be:
'''
# Not sure if killer moves should go before or after MVV/LLA
- Hash Move
- Promotions
- MVV_LLA
- Killer Moves 
- Other moves sorted with history heuristics'
'''
# Passing the hash_move like this so we don't have to remove it and re-insert it manually each time
def move_ordering(moves, hash_move=None, ply=-1):

    # This is twice as slow but it is working correctly
    scores = []
    killer_1, killer_2 = KILLER_MOVES_TABLE[ply]

    for move in moves:
        if move == hash_move:
            scores.append(1_000)
        elif move == killer_1 or move == killer_2:
            scores.append(2)

        elif move.promotion: scores.append(100)

        else: scores.append(MVV_LLA_TABLE[piece_indices[move.piece_captured]][piece_indices[move.piece_moved]])


    combined = list(zip(moves, scores))

    # Sort the combined list based on scores
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

    # Extract the sorted values
    moves = [tup[0] for tup in sorted_combined]
   # promotions.extend(moves)

 #   print(f'last pass at depth: {ply}')
#    for tup in sorted_combined:
   #     print(tup[0].get_pgn_notation(), tup[1])

    return moves