# interaction_handler.py
import math
from typing import Tuple
from .enums import GamePhase
from .resources import ResourceManager

class InteractionHandler:
    def __init__(self, game):
        self.game = game
        self.resource_manager = ResourceManager(self)


    def handle_click(self, pos: Tuple[int, int]):
        if self.game.game_phase == GamePhase.SETUP:
            self.game.setup_manager.handle_setup_phase()
        elif self.game.game_phase == GamePhase.PLAY:
            if not self.game.dice_rolled_this_turn:
                roll_value = self.game.dice.handle_click(pos)
                if roll_value is not None:
                    print(f"Rolled: {roll_value}")
                    self.game.dice_rolled_this_turn = True
                    self.resource_manager.distribute_resources(roll_value)
            
            end_turn_rect = self.game.ui_renderer.draw_end_turn_button(self.game.dice_rolled_this_turn)
            if end_turn_rect is not None and end_turn_rect.collidepoint(pos) and self.game.dice_rolled_this_turn:
                self.game.end_turn()
            
            placement_mode_rect = self.game.ui_renderer.draw_placement_mode_button(self.game.placement_mode)

            if placement_mode_rect.collidepoint(pos):
                self.game.placement_manager.toggle_placement_mode()

            if self.game.placement_mode:
                self.game.placement_manager.try_place_settlement(pos)
                self.game.placement_manager.try_place_road(pos)

    def handle_mouse_motion(self, pos: Tuple[int, int]):
        if self.game.placement_mode or self.game.game_phase == GamePhase.SETUP:
            self.game.hovered_corner = None
            self.game.hovered_road = None
            for _, (col, row) in enumerate(self.game.board.layout):
                x, y = self.game.board.get_hex_center(col, row)
                corners = self.game.board.get_hex_corners(x, y)
                for i, (corner_x, corner_y) in enumerate(corners):
                    if math.hypot(pos[0] - corner_x, pos[1] - corner_y) <= self.game.hover_distance:
                        self.game.hovered_corner = (corner_x, corner_y)
                        return
                    next_corner = corners[(i + 1) % 6]
                    mid_x = (corner_x + next_corner[0]) / 2
                    mid_y = (corner_y + next_corner[1]) / 2
                    if math.hypot(pos[0] - mid_x, pos[1] - mid_y) <= self.game.hover_distance:
                        self.game.hovered_road = ((corner_x, corner_y), next_corner)
                        return