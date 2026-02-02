from copy import deepcopy

GRID_SIZE = 9
DIGITS = set(range(1, 10))

def parse_grid(line):
    if len(line) != 81:
        raise ValueError("Input must be exactly 81 characters")
    return [[int(line[r*9 + c]) for c in range(9)] for r in range(9)]

def print_grid(grid):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)
        for c in range(9):
            if c % 3 == 0 and c != 0:
                print("|", end=" ")
            print(grid[r][c], end=" ")
        print()

def box_coords(r, c):
    br, bc = (r // 3) * 3, (c // 3) * 3
    return [(br + i, bc + j) for i in range(3) for j in range(3)]

def candidates(grid, r, c):
    if grid[r][c] != 0:
        return set()
    used = set(grid[r]) | \
           {grid[i][c] for i in range(9)} | \
           {grid[x][y] for x, y in box_coords(r, c)}
    return DIGITS - used

def naked_singles(grid):
    progress = False
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                cand = candidates(grid, r, c)
                if len(cand) == 1:
                    grid[r][c] = cand.pop()
                    progress = True
    return progress

def hidden_singles(grid):
    progress = False

    # Rows
    for r in range(9):
        counts = {}
        for c in range(9):
            if grid[r][c] == 0:
                for v in candidates(grid, r, c):
                    counts.setdefault(v, []).append(c)
        for v, cols in counts.items():
            if len(cols) == 1:
                grid[r][cols[0]] = v
                progress = True

    # Columns
    for c in range(9):
        counts = {}
        for r in range(9):
            if grid[r][c] == 0:
                for v in candidates(grid, r, c):
                    counts.setdefault(v, []).append(r)
        for v, rows in counts.items():
            if len(rows) == 1:
                grid[rows[0]][c] = v
                progress = True

    # Boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            counts = {}
            cells = [(br+i, bc+j) for i in range(3) for j in range(3)]
            for r, c in cells:
                if grid[r][c] == 0:
                    for v in candidates(grid, r, c):
                        counts.setdefault(v, []).append((r, c))
            for v, locs in counts.items():
                if len(locs) == 1:
                    r, c = locs[0]
                    grid[r][c] = v
                    progress = True

    return progress

def is_solved(grid):
    return all(grid[r][c] != 0 for r in range(9) for c in range(9))

def find_best_cell(grid):
    best = None
    best_cand = None
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                cand = candidates(grid, r, c)
                if not cand:
                    return None, None
                if best is None or len(cand) < len(best_cand):
                    best = (r, c)
                    best_cand = cand
    return best, best_cand

def solve(grid):
    while True:
        if not (naked_singles(grid) or hidden_singles(grid)):
            break

    if is_solved(grid):
        return True

    cell, cand = find_best_cell(grid)
    if cell is None:
        return False

    r, c = cell
    for v in cand:
        snapshot = deepcopy(grid)
        grid[r][c] = v
        if solve(grid):
            return True
        grid[:] = snapshot
    return False

#__________________________Main__________________________

from image_to_sudoku import image_to_sudoku_string

if __name__ == "__main__":
    choice = input("1 = manual input | 2 = image\n")

    if choice == "2":
        path = input("Path to Sudoku image: ")
        puzzle = image_to_sudoku_string(path)
        print("Detected puzzle:")
        print(puzzle)
    else:
        puzzle = input("Enter Sudoku line:\n")

    grid = parse_grid(puzzle)

    print("\nOriginal:")
    print_grid(grid)

    if solve(grid):
        print("\nSolved:")
        print_grid(grid)
    else:
        print("\nNo solution found.")
