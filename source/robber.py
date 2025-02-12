import math
import random
from typing import Optional, Tuple, List, Dict
import pygame
from .constants import BLACK, GRAY, TILE_SIZE, WHITE, FONT, SCREEN_HEIGHT, SCREEN_WIDTH

class RobberManager:
    """handles robber movement and stealing mechanics"""
    
    def __init__(self, game):
        self.game = game
        self.move_pending = False
        self.stealing_enabled = True
        self.stealing_pending = False
        self.current_victims: List[int] = []
        self.victim_buttons: Dict[int, pygame.Rect] = {}
        
    def draw_robber(self, screen):
        """draw the robber token on its tile"""
        robber_q, robber_r = self.game.board.axial_layout[self.game.game_state.robber_position]
        x, y = self.game.board.get_hex_center(robber_q, robber_r)
        radius = TILE_SIZE * 0.2
        pygame.draw.circle(screen, GRAY, (int(x), int(y)), int(radius))
        pygame.draw.circle(screen, BLACK, (int(x), int(y)), int(radius), 2)
    
    def draw_placement_indicator(self, screen, mouse_pos: Tuple[int, int]):
        """show where robber can be placed"""
        if not self.move_pending:
            return
            
        for index, (q, r) in enumerate(self.game.board.axial_layout):
            x, y = self.game.board.get_hex_center(q, r)
            if (math.hypot(mouse_pos[0] - x, mouse_pos[1] - y) <= TILE_SIZE and 
                index != self.game.game_state.robber_position):
                pygame.draw.circle(screen, BLACK, (int(x), int(y)), int(TILE_SIZE * 0.3), 3)

    def draw_stealing_interface(self, screen):
        """draw the interface for choosing who to steal from"""
        if not self.stealing_pending:
            return

        self.victim_buttons.clear()

        # darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # set up dialog box
        box_width = 300
        box_height = 50 + (len(self.current_victims) * 60)
        x = (SCREEN_WIDTH - box_width) // 2
        y = (SCREEN_HEIGHT - box_height) // 2

        # draw box
        pygame.draw.rect(screen, WHITE, (x, y, box_width, box_height))
        pygame.draw.rect(screen, BLACK, (x, y, box_width, box_height), 2)

        # add title
        title = FONT.render("select a player to steal from:", True, BLACK)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, y=y+10)
        screen.blit(title, title_rect)

        # add player buttons
        button_y = y + 50
        for victim_idx in self.current_victims:
            victim = self.game.players[victim_idx]
            button_rect = pygame.Rect(x+20, button_y, box_width-40, 40)
            self.victim_buttons[victim_idx] = button_rect

            pygame.draw.rect(screen, victim.color, button_rect)
            pygame.draw.rect(screen, BLACK, button_rect, 2)

            text = FONT.render(f"{victim.name} ({victim.get_resource_count()} resources)", True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)

            button_y += 60

    def handle_seven_rolled(self):
        """start robber movement when 7 is rolled"""
        print("seven rolled! move the robber")
        self.move_pending = True
        self.game.ui_renderer.add_message("click a tile to move the robber")

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """handle clicks during robber phase"""
        if self.stealing_pending:
            for victim_idx, button_rect in self.victim_buttons.items():
                if button_rect.collidepoint(pos[0], pos[1]):
                    self._steal_from_player(victim_idx)
                    return True
        elif self.move_pending:
            return self._handle_tile_click(pos)
        return False

    def _handle_tile_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """handle clicking a tile to move the robber"""
        for idx, (q, r) in enumerate(self.game.board.axial_layout):
            x, y = self.game.board.get_hex_center(q, r)
            
            if math.hypot(mouse_pos[0] - x, mouse_pos[1] - y) <= TILE_SIZE:
                if idx != self.game.game_state.robber_position:
                    self.game.game_state.robber_position = idx
                    self.move_pending = False
                    print(f"moved robber to tile {idx}")
                    
                    if self.stealing_enabled:
                        self.current_victims = self._find_potential_victims(idx)
                        if len(self.current_victims) == 1:
                            victim_idx = self.current_victims[0]
                            print(f"automatically stealing from {self.game.players[victim_idx].name}")
                            self._steal_from_player(victim_idx)
                            self.current_victims = []
                        elif len(self.current_victims) > 1:
                            self.stealing_pending = True

                    self.game.update_game_state()
                    return True
        return False

    def _find_potential_victims(self, tile_idx: int) -> List[int]:
        """find players who can be stolen from on this tile"""
        victims = set()
        tile_q, tile_r = self.game.board.axial_layout[tile_idx]
        tile_center = self.game.board.get_hex_center(tile_q, tile_r)
        corners = self.game.board.get_hex_corners(*tile_center)
        
        for corner in corners:
            rounded_corner = (round(corner[0]), round(corner[1]))
            
            # check both settlements and cities
            for structures, structure_type in [(self.game.game_state.settlements, "settlement"), 
                                            (self.game.game_state.cities, "city")]:
                if rounded_corner in structures:
                    player_idx = structures[rounded_corner]
                    if (player_idx != self.game.game_state.current_player_index and 
                        self.game.players[player_idx].get_resource_count() > 0):
                        victims.add(player_idx)
                    
        return list(victims)

    def _steal_from_player(self, victim_idx: int):
        """steal random resource from chosen player"""
        victim = self.game.players[victim_idx]
        thief = self.game.current_player
        
        available_resources = [
            resource for resource, amount in victim.resources.items()
            if amount > 0
        ]
        
        if available_resources:
            stolen_resource = random.choice(available_resources)
            victim.remove_resource(stolen_resource)
            thief.add_resource(stolen_resource)
            print(f"{thief.name} stole {stolen_resource.name} from {victim.name}")
            self.game.ui_renderer.add_message(f"{thief.name} stole {stolen_resource.name} from {victim.name}")
            
        self.stealing_pending = False
        self.current_victims.clear()
        self.victim_buttons.clear()
        self.game.update_game_state()