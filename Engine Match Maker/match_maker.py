from Engine_1_OLD.move_finder import iterative_deepening
from Engine_2_NEW.Move_Generator import  get_all_valid_moves
from Engine_2_NEW.Search import  iterative_deepening as iter_2
from Engine_2_NEW.Board_State import generate_from_FEN, make_move, undo_move

results_file = open('results.txt', 'w')


STARTING_DICT, STARTING_BOARD = None, None
THINKING_TIME = 0.1  # Seconds

def start_match(swap_players):
    global STARTING_DICT, STARTING_BOARD

    dict, board = generate_from_FEN()
    STARTING_DICT, STARTING_BOARD = dict.copy(), board.copy()

    white, black = 0, 0
    draws = 0

    while True:
        if swap_players:
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

    if swap_players:
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
    results_file.write(results)

def main():
    white, black, draws = 0, 0, 0
    for i in range(20):
        swap_players = False # False so the newer engine is playing as black

        if i > 9:
            swap_players = True

        dictionary, white_1, black_1, draws_1 = start_match(swap_players)
        white += white_1
        black += black_1
        draws += draws_1
        print('Match ', i + 1, ' has ended', white, black, draws)

        write_pgn(dictionary['move_log'])

    print('White wins: ', white, ' Black wins: ', black, ' Draws: ', draws)
    results_file.close()

if __name__ == '__main__':
    main()
