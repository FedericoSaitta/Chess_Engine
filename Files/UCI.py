import sys
from chess_engine import get_all_valid_moves, generate_from_FEN
from move_finder import iterative_deepening


ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

piece_dict = {100: 'p', 500: 'r', 330: 'b', 320: 'n', 900: 'q'}


THINKING_TIME = 2
engine_ID = 'id name Aquatic_Python'
author_ID = 'id author Federico Saitta'

'''IMPORTANT'''

def uci():
    print(engine_ID)
    print(author_ID)
    print("uciok")

def is_ready():
    print("readyok")

def position(fen):
    global board, dict
    dict, board = generate_from_FEN(fen)
    print(f"info string Setting position to: {fen}")
    return board, dict

def go(board, dict, Time):
    valid_moves = get_all_valid_moves(board, dict)
    move = iterative_deepening(valid_moves, board, dict, Time)

    move_notation = get_chess_notation((move.start_ind, move.end_ind), move.prom_piece)
    print(f"bestmove {move_notation}")

def get_chess_notation(tuple, prom_piece):
    start, end = tuple
    start_row, start_col = start // 8, start % 8
    end_row, end_col = end // 8, end % 8

    if prom_piece == None:
        first = cols_to_files[start_col] + rows_to_ranks[start_row]
        second = cols_to_files[end_col] + rows_to_ranks[end_row]
    else:
        piece = piece_dict[prom_piece]
        first = cols_to_files[start_col] + rows_to_ranks[start_row]
        second = cols_to_files[end_col] + rows_to_ranks[end_row] + piece

    return (first + second)


def main():
    while True:

        # Read input command
        line = sys.stdin.readline().strip()

        if line == "uci":
            uci()
        elif line == "isready":
            is_ready()
        elif line.startswith("position"):
            parts = line.split(" ")
            print(parts)
            fen = " ".join(parts[1:])
            position(fen)
        elif line.startswith("go"):
            go(board, dict, THINKING_TIME)

# You can make it start quicker probs by deleting some of those things that you dont need

# Make sure you are not in venv when building UCI though
# The line is: pyinstaller --onefile --add-data "opening_moves.txt:." UCI.py
# python3 lichess-bot.py -u

#curl -d '' https://lichess.org/api/bot/account/upgrade -H "Authorization: Bearer lip_w4fBPbSxTV2JZPpelmFg"





#lip_w4fBPbSxTV2JZPpelmFg
# Older one lip_vXt4JaI2OWkpqQUPaeq7
if __name__ == "__main__":
    main()
