import pygame
import os
import time
import math

from chessboard import Chessboard
from config import *
from stockfish import Stockfish

stockfish = Stockfish(
    path=r"stockfish\stockfish-windows-x86-64-avx2.exe", # Replace with path to locally stored stockfish directory
    depth=12,
    parameters={"Threads": 2, "Minimum Thinking Time": 30},
)


class Topbar:
    def __init__(self, window, width, height, color, chessboard):
        self.window = window
        self.width = width
        self.height = height
        self.color = color
        self.chessboard = chessboard
        self.evaluation_result = 0

    def draw(self):
        pygame.draw.rect(self.window, self.color, (0, 0, self.width, self.height))
        self.draw_horizontal_line()
        self.draw_evaluation_bar()
        self.draw_evaluation_text()

    def draw_horizontal_line(self):
        line_color = (40, 40, 40)
        pygame.draw.rect(self.window, line_color, (0, self.height - LINE_THICKNESS, self.width, LINE_THICKNESS))

    
    def draw_evaluation_bar(self):
        max_width = WINDOW_WIDTH - SIDE_BAR_WIDTH - (4 * LINE_THICKNESS)  # Maximum width of the evaluation bar
        min_value = 0  # Minimum evaluation value (adjust as needed)
        max_value = 1  # Maximum evaluation value (adjust as needed)
        bar_height = 50

        # Calculate the ratio of white and black in the bar based on the evaluation result
        ratio = (self.evaluation_result - min_value) / (max_value - min_value)
        white_width = int(max_width * ratio)
        black_width = max_width - white_width

        # Draw the gradient rectangle with white on the left and black on the right
        pygame.draw.rect(self.window, (255, 255, 255), (2 * LINE_THICKNESS, (TOP_BAR_HEIGHT // 2) - (bar_height // 2) + LINE_THICKNESS, white_width, self.height // 2))
        pygame.draw.rect(self.window, (0, 0, 0), (2 * LINE_THICKNESS + white_width, (TOP_BAR_HEIGHT // 2) - (bar_height // 2) + LINE_THICKNESS, black_width, self.height // 2))

    def draw_evaluation_text(self):
        # Create a font and render the evaluation result as text
        font = pygame.font.Font(None, 40)
        text = font.render(f"{self.evaluation_result:.2f}", True, (255, 255, 255))

        # Determine the position to display the text (top right corner)
        text_x = self.width - (SIDE_BAR_WIDTH // 2) - (text.get_width() // 2) - LINE_THICKNESS
        text_y = (self.height // 2) - (text.get_height() // 2)

        # Blit the text on the window
        self.window.blit(text, (text_x, text_y))


    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left button
                x, y = event.pos

                # Add when have more buttons


class Sidebar:

    def __init__(self, window, width, height, color, x_pos, y_pos, chessboard):
        self.window = window
        self.width = width
        self.height = height
        self.color = color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.restart_button_rect = None  # Initialize restart_button_rect as None
        self.chessboard = chessboard  # Store a reference to the Chessboard instance

        self.white_captured_rect = pygame.Rect(self.x_pos + 15, self.y_pos + 40, self.width - 30, 100)
        self.black_captured_rect = pygame.Rect(self.x_pos + 15, self.y_pos + 180, self.width - 30, 100)

        # New attributes for titles
        self.white_title = "White: Player 1"
        self.black_title = "Black: Player 2"
        
    def draw(self):
        pygame.draw.rect(self.window, self.color, (self.x_pos, self.y_pos, self.width, self.height))
        self.draw_restart_button()

        # Draw Player: White title
        white_title_font = pygame.font.Font(None, 20)
        white_title_text = white_title_font.render(self.white_title, True, (255, 255, 255))
        self.window.blit(white_title_text, (self.x_pos + 15, self.y_pos + 20))

        # Draw Player: Black title
        black_title_font = pygame.font.Font(None, 20)
        black_title_text = black_title_font.render(self.black_title, True, (255, 255, 255))
        self.window.blit(black_title_text, (self.x_pos + 15, self.y_pos + 160))

        # Draw Player: White captured pieces
        pygame.draw.rect(self.window, (255, 255, 255), self.white_captured_rect)
        self.draw_captured_pieces(self.white_captured_rect, self.chessboard.white_captured_pieces)

        # Draw Player: Black captured pieces
        pygame.draw.rect(self.window, (0, 0, 0), self.black_captured_rect)
        self.draw_captured_pieces(self.black_captured_rect, self.chessboard.black_captured_pieces)


    def draw_captured_pieces(self, rect, captured_pieces):
        x = rect.left + 10
        y = rect.top + 10
        max_pieces_per_row = 5  # Maximum number of pieces to display per row
        piece_size = int(rect.width // 8)

        for i, piece_notion in enumerate(captured_pieces):
            row = i // max_pieces_per_row
            col = i % max_pieces_per_row
            piece_x = x + col * (piece_size + 5)
            piece_y = y + row * (piece_size + 5)

            image_path = os.path.join("assets", PIECE_MAPPING[piece_notion])
            image = pygame.image.load(image_path)
            scaled_image = pygame.transform.scale(image, (piece_size, piece_size))
            self.window.blit(scaled_image, (piece_x, piece_y))


    def draw_restart_button(self):

        restart_button_width = self.width - 30  # Adjust the width of the restart button
        restart_button_height = 25
        restart_button_x = self.x_pos + (self.width - restart_button_width) // 2 
        restart_button_y = self.y_pos + (WINDOW_HEIGHT - TOP_BAR_HEIGHT) - restart_button_height - 15

        restart_button_color = (120, 120, 120)  # Blue color for the restart button

        restart_button_rect = pygame.Rect(restart_button_x, restart_button_y, restart_button_width, restart_button_height)
        pygame.draw.rect(self.window, restart_button_color, restart_button_rect)

        # You can add text to the restart button if desired, for example:
        font = pygame.font.Font(None, 30)
        text = font.render("Restart", True, (0, 0, 0))
        text_rect = text.get_rect(center=(restart_button_x + restart_button_width / 2, restart_button_y + restart_button_height / 2))
        self.window.blit(text, text_rect)

        # Save the restart button rectangle for click detection in handle_mouse_event
        self.restart_button_rect = restart_button_rect


    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left button
                x, y = event.pos

                # Check if the click is within the restart button's rectangular area
                if self.restart_button_rect.collidepoint(x, y):
                    # Handle the click on the restart button here
                    print("Game Restarted")
                    self.chessboard.reset_game()


class Evaluation:
    def __init__(self):
        self.depth = 12  # Initial depth for Stockfish evaluation
        self.previous_fen = None  # Variable to store the previous FEN


    def sigmoid(self, x):
        return 1 / (1 + math.exp(-0.004 * x))


    def stockfish_evaluation(self, fen_string):
        """
        Returns the centripawns evaluation from Stockfish for the current board position
        """
        if stockfish.is_fen_valid(fen_string):
            stockfish.set_fen_position(fen_string)
            evaluation = stockfish.get_evaluation()

            if evaluation['type'] == "cp":
                centipawn_evaluation = int(evaluation['value'])
                white_win_prob = self.sigmoid(centipawn_evaluation)
                return white_win_prob

        else:
            print('Invalid FEN')




def main():
    pygame.init()

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chessboard")

    chessboard = Chessboard(window)
    chessboard.initialize_board()

    # Fill the window with a background color (white in this case)
    window.fill((255, 255, 255))

    top_bar = Topbar(window, WINDOW_WIDTH, TOP_BAR_HEIGHT, (20, 20, 20), chessboard)
    side_bar = Sidebar(window, SIDE_BAR_WIDTH, WINDOW_HEIGHT - TOP_BAR_HEIGHT, (10, 10, 10), WINDOW_WIDTH - SIDE_BAR_WIDTH, TOP_BAR_HEIGHT, chessboard)

    evaluation = Evaluation()

    last_evaluation_time = 0  # Variable to store the last time the evaluation was triggered

    running = True
    while running:
        current_time = time.time()  # Get the current time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            chessboard.draw(window)
            top_bar.draw()
            side_bar.draw()

            fen_string = chessboard.current_fen

            # Check if it's time to trigger the evaluation and the FEN position changed
            if current_time - last_evaluation_time >= 0.5 and fen_string != evaluation.previous_fen:
                top_bar.evaluation_result = evaluation.stockfish_evaluation(fen_string)
                last_evaluation_time = current_time  # Update the last evaluation time

            evaluation.previous_fen = fen_string

            chessboard.handle_mouse_event(event)
            top_bar.handle_mouse_event(event)
            side_bar.handle_mouse_event(event)

        turn_text = "White's Turn" if chessboard.current_player == 'w' else "Black's Turn"
        pygame.display.set_caption(f"Chessboard - {turn_text}")

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
