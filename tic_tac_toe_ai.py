import tkinter as tk
from tkinter import messagebox, ttk
import time
import random
from pygame import mixer
import os

# Initialize mixer for sound
mixer.init()

# Paths for sound files (use relative path for portability)
BASE_PATH = os.path.dirname(__file__)
MOVE_SOUND = os.path.join(BASE_PATH, "mixkit-select-click-1109.wav")
WIN_SOUND = os.path.join(BASE_PATH, "mixkit-winning-chimes-2015.wav")
DRAW_SOUND = os.path.join(BASE_PATH, "mixkit-success-software-tone-2865.wav")


def play_sound(sound):
    """Play sound file safely."""
    try:
        mixer.Sound(sound).play()
    except Exception as e:
        print(f"Error playing sound: {e}")


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - With AI")
        self.root.geometry("400x500")  # Set window size
        self.root.resizable(False, False)  # Fixed window size

        # Game variables
        self.board = [' '] * 10
        self.buttons = {}
        self.current_player = "Player"
        self.player_marker = 'X'
        self.ai_marker = 'O'

        # Statistics
        self.player_score = 0
        self.ai_score = 0
        self.draws = 0
        self.games_played = 0
        self.move_times = []

        # Game state
        self.game_over = False
        self.ai_thinking = False

        # AI difficulty settings
        self.difficulty_levels = ["Easy", "Medium", "Hard"]
        self.current_difficulty = "Medium"
        self.max_depth = 5  # For limiting AI search depth

        # Create the UI
        self.create_menu()
        self.create_widgets()
        self.update_scoreboard()

        # Apply theme
        self.apply_theme()

    def apply_theme(self):
        """Apply a consistent theme to the UI elements"""
        bg_color = "#f0f0f0"
        button_color = "#e1e1e1"
        self.root.configure(bg=bg_color)

        # Apply to all frames
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color)

        # Style for the game buttons
        for btn in self.buttons.values():
            btn.configure(bg=button_color, activebackground="#d0d0d0",
                          borderwidth=2, relief=tk.RAISED)

    def create_menu(self):
        """Create the menu frame for game controls"""
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(fill=tk.X, padx=10, pady=10)

        # Difficulty selector
        tk.Label(self.menu_frame, text="Difficulty:").pack(side=tk.LEFT, padx=5)
        self.difficulty_var = tk.StringVar(value=self.current_difficulty)
        self.difficulty_menu = ttk.Combobox(self.menu_frame,
                                            textvariable=self.difficulty_var,
                                            values=self.difficulty_levels,
                                            state="readonly",
                                            width=8)
        self.difficulty_menu.pack(side=tk.LEFT, padx=5)
        self.difficulty_menu.bind("<<ComboboxSelected>>", self.change_difficulty)

        # Reset button
        self.reset_button = tk.Button(self.menu_frame, text="New Game",
                                      command=self.reset_board,
                                      width=10)
        self.reset_button.pack(side=tk.RIGHT, padx=5)

        # Stats button
        self.stats_button = tk.Button(self.menu_frame, text="Stats",
                                      command=self.show_stats,
                                      width=8)
        self.stats_button.pack(side=tk.RIGHT, padx=5)

    def create_widgets(self):
        """Create the main game board and UI elements"""
        # Score frame
        self.score_frame = tk.Frame(self.root)
        self.score_frame.pack(fill=tk.X, padx=10, pady=5)

        self.score_label = tk.Label(self.score_frame, text="", font=("Helvetica", 12))
        self.score_label.pack()

        # Game board frame
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(padx=10, pady=10)

        # Create the 3x3 game board
        for i in range(9):
            row, col = divmod(i, 3)
            b = tk.Button(self.board_frame, text=" ", font=("Helvetica", 24),
                          width=3, height=1,
                          command=lambda pos=i + 1: self.player_move(pos))
            b.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            self.buttons[i + 1] = b

        # Configure grid to be responsive
        for i in range(3):
            self.board_frame.grid_columnconfigure(i, weight=1, minsize=80)
            self.board_frame.grid_rowconfigure(i, weight=1, minsize=80)

        # Status frame
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(self.status_frame, text="Your turn", font=("Helvetica", 12))
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.timer_label = tk.Label(self.status_frame, text="", font=("Helvetica", 10))
        self.timer_label.pack(side=tk.RIGHT, padx=5)

    def change_difficulty(self, event=None):
        """Handle difficulty level change"""
        self.current_difficulty = self.difficulty_var.get()

        # Update max search depth based on difficulty
        if self.current_difficulty == "Easy":
            self.max_depth = 1
        elif self.current_difficulty == "Medium":
            self.max_depth = 3
        else:  # Hard
            self.max_depth = 9

        self.status_label.config(text=f"Difficulty set to {self.current_difficulty}")

    def show_stats(self):
        """Display game statistics in a new window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Game Statistics")
        stats_window.geometry("300x250")

        # Calculate win percentages
        win_rate = 0 if self.games_played == 0 else (self.player_score / self.games_played) * 100
        loss_rate = 0 if self.games_played == 0 else (self.ai_score / self.games_played) * 100
        draw_rate = 0 if self.games_played == 0 else (self.draws / self.games_played) * 100

        # Calculate average AI move time
        avg_time = 0 if not self.move_times else sum(self.move_times) / len(self.move_times)

        # Display stats
        tk.Label(stats_window, text="Game Statistics", font=("Helvetica", 14, "bold")).pack(pady=10)

        stats_text = f"""
Games Played: {self.games_played}

Player Wins: {self.player_score} ({win_rate:.1f}%)
AI Wins: {self.ai_score} ({loss_rate:.1f}%)
Draws: {self.draws} ({draw_rate:.1f}%)

Current Difficulty: {self.current_difficulty}
Average AI Move Time: {avg_time:.3f}s
"""

        tk.Label(stats_window, text=stats_text, justify=tk.LEFT).pack(padx=20, pady=10)

        tk.Button(stats_window, text="Close", command=stats_window.destroy).pack(pady=10)

    def player_move(self, pos):
        """Handle the player's move"""
        if self.board[pos] == ' ' and self.current_player == "Player" and not self.game_over:
            self.make_move(pos, self.player_marker)
            play_sound(MOVE_SOUND)

            if self.check_game_end(self.player_marker, "Player"):
                return

            self.current_player = "AI"
            self.status_label.config(text="AI is thinking...")
            self.disable_buttons()

            # Schedule AI move with slight delay for better UX
            self.ai_thinking = True
            self.root.after(300, self.ai_move)

    def ai_move(self):
        """Handle the AI's move based on current difficulty level"""
        if self.game_over:
            return

        start_time = time.time()

        # Choose move based on difficulty
        if self.current_difficulty == "Easy":
            pos = self.get_easy_move()
        elif self.current_difficulty == "Medium":
            pos = self.get_medium_move()
        else:  # Hard
            pos = self.get_hard_move()

        # Record the time taken
        time_taken = time.time() - start_time
        self.move_times.append(time_taken)
        self.timer_label.config(text=f"AI: {time_taken:.2f}s")

        # Make the move
        self.make_move(pos, self.ai_marker)
        play_sound(MOVE_SOUND)

        if self.check_game_end(self.ai_marker, "Computer"):
            return

        self.current_player = "Player"
        self.status_label.config(text="Your turn")
        self.enable_buttons()
        self.ai_thinking = False

    def get_easy_move(self):
        """Easy AI: Make random moves"""
        # Get list of available positions
        available_moves = [i for i in range(1, 10) if self.board[i] == ' ']
        return random.choice(available_moves)

    def get_medium_move(self):
        """Medium AI: Block wins and take obvious winning moves"""
        # First check if AI can win in next move
        for i in range(1, 10):
            if self.board[i] == ' ':
                self.board[i] = self.ai_marker
                if self.win_check(self.board, self.ai_marker):
                    self.board[i] = ' '
                    return i
                self.board[i] = ' '

        # Check if player can win in next move and block
        for i in range(1, 10):
            if self.board[i] == ' ':
                self.board[i] = self.player_marker
                if self.win_check(self.board, self.player_marker):
                    self.board[i] = ' '
                    return i
                self.board[i] = ' '

        # Try to take center if available
        if self.board[5] == ' ':
            return 5

        # Try to take corners
        corners = [1, 3, 7, 9]
        available_corners = [corner for corner in corners if self.board[corner] == ' ']
        if available_corners:
            return random.choice(available_corners)

        # Take any available edge
        edges = [2, 4, 6, 8]
        available_edges = [edge for edge in edges if self.board[edge] == ' ']
        if available_edges:
            return random.choice(available_edges)

        # Fallback to random (shouldn't happen)
        return self.get_easy_move()

    def get_hard_move(self):
        """Hard AI: Use minimax algorithm with alpha-beta pruning"""
        # First move randomization for variety
        if self.board.count(' ') >= 9:
            return random.choice([1, 3, 5, 7, 9])

        best_score = -float('inf')
        best_move = None
        alpha = -float('inf')
        beta = float('inf')

        for i in range(1, 10):
            if self.board[i] == ' ':
                self.board[i] = self.ai_marker
                score = self.minimax(self.board[:], 0, False, alpha, beta)
                self.board[i] = ' '

                if score > best_score:
                    best_score = score
                    best_move = i

                alpha = max(alpha, best_score)

        return best_move

    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning and depth limiting"""
        # Terminal states
        if self.win_check(board, self.ai_marker):
            return 10 - depth
        elif self.win_check(board, self.player_marker):
            return depth - 10
        elif all(space != ' ' for space in board[1:]):
            return 0

        # Depth limit for medium difficulty
        if depth >= self.max_depth:
            return self.evaluate_board(board)

        if is_maximizing:
            best_score = -float('inf')
            for i in range(1, 10):
                if board[i] == ' ':
                    board[i] = self.ai_marker
                    score = self.minimax(board[:], depth + 1, False, alpha, beta)
                    board[i] = ' '

                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)

                    # Alpha-beta pruning
                    if beta <= alpha:
                        break

            return best_score
        else:
            best_score = float('inf')
            for i in range(1, 10):
                if board[i] == ' ':
                    board[i] = self.player_marker
                    score = self.minimax(board[:], depth + 1, True, alpha, beta)
                    board[i] = ' '

                    best_score = min(score, best_score)
                    beta = min(beta, best_score)

                    # Alpha-beta pruning
                    if beta <= alpha:
                        break

            return best_score

    def evaluate_board(self, board):
        """Heuristic evaluation for non-terminal states"""
        # This is used when we reach max depth but game isn't over
        score = 0

        # Check all win patterns
        win_combos = [
            (7, 8, 9), (4, 5, 6), (1, 2, 3),  # Rows
            (7, 4, 1), (8, 5, 2), (9, 6, 3),  # Columns
            (7, 5, 3), (9, 5, 1)  # Diagonals
        ]

        # Evaluate each win combo
        for combo in win_combos:
            score += self.evaluate_line(board, combo)

        # Center position is strategically valuable
        if board[5] == self.ai_marker:
            score += 1
        elif board[5] == self.player_marker:
            score -= 1

        return score

    def evaluate_line(self, board, combo):
        """Evaluate a specific line (row, column, diagonal)"""
        a, b, c = combo

        # Count markers in this line
        ai_count = sum(1 for pos in combo if board[pos] == self.ai_marker)
        player_count = sum(1 for pos in combo if board[pos] == self.player_marker)

        # Score based on potential
        if ai_count == 2 and player_count == 0:
            return 3  # Two in a row for AI with open third spot
        elif player_count == 2 and ai_count == 0:
            return -3  # Two in a row for player with open third spot
        elif ai_count == 1 and player_count == 0:
            return 1  # One for AI with two open spots
        elif player_count == 1 and ai_count == 0:
            return -1  # One for player with two open spots

        return 0  # Mixed or empty line

    def make_move(self, pos, marker):
        """Update the board and UI with a new move"""
        self.board[pos] = marker
        self.buttons[pos].config(text=marker, state="disabled")

        # Visual indication of the last move
        if marker == self.player_marker:
            self.buttons[pos].config(fg="blue")
        else:
            self.buttons[pos].config(fg="red")

    def disable_buttons(self):
        """Disable all empty board positions"""
        for i in range(1, 10):
            if self.board[i] == ' ':
                self.buttons[i].config(state="disabled")

    def enable_buttons(self):
        """Enable all empty board positions"""
        for i in range(1, 10):
            if self.board[i] == ' ':
                self.buttons[i].config(state="normal")

    def win_check(self, board, mark):
        """Check if a player has won"""
        win_combos = [
            (7, 8, 9), (4, 5, 6), (1, 2, 3),  # Rows
            (7, 4, 1), (8, 5, 2), (9, 6, 3),  # Columns
            (7, 5, 3), (9, 5, 1)  # Diagonals
        ]
        for combo in win_combos:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] == mark:
                self.last_win_combo = combo
                return True
        return False

    def check_game_end(self, marker, player):
        """Check if game has ended and handle the outcome"""
        if self.win_check(self.board, marker):
            # Update scores
            if player == "Player":
                self.player_score += 1
            else:
                self.ai_score += 1

            self.games_played += 1
            play_sound(WIN_SOUND)
            self.highlight_win(self.last_win_combo)

            # Update UI
            self.game_over = True
            self.update_scoreboard()
            self.status_label.config(text=f"{player} wins!")

            # Show notification after a short delay
            self.root.after(800, lambda: messagebox.showinfo("Game Over", f"{player} wins!"))
            return True

        elif all(space != ' ' for space in self.board[1:]):
            # Handle draw
            self.draws += 1
            self.games_played += 1
            play_sound(DRAW_SOUND)

            # Update UI
            self.game_over = True
            self.update_scoreboard()
            self.status_label.config(text="It's a draw!")

            # Show notification
            messagebox.showinfo("Game Over", "It's a draw!")
            return True

        return False

    def highlight_win(self, combo):
        """Highlight the winning combination on the board"""
        for i in combo:
            self.buttons[i].config(bg="lightgreen")

    def reset_board(self):
        """Reset the game board while keeping scores"""
        self.board = [' '] * 10
        for i in range(1, 10):
            self.buttons[i].config(text=" ", state="normal", bg="SystemButtonFace", fg="black")

        self.game_over = False
        self.current_player = "Player"
        self.status_label.config(text="Your turn")
        self.timer_label.config(text="")
        self.update_scoreboard()

    def reset_game(self):
        """Reset everything including scores"""
        self.player_score = 0
        self.ai_score = 0
        self.draws = 0
        self.games_played = 0
        self.move_times = []
        self.reset_board()

    def update_scoreboard(self):
        """Update the score display"""
        self.score_label.config(text=f"Player: {self.player_score} | Computer: {self.ai_score} | Draws: {self.draws}")

    def on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()