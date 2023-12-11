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
    #chess_engine.make_move(board, chess_engine.Move(33, 57, board),dict )
    #chess_engine.make_move(board, chess_engine.Move(39, 38, board), dict)
    #chess_engine.make_move(board, chess_engine.Move(24, 33, board), dict)

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
    if move.piece_captured != 0:
        count +=1
print(count)


for key, value in list_of_parents.items():
    print(f'{key}: {value}')

''' same position, captures and en_passant is good, missing 35 moves though
go perft 5
e2e3: 45326 GOOD
g2g3: 14747 GOOD
a5a6: 59028 GOOD
e2e4: 36889 GOOD
g2g4: 53895 GOOD
b4b1: 69665 GOOD
b4b2: 48498 GOOD
b4b3: 59719 GOOD
b4a4: 45591 GOOD
b4c4: 63781 FALSE, UNDERDOING 2
b4d4: 59574 FALSE, UNDERDOING 3
b4e4: 54192 GOOD
b4f4: 10776 FALSE, UNDERDOING 14
a5a4: 52943 FALSE, UNDERDOING 16 doing this one 






















'''
