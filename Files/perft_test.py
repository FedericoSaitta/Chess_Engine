
from Files import chess_engine
import timeit
import subprocess

#import pstats
#from collections import Counter

# Run the compiled chess engine with PyPy
#subprocess.run(['pypy3', '__pycache__/chess_engine.pyc'])


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

    print('Searched ' + str(nodes) + ' nodes, in ' + str(end) + ' seconds, Nodes per second: ' + str(int(nodes/end)))


    for key, value in list_of_parents.items():
        print('{}: {}'.format(key, value))


if __name__ == '__main__':
    #with cProfile.Profile() as profile:

    main()
        #profiler_stats = pstats.Stats(profile)
        #specific_file = ('chess_engine.py')
        #profiler_stats.strip_dirs().sort_stats('cumulative').print_stats(specific_file)
        # This only profiles the code if it hasnt been compiled in Cython