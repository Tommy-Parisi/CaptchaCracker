import pyautogui
import numpy as np
import time

def get_tile_indices_for_box(box, tile_w, tile_h, num_cols, num_rows=3):
    """
    Returns the indices of all grid tiles that are fully or partially within the given bounding box.

    The bounding box is provided in pixel coordinates and mapped onto a fixed-size grid.
    Each tile index corresponds to a flattened (row-major) representation of the grid.

    :param box: A bounding box defined as [x1, y1, x2, y2] in image-space coordinates.
    :param tile_w: Width of each tile in pixels.
    :param tile_h: Height of each tile in pixels.
    :param num_cols: Total number of columns in the grid.
    :param num_rows: Total number of rows in the grid (default is 3).
    :return: A list of tile indices (integers) that intersect with the bounding box.
             For example, tile at row 1, col 2 in a 4-column grid has index 6.
    """
    x1, y1, x2, y2 = map(int, box)
    tiles = set()

    # Clamp coordinates to avoid index overflow
    row_start = max(0, y1 // tile_h)
    row_end = min(num_rows - 1, y2 // tile_h)
    col_start = max(0, x1 // tile_w)
    col_end = min(num_cols - 1, x2 // tile_w)

    for row in range(row_start, row_end + 1):
        for col in range(col_start, col_end + 1):
            index = row * num_cols + col
            tiles.add(index)

    return list(tiles)


def click_on_center_of_box(detections, grid_top_left):
    """
    Clicks on the center of each detected bounding box.

    :param detections: List of bounding boxes [[x1, y1, x2, y2], ...]
    :param grid_top_left: (x, y) of the t
    op-left corner of the grid on the screen
    :param tile_w: Width of each tile (not needed for center-click but kept for signature consistency)
    :param tile_h: Height of each tile (same as above)
    :param num_cols: Number of columns in the grid (optional, unused here)
    :param num_rows: Number of rows in the grid (optional, unused here)
    """
    grid_top_left = (int(grid_top_left[0]), int(grid_top_left[1]))
    for box in detections:
        print(f"[INFO] Box: {box}")
        x1, y1, x2, y2 = map(int, box)
        macOS = True
        if macOS:
            x1 //= 2
            y1 //= 2
            x2 //= 2
            y2 //= 2 
            
        center_x = grid_top_left[0] + ((x1 + x2) // 2)
        center_y = grid_top_left[1] + ((y1 + y2) // 2)

        pyautogui.click(center_x, center_y)
        print(f"[✔] Clicked center at ({center_x}, {center_y}) from box ({x1}, {y1}, {x2}, {y2})")
        time.sleep(0.1)  # optional delay


def click_on_tiles(box, grid_top_left, tile_w, tile_h, num_cols, num_rows=3):
    """
    Clicks on every tile that exists within with the given bounding box.

    :param box: A single bounding box [x1, y1, x2, y2]
    :param grid_top_left: (x, y) of the top-left corner of the grid on the screen
    :param tile_w: Width of each tile
    :param tile_h: Height of each tile
    :param num_cols: Number of columns in the grid
    :param num_rows: Number of rows in the grid
    """
    # Ensure box is scaled properly for macOS retina if necessary
    macOS = True
    x1, y1, x2, y2 = map(int, box)
    if macOS:
        x1 //= 2
        y1 //= 2
        x2 //= 2
        y2 //= 2
    box_scaled = [x1, y1, x2, y2]

    indices = get_tile_indices_for_box(box_scaled, tile_w, tile_h, num_cols, num_rows)
    for index in indices:
        row = index // num_cols
        col = index % num_cols

        center_x = grid_top_left[0] + col * tile_w + tile_w // 2
        center_y = grid_top_left[1] + row * tile_h + tile_h // 2

        pyautogui.click(center_x, center_y)
        print(f"[✔] Clicked tile at ({center_x}, {center_y}) in row {row}, col {col}")

