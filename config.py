import os
import numpy as np

# Define the window dimensions
WINDOW_WIDTH = 550
WINDOW_HEIGHT = 475

# Define the top bar dimensions
TOP_BAR_HEIGHT = 75

# Define the side bar dimensions
SIDE_BAR_WIDTH = 150

# Define the chessboard dimensions
CHESSBOARD_SIZE = 8
SQUARE_SIZE = (WINDOW_WIDTH - SIDE_BAR_WIDTH) // CHESSBOARD_SIZE

PIECE_SIZE_SCALE = 0.75

LINE_THICKNESS = 5

STARTING_BOARD = np.array([
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
     ])


COLUMN_LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']


def load_pieces_from_folder(folder_path):
    piece_mapping = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            piece_color = filename[0]
            piece_type = filename[2]
            notation = piece_type.upper() if piece_color == 'w' else piece_type.lower()
            piece_mapping[notation] = filename

    return piece_mapping


PIECE_MAPPING = load_pieces_from_folder("assets")