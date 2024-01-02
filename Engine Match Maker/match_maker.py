from Engine_1_OLD.move_finder import iterative_deepening
from Engine_2_NEW.Move_Generator import  get_all_valid_moves
from Engine_2_NEW.Search import  iterative_deepening as iter_2
from Engine_2_NEW.Board_State import generate_from_FEN, make_move, undo_move
from random import randint

results_file = open('results.txt', 'w')


STARTING_DICT, STARTING_BOARD = None, None
THINKING_TIME = 0.1  # Seconds


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
 #   print(all_possible_notations)
  #  print(notation)
    for move in moves:
        move_notation = move.get_pgn_notation()

        if all_possible_notations.count(move_notation) > 1:
            move_not = move.get_pgn_notation(multiple_piece_flag=True)
        else:
            move_not = move.get_pgn_notation()

        if move_not == notation:
            return move

   # print('Could not find a move for this notation: ', notation)
    return None

def get_opening_book(board, moves, dict, opening_line, turn):
    move = opening_line[turn]
    move = get_move_from_notation(board, moves, move)
    return move

OPENING_DF = read_csv_to_matrix(open('/Users/federicosaitta/PycharmProjects/Chess/Engine Match Maker/Opening_repertoire.txt', 'r'))

index = randint(0, len(OPENING_DF) - 1)

def start_match(game_number):
    global STARTING_DICT, STARTING_BOARD, index

    dict, board = generate_from_FEN()
    STARTING_DICT, STARTING_BOARD = dict.copy(), board.copy()

    white, black = 0, 0
    draws = 0
    turn = 0


    if game_number % 2 == 0:
        swap_player = False
        index = randint(0, len(OPENING_DF) - 1)
    else:
        swap_player = True


    Opening_line = OPENING_DF[index]
    print(Opening_line, swap_player)
    while True:
        # We first choose a random line
        if turn < 18:
            moves = get_all_valid_moves(board, dict)
            move = get_opening_book(board, moves, dict, Opening_line, turn)
            make_move(board, move, dict)
            turn += 1

        else:
            if swap_player:
                white_moves = get_all_valid_moves(board, dict)
                if white_moves == []:
                    if dict['check_mate']:black += 1
                    else:draws += 1
                    break
                white_move = iter_2(white_moves, board, dict, THINKING_TIME)
                make_move(board, white_move, dict)

                black_moves = get_all_valid_moves(board, dict)
                if black_moves == []:
                    if dict['check_mate']:
                        white += 1
                    else:
                        draws += 1
                    break
                black_move = iterative_deepening(black_moves, board, dict, THINKING_TIME)
                make_move(board, black_move, dict)
            else:
                white_moves = get_all_valid_moves(board, dict)
                if white_moves == []:
                    if dict['check_mate']: black += 1
                    else:
                        draws += 1
                    break
                white_move = iterative_deepening(white_moves, board, dict, THINKING_TIME)
                make_move(board, white_move, dict)

                black_moves = get_all_valid_moves(board, dict)
                if black_moves == []:
                    if dict['check_mate']: white += 1
                    else:
                        draws += 1
                    break
                black_move = iter_2(black_moves, board, dict, THINKING_TIME)
                make_move(board, black_move, dict)

    if swap_player:
        return dict, black, white, draws

    return dict, white, black, draws


def write_pgn(old_move_log):
    move_notation = []

    for index in range(len(old_move_log)):
        move = old_move_log[index]
        valid_moves = get_all_valid_moves(STARTING_BOARD, STARTING_DICT)
        multiple_piece_flag, same_col = False, False

        if move in valid_moves:
            valid_moves.remove(move)

        for other_move in valid_moves:
            if move.end_ind == other_move.end_ind:
                if move.piece_moved == other_move.piece_moved:
                    multiple_piece_flag = True
                    if move.start_ind % 8 == other_move.start_ind % 8:
                        same_col = True

        notation = move.get_pgn_notation(multiple_piece_flag, same_col)
        make_move(STARTING_BOARD, move, STARTING_DICT)
        move_notation.append(notation)


    for index in range(len(move_notation)):
        turn = index//2 + 1
        if index % 2 == 0:
            move_notation[index] = str(turn) + '. ' + move_notation[index]

    results = ' '.join(move_notation)
    results_file.write(results + '\n')
def main():
    white, black, draws = 0, 0, 0
    for i in range(100):

        dictionary, white_1, black_1, draws_1 = start_match(i)
        white += white_1
        black += black_1
        draws += draws_1
        print('Match ', i + 1, ' has ended', white, black, draws)

        write_pgn(dictionary['move_log'])

    print('White wins: ', white, ' Black wins: ', black, ' Draws: ', draws)
    results_file.close()

if __name__ == '__main__':
    main()
