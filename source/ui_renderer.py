import pygame
from .constants import *
from .enums import GameState

class UIRenderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_player_info(self, players):
        info_height = 150
        player_width = SCREEN_WIDTH // 4
        for i, player in enumerate(players):
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

    def draw_end_turn_button(self, dice_rolled):
        if dice_rolled:
            button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 250, 130, 50)
            pygame.draw.rect(self.screen, LIGHT_GRAY, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            text = FONT.render("End Turn", True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            return button_rect

    def draw_placement_mode_button(self, placement_mode):
        button_rect = pygame.Rect(20, SCREEN_HEIGHT - 250, 175, 50)
        color = LIGHT_GRAY if not placement_mode else YELLOW
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        text = FONT.render("Placement Mode", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        return button_rect
    
    def draw_setup_instructions(self, game_state, current_setup_action):
        if game_state == GameState.SETUP_FIRST_ROUND:
            round_text = "First Round Setup"
        elif game_state == GameState.SETUP_SECOND_ROUND:
            round_text = "Second Round Setup"
        else:
            return

        action_text = f"Place a {current_setup_action}"

        round_surface = FONT.render(round_text, True, BLACK)
        action_surface = FONT.render(action_text, True, BLACK)
        
        round_rect = round_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
        action_rect = action_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        
        # Draw a background rectangle to cover previous text
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 90)
        pygame.draw.rect(self.screen, BLUE_SEA, bg_rect)
        
        self.screen.blit(round_surface, round_rect)
        self.screen.blit(action_surface, action_rect)

    def draw_current_player(self, current_player):
        text = FONT.render(f"Current Player: {current_player.name}", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        
        # Draw a background rectangle to cover previous text
        bg_rect = pygame.Rect(0, 75, SCREEN_WIDTH, 30)
        pygame.draw.rect(self.screen, BLUE_SEA, bg_rect)
        
        self.screen.blit(text, text_rect)