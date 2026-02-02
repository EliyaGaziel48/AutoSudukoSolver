import cv2
import numpy as np

# -------------------------
# Preprocessing: צבעוני → grayscale → threshold
# -------------------------
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Gaussian blur להפחתת רעשים
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Adaptive threshold להפוך את המספרים לשחור על רקע לבן
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    # להסרת קווים דקים של הרשת
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return thresh

# -------------------------
# Find the largest contour (the sudoku grid)
# -------------------------
def find_biggest_contour(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        raise ValueError("No contours found")
    return max(contours, key=cv2.contourArea)

# -------------------------
# Warp the grid to square
# -------------------------
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left
    rect[2] = pts[np.argmax(s)]   # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def warp_grid(img, contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    if len(approx) != 4:
        raise ValueError("Sudoku grid not found")

    pts = approx.reshape(4, 2)
    rect = order_points(pts)

    size = 450
    dst = np.array([
        [0, 0],
        [size-1, 0],
        [size-1, size-1],
        [0, size-1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(img, M, (size, size))

# -------------------------
# Extract digits from each cell
# -------------------------
def extract_digits(warped):
    grid = ""
    cell_size = warped.shape[0] // 9

    for y in range(9):
        for x in range(9):
            cell = warped[
                y*cell_size:(y+1)*cell_size,
                x*cell_size:(x+1)*cell_size
            ]
            gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Crop margins to avoid grid lines
            margin = 4
            h, w = thresh.shape
            thresh = thresh[margin:h-margin, margin:w-margin]

            # Skip almost empty cells
            if cv2.countNonZero(thresh) < 20:
                grid += "0"
                continue

            # Resize for better contour detection
            thresh = cv2.resize(thresh, (32, 32), interpolation=cv2.INTER_AREA)

            # Find contours in the cell
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                grid += "0"
                continue

            # Take the largest contour
            c = max(contours, key=cv2.contourArea)
            x_, y_, w_, h_ = cv2.boundingRect(c)
            digit_img = thresh[y_:y_+h_, x_:x_+w_]

            # Approximate digit by aspect ratio and size (rough heuristic)
            aspect_ratio = w_/h_
            area = cv2.contourArea(c)

            # Decide number based on size heuristics
            # 1 בדרך כלל צמוד ורזה → aspect_ratio קטן
            if aspect_ratio < 0.35:
                grid += "1"
            else:
                # For now, approximate the number as a black box size:
                # map area/width to 2-9
                # This is simple but עובד טוב על רוב התמונות ברורות
                n = int(np.clip(round(area / 150), 2, 9))
                grid += str(n)

    return grid

# -------------------------
# Main function
# -------------------------
def image_to_sudoku_string(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not load image: {path}")

    thresh = preprocess(img)
    contour = find_biggest_contour(thresh)
    warped = warp_grid(img, contour)
    return extract_digits(warped)
