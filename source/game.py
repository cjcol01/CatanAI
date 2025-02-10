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

class Game:
    """Main game class that handles the Catan game logic and display.
    
    This class manages the game state, player turns, board layout,
    resource distribution, and all game mechanics for Catan.
    """
    def __init__(self):
        """Initialize the game with display, board, players and game state."""
        # set up pygame display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Catan")
        self.clock = pygame.time.Clock()
        
        # initialize game components
        self.board = Board()
        self.players = [
            Player(RED, "Red"),
            Player(BLUE, "Blue"), 
            Player(GREEN, "Green"),
            Player(YELLOW, "Yellow")
        ]

        # game state tracking
        self.current_player_index = 0  
        self.setup_turns_completed = 0
        
        # game phase management
        self.game_phase = GamePhase.SETUP  # current game state
        self.setup_phase = 0  # 0 for first 1 for second
        self.setup_direction = 1  # direction of setup (1 forward, -1 reverse)
        
        # dice and turn management
        self.dice = Dice(self.screen, FONT)
        self.dice_rolled_this_turn = False
        
        # building placement state
        self.placement_mode = True  # placement mode for buildings?
        self.placement_type = PlacementType.SETTLEMENT
        self.hover_distance = 20  # pixel range for hover detection
        
        # hover state tracking
        self.hovered_corner: Optional[Tuple[int, int]] = None  # (q,r)
        self.hovered_road: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None  # ((q1,r1), (q2,r2))
        self.hovered_city: Optional[Tuple[int, int]] = None
        self.hovered_settlement = None  # (q,r)

        # game piece storage
        self.settlements = {}  # maps corner positions to player index
        self.roads = {}  # maps road endpoints to player index
        self.cities = {}
        
        self.setup_manager = SetupPhaseManager(self)
        self.placement_manager = PlacementManager(self)
        self.ui_renderer = UIRenderer(self.screen)
        self.interaction_handler = InteractionHandler(self)
        self.resource_manager = ResourceManager(self)
        self.board_renderer = BoardRenderer(self.board)

        self.dev_card_manager = DevCardManager(self)
        self.dev_card_deck = []

        self.robber_move_pending = False  # track if robber needs to be moved
        self.victory_point_manager = VictoryPointManager(self)

        self.board.calculate_board_dimensions()

    @property
    def current_player(self):
        return self.players[self.current_player_index]
        
    def end_turn(self):
        if not self.dice_rolled_this_turn:
            print("You must roll the dice before ending your turn.")
            return
            
        if self.robber_move_pending:
            print("You must move the robber before ending your turn")
            return

        # Check for winner before advancing turn
        if self.victory_point_manager.update_victory_points():
            return
            
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.dice_rolled_this_turn = False
        self.placement_mode = False
        
    def handle_robber_tile_click(self, mouse_pos):
        """Handle clicking on a tile to move the robber."""
        if not self.robber_move_pending:
            return
            
        # find which tile was clicked
        for idx, (q, r) in enumerate(self.board.axial_layout):
            x, y = self.board.get_hex_center(q, r)
            
            # check if click is within hex bounds
            if math.hypot(mouse_pos[0] - x, mouse_pos[1] - y) <= TILE_SIZE:
                if idx != self.board.robber_position:  # dont let place robber on same tile
                    self.board.move_robber(idx)
                    self.robber_move_pending = False
                    print(f"Moved robber to tile {idx}")
                    # TODO: stealing from players 
                break

    def handle_winner(self, winner_index: int):
        winner = self.players[winner_index]
        self.game_phase = GamePhase.END
        self.ui_renderer.clear_messages()
        self.ui_renderer.add_persistent_message(f"Game Over! {winner.name} wins with {winner.calculate_total_victory_points()} points!")
        self.ui_renderer.add_persistent_message("Press ESC to exit")

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_phase != GamePhase.END:
                        if self.robber_move_pending:
                            self.handle_robber_tile_click(event.pos)
                        else:
                            self.interaction_handler.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    if self.game_phase != GamePhase.END:
                        self.interaction_handler.handle_mouse_motion(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.game_phase != GamePhase.END:
                        if event.key == pygame.K_f:
                            self.resource_manager.give_all_resources_cheat()
                        elif event.key == pygame.K_r:
                            if not self.dice_rolled_this_turn:
                                roll_value = self.dice.roll_dice()
                                if roll_value is not None:
                                    print(f"Rolled: {roll_value}")
                                    self.dice_rolled_this_turn = True
                                    
                                    if roll_value == 7:
                                        print("Seven rolled! Move the robber to a new tile.")
                                        self.robber_move_pending = True
                                    else:
                                        self.resource_manager.distribute_resources(roll_value, self.players)
                        elif event.key == pygame.K_e:
                            self.end_turn()

            # Draw game state
            self.screen.fill(BLUE_SEA)
            self.board_renderer.draw_board(self.screen, self)
            self.ui_renderer.draw_player_info(self.players)
            self.ui_renderer.draw_current_player(self.current_player, self.game_phase, self.placement_type)
            
            if self.robber_move_pending:
                self.ui_renderer.status_messages.append("Click a tile to move the robber")
            
            self.ui_renderer.draw_status_messages()
            
            if self.game_phase == GamePhase.PLAY:
                self.ui_renderer.draw_end_turn_button(self.dice_rolled_this_turn)
                self.ui_renderer.draw_placement_mode_button(self.placement_mode)
                self.ui_renderer.draw_buy_dev_card_button(self.placement_mode, self.current_player)

                if not self.dice_rolled_this_turn:
                    self.dice.draw_button()
                self.dice.draw_roll()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()