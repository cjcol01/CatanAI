from .enums import GamePhase, PlacementType
from .placement import PlacementManager
import pygame

class SetupPhaseManager:
    def __init__(self, game):
        self.game = game
        self.setup_turns_completed = 0
        self.setup_phase = 0
        self.setup_direction = 1
        self.placement_type = PlacementType.SETTLEMENT
        self.placement_manager = PlacementManager(game)


    def next_setup_turn(self):
        self.setup_turns_completed += 1
        if self.setup_phase == 0:
            self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
            if self.game.current_player_index == 0:
                self.setup_phase = 1
                self.setup_direction = -1
                self.game.current_player_index = len(self.game.players) - 1  # Start with the last player
        elif self.setup_phase == 1:
            self.game.current_player_index = (self.game.current_player_index + self.setup_direction) % len(self.game.players)
        
        if self.setup_turns_completed == len(self.game.players) * 2:
            self.end_setup_phase()
        else:
            self.placement_type = PlacementType.SETTLEMENT
            print(f"Next player: {self.game.current_player.name}. Place a settlement.")

    def end_setup_phase(self):
        self.game.game_phase = GamePhase.PLAY
        self.game.placement_mode = False
        self.game.current_player_index = 0  # Start the main game with the first player
        print("Setup phase complete. Starting main game phase.")

    def handle_setup_phase(self):
        current_pos = pygame.mouse.get_pos()
        if self.placement_type == PlacementType.SETTLEMENT:
            if self.placement_manager.try_place_settlement(current_pos):
                self.placement_type = PlacementType.ROAD
                print(f"Player {self.game.current_player.name} placed a settlement. Now place a road.")
        elif self.placement_type == PlacementType.ROAD:
            if self.placement_manager.try_place_road(current_pos):
                self.next_setup_turn()