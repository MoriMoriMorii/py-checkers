import pygame
import sys

# Constants
WIDTH, HEIGHT = 700, 700
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
legal_moves = {}
pygame.mixer.init()
music = pygame.mixer.Channel(0)
sound_effects = pygame.mixer.Channel(1)

bgm = pygame.mixer.Sound("bgm.mp3")
king_sound = pygame.mixer.Sound("cr.mp3")
move_sound = pygame.mixer.Sound("move.mp3")
capture_sound = pygame.mixer.Sound("capture.mp3")
# Initialize Pygame
pygame.init()

# Create the game board
board = [
    [0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 2, 0, 2, 0, 2, 0],
    [0, 2, 0, 2, 0, 2, 0, 2],
    [2, 0, 2, 0, 2, 0, 2, 0]
]

# Initialize Pygame window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Checkers Game")
music.play(bgm, -1)
# Function to draw the board
def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(window, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Function to draw the pieces
def draw_pieces():
    for row in range(ROWS):
        for col in range(COLS):
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)

            if board[row][col] == 1:
                pygame.draw.circle(window, RED, center, SQUARE_SIZE // 2 - 10)
            elif board[row][col] == 2:
                pygame.draw.circle(window, WHITE, center, SQUARE_SIZE // 2 - 10)
            elif board[row][col] == 3:
                pygame.draw.circle(window, RED, center, SQUARE_SIZE // 2 - 10)
                pygame.draw.circle(window, BLACK, center, SQUARE_SIZE // 4)
            elif board[row][col] == 4:
                pygame.draw.circle(window, WHITE, center, SQUARE_SIZE // 2 - 10)
                pygame.draw.circle(window, BLACK, center, SQUARE_SIZE // 4)
                pygame.draw.circle(window, BLACK, center, 5)  # Draw a dot for kinged pieces


# Function to move a piece
def move_piece(row, col, new_row, new_col):
    board[new_row][new_col] = board[row][col]
    board[row][col] = 0
    sound_effects.play(move_sound)
    # Check for king promotion
    if (player == 1 and new_row == ROWS - 1 and board[new_row][new_col] == 1) or (player == 2 and new_row == 0 and board[new_row][new_col] == 2):
        promote_to_king(new_row, new_col)
        sound_effects.play(king_sound)
# Function to promote a piece to king
def promote_to_king(row, col):
    if board[row][col] == 1:
        board[row][col] = 3  # Kinged piece for player 1
    elif board[row][col] == 2:
        board[row][col] = 4  # Kinged piece for player 2
    elif board[row][col] == 3:
        board[row][col] = 3  # Ensure a king stays a king for player 1
    elif board[row][col] == 4:
        board[row][col] = 4  # Ensure a king stays a king for player 2


def perform_capture(start_row, start_col, end_row, end_col, board):
    global pieces_taken_player1, pieces_taken_player2  # Declare as global variables

    captured_row = (start_row + end_row) // 2
    captured_col = (start_col + end_col) // 2

    # Increment captured pieces count
    captured_piece = board[captured_row][captured_col]
    if captured_piece == 1:
        print("White Takes!")
        pieces_taken_player1 += 1
    elif captured_piece == 2:
        print("Red Takes!")
        pieces_taken_player2 += 1

    # Update the board to remove the captured piece
    board[captured_row][captured_col] = 0
    sound_effects.play(capture_sound)



# Function to get legal moves for a selected piece
def get_legal_moves(row, col, player, pieces_taken_player1, pieces_taken_player2):
    legal_moves = []
    directions = [1, -1] if player == 1 else [-1, 1]

    # Check if the piece is kinged
    is_kinged = board[row][col] in [3, 4]

    for d in directions:
        for dc in directions:
            new_row, new_col = row + d, col + dc

            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                # Empty square, regular move
                if board[new_row][new_col] == 0 and (is_kinged or (player == 1 and d == 1) or (player == 2 and d == -1)):
                    legal_moves.append((new_row, new_col))

                # Capture move
                elif (
                    is_kinged
                    and 0 <= col + 2 * dc < COLS
                    and 0 <= row + 2 * d < ROWS
                    and board[row + d][col + dc] != 0
                    and board[row + 2 * d][col + 2 * dc] == 0
                    and board[row + d][col + dc] != player
                ) or (
                    not is_kinged
                    and 0 <= col + 2 * dc < COLS
                    and 0 <= row + 2 * d < ROWS
                    and board[row + d][col + dc] != 0
                    and board[row + 2 * d][col + 2 * dc] == 0
                    and board[row + d][col + dc] != player
                    and ((player == 1 and d == 1) or (player == 2 and d == -1))
                ):
                    capturing_piece = board[row + d][col + dc]
                    if capturing_piece != player and capturing_piece != player + 2:  # Ensure not capturing a piece of the same color
                        legal_moves.append((row + 2 * d, col + 2 * dc))

    return legal_moves
# Main game loop
player = 1  # Player 1 starts
running = True
selected_piece = None  # Initialize selected piece
score = {1: 0, 2: 0}  # Initialize score
totals_printed = False
# Counters for pieces taken on each side
pieces_taken_player1 = 0
pieces_taken_player2 = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get mouse position
            mouseX, mouseY = pygame.mouse.get_pos()
            row = mouseY // SQUARE_SIZE
            col = mouseX // SQUARE_SIZE

            if selected_piece is None:
                if player == 1 and (board[row][col] == 1 or board[row][col] == 3):
                    selected_piece = (row, col)
                    legal_moves = get_legal_moves(row, col, player, pieces_taken_player1, pieces_taken_player2)
                elif player == 2 and (board[row][col] == 2 or board[row][col] == 4):
                    selected_piece = (row, col)
                    legal_moves = get_legal_moves(row, col, player, pieces_taken_player1, pieces_taken_player2)
    # Rest of the code remains the same

            else:
                # Check if the player clicked on the same square
                if (row, col) == selected_piece:
                    selected_piece = None  # Deselect the piece
                    legal_moves = []  # Clear legal moves
                elif (row, col) in legal_moves:
                    move_piece(selected_piece[0], selected_piece[1], row, col)

                    # Check for capturing move
                    if abs(selected_piece[0] - row) == 2:
                        perform_capture(selected_piece[0], selected_piece[1], row, col, board)
                        totals_printed = False
                    # Check for king promotion
                    if player == 1 and row == 0:
                        board[row][col] = 3  # Kinged piece
                    elif player == 2 and row == 7:
                        board[row][col] = 4  # Kinged piece

                    selected_piece = None  # Reset selected piece
                    legal_moves = []  # Reset legal moves

                    # Switch players
                    player = 3 - player  # Toggle between 1 and 2
                else:
                    selected_piece = None  # Deselect the piece
                    legal_moves = []  # Clear legal moves

    # Draw the board and pieces
    draw_board()
    draw_pieces()

    # Highlight selected piece
    if selected_piece is not None:
        pygame.draw.rect(window, GREEN, (selected_piece[1] * SQUARE_SIZE, selected_piece[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

    # Highlight legal moves
    for move in legal_moves:
        pygame.draw.circle(window, BLUE, (move[1] * SQUARE_SIZE + SQUARE_SIZE // 2, move[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 15)
    # Check for a win
    if sum(row.count(1) for row in board) == 0:
        print("Player 2 wins!")
        print("Pieces taken by Red", pieces_taken_player2)
        print("Pieces taken by White:", pieces_taken_player1)
        running = False
    elif sum(row.count(2) for row in board) == 0:
        print("Red wins!")
        print("Pieces taken by Red:", pieces_taken_player2)
        print("Pieces taken by White:", pieces_taken_player1)
        running = False
    elif not totals_printed:
        print("Current Pieces Taken:")
        print("Red:", pieces_taken_player2)
        print("White:", pieces_taken_player1)
        totals_printed = True
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
