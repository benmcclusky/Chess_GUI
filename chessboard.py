import pygame
import sys
import numpy as np
import os
import math

from config import *


class Chessboard:

    def __init__(self, window):
        self.board = np.empty((CHESSBOARD_SIZE, CHESSBOARD_SIZE), dtype=object)
        self.window = window
        self.current_player = 'w'  # 'w' for white, 'b' for black
        self.selected_piece = None
        self.selected_piece_pos = None
        self.white_pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P']
        self.black_pieces = ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        self.white_captured_pieces = []
        self.black_captured_pieces = []
        self.moves_since_last_pawn_move = 0
        self.moves_since_last_capture = 0
        self.last_boards = []  # A list to store the last few board states along with the moves made, Store tuples (board_state, moves)
        self.moves = []  # Add the moves attribute to keep track of moves made during the game
        self.uci_moves = []  # A list to store the moves in the UCI (Universal Chess Interface) notation
        self.current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"


    def draw(self, surface):
        """
        Draws chess board & chess pieces at specified positions
        """
        
        # Draw the chessboard squares
        for row in range(CHESSBOARD_SIZE):
            for col in range(CHESSBOARD_SIZE):
                x = col * SQUARE_SIZE
                y = TOP_BAR_HEIGHT + row * SQUARE_SIZE
                color = (139, 69, 19) if (row + col) % 2 == 0 else (169, 169, 169)
                pygame.draw.rect(surface, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        # Draw the chess pieces on the board
        for row in range(CHESSBOARD_SIZE):
            for col in range(CHESSBOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    # Calculate the scaled size of the piece image
                    scaled_size = int(SQUARE_SIZE * PIECE_SIZE_SCALE)

                    # Scale the piece image to the calculated size
                    scaled_image = pygame.transform.scale(piece.image, (scaled_size, scaled_size))

                    # Calculate the pixel coordinates (x, y) of the piece on the board
                    x = col * SQUARE_SIZE + (SQUARE_SIZE - scaled_size) // 2
                    y = TOP_BAR_HEIGHT + row * SQUARE_SIZE + (SQUARE_SIZE - scaled_size) // 2

                    # Blit (draw) the scaled piece image on the board surface
                    surface.blit(scaled_image, (x, y))



    def set_piece(self, row, col, piece):
        """
        Places piece at specified row, col on the 
        """
        self.board[row][col] = piece


    def get_piece(self, row, col):
        """
        Retrieves piece at specified row, col on the chessboard
        """
        return self.board[row][col]


    def clear_piece(self, row, col):
        """
        Clears piece at specified row, col on the chessboard
        """
        self.board[row][col] = None


    def initialize_board(self):
        """
        Initiisalses starting board, sets pieces and resets all game variables 
        """

        # Reset all variables to the starting value for a new game
        self.current_player = 'w'  # 'w' for white, 'b' for black
        self.selected_piece = None
        self.selected_piece_pos = None
        self.white_pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P']
        self.black_pieces = ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        self.white_captured_pieces = []
        self.black_captured_pieces = []
        self.moves_since_last_pawn_move = 0
        self.moves_since_last_capture = 0
        self.last_boards = []
        self.moves = []
        self.uci_moves = []
        self.current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

        # Loop through each cell of the chessboard
        for row in range(CHESSBOARD_SIZE):
            for col in range(CHESSBOARD_SIZE):
                # Get the letter representing the piece at the current cell from the STARTING_BOARD configuration
                piece_letter = STARTING_BOARD[row][col]
                
                # Check if the cell contains a piece (not an empty space)
                if piece_letter != ' ':
                    # Check if the piece has a valid mapping in the PIECE_MAPPING dictionary
                    if piece_letter in PIECE_MAPPING:
                        # Get the filename for the piece's image from the PIECE_MAPPING
                        filename = PIECE_MAPPING[piece_letter]
                        
                        # Load the image of the piece from the assets directory
                        image_path = os.path.join("assets", filename)
                        image = pygame.image.load(image_path)
                        
                        # Determine the color of the piece based on whether the piece_letter is uppercase (white) or lowercase (black)
                        color = 'w' if piece_letter.isupper() else 'b'
                        
                        # Create a new Piece object with the loaded image and color, and set it at the current cell on the board
                        self.set_piece(row, col, Piece(piece_letter, image, color))
                    else:
                        # If the piece_letter is not found in the PIECE_MAPPING, raise a ValueError with an appropriate message
                        raise ValueError(f"No image mapping found for piece '{piece_letter}'")
                else:
                    # If the cell is empty, clear the piece at the current cell on the board
                    self.clear_piece(row, col)



    def handle_mouse_event(self, event):
        """
        Handles mouse press events within the chess board area.
        """

        # Check if the mouse button was pressed down
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the left mouse button was pressed (button == 1)
            if event.button == 1:  # Left button
                # Get the coordinates (x, y) of the mouse click
                x, y = event.pos

                # Check if the click is inside the chessboard or below it (to ignore clicks on the top bar)
                if y >= TOP_BAR_HEIGHT:  
                    # Calculate the row and column on the chessboard based on the click position
                    row = (y - TOP_BAR_HEIGHT) // SQUARE_SIZE
                    col = x // SQUARE_SIZE

                    # Check if the calculated row and column values are within the valid chessboard bounds
                    if 0 <= row < CHESSBOARD_SIZE and 0 <= col < CHESSBOARD_SIZE:
                        # If the click is inside the chessboard
                        # Get the piece (if any) at the clicked position
                        piece = self.get_piece(row, col)

                        # Check if no piece is currently selected and the clicked cell contains a piece of the current player's color
                        if self.selected_piece is None and piece is not None and piece.color == self.current_player:
                            # First left-click: Select the clicked piece as the current selected_piece
                            self.selected_piece = self.get_piece(row, col)
                            self.selected_piece_pos = (row, col)
                        else:
                            # Second left-click
                            # Check if there is a selected_piece and the second click is not on the same position as the first click
                            if self.selected_piece and (row, col) != self.selected_piece_pos:
                                # Move the selected_piece to the new position (row, col)
                                self.move_piece(row, col)

                                # Reset the selected_piece and its position to None after the move is completed
                                self.selected_piece = None
                                self.selected_piece_pos = None



    def coord_to_square_notation(self, coord):
        """
        Converts coordinates (x, y) to chess square notation (e.g., 'a1', 'b2').
        """
        x, y = coord
        return COLUMN_LETTERS[y] + str(8 - x)


    def move_to_uci(self, selected_row, selected_col, row, col, piece):
        """
        Converts a move to UCI notation (Universal Chess Interface) including promotion notation if applicable.
        """
        starting_pos = self.coord_to_square_notation((selected_row, selected_col))
        dest_pos = self.coord_to_square_notation((row, col))
        promote_chosen = ''

        # Check if the piece is a pawn and if the move is a promotion move (reaching the last rank)
        if piece.notation.lower() == 'p':
            if row == 0 or row == 7:
                # Get the piece at the destination position (promotion piece)
                promotion_piece = self.board[row][col]
                promote_chosen = promotion_piece.notation.upper()

        # Concatenate the starting position, destination position, and promotion notation (if any)
        return starting_pos + dest_pos + promote_chosen


    def square_notation_to_coord(self, square_notation):
        """
        Converts chess square notation (e.g., 'a1', 'b2') to coordinates (x, y).
        """
        x = COLUMN_LETTERS.index(square_notation[0])
        y = 8 - int(square_notation[1])
        return y, x


    def uci_to_move(self, uci_move):
        """
        Converts a move in UCI notation (e.g., 'e2e4', 'e7e8q') to coordinates (x, y) for the source and destination squares.
        """
        # Extract source (selected) row and column from the first two characters of the UCI move
        selected_row, selected_col = self.square_notation_to_coord(uci_move[0:2])

        # Extract destination row and column from the last two characters of the UCI move
        row, col = self.square_notation_to_coord(uci_move[2:4])

        return selected_row, selected_col, row, col


    def board_to_fen(self, board):
        """
        Converts the current board state to the Forsyth-Edwards Notation (FEN) string.
        """

        fen = ""
        empty_squares = 0

        # Step 1: Convert the board state to the piece placement section using list comprehensions
        for row in board:
            for square in row:
                if square is None:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen += str(empty_squares)
                        empty_squares = 0
                    fen += square.notation

            if empty_squares > 0:
                fen += str(empty_squares)
                empty_squares = 0

            fen += "/"

        fen = fen[:-1]  # Remove the trailing '/' character

        # Step 2: Determine the active color and add it to the FEN string
        fen += ' '
        fen += self.current_player

        # Step 3: Determine the castling availability, FEN only checks if kings / rooks have moved

        castle_options = ' '

        w_k = self.get_piece(7,4)
        w_h_r = self.get_piece(7,7)
        w_a_r = self.get_piece(7,0)

        b_k = self.get_piece(0,4)
        b_h_r = self.get_piece(0,7)
        b_a_r = self.get_piece (0,0)

        if w_k and w_k.notation == 'K' and w_k.has_moved == False:
            if  w_h_r and w_h_r.notation == 'R'and  w_h_r.has_moved == False:
                castle_options += 'K' # White Kingside
            else:
                castle_options += '-'
            if w_a_r and w_a_r.notation == 'R'and  w_a_r.has_moved == False:
                castle_options += 'Q' # White Queenside
            else:
                castle_options += '-'

        if b_k and b_k.notation == 'k' and b_k.has_moved == False:
            if  b_h_r and b_h_r.notation == 'r'and  b_h_r.has_moved == False:
                castle_options += 'k' # Black kingside
            else:
                castle_options += '-'
            if b_a_r and b_a_r.notation == 'r'and  b_a_r.has_moved == False:
                castle_options += 'q' # Black queenside
            else:
                castle_options += '-'

        fen += castle_options + ' '

        # Step 4: Determine the en passant target square (for this example, assuming no en passant)
        en_passant_square = self.find_en_passant_square()
        fen += (self.coord_to_square_notation(en_passant_square) if en_passant_square else '-')

        # Step 5: Add the halfmove clock and fullmove number (assuming both are 0)
        fen += f' {min(self.moves_since_last_capture, self.moves_since_last_pawn_move)} {math.floor(len(self.moves) // 2)}'

        return fen
    

    def show_promotion_dialog(self, surface, row, col, color):
        """
        Shows a promotion dialog box to the player after a pawn reaches the opposite end of the board.
        """

        # Determine the promotion options based on the pawn's color
        if color == 'w':
            promotion_options = ['Q', 'N', 'R', 'B']  # Queen, Knight, Rook, Bishop
        elif color == 'b':
            promotion_options = ['q', 'n', 'r', 'b']  # queen, knight, rook, bishop (lowercase notation)
        else:
            raise ValueError(f"Invalid pawn color: {color}")

        option_images = [pygame.image.load(os.path.join("assets", PIECE_MAPPING[option])) for option in promotion_options]
        option_rects = []

        # Calculate the dimensions and position of the promotion dialog box
        dialog_width = len(promotion_options) * SQUARE_SIZE + (len(promotion_options) - 1) * 20
        dialog_height = SQUARE_SIZE + 20
        dialog_x = (CHESSBOARD_SIZE * SQUARE_SIZE) // 2 - dialog_width // 2  # Centered horizontally
        dialog_y = TOP_BAR_HEIGHT + (CHESSBOARD_SIZE * SQUARE_SIZE) // 2 - dialog_height // 2

        # Draw the promotion dialog box
        pygame.draw.rect(surface, (200, 200, 200), (dialog_x - 5, dialog_y - 5, dialog_width + 10, dialog_height + 10))
        pygame.draw.rect(surface, (20, 20, 20), (dialog_x, dialog_y, dialog_width, dialog_height))

        # Draw promotion options
        for i, image in enumerate(option_images):
            x = dialog_x + i * (SQUARE_SIZE + 20)
            y = dialog_y + 10
            scaled_image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            surface.blit(scaled_image, (x, y))
            option_rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
            option_rects.append(option_rect)

        pygame.display.flip()

        # Wait for the player to make a selection
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for i, option_rect in enumerate(option_rects):
                        if option_rect.collidepoint(x, y):
                            return promotion_options[i]

                        

    def promote_pawn(self, row, col):
        """
        Promotes a pawn on the chessboard if it reaches the last rank.
        """
        # Get the piece at the specified position on the chessboard
        piece = self.get_piece(row, col)

        # Check if the piece exists and if it is a pawn (notation is 'p' or 'P')
        if piece and piece.notation.lower() == 'p':
            # Check if the pawn is at the last rank (for both black and white)
            if (piece.color == 'b' and row == 7) or (piece.color == 'w' and row == 0):
                # Show the promotion dialog and get the player's choice
                new_piece_notation = self.show_promotion_dialog(self.window, row, col, piece.color)

                # Create the new promoted piece with the chosen notation and update the board
                promoted_piece = Piece(new_piece_notation, pygame.image.load(os.path.join("assets", PIECE_MAPPING[new_piece_notation])), piece.color)
                self.set_piece(row, col, promoted_piece)

                

    def update_counters(self, piece, selected_row, selected_col, row, col, destination_piece):
        """
        Updates various counters and lists after a move is made.
        """
        # Append the move coordinates to the moves list
        self.moves.append((selected_row, selected_col, row, col))

        # Append the current board state along with the moves made to the last_boards list
        self.last_boards.append((np.copy(self.board), self.moves))

        # Check if the length of the last_boards list is more than 6, and if so, remove the oldest board state and moves
        if len(self.last_boards) > 6:
            self.last_boards.pop(0)

        # Increment the moves_since_last_pawn_move counter if the piece is not a pawn; otherwise, reset it to 0
        if piece.notation.lower() == 'p':
            self.moves_since_last_pawn_move = 0
        else:
            self.moves_since_last_pawn_move += 1

        # Check if there is a piece at the destination position (captured piece)
        if destination_piece is not None:
            # Reset the moves_since_last_capture counter to 0
            self.moves_since_last_capture = 0

            # Check if the captured piece belongs to the opponent (white capturing black)
            if destination_piece.color == 'b':
                try:
                    # Remove the captured piece's notation from the black_pieces list
                    self.black_pieces.remove(destination_piece.notation)
                    # Append the captured piece's notation to the white_captured_pieces list
                    self.white_captured_pieces.append(destination_piece.notation)
                except ValueError:
                    pass  # If the value is not found, do nothing

            # Check if the captured piece belongs to the opponent (black capturing white)
            elif destination_piece.color == 'w':
                try:
                    # Remove the captured piece's notation from the white_pieces list
                    self.white_pieces.remove(destination_piece.notation)
                    # Append the captured piece's notation to the black_captured_pieces list
                    self.black_captured_pieces.append(destination_piece.notation)
                except ValueError:
                    pass  # If the value is not found, do nothing
        else:
            # If no piece is captured, increment the moves_since_last_capture counter
            self.moves_since_last_capture += 1


    def check_for_outcome(self):
        """
        Checks for different game outcomes and prints the corresponding messages.
        """
        # Determine the opponent's color based on the current player's color
        opponent_color = 'w' if self.current_player == 'b' else 'b'

        # Find the position of the opponent's king on the chessboard
        opponent_king_position = self.find_king_position(opponent_color)

        # Check if the opponent's king is on the board and is in check
        if opponent_king_position is not None and self.check_for_check(opponent_king_position, opponent_color):
            # If the opponent's king is in check

            # Check if the opponent's king is in checkmate
            if self.check_for_checkmate(opponent_king_position, opponent_color):
                print('Checkmate! Game Over')
            else:
                print("Opponent's king is in check!")
        # Check for other draw conditions
        elif self.check_for_stalemate(opponent_king_position, opponent_color):
            print('Draw - Stalemate')
        elif self.check_for_insufficient_material():
            print('Draw - Insufficient Material')
        elif self.check_for_fifty_moves():
            print('Draw - Fifty Move Rule')
        elif self.check_for_threefold_repetition():
            print('Draw - Threefold Repetition')


    def move_piece(self, row, col):
        """
        Moves the selected piece to the specified row and column, if the move is valid.
        """
        # Get the row and column of the selected piece
        selected_row, selected_col = self.selected_piece_pos

        # Get the selected piece from the board
        piece = self.selected_piece

        # Get the piece (if any) at the destination position
        destination_piece = self.board[row][col]

        # Check if the selected piece is not None and the move is valid, or if it is a valid castling move, or if it is a valid en passant move
        if piece and (
            self.is_valid_move(selected_row, selected_col, row, col)
            or self.is_valid_castling_move(selected_row, selected_col, row, col)
            or self.is_valid_en_passant(selected_row, selected_col, row, col, piece)
        ):
            # If the move is a standard valid move
            if self.is_valid_move(selected_row, selected_col, row, col):
                # Perform the valid move
                self.perform_valid_move(selected_row, selected_col, row, col, piece)

            # If the move is a valid castling move
            if self.is_valid_castling_move(selected_row, selected_col, row, col):
                # Perform the castling move
                self.perform_castling(selected_row, selected_col, row, col, piece)
                # Update the destination piece to None since the rook moves as part of castling
                destination_piece = None

            # If the move is a valid en passant move
            if self.is_valid_en_passant(selected_row, selected_col, row, col, piece):
                # Perform the en passant move
                self.perform_en_passant(selected_row, selected_col, row, col, piece)

            # Update various counters and check for game outcomes
            self.update_counters(piece, selected_row, selected_col, row, col, destination_piece)
            self.check_for_outcome()

            # Switch to the next player's turn
            self.toggle_player_turn()

            # Convert the move to UCI notation and add it to the list of UCI moves
            uci_notation = self.move_to_uci(selected_row, selected_col, row, col, piece)
            self.uci_moves.append(uci_notation)

            # Convert the current board state to the FEN (Forsyth-Edwards Notation) format
            self.current_fen = self.board_to_fen(self.board)

        

            


   
    def check_for_check(self, king_position, king_color, board=None):
        """
        Checks if the king of the specified color is under attack by any of the opponent's pieces.
        """
        # If a board is not provided, use the current board of the game
        if board is None:
            board = self.board

        # Extract the row and column of the king's position
        king_row, king_col = king_position

        # Loop through each cell of the chessboard
        for row in range(CHESSBOARD_SIZE):
            for col in range(CHESSBOARD_SIZE):
                # Get the piece at the current cell
                piece = board[row][col]

                # Check if there is a piece at the current cell and it is of the opponent's color (not king_color)
                if piece and piece.color != king_color:
                    # Check if the piece at (row, col) can attack the king at (king_row, king_col)
                    if self.is_valid_move(row, col, king_row, king_col, board=board):
                        # If the opponent's piece can attack the king, return True (check)
                        return True

        # If no opponent's piece can attack the king, return False (no check)
        return False

    

    def check_for_checkmate(self, king_position, king_color, board=None):
        """
        Checks if the king of the specified color is in checkmate (cannot escape from check).
        """
        # If a board is not provided, use the current board of the game
        if board is None:
            board = self.board

        # Check if any move by the opponent's pieces can move the king out of check
        for row in range(CHESSBOARD_SIZE):
            for col in range(CHESSBOARD_SIZE):
                # Get the piece at the current cell
                piece = board[row][col]

                # Check if there is a piece at the current cell and it is of the king's color (king_color)
                if piece and piece.color == king_color:
                    # Loop through all possible moves for the king's piece
                    for move_row in range(CHESSBOARD_SIZE):
                        for move_col in range(CHESSBOARD_SIZE):
                            # Check if the move (row, col) -> (move_row, move_col) is a valid move
                            if self.is_valid_move(row, col, move_row, move_col, board=board):
                                # Simulate the move by creating a temporary copy of the board
                                temp_board = np.copy(board)
                                temp_board[move_row][move_col] = piece
                                temp_board[row][col] = None

                                # Check if the move moves the king out of check (check_for_check returns False)
                                if not self.check_for_check(king_position, king_color, board=temp_board):
                                    return False  # King can move out of check, not checkmate

        # If no move can move the king out of check, return True (checkmate)
        return True


    def check_for_stalemate(self, opponent_king_position, opponent_color, board=None):
        """
        Checks if the player with the specified opponent color is in stalemate (no legal moves).
        """
        # If a board is not provided, use the current board of the game
        if board is None:
            board = self.board

        # Loop through each cell of the chessboard
        for row in range(CHESSBOARD_SIZE):
            for col in range(CHESSBOARD_SIZE):
                # Get the piece at the current cell
                piece = board[row][col]

                # Check if there is a piece at the current cell and it is of the opponent's color (opponent_color)
                if piece and piece.color == opponent_color:
                    # Loop through all possible moves for the opponent's piece
                    for move_row in range(CHESSBOARD_SIZE):
                        for move_col in range(CHESSBOARD_SIZE):
                            # Check if the move (row, col) -> (move_row, move_col) is a valid move
                            if self.is_valid_move(row, col, move_row, move_col, board=board):
                                # Simulate the move by creating a temporary copy of the board
                                temp_board = np.copy(board)
                                temp_board[move_row][move_col] = piece
                                temp_board[row][col] = None

                                # Check if the move results in a position where the opponent's king is not in check
                                if opponent_king_position is not None and not self.check_for_check(opponent_king_position, opponent_color, board=temp_board):
                                    return False  # Player has at least one legal move

        # If no move can be made by the player without putting their own king in check, return True (stalemate)
        return True

    

    def check_for_insufficient_material(self, board=None):
        """
        Checks if there is insufficient material for either side to checkmate the opponent.
        """
        # If a board is not provided, use the current board of the game
        if board is None:
            board = self.board

        # Check for insufficient material
        if (
            len(self.white_pieces) <= 2 and all(piece in ['K', 'B', 'N'] for piece in self.white_pieces) and
            len(self.black_pieces) <= 2 and all(piece in ['k', 'b', 'n'] for piece in self.black_pieces)
        ):
            return True  # Insufficient material

        return False  # Sufficient material

    

    def check_for_fifty_moves(self, board=None):
        """
        Checks if there have been 50 consecutive moves without any pawn move or capture.
        """
        # If a board is not provided, use the current board of the game
        if board is None:
            board = self.board

        # Check if there have been 50 or more consecutive moves without any pawn move or capture
        if self.moves_since_last_capture >= 50 or self.moves_since_last_pawn_move >= 50:
            return True  # Fifty moves rule is satisfied (draw)

        return False  # Fifty moves rule is not satisfied

    

    def check_for_threefold_repetition(self):
        """
        Checks if the current board state has occurred three or more times in the game history (last_boards).
        """
        current_board = np.copy(self.board)

        # Count how many times the current board state appears in the last_boards list
        count = sum(1 for board, _ in self.last_boards if np.array_equal(board, current_board))

        # If the count is 3 or more, it's a threefold repetition
        return count >= 3

    
    def move_exposes_own_king_to_check(self, start_row, start_col, end_row, end_col, board=None):
        """
        Checks if a move from the start position to the end position exposes the player's king to check.
        """
        if board is None:
            board = self.board

        # Create a temporary board to simulate the move
        temp_board = np.copy(board)
        piece = temp_board[start_row][start_col]
        temp_board[start_row][start_col] = None
        temp_board[end_row][end_col] = piece

        # Find the player's king position after the move
        player_king_color = piece.color
        player_king_position = self.find_king_position(player_king_color, board=temp_board)

        # Check if the player's king is in check after the move
        if player_king_position is not None:
            return self.check_for_check(player_king_position, player_king_color, board=temp_board)

        return False



    def find_king_position(self, color, board=None):
        """
        Finds the position of the king of the specified color on the chessboard.
        """
        if board is None:
            board = self.board

        # Iterate through the chessboard to find the king of the specified color
        for row in range(CHESSBOARD_SIZE):
            for col in range(CHESSBOARD_SIZE):
                piece = board[row][col]
                if piece and piece.notation.lower() == 'k' and piece.color == color:
                    return row, col

        # If the king of the specified color is not found, return None
        return None

    

    def is_valid_castling_move(self, start_row, start_col, end_row, end_col, board=None):
        """
        Checks if the move is a valid castling move (king-side or queen-side) on the chessboard.
        """
        if board is None:
            board = self.board

        # Retrieve the start and end pieces from the board
        start_piece = board[start_row][start_col]
        end_piece = board[end_row][end_col]

        # Check if the start or end positions are empty or do not contain a king or rook
        if start_piece is None or end_piece is None:
            return False

        if start_piece.notation.lower() not in ['k', 'r'] or end_piece.notation.lower() not in ['k', 'r']:
            return False

        # Check if the king or rook has moved before (castling requires unmoved king and rook)
        if start_piece.has_moved or end_piece.has_moved:
            return False

        # Check if there are no pieces between the king and the rook
        step = 1 if start_col < end_col else -1
        rook_col = end_col - step
        while rook_col != start_col:
            if board[start_row][rook_col]:
                return False
            rook_col -= step

        # Check if the king passes through or ends up in an attacked square
        opponent_color = 'b' if start_piece.color == 'w' else 'w'
        for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
            if self.check_for_check((start_row, col), start_piece.color, board=board):
                return False

        # If all conditions are met, the move is a valid castling move
        return True



    def perform_castling(self, start_row, start_col, end_row, end_col, selected_piece):
        """
        Performs castling move on the chessboard.
        """
        # Determine the direction of castling (left or right)
        direction = 1 if start_col < end_col else -1

        # If the selected piece is a rook, the direction is flipped
        if selected_piece.notation.lower() == 'r':
            direction = -direction

        # Perform king-side castling 
        if direction == 1:
            rook_col = 7
            king_col = 4
            new_rook_col = 5
            new_king_col = 6
        # Perform queen-side castling
        else:
            rook_col = 0
            king_col = 4
            new_rook_col = 3
            new_king_col = 2

        # Move the king to the new position
        king_piece = self.get_piece(start_row, king_col)
        self.set_piece(start_row, king_col, None)
        self.set_piece(start_row, new_king_col, king_piece)
        king_piece.has_moved = True

        # Move the rook to the new position
        rook_piece = self.get_piece(start_row, rook_col)
        self.set_piece(start_row, rook_col, None)
        self.set_piece(start_row, new_rook_col, rook_piece)
        rook_piece.has_moved = True


    def find_en_passant_square(self):
        """
        Finds the en passant square on the chessboard.
        """
        if self.last_boards:
            # Get the previous board and move from the last_boards list
            prev_board = self.last_boards[-1][0]
            prev_move = self.last_boards[-1][1][-1]
            prev_start_row, prev_start_col = prev_move[0], prev_move[1]
            prev_end_row, prev_end_col = prev_move[2], prev_move[3]
            prev_piece = prev_board[prev_end_row][prev_end_col]

            # Check if the previous move was performed by a pawn of the opposite color
            if prev_piece and prev_piece.notation.lower() == 'p' and prev_piece.color != self.current_player:
                # Check if the pawn moved two squares forward
                if abs(prev_start_row - prev_end_row) == 2:
                    # Return the en passant square based on the direction of the pawn
                    if prev_piece.color == 'w':
                        return prev_end_row + 1, prev_end_col
                    else:
                        return prev_end_row - 1, prev_end_col

        return None  # No en passant square found


    def is_valid_en_passant(self, selected_row, selected_col, row, col, piece):
        """
        Checks if the move is a valid en passant capture.
        """
        if self.last_boards:
            # Get the previous board and move from the last_boards list
            prev_board = self.last_boards[-1][0]
            prev_move = self.last_boards[-1][1][-1]
            prev_start_row, prev_start_col = prev_move[0], prev_move[1]
            prev_end_row, prev_end_col = prev_move[2], prev_move[3]
            prev_piece = prev_board[prev_end_row][prev_end_col]

            # Check if the previous move was performed by a pawn of the opposite color
            if prev_piece and prev_piece.notation.lower() == 'p' and prev_piece.color != piece.color:
                # Check if the pawn moved two squares forward and landed on the same column as the current move
                if abs(prev_start_row - prev_end_row) == 2 and prev_end_col == col:
                    # Check if the current move is made by a pawn from the 3rd (for white) or 4th (for black) row
                    if (selected_row == 3 and piece.color == 'w') or (selected_row == 4 and piece.color == 'b'):
                        return True

        return False

    
    def perform_en_passant(self, selected_row, selected_col, row, col, piece):
        """
        Performs the en passant capture and updates the board accordingly.
        """
        # Get the last move from the last_boards list
        prev_move = self.last_boards[-1][1][-1]
        prev_end_row, prev_end_col = prev_move[2], prev_move[3]

        # Set the current piece to the new position (capturing the en passant pawn)
        self.set_piece(row, col, piece)

        # Remove the original pawn that was captured (en passant)
        self.set_piece(selected_row, selected_col, None)

        # Remove the captured pawn (located at the ending position of the previous move)
        self.set_piece(prev_end_row, prev_end_col, None)

        # Set the has_moved attribute of the capturing pawn to True
        piece.has_moved = True


    def is_valid_move(self, start_row, start_col, end_row, end_col, board=None):
        """
        Determines if the move from the starting position (start_row, start_col)
        to the ending position (end_row, end_col) is valid.
        """
        if board is None:
            board = self.board

        piece = board[start_row][start_col]
        destination_piece = board[end_row][end_col]  # Get the piece at the destination square

        if destination_piece is None or destination_piece.color != piece.color:
            # Destination square is either empty or occupied by an opponent's piece
            # Continue with the existing move validation

            if piece.notation.lower() == 'p':
                return (
                    self.is_valid_pawn_move(start_row, start_col, end_row, end_col, piece.color, board=board) and
                    not self.move_exposes_own_king_to_check(start_row, start_col, end_row, end_col, board=board)
                )
            elif piece.notation.lower() == 'r':
                return (
                    self.is_valid_rook_move(start_row, start_col, end_row, end_col, board=board) and
                    not self.move_exposes_own_king_to_check(start_row, start_col, end_row, end_col, board=board)
                )
            elif piece.notation.lower() == 'n':
                return self.is_valid_knight_move(start_row, start_col, end_row, end_col)
            elif piece.notation.lower() == 'b':
                return (
                    self.is_valid_bishop_move(start_row, start_col, end_row, end_col, board=board) and
                    not self.move_exposes_own_king_to_check(start_row, start_col, end_row, end_col, board=board)
                )
            elif piece.notation.lower() == 'q':
                return (
                    self.is_valid_queen_move(start_row, start_col, end_row, end_col, board=board) and
                    not self.move_exposes_own_king_to_check(start_row, start_col, end_row, end_col, board=board)
                )
            elif piece.notation.lower() == 'k':
                return (
                    self.is_valid_king_move(start_row, start_col, end_row, end_col) and
                    not self.move_exposes_own_king_to_check(start_row, start_col, end_row, end_col, board=board)
                )
            else:
                return False

        return False

    
    def perform_valid_move(self, selected_row, selected_col, row, col, piece):
        """
        Performs a valid move from the starting position (selected_row, selected_col)
        to the ending position (row, col) for the given piece.
        """
        self.set_piece(row, col, piece)  # Place the piece at the new position
        self.promote_pawn(row, col)      # Check for pawn promotion
        self.set_piece(selected_row, selected_col, None)  # Remove the piece from the old position
        piece.has_moved = True           # Mark the piece as moved


    def is_valid_pawn_move(self, start_row, start_col, end_row, end_col, color, board=None):
        """
        Checks if the pawn move from the starting position (start_row, start_col) to
        the ending position (end_row, end_col) is valid for the given color (white or black).
        """
        if board is None:
            board = self.board

        direction = 1 if color == 'b' else -1

        if start_col == end_col:
            # Pawn moves forward
            if start_row + direction == end_row and board[end_row][end_col] is None:
                return True
            
            # Pawn double move on the first move
            if (
                (start_row == 1 and color == 'b' and end_row == 3) or
                (start_row == 6 and color == 'w' and end_row == 4)
            ):
                if (
                    board[start_row + direction][end_col] is None and
                    board[end_row][end_col] is None
                ):
                    return True
        else:
            # Pawn captures diagonally
            if start_row + direction == end_row and abs(start_col - end_col) == 1:
                target_piece = board[end_row][end_col]
                if target_piece:
                    # Normal capture
                    if target_piece.color != color:
                        return True
                else:
                    # En passant capture dealt with in check_for_en_passant method
                    pass
        
        return False


    def is_valid_rook_move(self, start_row, start_col, end_row, end_col, board=None):
        """
        Checks if the rook move from the starting position (start_row, start_col) to
        the ending position (end_row, end_col) is valid.
        """
        if board is None:
            board = self.board

        if start_row == end_row:
            # Horizontal movement
            step = 1 if start_col < end_col else -1
            for col in range(start_col + step, end_col, step):
                if board[start_row][col]:
                    return False
            return True
        elif start_col == end_col:
            # Vertical movement
            step = 1 if start_row < end_row else -1
            for row in range(start_row + step, end_row, step):
                if board[row][start_col]:
                    return False
            return True
        
        return False


    def is_valid_knight_move(self, start_row, start_col, end_row, end_col, board=None):
        """
        Checks if the knight move from the starting position (start_row, start_col) to
        the ending position (end_row, end_col) is valid.
        """
        if board is None:
            board = self.board

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)


    def is_valid_bishop_move(self, start_row, start_col, end_row, end_col, board=None):
        """
        Checks if the bishop move from the starting position (start_row, start_col) to
        the ending position (end_row, end_col) is valid.
        """
        if board is None:
            board = self.board

        if abs(start_row - end_row) == abs(start_col - end_col):
            # Diagonal movement
            row_step = 1 if start_row < end_row else -1
            col_step = 1 if start_col < end_col else -1
            row = start_row + row_step
            col = start_col + col_step

            while row != end_row:
                if board[row][col]:
                    return False
                row += row_step
                col += col_step

            return True

        return False

    def is_valid_queen_move(self, start_row, start_col, end_row, end_col, board=None):
        """
        Checks if the queen move from the starting position (start_row, start_col) to
        the ending position (end_row, end_col) is valid.
        """
        if board is None:
            board = self.board

        return (
            self.is_valid_rook_move(start_row, start_col, end_row, end_col, board=board) or
            self.is_valid_bishop_move(start_row, start_col, end_row, end_col, board=board)
        )


    def is_valid_king_move(self, start_row, start_col, end_row, end_col, board=None):
        """
        Checks if the king move from the starting position (start_row, start_col) to
        the ending position (end_row, end_col) is valid.
        """
        if board is None:
            board = self.board

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1) or (row_diff == 1 and col_diff == 1)


    def toggle_player_turn(self):
        """
        Toggles the current player's turn between 'w' (white) and 'b' (black).
        """
        if self.current_player == 'w':
            self.current_player = 'b'
        else:
            self.current_player = 'w'


    def reset_game(self):
        """
        Resets the game to the starting position.
        """
        self.initialize_board()  # Initializes the board with the starting position
        self.draw(self.window)  # Draws the chessboard and pieces on the window
        pygame.display.flip()  # Updates the display to show the changes



class Piece:
    def __init__(self, notation, image, color):
        """
        Initializes a chess piece.
        """
        self.notation = notation  # The notation of the chess piece (e.g., 'K', 'Q', 'R', 'B', 'N', 'P')
        self.image = image  # The image representing the chess piece
        self.color = color  # The color of the piece ('w' for white, 'b' for black)
        self.has_moved = False  # A flag to track if the piece has moved during the game

    def __repr__(self):
        """
        Returns the string representation of the chess piece.
        """
        return self.notation


