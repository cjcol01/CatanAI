import pygame
from .constants import *
from .enums import ResourceType, DevCardType, GamePhase, PlayerAction, PlacementType


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

    def draw_current_player(self, current_player, game_phase, placement_type):
            if game_phase == GamePhase.SETUP:
                phase_text = f"Setup Phase {'1' if GamePhase.SETUP == 0 else '2'}"
                action_text = f"Place a {'settlement' if placement_type == PlacementType.SETTLEMENT else 'road'}"
                text = FONT.render(f"Current Player: {current_player.name} - {phase_text} - {action_text}", True, BLACK)
            else:
                text = FONT.render(f"Current Player: {current_player.name}", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(text, text_rect)

    def draw_city_button(self, placement_mode):
        button_rect = pygame.Rect(SCREEN_WIDTH - 160, 10, 150, 30)
        pygame.draw.rect(self.screen, LIGHT_GRAY, button_rect)
        text = FONT.render("Build City", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        return button_rect