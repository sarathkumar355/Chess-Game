import pygame, chess
from random import choice
from traceback import format_exc
from sys import stderr
from time import strftime, time



pygame.init()

SQUARE_SIDE = 50
AI_SEARCH_DEPTH = 2

# Colors
RED_CHECK = (240, 150, 150)
WHITE = (255, 255, 255)
BLUE_LIGHT = (140, 184, 219)
BLUE_DARK = (91, 131, 159)
GRAY_LIGHT = (240, 240, 240)
GRAY_DARK = (200, 200, 200)
GREEN_HIGHLIGHT = (0, 255, 0)
RED_HIGHLIGHT = (255, 0, 0)
BLACK = (0, 0, 0)

BOARD_COLORS = [(GRAY_LIGHT, GRAY_DARK), (BLUE_LIGHT, BLUE_DARK)]
BOARD_COLOR = choice(BOARD_COLORS)

# Improved Image Loading
def load_image(path):
    try:
        return pygame.image.load(path)
    except pygame.error:
        print(f"Error loading image: {path}")
        return pygame.Surface((SQUARE_SIDE, SQUARE_SIDE))

# Piece Images
piece_images = {
    'K': load_image('images/black_king.png'),
    'Q': load_image('images/black_queen.png'),
    'R': load_image('images/black_rook.png'),
    'B': load_image('images/black_bishop.png'),
    'N': load_image('images/black_knight.png'),
    'P': load_image('images/black_pawn.png'),
    'k': load_image('images/white_king.png'),
    'q': load_image('images/white_queen.png'),
    'r': load_image('images/white_rook.png'),
    'b': load_image('images/white_bishop.png'),
    'n': load_image('images/white_knight.png'),
    'p': load_image('images/white_pawn.png'),
}

# Screen Configuration
CLOCK = pygame.time.Clock()
CLOCK_TICK = 15
SCREEN = pygame.display.set_mode((8 * SQUARE_SIDE, 8 * SQUARE_SIDE + 50))  # Extra space for the clock
SCREEN_TITLE = 'Chess Game'
pygame.display.set_caption(SCREEN_TITLE)

# Font for displaying the timer
FONT = pygame.font.SysFont("Arial", 24)

# Tracking Moves
move_history = []
redo_moves = []

# Timer for game clock
start_time = time()

def resize_screen(square_side_len):
    global SQUARE_SIDE, SCREEN
    SCREEN = pygame.display.set_mode((8 * square_side_len, 8 * square_side_len + 50), pygame.RESIZABLE)
    SQUARE_SIDE = square_side_len

def print_empty_board():
    SCREEN.fill(BOARD_COLOR[0])
    paint_dark_squares(BOARD_COLOR[1])

def paint_square(square, square_color):
    col, row = chess.square_file(square), chess.square_rank(square)
    pygame.draw.rect(SCREEN, square_color, (SQUARE_SIDE * col, SQUARE_SIDE * (7 - row), SQUARE_SIDE, SQUARE_SIDE))

def paint_dark_squares(square_color):
    for square in chess.SQUARES:
        if (chess.square_file(square) + chess.square_rank(square)) % 2 == 1:
            paint_square(square, square_color)

def get_square_rect(square):
    col, row = chess.square_file(square), chess.square_rank(square)
    return pygame.Rect((col * SQUARE_SIDE, (7 - row) * SQUARE_SIDE), (SQUARE_SIDE, SQUARE_SIDE))

def print_board(board, selected_square=None):
    print_empty_board()

    # Highlight valid moves
    if selected_square is not None:
        for move in board.legal_moves:
            if move.from_square == selected_square:
                target_square = move.to_square
                highlight_color = RED_HIGHLIGHT if board.piece_at(target_square) else GREEN_HIGHLIGHT
                paint_square(target_square, highlight_color)

    # Draw pieces
    for square, piece in board.piece_map().items():
        img = piece_images.get(piece.symbol(), None)
        if img:
            SCREEN.blit(pygame.transform.scale(img, (SQUARE_SIDE, SQUARE_SIDE)), get_square_rect(square))

    # Display Game Clock
    elapsed_time = int(time() - start_time)
    time_text = FONT.render(f"Time: {elapsed_time // 60}:{elapsed_time % 60:02}", True, BLACK)
    SCREEN.blit(time_text, (10, 8 * SQUARE_SIDE + 10))

    pygame.display.flip()

def ai_move(board):
    possible_moves = list(board.legal_moves)
    if possible_moves:
        move = choice(possible_moves)
        board.push(move)

def play_as(game, color):
    run = True
    selected_square = None  

    try:
        while run:
            CLOCK.tick(CLOCK_TICK)
            print_board(game, selected_square)

            if game.is_checkmate() or game.is_stalemate():
                set_title(f"{SCREEN_TITLE} - Game Over")
                break  

            if game.turn != color:
                ai_move(game)
                print_board(game)
                pygame.display.update()  

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False

                    elif event.key == pygame.K_u and len(move_history) > 0:  
                        game.pop()
                        redo_moves.append(move_history.pop())  # Save for redo

                    elif event.key == pygame.K_r and len(redo_moves) > 0:  
                        next_move = redo_moves.pop()
                        if next_move in game.legal_moves:
                            game.push(next_move)
                            move_history.append(next_move)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    clicked_square = chess.square(x // SQUARE_SIDE, 7 - (y // SQUARE_SIDE))

                    if selected_square is None:
                        piece = game.piece_at(clicked_square)
                        if piece and piece.color == color:
                            selected_square = clicked_square
                        else:
                            print("⚠️ Invalid piece selection!")
                    else:
                        move = chess.Move(selected_square, clicked_square)
                        
                        if game.piece_at(selected_square).symbol().lower() == 'p' and \
                           (chess.square_rank(clicked_square) == 0 or chess.square_rank(clicked_square) == 7):
                            move = chess.Move(selected_square, clicked_square, promotion=chess.QUEEN)

                        if move in game.legal_moves:
                            game.push(move)
                            move_history.append(move)
                            print_board(game)
                            pygame.display.update()  
                        else:
                            print("❌ Invalid move attempted!")
                        selected_square = None  

                if event.type == pygame.VIDEORESIZE:
                    resize_screen(int(event.h / 8.0))
                    print_board(game)

    except Exception:
        print(format_exc(), file=stderr)
        with open('bug_report.txt', 'a') as bug_file:
            bug_file.write(f'----- {strftime("%x %X")} -----\n')
            bug_file.write(format_exc())
            bug_file.write('\n-----------------------------\n\n')

def set_title(title):
    pygame.display.set_caption(title)
    pygame.display.flip()

# Start Game
play_as(chess.Board(), chess.WHITE)
