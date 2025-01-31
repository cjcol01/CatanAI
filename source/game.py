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



class Game:
    """Main game class that handles the Catan game logic and display.
    
    This class manages the game state, player turns, board layout,
    resource distribution, and all game mechanics for Catan.
    """
    def __init__(self):
        """Initialize the game with display, board, players and game state."""
        # Set up pygame display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Catan")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.board = Board()
        self.players = [
            Player(RED, "Red"),
            Player(BLUE, "Blue"), 
            Player(GREEN, "Green"),
            Player(YELLOW, "Yellow")
        ]
        # Game state tracking
        self.current_player_index = 0  # Index of current player in self.players
        self.setup_turns_completed = 0  # Counter for setup phase turns
        
        # Game phase management
        self.game_phase = GamePhase.SETUP  # Current game state (SETUP or PLAY)
        self.setup_phase = 0  # Setup round (0 for first round, 1 for second round)
        self.setup_direction = 1  # Direction of setup turns (1 forward, -1 reverse)
        
        # Dice and turn management
        self.dice = Dice(self.screen, FONT)
        self.dice_rolled_this_turn = False
        
        # Building placement state
        self.placement_mode = True  # Whether in placement mode for buildings
        self.placement_type = PlacementType.SETTLEMENT
        self.hover_distance = 20  # Pixel distance for hover detection
        
        # Hover state tracking
        self.hovered_corner: Optional[Tuple[float, float]] = None
        self.hovered_road: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None
        
        # Game piece storage
        self.settlements = {}  # Maps corner positions to player index
        self.roads = {}  # Maps road endpoints to player index
        
        self.setup_manager = SetupPhaseManager(self)
        self.placement_manager = PlacementManager(self)
        self.ui_renderer = UIRenderer(self.screen)
        self.interaction_handler = InteractionHandler(self)
        self.resource_manager = ResourceManager(self)

        self.board.calculate_board_layout()

    @property
    def current_player(self):
        """Get the current player based on the current_player_index."""
        return self.players[self.current_player_index]

    def draw_board(self):
        # Find the leftmost and rightmost column indices
        min_col = min(col for col, _ in self.board.layout)
        max_col = max(col for col, _ in self.board.layout)
        
        for index, (col, row) in enumerate(self.board.layout):
            tile = self.board.get_tile_at(index)
            x, y = self.board.get_hex_center(col, row)
            color = RESOURCE_COLORS[tile.resource_type.name]
            self.board.draw_hexagon(self.screen, color, (x, y), TILE_SIZE)

            if tile.value is not None:
                text = FONT.render(str(tile.value), True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)

            if self.placement_mode or self.game_phase == GamePhase.SETUP:
                corners = self.board.get_hex_corners(x, y)
                current_player_color = self.players[self.current_player_index].color
                for corner_x, corner_y in corners:
                    pygame.draw.circle(self.screen, BLACK, (int(corner_x), int(corner_y)), 4)
                    
                    if self.hovered_corner and math.isclose(corner_x, self.hovered_corner[0], abs_tol=1) and math.isclose(corner_y, self.hovered_corner[1], abs_tol=1):
                        if self.placement_manager.is_valid_settlement_placement((corner_x, corner_y)):
                            pygame.draw.circle(self.screen, current_player_color, (int(corner_x), int(corner_y)), 10, 2)

        for (x, y), player_index in self.settlements.items():
            pygame.draw.circle(self.screen, self.players[player_index].color, (int(x), int(y)), 8)
            pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), 8, 2)

        for (start, end), player_index in self.roads.items():
            road_color = self.players[player_index].color
            # Draw black outline
            pygame.draw.line(self.screen, BLACK, start, end, 6)
            # Draw colored road
            pygame.draw.line(self.screen, road_color, start, end, 4)

        if (self.placement_mode or self.game_phase == GamePhase.SETUP) and self.hovered_corner:
            x, y = self.hovered_corner
            current_player_color = self.players[self.current_player_index].color
            if self.placement_manager.is_valid_settlement_placement((x, y)):
                pygame.draw.circle(self.screen, current_player_color, (int(x), int(y)), 8, 2)

        if (self.placement_mode or self.game_phase == GamePhase.SETUP) and self.hovered_road:
            start, end = self.hovered_road
            current_player_color = self.players[self.current_player_index].color
            if self.placement_manager.is_valid_road_placement(start, end):
                pygame.draw.line(self.screen, current_player_color, start, end, 4)
                    
    def end_turn(self):
        if not self.dice_rolled_this_turn:
            print("You must roll the dice before ending your turn.")
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.dice_rolled_this_turn = False
        self.placement_mode = False
        print(f"Turn ended. Current player: {self.current_player.name}")
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.interaction_handler.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.interaction_handler.handle_mouse_motion(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.resource_manager.give_all_resources_cheat()
                    elif event.key == pygame.K_r:
                        if not self.dice_rolled_this_turn:
                            roll_value = self.dice.roll_dice() 
                            if roll_value is not None:
                                print(f"Rolled: {roll_value}")
                                self.dice_rolled_this_turn = True
                                self.resource_manager.distribute_resources(roll_value)
                    elif event.key == pygame.K_e:
                        self.end_turn()

            self.screen.fill(BLUE_SEA)
            self.draw_board()
            self.ui_renderer.draw_player_info(self.players)
            self.ui_renderer.draw_current_player(self.current_player, self.game_phase, self.placement_type)
            
            if self.game_phase == GamePhase.PLAY:
                self.ui_renderer.draw_end_turn_button(self.dice_rolled_this_turn)
                self.ui_renderer.draw_placement_mode_button(self.placement_mode)
                
                if not self.dice_rolled_this_turn:
                    self.dice.draw_button()
                self.dice.draw_roll()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
