# Chess_GUI
Simple chess engine and GUI built with Pygame. Intended as a personal project to develop my Python skills, particularly focusing on using object oriented programming. 

Created chess mechanics from first principles including complex movements/rulesets such as En Passant and Castling.

Evaluations performed with [Stockfish](https://github.com/official-stockfish/Stockfish "Stockfish Repository"). For the GUI to work, you will need to download Stockfish and replace the path in game.py to your executable file. 

Annotated with the help of ChatGPT 

![GUI_Screenshot](https://github.com/benmcclusky/Chess_GUI/assets/121236905/b56777af-c895-4153-be4f-9b34367aceae)


**game.py:** Launches the GUI containing the chessboard, topbar and sidebar. Topbar contains a reset game button and displays captured pieces. Sidebar displays the  evaluation bar (powered by stockfish) with the white winning probability displayed in the top right. 


**chessboard.py:** Contains two classes: 

  **Chessboard:** Stores all the game mechanics (drawing the chessboard, 
  calculating valid moves, determining game outcome, toggling player turns, reseting the game) 

  **Piece:** Represents the individual chess pieces storing characteristics such as board notation, image file, color and tracking if they have already moved. 


**config.py:** Contains all global variables, loads png files for chessboard pieces



