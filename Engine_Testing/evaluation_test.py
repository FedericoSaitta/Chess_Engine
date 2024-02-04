'''This file is used to test the speed and accuracy of the search and evaluation function'''



# Do the imports using the OS module to get the path right
import pstats
from collections import Counter
import cProfile

from Board_state import make_move, undo_move, generate_from_FEN
from Move_Generator import get_all_valid_moves
from Engine_2_NEW.Search import iterative_deepening


FEN = '8/8/7k/8/8/8/8/6QK w KQkq - 0 8'
TIME_LIMIT = 4

def main():
    dict, board = generate_from_FEN(FEN)
    moves = get_all_valid_moves(board, dict)
    iterative_deepening(moves, board, dict, TIME_LIMIT, debug_info=True)


if __name__ == '__main__':
    with (cProfile.Profile() as profile):
        main()

        profiler_stats = pstats.Stats(profile)
        #   specific_file = ('Search.py')
        profiler_stats.strip_dirs().sort_stats('tottime').print_stats()