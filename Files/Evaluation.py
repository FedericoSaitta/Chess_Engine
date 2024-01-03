'''
This file is responsible for:
- Initializing and flipping the Pesto boards for the white and black side.
- Evaluating the board position using a tapered evaluation with PeSTO boards

Resources:
- Tapered eval: https://www.chessprogramming.org/Tapered_Eval

Improvements:
- Making the evaluation function more accurate, especially for king safety

'''


PAWN_PHASE = 0
KNIGHT_PHASE = 1
BISHOP_PHASE = 1
ROOK_PHASE = 2
QUEEN_PHASE = 4
TOTAL_PHASE = PAWN_PHASE * 16 + KNIGHT_PHASE * 4 + BISHOP_PHASE * 4 + ROOK_PHASE * 4 + QUEEN_PHASE * 2

pieces_phase_dictionary = {1:0, 100: PAWN_PHASE, 320: KNIGHT_PHASE, 330: BISHOP_PHASE, 500: ROOK_PHASE, 900:QUEEN_PHASE,
                    -1:0, -100: PAWN_PHASE, -320: KNIGHT_PHASE, -330: BISHOP_PHASE, -500: ROOK_PHASE, -900: QUEEN_PHASE,
                          0:0 }

########################################################################################################################
#                                                    PeSTO TABLES                                                      #
########################################################################################################################

'''CHECK THAT PESTO TABLES ARE CORRECT AND THAT YOU ARE INTERPOLATING BETWEEN THEM CORRECTLY, SPEED UP THE PROCESS TOO'''
middle_game_pieces = {100: 82, 320: 337, 330: 365, 500: 477, 900: 1025, 1: 0,
                      -100: -82, -320: -337, -330: -365, -500: -477, -900: -1025, -1: 0}  # adds to 4039
end_game_pieces = {100: 94, 320: 281, 330: 297, 500: 512, 900: 936, 1: 0,
                   -100: -94, -320: -281, -330: -297, -500: -512, -900: -936, -1: 0}
                   # adds to 3868

PAWN_MG_white =  ([[0, 0, 0, 0, 0, 0, 0, 0],
                  [98, 134, 61, 95, 68, 126, 34, -11],
                  [-6, 7, 26, 31, 65, 56, 25, -20],
                  [-14, 13, 6, 21, 23, 12, 17, -23],
                  [-27, -2, -5, 12, 17, 6, 10, -25],
                  [-26, -4, -4, -10, 3, 3, 33, -12],
                  [-35, -1, -20, -23, -15, 24, 38, -22],
                  [0, 0, 0, 0, 0, 0, 0, 0]])

PAWN_EG_white =  ([[0, 0, 0, 0, 0, 0, 0, 0],
                  [178, 173, 158, 134, 147, 132, 165, 187],
                  [94, 100, 85, 67, 56, 53, 82, 84],
                  [32, 24, 13, 5, -2, 4, 17, 17],
                  [13, 9, -3, -7, -7, -8, 3, -1],
                  [4, 7, -6, 1, 0, -5, -1, -8],
                  [13, 8, 8, 10, 13, 0, 2, -7],
                  [0, 0, 0, 0, 0, 0, 0, 0]])

KNIGHT_MG_white =  ([[-167, -89, -34, -49, 61, -97, -15, -107],
                    [-73, -41, 72, 36, 23, 62, 7, -17],
                    [-47, 60, 37, 65, 84, 129, 73, 44],
                    [-9, 17, 19, 53, 37, 69, 18, 22],
                    [-13, 4, 16, 13, 28, 19, 21, -8],
                    [-23, -9, 12, 10, 19, 17, 25, -16],
                    [-29, -53, -12, -3, -1, 18, -14, -19],
                    [-105, -21, -58, -33, -17, -28, -19, -23]])

KNIGHT_EG_white =  ([[-58, -38, -13, -28, -31, -27, -63, -99],
                    [-25, -8, -25, -2, -9, -25, -24, -52],
                    [-24, -20, 10, 9, -1, -9, -19, -41],
                    [-17, 3, 22, 22, 22, 11, 8, -18],
                    [-18, -6, 16, 25, 16, 17, 4, -18],
                    [-23, -3, -1, 15, 10, -3, -20, -22],
                    [-42, -20, -10, -5, -2, -20, -23, -44],
                    [-29, -51, -23, -15, -22, -18, -50, -64]])

BISHOP_MG_white =  ([[-29, 4, -82, -37, -25, -42, 7, -8],
                    [-26, 16, -18, -13, 30, 59, 18, -47],
                    [-16, 37, 43, 40, 35, 50, 37, -2],
                    [-4, 5, 19, 50, 37, 37, 7, -2],
                    [-6, 13, 13, 26, 34, 12, 10, 4],
                    [0, 15, 15, 15, 14, 27, 18, 10],
                    [4, 15, 16, 0, 7, 21, 33, 1],
                    [-33, -3, -14, -21, -13, -12, -39, -21]])

BISHOP_EG_white =  ([[-14, -21, -11, -8, -7, -9, -17, -24],
                    [-8, -4, 7, -12, -3, -13, -4, -14],
                    [2, -8, 0, -1, -2, 6, 0, 4],
                    [-3, 9, 12, 9, 14, 10, 3, 2],
                    [-6, 3, 13, 19, 7, 10, -3, -9],
                    [-12, -3, 8, 10, 13, 3, -7, -15],
                    [-14, -18, -7, -1, 4, -9, -15, -27],
                    [-23, -9, -23, -5, -9, -16, -5, -17]])

ROOK_MG_white = ([[32, 42, 32, 51, 63, 9, 31, 43],
                  [27, 32, 58, 62, 80, 67, 26, 44],
                  [-5, 19, 26, 36, 17, 45, 61, 16],
                  [-24, -11, 7, 26, 24, 35, -8, -20],
                  [-36, -26, -12, -1, 9, -7, 6, -23],
                  [-45, -25, -16, -17, 3, 0, -5, -33],
                  [-44, -16, -20, -9, -1, 11, -6, -71],
                  [-19, -13, 1, 17, 16, 7, -37, -26]])

ROOK_EG_white =  ([[13, 10, 18, 15, 12, 12, 8, 5],
                  [11, 13, 13, 11, -3, 3, 8, 3],
                  [7, 7, 7, 5, 4, -3, -5, -3],
                  [4, 3, 13, 1, 2, 1, -1, 2],
                  [3, 5, 8, 4, -5, -6, -8, -11],
                  [-4, 0, -5, -1, -7, -12, -8, -16],
                  [-6, -6, 0, 2, -9, -9, -11, -3],
                  [-9, 2, 3, -1, -5, -13, 4, -20]])

QUEEN_MG_white =  ([[-28, 0, 29, 12, 59, 44, 43, 45],
                   [-24, -39, -5, 1, -16, 57, 28, 54],
                   [-13, -17, 7, 8, 29, 56, 47, 57],
                   [-27, -27, -16, -16, -1, 17, -2, 1],
                   [-9, -26, -9, -10, -2, -4, 3, -3],
                   [-14, 2, -11, -2, -5, 2, 14, 5],
                   [-35, -8, 11, 2, 8, 15, -3, 1],
                   [-1, -18, -9, 10, -15, -25, -31, -50]])

QUEEN_EG_white =  ([[-9, 22, 22, 27, 27, 19, 10, 20],
                   [-17, 20, 32, 41, 58, 25, 30, 0],
                   [-20, 6, 9, 49, 47, 35, 19, 9],
                   [3, 22, 24, 45, 57, 40, 57, 36],
                   [-18, 28, 19, 47, 31, 34, 39, 23],
                   [-16, -27, 15, 6, 9, 17, 10, 5],
                   [-22, -23, -30, -16, -16, -23, -36, -32],
                   [-33, -28, -22, -43, -5, -32, -20, -41]])

KING_MG_white =  ([[-65, 23, 16, -15, -56, -34, 2, 13],
                  [29, -1, -20, -7, -8, -4, -38, -29],
                  [-9, 24, 2, -16, -20, 6, 22, -22],
                  [-17, -20, -12, -27, -30, -25, -14, -36],
                  [-49, -1, -27, -39, -46, -44, -33, -51],
                  [-14, -14, -22, -46, -44, -30, -15, -27],
                  [1, 7, -8, -64, -43, -16, 9, 8],
                  [-15, 36, 12, -54, 8, -28, 24, 14]])

KING_EG_white =  ([[-74, -35, -18, -18, -11, 15, 4, -17],
                  [-12, 17, 14, 17, 17, 38, 23, 11],
                  [10, 17, 23, 15, 20, 45, 44, 13],
                  [-8, 22, 24, 27, 26, 33, 26, 3],
                  [-18, -4, 21, 24, 27, 23, 9, -11],
                  [-19, -3, 11, 21, 23, 16, 7, -9],
                  [-27, -11, 4, 13, 14, 4, -5, -17],
                  [-53, -34, -21, -11, -28, -14, -24, -43]])


def flip_rows_pst(psq_matrix):
    flipped_matrix = psq_matrix[::-1]
    return flipped_matrix


def ravel(pst_matrix, color):
    # Ravels the matrix and negates its elements for black pst.
    array = []
    multiplier = 1 if color > 0 else -1

    for row in pst_matrix:
        for square in row:
            array.append(square * multiplier)

    return tuple(array)


PAWN_MG_black, PAWN_EG_black = flip_rows_pst(PAWN_MG_white), flip_rows_pst(PAWN_EG_white)
KNIGHT_MG_black, KNIGHT_EG_black = flip_rows_pst(KNIGHT_MG_white), flip_rows_pst(KNIGHT_EG_white)
BISHOP_MG_black, BISHOP_EG_black = flip_rows_pst(BISHOP_MG_white), flip_rows_pst(BISHOP_EG_white)
ROOK_MG_black, ROOK_EG_black = flip_rows_pst(ROOK_MG_white), flip_rows_pst(ROOK_EG_white)
QUEEN_MG_black, QUEEN_EG_black = flip_rows_pst(QUEEN_MG_white), flip_rows_pst(QUEEN_EG_white)
KING_MG_black, KING_EG_black = flip_rows_pst(KING_MG_white), flip_rows_pst(KING_EG_white)

variables = [ (PAWN_MG_white, PAWN_EG_white, 100), (KNIGHT_MG_white, KNIGHT_EG_white, 320),
              (BISHOP_MG_white, BISHOP_EG_white, 330), (ROOK_MG_white, ROOK_EG_white, 500),
              (QUEEN_MG_white, QUEEN_EG_white, 900), (KING_MG_white, KING_EG_white, 1),

              (PAWN_MG_black, PAWN_EG_black, -100), (KNIGHT_MG_black, KNIGHT_EG_black, -320),
              (BISHOP_MG_black, BISHOP_EG_black, -330),(ROOK_MG_black, ROOK_EG_black, -500),
              (QUEEN_MG_black, QUEEN_EG_black, -900), (KING_MG_black, KING_EG_black, -1) ]

def build_pst_dictionary():
    piece_sq_values = {}

    for variable_tuple in variables:
        color = variable_tuple[2]

        pst_middle_game_list = ravel(variable_tuple[0], color)
        pst_end_game_list = ravel(variable_tuple[1], color)

        piece_sq_values[color] = (pst_middle_game_list, pst_end_game_list)

    return piece_sq_values


########################################################################################################################
#                                                   EVALUATION FUNCTION                                                #
########################################################################################################################

# Dictionary is built at the start as it is inexpensive
piece_sq_values = build_pst_dictionary()

# This has been optimized and tested, this is the fastest version I could write
# Dynamically keeping track of the phase could maybe squeeze some more performance but as pruning gets better the edge
# of using this dynamic method worsens
def evaluate_board(board):
    pieces_phase_dictionary_2 = pieces_phase_dictionary
    piece_sq_values_2 = piece_sq_values

    phase = TOTAL_PHASE - sum(pieces_phase_dictionary_2[p] for p in board)
    phase = (phase * 256 + (TOTAL_PHASE / 2)) / TOTAL_PHASE

    mg_eval, eg_eval = 0, 0

    for index, piece in enumerate(board):
        if piece != 0:
            mg_eval += piece_sq_values_2[piece][0][index] + middle_game_pieces[piece]
            eg_eval += piece_sq_values_2[piece][1][index] + end_game_pieces[piece]

    eval_bar = ((mg_eval * (256 - phase)) + (eg_eval * phase)) / 256
    return eval_bar / 100
