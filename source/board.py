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
        self.use_axial = True
        self.tiles: List[Tile] = self.generate_board()
        self.axial_layout: List[Tuple[int, int]] = self.generate_axial_layout()
        self.hex_height = TILE_SIZE * 2
        self.hex_width = math.sqrt(3) * TILE_SIZE
        self.calculate_board_dimensions()
        
        # track vertices and edges
        self.vertex_positions = {}
        self.edge_positions = {}
        self._init_vertices_and_edges()
        self.robber_position = self._find_desert_tile()

    def _init_vertices_and_edges(self):
        """set up all vertex and edge positions"""
        # get vertex positions from each hex
        for q, r in self.axial_layout:
            x, y = self.get_hex_center(q, r)  
            corners = self.get_hex_corners(x, y)

            # store rounded vertex positions
            for corner_x, corner_y in corners:
                vertex_px = (round(corner_x), round(corner_y))
                if vertex_px not in self.vertex_positions:
                    self.vertex_positions[vertex_px] = (q, r)

            # create edges between vertices 
            for i in range(6):
                corner1 = corners[i]
                corner2 = corners[(i + 1) % 6]
                
                v1 = (round(corner1[0]), round(corner1[1]))
                v2 = (round(corner2[0]), round(corner2[1]))
                
                if v1 > v2:
                    v1, v2 = v2, v1
                    
                edge = (v1, v2)
                if edge not in self.edge_positions:
                    self.edge_positions[edge] = (
                        self.vertex_positions[v1],
                        self.vertex_positions[v2]
                    )

    def calculate_board_dimensions(self):
        """figure out where to place the board on screen"""
        board_width = self.hex_width * 5
        board_height = self.hex_height * 4.5
        self.board_left = (SCREEN_WIDTH - board_width) // 2
        self.board_top = (SCREEN_HEIGHT - board_height) // 2 - self.hex_height // 4
        self.board_center_x = SCREEN_WIDTH // 2
        self.board_center_y = self.board_top + board_height // 2

    def generate_board(self) -> List[Tile]:
        """create randomized board layout"""
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

    def generate_axial_layout(self) -> List[Tuple[int, int]]:
        """create hex grid coordinates"""
        layout = []
        radius = 2
        for q in range(-radius, radius + 1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)
            for r in range(r1, r2 + 1):
                layout.append((q, r))
        return layout

    def get_hex_center(self, q: int, r: int) -> Tuple[float, float]:
        """convert hex coords to pixel position"""
        x = self.board_center_x + self.hex_width * (q + r/2)
        y = self.board_center_y + self.hex_height * r * 0.75 
        return (x, y)
    
    def get_hex_corners(self, center_x: float, center_y: float) -> List[Tuple[float, float]]:
        """get all corner points for a hex"""
        corners = []
        for i in range(6):
            angle_deg = 60 * i - 30  # pointy-top orientation
            angle_rad = math.pi / 180 * angle_deg
            corner_x = center_x + TILE_SIZE * math.cos(angle_rad)
            corner_y = center_y + TILE_SIZE * math.sin(angle_rad)
            corners.append((corner_x, corner_y))
        return corners
    
    def get_tile_at(self, index: int) -> Tile:
        """get tile info by index"""
        return self.tiles[index]
    
    def get_adjacent_tiles(self, x: float, y: float) -> List[Tuple[int, Tile]]:
        """find tiles connected to a vertex"""
        adjacent_tiles = []
        for idx, (q, r) in enumerate(self.axial_layout):
            # check each hex
            center_x, center_y = self.get_hex_center(q, r)
            corners = self.get_hex_corners(center_x, center_y)
            
            # look for corner match
            for corner_x, corner_y in corners:
                if (math.isclose(x, corner_x, abs_tol=1.0) and 
                    math.isclose(y, corner_y, abs_tol=1.0)):
                    adjacent_tiles.append((idx, self.tiles[idx]))
                    break
                    
        return adjacent_tiles
    
    def find_nearest_vertex(self, pos: Tuple[int, int], max_dist: float = 20) -> Optional[Tuple[int, int]]:
        """find closest vertex to mouse"""
        nearest = min(self.vertex_positions.keys(),
                    key=lambda v: math.hypot(pos[0] - v[0], pos[1] - v[1]))
        dist = math.hypot(pos[0] - nearest[0], pos[1] - nearest[1])
        return nearest if dist <= max_dist else None

    def find_nearest_edge(self, pos: Tuple[int, int], max_dist: float = 20) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """find closest edge to mouse"""
        def point_to_line_dist(point, line_start, line_end):
            px, py = point
            x1, y1 = line_start
            x2, y2 = line_end
            
            # vector math for distance
            line_vec = (x2-x1, y2-y1)
            point_vec = (px-x1, py-y1)
            line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
            
            if line_len == 0:
                return math.hypot(px-x1, py-y1)
                
            t = max(0, min(1, (point_vec[0]*line_vec[0] + point_vec[1]*line_vec[1]) / (line_len*line_len)))
            proj_x = x1 + t * line_vec[0]
            proj_y = y1 + t * line_vec[1]
            
            return math.hypot(px-proj_x, py-proj_y)

        nearest = None
        min_dist = float('inf')
        
        for edge in self.edge_positions.keys():
            dist = point_to_line_dist(pos, edge[0], edge[1])
            if dist < min_dist and dist <= max_dist:
                min_dist = dist
                nearest = edge

        return nearest
    
    def _find_desert_tile(self) -> int:
        """find starting robber position"""
        for idx, tile in enumerate(self.tiles):
            if tile.resource_type == ResourceType.DESERT:
                return idx
        return 0

    def move_robber(self, new_position: int) -> bool:
        """try to move robber to new tile"""
        if 0 <= new_position < len(self.tiles):
            self.robber_position = new_position
            return True
        return False
    
    def pixel_to_axial(self, x: float, y: float) -> Tuple[int, int]:
        """convert screen position to hex coords"""
        x_offset = (x - self.board_center_x) 
        y_offset = (y - self.board_center_y)
        
        r = round((y_offset) / (self.hex_height * 0.75))
        q = round(x_offset/self.hex_width - r/2)
        
        return (q, r)

    def axial_to_pixel(self, q: int, r: int) -> Tuple[float, float]:
        """Convert axial coordinates to pixel coordinates"""
        return self.get_hex_center(q, r)