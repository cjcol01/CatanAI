from typing import List
from .enums import ResourceType, GamePhase
from .player import Player

class ResourceManager:
    def __init__(self, game):
        self.game = game

    def distribute_resources(self, roll_value: int, players):
        """Distribute resources to players based on dice roll"""
        print(f"Rolling {roll_value}")

        for player_index, player in enumerate(players):
            for settlement_pos in self.game.game_state.settlements:
                if self.game.game_state.settlements[settlement_pos] == player_index:
                    adjacent_tiles = self.game.board.get_adjacent_tiles(*settlement_pos)
                    for _, tile in adjacent_tiles:
                        if tile.value == roll_value and tile.resource_type != ResourceType.DESERT:
                            player.add_resource(tile.resource_type)  # first resource for settlement
                            
                            # if city add second resource
                            if settlement_pos in self.game.game_state.cities:
                                player.add_resource(tile.resource_type)
                                print(f"Player {player.name} received 2 {tile.resource_type.name} from city")
                            else:
                                print(f"Player {player.name} received 1 {tile.resource_type.name} from settlement")
        
        self.game.update_game_state()

    def give_all_resources_cheat(self):
        """Cheat function that gives all resources to current player"""
        if self.game.game_state.game_phase == GamePhase.PLAY:
            for resource in ResourceType:
                if resource != ResourceType.DESERT:  
                    for _ in range(10):  # Give 10 of each resource
                        self.game.current_player.add_resource(resource)
                    print(f"Gave {self.game.current_player.name} 10 {resource.name}")
            
            self.game.update_game_state()