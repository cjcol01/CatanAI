from typing import List, Optional
from .player import Player

class VictoryPointManager:
    """Manages victory point tracking and special card assignments"""
    
    def __init__(self, game):
        self.game = game
        self.longest_road_holder: Optional[int] = None  # Player index
        self.largest_army_holder: Optional[int] = None  # Player index
        self.min_road_length_for_longest = 5
        self.min_knights_for_largest = 3
        
    def update_victory_points(self):
        """Check for winner after any point changes."""
        self._update_longest_road()
        self._update_largest_army()
        
        for i, player in enumerate(self.game.players):
            if player.calculate_total_victory_points() >= 10:
                self.game.handle_winner(i)
                return True
        return False
        
    def _update_longest_road(self):
        """Update longest road card holder"""
        current_holder = self.longest_road_holder
        longest_length = self.min_road_length_for_longest - 1
        new_holder = None
        
        # Find player with longest road >= minimum length
        for i, player in enumerate(self.game.players):
            road_length = self._calculate_longest_road_length(player)
            if road_length >= self.min_road_length_for_longest:
                if road_length > longest_length:
                    longest_length = road_length
                    new_holder = i
                elif road_length == longest_length and current_holder == i:
                    new_holder = i  # Current holder keeps card in case of tie
        
        # Update longest road card holder
        if new_holder != current_holder:
            if current_holder is not None:
                self.game.players[current_holder].has_longest_road = False
            if new_holder is not None:
                self.game.players[new_holder].has_longest_road = True
            self.longest_road_holder = new_holder
    
    def _update_largest_army(self):
        """Update largest army card holder"""
        current_holder = self.largest_army_holder
        largest_army = self.min_knights_for_largest - 1
        new_holder = None
        
        # Find player with most knights >= minimum
        for i, player in enumerate(self.game.players):
            if player.knights_played >= self.min_knights_for_largest:
                if player.knights_played > largest_army:
                    largest_army = player.knights_played
                    new_holder = i
                elif player.knights_played == largest_army and current_holder == i:
                    new_holder = i  # Current holder keeps card in case of tie
        
        # Update largest army card holder
        if new_holder != current_holder:
            if current_holder is not None:
                self.game.players[current_holder].has_largest_army = False
            if new_holder is not None:
                self.game.players[new_holder].has_largest_army = True
            self.largest_army_holder = new_holder
    
    def _calculate_longest_road_length(self, player: Player) -> int:
        """Calculate the length of the longest continuous road for a player"""
        # placehodler, just return the total number of roads
        return len(player.roads)
    
    def add_victory_point_card(self, player_index: int):
        """Add a victory point from a development card"""
        self.game.players[player_index].hidden_victory_points += 1
        self.update_victory_points()  # winner after adding VP?