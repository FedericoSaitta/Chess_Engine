import chess_engine
import timeit
import cProfile
import pstats
from collections import Counter

ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

piece_dict = {100: 'p', 500: 'r', 300: 'b', 293: 'n', 900: 'q'}

DEPTH = 4
board = chess_engine.board
dict = chess_engine.general_dict
list_of_parents = {}


def perft(board, dict, depth):
    nodes = 0
    moves = chess_engine.get_all_valid_moves(board, dict)

    if depth == 1:
        return len(moves)

    for move in moves:
        chess_engine.make_move(board, move, dict)
        nodes += perft(board, dict, depth - 1)
        chess_engine.undo_move(board, dict)

    return nodes

def divide_perft(board, dict, depth): # This is slower, so should be used only for debugging
   # chess_engine.make_move(board, chess_engine.Move(11, 2, board, (False, False, (True, 900))), dict)
   # chess_engine.make_move(board, chess_engine.Move(53, 59, board), dict)
   # chess_engine.make_move(board, chess_engine.Move(57, 57 - 16 + 1, board), dict)
    moves = chess_engine.get_all_valid_moves(board, dict)
    #print(len(moves))
    for move in moves:
        leafs = 0
        key = get_chess_notation((move.start_ind, move.end_ind), move.prom_piece)

        chess_engine.make_move(board, move, dict)
        leafs += (perft(board, dict, depth - 1, key))
        chess_engine.undo_move(board, dict)

        list_of_parents[key] = leafs
    tot = [ind for key, ind in list_of_parents.items()]
    return sum(tot)

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


    start = timeit.default_timer()
    nodes = perft(board, dict, DEPTH)
    end = timeit.default_timer() - start

    print(f'Searched {nodes} nodes, in {end} seconds, Nodes per second: {int(nodes/end)}')

    for key, value in list_of_parents.items():
        print(f'{key}: {value}')


if __name__ == '__main__':
    with cProfile.Profile() as profile:

        main()
        profiler_stats = pstats.Stats(profile)
        specific_file = ('chess_engine.py')
        profiler_stats.strip_dirs().sort_stats('cumulative').print_stats(specific_file)
        # This only profiles the code if it hasnt been compiled in Cython



'''
['c8d6', 'c8b6', 'c8e7', 'c8a7', 'c4d3', 'c4b3', 'c4d5', 'c4e6', 'c4f7', 'c4b5', 'c4a6', 'a2a3', 'a2a4', 'b2b3', 
'b2b4', 'c2c3', 'e2f4', 'e2d4', 'e2g1', 'e2g3', 'e2c3', 'g2g3', 'g2g4', 'h2h3', 'h2h4', 'b1c3', 'b1a3', 'b1d2', 'c1d2', 
'c1e3', 'c1f4', 'c1g5', 'c1h6', 'e1f1', 'h1g1', 'h1f1'] 
36
'''

'''
go perft 3
a2a3: 1373
b2b3: 1368
c2c3: 1440
g2g3: 1308
h2h3: 1371
a2a4: 1433
b2b4: 1398
g2g4: 1337
h2h4: 1402
d7c8q: 1459 T   I get 1433
d7c8r: 1296 T
d7c8b: 1668 False
d7c8n: 1607 False Overdoing by 3
b1d2: 1174 
b1a3: 1303
b1c3: 1467
e2g1: 1431
e2c3: 1595
e2g3: 1523
e2d4: 1554
e2f4: 1555
c1d2: 1368
c1e3: 1587
c1f4: 1552
c1g5: 1422
c1h6: 1312
c4b3: 1275 False overdoing 1 
c4d3: 1269 False overdoing 1 
c4b5: 1332
c4d5: 1375
c4a6: 1256
c4e6: 1438
c4f7: 1328 False overdoing 1 
h1f1: 1364
h1g1: 1311
d1d2: 1436
d1d3: 1685
d1d4: 1751
d1d5: 1688
d1d6: 1500
e1f1: 1445
e1d2: 978
e1f2: 1269
e1g1: 1376

Nodes searched: 62379


d7c8q: 1459 T   I get 1433

go perft 2
c6c5: 52
a7a6: 51
b7b6: 52
f7f6: 52
g7g6: 51
h7h6: 51
a7a5: 51
b7b5: 51
f7f5: 50
g7g5: 50
h7h5: 51
f2d1: 43
f2h1: 47
f2d3: 5
f2h3: 48
f2e4: 50
f2g4: 48
b8a6: 52 T
b8d7: 48 False - 1
e7a3: 50
e7b4: 8
e7h4: 49
e7c5: 50
e7g5: 50
e7d6: 50
e7f6: 51
h8g8: 51
f8g8: 51
f8e8: 51
d8e8: 53 False -1
d8c8: 42

Nodes searched: 1459

'''