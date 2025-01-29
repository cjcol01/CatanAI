import pygame
import math
from typing import List, Tuple, Optional
from .constants import *
from .enums import ResourceType, DevCardType, GameState, PlayerAction, PlacementType
from .board import Board, Tile
from .player import Player
from .dice import Dice

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
        self.game_state = GameState.SETUP  # Current game state (SETUP or PLAY)
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
        
        self.calculate_board_layout()

        
    def calculate_board_layout(self):
        """Calculate the dimensions and position of the game board.
        
        Sets up the hexagonal grid measurements and positions the board
        centered on the screen with space for player information.
        """
        self.hex_height = TILE_SIZE * 2
        self.hex_width = math.sqrt(3) * TILE_SIZE
        
        # Calculate board dimensions
        board_width = self.hex_width * 5  # 5 hexes wide
        board_height = self.hex_height * 4.5  # 5 rows, but they overlap, so it's 4.5 times the height
        
        # Calculate board position
        self.board_left = (SCREEN_WIDTH - board_width) // 2
        self.board_top = (SCREEN_HEIGHT - board_height) // 2 - self.hex_height // 4  # Adjust for player info at bottom

        # Calculate the center of the board
        self.board_center_x = SCREEN_WIDTH // 2
        self.board_center_y = self.board_top + board_height // 2

    def draw_hexagon(self, surface: pygame.Surface, color: Tuple[int, int, int], center: Tuple[float, float], size: float):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            points.append((center[0] + size * math.cos(angle_rad),
                           center[1] + size * math.sin(angle_rad)))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 4)

    def get_hex_corners(self, center_x: float, center_y: float) -> List[Tuple[float, float]]:
        corners = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            corner_x = center_x + TILE_SIZE * math.cos(angle_rad)
            corner_y = center_y + TILE_SIZE * math.sin(angle_rad)
            corners.append((corner_x, corner_y))
        return corners

    def draw_board(self):
        # Find the leftmost and rightmost column indices
        min_col = min(col for col, _ in self.board.layout)
        max_col = max(col for col, _ in self.board.layout)
        
        for index, (col, row) in enumerate(self.board.layout):
            tile = self.board.get_tile_at(index)
            x, y = self.board.get_hex_center(col, row)
            color = RESOURCE_COLORS[tile.resource_type.name]
            self.draw_hexagon(self.screen, color, (x, y), TILE_SIZE)

            if tile.value is not None:
                text = FONT.render(str(tile.value), True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)

            if self.placement_mode or self.game_state == GameState.SETUP:
                corners = self.board.get_hex_corners(x, y)
                current_player_color = self.players[self.current_player_index].color
                for corner_x, corner_y in corners:
                    pygame.draw.circle(self.screen, BLACK, (int(corner_x), int(corner_y)), 4)
                    
                    if self.hovered_corner and math.isclose(corner_x, self.hovered_corner[0], abs_tol=1) and math.isclose(corner_y, self.hovered_corner[1], abs_tol=1):
                        if self.is_valid_settlement_placement((corner_x, corner_y)):
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

        if (self.placement_mode or self.game_state == GameState.SETUP) and self.hovered_corner:
            x, y = self.hovered_corner
            current_player_color = self.players[self.current_player_index].color
            if self.is_valid_settlement_placement((x, y)):
                pygame.draw.circle(self.screen, current_player_color, (int(x), int(y)), 8, 2)

        if (self.placement_mode or self.game_state == GameState.SETUP) and self.hovered_road:
            start, end = self.hovered_road
            current_player_color = self.players[self.current_player_index].color
            if self.is_valid_road_placement(start, end):
                pygame.draw.line(self.screen, current_player_color, start, end, 4)

    def handle_mouse_motion(self, pos: Tuple[int, int]):
        if self.placement_mode or self.game_state == GameState.SETUP:
            self.hovered_corner = None
            self.hovered_road = None
            for _, (col, row) in enumerate(self.board.layout):
                x, y = self.board.get_hex_center(col, row)
                corners = self.board.get_hex_corners(x, y)
                for i, (corner_x, corner_y) in enumerate(corners):
                    if math.hypot(pos[0] - corner_x, pos[1] - corner_y) <= self.hover_distance:
                        self.hovered_corner = (corner_x, corner_y)
                        return
                    next_corner = corners[(i + 1) % 6]
                    mid_x = (corner_x + next_corner[0]) / 2
                    mid_y = (corner_y + next_corner[1]) / 2
                    if math.hypot(pos[0] - mid_x, pos[1] - mid_y) <= self.hover_distance:
                        self.hovered_road = ((corner_x, corner_y), next_corner)
                        return

    def draw_player_info(self):
        info_height = 150
        player_width = SCREEN_WIDTH // 4
        for i, player in enumerate(self.players):
            x = i * player_width
            y = SCREEN_HEIGHT - info_height
            pygame.draw.rect(self.screen, player.color, (x, y, player_width, info_height))
            pygame.draw.rect(self.screen, BLACK, (x, y, player_width, info_height), 2)
            
            text_y = y + 10
            for resource, amount in player.resources.items():
                text = FONT.render(f"{resource.name}: {amount}", True, BLACK)
                self.screen.blit(text, (x + 10, text_y))
                text_y += 20
            
            text_y += 10
            for dev_card, amount in player.dev_cards.items():
                if amount > 0:
                    text = FONT.render(f"{dev_card.name}: {amount}", True, BLACK)
                    self.screen.blit(text, (x + 10, text_y))
                    text_y += 20

    def draw_current_player(self):
        current_player = self.players[self.current_player_index]
        if self.game_state == GameState.SETUP:
            phase_text = f"Setup Phase {'1' if self.setup_phase == 0 else '2'}"
            action_text = f"Place a {'settlement' if self.placement_type == PlacementType.SETTLEMENT else 'road'}"
            text = FONT.render(f"Current Player: {current_player.name} - {phase_text} - {action_text}", True, BLACK)
        else:
            text = FONT.render(f"Current Player: {current_player.name}", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(text, text_rect)

    def end_turn(self):
        if not self.dice_rolled_this_turn:
            print("You must roll the dice before ending your turn.")
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.dice_rolled_this_turn = False
        self.placement_mode = False
        print(f"Turn ended. Current player: {self.players[self.current_player_index].name}")

    def draw_end_turn_button(self):
        if self.dice_rolled_this_turn:
            button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 250, 130, 50)
            button_color = LIGHT_GRAY
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            text = FONT.render("End Turn", True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            return button_rect

    
    def handle_click(self, pos: Tuple[int, int]):
        if self.game_state == GameState.SETUP:
            self.handle_setup_phase()
        elif self.game_state == GameState.PLAY:
            if not self.dice_rolled_this_turn:
                roll_value = self.dice.handle_click(pos)
                if roll_value is not None:
                    print(f"Rolled: {roll_value}")
                    self.dice_rolled_this_turn = True
                    self.distribute_resources(roll_value)
            
            end_turn_rect = self.draw_end_turn_button()
            if end_turn_rect is not None and end_turn_rect.collidepoint(pos) and self.dice_rolled_this_turn:
                self.end_turn()
            
            placement_mode_rect = self.draw_placement_mode_button()
            if placement_mode_rect.collidepoint(pos):
                self.toggle_placement_mode()

            if self.placement_mode:
                self.try_place_settlement(pos)
                self.try_place_road(pos)
    def distribute_resources(self, roll_value: int):
        """Distribute resources to players based on dice roll.
        
        Args:
            roll_value: The sum of the dice roll (2-12)
            
        Gives one resource to each player for each settlement they own
        adjacent to a hex with the rolled number.
        """
        for player_index, player in enumerate(self.players):
            for settlement_pos in self.settlements:
                if self.settlements[settlement_pos] == player_index:
                    adjacent_tiles = self.board.get_adjacent_tiles(*settlement_pos)
                    for _, tile in adjacent_tiles:
                        if tile.value == roll_value and tile.resource_type != ResourceType.DESERT:
                            player.add_resource(tile.resource_type)
                            print(f"Player {player.name} received 1 {tile.resource_type.name}")

    def draw_placement_mode_button(self):
        button_rect = pygame.Rect(20, SCREEN_HEIGHT - 250, 175, 50)
        color = LIGHT_GRAY if not self.placement_mode else YELLOW
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        text = FONT.render("Placement Mode", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        return button_rect

    def toggle_placement_mode(self):
        self.placement_mode = not self.placement_mode
        print(f"Placement mode {'activated' if self.placement_mode else 'deactivated'}")
                
    def try_place_settlement(self, pos: Tuple[int, int]) -> bool:
        if self.hovered_corner:
            corner_x, corner_y = self.hovered_corner
            if self.is_valid_settlement_placement((corner_x, corner_y)):
                self.place_settlement((corner_x, corner_y))
                return True
        return False

    def place_settlement(self, pos: Tuple[float, float]):
        self.settlements[pos] = self.current_player_index
        self.players[self.current_player_index].build_settlement(len(self.settlements) - 1)
        print(f"Player {self.players[self.current_player_index].name} placed a settlement at {pos}")
        
        if self.game_state == GameState.SETUP and self.setup_phase == 1:
            adjacent_tiles = self.board.get_adjacent_tiles(*pos)
            for _, tile in adjacent_tiles:
                if tile.resource_type != ResourceType.DESERT:
                    self.players[self.current_player_index].add_resource(tile.resource_type)
                    print(f"Player {self.players[self.current_player_index].name} received 1 {tile.resource_type.name} for initial settlement")


    def is_valid_road_placement(self, start: Tuple[float, float], end: Tuple[float, float]) -> bool:
        if (start, end) in self.roads or (end, start) in self.roads:
            return False
        
        player_settlements = [pos for pos, player in self.settlements.items() if player == self.current_player_index]
        if start in player_settlements or end in player_settlements:
            if self.game_state == GameState.PLAY:
                current_player = self.players[self.current_player_index]
                return current_player.can_afford_road()
            return True
        
        player_roads = [road for road, player in self.roads.items() if player == self.current_player_index]
        for road_start, road_end in player_roads:
            if start == road_start or start == road_end or end == road_start or end == road_end:
                if self.game_state == GameState.PLAY:
                    current_player = self.players[self.current_player_index]
                    return current_player.can_afford_road()
                return True
        
        return False
                
    def is_valid_settlement_placement(self, pos: Tuple[float, float]) -> bool:
        if pos in self.settlements:
            return False
        
        for settlement_pos in self.settlements:
            if math.hypot(pos[0] - settlement_pos[0], pos[1] - settlement_pos[1]) < self.hex_width:
                return False
        
        if self.game_state == GameState.PLAY:
            player_roads = [road for road, player in self.roads.items() if player == self.current_player_index]
            if not any(pos in road for road in player_roads):
                return False
            
            current_player = self.players[self.current_player_index]
            if not current_player.can_afford_settlement():
                return False
        
        return True

    def try_place_road(self, pos: Tuple[int, int]) -> bool:
        if self.hovered_road:
            start, end = self.hovered_road
            if self.is_valid_road_placement(start, end):
                self.place_road(start, end)
                return True
        return False 


    def place_settlement(self, pos: Tuple[float, float]):
        """Place a settlement at the specified position.
        
        Args:
            pos: (x, y) coordinates for the settlement
            
        Handles resource costs, updates game state, and distributes
        initial resources during setup phase.
        """
        current_player = self.players[self.current_player_index]
        
        if self.game_state == GameState.PLAY:
            if not current_player.can_afford_settlement():
                print(f"Player {current_player.name} cannot afford a settlement.")
                return
            
            settlement_cost = {
                ResourceType.WOOD: 1,
                ResourceType.BRICK: 1,
                ResourceType.GRAIN: 1,
                ResourceType.WOOL: 1
            }
            current_player.spend_resources(settlement_cost)
        
        self.settlements[pos] = self.current_player_index
        current_player.build_settlement(len(self.settlements) - 1)
        print(f"Player {current_player.name} placed a settlement at {pos}")
        
        if self.game_state == GameState.SETUP and self.setup_phase == 1:
            adjacent_tiles = self.board.get_adjacent_tiles(*pos)
            for _, tile in adjacent_tiles:
                if tile.resource_type != ResourceType.DESERT:
                    current_player.add_resource(tile.resource_type)
                    print(f"Player {current_player.name} received 1 {tile.resource_type.name} for initial settlement")

    def place_road(self, start: Tuple[float, float], end: Tuple[float, float]):
        current_player = self.players[self.current_player_index]
        
        if self.game_state == GameState.PLAY:
            if not current_player.can_afford_road():
                print(f"Player {current_player.name} cannot afford a road.")
                return
            
            road_cost = {
                ResourceType.WOOD: 1,
                ResourceType.BRICK: 1
            }
            current_player.spend_resources(road_cost)
        
        self.roads[(start, end)] = self.current_player_index
        current_player.build_road(start, end)
        print(f"Player {current_player.name} placed a road from {start} to {end}")


    def next_setup_turn(self):
        self.setup_turns_completed += 1
        if self.setup_phase == 0:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if self.current_player_index == 0:
                self.setup_phase = 1
                self.setup_direction = -1
                self.current_player_index = len(self.players) - 1  # Start with the last player
        elif self.setup_phase == 1:
            self.current_player_index = (self.current_player_index + self.setup_direction) % len(self.players)
        
        if self.setup_turns_completed == len(self.players) * 2:
            self.end_setup_phase()
        else:
            self.placement_type = PlacementType.SETTLEMENT
            print(f"Next player: {self.players[self.current_player_index].name}. Place a settlement.")

    def end_setup_phase(self):
        self.game_state = GameState.PLAY
        self.placement_mode = False
        self.current_player_index = 0  # Start the main game with the first player
        print("Setup phase complete. Starting main game phase.")

    def handle_setup_phase(self):
        current_pos = pygame.mouse.get_pos()
        if self.placement_type == PlacementType.SETTLEMENT:
            if self.try_place_settlement(current_pos):
                self.placement_type = PlacementType.ROAD
                print(f"Player {self.players[self.current_player_index].name} placed a settlement. Now place a road.")
        elif self.placement_type == PlacementType.ROAD:
            if self.try_place_road(current_pos):
                self.next_setup_turn()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)

            self.screen.fill(BLUE_SEA)
            self.draw_board()
            self.draw_player_info()
            self.draw_current_player()
            
            if self.game_state == GameState.PLAY:
                self.draw_end_turn_button()
                self.draw_placement_mode_button()
                
                if not self.dice_rolled_this_turn:
                    self.dice.draw_button()
                self.dice.draw_roll()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
