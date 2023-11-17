from math import fabs
from numba import njit

'''CONSTANTS needed for look-ups'''
N, S, E, W = -8, 8, 1, -1

ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

BISHOP_MOVES = [N + E, N + W, S + E, S + W]
ROOK_MOVES = [N, S, E, W]

KING_MOVES = [N, S, E, W,  # These are moves that look forwards
              N + E, N + W, S + E, S + W]  # These look diagonally

KNIGHT_MOVES = [N + N + E, N + N + W, S + S + E, S + S + W,
                N + E + E, N + W + W, S + E + E, S + W + W]

BISHOP_MOVES_tup = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
ROOK_MOVES_tup = [(1, 0), (-1, 0), (0, 1), (0, -1)]

KING_MOVES_tup = [(1, 0), (-1, 0), (0, 1), (0, -1),  # These are moves that look forwards
                  (-1, -1), (1, -1), (1, 1), (1, -1)]  # These look diagonally

KNIGHT_MOVES_tup = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

QUEEN_MOVES_tup = [(1, 1), (1, -1), (-1, 1), (-1, -1),  # Diagonal
                   (1, 0), (-1, 0), (0, 1), (0, -1)]  # Perpendicular


'''Here are the variables that will be re-assigned and changed during run time'''

board = [  # 1D Board                                     # Left right is +/- 1 and up and down is +/- 8
         -500, -293, -300, -900, -1, -300, -293, -500,    # 0 to 7
         -100, -100, -100, -100,-100,-100, -100, -100,    # 8 to 15
            0,    0,    0,    0,   0,   0,    0,   0,     # 16 to 23
            0,    0,    0,    0,   0,   0,    0,   0,     # 24 to 31
            0,    0,    0,    0,   0,   0,    0,   0,     # 32 to 39
            0,    0,    0,    0,   0,   0,    0,   0,     # 40 to 47
           100,  100,  100,  100, 100, 100,  100, 100,    # 48 to 55
           500,  293,  300,  900,  1,  300,  293, 500     # 56 to 63
        ]


white_to_move = True
move_log = []

white_king_loc = 60
black_king_loc = 4

check_mate, stale_mate = False, False
white_en_passant_sq, black_en_passant_sq = (None, None), (None, None)

def make_move(board, move): # Move will remain an object, this cannot be sped up by numba as it doesn't know Move objs.
    global white_to_move

    if move.piece_moved == 1:
        white_king_loc = (move.end_ind)
    elif move.piece_moved == -1:
        black_king_loc = (move.end_ind)

    '''Checks for possibility of enpassant'''
    if move.piece_moved == 100 or move.piece_moved == -100:
        if move.start_ind // 8 == 1 and move.end_ind // 8 == 3:
            black_en_passant_sq = (move.end_ind - 8)
        elif move.start_ind // 8 == 6 and move.end_ind // 8 == 4:
            white_en_passant_sq = (move.end_ind + 8)
    else:
        black_en_passant_sq, white_en_passant_sq = (None, None), (None, None)

    '''If the move is an en-passant'''
    if move.en_passant:
        if move.piece_moved > 0:
            board[move.end_ind + 8] = 0
        else:
            board[move.end_ind - 8] = 0

    board[move.start_ind] = 0
    board[move.end_ind] = move.piece_moved
    move_log.append(move)

    white_to_move = not white_to_move  # Swap the player's move

    return board

def undo_move(board):
    global white_to_move, black_en_passant_sq, white_en_passant_sq, white_king_loc, black_king_loc

    if len(move_log) > 0:
        move = move_log.pop()
        if move.en_passant:
            if move.piece_moved > 0:
                board[move.end_ind + 8] = -100
                black_en_passant_sq = (move.end_ind)

            else:
                board[move.end_ind - 8] = 100
                white_en_passant_sq = (move.end_ind)

        board[move.start_ind] = move.piece_moved
        board[move.end_ind] = move.piece_captured

        white_to_move = not white_to_move

        # Keep track of white_king loc and black one too if you implement this  # Doesnt yet work with castling

        if move.piece_moved == 1:
            white_king_loc = (move.start_ind)
        elif move.piece_moved == -1:
            black_king_loc = (move.start_ind)

    return board

def sq_under_attack(board, index):  # Determine if the enemy can attack the square (r, c)
        '''
        king_color = self.board[index][0]

        col = index % 8
        row = index // 8

        starttime = timeit.default_timer()

        for pos, tup in enumerate(QUEEN_MOVES_tup):
            if pos < 4:
                if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                    piece = self.board[8 * (row + tup[0]) + col + tup[1]]

                    if piece[0] == king_color:
                        continue
                    elif piece[1] == 'B' or piece[1] == 'Q':  # As these must be opposite coloured queens and bishops
                        return True
                    else:
                        for mul in range(2, 8):
                            if -1 < (row + (mul * tup[0])) < 8 and -1 < (col + (mul * tup[1])) < 8:
                                piece = self.board[8 * (row + mul * tup[0]) + col + mul * tup[1]]

                                if piece[0] == king_color:
                                    break
                                elif piece[1] == 'B' or piece[1] == 'Q':
                                    return True
                            else:
                                break
            else:
                if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:

                    piece = self.board[8 * (row + tup[0]) + col + tup[1]]

                    if piece[0] == king_color:
                        continue
                    elif piece[1] == 'Q' or piece[1] == 'R':
                        return True
                    else:
                        for mul in range(2, 8):
                            if -1 < (row + (mul * tup[0])) < 8 and -1 < (col + (mul * tup[1])) < 8:
                                piece = self.board[8 * (row + mul * tup[0]) + col + mul * tup[1]]
                                if piece[0] == king_color:
                                    break
                                elif piece[1] == 'Q' or piece[1] == 'R':
                                    return True
                            else:
                                break
        print(f"QBR validation:", timeit.default_timer() - starttime)

        starttime = timeit.default_timer()
        FOR
        THE
        KNIGHT
        MOVES
        for tup in KNIGHT_MOVES_tup:
            if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                piece = self.board[8 * (row + tup[0]) + col + tup[1]]
                if piece[0] != king_color and piece[1] == 'N':
                    return True

        print(f"KNIGHT validation:", timeit.default_timer() - starttime)
        starttime = timeit.default_timer()

        FOR
        THE
        PAWN
        MOVES
        white_squares = [(-1, 1), (-1, -1)]
        black_squares = [(1, 1), (1, -1)]

        if king_color == 'w':
            for tup in white_squares:
                if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                    ind = 8 * (row + tup[0]) + col + tup[1]
                    if self.board[ind] == 'bP':
                        return True

        else:
            for tup in black_squares:
                if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                    ind = 8 * (row + tup[0]) + col + tup[1]
                    if self.board[ind] == 'wP':
                        return True

        print(f"PAWN validation:", timeit.default_timer() - starttime)
        starttime = timeit.default_timer()


        for tup in KING_MOVES_tup:
            if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                ind = 8 * (row + tup[0]) + col + tup[1]

                if self.board[ind][0] != king_color and self.board[ind][1] == 'K':
                    return True

        print(f"KING validation:", timeit.default_timer() - starttime)'''

        return False

def in_check(board):
    global white_to_move, white_king_loc, black_king_loc

    if white_to_move:
        return sq_under_attack(board, white_king_loc)
    else:
        return sq_under_attack(board, black_king_loc)


def get_pawn_moves(board, ind):
    global white_en_passant_sq, black_en_passant_sq

    moves = []
    col = ind % 8
    row = ind // 8

    if board[ind] > 0:
        poss_moves = [(row - 1, col), (row - 1, col - 1), (row - 1, col + 1)]
    else:
        poss_moves = [(row + 1, col), (row + 1, col - 1), (row + 1, col + 1)]

    for index, tup in enumerate(poss_moves):
        if -1 < tup[0] < 8 and -1 < tup[1] < 8:
            square = 8 * tup[0] + tup[1]
            if index == 0:
                if board[square] == 0:
                    moves.append((ind, square, board))

                    if row == 1 and board[ind] < 0:  # Checking for double move
                        square = 8 * tup[0] + tup[1] + 8
                        if board[square] == 0:
                            moves.append((ind, square, board))

                    elif row == 6 and board[ind] > 0:
                        square = 8 * tup[0] + tup[1] - 8
                        if board[square] == 0:
                            moves.append((ind, square, board))
            else:
                if board[square] != board[ind] and board[square] != 0:
                    moves.append((ind, square, board))

#                elif board[ind] > 0:
#                    if square == black_en_passant_sq:
#                        moves.append((ind, square, board, en_passant=True))
#                    elif square == white_en_passant_sq:  # As the piece is definetely black
#                        moves.append((ind, square, board, en_passant=True))
    return moves


def sliding_pieces_moves(board, ind, MOVES):
    moves = []

    col = ind % 8
    row = ind // 8


    for tup in MOVES:
        if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
            square = 8 * (row + tup[0]) + (col + tup[1])
            if (board[square] != 0) and (board[square] > 0) == (board[ind] > 0):
                continue
            elif board[square] != 0:
                    moves.append((ind, square, board))
                    continue
            else:
                for mul in range(1, 8):
                    if -1 < (row + (mul * tup[0])) < 8 and -1 < (col + (mul * tup[1])) < 8:
                        square = 8 * (row + mul * tup[0]) + (col + mul * tup[1])
                        if (board[square] != 0) and (board[square] > 0) == (board[ind] > 0):
                            break
                        elif board[square] != 0:
                            moves.append((ind, square, board))
                            break
                        else:
                            moves.append((ind, square, board))
                    else:
                        break

    return moves

def get_knight_moves(board, ind):
    moves = []
    col = ind % 8
    row = ind // 8

    for tup in KNIGHT_MOVES_tup:
        if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
            square = 8 * (row + tup[0]) + (col + tup[1])
            if (board[square] == 0) or (board[square] >  0) != (board[ind] > 0):
                    moves.append((ind, square, board))

    return moves

def get_king_moves(board, ind):
    moves = []
    col = ind % 8
    row = ind // 8

    for tup in KING_MOVES_tup:
        if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
            square = 8 * (row + tup[0]) + (col + tup[1])
            if (board[square] == 0) or (board[square] >  0) != (board[ind] > 0):
                moves.append((ind, square, board))
    return moves

def get_all_possible_moves(board):
    global white_to_move
    moves = []

    for ind in range(64):
        if board[ind] == 0:
            continue

        if (board[ind] > 0 and white_to_move) or (board[ind] < 0 and not white_to_move):

            piece = fabs(board[ind])
            piece_col = 'w' if board[ind] > 0 else 'b'  # True for

            if piece == 100:
                moves.extend(get_pawn_moves(board, ind))
            elif piece == 500:
                moves.extend(sliding_pieces_moves(board, ind, ROOK_MOVES_tup))
            elif piece == 293:
                moves.extend(get_knight_moves(board, ind))
            elif piece == 300:
                moves.extend(sliding_pieces_moves(board, ind, BISHOP_MOVES_tup))
            elif piece == 900:
                moves.extend(sliding_pieces_moves(board, ind, ROOK_MOVES_tup))
                moves.extend(sliding_pieces_moves(board, ind,  BISHOP_MOVES_tup))
            elif piece == 1:
                moves.extend(get_king_moves(board, ind))

    moves = [Move(tup[0], tup[1], tup[2]) for tup in moves]
    return moves

def get_all_valid_moves(board):  # This will take into account non-legal moves that put our king in check

    global white_to_move, check_mate, stale_mate

    moves = get_all_possible_moves(board)

    for i in range(len(moves) - 1, -1, -1):  # Going backwards through loop
        board = make_move(board, moves[i])
        white_to_move = not white_to_move

        if in_check(board):
            moves.remove(moves[i])

        white_to_move = not white_to_move
        board = undo_move(board)

        if len(moves) == 0:
            if in_check():
                print(f'Check Mate on the Board, white wins: {not white_to_move}')
                check_mate = True
            else:
                print(f'We have a Stale Mate on the board, none wins')
                stale_mate = True
        else:
            check_mate, stale_mate = False, False

    return moves





class Move:

    __slots__ = ('start_ind', 'end_ind', 'move_ID',
                 'piece_moved', 'piece_captured', 'castle_move', 'en_passant')


    def __init__(self, start_sq, end_sq, board, castle_move=False, en_passant=False):

        self.start_ind = start_sq  # Tuple
        self.end_ind = end_sq  # Tuple

        # Similar idea to hash function
        self.move_ID = self.start_ind * 100 + self.end_ind
        self.piece_moved = board[self.start_ind]

        self.piece_captured = board[self.end_ind]

        self.castle_move = castle_move
        self.en_passant = en_passant

    def get_chess_notation(self, board):
        dict = {-100: 'bP', 100: 'wP', -500: 'bR', 500: 'wR', -300: 'bB', 300: 'wB',
                -293: 'bN', 293: 'wN', -900: 'bQ', 900: 'wQ', -1: 'bK', 1: 'wK'}

        piece = board[self.start_ind]
        start_rank_file = self.get_rank_file(self.start_ind)
        end_rank_file = self.get_rank_file(self.end_ind)

        if fabs(piece) == 100:
            if board[self.end_ind] != 0:
                return dict[piece][1:] + start_rank_file + ' x ' + end_rank_file

        if board[self.end_ind] != 0:
            return dict[piece][1:] + start_rank_file + ' x ' + end_rank_file

        return dict[piece][1:] + start_rank_file + ' to ' + end_rank_file

    def get_rank_file(self, index):
        c = index % 8
        r = index // 8
        return cols_to_files[c] + rows_to_ranks[r]

    def __eq__(self, other):  # Note the other move is the one stored in the valid_moves list
        if isinstance(other, Move):
            if (self.move_ID == other.move_ID) and other.castle_move:
                self.castle_move = True
                return True
            elif (self.move_ID == other.move_ID) and other.en_passant:
                self.en_passant = True
                return True

            elif (self.move_ID == other.move_ID):
                return True
        return False