# Stores information about current state of system, responsible for valid moves at the current state
# Will also keep a move log
# dskjfhsdf

class GameState:
    def __init__(self):
        # Each element of 8x8 has two chars, first char represents colour of piece,
        # The second one represent the type of the piece
        # '--' represents that no piece is present
        # sdwer

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


    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved

        self.moveLog.append(move)
        self.white_to_move = not self.white_to_move # Swap the player's move


class Move:
    ranks_to_rows = {'1':7, '2':6, '3':5, '4':4,
                     '5':3, '6':2, '7':1, '8':0 }
    rows_to_ranks = {v: k for k,v in ranks_to_rows.items()} #  To reverse the dictionary

    files_to_cols = {'a':0, 'b':1, 'c':2, 'd':3,
                     'e':4, 'f':5, 'g':6, 'h':7 }
    cols_to_files = {v: k for k,v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        print(start_sq, end_sq)
        self.start_row, self.start_col = start_sq # Tuple
        self.end_row, self.end_col = end_sq # Tuple

        self.piece_moved = board[self.start_row][self.start_col]

        self.piece_captured = board[self.end_row][self.end_col]

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + ' ' + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

