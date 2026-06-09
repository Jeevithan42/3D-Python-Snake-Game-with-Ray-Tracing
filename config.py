# config.py
# Game configuration constants shared across modules

# Window size (pixels)
WIDTH, HEIGHT = 800, 800

# Size of one grid cell (world units, also matches model scale)
BLOCK_SIZE = 1  # Panda3D uses world units; we map each cell to 1 unit

# Base frames per second; will increase with level
FPS_BASE = 12

# Colors (RGB 0-1 for Panda3D)
WHITE = (1, 1, 1)
BLACK = (0, 0, 0)
RED = (0.9, 0.16, 0.16)
GREEN = (0.16, 0.9, 0.16)
DARK_GREEN = (0, 0.63, 0)
GREY = (0.66, 0.66, 0.66)
DARK_GREY = (0.2, 0.2, 0.2)
WALL_COLOR = (0.47, 0.47, 0.51)

# Visual theme
BG_COLOR = (0.12, 0.12, 0.16)  # dark modern theme
