# Do the OS stuff here
from Board_state import make_move, undo_move, generate_from_FEN
from Move_Generator import get_all_valid_moves

get_all_valid_moves = get_all_valid_moves

import numpy as np
import timeit
import pstats
import cProfile


EXECUTION_NODES = np.array([])
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

piece_dict = {100: 'p', 500: 'r', 330: 'b', 320: 'n', 900: 'q'}


DEPTH = 5
FEN = '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 0'

list_of_parents = {}



def perft(board, dict, depth):
    nodes = 0
    moves = get_all_valid_moves(board, dict)

    if depth == 1:
        return len(moves)

    for move in moves:
        make_move(board, move, dict)
        nodes += perft(board, dict, depth - 1)
        undo_move(board, dict)

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

        make_move(board, move, dict)
        leafs += (perft(board, dict, depth - 1))
        undo_move(board, dict)

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
    global EXECUTION_NODES
    
    dict, board = generate_from_FEN(FEN)
    start = timeit.default_timer()
    nodes = perft(board, dict, DEPTH)
    end = timeit.default_timer() - start

    EXECUTION_NODES = np.append(EXECUTION_NODES, int(nodes/end))

    print('Searched ' + str(nodes) + ' nodes, in ' + str(end) + ' seconds, Nodes per second: ' + str(int(nodes/end)))

    # Used when doing the perft_divide routine
    for key, value in list_of_parents.items():
        print('{}: {}'.format(key, value))




PROFILING_CODE = False

if __name__ == '__main__':
    # Code runs about 3x slower with profiler on
    if PROFILING_CODE:
        with cProfile.Profile() as profile:
            for i in range(10):
                main()

            profiler_stats = pstats.Stats(profile)

            profiler_stats.strip_dirs().sort_stats('tottime').print_stats()
            # This only profiles the code if it hasnt been compiled in Cython or using PyPy

    else:
        for i in range(10): main()

        print(f'AVG NODES: {np.average(EXECUTION_NODES)}, STD: {np.std(EXECUTION_NODES)}')


