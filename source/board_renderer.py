import pygame
import math
from .constants import *
from .board import Board

class BoardRenderer:
    def __init__(self, screen, board):
        self.screen = screen
        self.board = board
        self.hex_height = TILE_SIZE * 2
        self.hex_width = math.sqrt(3) * TILE_SIZE
        self.calculate_board_layout()

    def calculate_board_layout(self):
        board_width = self.hex_width * 5
        board_height = self.hex_height * 4.5
        self.board_left = (SCREEN_WIDTH - board_width) // 2
        self.board_top = (SCREEN_HEIGHT - board_height) // 2 - self.hex_height // 4
        self.board_center_x = SCREEN_WIDTH // 2
        self.board_center_y = self.board_top + board_height // 2

    def draw_hexagon(self, color, center, size):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            points.append((center[0] + size * math.cos(angle_rad),
                           center[1] + size * math.sin(angle_rad)))
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, BLACK, points, 4)

    def get_hex_corners(self, center_x, center_y):
        corners = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            corner_x = center_x + TILE_SIZE * math.cos(angle_rad)
            corner_y = center_y + TILE_SIZE * math.sin(angle_rad)
            corners.append((corner_x, corner_y))
        return corners

    def draw_board(self, settlements, roads, placement_mode, hovered_corner, hovered_road, current_player_color):
        min_col = min(col for col, _ in self.board.layout)
        max_col = max(col for col, _ in self.board.layout)
        
        for index, (col, row) in enumerate(self.board.layout):
            tile = self.board.get_tile_at(index)
            x = self.board_center_x + self.hex_width * (col - (min_col + max_col) / 2 + (row % 2) * 0.5)
            y = self.board_center_y + self.hex_height * 0.75 * (row - 2)

            color = RESOURCE_COLORS[tile.resource_type.name]
            self.draw_hexagon(color, (x, y), TILE_SIZE)

            if tile.value is not None:
                text = FONT.render(str(tile.value), True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)

            if placement_mode:
                corners = self.get_hex_corners(x, y)
                for corner_x, corner_y in corners:
                    pygame.draw.circle(self.screen, BLACK, (int(corner_x), int(corner_y)), 4)
                    
                    if hovered_corner and math.isclose(corner_x, hovered_corner[0], abs_tol=1) and math.isclose(corner_y, hovered_corner[1], abs_tol=1):
                        pygame.draw.circle(self.screen, current_player_color, (int(corner_x), int(corner_y)), 10, 2)
        
        for (x, y), player_color in settlements.items():
            pygame.draw.circle(self.screen, player_color, (int(x), int(y)), 8)
            pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), 8, 2)

        for (start, end), player_color in roads.items():
            pygame.draw.line(self.screen, player_color, start, end, 4)

        if placement_mode and hovered_corner:
            x, y = hovered_corner
            pygame.draw.circle(self.screen, current_player_color, (int(x), int(y)), 8, 2)

        if placement_mode and hovered_road:
            start, end = hovered_road
            pygame.draw.line(self.screen, current_player_color, start, end, 4)