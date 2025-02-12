from .enums import GamePhase, PlacementType
import pygame

class SetupPhaseManager:
    def __init__(self, game):
        self.game = game

    @property
    def setup_phase(self):
        return self.game.game_state.setup_phase

    def next_setup_turn(self):
        """Advance to the next player's setup turn"""
        self.game.game_state.setup_turns_completed += 1
        
        if self.setup_phase == 0:
            self.game.game_state.current_player_index = (self.game.game_state.current_player_index + 1) % len(self.game.players)
            if self.game.game_state.current_player_index == 0:
                self.game.game_state.setup_phase = 1
                self.game.game_state.setup_direction = -1
                self.game.game_state.current_player_index = len(self.game.players) - 1  # start with last player
        elif self.setup_phase == 1:
            self.game.game_state.current_player_index = (
                self.game.game_state.current_player_index + self.game.game_state.setup_direction
            ) % len(self.game.players)
        
        if self.game.game_state.setup_turns_completed == len(self.game.players) * 2:
            self.end_setup_phase()
        else:
            self.game.game_state.placement_type = PlacementType.SETTLEMENT
            print(f"Next player: {self.game.current_player.name}. Place a settlement.")

    def end_setup_phase(self):
        """End the setup phase and begin main game"""
        self.game.game_state.game_phase = GamePhase.PLAY
        self.game.game_state.placement_mode = False
        self.game.game_state.current_player_index = 0  # start main game with first player
        print("Setup phase complete. Starting main game phase.")

    def handle_setup_phase(self):
        """Handle setup phase placement logic"""
        current_pos = pygame.mouse.get_pos()
        if self.game.game_state.placement_type == PlacementType.SETTLEMENT:
            if self.game.placement_manager.try_place_settlement(current_pos):
                self.game.game_state.placement_type = PlacementType.ROAD
                print(f"Player {self.game.current_player.name} placed a settlement. Now place a road.")
        elif self.game.game_state.placement_type == PlacementType.ROAD:
            if self.game.placement_manager.try_place_road(current_pos):
                self.next_setup_turn()