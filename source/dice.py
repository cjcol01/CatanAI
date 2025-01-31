import random
import pygame
# from .graphic_dice import graphic_dice

class Dice:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.roll_value = None
        self.roll_time = 0
        self.display_duration = 3000  # Display dice roll for 3 seconds

    def roll(self):
        self.roll_value = random.randint(1, 6) + random.randint(1, 6)
        self.roll_time = pygame.time.get_ticks()
        return self.roll_value

    def draw_button(self):
        button_rect = pygame.Rect(self.screen.get_width() - 150, 20, 130, 50)
        pygame.draw.rect(self.screen, (200, 200, 200), button_rect)  # Light gray
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)  # Black border
        text = self.font.render("Roll Dice", True, (0, 0, 0))
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        return button_rect

    def draw_roll(self):

        # graphic_dice()

        if self.roll_value is not None and pygame.time.get_ticks() - self.roll_time < self.display_duration:
            text = self.font.render(f"Dice Roll: {self.roll_value}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 50))
            self.screen.blit(text, text_rect)

    def roll_dice(self):
        """Roll dice directly without button check"""
        roll_value = self.roll()
        return roll_value


    def handle_click(self, pos):
        button_rect = self.draw_button()
        if button_rect.collidepoint(pos):
            return self.roll()
        return None