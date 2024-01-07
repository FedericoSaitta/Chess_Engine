'''
This file is responsible for:
- Initializing and return opening book moves from the repertoire file
'''

from Board_state import generate_from_FEN
from random import randint
# Need to fix quite a few bugs and write much cleaner code for the book move generation
OPENING_REPERTOIRE_FILE = '/Users/federicosaitta/PycharmProjects/Chess/Files/Opening_repertoire.txt'
OPENING_DF = None

# Methods to read and index the opening repertoire matrix, pandas is avoided to minimize size of executable file
def initialize_opening_repertoire(file_name):
    return read_csv_to_matrix(open(file_name, 'r'))


def read_csv_to_matrix(file_obj):
    # Reads the data, removes the extra spaces at the end of the line, it splits each line into a subsequent list
    # using space as a delimeter.
    data_matrix = []
    for line in file_obj:
        line = line.strip('\n')
        line = line.split(' ')
        line.remove('')

        data_matrix.append(line)

    return data_matrix


def index_matrix(matrix, row_index, column):
    # Indexes a matrix, returns all the rows which have the same row_index found at the specified column index
    for i in range(len(matrix) -1, -1, -1):
        if matrix[i][column] != row_index:
            matrix.remove(matrix[i])


def get_opening_book(board, moves, dict):
    global OPENING_DF

    if OPENING_DF is None: OPENING_DF = initialize_opening_repertoire(OPENING_REPERTOIRE_FILE)

    try:  # We look if the current position key is present in the data frame
        turn = len(dict['move_log'])
        if turn > 0:

            previous_move = (dict['move_log'][-1]).get_pgn_notation()
            previous_move_2 = (dict['move_log'][-1]).get_pgn_notation(multiple_piece_flag=True)

            OPENING_1 = OPENING_DF.copy()
            index_matrix(OPENING_DF, previous_move, turn-1)

            if OPENING_DF == []:
                index_matrix(OPENING_1, previous_move_2, turn-1)
                OPENING_DF = OPENING_1


            index = randint(0, len(OPENING_DF) - 1)
            move = OPENING_DF[index][turn]
            move = get_move_from_notation(board, moves, move)


        else:
            index = randint(0, len(OPENING_DF) - 1)
            move = OPENING_DF[index][0]
            move = get_move_from_notation(board, moves, move)

        return move

    except (KeyError, ValueError, AttributeError) as e :
        # Means we are out of book, so we return to finding a move with negamax
        return None


ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}


def get_move_from_notation(board, moves, notation):
    if notation is None: return None
    if notation == 'O-O':
        end_col = 6
        for move in moves:
            if (move.end_ind % 8 == end_col) and move.castle_move:
                return move

    elif notation == 'O-O-O':
        end_col = 2
        for move in moves:
            if (move.end_ind % 8 == end_col) and move.castle_move:
                return move

    # Checks if there are multiple moves of the same type achieving the same square
    # So we flag them as multiple moves

    all_possible_notations = [move.get_pgn_notation() for move in moves]
    for move in moves:
        move_notation = move.get_pgn_notation()

        if all_possible_notations.count(move_notation) > 1:
            move_not = move.get_pgn_notation(multiple_piece_flag=True)
        else:
            move_not = move.get_pgn_notation()

        if move_not == notation:
            return move

    return None