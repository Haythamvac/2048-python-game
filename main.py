import tkinter as tk
import random
import os


class Game2048(tk.Tk):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.score = 0
        self.high_score = self.load_high_score()
        self.title('2048')
        self.geometry(f'{size * 100}x{size * 150}')
        self.grid()
        self.board = [[0] * self.size for _ in range(self.size)]
        self.create_widgets()
        self.add_new_tile()
        self.add_new_tile()
        self.update_board()

    def create_widgets(self):
        self.score_label = tk.Label(self, text=f'Счет: {self.score}', font=('Arial', 16))
        self.score_label.grid(row=0, column=0, columnspan=self.size // 2, sticky='w', padx=5, pady=5)
        self.high_score_label = tk.Label(self, text=f'Лучший счет: {self.high_score}', font=('Arial', 16))
        self.high_score_label.grid(row=0, column=self.size // 2, columnspan=self.size // 2, sticky='e', padx=5, pady=5)

        self.tiles = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                tile = tk.Label(self, text='', width=4, height=2, font=('Arial', 24), bg='#ccc0b3', fg='#776e65')
                tile.grid(row=i + 1, column=j, padx=5, pady=5, ipadx=10, ipady=10)
                row.append(tile)
            self.tiles.append(row)
        self.bind('<Key>', self.handle_keypress)

    def add_new_tile(self):
        empty_tiles = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty_tiles:
            i, j = random.choice(empty_tiles)
            self.board[i][j] = random.choice([2, 4])

    def update_board(self):
        self.score_label.config(text=f'Счет: {self.score}')
        self.high_score_label.config(text=f'Лучший счет: {self.high_score}')
        for i in range(self.size):
            for j in range(self.size):
                value = self.board[i][j]
                if value:
                    self.tiles[i][j].configure(text=str(value), bg=self.get_tile_color(value))
                else:
                    self.tiles[i][j].configure(text='', bg='#ccc0b3')

    def get_tile_color(self, value):
        colors = {
            2: '#eee4da', 4: '#ede0c8', 8: '#f2b179', 16: '#f59563',
            32: '#f67c5f', 64: '#f65e3b', 128: '#edcf72', 256: '#edcc61',
            512: '#edc850', 1024: '#edc53f', 2048: '#edc22e'
        }
        return colors.get(value, '#3c3a32')

    def handle_keypress(self, event):
        key = event.keysym
        if key in ['Up', 'Down', 'Left', 'Right']:
            if self.move(key):
                self.add_new_tile()
                self.update_board()
                if self.is_game_over():
                    self.show_game_over()

    def move(self, direction):
        moved = False

        def slide_and_merge(row):
            nonlocal moved
            new_row = [num for num in row if num != 0]
            for i in range(len(new_row) - 1):
                if new_row[i] == new_row[i + 1]:
                    new_row[i] *= 2
                    self.score += new_row[i]
                    new_row[i + 1] = 0
            new_row = [num for num in new_row if num != 0]
            moved = moved or new_row != row[:len(new_row)]
            return new_row + [0] * (self.size - len(new_row))

        if direction == 'Up':
            for j in range(self.size):
                col = slide_and_merge([self.board[i][j] for i in range(self.size)])
                for i in range(self.size):
                    self.board[i][j] = col[i]
        elif direction == 'Down':
            for j in range(self.size):
                col = slide_and_merge([self.board[i][j] for i in range(self.size - 1, -1, -1)])
                for i in range(self.size):
                    self.board[self.size - 1 - i][j] = col[i]
        elif direction == 'Left':
            for i in range(self.size):
                self.board[i] = slide_and_merge(self.board[i])
        elif direction == 'Right':
            for i in range(self.size):
                self.board[i] = slide_and_merge(self.board[i][::-1])[::-1]

        return moved

    def is_game_over(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return False
                if i < self.size - 1 and self.board[i][j] == self.board[i + 1][j]:
                    return False
                if j < self.size - 1 and self.board[i][j] == self.board[i][j + 1]:
                    return False
        return True

    def show_game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        game_over = tk.Toplevel(self)
        game_over.title('Ты проиграл')
        tk.Label(game_over, text='Ты проиграл!', font=('Arial', 24)).pack(padx=20, pady=20)
        tk.Label(game_over, text=f'Твой счет: {self.score}', font=('Arial', 16)).pack(pady=10)
        tk.Label(game_over, text=f'Лучший счет: {self.high_score}', font=('Arial', 16)).pack(pady=10)
        tk.Label(game_over, text='Введите свое имя:', font=('Arial', 14)).pack(pady=10)
        name_entry = tk.Entry(game_over, font=('Arial', 14))
        name_entry.pack(pady=5)
        tk.Button(game_over, text='Сохранить и начать заново',
                  command=lambda: self.save_score(name_entry.get(), game_over)).pack(pady=10)

    def save_score(self, name, window):
        scores = self.load_scores()
        scores[name] = max(scores.get(name, 0), self.score)
        self.save_scores(scores)
        window.destroy()
        self.restart_game()

    def restart_game(self):
        self.score = 0
        self.board = [[0] * self.size for _ in range(self.size)]
        self.add_new_tile()
        self.add_new_tile()
        self.update_board()

    def load_high_score(self):
        scores = self.load_scores()
        if scores:
            return max(scores.values())
        return 0

    def save_high_score(self):
        scores = self.load_scores()
        scores['Лучший счет'] = self.high_score
        self.save_scores(scores)

    def load_scores(self):
        if os.path.exists('high_scores.txt'):
            with open('high_scores.txt', 'r') as f:
                lines = f.readlines()
                scores = {}
                for line in lines:
                    name, score = line.strip().split(': ')
                    scores[name] = int(score)
                return scores
        return {}

    def save_scores(self, scores):
        with open('high_scores.txt', 'w') as f:
            for name, score in scores.items():
                f.write(f'{name}: {score}\n')


class StartScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Выберите размер доски')
        self.geometry('300x300')
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text='Выберите размер доски', font=('Arial', 18)).pack(pady=20)
        sizes = [4, 5, 6, 8]
        for size in sizes:
            tk.Button(self, text=f'{size}x{size}', font=('Arial', 14), command=lambda s=size: self.start_game(s)).pack(
                pady=5)

    def start_game(self, size):
        self.destroy()
        game = Game2048(size)
        game.mainloop()


if __name__ == '__main__':
    start_screen = StartScreen()
    start_screen.mainloop()
