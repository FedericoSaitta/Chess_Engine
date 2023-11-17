from math import fabs

import numpy as np

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


class GameState:
    __slots__ = ('board', 'white_to_move', 'moveLog', 'w_l_c', 'b_l_c',
                 'w_r_c', 'b_r_c', 'white_king_loc', 'black_king_loc',
                 'check_mate', 'stale_mate', 'white_en_passant_sq', 'black_en_passant_sq')

    def __init__(self):
        # Each element of 8x8 has two chars, first char represents colour of piece,
        # The second one represent the type of the piece
        # '--' represents that no piece is present
        self.board = [  # Switching to a 1D board representation    # Left right is +/- 1 and up and down is +/- 8
            -500, -293, -300, -900, -1, -300, -293, -500,    # 0 to 7
            -100, -100, -100, -100,-100,-100, -100, -100,    # 8 to 15
              0,    0,    0,    0,   0,   0,    0,    0,     # 16 to 23
              0,    0,    0,    0,   0,   0,    0,    0,     # 24 to 31
              0,    0,    0,    0,   0,   0,    0,    0,     # 32 to 39
              0,    0,    0,    0,   0,   0,    0,    0,     # 40 to 47
             100,  100,  100,  100, 100, 100,  100,  100,    # 0 to 7
             500,  293,  300,  900,  1,  300,  293,  500]

        self.white_to_move = True
        self.moveLog = []

        self.w_l_c, self.b_l_c = True, True  # Castling rights for white and black
        self.w_r_c, self.b_r_c = True, True

        self.white_king_loc = (60)  # Make sure to change these once you change to a new board
        self.black_king_loc = (4)
        self.check_mate, self.stale_mate = False, False

        self.white_en_passant_sq, self.black_en_passant_sq = (None, None), (None, None)

        # Here we will keep track of things such as right to castle etc.

    def make_move(self, move):  # This will not work for pawn promotion, en passant and castleling

        '''To keep location of both kings at all times'''
        if move.piece_moved == 1:
            self.white_king_loc = (move.end_ind)
        elif move.piece_moved == -1:
            self.black_king_loc = (move.end_ind)

        '''Checks for possibility of enpassant'''
        if move.piece_moved == 100 or move.piece_moved == -100:
            if move.start_ind // 8 == 1 and move.end_ind // 8 == 3:
                self.black_en_passant_sq = (move.end_ind - 8)
            elif move.start_ind // 8 == 6 and move.end_ind // 8 == 4:
                self.white_en_passant_sq = (move.end_ind + 8)
        else:
            self.black_en_passant_sq, self.white_en_passant_sq = (None, None), (None, None)

        '''If the move is an en-passant'''
        if move.en_passant:
            if move.piece_moved > 0:
                self.board[move.end_ind + 8] = 0
            else:
                self.board[move.end_ind - 8] = 0

        self.board[move.start_ind] = 0
        self.board[move.end_ind] = move.piece_moved
        self.moveLog.append(move)
        self.white_to_move = not self.white_to_move  # Swap the player's move

    def undo_move(self):  # To reverse a move
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()

            if move.en_passant:
                if move.piece_moved > 0:
                    self.board[move.end_ind + 8] = -100
                    self.black_en_passant_sq = (move.end_ind)

                else:
                    self.board[move.end_ind - 8] = 100
                    self.white_en_passant_sq = (move.end_ind)

            self.board[move.start_ind] = move.piece_moved
            self.board[move.end_ind] = move.piece_captured

            self.white_to_move = not self.white_to_move
            # Keep track of white_king loc and black one too if you implement this  # Doesnt yet work with castling

            if self.board[move.start_ind] == 1:
                self.white_king_loc = (move.start_ind)
            elif self.board[move.start_ind] == -1:
                self.black_king_loc = (move.start_ind)

    def get_all_valid_moves(self):  # This will take into account non-legal moves that put our king in check
        ''' As long as we switch turns an even number of times at the end we should be good'''

        moves = self.get_all_possible_moves()
        for i in range(len(moves) - 1, -1, -1):  # Going backwards through loop
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move

            if self.in_check():
                moves.remove(moves[i])

            self.white_to_move = not self.white_to_move
            self.undo_move()

        if len(moves) == 0:
            if self.in_check():
                print(f'Check Mate on the Board, white wins: {not self.white_to_move}')
                self.check_mate = True
            else:
                print(f'We have a Stale Mate on the board, none wins')
                self.stale_mate = True
        else:
            self.check_mate, self.stale_mate = False, False

        return moves

    def in_check(self):  # Determine if the current player is in check
        if self.white_to_move:
            return self.sq_under_attack(self.white_king_loc)
        else:
            return self.sq_under_attack(self.black_king_loc)


    def sq_under_attack(self, index):  # Determine if the enemy can attack the square (r, c)
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


    def get_all_possible_moves(self):  # This will generate all possible moves, some might not be legal due to opening up our king to check etc
        moves = []

        for ind in range(64):
            if self.board[ind] == 0:
                continue

            if (self.board[ind] > 0 and self.white_to_move) or (self.board[ind] < 0 and not self.white_to_move):

                piece = fabs(self.board[ind])
                piece_col = 'w' if self.board[ind] > 0 else 'b'  # True for

                if piece == 100:
                    self.get_pawn_moves(ind, moves)
                elif piece == 500:
                    self.sliding_pieces_moves(ind, moves, piece_col, ROOK_MOVES_tup)
                elif piece == 293:
                    self.get_knight_moves(ind, moves, piece_col)
                elif piece == 300:
                    self.sliding_pieces_moves(ind, moves, piece_col, BISHOP_MOVES_tup)
                elif piece == 900:
                    self.sliding_pieces_moves(ind, moves, piece_col, ROOK_MOVES_tup)
                    self.sliding_pieces_moves(ind, moves, piece_col, BISHOP_MOVES_tup)
                elif piece == 1:
                    self.get_king_moves(ind, moves, piece_col)

        return moves





    def get_pawn_moves(self, ind, moves_obj_list):
        board = self.board
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
                        moves_obj_list.append(Move(ind, square, board))

                        if row == 1 and self.board[ind] < 0:  # Checking for double move
                            square = 8 * tup[0] + tup[1] + 8
                            if board[square] == 0:
                                moves_obj_list.append((Move(ind, square, board)))

                        elif row == 6 and board[ind] > 0:
                            square = 8 * tup[0] + tup[1] - 8
                            if board[square] == 0:
                                moves_obj_list.append((Move(ind, square, board)))
                else:
                    if board[square] != board[ind] and board[square] != 0:
                        moves_obj_list.append((Move(ind, square, board)))

                    elif board[ind] > 0:
                        if square == self.black_en_passant_sq:
                            moves_obj_list.append((Move(ind, square, board, en_passant=True)))
                    elif square == self.white_en_passant_sq:     # As the piece is definetely black
                        moves_obj_list.append((Move(ind, square, board, en_passant=True)))

    def sliding_pieces_moves(self, ind, moves_obj_list, piece_col, MOVES):

        board = self.board

        col = ind % 8
        row = ind // 8

        colour = 'w' if board[ind] > 0 else 'b'
        for tup in MOVES:
            if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                square = 8 * (row + tup[0]) + (col + tup[1])
                if (board[square] != 0) and (board[square] > 0) == (board[ind] > 0):
                    continue
                elif board[square] != 0:
                    moves_obj_list.append(Move(ind, square, board))
                    continue
                else:
                    for mul in range(1, 8):
                        if -1 < (row + (mul * tup[0])) < 8 and -1 < (col + (mul * tup[1])) < 8:
                            square = 8 * (row + mul * tup[0]) + (col + mul * tup[1])
                            if (board[square] != 0) and (board[square] > 0) == (board[ind] > 0):
                                break
                            elif board[square] != 0:
                                moves_obj_list.append(Move(ind, square, board))
                                break
                            else:
                                moves_obj_list.append(Move(ind, square, board))
                        else:
                            break

    def get_knight_moves(self, ind, moves_obj_list, piece_col):
        col = ind % 8
        row = ind // 8
        colour = 'w' if self.board[ind] > 0 else 'b'
        for tup in KNIGHT_MOVES_tup:
            if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                square = 8 * (row + tup[0]) + (col + tup[1])
                if (self.board[square] == 0) or (self.board[square] >  0) != (self.board[ind] > 0):
                    moves_obj_list.append(Move(ind, square, self.board))

    def get_king_moves(self, ind, moves_obj_list, piece_col):
        col = ind % 8
        row = ind // 8

        for tup in KING_MOVES_tup:
            if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                square = 8 * (row + tup[0]) + (col + tup[1])
                if (self.board[square] == 0) or (self.board[square] >  0) != (self.board[ind] > 0):
                    moves_obj_list.append(Move(ind, square, self.board))


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