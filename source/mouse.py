import math
from typing import Tuple
from .enums import GamePhase
import pygame

class InteractionHandler:
    def __init__(self, game):
        self.game = game

    def handle_click(self, pos: Tuple[int, int]):
        """handle all mouse clicks during the game"""
        if self.game.game_state.game_phase == GamePhase.SETUP:
            self.game.setup_manager.handle_setup_phase()
            
        elif self.game.game_state.game_phase == GamePhase.PLAY:
            # try rolling dice first if not rolled
            if not self.game.game_state.dice_rolled:
                roll_value = self.game.dice.handle_click(pos)
                if roll_value is not None:
                    print(f"rolled: {roll_value}")
                    self.game.game_state.dice_rolled = True
                    self.game.resource_manager.distribute_resources(roll_value, self.game.players)
            
            # check end turn button
            end_turn_rect = self.game.ui_renderer.draw_end_turn_button(self.game.game_state.dice_rolled)
            if end_turn_rect is not None and end_turn_rect.collidepoint(pos) and self.game.game_state.dice_rolled:
                self.game.end_turn()
            
            # check placement mode toggle
            placement_mode_rect = self.game.ui_renderer.draw_placement_mode_button(self.game.game_state.placement_mode)
            if placement_mode_rect.collidepoint(pos):
                self.game.placement_manager.toggle_placement_mode()

            # handle placement mode actions
            if self.game.game_state.placement_mode:
                # try buying dev card
                dev_card_rect = pygame.Rect(20, 20, 150, 40)
                if dev_card_rect.collidepoint(pos) and self.game.current_player.can_afford_dev():
                    if self.game.dev_card_manager.buy_dev_card(self.game.current_player):
                        print(f"development card purchased successfully!")
                    return

                # try building things in order
                if not self.game.placement_manager.try_place_settlement(pos):
                    if not self.game.placement_manager.try_place_road(pos):
                        self.game.placement_manager.try_place_city(pos)

    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """handle hover effects when mouse moves"""
        if self.game.game_state.placement_mode or self.game.game_state.game_phase == GamePhase.SETUP:
            # clear previous hover states
            self.game.game_state.hovered_corner = None
            self.game.game_state.hovered_road = None
            self.game.game_state.hovered_settlement = None
            
            # check settlement upgrade first
            for settlement_pos, player_index in self.game.game_state.settlements.items():
                if (player_index == self.game.game_state.current_player_index and 
                    math.hypot(pos[0] - settlement_pos[0], pos[1] - settlement_pos[1]) <= self.game.game_state.hover_distance):
                    self.game.game_state.hovered_settlement = settlement_pos
                    return

            # then check for new settlement spots
            nearest_vertex = self.game.board.find_nearest_vertex(pos, self.game.game_state.hover_distance)
            if nearest_vertex:
                self.game.game_state.hovered_corner = nearest_vertex
                return
                
            # finally check for road spots
            nearest_edge = self.game.board.find_nearest_edge(pos, self.game.game_state.hover_distance)
            if nearest_edge:
                self.game.game_state.hovered_road = nearest_edge
                return