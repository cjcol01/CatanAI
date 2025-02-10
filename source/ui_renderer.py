import pygame
from .constants import *
from .enums import ResourceType, DevCardType, GamePhase, PlayerAction, PlacementType


class UIRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.message_queue = []
        self.persistent_messages = [] 
        self.current_player_message = None  # current player message separately

        self.BASE_LINE_HEIGHT = 20  # height of each line 
        self.PADDING = 10 
        self.SECTION_SPACING = 10  # gap between resources and dev
        self.current_info_height = 0  
        self.game_over = False

    def calculate_player_box_height(self, player):
        """Calculate required height for player info box based on content."""
        height = self.PADDING 
        
        # height for resources - always shown
        resource_count = len([r for r in ResourceType if r != ResourceType.DESERT])
        height += resource_count * self.BASE_LINE_HEIGHT
        
        # spacing if there are dev cards
        if any(amount > 0 for amount in player.dev_cards.values()):
            height += self.SECTION_SPACING
            
        # height for dev cards
        dev_card_count = sum(1 for amount in player.dev_cards.values() if amount > 0)
        if dev_card_count > 0:
            height += dev_card_count * self.BASE_LINE_HEIGHT
            
        height += self.PADDING
        return height

    def draw_player_info(self, players):
        player_width = SCREEN_WIDTH // 4
        max_height = 0
        
        # calc max height needed
        for player in players:
            height = self.calculate_player_box_height(player)
            max_height = max(max_height, height)
        
        # store height for other methods
        self.current_info_height = max_height
        
        # draw player boxes
        for i, player in enumerate(players):
            x = i * player_width
            y = SCREEN_HEIGHT - max_height
            pygame.draw.rect(self.screen, player.color, (x, y, player_width, max_height))
            pygame.draw.rect(self.screen, BLACK, (x, y, player_width, max_height), 2)
            
            # draw resources
            text_y = y + self.PADDING
            for resource in ResourceType:
                if resource != ResourceType.DESERT:
                    amount = player.resources[resource]
                    text = FONT.render(f"{resource.name}: {amount}", True, BLACK)
                    self.screen.blit(text, (x + self.PADDING, text_y))
                    text_y += self.BASE_LINE_HEIGHT
            
            # draw dev cards if player has any
            has_dev_cards = any(amount > 0 for amount in player.dev_cards.values())
            if has_dev_cards:
                text_y += self.SECTION_SPACING
                for dev_card, amount in player.dev_cards.items():
                    if amount > 0:
                        text = FONT.render(f"{dev_card.name}: {amount}", True, BLACK)
                        self.screen.blit(text, (x + self.PADDING, text_y))
                        text_y += self.BASE_LINE_HEIGHT

    def draw_end_turn_button(self, dice_rolled):
        if dice_rolled:
            button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - self.current_info_height - 60, 130, 50)
            pygame.draw.rect(self.screen, LIGHT_GRAY, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            text = FONT.render("End Turn", True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            return button_rect

    def draw_placement_mode_button(self, placement_mode):
        button_rect = pygame.Rect(20, SCREEN_HEIGHT - self.current_info_height - 60, 175, 50)
        color = LIGHT_GRAY if not placement_mode else YELLOW
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        text = FONT.render("Placement Mode", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        return button_rect

    def draw_buy_dev_card_button(self, placement_mode, current_player):
        """Draw the buy development card button if in placement mode."""
        if placement_mode:
            button_rect = pygame.Rect(20, 20, 150, 40)
            color = GREEN if current_player.can_afford_dev() else LIGHT_GRAY
            
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            text = FONT.render("Buy Dev Card", True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            return button_rect

    def draw_current_player(self, current_player, game_phase, placement_type):
        if game_phase == GamePhase.END:
            return
            
        message = f"Current Player: {current_player.name}"
        if game_phase == GamePhase.SETUP:
            phase_text = f"Setup Phase {'1' if GamePhase.SETUP == 0 else '2'}"
            action_text = f"Place a {'settlement' if placement_type == PlacementType.SETTLEMENT else 'road'}"
            message = f"{message} - {phase_text} - {action_text}"
        
        self.set_current_player_message(message)

    def add_message(self, text, duration=2000):
        # Add only if not duplicate
        if not any(msg['text'] == text for msg in self.message_queue):
            self.message_queue.append({
                'text': text,
                'timestamp': pygame.time.get_ticks(),
                'duration': duration
            })

    def set_current_player_message(self, text):
        self.current_player_message = text

    def draw_status_messages(self):
        current_time = pygame.time.get_ticks()
        # clean expired
        self.message_queue = [msg for msg in self.message_queue 
                            if current_time - msg['timestamp'] < msg['duration']]
        
        y_offset = 30

        # current player
        if self.current_player_message:
            text = FONT.render(self.current_player_message, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35

        # temporary messages
        for msg in self.message_queue:
            text = FONT.render(msg['text'], True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35

        # persistent messages last
        for msg in self.persistent_messages:
            text = FONT.render(msg, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35

    def add_persistent_message(self, text):
        self.add_message(text, float('inf'))

    def clear_messages(self):
        self.message_queue = []
        self.persistent_messages = []
        self.current_player_message = []