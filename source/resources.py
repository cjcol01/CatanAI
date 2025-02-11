# resource_manager.py
from typing import List
from .enums import ResourceType, GamePhase
from .player import Player
from .board import Board, Tile

class ResourceManager:
    def __init__(self, game):
        self.game = game

    def distribute_resources(self, roll_value: int, players):
        print(f"Rolling {roll_value}")  # debug
        for player_index, player in enumerate(players):
            for settlement_pos in self.game.settlements:
                if self.game.settlements[settlement_pos] == player_index:
                    adjacent_tiles = self.game.board.get_adjacent_tiles(*settlement_pos)
                    for _, tile in adjacent_tiles:
                        if tile.value == roll_value and tile.resource_type != ResourceType.DESERT:
                            player.add_resource(tile.resource_type)  # first resource for settlment
                            
                            # if city add second resource
                            if settlement_pos in self.game.cities:
                                player.add_resource(tile.resource_type)
                                print(f"Player {player.name} received 2 {tile.resource_type.name} from city")
                            else:
                                print(f"Player {player.name} received 1 {tile.resource_type.name} from settlement")

    def give_all_resources_cheat(self):
        """Cheat function that gives all players one of each resource"""
        if self.game.game_phase == GamePhase.PLAY:
            for resource in ResourceType:
                if resource != ResourceType.DESERT:  # skip desert
                    self.game.current_player.add_resource(resource) # clearly the best way of doing this
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    self.game.current_player.add_resource(resource)
                    print(f"Gave {self.game.current_player.name} 1 {resource.name}")