import chess_engine
import timeit
import numpy as np
from collections import Counter

ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

DEPTH = 5
board = chess_engine.board
dict = chess_engine.general_dict

def perft(board, dict, depth):
    nodes = 0
    moves = chess_engine.get_all_valid_moves(board, dict)

    if depth == 1:
        all_moves.extend(moves)
        return len(moves)

    for move in moves:
        chess_engine.make_move(board, move, dict)
        nodes += perft(board, dict, depth - 1)
        chess_engine.undo_move(board, dict)

    return nodes

all_moves = []

list_of_parents = {}
def divide_perft(board, dict, depth):
  #  chess_engine.make_move(board, chess_engine.Move(52, 36, board),dict )
  #  chess_engine.make_move(board, chess_engine.Move(31, 23, board), dict)

    moves = chess_engine.get_all_valid_moves(board, dict)
    for move in moves:
        leafs = 0
        key = get_chess_notation((move.start_ind, move.end_ind))

        chess_engine.make_move(board, move, dict)
        leafs += (perft(board, dict, depth - 1))
        chess_engine.undo_move(board, dict)

        list_of_parents[key] = leafs

    tot = [ind for key, ind in list_of_parents.items()]
    return sum(tot)



def get_chess_notation(tuple):
    start, end = tuple
    start_row, start_col = start // 8, start % 8
    end_row, end_col = end // 8, end % 8

    first = cols_to_files[start_col] + rows_to_ranks[start_row]
    second = cols_to_files[end_col] + rows_to_ranks[end_row]
    return (first + second)
start = timeit.default_timer()
nodes = divide_perft(board, dict, DEPTH)
end = timeit.default_timer() - start
print(nodes, f'done in {end} seconds')

count =0
for move in all_moves:
    if move.en_passant:
        count +=1
print(count)


for key, value in list_of_parents.items():
    print(f'{key}: {value}')

'''go perft 4
e2e3: 3107 check
g2g3: 1014 check
a5a6: 3653 check 
e2e4: 2748 WRONG: 2792 is my value
g2g4: 3702 WRONG: 3614 is my value
b4b1: 4199 check
b4b2: 3328 check
b4b3: 3658 check
b4a4: 3019 check
b4c4: 3797 check
b4d4: 3622 check
b4e4: 3391 check
b4f4: 606 check
a5a4: 3394 check 

Nodes searched: 43238
'''

# Lets explore on these moves
# After doing e2 e4
'''go perft 3
f4f3: 174 t
d6d5: 171 F
c7c6: 179 F
c7c5: 167 F
h5b5: 52 False
h5c5: 180 t
h5d5: 176 t
h5e5: 168 t
h5f5: 180 t
h5g5: 191 t
h5h6: 161 t
h5h7: 172 False
h5h8: 205 False
h4g3: 178 t
h4g5: 195 t
h4g4: 199 t
'''