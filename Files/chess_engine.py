# Stores information about current state of system, responsible for valid moves at the current state
# Will also keep a move log
# dskjfhsdf
import numpy
import numpy as np

BISHOP_MOVES = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
ROOK_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
KING_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1),
              (1, 1), (1, -1), (-1, 1), (-1, -1)]




class GameState:
    def __init__(self):
        # Each element of 8x8 has two chars, first char represents colour of piece,
        # The second one represent the type of the piece
        # '--' represents that no piece is present

        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.white_to_move = True
        self.moveLog = []

        self.w_l_c, self.b_l_c = True, True # Castling rights for white and black
        self.w_r_c, self.b_r_c = True, True

        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.check_mate, self.stale_mate = False, False

        # Here we will keep track of things such as right to castle etc.

    def make_move(self, move): # This will not work for pawn promotion, en passant and castleling

        if move.piece_moved == 'wK':
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.end_row, move.end_col)

        '''if move.castle_move:
            if move.end_col == 2:  # For left castle
                if move.end_row == 7:  # For white
                    self.board[7][0] = '--'
                    self.board[7][3] = 'wR'
                    self.w_l_c = self.w_r_c = False
                elif move.end_row == 0:  # For black
                    self.board[0][0] = '--'
                    self.board[0][3] = 'bR'
                    self.b_l_c = self.w_r_c = False

            if move.end_col == 6:  # For right castle
                if move.end_row == 7:
                    self.board[7][7] = '--'
                    self.board[7][5] = 'wR'
                    self.w_l_c = self.w_r_c = False
                elif move.end_row == 0:
                    self.board[0][7] = '--'
                    self.board[0][5] = 'bR'
                    self.b_l_c = self.w_r_c = False'''


        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move)

        '''if self.w_r_c or self.w_l_c or self.b_l_c or self.b_r_c:
            if self.board[move.start_row][move.start_col][1] == 'K':
                if self.white_to_move:
                    self.w_l_c, self.w_r_c = False, False
                else:
                    self.b_l_c, self.b_r_c = False, False

            if self.board[move.start_row][move.start_col][1] == 'R':
                if self.white_to_move:
                    if move.start_col == 0:
                        self.w_l_c = False
                    elif move.start_col == 7:
                        self.w_r_c = False
                else:
                    if move.start_col == 0:
                        self.w_l_c = False
                    elif move.start_col == 7:
                        self.w_r_c = False'''

        self.white_to_move = not self.white_to_move # Swap the player's move

    def undo_move(self): # To reverse a move
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()

            '''if move.castle_move:
                if move.end_col == 6 and move.end_row == 7:
                    self.w_r_c = True
                    self.board[7][7] = 'wR'
                    self.board[7][5] = '--'

                elif move.end_col == 6 and move.end_row == 0:
                    self.b_r_c = True
                    self.board[0][7] = 'bR'
                    self.board[0][5] = '--'

                elif move.end_col == 2 and move.end_row == 0:
                    self.b_l_c = True
                    self.board[0][0] = 'bR'
                    self.board[0][3] = '--'

                elif move.end_col == 2 and move.end_row == 7:
                    self.w_l_c = True
                    self.board[7][0] = 'wR'
                    self.board[7][3] = '--' '''

            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # Keep track of white_king loc and black one too if you implement this  # Doesnt yet work with castling

            if self.board[move.start_row][move.start_col] == 'wK':
                self.white_king_loc = (move.start_row, move.start_col)
            elif self.board[move.start_row][move.start_col] == 'bK':
                self.black_king_loc = (move.start_row, move.start_col)





    def get_all_valid_moves(self): # This will take into account non-legal moves that put our king in check
        ''' As long as we switch turns an even number of times at the end we should be good'''

        moves =  self.get_all_possible_moves()
        for i in range(len(moves) - 1, -1, -1): # Going backwards through loop
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

    def in_check(self): # Determine if the current player is in check
        if self.white_to_move:
            return self.sq_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.sq_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def sq_under_attack(self, r, c): # Determine if the enemy can attack the square (r, c)

        self.white_to_move = not self.white_to_move
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move

        for move in opp_moves:
            if (move.end_row == r) and (move.end_col == c):
                return True
        return False


    def get_all_possible_moves(self): # This will generate all possible moves, some might not be legal due to opening up our king to check etc
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                col_piece = self.board[r][c][0]
                if (col_piece == 'w' and self.white_to_move) or (col_piece == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        self.get_pawn_moves(r, c, moves)
                    elif piece == 'R':
                        self.sliding_pieces_moves(r, c, moves, ROOK_MOVES)
                    elif piece == 'N':
                        self.get_knight_moves(r, c, moves)
                    elif piece == 'B':
                        self.sliding_pieces_moves(r, c, moves, BISHOP_MOVES)
                    elif piece == 'Q':
                        self.sliding_pieces_moves(r, c, moves, ROOK_MOVES)
                        self.sliding_pieces_moves(r, c, moves, BISHOP_MOVES)
                    elif piece == 'K':
                        self.get_king_moves(r, c, moves)

        return moves

# Piece functions dont need to return anything as they are just appending
    def get_pawn_moves(self, row, col, moves_obj_list):
        piece_color = self.board[row][col][0]

        if piece_color == 'w':
            poss_moves = [(row - 1, col), (row -  1, col -1), (row - 1, col + 1)]
        else:
            poss_moves = [(row + 1, col), (row +  1, col -1), (row + 1, col + 1)]

        for index, tup in enumerate(poss_moves):
            if -1 < tup[0] < 8 and -1 < tup[1] < 8:
                if index == 0:
                    if self.board[tup[0]][tup[1]] == '--':
                        moves_obj_list.append(Move((row, col), tup, self.board))

                        if row == 1 and piece_color == 'b': # Checking for double move
                            if self.board[row + 2][col] == '--':
                                moves_obj_list.append(Move((row, col), (row + 2, col), self.board))

                        elif row == 6 and piece_color == 'w':
                            if self.board[row - 2][col] == '--':
                                moves_obj_list.append(Move((row, col), (row - 2, col), self.board))
                else:
                    if self.board[tup[0]][tup[1]][0] != piece_color and self.board[tup[0]][tup[1]] != '--':
                        moves_obj_list.append(Move((row, col), tup , self.board))


    def sliding_pieces_moves(self, row, col, moves_obj_list, MOVES): # This does not consider castling

        piece_color = self.board[row][col][0]
        for tup in MOVES:
            if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                if self.board[row + tup[0]][col + tup[1]][0] == piece_color:
                    continue
                elif self.board[row + tup[0]][col + tup[1]] != '--':
                    moves_obj_list.append(Move((row, col), (row + tup[0], col + tup[1]), self.board))
                    continue
                else:
                    for mul in range(1, 8):
                        if -1 < (row + (mul * tup[0])) < 8 and -1 < (col + (mul * tup[1])) < 8:
                            if self.board[row + (mul * tup[0])][col + (mul * tup[1])][0] == piece_color:
                                break
                            elif self.board[row + (mul * tup[0])][col + (mul * tup[1])] != '--':
                                moves_obj_list.append(Move((row, col), (row + mul * tup[0], col + mul * tup[1]), self.board))
                                break
                            else:
                                moves_obj_list.append(Move((row, col), (row + mul * tup[0], col + mul * tup[1]), self.board))
                        else:
                            break

    def get_knight_moves(self, row, col, moves_obj_list):
        possible_moves = [(row + 2, col + 1), (row + 2, col - 1), (row - 2, col + 1), (row - 2, col - 1),
                         (row + 1, col + 2), (row + 1, col - 2), (row - 1, col + 2), (row - 1, col - 2)]
        color = self.board[row][col][0]

        for tup in possible_moves:
            if -1 < tup[0] < 8 and -1 < tup[1] < 8:
                if self.board[tup[0]][tup[1]][0] != color:
                    moves_obj_list.append(Move((row, col), (tup[0], tup[1]), self.board))

    def get_king_moves(self, row, col, moves_obj_list):
        piece_color = self.board[row][col][0]
        for tup in KING_MOVES:
            if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
                if self.board[row + tup[0]][col + tup[1]][0] != piece_color:
                    moves_obj_list.append(Move((row, col), (row + tup[0], col + tup[1]), self.board))

        # Castling check

        '''if self.board[row][col][0] == 'w':
            if self.w_l_c and self.board[row][1:4] == ['--', '--' ,'--']:
                moves_obj_list.append(Move((row, col), (row, col - 2), self.board, castle_move=True))
            if self.w_r_c and self.board[row][5:7] == ['--', '--']:
                moves_obj_list.append(Move((row, col), (row, col + 2), self.board, castle_move=True))


        elif self.board[row][col][0] == 'b':
            if self.b_l_c and self.board[row][1:4] == ['--', '--', '--']:
                moves_obj_list.append(Move((row, col), (row, col - 2), self.board, castle_move=True))
            if self.b_r_c and self.board[row][5:7] == ['--', '--']:
                moves_obj_list.append(Move((row, col), (row, col + 2), self.board, castle_move=True))'''



class Move:
    ranks_to_rows = {'1':7, '2':6, '3':5, '4':4,
                     '5':3, '6':2, '7':1, '8':0}
    rows_to_ranks = {v: k for k,v in ranks_to_rows.items()} #  To reverse the dictionary

    files_to_cols = {'a':0, 'b':1, 'c':2, 'd':3,
                     'e':4, 'f':5, 'g':6, 'h':7 }
    cols_to_files = {v: k for k,v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, castle_move=False):
        self.start_row, self.start_col = start_sq # Tuple
        self.end_row, self.end_col = end_sq # Tuple

        # Similar idea to hash function
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.piece_moved = board[self.start_row][self.start_col]

        self.piece_captured = board[self.end_row][self.end_col]

        self.castle_move = castle_move



    def get_chess_notation(self, board):
        piece = board[self.start_row][self.start_col][1]
        start_rank_file = self.get_rank_file(self.start_row, self.start_col)
        end_rank_file = self.get_rank_file(self.end_row, self.end_col)

        if piece == 'P':
            if board[self.end_row][self.end_col] != '--':
                return piece + start_rank_file + ' x ' + end_rank_file

        if board[self.end_row][self.end_col] != '--':
            return piece + start_rank_file + ' x ' + end_rank_file

        return piece + start_rank_file + ' to ' + end_rank_file

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    def __eq__(self, other):  # Note the other move is the one stored in the valid_moves list
        if isinstance(other, Move):
            if (self.move_ID == other.move_ID) and other.castle_move:
                self.castle_move = True
                return True
            elif (self.move_ID == other.move_ID):
                return True
        return False