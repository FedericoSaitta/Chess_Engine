'''This file is used to test the speed and accuracy of the search and evaluation function'''



# Do the imports using the OS module to get the path right
import pstats
from collections import Counter
import cProfile

import os
import sys

# Get the directory of the current script
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the 'Files' folder
files_folder = os.path.join(current_script_dir, 'Files')

# Add the 'Files' folder to the system path
sys.path.append(files_folder)

# Now you can import your modules
from Board_state import generate_from_FEN
from Search import iterative_deepening
from Move_Generator import get_all_valid_moves

from Move_Generator import get_all_valid_moves


FEN = '8/8/7k/8/8/8/8/6QK w KQkq - 0 8'
TIME_LIMIT = 4

def main():
    dictionary, board = generate_from_FEN(FEN)
    moves = get_all_valid_moves(board, dict)
    iterative_deepening(moves, board, dict, TIME_LIMIT, debug_info=True)


if __name__ == '__main__':
    with (cProfile.Profile() as profile):
        main()

        profiler_stats = pstats.Stats(profile)
        #   specific_file = ('Search.py')
        profiler_stats.strip_dirs().sort_stats('cumulative').print_stats()