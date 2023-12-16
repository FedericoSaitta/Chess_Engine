# Chess
Started on 1/11/2023. My first long term and proudest project so far.
The aim is to write a chess engine that is at least around the 1700 level on chess.com. 

## Board Representation: 
-1D Python array with integers representing pieces. 

## Move Generation: 
- Generates all possible moves for each piece and checks for possibility of en-passant and castling
- legal moves are validated by keeping track of pins and checks
- Use of PyPy3 significantly increases performance, at deeper depths speeds increase, unlike for
  CPython and Cython which plateau.
 
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
-To be implemented soon

## Move Search: 
-To be implemented soon

