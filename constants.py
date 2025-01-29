import pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
TILE_SIZE = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE_SEA = (127,205,255)
BLUE = (36, 87, 240)
RED = (227, 36, 36)
GREEN = (89, 189, 89)
YELLOW = (255, 228, 0)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (200, 200, 200)

# Resource colors
RESOURCE_COLORS = {
    'WOOD': (34, 139, 34),    # Forest Green
    'BRICK': (178, 34, 34),   # Firebrick
    'ORE': (105, 105, 105),   # Dim Gray
    'GRAIN': (218, 165, 32),  # Goldenrod
    'WOOL': (144, 238, 144),  # Light Green
    'DESERT': (194, 178, 128) # Sand
}

# Font
FONT = pygame.font.Font(None, 24)