# Sudoku AutoSolver

**Sudoku AutoSolver** is a Python application that can automatically solve Sudoku puzzles. It supports both **manual input** and **image-based recognition** using computer vision and OCR. The application includes a **modern interactive GUI** with keyboard navigation, automatic solving, and visual feedback for a complete user-friendly experience.

---

## Features

- Solve Sudoku puzzles from:
  - **Manual input** (enter numbers directly or fill in the grid interactively)
  - **Image input** (take a photo or upload a picture of a Sudoku)
- **OCR integration** using EasyOCR to recognize numbers from images
- **Interactive GUI**:
  - Highlight the selected cell
  - Color-coded 3x3 blocks
  - Different colors for user input vs solver numbers
- **Keyboard navigation**:
  - Arrow keys to move the selection
  - Digit keys to fill in numbers
- Home screen with buttons for Solve, Load Image, and Credits
- Credits screen showing project info and technologies used
- Human-like solving strategies combined with backtracking for complex puzzles

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/SudokuAutoSolver.git
cd SudokuAutoSolver
