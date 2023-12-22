# Chess
Inspired from Eddie Sharick and Sebastian Lague, my first longest and proudest project so far.
The goal is to write a chess engine that is at least around the 1700 FIDE level. 

## Board Representation: 
-1D Python array with integers representing pieces. 

## Move Generation: 
- Generates pins and checks to only generate legal moves
- Checks for en-passant and castling separately

  ### Perft Test results:
  - Starting position:
    - Ply 5 in 31.8 s, 152 KNodes/s using CPython 
    - Ply 5 in 12.6 s, 386 KNodes/s using Cython
    - Ply 5 in 3.07 s, 1.58 MNodes/s using PyPy3 

  - Middle-game position (Kiwipete):
    - Ply 4 in 24.9 s, 164 KNodes/s using CPython 
    - Ply 4 in 8.82 s, 493 KNodes/s using Cython
    - Ply 4 in 3.16 s, 1.28 MNodes/s using PyPy3 

  - Endgame position (FEN: 8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -):
    - Ply 5 in 7.48 s, 90 KNodes/s using CPython 
    - Ply 5 in 2.86 s, 236 KNodes/s using Cython
    - Ply 5 in 1.74 s, 387 MNodes/s using PyPy3 
    
## Board Evaluation: 
- Interpolates between PESTO boards based on the opponent's material (fewer pieces means closer to the endgame). 
  This results in knights being worth more on central squares and rooks gaining in value closer to the endgame.
- If very few pieces are left, and one side is clearly winning, checkmate is encouraged by giving bonuses for forcing
  the opponent into a corner.

## Move Search: 
- Iterative deepening with Negamax (alpha-beta) and Quiescence search for captures only

## Move Ordering: 
- Best move from previous search is placed first
- Subsequent moves are ranked with MVV/LLA tables

