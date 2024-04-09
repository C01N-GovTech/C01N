from badge import oled, btn
from time import sleep_ms
from random import choice
import copy

# Define constants
GRID_SIZE = 3
CELL_SIZE = 21  # Adjusted to fit the screen
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE

# Define colors
COLOR_BLACK = 0
COLOR_WHITE = 1

class TicTacToeGame:
    def __init__(self, player_mode):
        self.grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.selected_row = 0
        self.selected_col = 0
        self.player_mode = player_mode
        
        if self.player_mode == "Robot":
            self.current_player = 'O'  # Let the AI (O) play first

    def check_winner(self, grid):
        # Check rows
        for row in grid:
            if row[0] == row[1] == row[2] != ' ':
                return row[0]

        # Check columns
        for col in range(GRID_SIZE):
            if grid[0][col] == grid[1][col] == grid[2][col] != ' ':
                return grid[0][col]

        # Check diagonals
        if grid[0][0] == grid[1][1] == grid[2][2] != ' ':
            return grid[0][0]
        if grid[0][2] == grid[1][1] == grid[2][0] != ' ':
            return grid[0][2]

        # Check if it's a draw
        if all([cell != ' ' for row in grid for cell in row]):
            return 'Draw'

        return None

    def draw(self):
        oled.fill(0)

        # Draw grid lines
        for i in range(GRID_SIZE + 1):
            oled.vline(i * CELL_SIZE, 0, GRID_HEIGHT, COLOR_WHITE)
            oled.hline(0, i * CELL_SIZE, GRID_WIDTH, COLOR_WHITE)

        # Highlight selected box
        oled.rect(self.selected_col * CELL_SIZE, self.selected_row * CELL_SIZE, CELL_SIZE, CELL_SIZE, COLOR_WHITE)

        # Draw X's and O's
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == 'X':
                    self.draw_x(row, col)
                elif self.grid[row][col] == 'O':
                    self.draw_o(row, col)

        # Draw turn indicator
        if not self.game_over:
            oled.text("Your" if self.current_player == 'X' else "Opponent", GRID_WIDTH + 5, 15, COLOR_WHITE)
            oled.text("Turn", GRID_WIDTH + 5, 30, COLOR_WHITE)

        oled.show()

    def draw_x(self, row, col):
        oled.line(col * CELL_SIZE + 2, row * CELL_SIZE + 2, (col + 1) * CELL_SIZE - 2, (row + 1) * CELL_SIZE - 2, COLOR_WHITE)
        oled.line((col + 1) * CELL_SIZE - 2, row * CELL_SIZE + 2, col * CELL_SIZE + 2, (row + 1) * CELL_SIZE - 2, COLOR_WHITE)

    def draw_o(self, row, col):
        oled.circle(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 2, COLOR_WHITE)

    def handle_input(self):
        if self.player_mode != "Robot":
            # Handle button presses for selecting boxes
            if btn.U.value() == 0:
                self.selected_row = (self.selected_row - 1) % GRID_SIZE
            elif btn.D.value() == 0:
                self.selected_row = (self.selected_row + 1) % GRID_SIZE
            elif btn.L.value() == 0:
                self.selected_col = (self.selected_col - 1) % GRID_SIZE
            elif btn.R.value() == 0:
                self.selected_col = (self.selected_col + 1) % GRID_SIZE
            elif btn.A.value() == 0:
                if self.grid[self.selected_row][self.selected_col] == ' ':
                    self.grid[self.selected_row][self.selected_col] = self.current_player
                    self.game_over = self.check_winner(self.grid) is not None
                    if not self.game_over:
                        self.current_player = 'O' if self.current_player == 'X' else 'X'

        if self.player_mode == "Robot" and self.current_player == 'O' and not self.game_over:
            self.make_ai_move()

    def make_ai_move(self):
        # Check for winning move for AI
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == ' ':
                    temp_grid = copy.deepcopy(self.grid)
                    temp_grid[i][j] = 'O'
                    if self.check_winner(temp_grid) == 'O':
                        self.grid[i][j] = 'O'
                        self.game_over = True
                        self.winner = 'O'
                        return

        # Check for winning move for player and block it
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == ' ':
                    temp_grid = copy.deepcopy(self.grid)
                    temp_grid[i][j] = 'X'
                    if self.check_winner(temp_grid) == 'X':
                        self.grid[i][j] = 'O'
                        return

        # Make a random move
        empty_cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if self.grid[i][j] == ' ']
        if empty_cells:
            row, col = choice(empty_cells)
            self.grid[row][col] = 'O'

def start_page():
    oled.fill(0)
    oled.text("Select Mode:", 5, 10, COLOR_WHITE)
    oled.text("[A] Robot", 5, 30, COLOR_WHITE)
    oled.text("[B] 2 Players", 5, 45, COLOR_WHITE)
    oled.show()

    while True:
        if btn.A.value() == 0:
            return "Robot"
        elif btn.B.value() == 0:
            return "2 Player"

def end_game(winner):
    oled.fill(0)
    if winner == 'Draw':
        oled.text("Draw", 48, 20, COLOR_WHITE)
    else:
        oled.text("Win" if winner == 'X' else "Lose", 48, 20, COLOR_WHITE)
    oled.text("[U] to Exit", 20, 40, COLOR_WHITE)
    oled.show()

    while True:
        if btn.U.value() == 0:
            return

def app_start():
    player_mode = start_page()

    if player_mode == "Robot":
        game = TicTacToeGame(player_mode)
        while not game.game_over:
            game.handle_input()
            game.draw()
            sleep_ms(100)
        end_game(game.check_winner(game.grid))
    elif player_mode == "2 Player":
        game = TicTacToeGame(player_mode)
        while not game.game_over:
            game.handle_input()
            game.draw()
            sleep_ms(100)
        end_game(game.check_winner(game.grid))

app_start()


# from badge import oled, btn
# from time import sleep_ms
# from random import choice
# import copy

# # Define constants
# GRID_SIZE = 3
# CELL_SIZE = 21  # Adjusted to fit the screen
# GRID_WIDTH = GRID_SIZE * CELL_SIZE
# GRID_HEIGHT = GRID_SIZE * CELL_SIZE

# # Define colors
# COLOR_BLACK = 0
# COLOR_WHITE = 1

# class TicTacToeGame:
#     def __init__(self, player_mode):
#         self.grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
#         self.current_player = 'X'
#         self.game_over = False
#         self.winner = None
#         self.selected_row = 0
#         self.selected_col = 0
#         self.player_mode = player_mode
        
#         if self.player_mode == "Robot":
#             self.current_player = 'O'  # Let the AI (O) play first

#     def check_winner(self, grid):
#         # Check rows
#         for row in grid:
#             if row[0] == row[1] == row[2] != ' ':
#                 return row[0]

#         # Check columns
#         for col in range(GRID_SIZE):
#             if grid[0][col] == grid[1][col] == grid[2][col] != ' ':
#                 return grid[0][col]

#         # Check diagonals
#         if grid[0][0] == grid[1][1] == grid[2][2] != ' ':
#             return grid[0][0]
#         if grid[0][2] == grid[1][1] == grid[2][0] != ' ':
#             return grid[0][2]

#         # Check if it's a draw
#         if all([cell != ' ' for row in grid for cell in row]):
#             return 'Draw'

#         return None

#     def draw(self):
#         oled.fill(0)

#         # Draw grid lines
#         for i in range(GRID_SIZE + 1):
#             oled.vline(i * CELL_SIZE, 0, GRID_HEIGHT, COLOR_WHITE)
#             oled.hline(0, i * CELL_SIZE, GRID_WIDTH, COLOR_WHITE)

#         # Highlight selected box
#         oled.rect(self.selected_col * CELL_SIZE, self.selected_row * CELL_SIZE, CELL_SIZE, CELL_SIZE, COLOR_WHITE)

#         # Draw X's and O's
#         for row in range(GRID_SIZE):
#             for col in range(GRID_SIZE):
#                 if self.grid[row][col] == 'X':
#                     self.draw_x(row, col)
#                 elif self.grid[row][col] == 'O':
#                     self.draw_o(row, col)

#         # Draw turn indicator
#         if not self.game_over:
#             oled.text("Your" if self.current_player == 'X' else "Opponent", GRID_WIDTH + 5, 15, COLOR_WHITE)
#             oled.text("Turn", GRID_WIDTH + 5, 30, COLOR_WHITE)

#         oled.show()

#     def draw_x(self, row, col):
#         oled.line(col * CELL_SIZE + 2, row * CELL_SIZE + 2, (col + 1) * CELL_SIZE - 2, (row + 1) * CELL_SIZE - 2, COLOR_WHITE)
#         oled.line((col + 1) * CELL_SIZE - 2, row * CELL_SIZE + 2, col * CELL_SIZE + 2, (row + 1) * CELL_SIZE - 2, COLOR_WHITE)

#     def draw_o(self, row, col):
#         oled.circle(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 2, COLOR_WHITE)

#     def handle_input(self):
#         if self.player_mode != "Robot":
#             # Handle button presses for selecting boxes
#             if btn.U.value() == 0:
#                 self.selected_row = (self.selected_row - 1) % GRID_SIZE
#             elif btn.D.value() == 0:
#                 self.selected_row = (self.selected_row + 1) % GRID_SIZE
#             elif btn.L.value() == 0:
#                 self.selected_col = (self.selected_col - 1) % GRID_SIZE
#             elif btn.R.value() == 0:
#                 self.selected_col = (self.selected_col + 1) % GRID_SIZE
#             elif btn.A.value() == 0:
#                 if self.grid[self.selected_row][self.selected_col] == ' ':
#                     self.grid[self.selected_row][self.selected_col] = self.current_player
#                     self.game_over = self.check_winner(self.grid) is not None
#                     if not self.game_over:
#                         self.current_player = 'O' if self.current_player == 'X' else 'X'

#         if self.player_mode == "Robot" and self.current_player == 'O' and not self.game_over:
#             self.make_ai_move()

#     def make_ai_move(self):
#         # Define the depth of the lookahead for the minimax algorithm
#         depth = 3  # Adjust this value for desired difficulty level
        
#         best_score = float('-inf')
#         best_move = None

#         # Iterate over all empty cells and simulate each move
#         for i in range(GRID_SIZE):
#             for j in range(GRID_SIZE):
#                 if self.grid[i][j] == ' ':
#                     # Make a copy of the current game state
#                     temp_grid = copy.deepcopy(self.grid)
#                     # Try making the move
#                     temp_grid[i][j] = 'O'
#                     score = self.minimax(temp_grid, depth, False)
#                     # Update best move if score is better
#                     if score > best_score:
#                         best_score = score
#                         best_move = (i, j)

#         # Make the best move
#         if best_move:
#             self.grid[best_move[0]][best_move[1]] = 'O'
#             self.game_over = self.check_winner(self.grid) is not None
#             if not self.game_over:
#                 self.current_player = 'X'

#     def minimax(self, temp_grid, depth, is_maximizing):
#         # Check if the game is over or the depth limit is reached
#         winner = self.check_winner(temp_grid)
#         if winner is not None or depth == 0:
#             if winner == 'O':
#                 return 1
#             elif winner == 'X':
#                 return -1
#             else:
#                 return 0

#         if is_maximizing:
#             best_score = float('-inf')
#             for i in range(GRID_SIZE):
#                 for j in range(GRID_SIZE):
#                     if temp_grid[i][j] == ' ':
#                         temp_grid[i][j] = 'O'
#                         score = self.minimax(temp_grid, depth - 1, False)
#                         temp_grid[i][j] = ' '
#                         best_score = max(score, best_score)
#             return best_score
#         else:
#             best_score = float('inf')
#             for i in range(GRID_SIZE):
#                 for j in range(GRID_SIZE):
#                     if temp_grid[i][j] == ' ':
#                         temp_grid[i][j] = 'X'
#                         score = self.minimax(temp_grid, depth - 1, True)
#                         temp_grid[i][j] = ' '
#                         best_score = min(score, best_score)
#             return best_score

# def start_page():
#     oled.fill(0)
#     oled.text("Select Mode:", 5, 10, COLOR_WHITE)
#     oled.text("[A] Robot", 5, 30, COLOR_WHITE)
#     oled.text("[B] 2 Players", 5, 45, COLOR_WHITE)
#     oled.show()

#     while True:
#         if btn.A.value() == 0:
#             return "Robot"
#         elif btn.B.value() == 0:
#             return "2 Player"

# def end_game(winner):
#     oled.fill(0)
#     if winner == 'Draw':
#         oled.text("Draw", 48, 20, COLOR_WHITE)
#     else:
#         oled.text("Win" if winner == 'X' else "Lose", 48, 20, COLOR_WHITE)
#     oled.text("[U] to Exit", 20, 40, COLOR_WHITE)
#     oled.show()

#     while True:
#         if btn.U.value() == 0:
#             return

# def app_start():
#     player_mode = start_page()

#     if player_mode == "Robot":
#         game = TicTacToeGame(player_mode)
#         while not game.game_over:
#             game.handle_input()
#             game.draw()
#             sleep_ms(100)
#         end_game(game.check_winner(game.grid))
#     elif player_mode == "2 Player":
#         game = TicTacToeGame(player_mode)
#         while not game.game_over:
#             game.handle_input()
#             game.draw()
#             sleep_ms(100)
#         end_game(game.check_winner(game.grid))

# app_start()



# from badge import oled, btn
# from time import sleep_ms
# from random import choice
# import copy

# # Define constants
# GRID_SIZE = 3
# CELL_SIZE = 21  # Adjusted to fit the screen
# GRID_WIDTH = GRID_SIZE * CELL_SIZE
# GRID_HEIGHT = GRID_SIZE * CELL_SIZE

# # Define colors
# COLOR_BLACK = 0
# COLOR_WHITE = 1

# class TicTacToeGame:
#     def __init__(self, player_mode):
#         self.grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
#         self.current_player = 'X'
#         self.game_over = False
#         self.winner = None
#         self.selected_row = 0
#         self.selected_col = 0
#         self.player_mode = player_mode
        
#         if self.player_mode == "Robot":
#             self.current_player = 'O'  # Let the AI (O) play first

#     def check_winner(self, grid):
#         # Check rows
#         for row in grid:
#             if row[0] == row[1] == row[2] != ' ':
#                 return row[0]

#         # Check columns
#         for col in range(GRID_SIZE):
#             if grid[0][col] == grid[1][col] == grid[2][col] != ' ':
#                 return grid[0][col]

#         # Check diagonals
#         if grid[0][0] == grid[1][1] == grid[2][2] != ' ':
#             return grid[0][0]
#         if grid[0][2] == grid[1][1] == grid[2][0] != ' ':
#             return grid[0][2]

#         # Check if it's a draw
#         if all([cell != ' ' for row in grid for cell in row]):
#             return 'Draw'

#         return None

#     def draw(self):
#         oled.fill(0)

#         # Draw grid lines
#         for i in range(GRID_SIZE + 1):
#             oled.vline(i * CELL_SIZE, 0, GRID_HEIGHT, COLOR_WHITE)
#             oled.hline(0, i * CELL_SIZE, GRID_WIDTH, COLOR_WHITE)

#         # Highlight selected box
#         oled.rect(self.selected_col * CELL_SIZE, self.selected_row * CELL_SIZE, CELL_SIZE, CELL_SIZE, COLOR_WHITE)

#         # Draw X's and O's
#         for row in range(GRID_SIZE):
#             for col in range(GRID_SIZE):
#                 if self.grid[row][col] == 'X':
#                     self.draw_x(row, col)
#                 elif self.grid[row][col] == 'O':
#                     self.draw_o(row, col)

#         # Draw turn indicator
#         if not self.game_over:
#             oled.text("Your" if self.current_player == 'X' else "Opponent", GRID_WIDTH + 5, 15, COLOR_WHITE)
#             oled.text("Turn", GRID_WIDTH + 5, 30, COLOR_WHITE)

#         oled.show()

#     def draw_x(self, row, col):
#         oled.line(col * CELL_SIZE + 2, row * CELL_SIZE + 2, (col + 1) * CELL_SIZE - 2, (row + 1) * CELL_SIZE - 2, COLOR_WHITE)
#         oled.line((col + 1) * CELL_SIZE - 2, row * CELL_SIZE + 2, col * CELL_SIZE + 2, (row + 1) * CELL_SIZE - 2, COLOR_WHITE)

#     def draw_o(self, row, col):
#         oled.circle(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 - 2, COLOR_WHITE)

#     def handle_input(self):
#         if self.player_mode != "Robot":
#             # Handle button presses for selecting boxes
#             if btn.U.value() == 0:
#                 self.selected_row = (self.selected_row - 1) % GRID_SIZE
#             elif btn.D.value() == 0:
#                 self.selected_row = (self.selected_row + 1) % GRID_SIZE
#             elif btn.L.value() == 0:
#                 self.selected_col = (self.selected_col - 1) % GRID_SIZE
#             elif btn.R.value() == 0:
#                 self.selected_col = (self.selected_col + 1) % GRID_SIZE
#             elif btn.A.value() == 0:
#                 if self.grid[self.selected_row][self.selected_col] == ' ':
#                     self.grid[self.selected_row][self.selected_col] = self.current_player
#                     self.game_over = self.check_winner(self.grid) is not None
#                     if not self.game_over:
#                         self.current_player = 'O' if self.current_player == 'X' else 'X'

#         if self.player_mode == "Robot" and self.current_player == 'O' and not self.game_over:
#             self.make_ai_move()

#     def make_ai_move(self):
#         best_score = float('-inf')
#         best_move = None

#         # Iterate over all empty cells and simulate each move
#         for i in range(GRID_SIZE):
#             for j in range(GRID_SIZE):
#                 if self.grid[i][j] == ' ':
#                     # Make a copy of the current game state
#                     temp_grid = copy.deepcopy(self.grid)
#                     # Make the move
#                     temp_grid[i][j] = 'O'
#                     score = self.minimax(temp_grid, False)
#                     # Update best move if score is better
#                     if score > best_score:
#                         best_score = score
#                         best_move = (i, j)

#         # Make the best move
#         if best_move:
#             self.grid[best_move[0]][best_move[1]] = 'O'
#             self.game_over = self.check_winner(self.grid) is not None
#             if not self.game_over:
#                 self.current_player = 'X'

#     def minimax(self, temp_grid, is_maximizing):
#         # Check if the game is over
#         winner = self.check_winner(temp_grid)
#         if winner is not None:
#             if winner == 'O':
#                 return 1
#             elif winner == 'X':
#                 return -1
#             else:
#                 return 0

#         if is_maximizing:
#             best_score = float('-inf')
#             for i in range(GRID_SIZE):
#                 for j in range(GRID_SIZE):
#                     if temp_grid[i][j] == ' ':
#                         temp_grid[i][j] = 'O'
#                         score = self.minimax(temp_grid, False)
#                         temp_grid[i][j] = ' '
#                         best_score = max(score, best_score)
#             return best_score
#         else:
#             best_score = float('inf')
#             for i in range(GRID_SIZE):
#                 for j in range(GRID_SIZE):
#                     if temp_grid[i][j] == ' ':
#                         temp_grid[i][j] = 'X'
#                         score = self.minimax(temp_grid, True)
#                         temp_grid[i][j] = ' '
#                         best_score = min(score, best_score)
#             return best_score

# def start_page():
#     oled.fill(0)
#     oled.text("Select Mode:", 5, 10, COLOR_WHITE)
#     oled.text("[A] Robot", 5, 30, COLOR_WHITE)
#     oled.text("[B] 2 Players", 5, 45, COLOR_WHITE)
#     oled.show()

#     while True:
#         if btn.A.value() == 0:
#             return "Robot"
#         elif btn.B.value() == 0:
#             return "2 Player"

# def end_game(winner):
#     oled.fill(0)
#     if winner == 'Draw':
#         oled.text("Draw", 48, 20, COLOR_WHITE)
#     else:
#         oled.text("Win" if winner == 'X' else "Lose", 48, 20, COLOR_WHITE)
#     oled.text("[U] to Exit", 20, 40, COLOR_WHITE)
#     oled.show()

#     while True:
#         if btn.U.value() == 0:
#             return

# def app_start():
#     player_mode = start_page()

#     if player_mode == "Robot":
#         game = TicTacToeGame(player_mode)
#         while not game.game_over:
#             game.handle_input()
#             game.draw()
#             sleep_ms(100)
#         end_game(game.check_winner(game.grid))
#     elif player_mode == "2 Player":
#         game = TicTacToeGame(player_mode)
#         while not game.game_over:
#             game.handle_input()
#             game.draw()
#             sleep_ms(100)
#         end_game(game.check_winner(game.grid))

# app_start()

# from badge import oled, btn
# from time import sleep_ms

# # Define constants
# CELL_SIZE = 8
# GRID_SIZE = 8
# GRID_WIDTH = GRID_SIZE * CELL_SIZE
# GRID_HEIGHT = GRID_SIZE * CELL_SIZE
# DISPLAY_WIDTH = 128
# DISPLAY_HEIGHT = 64

# # Define colors
# COLOR_BLACK = 0
# COLOR_WHITE = 1

# class ReversiGame:
#     def __init__(self):
#         self.board = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
#         self.board[3][3] = 'W'
#         self.board[4][4] = 'W'
#         self.board[3][4] = 'B'
#         self.board[4][3] = 'B'
#         self.current_player = 'B'  # Black plays first
#         self.selected_cell = [3, 2]  # Initial selected cell
#         self.scroll_offset = [0, 0]

#     def draw(self):
#         oled.fill(0)

#         # Draw gridlines
#         for i in range(GRID_SIZE):
#              for j in range(GRID_SIZE):
#                  x = i * CELL_SIZE
#                  y = j * CELL_SIZE
#                  oled.rect(x, y, CELL_SIZE, CELL_SIZE, COLOR_BLACK)

#         # Draw pieces
#         for i in range(GRID_SIZE):
#             for j in range(GRID_SIZE):
#                 x = i * CELL_SIZE
#                 y = j * CELL_SIZE
#                 if self.board[i][j] == 'B':
#                     self.draw_black_cross(x, y)
#                 elif self.board[i][j] == 'W':
#                     self.draw_piece(x, y, COLOR_WHITE)

#         # Highlight selected cell
#         x = self.selected_cell[0] * CELL_SIZE
#         y = self.selected_cell[1] * CELL_SIZE
#         oled.rect(x, y, CELL_SIZE, CELL_SIZE, COLOR_WHITE)

#         oled.show()

#     def draw_piece(self, x, y, color):
#         piece_size = CELL_SIZE // 2
#         piece_x = x + CELL_SIZE // 2
#         piece_y = y + CELL_SIZE // 2
#         oled.fill_circle(piece_x, piece_y, piece_size, color)

#     def draw_black_cross(self, x, y):
#         cross_size = CELL_SIZE // 2
#         cross_x = x + CELL_SIZE // 2
#         cross_y = y + CELL_SIZE // 2
#         oled.line(cross_x - cross_size, cross_y - cross_size, cross_x + cross_size, cross_y + cross_size, COLOR_WHITE)
#         oled.line(cross_x + cross_size, cross_y - cross_size, cross_x - cross_size, cross_y + cross_size, COLOR_WHITE)

#     def handle_input(self):
#         initial_selected_cell = self.selected_cell.copy()

#         if btn.U.value() == 0:
#             if self.selected_cell[1] > 0:
#                 self.selected_cell[1] -= 1
#         elif btn.D.value() == 0:
#             if self.selected_cell[1] < GRID_SIZE - 1:
#                 self.selected_cell[1] += 1
#         elif btn.L.value() == 0:
#             if self.selected_cell[0] > 0:
#                 self.selected_cell[0] -= 1
#         elif btn.R.value() == 0:
#             if self.selected_cell[0] < GRID_SIZE - 1:
#                 self.selected_cell[0] += 1
#         elif btn.A.value() == 0:  # Place piece
#             if self.is_valid_move():
#                 self.place_piece()
#                 self.current_player = 'W' if self.current_player == 'B' else 'B'

#         if initial_selected_cell != self.selected_cell:
#             self.scroll_offset[0] = min(max(0, self.scroll_offset[0]), GRID_WIDTH - DISPLAY_WIDTH)
#             self.scroll_offset[1] = min(max(0, self.scroll_offset[1]), GRID_HEIGHT - DISPLAY_HEIGHT)

#     def is_valid_move(self):
#         x, y = self.selected_cell
#         if self.board[x][y] != ' ':
#             return False
#         for dx in range(-1, 2):
#             for dy in range(-1, 2):
#                 if dx == 0 and dy == 0:
#                     continue
#                 if self.check_and_flip(x, y, dx, dy, self.current_player):
#                     return True
#         return False

#     def place_piece(self):
#         x, y = self.selected_cell
#         self.board[x][y] = self.current_player
#         for dx in range(-1, 2):
#             for dy in range(-1, 2):
#                 if dx == 0 and dy == 0:
#                     continue
#                 self.check_and_flip(x, y, dx, dy, self.current_player)

#     def check_and_flip(self, x, y, dx, dy, player):
#         nx, ny = x + dx, y + dy
#         to_flip = []
#         while 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.board[nx][ny] != ' ' and self.board[nx][ny] != player:
#             to_flip.append((nx, ny))
#             nx += dx
#             ny += dy
#         if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.board[nx][ny] == player:
#             for flip_x, flip_y in to_flip:
#                 self.board[flip_x][flip_y] = player
#             return True
#         return False

#     def is_game_over(self):
#         for row in self.board:
#             if ' ' in row:
#                 return False
#         return True

# def app_start():
#     game = ReversiGame()

#     while not game.is_game_over():
#         game.handle_input()
#         game.draw()
#         sleep_ms(100)

#     oled.fill(0)
#     oled.text("Game Over!", 30, 28, COLOR_WHITE)
#     oled.show()

#     while True:
#         pass

# app_start()
