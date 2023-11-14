# Chess
Started on 1/11/2023
The aim to to write a chess engine that is at least around the 1700 level on chess.com. 

## Board Representation: 
-2D Python array with 2 character strings. If performance leap is needed, switch to 1D array or bitboards will be made.

## Move Generation: 
- Generates all possible moves for each piece by looping until an obstacle or enemy piece is hit
- Removes the moves which dont stop an enemy piece from attacking your own kind (not legal moves due to check)

## Board Evaluation: 
-To be implemented soon

## Move Search: 
-To be implemented soon

