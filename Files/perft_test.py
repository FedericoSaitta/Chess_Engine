import chess_engine
import timeit
import numpy as np
from collections import Counter

ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

DEPTH = 4
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


import chess
import chess.engine

list_of_parents = {}
def divide_perft(board, dict, depth, parent_key='None'):
    nodes = 0
    moves = chess_engine.get_all_valid_moves(board, dict)

    if depth == 1:
        all_moves.extend(moves)
        return len(moves)

    for move in moves:
        nodes = 0
        if depth == DEPTH:
            key = get_chess_notation((move.start_ind, move.end_ind))
            list_of_parents[key] = 0
        else:
            key = parent_key

        chess_engine.make_move(board, move, dict)
        nodes += (divide_perft(board, dict, depth - 1, key))
        chess_engine.undo_move(board, dict)

        list_of_parents[key] += nodes

    return nodes



def get_chess_notation(tuple):
    start, end = tuple


    start_row, start_col = start // 8, start % 8
    end_row, end_col = end // 8, end % 8

    first = cols_to_files[start_col] + rows_to_ranks[start_row]
    second = cols_to_files[end_col] + rows_to_ranks[end_row]
    return (first + second)


start = timeit.default_timer()
nodes = perft(board, dict, DEPTH)
end = timeit.default_timer() - start
print(nodes, f'done in {end} seconds')

count =0
for move in all_moves:
    if move.en_passant:
        count +=1

print(count)
'''divide_perft(board, dict, DEPTH)



total = 0
for key, value in list_of_parents.items():
    total += value


print(total)'''




#print([print(key, value) for key,value in a.items()])
#print(count)



'''Seems to handle well the checkmates for both sides actually '''
'''Overshooting moves by 517'''

## I know that castling and simple piece capturing works


a = '''a2a3: 2186,
b2b3: 1964,
g2g3: 1882,
d5d6: 1991,
a2a4: 2149,
g2g4: 1843,
g2h3: 1970,
d5e6: 2241,
c3b1: 2038,
c3d1: 2040,
c3a4: 2203,
c3b5: 2138,
e5d3: 1803,
e5c4: 1880,
e5g4: 1878,
e5c6: 2027,
e5g6: 1997,
e5d7: 2124,
e5f7: 2080,
d2c1: 1963,
d2e3: 2136,
d2f4: 2000,
d2g5: 2134,
d2h6: 2019,
e2d1: 1733,
e2f1: 2060,
e2d3: 2050,
e2c4: 2082,
e2b5: 2057,
e2a6: 1907,
a1b1: 1969,
a1c1: 1968,
a1d1: 1885,
h1f1: 1929,
h1g1: 2013,
f3d3: 2005,
f3e3: 2174,
f3g3: 2214,
f3h3: 2360,
f3f4: 2132,
f3g4: 2169,
f3f5: 2396,
f3h5: 2267,
f3f6: 2111,
e1d1: 1894,
e1f1: 1855,
e1g1: 2059,
e1c1: 1887'''


