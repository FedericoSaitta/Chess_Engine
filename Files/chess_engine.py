from math import fabs
from random import getrandbits

'''CONSTANTS needed for look-ups'''
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

BISHOP_MOVES = ( (1, 1), (1, -1), (-1, 1), (-1, -1) )
ROOK_MOVES = ( (1, 0), (-1, 0), (0, 1), (0, -1) )

KING_MOVES = ( (1, 0), (-1, 0), (0, 1), (0, -1),  # These are moves that look forwards
               (-1, -1), (-1, 1), (1, 1), (1, -1) )   # These look diagonally

DIRECTIONS_WITH_PIECES = ( (-1, -1, {330, 900}), (-1, 1, {330, 900}), ( 1, -1, {330, 900}), ( 1,  1, {330, 900}),
                           (-1,  0, {500, 900}), ( 1, 0, {500, 900}), ( 0,  1, {500, 900}), ( 0, -1, {500, 900}) )


KNIGHT_MOVES = ( (2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2) )


QUEEN_MOVES = ( (1, 1), (1, -1), (-1, 1), (-1, -1),  # Diagonal
                   (1, 0), (-1, 0), (0, 1), (0, -1) )  # Perpendicular

WHITE_PAWN_MOVES = ( (-1, 0), (- 1, -1), (-1, 1) )

BLACK_PAWN_MOVES = ( (1, 0), (1, -1), (1, 1) )


FABS = fabs

'''Here are the variables that will be re-assigned and changed during run time'''

board = [  # Switching to a 1D board representation    # Left right is +/- 1 and up and down is +/- 8
    -500, -320, -330, -900, -1, -330, -320, -500,  # 0 to 7
    -100, -100, -100, -100, -100, -100, -100, -100,  # 8 to 15
                0, 0, 0, 0, 0, 0, 0, 0,  # 16 to 23
                0, 0, 0, 0, 0, 0, 0, 0,  # 24 to 31
                0, 0, 0, 0, 0, 0, 0, 0,  # 32 to 39
                0, 0, 0, 0, 0, 0, 0, 0,  # 40 to 47
    100, 100, 100, 100, 100, 100, 100, 100,  # 48 to 55
    500, 320, 330, 900, 1, 330, 320, 500]  # 56 to 63


HASHING_DICTIONARY = {  1: 0,   -1:  6,
                      100: 1, -100: 7,
                      320: 2, -320: 8,
                      330: 3, -330: 9,
                      500: 4, -500: 10,
                      900: 5, -900: 11}

HASH_LOG = []  # Used for three move repetition

def initialize_zobrist_table():
    ZOBRIST_HASH_TABLE = [[getrandbits(64) for _ in range(12)] for _ in range(64)]
    return ZOBRIST_HASH_TABLE


def calculate_initial_hash(board, ZOBRIST_HASH_TABLE):
    hash_value = 0
    for square in range(64):
        piece = board[square]
        if piece != 0:  # 0 represents an empty square

            piece_num = HASHING_DICTIONARY[piece]

            hash_value ^= ZOBRIST_HASH_TABLE[square][piece_num]

    return hash_value


ZOBRIST_TABLE = initialize_zobrist_table()
INITIAL_HASH = calculate_initial_hash(board, ZOBRIST_TABLE)


# Dictionary with kwargs needed during a game
general_dict = {
        'white_to_move': True,
        'white_king_loc': 60,
        'black_king_loc': 4,
        'en_passant_sq': None,
        'move_log': [],
        'white_castle': (True, True),  #  [Left, Right]
        'black_castle': (True, True), # These simply state whether the right is still there, not if the move
        'castle_rights_log': [],  # [left, right], even means white, odd means black, each turn a tuple of two
        'in_check': False,                                        # values is added
        'pins_list': [],
        'checks_list': [],
        'en_passant_log': [],
        'stale_mate': False,
        'check_mate': False,
        'ZOBRIST_HASH': INITIAL_HASH
}




def make_move(board, move, dict):
    dict['ZOBRIST_HASH'] = update_hash_move(dict['ZOBRIST_HASH'], move, board)
    HASH_LOG.append(dict['ZOBRIST_HASH'])

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


def undo_move(board, dict):

    if len(dict['move_log']) > 0:
        move = dict['move_log'].pop()
        HASH_LOG.pop()

        dict['ZOBRIST_HASH'] = undo_hash_move(dict['ZOBRIST_HASH'], move, board)

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


def un_attacked_sq(board, ind, row, col, dict, king_color):  # Determine if the enemy can attack the square (r, c), used to determine validity of castling only
    # Should check if diagonally one space away there is a king, and diagonally queen and bishop and vertically and horizontally
    # if there is a queen or a rook, do pawns separately, should also check knights separately

    for index, tup in enumerate(DIRECTIONS_WITH_PIECES):  # First 4 are diagonals, last 4 are verticals
        if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
            square = 8 * tup[0] + tup[1] + ind
            loc = board[square]
            if loc != 0: # Checks for colour
                if (loc > 0) != king_color:
                    piece = FABS(board[square])
                    if ((piece in tup[2]) or (index < 2 and (piece == 100 and king_color)) or
                            (1 < index < 4 and (piece == 100 and not king_color)) or piece == 1):
                        return False

                    # Automatically continues as there is a piece of your own colour

            else: # We need to keep looking ahead
                for mul in range(2, 8):
                    if -1 < (row + (mul * tup[0])) < 8 and -1 < (col + (mul * tup[1])) < 8:
                        square = 8 * (mul * tup[0]) + (mul * tup[1]) + ind
                        loc = board[square]
                        if loc != 0:
                            if ((loc > 0) != king_color):
                                piece = FABS(loc)
                                if piece in tup[2]: return False
                                else: break  # We need to break out as enemy piece that cant capture is blocking
                            break

                        else:
                            continue
                    else:
                        break

    for tup in KNIGHT_MOVES:  # Checks any knight moves
        if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
            square = 8 * tup[0] + tup[1] + ind
            if ((board[square] > 0) != king_color) and board[square] != 0:  # Checks for colour
                if FABS(board[square]) == 320:
                    return False  # So that side cannot castle

    return True

def get_P_moves(moves, board, ind, row, col, dict, MOVES, king_color):

    piece_pinned, pin_direction = False, ()
    for i in range(len(dict['pins_list']) - 1, -1, -1):
        if dict['pins_list'][i][0] == ind:
            piece_pinned = True
            pin_direction = (dict['pins_list'][i][1], dict['pins_list'][i][2])
            dict['pins_list'].remove(dict['pins_list'][i])
            break

    index = 0
    for tup in (MOVES):
        if (col != 0 and col != 7) or -1 < (col + tup[1]) < 8: # As pawns literally cant get of the board
            square = 8 * tup[0]  + tup[1] + ind

            if index == 0:
                if board[square] == 0:
                    if not piece_pinned or pin_direction == tup or (pin_direction[0] * -1, pin_direction[1] * -1) == tup:
                        if (row == 6 and not king_color) or (row == 1 and king_color):
                            moves.append(Move(ind, square, board, (False, False, (True, 900))))
                            moves.append(Move(ind, square, board, (False, False, (True, 500))))
                            moves.append(Move(ind, square, board, (False, False, (True, 330))))
                            moves.append(Move(ind, square, board, (False, False, (True, 320))))
                        else:
                            moves.append(Move(ind, square, board))

                        if (row == 6) and king_color:
                            if board[square - 8] == 0:  # Goes back one row
                                moves.append(Move(ind, square - 8, board))

                        elif (row == 1) and (not king_color):  # Checking for double move
                            if board[square + 8] == 0:    # Goes forth one row
                                moves.append(Move(ind, square + 8, board))
            else:
                if ((board[square] > 0) != king_color) and board[square] != 0:
                    if not piece_pinned or pin_direction == tup:
                        if (row == 6 and not king_color) or (row == 1 and king_color):
                            moves.append(Move(ind, square, board, (False, False, (True, 900))))
                            moves.append(Move(ind, square, board, (False, False, (True, 500))))
                            moves.append(Move(ind, square, board, (False, False, (True, 330))))
                            moves.append(Move(ind, square, board, (False, False, (True, 320))))
                        else:
                            moves.append(Move(ind, square, board))


                elif (square == dict['en_passant_sq']) and king_color:
                    move = Move(ind, square, board, (False, True, (False, None)))
                    make_move(board, move, dict)
                    king_position = dict['white_king_loc']
                    horizontal, vertical = king_position // 8, king_position % 8
                    if un_attacked_sq(board, king_position, horizontal, vertical, dict, True):
                        moves.append(move)

                    undo_move(board, dict)

                elif (square == dict['en_passant_sq']) and not king_color:  # As the piece is definetely black
                    move = Move(ind, square, board, (False, True, (False, None)))
                    make_move(board, move, dict)
                    king_position = dict['black_king_loc']
                    horizontal, vertical = king_position // 8, king_position % 8
                    if un_attacked_sq(board, king_position, horizontal, vertical, dict, False):
                        moves.append(move)

                    undo_move(board, dict)
        index+= 1

def get_Sliding_moves(moves, board, ind, row, col, MOVES, dict, king_color):
    piece_can_move, pin_direction = True, ()

    for i in range(len(dict['pins_list']) - 1, -1, -1):
        if dict['pins_list'][i][0] == ind:
            piece_can_move = False
            pin_direction = (dict['pins_list'][i][1], dict['pins_list'][i][2])
            dict['pins_list'].remove(dict['pins_list'][i])
            break

    for tup in MOVES:
        for mul in range(1, 8):
            if -1 < (row + (mul * tup[0])) < 8 and -1 < (col + (mul * tup[1])) < 8:
                square = 8 * (mul * tup[0]) + (mul * tup[1]) + ind
                loc = board[square]
                if (loc != 0):
                    if (loc > 0) == king_color:
                        break

                    if piece_can_move or (pin_direction == tup) or (pin_direction[0] * -1, pin_direction[1] * -1) == tup:
                        moves.append(Move(ind, square, board)) # It is an enemy piece
                        break
                else:
                    if piece_can_move or (pin_direction == tup) or (pin_direction[0] * -1, pin_direction[1] * -1) == tup:
                        moves.append(Move(ind, square, board))
            else:
                break

def get_N_moves(moves, board, ind, row, col, dict, king_color):
    piece_can_move = True
    for i in range(len(dict['pins_list']) - 1, -1, -1):
        if dict['pins_list'][i][0] == ind:
            piece_can_move = False
            dict['pins_list'].remove(dict['pins_list'][i])
            break

    for tup in KNIGHT_MOVES:
        if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
            square = 8 * (row + tup[0]) + (col + tup[1])
            if (board[square] == 0) or (board[square] >  0) != king_color:
                if piece_can_move:
                    moves.append(Move(ind, square, board))

def get_K_moves(moves, board, ind, row, col, dict, king_color):

    '''NEED TO FIX THIS BECAUSE FOR NOW KING CAN WALK INTO CHECK '''
    local_moves = []

    for tup in KING_MOVES:
        if -1 < (row + tup[0]) < 8 and -1 < (col + tup[1]) < 8:
            square = 8 * (row + tup[0]) + (col + tup[1])
            if (board[square] == 0) or ((board[square] >  0) != king_color):
                local_moves.append(Move(ind, square, board))

    for i in range(len(local_moves) - 1, -1, -1):
        move = local_moves[i]
        index = move.end_ind
        # Now we need to check these as they are pseudo legal
        make_move(board, move, dict)
        if not un_attacked_sq(board, index, index // 8, index % 8, dict, king_color):
            local_moves.remove(move)

        undo_move(board, dict)

    moves.extend(local_moves)


    # Now checking for castling
    if not dict['in_check']:
        if dict['white_to_move'] and dict['white_king_loc'] == 60:
            if dict['white_castle'][1]:
                if board[61:63] == [0, 0]:
                    if (un_attacked_sq(board, 61, 7, 5, dict, True)) and (un_attacked_sq(board, 62, 7, 6, dict, True)):
                        moves.append(Move(ind, 62, board, (True, False, (False, None))))

            if dict['white_castle'][0]:
                if board[57:60] == [0,0,0]:
                    if (un_attacked_sq(board, 59, 7, 3, dict, True)) and (un_attacked_sq(board, 58, 7, 2, dict, True)):
                        moves.append(Move(ind, 58, board, (True, False, (False, None))))
        elif not dict['white_to_move'] and dict['black_king_loc'] == 4:
            if dict['black_castle'][1]:
                if board[5:7] == [0,0]:
                    if (un_attacked_sq(board, 5, 0, 5, dict, False)) and (un_attacked_sq(board, 6, 0, 6, dict, False)):
                        moves.append(Move(ind, 6, board, (True, False, (False, None))))
            if dict['black_castle'][0]:
                if board[1:4] == [0,0,0]:
                    if (un_attacked_sq(board, 3, 0, 3, dict, False)) and (un_attacked_sq(board, 2, 0, 2, dict, False)):
                        moves.append(Move(ind, 2, board, (True, False, (False, None))))

def get_all_possible_moves(board, dict): # Using all these if statements as it is fastest
    moves = []

    for ind in range(64):
        if (board[ind] > 0 and dict['white_to_move']) or (board[ind] < 0 and not dict['white_to_move']):
            col, row = ind % 8, ind // 8
            piece = FABS(board[ind])
            king_color = dict['white_to_move']

            if piece == 100:
                if board[ind] > 0:
                    get_P_moves(moves, board, ind, row, col, dict, WHITE_PAWN_MOVES, king_color)
                else:
                    get_P_moves(moves, board, ind, row, col, dict, BLACK_PAWN_MOVES, king_color)

            elif piece == 500: get_Sliding_moves(moves, board, ind, row, col, ROOK_MOVES, dict, king_color)
            elif piece == 320: get_N_moves(moves, board, ind, row, col, dict, king_color)
            elif piece == 330: get_Sliding_moves(moves, board, ind, row, col, BISHOP_MOVES, dict, king_color)
            elif piece == 900: get_Sliding_moves(moves, board, ind, row, col, QUEEN_MOVES, dict, king_color)
            elif piece == 1: get_K_moves(moves, board, ind, row, col, dict, king_color)

    return moves

def get_all_valid_moves(board, dict):  # This will take into account non-legal moves that put our king in check

    moves = []
    ### COUNTING FOR 3 MOVE REPETITION:
    if len(HASH_LOG) > 7:
        counter = 0
        for index in range(len(HASH_LOG)-1, -1, -1):
            hash = HASH_LOG[index]

            if hash == (dict['ZOBRIST_HASH']):
                counter += 1

            if counter == 3:
                dict['stale_mate'] = True
                print('Three fold repetition on the board')
                return []

    if dict['white_to_move']:
        king_sq = dict['white_king_loc']
    else:
        king_sq = dict['black_king_loc']

    col, row = king_sq % 8, king_sq // 8

    check_pins_and_checks(board, king_sq, col, row, dict)  # Updates dictionary
    in_check, pins_list, checks_list = dict['in_check'], dict['pins_list'], dict['checks_list']

    if in_check:
        if len(checks_list) == 1:
            moves = get_all_possible_moves(board, dict)
            check = checks_list[0]
            check_sq = check[0]
            piece_checking = board[check_sq]
            valid_squares = []

            if FABS(piece_checking) == 320:
                valid_squares = [(check_sq)]
            else:
                for mul in range(1, 8):
                    valid_sq = (king_sq + mul * check[1] * 8 + mul * check[2])
                    valid_squares.append(valid_sq)
                    if valid_sq == check_sq:
                        break

            for i in range(len(moves) - 1, -1, -1):
                if FABS(moves[i].piece_moved) != 1: # Move doesn't move king so must block or capture
                    if moves[i].en_passant:
                        if moves[i].piece_moved > 0:
                            if not (moves[i].end_ind + 8) in valid_squares:
                                moves.remove(moves[i])
                        else:
                            if not (moves[i].end_ind - 8) in valid_squares:
                                moves.remove(moves[i])

                    elif not (moves[i].end_ind) in valid_squares:
                        moves.remove(moves[i])

        else: # double check so king has to move
            get_K_moves(moves, board, king_sq, row, col, dict, dict['white_to_move'])

    else:  # Not in check so make all moves minus all the moves that deal with pins
        moves = get_all_possible_moves(board, dict)

    # print(dict['checks_list'], dict['pins_list'], dict['in_check'] )

    if len(moves) == 0:
        if dict['in_check']:
            dict['check_mate'] = True
           # print(f"Check-Mate on the board for: {colour}")
        else:
            dict['stale_mate'] = True
          #  print("Stale-Mate on the board")

        return []

    return moves

def check_pins_and_checks(board, ind, col, row, dict):
    pins, checks, in_check = [], [], False
    if dict['white_to_move']:
        enemy_col, ally_col = -1, 1
    else:
        enemy_col, ally_col = 1, -1

    start_sq = ind

    index = 0
    for tup in (KING_MOVES):
        possible_pin = ()
        for mul in range(1, 8):
            end_row = row + tup[0] * mul
            end_col = col + tup[1] * mul
            end_sq = end_row * 8 + end_col
            if -1 < end_row < 8 and -1 < end_col < 8:
                end_piece = board[end_sq]
                if ( (end_piece > 0) == (ally_col > 0) ) and end_piece != 0:
                    if possible_pin == ():
                        possible_pin = (end_sq, tup[0], tup[1])
                    else:
                        break   # As this is the second piece so double walling the pin
                elif ( (end_piece > 0) != (ally_col > 0) ) and end_piece != 0:
                    type = FABS(end_piece)

                    if (index <= 3 and type == 500) or (index >= 4 and type == 330) or \
                        (mul == 1 and type == 100 and ( (enemy_col == -1 and (4 <= index <= 5)) or (enemy_col == 1 and (6 <= index <= 7)) ) )  \
                        or (type == 900) or (mul == 1 and type == 1):

                        if possible_pin == ():  # No piece blocking so it is a check
                            in_check = True
                            checks.append((end_sq, tup[0], tup[1]))
                            break
                        else: # Piece blocking so it's a pin
                            pins.append(possible_pin)
                            break
                    else:
                        break # Enemy piece not applying check
            else:
                break # We are outside the board
        index+= 1

    for tup in KNIGHT_MOVES:
        end_row = row + tup[0]
        end_col = col + tup[1]
        if -1 < end_row < 8 and -1 < end_col < 8:
            end_piece = board[end_col + end_row * 8]
            if ( (end_piece > 0) == (enemy_col > 0) and end_piece != 0) and (FABS(end_piece) == 320):
                in_check = True
                checks.append((end_row*8 + end_col, tup[0], tup[1]))

    dict['in_check'], dict['pins_list'], dict['checks_list'] = in_check, pins, checks



########################################################################################################################
#                                            HASHING AND FEN FUNCTIONS                                                 #
########################################################################################################################
# Please also encode en_passant square, castleling etc into the hash because two positions may not be equal
def update_hash_move(hash_value, move, board):
    # Needs to be ran before the board changes state
    from_square, to_square = move.start_ind, move.end_ind

    if move.promotion:
        promotion_piece = HASHING_DICTIONARY[move.prom_piece]
    else:
        promotion_piece = HASHING_DICTIONARY[move.piece_moved]

    hash_value ^= ZOBRIST_TABLE[from_square][promotion_piece]  # unXOR
    hash_value ^= ZOBRIST_TABLE[to_square][promotion_piece]       # XOR

    return hash_value

def undo_hash_move(hash_value, move, board):
    # Needs to be ran before the board changes state
    from_square, to_square = move.start_ind, move.end_ind
    piece = HASHING_DICTIONARY[move.piece_moved]

    hash_value ^= ZOBRIST_TABLE[from_square][piece]  # XOR
    hash_value ^= ZOBRIST_TABLE[to_square][piece]  # unXOR

    return hash_value



########################################################################################################################
#                                                      MOVE CLASS                                                      #
########################################################################################################################


class Move:
    __slots__ = ('start_ind', 'end_ind', 'move_ID',
                 'piece_moved', 'piece_captured', 'castle_move', 'en_passant',
                 'promotion', 'prom_piece')

    def __init__(self, start_sq, end_sq, board, tup=(False, False, (False, None))):

        self.start_ind, self.end_ind = start_sq, end_sq
        self.piece_moved, self.piece_captured = board[self.start_ind], board[self.end_ind]
        self.castle_move, self.en_passant, (self.promotion, self.prom_piece)  = tup

        # Similar idea to hash function
        self.move_ID = self.start_ind * 100 + self.end_ind


    def get_chess_notation(self, board):
        dict = {-100: 'bP', 100: 'wP', -500: 'bR', 500: 'wR', -330: 'bB', 330: 'wB',
                -320: 'bN', 320: 'wN', -900: 'bQ', 900: 'wQ', -1: 'bK', 1: 'wK', 0:'None'}

        piece = board[self.start_ind]
        start_rank_file = self.get_rank_file(self.start_ind)
        end_rank_file = self.get_rank_file(self.end_ind)

        if FABS(piece) == 100:
            if board[self.end_ind] != 0:
                return dict[piece][1:] + start_rank_file + ' x ' + end_rank_file

        if board[self.end_ind] != 0:
            return dict[piece][1:] + start_rank_file + ' x ' + end_rank_file

        return dict[piece][1:] + start_rank_file + ' to ' + end_rank_file

    def get_rank_file(self, index):
        c = index % 8
        r = index // 8
        return cols_to_files[c] + rows_to_ranks[r]

    def __eq__(self, other):  # Note the other move is the one stored in the valid_move list
        if isinstance(other, Move):
            if (self.move_ID == other.move_ID):
                return True

            elif (self.move_ID == other.move_ID) and other.castle_move:
                self.castle_move = True
                return True
            elif (self.move_ID == other.move_ID) and other.en_passant:
                self.en_passant = True
                return True

            elif (self.move_ID == other.move_ID) and other.promotion:
                self.promotion = True
                return True


        return False