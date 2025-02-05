
from typing import Tuple, Dict, Optional
import math
from .enums import GamePhase, ResourceType
from .game import *
from .player import Player
from .placement import PlacementType
class PlacementManager:
    def __init__(self, game):
        self.game = game
        self.placement_mode = False

    def toggle_placement_mode(self):
        self.game.placement_mode = not self.game.placement_mode
        if self.game.placement_mode:
            self.game.placement_type = PlacementType.SETTLEMENT  # default placement type when activating
        print(f"Placement mode {'activated' if self.game.placement_mode else 'deactivated'}")

    def try_place_settlement(self, pos: Tuple[int, int]) -> bool:
        if self.game.hovered_corner:
            corner_x, corner_y = self.game.hovered_corner
            if self.is_valid_settlement_placement((corner_x, corner_y)):
                self.place_settlement((corner_x, corner_y))
                return True
        return False

    def try_place_road(self, pos: Tuple[int, int]) -> bool:
        if self.game.hovered_road:
            start, end = self.game.hovered_road
            if self.is_valid_road_placement(start, end):
                self.place_road(start, end)
                return True
        return False

    def is_valid_road_placement(self, start: Tuple[float, float], end: Tuple[float, float]) -> bool:
        if (start, end) in self.game.roads or (end, start) in self.game.roads:
            return False
        
        player_settlements = [pos for pos, player in self.game.settlements.items() 
                            if player == self.game.current_player_index]
        if start in player_settlements or end in player_settlements:
            if self.game.game_phase == GamePhase.PLAY:
                return self.game.current_player.can_afford_road()
            return True
        
        player_roads = [road for road, player in self.game.roads.items() 
                       if player == self.game.current_player_index]
        for road_start, road_end in player_roads:
            if start == road_start or start == road_end or end == road_start or end == road_end:
                if self.game.game_phase == GamePhase.PLAY:
                    return self.game.current_player.can_afford_road()
                return True
        
        return False

    def is_valid_settlement_placement(self, pos: Tuple[float, float]) -> bool:
        if pos in self.game.settlements or pos in self.game.cities:
            return False
        
        for settlement_pos in self.game.settlements:
            if math.hypot(pos[0] - settlement_pos[0], pos[1] - settlement_pos[1]) < self.game.board.hex_width:
                return False
        
        for settlement_pos in self.game.cities:
            if math.hypot(pos[0] - settlement_pos[0], pos[1] - settlement_pos[1]) < self.game.board.hex_width:
                return False
            
        if self.game.game_phase == GamePhase.PLAY:
            player_roads = [road for road, player in self.game.roads.items() 
                          if player == self.game.current_player_index]
            if not any(pos in road for road in player_roads):
                return False
            
            if not self.game.current_player.can_afford_settlement():
                return False
        
        return True

    def place_settlement(self, pos: Tuple[float, float]):
        current_player = self.game.current_player
        
        if self.game.game_phase == GamePhase.PLAY:
            if not current_player.can_afford_settlement():
                print(f"Player {current_player.name} cannot afford a settlement.")
                return
            
            settlement_cost = {
                ResourceType.WOOD: 1,
                ResourceType.BRICK: 1,
                ResourceType.GRAIN: 1,
                ResourceType.WOOL: 1
            }
            current_player.spend_resources(settlement_cost)
        
        self.game.settlements[pos] = self.game.current_player_index
        current_player.build_settlement(len(self.game.settlements) - 1)
        print(f"Player {current_player.name} placed a settlement at {pos}")
        
        if self.game.game_phase == GamePhase.SETUP and self.game.setup_manager.setup_phase == 1:
            adjacent_tiles = self.game.board.get_adjacent_tiles(*pos)
            for _, tile in adjacent_tiles:
                if tile.resource_type != ResourceType.DESERT:
                    current_player.add_resource(tile.resource_type)
                    print(f"Player {current_player.name} received 1 {tile.resource_type.name} for initial settlement")

    def place_road(self, start: Tuple[float, float], end: Tuple[float, float]):
        current_player = self.game.current_player
        
        if self.game.game_phase == GamePhase.PLAY:
            if not current_player.can_afford_road():
                print(f"Player {current_player.name} cannot afford a road.")
                return
            
            road_cost = {
                ResourceType.WOOD: 1,
                ResourceType.BRICK: 1
            }
            current_player.spend_resources(road_cost)
        
        self.game.roads[(start, end)] = self.game.current_player_index
        current_player.build_road(start, end)
        print(f"Player {current_player.name} placed a road from {start} to {end}")

    def place_city(self, pos: Tuple[float, float]):
        """Upgrade a settlement to a city at the specified position."""
        current_player = self.game.current_player
        
        if pos not in self.game.settlements or self.game.settlements[pos] != self.game.current_player_index:
            print("You can only build a city on your own settlement.")
            return
            
        if self.game.game_phase == GamePhase.PLAY:
            if not current_player.can_afford_city():
                print(f"Player {current_player.name} cannot afford a city.")
                return
            
            city_cost = {
                ResourceType.GRAIN: 2,
                ResourceType.ORE: 3
            }
            current_player.spend_resources(city_cost)
        
        # Remove settlement and add city
        del self.game.settlements[pos]
        self.game.cities[pos] = self.game.current_player_index
        current_player.build_city(len(self.game.cities) - 1)
        print(f"Player {current_player.name} upgraded settlement to city at {pos}")

    def is_valid_city_placement(self, pos: Tuple[float, float]) -> bool:
        current_player = self.game.current_player

        """Check if a city can be built at the specified position."""
        if pos not in self.game.settlements:
            return False
        if self.game.settlements[pos] != self.game.current_player_index:
            return False
        if self.game.game_phase == GamePhase.PLAY:
            if not current_player.can_afford_city():
                return False
        return True
    
    def try_place_city(self, pos: Tuple[int, int]) -> bool:
        if self.game.hovered_settlement: 
            settlement_pos = self.game.hovered_settlement
            if self.is_valid_city_placement(settlement_pos):
                self.place_city(settlement_pos)
                return True
        return False