from typing import List, Optional, Dict
import random
from .enums import DevCardType, ResourceType
from .player import Player


class DevCardManager:
    """Manages all development card related functionality in the game."""
    
    def __init__(self, game):
        self.game = game
        self.dev_card_deck: List[DevCardType] = []
        self._initialize_dev_card_deck()

    def _initialize_dev_card_deck(self):
        """Initialize the development card deck with standard Catan distribution."""
        self.dev_card_deck = (
            [DevCardType.KNIGHT] * 14 +
            [DevCardType.VICTORY_POINT] * 5 +
            [DevCardType.ROAD_BUILDING] * 2 +
            [DevCardType.YEAR_OF_PLENTY] * 2 +
            [DevCardType.MONOPOLY] * 2
        )
        random.shuffle(self.dev_card_deck)

    def draw_dev_card(self) -> Optional[DevCardType]:
        """Draw a development card from the deck if available."""
        if not self.dev_card_deck:
            print("No development cards left in the deck!")
            return None
        return self.dev_card_deck.pop()

    def buy_dev_card(self, player: Player) -> bool:
        """Handle the purchase of a development card by a player."""
        dev_cost = {
            ResourceType.GRAIN: 1,
            ResourceType.WOOL: 1,
            ResourceType.ORE: 1
        }
        
        # check if any cards in deck
        if not self.dev_card_deck:
            print("No development cards left in the deck!")
            return False
            
        # player can afford the card
        if not player.has_resources(dev_cost):
            print(f"Player {player.name} cannot afford a development card!")
            return False
            
        player.spend_resources(dev_cost)
        
        # draw card from deck
        drawn_card = self.draw_dev_card()
                
        # add card to player hand
        player.dev_cards[drawn_card] += 1
        print(f"Player {player.name} bought a {drawn_card.name} card!")
        
        return True