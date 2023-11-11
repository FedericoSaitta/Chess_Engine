# Stores information about current state of system, responsible for valid moves at the current state
# Will also keep a move log
# dskjfhsdf

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
        # Here we will keep track of things such as right to castle etc.


    def make_move(self, move): # This will not work for pawn promotion, en passant and castleling
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved

        self.moveLog.append(move)
        self.white_to_move = not self.white_to_move # Swap the player's move

    def undo_move(self): # To reverse a move
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

    def get_all_valid_moves(self): # This will take into account non-legal moves that put our king in check
        pass

    def get_all_possible_moves(self): # This will generate all possible moves, some might not be legal due to opening up our king to check etc
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                col_piece = self.board[r][c][0]
                if (col_piece == 'w' and self.white_to_move) or (col_piece == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        moves + (self.get_pawn_moves(r, c, moves))
                    elif piece == 'R':
                        self.get_rook_moves(r, c, moves)
                    elif piece == 'N':
                        self.get_knight_moves(r, c, moves)
                    elif piece == 'B':
                        self.get_bishop_moves(r, c, moves)
                    elif piece == 'Q':
                        self.get_queen_moves(r, c, moves)
                    elif piece == 'K':
                        self.get_king_moves(r, c, moves)
        for move in moves:
            print(move.get_chess_notation())
        return moves


    def get_pawn_moves(self, row, col, moves_obj_list):  # Can defo make this a lot smaller, there are
        if self.board[row][col][0] == 'w':               # smarter ways to do this, also a lot simpler probs

            if row == 6:
                if self.board[5][col] == '--':
                    moves_obj_list.append(Move((row,col), (row - 1, col), self.board))
                if self.board[4][col] == '--':
                    moves_obj_list.append(Move((row, col), (row - 2, col), self.board))
            else:
                if self.board[row - 1][col] == '--':
                    moves_obj_list.append(Move((row, col), (row - 1, col), self.board))

            if col != 7 and self.board[row - 1][col + 1][0] == 'b':
                moves_obj_list.append(Move((row, col), (row - 1, col+1), self.board))
            if col != 0 and self.board[row - 1][col - 1][0] == 'b':
                moves_obj_list.append(Move((row, col), (row - 1, col-1), self.board))

        elif self.board[row][col][0] == 'b':
            if row == 1:
                if self.board[1][col] == '--':
                    moves_obj_list.append(Move((row, col), (row + 1, col), self.board))
                if self.board[2][col] == '--':
                    moves_obj_list.append(Move((row, col), (row + 2, col), self.board))
            else:
                if self.board[row + 1][col] == '--':
                    moves_obj_list.append(Move((row, col), (row + 1, col), self.board))

            if col != 7 and self.board[row + 1][col + 1][0] == 'w':
                moves_obj_list.append(Move((row, col), (row + 1, col + 1), self.board))
            if col != 0 and self.board[row + 1][col - 1][0] == 'w':
                moves_obj_list.append(Move((row, col), (row + 1, col - 1), self.board))

        return moves_obj_list

    def get_rook_moves(self, row, col, moves_list):
        pass
    def get_knight_moves(self, row, col, moves_list):
        pass
    def get_bishop_moves(self, row, col, moves_list):
        pass
    def get_queen_moves(self, row, col, moves_list):
        pass
    def get_king_moves(self, row, col, moves_list):
        pass



class Move:
    ranks_to_rows = {'1':7, '2':6, '3':5, '4':4,
                     '5':3, '6':2, '7':1, '8':0}
    rows_to_ranks = {v: k for k,v in ranks_to_rows.items()} #  To reverse the dictionary

    files_to_cols = {'a':0, 'b':1, 'c':2, 'd':3,
                     'e':4, 'f':5, 'g':6, 'h':7 }
    cols_to_files = {v: k for k,v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        print(start_sq, end_sq)
        self.start_row, self.start_col = start_sq # Tuple
        self.end_row, self.end_col = end_sq # Tuple

        # Similar idea to hash function
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.piece_moved = board[self.start_row][self.start_col]

        self.piece_captured = board[self.end_row][self.end_col]

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + ' ' + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    def __eq__(self, other):
        if isinstance(other, Move):
            if (self.move_ID == other.move_ID):
                return True
        return False


