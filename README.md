# Chess
Started on 1/11/2023. My first long term and proudest project so far.
The aim to to write a chess engine that is at least around the 1700 level on chess.com. 

## Board Representation: 
-1D Python array with integers representing pieces. 

## Move Generation: 
- Generates all possible moves for each piece by looping until an obstacle or enemy piece is hit
- Removes the moves which dont stop an enemy piece from attacking your own kind (not legal moves due to check)
- legal moves are validated by keeping track of pins
- Can generate 180 000 moves/sec (pseudo-legal) with Cython compilation. 

## Board Evaluation: 
-To be implemented soon

## Move Search: 
-To be implemented soon

