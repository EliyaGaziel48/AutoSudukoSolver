import tkinter as tk
from tkinter import filedialog, messagebox
from sudoku_solver import parse_grid, solve
from image_to_sudoku import image_to_sudoku_string

CELL_SIZE = 60
GRID_COLOR = "#2E2E2E"
HIGHLIGHT_COLOR = "#FF6666"
USER_COLOR = "#000000"
SOLVER_COLOR = "#1E90FF"
FONT = ("Helvetica", 24, "bold")
BLOCK_COLOR_1 = "#F8F8F8"
BLOCK_COLOR_2 = "#E8E8E8"

BUTTON_BG = "#4CAF50"
BUTTON_FG = "#FFFFFF"
BUTTON_HOVER = "#45A049"

class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        self.default_bg = kwargs.get("bg", BUTTON_BG)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self['bg'] = BUTTON_HOVER

    def on_leave(self, event):
        self['bg'] = self.default_bg

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku AutoSolver")
        self.grid_values = [["0"]*9 for _ in range(9)]
        self.user_input = set()
        self.selected_cell = (0,0)
        self.current_screen = None
        self.show_home_screen()

    # ----------------- Home Screen -----------------
    def show_home_screen(self):
        self.clear_screen()
        self.current_screen = tk.Frame(self.root, bg="#EFEFEF")
        self.current_screen.pack(fill="both", expand=True)

        tk.Label(self.current_screen, text="Sudoku AutoSolver", font=("Helvetica", 32, "bold"), bg="#EFEFEF").pack(pady=50)

        ModernButton(self.current_screen, text="פתרון אוטומטי", width=20, height=2, command=self.show_solver_screen).pack(pady=15)
        ModernButton(self.current_screen, text="הכנס תמונה", width=20, height=2, command=self.load_image).pack(pady=15)
        ModernButton(self.current_screen, text="קרדיטים", width=20, height=2, command=self.show_credits).pack(pady=15)

    # ----------------- Credits Screen -----------------
    def show_credits(self):
        self.clear_screen()
        self.current_screen = tk.Frame(self.root, bg="#EFEFEF")
        self.current_screen.pack(fill="both", expand=True)

        tk.Label(self.current_screen, text="Credits", font=("Helvetica", 28, "bold"), bg="#EFEFEF").pack(pady=20)
        tk.Label(self.current_screen, text="Sudoku AutoSolver by Eliya Gaziel\nPython, OpenCV, EasyOCR, Tkinter", font=("Helvetica", 16), bg="#EFEFEF").pack(pady=20)
        ModernButton(self.current_screen, text="חזור", width=15, height=2, command=self.show_home_screen).pack(pady=10)

    # ----------------- Solver Screen -----------------
    def show_solver_screen(self):
        self.clear_screen()
        self.current_screen = tk.Frame(self.root, bg="#FFFFFF")
        self.current_screen.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.current_screen, width=9*CELL_SIZE, height=9*CELL_SIZE, bg="#FFFFFF")
        self.canvas.pack(pady=20)

        self.draw_grid()
        self.canvas.bind("<Button-1>", self.select_cell)
        self.root.bind("<Key>", self.key_pressed)

        btn_frame = tk.Frame(self.current_screen, bg="#FFFFFF")
        btn_frame.pack(pady=10)
        ModernButton(btn_frame, text="פתור אוטומטית", width=15, height=2, command=self.solve_sudoku).grid(row=0, column=0, padx=10)
        ModernButton(btn_frame, text="חזור", width=15, height=2, command=self.show_home_screen).grid(row=0, column=1, padx=10)

    # ----------------- Image Loading -----------------
    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files","*.png"),("JPG files","*.jpg")])
        if not path:
            return
        try:
            puzzle = image_to_sudoku_string(path)
            self.grid_values = [[puzzle[r*9 + c] for c in range(9)] for r in range(9)]
            self.user_input = {(r,c) for r in range(9) for c in range(9) if self.grid_values[r][c] != "0"}
            self.show_solver_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read image:\n{e}")

    # ----------------- Drawing -----------------
    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(9):
            for c in range(9):
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                x2, y2 = (c+1)*CELL_SIZE, (r+1)*CELL_SIZE
                # צבע רקע לכל בלוק 3x3
                color = BLOCK_COLOR_1 if (r//3 + c//3)%2==0 else BLOCK_COLOR_2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # קווים בין תאים
        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            self.canvas.create_line(0, i*CELL_SIZE, 9*CELL_SIZE, i*CELL_SIZE, width=width, fill=GRID_COLOR)
            self.canvas.create_line(i*CELL_SIZE, 0, i*CELL_SIZE, 9*CELL_SIZE, width=width, fill=GRID_COLOR)

        # מספרים
        for r in range(9):
            for c in range(9):
                num = self.grid_values[r][c]
                if num != "0":
                    color = SOLVER_COLOR if (r,c) not in self.user_input else USER_COLOR
                    x = c*CELL_SIZE + CELL_SIZE/2
                    y = r*CELL_SIZE + CELL_SIZE/2
                    self.canvas.create_text(x, y, text=num, font=FONT, fill=color)

        # תא נבחר
        r, c = self.selected_cell
        self.canvas.create_rectangle(c*CELL_SIZE, r*CELL_SIZE, (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                                     outline=HIGHLIGHT_COLOR, width=3)

    # ----------------- Cell Selection -----------------
    def select_cell(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if 0 <= r < 9 and 0 <= c < 9:
            self.selected_cell = (r, c)
            self.draw_grid()

    # ----------------- Keyboard Input -----------------
    def key_pressed(self, event):
        r, c = self.selected_cell
        # ספרות
        if event.char in "1234567890":
            self.grid_values[r][c] = event.char
            self.user_input.add((r,c))
            self.draw_grid()
        # חיצים – להזיז את התא הנבחר בלבד
        elif event.keysym in ("Up","Down","Left","Right"):
            dr, dc = 0, 0
            if event.keysym=="Up": dr=-1
            elif event.keysym=="Down": dr=1
            elif event.keysym=="Left": dc=-1
            elif event.keysym=="Right": dc=1
            nr = max(0, min(8, r+dr))
            nc = max(0, min(8, c+dc))
            self.selected_cell = (nr, nc)
            self.draw_grid()

    # ----------------- Solve -----------------
    def solve_sudoku(self):
        puzzle_str = "".join(self.grid_values[r][c] for r in range(9) for c in range(9))
        try:
            grid = parse_grid(puzzle_str)
            if solve(grid):
                self.grid_values = [[str(grid[r][c]) for c in range(9)] for r in range(9)]
                self.draw_grid()
                messagebox.showinfo("Solved", "Sudoku solved!")
            else:
                messagebox.showwarning("No Solution", "Could not solve the Sudoku!")
        except Exception as e:
            messagebox.showerror("Error", f"Error solving Sudoku:\n{e}")

    # ----------------- Helpers -----------------
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# ----------------- Run GUI -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
