import random
import math
from typing import List, Optional, Tuple
from .enums import ResourceType, GamePhase
from .constants import *
import pygame

class Tile:
    def __init__(self, resource_type: ResourceType, value: Optional[int]):
        self.resource_type = resource_type
        self.value = value

class Board:
    def __init__(self):
        self.tiles: List[Tile] = self.generate_board()
        self.layout: List[Tuple[int, int]] = self.generate_layout()
        self.hex_height = TILE_SIZE * 2
        self.hex_width = math.sqrt(3) * TILE_SIZE
        self.calculate_board_dimensions()

    def calculate_board_layout(self):
        """Calculate the dimensions and position of the game board.
        
        Sets up the hexagonal grid measurements and positions the board
        centered on the screen with space for player information.
        """
        self.hex_height = TILE_SIZE * 2
        self.hex_width = math.sqrt(3) * TILE_SIZE
        
        # Calculate board dimensions
        board_width = self.hex_width * 5  # 5 hexes wide
        board_height = self.hex_height * 4.5  # 5 rows, but they overlap, so it's 4.5 times the height
        
        # Calculate board position
        self.board_left = (SCREEN_WIDTH - board_width) // 2
        self.board_top = (SCREEN_HEIGHT - board_height) // 2 - self.hex_height // 4  # Adjust for player info at bottom

        # Calculate the center of the board
        self.board_center_x = SCREEN_WIDTH // 2
        self.board_center_y = self.board_top + board_height // 2
        
    def calculate_board_dimensions(self):
        board_width = self.hex_width * 5  # 5 hexes wide
        board_height = self.hex_height * 4.5  # 5 rows, but they overlap
        self.board_left = (SCREEN_WIDTH - board_width) // 2
        self.board_top = (SCREEN_HEIGHT - board_height) // 2 - self.hex_height // 4
        self.board_center_x = SCREEN_WIDTH // 2
        self.board_center_y = self.board_top + board_height // 2


    def generate_board(self) -> List[Tile]:
        resources = [ResourceType.WOOD] * 4 + [ResourceType.BRICK] * 3 + \
                    [ResourceType.ORE] * 3 + [ResourceType.GRAIN] * 4 + \
                    [ResourceType.WOOL] * 4 + [ResourceType.DESERT]
        values = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        random.shuffle(resources)
        random.shuffle(values)
        
        tiles = []
        for i, resource in enumerate(resources):
            if resource == ResourceType.DESERT:
                tiles.append(Tile(resource, None))
            else:
                tiles.append(Tile(resource, values[i if i < len(values) else i-1]))
        return tiles

    def generate_layout(self) -> List[Tuple[int, int]]:
        layout = []
        rows = [3, 4, 5, 4, 3]  # Number of hexes in each row
        for row, num_hexes in enumerate(rows):
            start_col = 2 - (num_hexes // 2)  # Center the row
            for col in range(num_hexes):
                layout.append((start_col + col, row))
        return layout

    def get_tile_at(self, index: int) -> Tile:
        return self.tiles[index]

    def get_adjacent_tiles(self, tile_index: int) -> List[Tile]:
        # TODO: Implement logic to get adjacent tiles
        pass


    def get_adjacent_tiles(self, x: float, y: float) -> List[Tuple[int, Tile]]:
        adjacent_tiles = []
        for index, (col, row) in enumerate(self.layout):
            tile_x, tile_y = self.get_hex_center(col, row)
            corners = self.get_hex_corners(tile_x, tile_y)
            if any(math.isclose(x, corner_x, abs_tol=1) and math.isclose(y, corner_y, abs_tol=1) for corner_x, corner_y in corners):
                adjacent_tiles.append((index, self.tiles[index]))
        return adjacent_tiles

    def get_hex_center(self, col: int, row: int) -> Tuple[float, float]:
        x = self.board_center_x + self.hex_width * (col - (min(col for col, _ in self.layout) + max(col for col, _ in self.layout)) / 2 + (row % 2) * 0.5)
        y = self.board_center_y + self.hex_height * 0.75 * (row - 2)
        return x, y

    def get_hex_corners(self, center_x: float, center_y: float) -> List[Tuple[float, float]]:
        corners = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            corner_x = center_x + TILE_SIZE * math.cos(angle_rad)
            corner_y = center_y + TILE_SIZE * math.sin(angle_rad)
            corners.append((corner_x, corner_y))
        return corners
    
    def draw_hexagon(self, surface: pygame.Surface, color: Tuple[int, int, int], center: Tuple[float, float], size: float):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            points.append((center[0] + size * math.cos(angle_rad),
                           center[1] + size * math.sin(angle_rad)))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 4)