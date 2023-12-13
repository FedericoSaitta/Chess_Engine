import chess_engine
import timeit
import cProfile
import pstats
from collections import Counter

ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

DEPTH = 6
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
   # chess_engine.make_move(board, chess_engine.Move(51, 51-16, board), dict)
   # chess_engine.make_move(board, chess_engine.Move(10, 18, board), dict)
   # chess_engine.make_move(board, chess_engine.Move(57, 57 - 16 + 1, board), dict)
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

    #for key, value in list_of_parents.items():
        #print(f'{key}: {value}')


if __name__ == '__main__':
    with cProfile.Profile() as profile:

        main()
        profiler_stats = pstats.Stats(profile)
        specific_file = ('chess_engine.py')
        profiler_stats.strip_dirs().sort_stats('cumulative').print_stats(specific_file)
        # This only profiles the code if it hasnt been compiled in Cython

'''go perft 5
a2a3: 181046 T 
b2b3: 215255 T
c2c3: 222861 T
d2d3: 328511 FAlse
e2e3: 402988
f2f3: 178889
g2g3: 217210
h2h3: 181044
a2a4: 217832
b2b4: 216145
c2c4: 240082
d2d4: 361790 False
e2e4: 405385
f2f4: 198473
g2g4: 214048
h2h4: 218829
b1a3: 198572
b1c3: 234656
g1f3: 233491
g1h3: 198502

Nodes searched: 4865609


a2a3: 181046
b2b3: 215255
c2c3: 222861
d2d3: 328511
e2e3: 402988
f2f3: 178889
g2g3: 217210
h2h3: 181044
a2a4: 217832
b2b4: 216145
c2c4: 240082
d2d4: 361790
e2e4: 405385
f2f4: 198473
g2g4: 214048
h2h4: 218829
b1a3: 198572
b1c3: 234656
g1f3: 233491
g1h3: 198502

Nodes searched: 4865609
After doing d2 to d4 

position fen rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1
go perft 4
a7a6: 15520 T 
b7b6: 17161 T 
c7c6: 16681 False
d7d6: 21961 T 
e7e6: 23762 False
f7f6: 15527 T
g7g6: 17092
h7h6: 15628
a7a5: 17138
b7b5: 17127
c7c5: 19380
d7d5: 20675
e7e5: 26048
f7f5: 16262
g7g5: 16203
h7h5: 17192
b8a6: 16338
b8c6: 17964
g8f6: 17844
g8h6: 16287

Nodes searched: 361790


After doing c7 to c6

go perft 4
a7a6: 15520
b7b6: 17161
c7c6: 16681
d7d6: 21961
e7e6: 23762
f7f6: 15527
g7g6: 17092
h7h6: 15628
a7a5: 17138
b7b5: 17127
c7c5: 19380
d7d5: 20675
e7e5: 26048
f7f5: 16262
g7g5: 16203
h7h5: 17192
b8a6: 16338
b8c6: 17964
g8f6: 17844
g8h6: 16287

Nodes searched: 361790

position fen rnbqkbnr/pp1ppppp/2p5/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2
go perft 3
a2a3: 546 T 
b2b3: 586 T
c2c3: 608 T
e2e3: 687 T
f2f3: 547 T
g2g3: 586 T
h2h3: 546 T
d4d5: 604 T
a2a4: 586 T
b2b4: 610 T
c2c4: 606 T
e2e4: 767 T
f2f4: 509 T
g2g4: 587 T
h2h4: 586 T
b1d2: 479 False
b1a3: 544 T
b1c3: 604 False
g1f3: 607 T
g1h3: 566 T
c1d2: 583
c1e3: 546
c1f4: 660
c1g5: 615
c1h6: 563
d1d2: 603
d1d3: 864
e1d2: 486

Nodes searched: 16681

go perft 2
c6c5: 30
a7a6: 29
b7b6: 29
d7d6: 29
e7e6: 29
f7f6: 29
g7g6: 29
h7h6: 29
a7a5: 29
b7b5: 29
d7d5: 28
e7e5: 30
f7f5: 29
g7g5: 28
h7h5: 29
b8a6: 29 T
g8f6: 29
g8h6: 29
d8a5: 24 False
d8b6: 29
d8c7: 29 T

Nodes searched: 604

'''