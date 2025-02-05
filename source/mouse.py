# interaction_handler.py
import math
from typing import Tuple
from .enums import GamePhase
from .resources import ResourceManager

class InteractionHandler:
    def __init__(self, game):
        self.game = game
        self.resource_manager = ResourceManager(self.game)

    def handle_click(self, pos: Tuple[int, int]):
        if self.game.game_phase == GamePhase.SETUP:
            self.game.setup_manager.handle_setup_phase()
        elif self.game.game_phase == GamePhase.PLAY:
            if not self.game.dice_rolled_this_turn:
                roll_value = self.game.dice.handle_click(pos)
                if roll_value is not None:
                    print(f"Rolled: {roll_value}")
                    self.game.dice_rolled_this_turn = True
                    self.resource_manager.distribute_resources(roll_value, self.game.players)
            
            end_turn_rect = self.game.ui_renderer.draw_end_turn_button(self.game.dice_rolled_this_turn)
            if end_turn_rect is not None and end_turn_rect.collidepoint(pos) and self.game.dice_rolled_this_turn:
                self.game.end_turn()
            
            placement_mode_rect = self.game.ui_renderer.draw_placement_mode_button(self.game.placement_mode)

            if placement_mode_rect.collidepoint(pos):
                self.game.placement_manager.toggle_placement_mode()

            if self.game.placement_mode:
                # try settlements 
                if not self.game.placement_manager.try_place_settlement(pos):
                    # if settlement placement failed, try roads
                    if not self.game.placement_manager.try_place_road(pos):
                        # if road placement failed, try cities
                        self.game.placement_manager.try_place_city(pos)

    def handle_mouse_motion(self, pos: Tuple[int, int]):
        if self.game.placement_mode or self.game.game_phase == GamePhase.SETUP:
            self.game.hovered_corner = None
            self.game.hovered_road = None
            self.game.hovered_settlement = None
            
            # check settlements first
            for settlement_pos, player_index in self.game.settlements.items():
                if (player_index == self.game.current_player_index and 
                    math.hypot(pos[0] - settlement_pos[0], pos[1] - settlement_pos[1]) <= self.game.hover_distance):
                    self.game.hovered_settlement = settlement_pos
                    # print("Found settlement hover")
                    return

            # check for vertex hover
            nearest_vertex = self.game.board.find_nearest_vertex(pos, self.game.hover_distance)
            if nearest_vertex:
                self.game.hovered_corner = nearest_vertex
                # print(f"Found vertex hover at {nearest_vertex}")
                return
                
            # check for edge hover
            nearest_edge = self.game.board.find_nearest_edge(pos, self.game.hover_distance)
            if nearest_edge:
                self.game.hovered_road = nearest_edge
                # print(f"Found edge hover at {nearest_edge}")
                return
            # else:
            #     print("No edge found")  # Debug print