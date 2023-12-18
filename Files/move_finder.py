# Evaluates positions and searches moves
import chess_engine
from random import randint
from math import fabs
import timeit

# If when we score the board, positive values indicate white is winning
FABS = fabs
CHECK_MATE = 10_000
STALE_MATE = 0

PAWN_white = (0,  0,  0,  0,  0,  0,  0,  0,
          50, 50, 50, 50, 50, 50, 50, 50,
          10, 10, 20, 30, 30, 20, 10, 10,
           5,  5, 10, 25, 25, 10,  5,  5,
           0,  0,  0, 20, 20,  0,  0,  0,
           5, -5,-10,  0,  0,-10, -5,  5,
           5, 10, 10,-20,-20, 10, 10,  5,
           0,  0,  0,  0,  0,  0,  0,  0)

KNIGHT_white = ( -50,-40,-30,-30,-30,-30,-40,-50,
           -40,-20,  0,  0,  0,  0,-20,-40,
           -30,  0, 10, 15, 15, 10,  0,-30,
           -30,  5, 15, 20, 20, 15,  5,-30,
           -30,  0, 15, 20, 20, 15,  0,-30,
           -30,  5, 10, 15, 15, 10,  5,-30,
           -40,-20,  0,  5,  5,  0,-20,-40,
           -50,-40,-30,-30,-30,-30,-40,-50)

BISHOP_white = ( -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20)

ROOK_white = ( 0,  0,  0,  0,  0,  0,  0,  0,
              5, 10, 10, 10, 10, 10, 10,  5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
              0,  0,  0,  5,  5,  0,  0,  0)

QUEEN_white = (-20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                 -5,  0,  5,  5,  5,  5,  0, -5,
                  0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20)

KING_white = (-30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20)


PAWN_black = [-item for item in tuple(reversed(PAWN_white))]
KNIGHT_black = [-item for item in tuple(reversed(KNIGHT_white))]
BISHOP_black = [-item for item in tuple(reversed(BISHOP_white))]
ROOK_black = [-item for item in tuple(reversed(ROOK_white))]
QUEEN_black  = [-item for item in tuple(reversed(QUEEN_white))]
KING_black = [-item for item in tuple(reversed(KING_white))]


piece_sq_values = {100: PAWN_white, -100:PAWN_black,
                   320: KNIGHT_white, -320: KNIGHT_black,
                   330: BISHOP_white, -330: BISHOP_black,
                   500: ROOK_white, -500: ROOK_black,
                   900: QUEEN_white, -900: QUEEN_black,
                   1: KING_white, -1: KING_black}

NODES_SEARCHED = 0


def find_random_move(moves):
    if moves != []:
        index = randint(0, len(moves) - 1)
        return moves[index]
    else:
        return None


def root_negamax(moves, board, dict, DEPTH):
    global NODES_SEARCHED
    turn_multiplier = 1 if dict['white_to_move'] else -1
    max_score, best_move = -CHECK_MATE, None
    alpha, beta = -CHECK_MATE, CHECK_MATE

    for move in moves:
        chess_engine.make_move(board, move, dict)
        score = -negamax(board, dict, DEPTH - 1, -turn_multiplier, -beta, -alpha)
        chess_engine.undo_move(board, dict)

        if score > max_score:
            max_score, best_move = score, move

        if max_score > alpha:
            alpha = max_score

    if best_move is None:
        best_move = find_random_move(moves)

    print('Best move:', best_move.get_chess_notation(board), 'eval_bar:', max_score * turn_multiplier)
    print('Searched:', NODES_SEARCHED)
    NODES_SEARCHED = 0
    return best_move

def negamax(board, dict, depth, turn_multiplier, alpha, beta):
    global NODES_SEARCHED

    if depth == 0:
        NODES_SEARCHED += 1
        return evaluate_board(board, dict) * turn_multiplier

    moves = chess_engine.get_all_valid_moves(board, dict)
    best = -CHECK_MATE

    for move in moves:
        chess_engine.make_move(board, move, dict)
        score = -negamax(board, dict, depth - 1, -turn_multiplier, -beta, -alpha)
        chess_engine.undo_move(board, dict)

        if score > best:
            best = score

        if score > alpha:
            alpha = score

        if alpha >= beta:
            break

    return best


### This is returns the same value wheter it is white or black perspective, after the score is returned it should
### be multiplied by the turn multiplier
def evaluate_board(board, dict):

    ## Putting the dict here for now, will change later probs
    if dict['check_mate']: return CHECK_MATE
    elif dict['stale_mate']: return STALE_MATE
    else:
        eval_bar = 0
        index = 0

        for square in board:
            if square != 0:
                eval_bar += (piece_sq_values[square])[index]

            index += 1

        empty_squares = board.count(0)

        # We know we are in an endgame position
        if empty_squares > 32:
            pass

        eval_bar += sum(board)
        return eval_bar/100
