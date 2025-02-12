from typing import Optional
import random
from .enums import DevCardType, ResourceType
from .player import Player

class DevCardManager:
    """manages all development card related functionality"""
    
    def __init__(self, game):
        self.game = game
        self.initial_deck = (
            [DevCardType.KNIGHT] * 14 +
            [DevCardType.VICTORY_POINT] * 5 +
            [DevCardType.ROAD_BUILDING] * 2 +
            [DevCardType.YEAR_OF_PLENTY] * 2 +
            [DevCardType.MONOPOLY] * 2
        )
        random.shuffle(self.initial_deck)

    def init_deck(self):
        """initialize the dev card deck with standard distribution"""
        self.game.game_state.dev_card_deck = self.initial_deck.copy()
        self.game.update_game_state()

    def draw_dev_card(self) -> Optional[DevCardType]:
        """draw a card from the deck if available"""
        if not self.game.game_state.dev_card_deck:
            print("No development cards left in the deck!")
            return None
            
        card = self.game.game_state.dev_card_deck.pop()
        self.game.update_game_state()
        return card

    def buy_dev_card(self, player: Player) -> bool:
        """handle dev card purchase attempt"""
        dev_cost = {
            ResourceType.GRAIN: 1,
            ResourceType.WOOL: 1,
            ResourceType.ORE: 1
        }
        
        # check if any cards in deck
        if not self.game.game_state.dev_card_deck:
            print("No development cards left in the deck!")
            return False
            
        # check if player can afford
        if not player.has_resources(dev_cost):
            print(f"Player {player.name} cannot afford a development card!")
            return False
            
        player.spend_resources(dev_cost)
        
        # draw and add to hand
        drawn_card = self.draw_dev_card()
        player.dev_cards[drawn_card] += 1
        print(f"Player {player.name} bought a {drawn_card.name} card!")
        
        self.game.update_game_state()
        return True