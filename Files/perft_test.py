import chess_engine
import timeit
import numpy as np
from collections import Counter

ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}  # To reverse the dictionary

files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}

DEPTH = 2
board = chess_engine.board
dict = chess_engine.general_dict

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

all_moves = []
def divide_perft(board, dict, depth):
    nodes = 0
    moves = chess_engine.get_all_valid_moves(board, dict)

    if depth == 1:
        all_moves.extend(moves)
        return len(moves)

    for move in moves:
        chess_engine.make_move(board, move, dict)
        nodes += divide_perft(board, dict, depth - 1)
        chess_engine.undo_move(board, dict)

    return nodes


def get_chess_notation(tuple):
    start, end = tuple


    start_row, start_col = start // 8, start % 8
    end_row, end_col = end // 8, end % 8

    first = cols_to_files[start_col] + rows_to_ranks[start_row]
    second = cols_to_files[end_col] + rows_to_ranks[end_row]
    return (first + second)

# There should be 2039 not 2052 moves in this position

start = timeit.default_timer()
nodes = divide_perft(board, dict, DEPTH)
end = timeit.default_timer() - start
print(nodes, f'done in {end} seconds')


all_moves = np.array(all_moves)

bool = []
for move in all_moves:
    if move.castle_move:
        bool.append(True)
    else:
        bool.append(False)

all_moves = all_moves[bool]
print(len(all_moves))


#squares = [1 for num in all_moves if num == True]
# So one captures is missing
# Castle moves is correct
# I have 14 en-passants, there should be 1

#print(sum(squares))
#my_counter = Counter(squares)

#for key, value in my_counter.items():
  #  print(key,  value)


# This is basically looking through 156 000 moves per second, yes depth 5 is wrong so will have to do divide
# With cython, this is 408 00 moves per second

'''A difference of 582 moves that I have extra'''
'''PERFT 5 RESULTS: nodes: 4865609
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
'''

'''Results: 
a4a5 16044
b2b3 161278
b2b4 159740
c2c3 148732
c2c4 146337
d2d3 155618
d2d4 153609
e2e3 154543
e2e4 152521
f2f3 148748
f2f4 146655
g2g3 162302
g2g4 159486
h2h3 148240
h2h4 146474
a1a2 31537
a1a3 16048
b1c3 147861
b1a3 147138
g1h3 147159
g1f3 147600
a4b5 2224
a3a4 15455
b3b4 17605
c1b2 32869
a3b4 624
b4b5 15551
b4a5 1599
c3c4 16331
d1c2 31609
d1b3 29827
d1a4 28049
c3d4 75
c3b4 187
c4c5 15591
c4b5 2406
c4d5 2679
d3d4 19283
b1d2 33290
c1d2 33406
c1e3 31378
c1f4 29624
c1g5 29549
c1h6 26801
d1d2 36408
e1d2 36281
d4d5 18001
d1d3 18522
d4e5 2203
d1d4 567
e3e4 20577
d1e2 36224
d1f3 32668
d1g4 30914
d1h5 30543
e1e2 38455
f1e2 35421
f1d3 33655
f1c4 31877
f1b5 31797
f1a6 28999
g1e2 35158
e3d4 539
e4e5 18690
e4d5 2205
e4f5 1875
f3f4 16345
e1f2 31105
f4f5 14858
f4e5 2651
f4g5 2398
g3g4 16700
f1g2 32865
f1h3 29317
g4g5 16338
g4f5 2433
g4h5 2394
h3h4 15395
h1h2 31537
h4h5 15302
h1h3 16048
h4g5 1558
a2a1 890
c3b1 14664
c3d5 15109
c3b5 15109
c3a2 1780
c3e4 14223
c3a4 14221
a1b1 32853
h3g1 14603
h3g5 15046
h3f4 14166
h1g1 32832
f3g1 14670
f3g5 15115
f3e5 15115
f3h4 14233
f3d4 14237
b4c5 1634
d4c5 1892
f3g4 1068
h3g4 624
d3e4 980
f3e4 520
b3a4 927
a1a4 460
b3c4 485
d3c4 1379
g2h3 1610
b2a3 1622
c1a3 29321
g3h4 114
h1h4 530
a2a3 148228
e3f4 931
g3f4 40
a5a6 351
a5b6 83
a1a5 24
a3a2 443
a3a1 443
a3b3 443
a3c3 443
a3d3 443
a3e3 443
a3f3 443
a3g3 443
a3h3 443
a3b1 14603
a3b5 15046
a3c4 14162
b5b6 405
b5c6 814
a1a6 19
a1a7 16
b5a6 830
a2a4 146266
b2c1 889
b2c3 889
b2d4 889
b2e5 885
b2f6 788
b2g7 656
d1c1 6083
b2h8 128
a3b2 885
a3c1 885
a3c5 436
a3d6 394
a3e7 349
a3f8 72
c5c6 367
c5b6 101
c5d6 98
a3c2 1774
c2d1 891
c2d3 891
c2e4 891
c2f5 887
c2g6 807
c2h7 735
c2b3 891
c2a4 891
e1d1 7242
b3c2 889
b3d1 889
b3d5 442
b3e6 395
b3f7 349
b3b5 879
b3b6 801
b3b7 721
b3a3 889
b3g8 63
a4b3 742
a4c2 742
a4d1 742
a4c6 664
a4a3 742
a4a6 668
a4a7 544
a4b4 742
a4c4 367
a4d4 365
a4e4 364
a4f4 362
a4g4 361
a4h4 358
a4d7 530
b3c3 446
b3d3 446
b3e3 446
b3f3 446
b3g3 446
b3h3 446
b3b8 1
d5d6 399
d5c6 127
d5e6 102
d2e4 883
d2c4 883
d2b1 883
d2f3 883
d2b3 883
d2c1 883
d2e3 2635
d2f4 1766
d2g5 1762
d2h6 1598
d2c3 2653
d2b4 1782
d2a5 1762
e3d2 891
e3c1 883
e3g5 881
e3h6 799
e3c5 439
e3b6 398
e3a7 361
f4g3 881
f4e3 881
f4d2 889
f4c1 881
f4h6 799
f4d6 785
f4c7 697
g5h4 831
g5f4 831
g5e3 829
g5d2 837
g5c1 829
g5h6 1010
g5f6 966
g5e7 693
g5d8 141
h6g5 733
h6f4 691
h6e3 689
h6d2 697
h6c1 689
h6g7 733
h6f8 104
d2d1 883
d2e1 883
d1e1 2633
f3d2 1782
f4b8 131
d3f5 883
d3g6 803
d3h7 731
d3b5 1330
d3a6 1213
d3d2 446
d3d1 442
d3e3 442
d3f3 442
d3g3 442
d3h3 442
d3c3 446
d3b3 442
d3a3 442
d1d5 51
d1d6 46
d1d7 43
e5e6 402
e5f6 113
e5d6 115
c3e2 1782
e2d1 891
e2f3 2654
e2g4 1782
e2h5 1762
e2d3 2656
e2c4 1782
e2b5 1778
e2a6 1622
f3e2 891
f3d1 891
f3h5 881
f3d5 443
f3c6 396
f3f5 889
f3f6 809
f3f7 669
f3g3 891
f3h3 891
f3b7 329
g4h3 873
g4f3 873
g4e2 873
g4d1 873
g4e6 793
g4d7 699
g4g3 873
g4g6 791
g4g7 715
g4h4 873
g4f4 873
g4e4 438
g4d4 433
g4c4 431
g4b4 430
g4a4 425
g4c8 135
h5g4 716
h5f3 706
h5e2 706
h5d1 706
h5g6 828
h5f7 642
h5h4 716
h5h3 712
h5h6 1069
h5h7 588
h5g5 716
h5f5 644
h5e5 634
h5d5 552
h5c5 478
h5b5 418
h5a5 366
e2e1 891
e2f1 891
e1f1 5964
d3e2 891
d3f1 891
c4d3 885
c4e2 885
c4f1 885
c4b3 885
c4e6 791
c4f7 699
c4a6 807
c4g8 127
b5c4 700
b5d3 698
b5e2 698
b5f1 698
b5a4 700
b5d7 562
a6b5 741
a6c4 703
a6d3 701
a6e2 701
a6f1 701
a6b7 741
a6c8 104
e2f4 891
e2d4 891
e2g1 891
e2g3 891
e2c3 891
f3a8 64
h5h8 30
f3e3 446
f3d3 446
f3c3 446
f3b3 446
f3a3 446
f5f6 364
f5e6 116
f5g6 92
f3f8 1
f2e3 869
f2g3 868
f2e1 887
h3f2 1774
g5g6 403
g2f1 889
g2f3 889
g2e4 889
g2d5 885
g2c6 792
g2b7 658
h3g2 885
h3f1 885
h3f5 436
h3e6 396
h3d7 349
h3c8 67
g2a8 128
f3h2 1780
h2h1 890
h3h2 443
h3h1 443
h3g3 443
h3f3 443
h3e3 443
h3d3 443
h3c3 443
h3b3 443
h3a3 443
h1h5 22
h1h6 19
h1h7 16
d5e3 422
d5c3 422
d5e7 422
d5c7 422
d5f4 422
d5b4 422
d5f6 422
d5b6 422
b5c3 850
b5a3 850
b5c7 850
b5a7 850
b5d4 850
b5d6 850
e4f6 443
e4d6 443
e4g3 443
e4c3 443
e4g5 443
e4c5 443
a4b6 444
a4c3 444
a4c5 444
b1a1 890
c4d6 444
c4b6 444
c4e3 444
c4a3 444
c4e5 444
c4a5 444
g5h3 838
g5f3 838
g5h7 838
g5f7 838
g5e4 838
g5e6 838
f4g6 444
f4e6 444
f4h3 444
f4d3 444
f4h5 444
f4d5 444
g1h1 890
e5f3 420
e5d3 420
e5f7 420
e5d7 420
e5g4 420
e5c4 420
e5g6 420
e5c6 420
h4g6 442
h4f3 442
h4f5 442
d4e6 443
d4c6 443
d4f3 443
d4b3 443
d4f5 443
d4b5 443'''