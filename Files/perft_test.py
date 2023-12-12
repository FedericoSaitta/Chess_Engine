import chess_engine
import timeit
import cProfile
import pstats
from collections import Counter

ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

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
   # chess_engine.make_move(board, chess_engine.Move(28, 43, board), dict)
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

def main():


    start = timeit.default_timer()
    nodes = perft(board, dict, DEPTH)
    end = timeit.default_timer() - start

    print(f'Searched {nodes} nodes, in {end} seconds, Nodes per second: {int(nodes/end)}')

   # for key, value in list_of_parents.items():
        #print(f'{key}: {value}')


if __name__ == '__main__':
    with cProfile.Profile() as profile:
        for i in range(5):
            main()
        profiler_stats = pstats.Stats(profile)
        specific_file = ('chess_engine.py')
        profiler_stats.strip_dirs().sort_stats('cumulative').print_stats(specific_file)
        # This only profiles the code if it hasnt been compiled in Cython

'''go perft 3
go perft 2
b4b3: 43
e6e5: 40
g6g5: 41
c7c6: 43
d7d6: 41
c7c5: 43
h3g2: 40
e6d5: 42
b4c3: 41
b6a4: 41
b6c4: 42
b6d5: 42
b6c8: 42
f6e4: 44
f6g4: 41
f6d5: 43
f6h5: 43
f6h7: 43
f6g8: 43
a6d3: 40
a6c4: 42
a6b5: 42
a6b7: 42
a6c8: 42
g7h6: 42
g7f8: 42
a8b8: 42
a8c8: 42
a8d8: 42
h8h4: 42
h8h5: 42
h8h6: 42
h8h7: 42
h8f8: 42
h8g8: 42
e7c5: 42
e7d6: 41
e7d8: 42
e7f8: 42
e8d8: 42
e8f8: 42
e8g8: 42
e8c8: 42

Nodes searched: 1803

'''