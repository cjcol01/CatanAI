from typing import Tuple, Dict, Optional
import math
from .enums import GamePhase, ResourceType, PlacementType

class PlacementManager:
    """handles placement of game pieces on the board"""
    
    def __init__(self, game):
        self.game = game

    def toggle_placement_mode(self):
        """toggle placement mode on/off"""
        self.game.game_state.placement_mode = not self.game.game_state.placement_mode
        if self.game.game_state.placement_mode:
            self.game.game_state.placement_type = PlacementType.SETTLEMENT
        print(f"Placement mode {'activated' if self.game.game_state.placement_mode else 'deactivated'}")

    def try_place_settlement(self, pos: Tuple[int, int]) -> bool:
        """attempt to place settlement at hover position"""
        if self.game.game_state.hovered_corner:
            corner_x, corner_y = self.game.game_state.hovered_corner
            if self.is_valid_settlement_placement((corner_x, corner_y)):
                self.place_settlement((corner_x, corner_y))
                return True
        return False

    def try_place_road(self, pos: Tuple[int, int]) -> bool:
        """attempt to place road at hover position"""
        if self.game.game_state.hovered_road:
            start, end = self.game.game_state.hovered_road
            if self.is_valid_road_placement(start, end):
                self.place_road(start, end)
                return True
        return False

    def is_valid_road_placement(self, start: Tuple[float, float], end: Tuple[float, float]) -> bool:
        """check if road placement is valid"""
        # check if road exists
        if (start, end) in self.game.game_state.roads or (end, start) in self.game.game_state.roads:
            return False
        
        # check for connection to settlement
        player_settlements = [pos for pos, player in self.game.game_state.settlements.items() 
                            if player == self.game.game_state.current_player_index]
        if start in player_settlements or end in player_settlements:
            if self.game.game_state.game_phase == GamePhase.PLAY:
                return self.game.current_player.can_afford_road()
            return True
        
        # check for connection to road
        player_roads = [road for road, player in self.game.game_state.roads.items() 
                       if player == self.game.game_state.current_player_index]
        for road_start, road_end in player_roads:
            if start == road_start or start == road_end or end == road_start or end == road_end:
                if self.game.game_state.game_phase == GamePhase.PLAY:
                    return self.game.current_player.can_afford_road()
                return True
        
        return False

    def is_valid_settlement_placement(self, pos: Tuple[float, float]) -> bool:
        """check if settlement placement is valid"""
        # check for existing buildings
        if pos in self.game.game_state.settlements or pos in self.game.game_state.cities:
            return False
        
        # check distance rule
        for settlement_pos in self.game.game_state.settlements:
            if math.hypot(pos[0] - settlement_pos[0], pos[1] - settlement_pos[1]) < self.game.board.hex_width:
                return False
        
        for city_pos in self.game.game_state.cities:
            if math.hypot(pos[0] - city_pos[0], pos[1] - city_pos[1]) < self.game.board.hex_width:
                return False
            
        # main game phase checks
        if self.game.game_state.game_phase == GamePhase.PLAY:
            # must connect to own road
            player_roads = [road for road, player in self.game.game_state.roads.items() 
                          if player == self.game.game_state.current_player_index]
            if not any(pos in road for road in player_roads):
                return False
            
            # check resources
            if not self.game.current_player.can_afford_settlement():
                return False
        
        return True

    def place_settlement(self, pos: Tuple[float, float]):
        """place settlement and handle resource costs"""
        current_player = self.game.current_player
        axial_pos = self.game.board.pixel_to_axial(*pos)
        
        if self.game.game_state.game_phase == GamePhase.PLAY:
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
        
        self.game.game_state.settlements[pos] = self.game.game_state.current_player_index
        current_player.build_settlement(axial_pos)
        print(f"Player {current_player.name} placed a settlement at {pos}")
        
        # handle setup phase resources
        if self.game.game_state.game_phase == GamePhase.SETUP and self.game.setup_manager.setup_phase == 1:
            adjacent_tiles = self.game.board.get_adjacent_tiles(*pos)
            for _, tile in adjacent_tiles:
                if tile.resource_type != ResourceType.DESERT:
                    current_player.add_resource(tile.resource_type)
                    print(f"Player {current_player.name} received 1 {tile.resource_type.name}")

        self.game.victory_point_manager.update_victory_points()

    def place_road(self, start: Tuple[float, float], end: Tuple[float, float]):
        """place road and handle resource costs"""
        current_player = self.game.current_player
        
        if self.game.game_state.game_phase == GamePhase.PLAY:
            if not current_player.can_afford_road():
                print(f"Player {current_player.name} cannot afford a road.")
                return
            
            road_cost = {
                ResourceType.WOOD: 1,
                ResourceType.BRICK: 1
            }
            current_player.spend_resources(road_cost)
        
        self.game.game_state.roads[(start, end)] = self.game.game_state.current_player_index
        current_player.build_road(start, end)
        print(f"Player {current_player.name} placed a road from {start} to {end}")

    def place_city(self, pos: Tuple[float, float]):
        """upgrade settlement to city"""
        current_player = self.game.current_player
        axial_pos = self.game.board.pixel_to_axial(*pos)
        
        if pos not in self.game.game_state.settlements or self.game.game_state.settlements[pos] != self.game.game_state.current_player_index:
            return
            
        if self.game.game_state.game_phase == GamePhase.PLAY:
            if not current_player.can_afford_city():
                return
            city_cost = {ResourceType.GRAIN: 2, ResourceType.ORE: 3}
            current_player.spend_resources(city_cost)
        
        del self.game.game_state.settlements[pos]
        self.game.game_state.cities[pos] = self.game.game_state.current_player_index
        current_player.build_city(axial_pos)
        print(f"Player {current_player.name} upgraded settlement to city at {pos}")
        self.game.victory_point_manager.update_victory_points()

    def is_valid_city_placement(self, pos: Tuple[float, float]) -> bool:
        """check if city placement is valid"""
        if pos not in self.game.game_state.settlements:
            return False
        if self.game.game_state.settlements[pos] != self.game.game_state.current_player_index:
            return False
        if self.game.game_state.game_phase == GamePhase.PLAY:
            if not self.game.current_player.can_afford_city():
                return False
        return True
    
    def try_place_city(self, pos: Tuple[int, int]) -> bool:
        """attempt to place city at hover position"""
        if self.game.game_state.hovered_settlement:
            settlement_pos = self.game.game_state.hovered_settlement
            if self.is_valid_city_placement(settlement_pos):
                self.place_city(settlement_pos)
                return True
        return False