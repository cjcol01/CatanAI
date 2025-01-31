# resource_manager.py
from typing import List
from .enums import ResourceType, GamePhase
from .player import Player
from .board import Board, Tile

class ResourceManager:
    def __init__(self, game):
        self.game = game

    def distribute_resources(self, roll_value: int):
        """Distribute resources to players based on dice roll.
        
        Args:
            roll_value: The sum of the dice roll (2-12)
            
        Gives one resource to each player for each settlement they own
        adjacent to a hex with the rolled number.
        """
        for player_index, player in enumerate(self.game.players):
            for settlement_pos in self.game.settlements:
                if self.game.settlements[settlement_pos] == player_index:
                    adjacent_tiles = self.game.board.get_adjacent_tiles(*settlement_pos)
                    for _, tile in adjacent_tiles:
                        if tile.value == roll_value and tile.resource_type != ResourceType.DESERT:
                            player.add_resource(tile.resource_type)
                            print(f"Player {player.name} received 1 {tile.resource_type.name}")

    def give_all_resources_cheat(self):
        """Cheat function that gives all players one of each resource"""
        if self.game.game_phase == GamePhase.PLAY:
            for resource in ResourceType:
                if resource != ResourceType.DESERT:  # Skip desert
                    self.game.current_player.add_resource(resource)
                    print(f"Gave {self.game.current_player.name} 1 {resource.name}")