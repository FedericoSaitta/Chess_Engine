
# Do the OS stuff here

import os
import sys

# Get the current working directory
current_dir = os.getcwd()

# Join the current directory with the 'Files' folder
files_folder = os.path.join(current_dir, 'Files')

# Add the 'Files' folder to the system path
sys.path.append(files_folder)

# Now you can import your modules
import Board_state
from Move_Generator import get_all_valid_moves

import timeit
import pstats
from collections import Counter
import cProfile




ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

piece_dict = {100: 'p', 500: 'r', 330: 'b', 320: 'n', 900: 'q'}


DEPTH = 4
FEN = 'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10'
dict, board = Board_state.generate_from_FEN()

list_of_parents = {}


def perft(board, dict, depth):
    nodes = 0
    moves = get_all_valid_moves(board, dict)

    if depth == 1:
        return len(moves)

    for move in moves:
        Board_state.make_move(board, move, dict)
        nodes += perft(board, dict, depth - 1)
        Board_state.undo_move(board, dict)

    return nodes

def divide_perft(board, dict, depth): # This is slower, so should be used only for debugging
   # Board_state.make_move(board, Board_state.Move(33, 36, board), dict)
   # Board_state.make_move(board, Board_state.Move(39, 39 + 7, board), dict)
   # Board_state.make_move(board, Board_state.Move(36, 36-8, board), dict)
   # Board_state.make_move(board, Board_state.Move(39 + 7, 39 + 14, board), dict)
    moves = get_all_valid_moves(board, dict)
    for move in moves:
        leafs = 0
        key = get_chess_notation((move.start_ind, move.end_ind), move.prom_piece)

        Board_state.make_move(board, move, dict)
        leafs += (perft(board, dict, depth - 1))
        Board_state.undo_move(board, dict)

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
    with cProfile.Profile() as profile:
        for i in range(10):
            main()

        profiler_stats = pstats.Stats(profile)
        specific_file = ('Board_state.py')
        profiler_stats.strip_dirs().sort_stats('cumulative').print_stats(specific_file)
        # This only profiles the code if it hasnt been compiled in Cython or using PyPy
