import math
from typing import List, Optional, Tuple
from .enums import GamePhase
from .constants import *
from .board import Board
import pygame

class BoardRenderer:
    """handles rendering for the game board"""
    def __init__(self, board: Board):
        self.board = board

    def draw_board(self, screen, game):
        """main draw function for the board and all its pieces"""
        self._draw_hex_tiles(screen, game)
        game.robber_manager.draw_robber(screen) 
        
        # draw game pieces in order
        self._draw_roads(screen, game.game_state.roads, game.game_state.players)
        self._draw_settlements(screen, game)
        self._draw_cities(screen, game.game_state.cities, game.game_state.players)
        
        # show placement indicators during setup and placement
        if game.game_state.placement_mode or game.game_state.game_phase == GamePhase.SETUP:
            self._draw_placement_indicators(screen, game)

    def draw_hexagon(self, surface: pygame.Surface, color: Tuple[int, int, int], 
                    center: Tuple[float, float], size: float):
        """draw a single hex tile"""
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            points.append((center[0] + size * math.cos(angle_rad),
                         center[1] + size * math.sin(angle_rad)))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 4)

    def _draw_hex_tiles(self, screen, game):
        """draw all the hex tiles on the board"""
        for index, (q, r) in enumerate(self.board.axial_layout):
            tile = self.board.get_tile_at(index)
            x, y = self.board.get_hex_center(q, r)
            color = RESOURCE_COLORS[tile.resource_type.name]
            self.draw_hexagon(screen, color, (x, y), TILE_SIZE)

            # show where robber can move
            if game.robber_manager.move_pending:
                game.robber_manager.draw_placement_indicator(screen, pygame.mouse.get_pos())

            if tile.value is not None:
                text = FONT.render(str(tile.value), True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                screen.blit(text, text_rect)

    def _draw_roads(self, screen, roads, players):
        """draw all player roads"""
        for (start, end), player_index in roads.items():
            road_color = players[player_index].color
            pygame.draw.line(screen, BLACK, start, end, 6)
            pygame.draw.line(screen, road_color, start, end, 4)

    def _draw_settlements(self, screen, game):
        """draw all settlements"""
        for coord, player_index in game.game_state.settlements.items():
            x, y = coord
            pygame.draw.circle(screen, game.game_state.players[player_index].color, (int(x), int(y)), 8)
            pygame.draw.circle(screen, BLACK, (int(x), int(y)), 8, 2)

    def _draw_cities(self, screen, cities, players):
        """draw all cities as stars"""
        for coord, player_index in cities.items():
            x, y = coord
            star_size = 12
            player_color = players[player_index].color
            
            points = []
            for i in range(10):
                angle = math.pi * (i / 5 - 0.5)
                radius = star_size if i % 2 == 0 else star_size / 2
                point_x = x + radius * math.cos(angle)
                point_y = y + radius * math.sin(angle)
                points.append((point_x, point_y))
            
            pygame.draw.polygon(screen, player_color, points)
            pygame.draw.polygon(screen, BLACK, points, 2)

    def _draw_placement_indicators(self, screen, game):
        """draw hover indicators for building placement"""
        current_player_color = game.game_state.players[game.game_state.current_player_index].color
        
        # show settlement placement
        if game.game_state.hovered_corner:
            x, y = game.game_state.hovered_corner
            if game.placement_manager.is_valid_settlement_placement((x, y)):
                pygame.draw.circle(screen, current_player_color, (int(x), int(y)), 10, 4)

        # show city upgrade
        if game.game_state.hovered_settlement:
            x, y = game.game_state.hovered_settlement
            if (game.game_state.placement_mode and 
                game.current_player.can_afford_city()):
                pygame.draw.circle(screen, current_player_color, (int(x), int(y)), 14, 4)

        # show road placement 
        if game.game_state.hovered_road:
            start, end = game.game_state.hovered_road
            if game.placement_manager.is_valid_road_placement(start, end):
                pygame.draw.line(screen, current_player_color, start, end, 4)