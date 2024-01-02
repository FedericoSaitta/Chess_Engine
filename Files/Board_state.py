'''
This file is responsible for:
- keeping track of board state and updating the pieces
- initializing and updating Zobrist Hash

To make it faster:

- Switch to 10 x 12 list for faster out of bord check
'''
from math import fabs
from random import getrandbits


'''CONSTANTS needed for look-ups'''
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}


FABS = fabs

'''Here are the variables that will be re-assigned and changed during run time'''
HASHING_DICTIONARY = {  1: 0,   -1:  6,
                      100: 1, -100: 7,
                      320: 2, -320: 8,
                      330: 3, -330: 9,
                      500: 4, -500: 10,
                      900: 5, -900: 11}


piece_dictionary = {'q': -900, 'Q': 900, 'r': -500, 'R': 500, 'b': -330, 'B':  330,
                    'n': -320, 'N': 320, 'p': -100, 'P': 100, 'k': -1, 'K': 1}

ZOBRIST_DICTIONARY = None

# METHODS TO GENERATE A BOARD AND A BOARD-DICTIONARY FROM A FEN
def generate_from_FEN(FEN='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
    global ZOBRIST_DICTIONARY
    # Splits the FEN into: [BOARD, TURN, CASTLING RIGHTS, EN PASSANT SQUARE]
    # Discards half move and full move clocks as engine doesn't apply 50 move rule.
    board_dictionary = {}
    board = []
    argument_list = FEN.split(' ')[:-2]
    board_FEN, turn, castling_rights, en_passant_sq = argument_list[0:4]


    board_dictionary['white_to_move'] = True if turn == 'w' else False
    board_dictionary['white_castle'] = (True if 'Q' in castling_rights else False, True if 'K' in castling_rights else False)
    board_dictionary['black_castle'] = (True if 'q' in castling_rights else False, True if 'k' in castling_rights else False)
    board_dictionary['castle_rights_log'] = []

    if en_passant_sq != '-':
        en_passant_sq = files_to_cols[en_passant_sq[0]] + ranks_to_rows[en_passant_sq[1]] * 8
    else: en_passant_sq = None
    board_dictionary['en_passant_sq'] = en_passant_sq
    board_dictionary['en_passant_log'] = [en_passant_sq]

    board_dictionary['pins_list'], board_dictionary['move_log'], board_dictionary['checks_list'] = [], [], []
    board_dictionary['in_check'], board_dictionary['stale_mate'], board_dictionary['check_mate'] = False, False, False
    board_dictionary['HASH_LOG'] = []

    white_king_loc, black_king_loc = 0, 0
    index = 0
    for character in board_FEN:
        if character.isnumeric():
            empty_squares = get_zeros(int(character))
            board.extend(empty_squares)
            index += int(character)
        elif character != '/':
            board.append(piece_dictionary[character])
            if character == 'k':
                black_king_loc = index
            elif character == 'K':
                white_king_loc =  index
            index += 1

    board_dictionary['white_king_loc'] = white_king_loc
    board_dictionary['black_king_loc'] = black_king_loc

    ZOBRIST_DICTIONARY = initialize_zobrist_dictionary()
    board_dictionary['ZOBRIST_HASH'] = calculate_initial_hash(board, board_dictionary, ZOBRIST_DICTIONARY)

    return board_dictionary, board

def get_zeros(len):
    return [0 for number in range(len)]



def make_null_move(dict):
    dict['white_to_move'] = not dict['white_to_move']

def undo_null_move(dict):
    dict['white_to_move'] = not dict['white_to_move']

def make_move(board, move, dict):
    board[move.start_ind], board[move.end_ind] = 0, move.piece_moved
    dict['move_log'].append(move)

    dict['en_passant_sq'] = None # Start by assuming there are no en passants
    if move.piece_moved == 1:
        dict['white_king_loc'] = move.end_ind
        dict['white_castle'] = (False, False)
    elif move.piece_moved == -1:
        dict['black_king_loc'] = move.end_ind
        dict['black_castle'] = (False, False)

    # Checks for possibility of enpassant
    elif move.piece_moved == 100 or move.piece_moved == -100:
        if (move.start_ind // 8 == 1 ) and (move.end_ind // 8 == 3):
            dict['en_passant_sq'] = move.end_ind - 8

        elif (move.start_ind // 8 == 6) and (move.end_ind // 8 == 4):
            dict['en_passant_sq'] = move.end_ind + 8

    # Checks if castling rights should be removed
    elif move.piece_moved == 500:
        if move.start_ind == 63:
            dict['white_castle'] = (dict['white_castle'][0], False)
        elif move.start_ind == 56:
            dict['white_castle'] = (False, dict['white_castle'][1])

    elif move.piece_moved == -500:
        if move.start_ind == 7:
            dict['black_castle'] = (dict['black_castle'][0], False)
        elif move.start_ind == 0:
            dict['black_castle'] = (False, dict['black_castle'][1])


    if move.piece_captured == 500:
        if move.end_ind == 63:
            dict['white_castle'] = (dict['white_castle'][0], False)
        elif move.end_ind == 56:
            dict['white_castle'] = (False, dict['white_castle'][1])

    elif move.piece_captured == -500:
        if move.end_ind == 7:
            dict['black_castle'] = (dict['black_castle'][0], False)
        elif move.end_ind == 0:
            dict['black_castle'] = (False, dict['black_castle'][1])


    '''If the move is an en-passant'''
    if move.en_passant:
        if move.piece_moved > 0:
            board[move.end_ind + 8] = 0
        else:
            board[move.end_ind - 8] = 0

   # '''If the move is a castling move'''
    elif move.castle_move:
        if move.piece_moved > 0:
            if move.end_ind == 62:  # Right castle
                board[63], board[61] = 0, 500
            else:
                board[56], board[59] = 0, 500
        else:
            if move.end_ind == 6: # Right castle
                board[7], board[5] = 0, -500
            else:
                board[0], board[3] = 0, -500

    elif move.promotion:
        if dict['white_to_move']: # White made the move
            board[move.end_ind] = move.prom_piece
        else:
            board[move.end_ind] = -move.prom_piece

    dict['white_to_move'] = not dict['white_to_move']  # Swap the player's move
    tup = (dict['white_castle'], dict['black_castle'])
    dict['castle_rights_log'].append(tup)
    dict['en_passant_log'].append(dict['en_passant_sq'])

    # Very last thing to do is to update the ZOBRIST HASH
    dict['ZOBRIST_HASH'] = update_hash_move(dict['ZOBRIST_HASH'], move, dict)
    dict['HASH_LOG'].append(dict['ZOBRIST_HASH'])


def undo_move(board, dict):

    if len(dict['move_log']) > 0:
        move = dict['move_log'].pop()

        '''Please you have to comment on this as it is not obvious'''
        # Very first thing to do is to update the hash_vale
        dict['HASH_LOG'].pop()
        dict['ZOBRIST_HASH'] = update_hash_move(dict['ZOBRIST_HASH'], move, dict)

        if move.en_passant:
            board[move.start_ind], board[move.end_ind]= move.piece_moved, 0
            dict['en_passant_sq'] = move.end_ind
            if dict['white_to_move']:
                board[move.end_ind - 8]  = 100 # Black made the en_passant
            else:
                board[move.end_ind + 8] = -100

        else:
            board[move.start_ind], board[move.end_ind] = move.piece_moved, move.piece_captured

        '''Bring back rooks if the last move was a castling move'''
        if move.castle_move:
            if move.end_ind == 62: board[61], board[63] = 0, 500
            elif move.end_ind == 58: board[59], board[56] = 0, 500
            elif move.end_ind == 6: board[5], board[7] = 0, -500
            else: board[3], board[0] = 0, -500

        '''Need to give back the previous castling rights'''
        dict['castle_rights_log'].pop()
        if len(dict['castle_rights_log']) > 0:
            dict['white_castle'] = dict['castle_rights_log'][-1][0]
            dict['black_castle'] = dict['castle_rights_log'][-1][1]
        else:
            dict['white_castle'], dict['black_castle'] = [True, True], [True, True]

        '''Need to take back to the last en-passant square'''
        dict['en_passant_log'].pop()
        if len(dict['en_passant_log']) > 0:
            dict['en_passant_sq'] = dict['en_passant_log'][-1]
        else:
            dict['en_passant_sq'] = None

        '''Keeping track of the kings locations'''
        if move.piece_moved == 1: dict['white_king_loc'] = move.start_ind
        elif move.piece_moved == -1: dict['black_king_loc'] = move.start_ind

        dict['white_to_move'] = not dict['white_to_move']
        dict['check_mate'], dict['stale_mate'] = False, False






########################################################################################################################
#                                               ZOBRIST HASH FUNCTIONS                                                 #
########################################################################################################################

# For more information head to: https://www.chessprogramming.org/Zobrist_Hashing
def get_random_bits_list(size):
    # 64 bits are used to minimize collisions. Statistically about one in 4 billion
    if size == 1: return getrandbits(64)
    else: return [getrandbits(64) for _ in range(size)]


def initialize_zobrist_dictionary():
    # 64 x 12 numbers to store all possible locations of all pieces (even though pawns cant occupy first and last rank)
    # 1 number to represent the side to move, 16 numbers to represent castling rights (used for faster accessing even
    # though only 8 are needed), 8 numbers to represent the column the en-passant square is on.
    # Keys are capitalized as they are constants and to not confused them with the board_dictionary keys.
    ZOBRIST_DICTIONARY = {}
    ZOBRIST_DICTIONARY['HASH_TABLE'] = [get_random_bits_list(12) for _ in range(64)]
    ZOBRIST_DICTIONARY['WHITE_TO_MOVE'] = get_random_bits_list(1)
    ZOBRIST_DICTIONARY['CASTLING_RIGHTS'] = get_random_bits_list(16)
    ZOBRIST_DICTIONARY['EN_PASSANT_COLUMN'] = get_random_bits_list(8)

    return ZOBRIST_DICTIONARY


def calculate_initial_hash(board, dict, ZOBRIST_DICTIONARY):
    hash_value = 0
    for square in range(64):
        piece = board[square]
        if piece != 0:  # 0 represents an empty square
            piece_num = HASHING_DICTIONARY[piece]
            hash_value ^= ZOBRIST_DICTIONARY['HASH_TABLE'][square][piece_num]

    if dict['white_to_move']: hash_value ^= ZOBRIST_DICTIONARY['WHITE_TO_MOVE']
    
    castling_index = 0
    if dict['white_castle'][0]: castling_index |= 1
    if dict['white_castle'][1]: castling_index |= 2
    if dict['black_castle'][0]: castling_index |= 4
    if dict['black_castle'][1]: castling_index |= 8
    
    hash_value ^= ZOBRIST_DICTIONARY['CASTLING_RIGHTS'][castling_index]

    if dict['en_passant_sq'] is not None:
        en_passant_index = dict['en_passant_sq'] % 8
        hash_value ^= ZOBRIST_DICTIONARY['EN_PASSANT_COLUMN'][en_passant_index]

    return hash_value


# We only need one function that updates the board due to symmetry of XOR operator
def update_hash_move(hash_value, move, dict):
    # Needs to be run before the board changes state
    from_square, to_square = move.start_ind, move.end_ind

    if move.promotion:
        promotion_piece = HASHING_DICTIONARY[move.prom_piece]
    else:
        promotion_piece = HASHING_DICTIONARY[move.piece_moved]

    hash_value ^= ZOBRIST_DICTIONARY['HASH_TABLE'][from_square][promotion_piece]  # unXOR
    hash_value ^= ZOBRIST_DICTIONARY['HASH_TABLE'][to_square][promotion_piece]    # XOR

    if dict['white_to_move']: hash_value ^= ZOBRIST_DICTIONARY['WHITE_TO_MOVE']

    if dict['en_passant_sq'] is not None:
        en_passant_index = dict['en_passant_sq'] % 8
        hash_value ^= ZOBRIST_DICTIONARY['EN_PASSANT_COLUMN'][en_passant_index]

    castling_index = 0
    if dict['white_castle'][0]: castling_index |= 1
    if dict['white_castle'][1]: castling_index |= 2
    if dict['black_castle'][0]: castling_index |= 4
    if dict['black_castle'][1]: castling_index |= 8

    hash_value ^= ZOBRIST_DICTIONARY['CASTLING_RIGHTS'][castling_index]

    return hash_value

########################################################################################################################
#                                                      MOVE CLASS                                                      #
########################################################################################################################


class Move:
    # USING SLOTS GIVES ABOUT A 15 % INCREASE IN OBJECT GENERATION
    __slots__ = ('start_ind', 'end_ind', 'move_ID',
                 'piece_moved', 'piece_captured', 'castle_move', 'en_passant',
                 'promotion', 'prom_piece', 'killer_move')

    def __init__(self, start_sq, end_sq, board, tup=(False, False, (False, None))):

        self.start_ind, self.end_ind = start_sq, end_sq
        self.piece_moved, self.piece_captured = board[self.start_ind], board[self.end_ind]
        self.castle_move, self.en_passant, (self.promotion, self.prom_piece)  = tup
        self.killer_move = False

    def get_pgn_notation(self, multiple_piece_flag=False, same_col = False):
        dict = {-100: ' ', 100: ' ', -500: 'bR', 500: 'wR', -330: 'bB', 330: 'wB',
                -320: 'bN', 320: 'wN', -900: 'bQ', 900: 'wQ', -1: 'bK', 1: 'wK'}

        piece = self.piece_moved
        start_rank_file = self.get_rank_file(self.start_ind)
        end_rank_file = self.get_rank_file(self.end_ind)

        if self.en_passant:
            return start_rank_file[0] + 'x' + end_rank_file
        if self.promotion:
            if self.piece_captured != 0:
                return start_rank_file[0] + 'x' + end_rank_file + '=' + dict[self.prom_piece][1]
            else:
                return end_rank_file + '=' + dict[self.prom_piece][1]

        if multiple_piece_flag and (FABS(self.piece_moved) != 100):
            if same_col:
                return dict[piece][1:] + start_rank_file[1] + end_rank_file
            else:
                return dict[piece][1:] + start_rank_file[0] + end_rank_file

        if FABS(piece) == 100:
            if self.piece_captured != 0:
                return start_rank_file[0] + 'x' + end_rank_file
            else:
                return end_rank_file

        elif FABS(piece) == 1:
            if self.castle_move:
                if (self.end_ind % 8) == 6:
                    return 'O-O'
                else:
                    return 'O-O-O'
            if self.piece_captured != 0:
                return dict[piece][1:] + 'x' + end_rank_file

        elif self.piece_captured != 0:
            return dict[piece][1:] + 'x' + end_rank_file

        return dict[piece][1:] + end_rank_file


    def get_rank_file(self, index):
        r, c = index // 8, index % 8
        return cols_to_files[c] + rows_to_ranks[r]

    def __eq__(self, other):  # Note the other move is the one stored in the valid_move list
        if isinstance(other, Move):
            if (self.start_ind, self.end_ind) == (other.start_ind, other.end_ind):
                return True

        return False