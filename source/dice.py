import random
import pygame
from .constants import BLACK, LIGHT_GRAY

class Dice:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.roll_time = 0
        self.display_duration = 3000  # show roll for 3 seconds
        self.game = None  # set later by game
        self.roll_value = None  # store locally for display

    def roll(self):
        """roll dice and update game state"""
        self.roll_value = random.randint(1, 6) + random.randint(1, 6)
        self.roll_time = pygame.time.get_ticks()
        if self.game:
            self.game.game_state.dice_value = self.roll_value
            self.game.update_game_state()
        return self.roll_value

    def draw_button(self):
        """draw the roll button"""
        button_rect = pygame.Rect(self.screen.get_width() - 150, 20, 130, 50)
        pygame.draw.rect(self.screen, LIGHT_GRAY, button_rect)  
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        text = self.font.render("Roll Dice", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        return button_rect

    def draw_roll(self):
        """draw current roll if within display time"""
        current_time = pygame.time.get_ticks()
        if (self.roll_value is not None and 
            current_time - self.roll_time < self.display_duration):
            text = self.font.render(f"Dice Roll: {self.roll_value}", True, BLACK)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 50))
            self.screen.blit(text, text_rect)

    def roll_dice(self):
        """roll dice without button check"""
        return self.roll()

    def handle_click(self, pos):
        """handle dice button clicks"""
        button_rect = self.draw_button()
        if button_rect.collidepoint(pos):
            return self.roll()
        return None

    def set_game(self, game):
        """set game reference after init"""
        self.game = game