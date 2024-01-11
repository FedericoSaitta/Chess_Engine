'''
This file is responsible for:
- Calculating legal moves by:
    - keeping track of pins and checks
    - iterating through the possible landing squares
    - en-passant, castling and king moves are first tested to see whether they would result in
      our king being in check.

To make it faster:

- Faster ways to allocate Move objects to a list?
- Include lazy generators to speed up quiesce search
- Reduced amount of memory allocated, and multiplications performed within functions
- Being able to generate just checks and captures (Need special functions for it)
- Running all the move in just one function, similar to pyfish, this should speed up
- multiprocessing for move generation?? A new thread is spawned each time a new get_moves methods is called for a piece
'''

from math import fabs
from Board_state import Move, make_move, undo_move


FABS = fabs

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


########################################################################################################################
#                                        FUNCTIONS FOR LEGAL MOVE GENERATION                                           #
########################################################################################################################

def un_attacked_sq(board, ind, row, col, dict, king_color):
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


def get_P_moves(moves: list, board: list, ind: int, row: int, col: int, dict: dict, MOVES: list, king_color: bool):
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

def get_all_possible_moves(board: list, dict: dict): # Using all these if statements as it is fastest
    moves = []

    ind = 0
    for piece in board:
        if (piece > 0 and dict['white_to_move']) or (piece < 0 and not dict['white_to_move']):
            col, row = ind % 8, ind // 8
            piece = FABS(piece)
            king_color = dict['white_to_move']

            if piece == 100:
                if king_color: get_P_moves(moves, board, ind, row, col, dict, WHITE_PAWN_MOVES, king_color)
                else: get_P_moves(moves, board, ind, row, col, dict, BLACK_PAWN_MOVES, king_color)

            elif piece == 500: get_Sliding_moves(moves, board, ind, row, col, ROOK_MOVES, dict, king_color)
            elif piece == 320: get_N_moves(moves, board, ind, row, col, dict, king_color)
            elif piece == 330: get_Sliding_moves(moves, board, ind, row, col, BISHOP_MOVES, dict, king_color)
            elif piece == 900: get_Sliding_moves(moves, board, ind, row, col, QUEEN_MOVES, dict, king_color)
            elif piece == 1: get_K_moves(moves, board, ind, row, col, dict, king_color)
        ind += 1

    return moves


def get_all_valid_moves(board: list, dict: dict):  # This will take into account non-legal moves that put our king in check
    moves = []
    HASH_LOG = dict['HASH_LOG']
    ### COUNTING FOR 3 MOVE REPETITION:
    if len(HASH_LOG) > 7:
        counter = 0
        for index in range(len(HASH_LOG)-1, -1, -1):
            hash = HASH_LOG[index]

            if hash == (dict['ZOBRIST_HASH']):
                counter += 1

            if counter == 3:
                dict['stale_mate'] = True
             #   print('Three fold repetition on the board')
                return []

    if dict['white_to_move']: king_sq = dict['white_king_loc']
    else: king_sq = dict['black_king_loc']

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
#                                      SPECIAL GENERATORS FOR QUIESCE SEARCH                                           #
########################################################################################################################

# In check validator for Null move pruning:
def is_not_in_check(board, dict):
    king_color = True if dict['white_to_move'] else False
    king_ind = dict['white_king_loc'] if king_color else dict['black_king_loc']

    return un_attacked_sq(board, king_ind, king_ind // 8, king_ind % 8, dict, king_color)