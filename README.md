# Chess
Inspired from Eddie Sharick and Sebastian Lague, my first longest and proudest project so far.
The goal is to write a chess engine that is at least around the 1900 elo lichess level. 

## Board Representation: 
-1D Python array with integers representing pieces

## Opening Book: 
- Chooses opening branches randomly from a database of 10 000 games obtained from ficsgames.org. The games are filtered 
  to only include 2400+ rated games with minimum 15 minutes on the clock each.
- Opening book only spans 9 turns, often it lasts only a couple though.

## Move Generation: 
- Generates pins and checks to only generate legal moves
- Checks for en-passant and castling separately

  <details>
  
  <summary> Perft Test results: </summary>
  Processor: 1,6 GHz Dual-Core Intel Core i5

  - Starting position:
    - Ply 5 in 31.8 s, 152 KNodes/s using CPython
    - Ply 5 in 3.07 s, 1.58 MNodes/s using PyPy3 

  - Middle-game position (Kiwipete):
    - Ply 4 in 24.9 s, 164 KNodes/s using CPython
    - Ply 4 in 3.16 s, 1.28 MNodes/s using PyPy3 

  - Endgame position (FEN: 8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -):
    - Ply 5 in 7.48 s, 90 KNodes/s using CPython
    - Ply 5 in 1.74 s, 387 MNodes/s using PyPy3 
    
  Note: Cython compilations falls in between PyPy and Cpython

  <details>

## Board Evaluation: 
- Interpolates between PESTO boards based on the opponent's material (fewer pieces means closer to the endgame). 
  This results in knights being worth more on central squares and rooks gaining in value closer to the endgame.
- If very few pieces are left, and one side is clearly winning, checkmate is encouraged by giving bonuses for forcing
  the opponent into a corner.

## Move Search: 
- Iterative deepening with Negamax (alpha-beta) and Quiescence search for captures only

## Move Ordering: 
- Best move from previous search is placed first
- Captures are ranked with MVV/LLA tables

## ROAD MAP: 
- [ ] Cleaning and commenting code, minimizing use of external libraries (to reduced size of executable)
- [ ] Implementing Killer moves (double) and History Heuristics. 
- [ ] Implementing TT tables used in search algorithm



