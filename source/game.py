import pygame
import math
from typing import List, Tuple, Optional
from .constants import *
from .enums import ResourceType, DevCardType, GamePhase, PlayerAction, PlacementType
from .board import Board, Tile
from .player import Player
from .dice import Dice
from .ui_renderer import *
from .board import *
from .setup_phase import *
from .placement import *
from .mouse import InteractionHandler
from .resources import ResourceManager
from .board_renderer import BoardRenderer
from .dev_card import DevCardManager
from .victory_points import VictoryPointManager
from .robber import RobberManager
from .game_state import GameState

class Game:
    """main game class that handles the catan game logic and display"""
    def __init__(self):
        """initialize the game state and display"""
        # set up pygame display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Catan")
        self.clock = pygame.time.Clock()
        
        # core components for rendering/interaction
        self.board = Board()
        self.board_renderer = BoardRenderer(self.board)
        self.ui_renderer = UIRenderer(self.screen, self)
        self.interaction_handler = InteractionHandler(self)
        self.dice = Dice(self.screen, FONT)
        self.dice.set_game(self)
        
        # initialize game managers
        self.dev_card_manager = DevCardManager(self)  # create manager before game state
        self.setup_manager = SetupPhaseManager(self)
        self.placement_manager = PlacementManager(self)
        self.resource_manager = ResourceManager(self)
        self.robber_manager = RobberManager(self)
        self.victory_point_manager = VictoryPointManager(self)
        
        # set up initial game state
        self.game_state = GameState(
            board=self.board,
            players=[
                Player(RED, "Red"),
                Player(BLUE, "Blue"),
                Player(GREEN, "Green"),
                Player(YELLOW, "Yellow")
            ],
            current_player_index=0,
            game_phase=GamePhase.SETUP,
            setup_phase=0,
            setup_direction=1,
            setup_turns_completed=0,
            settlements={},
            roads={},
            cities={},
            placement_mode=True,
            placement_type=PlacementType.SETTLEMENT,
            dice_rolled=False,
            hover_distance=20
        )
        
        # init deck after game state exists
        self.dev_card_manager.init_deck()
        
        self.board.calculate_board_dimensions()

    @property
    def current_player(self):
        return self.game_state.players[self.game_state.current_player_index]

    @property
    def players(self):
        return self.game_state.players

    @property
    def settlements(self):
        return self.game_state.settlements

    @property
    def roads(self):
        return self.game_state.roads

    @property
    def cities(self):
        return self.game_state.cities

    @property
    def game_phase(self):
        return self.game_state.game_phase

    @property
    def placement_mode(self):
        return self.game_state.placement_mode

    @placement_mode.setter
    def placement_mode(self, value):
        self.game_state.placement_mode = value

    @property 
    def dice_rolled_this_turn(self):
        return self.game_state.dice_rolled

    @dice_rolled_this_turn.setter
    def dice_rolled_this_turn(self, value):
        self.game_state.dice_rolled = value

    @property 
    def game_phase(self):
        return self.game_state.game_phase
    
    @game_phase.setter
    def game_phase(self, value):
        self.game_state.game_phase = value
    
    @property
    def current_player_index(self):
        return self.game_state.current_player_index

    @current_player_index.setter
    def current_player_index(self, value):
        self.game_state.current_player_index = value

    @property
    def current_player(self):
        return self.players[self.current_player_index]
        
    def end_turn(self):
        """handle end of turn logic and state updates"""
        if not self.dice_rolled_this_turn:
            print("you must roll the dice before ending your turn")
            return
            
        if self.robber_manager.move_pending:
            print("you must move the robber before ending your turn")
            return

        # check for winner first
        if self.victory_point_manager.update_victory_points():
            return
            
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.dice_rolled_this_turn = False
        self.placement_mode = False
        self.update_game_state()
        
    def handle_robber_tile_click(self, mouse_pos):
        """pass robber clicks to the manager"""
        return self.robber_manager._handle_tile_click(mouse_pos)

    def handle_winner(self, winner_index: int):
        """handle game end when someone wins"""
        winner = self.players[winner_index]
        self.game_phase = GamePhase.END
        self.ui_renderer.clear_messages()
        self.ui_renderer.add_persistent_message(f"game over! {winner.name} wins with {winner.calculate_total_victory_points()} points!")
        self.ui_renderer.add_persistent_message("press ESC to exit")

    def update_game_state(self):
        """sync game state with current game info"""
        self.game_state = GameState(
            board=self.board,
            players=self.game_state.players,
            current_player_index=self.game_state.current_player_index,
            game_phase=self.game_state.game_phase,
            setup_phase=self.game_state.setup_phase,
            setup_direction=self.game_state.setup_direction,
            settlements=self.game_state.settlements,
            roads=self.game_state.roads,
            cities=self.game_state.cities,
            placement_mode=self.game_state.placement_mode,
            placement_type=self.game_state.placement_type,
            dice_rolled=self.game_state.dice_rolled,
            hover_distance=self.game_state.hover_distance,
            setup_turns_completed=self.game_state.setup_turns_completed,
            robber_position=self.game_state.robber_position,
            dice_value=self.dice.roll_value if hasattr(self.dice, 'roll_value') else None,
            longest_road_holder=self.victory_point_manager.longest_road_holder,
            largest_army_holder=self.victory_point_manager.largest_army_holder,
            hovered_corner=self.game_state.hovered_corner,
            hovered_road=self.game_state.hovered_road,
            hovered_city=self.game_state.hovered_city,
            hovered_settlement=self.game_state.hovered_settlement,
            dev_card_deck=self.game_state.dev_card_deck
        )

    def run(self):
        """main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state.game_phase != GamePhase.END:
                        if self.robber_manager.stealing_pending:
                            self.robber_manager.handle_click(event.pos)
                        elif self.robber_manager.move_pending:
                            self.handle_robber_tile_click(event.pos)
                        else:
                            self.interaction_handler.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    if self.game_state.game_phase != GamePhase.END:
                        self.interaction_handler.handle_mouse_motion(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.game_state.game_phase != GamePhase.END:
                        if event.key == pygame.K_f:
                            self.resource_manager.give_all_resources_cheat()
                        elif event.key == pygame.K_r:
                            if not self.game_state.dice_rolled:
                                roll_value = self.dice.roll_dice()
                                if roll_value is not None:
                                    print(f"rolled: {roll_value}")
                                    self.game_state.dice_rolled = True
                                    
                                    if roll_value == 7:
                                        self.robber_manager.handle_seven_rolled()
                                    else:
                                        self.resource_manager.distribute_resources(roll_value, self.players)
                        elif event.key == pygame.K_e:
                            self.end_turn()

            # draw everything
            self.screen.fill(BLUE_SEA)
            self.board_renderer.draw_board(self.screen, self)
            self.ui_renderer.draw_player_info(self.players)
            self.ui_renderer.draw_current_player(self)
    
            if self.robber_manager.move_pending:
                self.ui_renderer.add_message("click a tile to move the robber")          
            
            if self.game_state.game_phase == GamePhase.PLAY:
                self.ui_renderer.draw_end_turn_button(self.game_state.dice_rolled)
                self.ui_renderer.draw_placement_mode_button(self.game_state.placement_mode)
                self.ui_renderer.draw_buy_dev_card_button(self.game_state.placement_mode, self.current_player)

                # draw dice ui elements
                if not self.game_state.dice_rolled:
                    self.dice.draw_button()
                self.dice.draw_roll()
            
            self.ui_renderer.draw_status_messages()

            if self.robber_manager.stealing_pending:
                self.robber_manager.draw_stealing_interface(self.screen)
                
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()